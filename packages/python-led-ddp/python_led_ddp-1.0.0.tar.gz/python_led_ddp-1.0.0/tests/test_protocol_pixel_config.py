"""Tests for PixelConfig."""

import pytest
from ddp.protocol.pixel_config import PixelConfig, DataType, PixelFormat


def test_pixel_config_default():
    """Test default PixelConfig creation."""
    config = PixelConfig.default()
    assert config.data_type == DataType.RGB
    assert config.data_size == PixelFormat.PIXEL_24_BITS
    assert config.customer_defined is False


def test_pixel_config_from_byte_rgb_24():
    """Test parsing RGB 24-bit config."""
    byte = 0x0D
    config = PixelConfig.from_byte(byte)

    assert config.data_type == DataType.RGB
    assert config.data_size == PixelFormat.PIXEL_24_BITS
    assert config.customer_defined is False


def test_pixel_config_from_byte_rgbw_32():
    """Test parsing RGBW 32-bit config."""
    byte = 0x1E
    config = PixelConfig.from_byte(byte)

    assert config.data_type == DataType.RGBW
    assert config.data_size == PixelFormat.PIXEL_32_BITS
    assert config.customer_defined is False


def test_pixel_config_from_byte_rgb_4():
    """Test parsing RGB 4-bit config."""
    byte = 0x0A
    config = PixelConfig.from_byte(byte)

    assert config.data_type == DataType.RGB
    assert config.data_size == PixelFormat.PIXEL_4_BITS
    assert config.customer_defined is False


def test_pixel_config_to_byte():
    """Test converting PixelConfig to byte."""
    config = PixelConfig(
        data_type=DataType.RGB,
        data_size=PixelFormat.PIXEL_24_BITS,
        customer_defined=False,
    )

    byte = config.to_byte()
    assert byte == 0x0D


def test_pixel_config_customer_defined():
    """Test customer_defined flag."""
    config = PixelConfig(
        data_type=DataType.RGB,
        data_size=PixelFormat.PIXEL_24_BITS,
        customer_defined=True,
    )

    byte = config.to_byte()
    assert byte & 0x80 == 0x80

    parsed = PixelConfig.from_byte(byte)
    assert parsed.customer_defined is True


def test_pixel_config_all_data_types():
    """Test all data types."""
    for data_type in [DataType.UNDEFINED, DataType.RGB, DataType.HSL, DataType.RGBW, DataType.GRAYSCALE]:
        config = PixelConfig(data_type=data_type, data_size=PixelFormat.PIXEL_8_BITS)
        byte = config.to_byte()
        parsed = PixelConfig.from_byte(byte)
        assert parsed.data_type == data_type


def test_pixel_config_all_pixel_formats():
    """Test all pixel formats."""
    formats = [
        PixelFormat.UNDEFINED,
        PixelFormat.PIXEL_1_BIT,
        PixelFormat.PIXEL_4_BITS,
        PixelFormat.PIXEL_8_BITS,
        PixelFormat.PIXEL_16_BITS,
        PixelFormat.PIXEL_24_BITS,
        PixelFormat.PIXEL_32_BITS,
    ]

    for pixel_format in formats:
        config = PixelConfig(data_type=DataType.RGB, data_size=pixel_format)
        byte = config.to_byte()
        parsed = PixelConfig.from_byte(byte)
        assert parsed.data_size == pixel_format


def test_pixel_config_equality():
    """Test PixelConfig equality."""
    config1 = PixelConfig(DataType.RGB, PixelFormat.PIXEL_24_BITS, False)
    config2 = PixelConfig(DataType.RGB, PixelFormat.PIXEL_24_BITS, False)
    config3 = PixelConfig(DataType.RGBW, PixelFormat.PIXEL_32_BITS, False)

    assert config1 == config2
    assert config1 != config3


def test_pixel_config_hash():
    """Test PixelConfig hashing."""
    config1 = PixelConfig(DataType.RGB, PixelFormat.PIXEL_24_BITS, False)
    config2 = PixelConfig(DataType.RGB, PixelFormat.PIXEL_24_BITS, False)

    assert hash(config1) == hash(config2)


def test_pixel_config_roundtrip():
    """Test PixelConfig roundtrip conversion."""
    original = PixelConfig(DataType.RGBW, PixelFormat.PIXEL_32_BITS, True)
    byte = original.to_byte()
    roundtrip = PixelConfig.from_byte(byte)

    assert original == roundtrip
