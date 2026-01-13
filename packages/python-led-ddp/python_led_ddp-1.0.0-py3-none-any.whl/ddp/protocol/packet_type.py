"""Packet type flags that control protocol behavior."""

from dataclasses import dataclass


@dataclass
class PacketType:
    """Packet type flags encoded in byte 0 of the header.

    Flag Bits:
    - Bits 6-7: Protocol version (1-4)
    - Bit 4: Timecode present (if set, header is 14 bytes instead of 10)
    - Bit 3: Storage (for persisting settings)
    - Bit 2: Reply (packet is a response)
    - Bit 1: Query (request information)
    - Bit 0: Push (final packet in sequence)
    """

    version: int = 1
    timecode: bool = False
    storage: bool = False
    reply: bool = False
    query: bool = False
    push: bool = False

    @staticmethod
    def from_byte(byte: int) -> 'PacketType':
        """Parse packet type from a byte."""
        VERSION_MASK = 0xC0
        TIMECODE = 0x10
        STORAGE = 0x08
        REPLY = 0x04
        QUERY = 0x02
        PUSH = 0x01

        version_bits = byte & VERSION_MASK
        if version_bits == 0x00:
            version = 0
        elif version_bits == 0x40:
            version = 1
        elif version_bits == 0x80:
            version = 2
        elif version_bits == 0xC0:
            version = 3
        else:
            version = 0

        return PacketType(
            version=version,
            timecode=(byte & TIMECODE) == TIMECODE,
            storage=(byte & STORAGE) == STORAGE,
            reply=(byte & REPLY) == REPLY,
            query=(byte & QUERY) == QUERY,
            push=(byte & PUSH) == PUSH,
        )

    def to_byte(self) -> int:
        """Convert packet type to a byte."""
        TIMECODE = 0x10
        STORAGE = 0x08
        REPLY = 0x04
        QUERY = 0x02
        PUSH = 0x01

        byte = 0

        # Set version bits
        if self.version in (1, 2, 3, 4):
            byte |= self.version << 6

        # Set flag bits
        if self.timecode:
            byte |= TIMECODE
        if self.storage:
            byte |= STORAGE
        if self.reply:
            byte |= REPLY
        if self.query:
            byte |= QUERY
        if self.push:
            byte |= PUSH

        return byte

    def set_push(self, push: bool) -> None:
        """Set the push flag."""
        self.push = push

    def __eq__(self, other):
        if not isinstance(other, PacketType):
            return False
        return (
            self.version == other.version
            and self.timecode == other.timecode
            and self.storage == other.storage
            and self.reply == other.reply
            and self.query == other.query
            and self.push == other.push
        )

    def __hash__(self):
        return hash((
            self.version,
            self.timecode,
            self.storage,
            self.reply,
            self.query,
            self.push,
        ))
