"""Timecode support for DDP synchronization."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class TimeCode:
    """DDP timecode for synchronized playback.

    The timecode is the 32 middle bits of 64-bit NTP time:
    16-bits for seconds and 16-bits for fraction of seconds.
    """

    value: Optional[int] = None

    @staticmethod
    def from_bytes(data: bytes) -> 'TimeCode':
        """Parse timecode from 4 bytes (big-endian)."""
        if len(data) < 4:
            return TimeCode(None)
        value = int.from_bytes(data[:4], byteorder='big')
        return TimeCode(value)

    def to_bytes(self) -> bytes:
        """Convert timecode to 4 bytes (big-endian)."""
        value = self.value if self.value is not None else 0
        return value.to_bytes(4, byteorder='big')

    def __eq__(self, other):
        if not isinstance(other, TimeCode):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
