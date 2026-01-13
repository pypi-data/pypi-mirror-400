"""Pixel format configuration for DDP packets."""

from enum import IntEnum
from dataclasses import dataclass


class DataType(IntEnum):
    """Pixel data type (color space)."""
    UNDEFINED = 0
    RGB = 1
    HSL = 2
    RGBW = 3
    GRAYSCALE = 4


class PixelFormat(IntEnum):
    """Number of bits per pixel."""
    UNDEFINED = 0
    PIXEL_1_BIT = 1
    PIXEL_4_BITS = 2
    PIXEL_8_BITS = 3
    PIXEL_16_BITS = 4
    PIXEL_24_BITS = 5
    PIXEL_32_BITS = 6


@dataclass
class PixelConfig:
    """Pixel format configuration.

    Describes how pixel data is encoded in the packet. The default configuration
    is RGB with 8 bits per channel (24 bits total per pixel).

    Examples:
        >>> # Default: RGB, 8 bits per channel
        >>> config = PixelConfig.default()
        >>> assert config.data_type == DataType.RGB
        >>> assert config.data_size == PixelFormat.PIXEL_24_BITS
        >>>
        >>> # Custom: RGBW pixels
        >>> rgbw_config = PixelConfig(
        ...     data_type=DataType.RGBW,
        ...     data_size=PixelFormat.PIXEL_32_BITS,
        ...     customer_defined=False
        ... )
    """

    data_type: DataType = DataType.RGB
    data_size: PixelFormat = PixelFormat.PIXEL_24_BITS
    customer_defined: bool = False

    @staticmethod
    def default() -> 'PixelConfig':
        """Create default pixel config (RGB, 24-bit)."""
        return PixelConfig()

    @staticmethod
    def from_byte(byte: int) -> 'PixelConfig':
        """Parse pixel config from a byte."""
        # Extract data type (bits 3-5)
        data_type_val = (byte >> 3) & 0x07
        try:
            data_type = DataType(data_type_val)
        except ValueError:
            data_type = DataType.UNDEFINED

        # Extract data size (bits 0-2)
        data_size_val = byte & 0x07
        try:
            data_size = PixelFormat(data_size_val)
        except ValueError:
            data_size = PixelFormat.UNDEFINED

        # Extract customer_defined flag (bit 7)
        customer_defined = (byte >> 7) != 0

        return PixelConfig(
            data_type=data_type,
            data_size=data_size,
            customer_defined=customer_defined,
        )

    def to_byte(self) -> int:
        """Convert pixel config to a byte."""
        byte = 0

        # Set data type (bits 3-5)
        byte |= (self.data_type & 0x07) << 3

        # Set data size (bits 0-2)
        byte |= self.data_size & 0x07

        # Set customer_defined flag (bit 7)
        if self.customer_defined:
            byte |= 0x80

        return byte

    def __eq__(self, other):
        if not isinstance(other, PixelConfig):
            return False
        return (
            self.data_type == other.data_type
            and self.data_size == other.data_size
            and self.customer_defined == other.customer_defined
        )

    def __hash__(self):
        return hash((self.data_type, self.data_size, self.customer_defined))
