"""DDP connection handling for sending and receiving pixel data.

This module provides the main DDPConnection type for communicating with
DDP-compatible LED displays.
"""

import asyncio
from typing import Optional, Tuple
import socket

from ddp.protocol import PixelConfig, ID, Header, PacketType
from ddp.protocol.timecode import TimeCode
from ddp.protocol import message
from ddp.packet import Packet
from ddp.error import DDPError, NoValidSocketAddrError, NothingToReceiveError


# Maximum pixel data size per DDP packet (480 pixels × 3 bytes RGB = 1440 bytes)
MAX_DATA_LENGTH = 480 * 3


class DDPConnection:
    """A connection to a DDP display device.

    This is the main type for sending pixel data to LED strips and other DDP-compatible
    displays. It handles packet assembly, sequencing, and automatic chunking of large
    data arrays.

    Examples:
        >>> import asyncio
        >>> from ddp import DDPConnection
        >>> from ddp.protocol import PixelConfig, ID
        >>>
        >>> async def main():
        ...     conn = await DDPConnection.create(
        ...         "192.168.1.40:4048",
        ...         PixelConfig.default(),
        ...         ID.DEFAULT
        ...     )
        ...     # Send RGB data for 3 pixels
        ...     await conn.write(bytes([
        ...         255, 0, 0,    # Red
        ...         0, 255, 0,    # Green
        ...         0, 0, 255,    # Blue
        ...     ]))
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        addr: Tuple[str, int],
        pixel_config: PixelConfig,
        id: ID,
        sock: socket.socket,
    ):
        """Initialize a DDPConnection.

        Note: Use DDPConnection.create() instead of calling this directly.
        """
        self.addr = addr
        self.pixel_config = pixel_config
        self.id = id
        self.socket = sock
        self.sequence_number = 1
        self.buffer = bytearray(1500)  # Reusable buffer
        self.receive_queue: asyncio.Queue[Packet] = asyncio.Queue()
        self._recv_task: Optional[asyncio.Task] = None

    @staticmethod
    async def create(
        addr: str,
        pixel_config: PixelConfig,
        id: ID,
        local_addr: str = "0.0.0.0:0",
    ) -> 'DDPConnection':
        """Create a new DDP connection to a display.

        Args:
            addr: The display address (IP:port). DDP standard port is 4048.
            pixel_config: Pixel format configuration (RGB, RGBW, etc.)
            id: Protocol ID to use for this connection
            local_addr: Local address to bind to (default: "0.0.0.0:0")

        Returns:
            A new DDPConnection instance

        Raises:
            NoValidSocketAddrError: Failed to resolve address
            DDPError: Failed to create connection

        Examples:
            >>> conn = await DDPConnection.create(
            ...     "192.168.1.40:4048",
            ...     PixelConfig.default(),
            ...     ID.DEFAULT
            ... )
        """
        # Parse remote address
        try:
            host, port_str = addr.rsplit(':', 1)
            remote_addr = (host, int(port_str))
        except (ValueError, AttributeError):
            raise NoValidSocketAddrError()

        # Parse local address
        try:
            local_host, local_port_str = local_addr.rsplit(':', 1)
            local_bind = (local_host, int(local_port_str))
        except (ValueError, AttributeError):
            local_bind = ("0.0.0.0", 0)

        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.bind(local_bind)

        conn = DDPConnection(remote_addr, pixel_config, id, sock)

        # Start receive task
        loop = asyncio.get_event_loop()
        conn._recv_task = loop.create_task(conn._receive_loop())

        return conn

    async def write(self, data: bytes) -> int:
        """Write pixel data to the display starting at offset 0.

        Large data arrays are automatically split into multiple packets. Each packet
        can contain up to 1440 bytes (480 RGB pixels).

        Args:
            data: Raw pixel data bytes. For RGB, this should be groups of 3 bytes (R,G,B).
                  For RGBW, groups of 4 bytes (R,G,B,W).

        Returns:
            The total number of bytes sent across all packets.

        Examples:
            >>> # Set first 3 pixels to red, green, blue
            >>> await conn.write(bytes([255, 0, 0, 0, 255, 0, 0, 0, 255]))
        """
        header = Header(
            packet_type=PacketType(version=1, push=False),
            sequence_number=self.sequence_number,
            pixel_config=self.pixel_config,
            id=self.id,
            offset=0,
            length=0,
            time_code=TimeCode(None),
        )

        return await self._slice_send(header, data)

    async def write_offset(self, data: bytes, offset: int) -> int:
        """Write pixel data to the display starting at a specific byte offset.

        This is useful for updating only a portion of your LED strip without
        resending all the data.

        Args:
            data: Raw pixel data bytes to send
            offset: Starting byte offset (not pixel offset). For RGB, offset 3 = pixel 1.

        Returns:
            The total number of bytes sent

        Examples:
            >>> # Update pixel 10 (offset = 10 * 3 = 30) to white
            >>> await conn.write_offset(bytes([255, 255, 255]), 30)
        """
        header = Header(
            packet_type=PacketType(version=1, push=False),
            sequence_number=self.sequence_number,
            pixel_config=self.pixel_config,
            id=self.id,
            offset=offset,
            length=0,
            time_code=TimeCode(None),
        )

        return await self._slice_send(header, data)

    async def write_message(self, msg: message.Message) -> int:
        """Send a JSON control message to the display.

        This is useful for things like setting brightness, changing display modes,
        or querying configuration.

        Args:
            msg: A message (typed or untyped JSON)

        Returns:
            The total number of bytes sent

        Examples:
            >>> # Send a control message
            >>> json_value = {"brightness": 128}
            >>> await conn.write_message((ID.CONTROL, json_value))
        """
        header = Header(
            packet_type=PacketType(version=1, push=False),
            sequence_number=self.sequence_number,
            pixel_config=self.pixel_config,
            id=message.message_get_id(msg),
            offset=0,
            length=0,
            time_code=TimeCode(None),
        )

        msg_data = message.message_to_bytes(msg)
        header.length = len(msg_data)

        return await self._slice_send(header, msg_data)

    async def _slice_send(self, header: Header, data: bytes) -> int:
        """Internal method to split and send data in chunks."""
        offset = header.offset
        sent = 0

        num_iterations = (len(data) + MAX_DATA_LENGTH - 1) // MAX_DATA_LENGTH
        iteration = 0

        data_offset = 0
        while data_offset < len(data):
            iteration += 1

            if iteration == num_iterations:
                header.packet_type.set_push(True)

            header.sequence_number = self.sequence_number

            chunk_end = min(data_offset + MAX_DATA_LENGTH, len(data))
            chunk = data[data_offset:chunk_end]
            header.length = len(chunk)
            header.offset = offset

            packet_len = self._assemble_packet(header, chunk)

            # Send to socket
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, self.buffer[:packet_len], self.addr)
            sent += packet_len

            # Increment sequence number
            if self.sequence_number >= 15:
                self.sequence_number = 1
            else:
                self.sequence_number += 1

            data_offset += MAX_DATA_LENGTH
            offset += MAX_DATA_LENGTH

        return sent

    def _assemble_packet(self, header: Header, data: bytes) -> int:
        """Assemble a packet into the reusable buffer.

        Returns the total packet length.
        """
        header_bytes = header.to_bytes()
        header_len = len(header_bytes)

        # Copy header
        self.buffer[:header_len] = header_bytes

        # Copy data
        self.buffer[header_len:header_len + len(data)] = data

        return header_len + len(data)

    async def get_incoming(self) -> Packet:
        """Attempt to retrieve a packet from the display (non-blocking).

        Checks if any response packets have been received from the display.

        Returns:
            A Packet if one was available

        Raises:
            NothingToReceiveError: No packets waiting
        """
        try:
            packet = self.receive_queue.get_nowait()
            return packet
        except asyncio.QueueEmpty:
            raise NothingToReceiveError()

    async def _receive_loop(self):
        """Background task that receives packets and queues them."""
        loop = asyncio.get_event_loop()
        while True:
            try:
                data, addr = await loop.sock_recvfrom(self.socket, 2048)
                packet = Packet.from_bytes(data)
                await self.receive_queue.put(packet)
            except Exception:
                # Silently ignore receive errors
                await asyncio.sleep(0.01)

    async def close(self):
        """Close the connection and cleanup resources."""
        if self._recv_task:
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass
        self.socket.close()

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'socket'):
            try:
                self.socket.close()
            except:
                pass
