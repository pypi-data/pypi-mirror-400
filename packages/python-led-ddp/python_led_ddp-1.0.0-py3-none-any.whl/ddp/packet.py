"""Packet parsing for receiving data from DDP displays.

This module provides the Packet type for parsing incoming DDP packets,
typically used when receiving responses from displays.
"""

from typing import Optional
from dataclasses import dataclass
import json

from ddp.protocol.header import Header
from ddp.protocol.id import ID
from ddp.protocol import message


@dataclass
class Packet:
    """A parsed DDP packet received from a display.

    This struct represents packets sent back by displays, such as status updates,
    configuration responses, or acknowledgments.

    Examples:
        >>> # Parse a packet from raw bytes
        >>> bytes_data = bytes([
        ...     0x41, 0x01, 0x0D, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03,
        ...     0xFF, 0x00, 0x00  # 1 RGB pixel: red
        ... ])
        >>> packet = Packet.from_bytes(bytes_data)
        >>>
        >>> assert packet.header.sequence_number == 1
        >>> assert packet.data == bytes([0xFF, 0x00, 0x00])
    """

    header: Header
    data: bytes
    parsed: Optional[message.Message] = None

    @staticmethod
    def from_data(h: Header, d: bytes) -> 'Packet':
        """Create a packet from a header and data slice (without parsing)."""
        return Packet(header=h, data=d, parsed=None)

    @staticmethod
    def from_bytes(data: bytes) -> 'Packet':
        """Parse a DDP packet from raw bytes.

        This method handles both 10-byte and 14-byte headers (with timecode),
        and attempts to parse JSON messages if the packet is a reply/query.

        Args:
            data: Raw packet bytes including header and data

        Returns:
            A parsed Packet. If parsing fails, returns a default packet with empty data.

        Examples:
            >>> bytes_data = bytes([
            ...     0x41, 0x01, 0x0D, 0x01,           # Packet type, seq, config, id
            ...     0x00, 0x00, 0x00, 0x00,           # Offset
            ...     0x00, 0x06,                        # Length = 6
            ...     0xFF, 0x00, 0x00,                 # Pixel 1: Red
            ...     0x00, 0xFF, 0x00,                 # Pixel 2: Green
            ... ])
            >>> packet = Packet.from_bytes(bytes_data)
            >>> assert len(packet.data) == 6
        """
        # Ensure we have at least 10 bytes for the minimum header
        if len(data) < 10:
            return Packet(header=Header(), data=b'', parsed=None)

        # First, parse just enough to check if timecode is present
        has_timecode = (data[0] & 0b00010000) != 0
        header_size = 14 if has_timecode else 10

        # Ensure we have enough bytes for the header
        if len(data) < header_size:
            return Packet(header=Header(), data=b'', parsed=None)

        header_bytes = data[0:header_size]
        header = Header.from_bytes(header_bytes)
        packet_data = data[header_size:]

        parsed_msg: Optional[message.Message] = None

        if header.packet_type.reply:
            # Try to parse the data into typed structs in the spec
            try:
                if header.id == ID.CONTROL:
                    parsed_dict = json.loads(packet_data.decode('utf-8'))
                    parsed_msg = message.ControlRoot.from_dict(parsed_dict)
                elif header.id == ID.CONFIG:
                    parsed_dict = json.loads(packet_data.decode('utf-8'))
                    parsed_msg = message.ConfigRoot.from_dict(parsed_dict)
                elif header.id == ID.STATUS:
                    parsed_dict = json.loads(packet_data.decode('utf-8'))
                    parsed_msg = message.StatusRoot.from_dict(parsed_dict)
            except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
                # Try untyped JSON
                if header.id in (ID.CONTROL, ID.CONFIG, ID.STATUS):
                    try:
                        parsed_dict = json.loads(packet_data.decode('utf-8'))
                        parsed_msg = (header.id, parsed_dict)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Try unparsed string
                        try:
                            parsed_str = packet_data.decode('utf-8')
                            parsed_msg = (header.id, parsed_str)
                        except UnicodeDecodeError:
                            # Give up, just keep data as bytes
                            pass

        return Packet(header=header, data=packet_data, parsed=parsed_msg)

    def __eq__(self, other):
        if not isinstance(other, Packet):
            return False
        return (
            self.header == other.header
            and self.data == other.data
            and self.parsed == other.parsed
        )
