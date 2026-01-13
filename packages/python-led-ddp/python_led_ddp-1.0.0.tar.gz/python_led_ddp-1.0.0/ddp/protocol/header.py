"""DDP packet header structure."""

from dataclasses import dataclass
from ddp.protocol.packet_type import PacketType
from ddp.protocol.pixel_config import PixelConfig
from ddp.protocol.id import ID
from ddp.protocol.timecode import TimeCode


@dataclass
class Header:
    """DDP packet header containing metadata and control flags.

    The header is 10 bytes (or 14 with timecode) and contains all the information
    needed to interpret the packet payload.

    Examples:
        >>> header = Header(
        ...     packet_type=PacketType(),
        ...     sequence_number=1,
        ...     pixel_config=PixelConfig.default(),
        ...     id=ID.DEFAULT,
        ...     offset=0,
        ...     length=9,
        ...     time_code=TimeCode(None)
        ... )
        >>>
        >>> # Convert to bytes for transmission
        >>> bytes_data = header.to_bytes()
    """

    packet_type: PacketType = None
    sequence_number: int = 1
    pixel_config: PixelConfig = None
    id: ID = ID.DEFAULT
    offset: int = 0
    length: int = 0
    time_code: TimeCode = None

    def __post_init__(self):
        if self.packet_type is None:
            self.packet_type = PacketType()
        if self.pixel_config is None:
            self.pixel_config = PixelConfig.default()
        if self.time_code is None:
            self.time_code = TimeCode(None)

    def to_bytes(self) -> bytes:
        """Convert header to bytes (10 or 14 bytes depending on timecode flag)."""
        buffer = bytearray(14 if self.packet_type.timecode else 10)

        # Byte 0: packet type
        buffer[0] = self.packet_type.to_byte()

        # Byte 1: sequence number
        buffer[1] = self.sequence_number & 0xFF

        # Byte 2: pixel config
        buffer[2] = self.pixel_config.to_byte()

        # Byte 3: id
        buffer[3] = int(self.id)

        # Bytes 4-7: offset (32-bit big-endian)
        buffer[4:8] = self.offset.to_bytes(4, byteorder='big')

        # Bytes 8-9: length (16-bit big-endian)
        buffer[8:10] = self.length.to_bytes(2, byteorder='big')

        # Bytes 10-13: optional timecode
        if self.packet_type.timecode:
            buffer[10:14] = self.time_code.to_bytes()

        return bytes(buffer)

    @staticmethod
    def from_bytes(data: bytes) -> 'Header':
        """Parse header from bytes."""
        if len(data) < 10:
            # Return default header if data is too short
            return Header()

        # Parse packet type to check if timecode is present
        packet_type = PacketType.from_byte(data[0])
        has_timecode = packet_type.timecode
        header_size = 14 if has_timecode else 10

        if len(data) < header_size:
            # Return default header if data is too short
            return Header()

        # Parse all fields
        sequence_number = data[1]
        pixel_config = PixelConfig.from_byte(data[2])
        id_val = ID.from_value(data[3])
        offset = int.from_bytes(data[4:8], byteorder='big')
        length = int.from_bytes(data[8:10], byteorder='big')

        if has_timecode and len(data) >= 14:
            time_code = TimeCode.from_bytes(data[10:14])
        else:
            time_code = TimeCode(None)

        return Header(
            packet_type=packet_type,
            sequence_number=sequence_number,
            pixel_config=pixel_config,
            id=id_val,
            offset=offset,
            length=length,
            time_code=time_code,
        )

    def __eq__(self, other):
        if not isinstance(other, Header):
            return False
        return (
            self.packet_type == other.packet_type
            and self.sequence_number == other.sequence_number
            and self.pixel_config == other.pixel_config
            and self.id == other.id
            and self.offset == other.offset
            and self.length == other.length
            and self.time_code == other.time_code
        )

    def __hash__(self):
        return hash((
            self.packet_type,
            self.sequence_number,
            self.pixel_config,
            self.id,
            self.offset,
            self.length,
            self.time_code,
        ))
