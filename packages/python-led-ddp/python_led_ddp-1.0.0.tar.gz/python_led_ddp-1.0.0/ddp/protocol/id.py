"""Protocol ID used to identify the purpose of a packet."""

from enum import IntEnum


class ID(IntEnum):
    """Protocol ID used to identify the purpose of a packet.

    IDs are used to differentiate between pixel data, control messages, configuration
    queries, and other packet types. The ID space is divided into several ranges:

    - 0: Reserved
    - 1: Default (standard pixel data)
    - 2-245, 247-249: Custom IDs for application-specific use
    - 246: Control messages (JSON control read/write)
    - 250: Configuration messages (JSON config read/write)
    - 251: Status messages (JSON status read-only)
    - 254: DMX data
    - 255: Broadcast to all displays

    Examples:
        >>> # Standard pixel data
        >>> pixel_id = ID.DEFAULT
        >>>
        >>> # Control message
        >>> control_id = ID.CONTROL
        >>>
        >>> # Custom application ID
        >>> custom_id = ID.from_value(42)
    """

    RESERVED = 0
    DEFAULT = 1
    CONTROL = 246
    CONFIG = 250
    STATUS = 251
    DMX = 254
    BROADCAST = 255

    @staticmethod
    def from_value(value: int) -> 'ID':
        """Create ID from a byte value.

        Custom IDs (2-245, 247-249, 252-253) are returned as their numeric value.
        """
        try:
            return ID(value)
        except ValueError:
            # For custom IDs, we'll need to handle them specially
            # Since IntEnum doesn't support dynamic values, we return a closest match
            if 2 <= value <= 245 or value in (247, 248, 249, 252, 253):
                # This is a custom ID - we'll store it as-is
                # Python's IntEnum doesn't handle this elegantly, so we work around it
                return value  # type: ignore
            else:
                return ID.DEFAULT

    def to_byte(self) -> int:
        """Convert ID to a byte value."""
        return int(self)

    @classmethod
    def is_custom(cls, value: int) -> bool:
        """Check if a value is a custom ID."""
        return (2 <= value <= 245) or value in (247, 248, 249, 252, 253)
