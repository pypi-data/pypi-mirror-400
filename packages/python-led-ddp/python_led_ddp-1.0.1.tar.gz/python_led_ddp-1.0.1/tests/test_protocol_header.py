"""Tests for Header."""

import pytest
from ddp.protocol.header import Header
from ddp.protocol.packet_type import PacketType
from ddp.protocol.pixel_config import PixelConfig, DataType, PixelFormat
from ddp.protocol.id import ID
from ddp.protocol.timecode import TimeCode


def test_header_default():
    """Test default Header creation."""
    header = Header()
    assert header.sequence_number == 1
    assert header.offset == 0
    assert header.length == 0
    assert header.id == ID.DEFAULT


def test_header_to_bytes_10():
    """Test converting header to 10 bytes."""
    header = Header(
        packet_type=PacketType(version=1, push=True),
        sequence_number=6,
        pixel_config=PixelConfig.default(),
        id=ID.DEFAULT,
        offset=0,
        length=3,
        time_code=TimeCode(None),
    )

    data = header.to_bytes()
    assert len(data) == 10
    assert data[0] == 0x41  # Version 1, push=True
    assert data[1] == 6
    assert data[8:10] == bytes([0x00, 0x03])


def test_header_to_bytes_14_with_timecode():
    """Test converting header with timecode to 14 bytes."""
    header = Header(
        packet_type=PacketType(version=1, timecode=True, push=True),
        sequence_number=3,
        pixel_config=PixelConfig.default(),
        id=ID.DEFAULT,
        offset=100,
        length=6,
        time_code=TimeCode(12345),
    )

    data = header.to_bytes()
    assert len(data) == 14
    assert data[0] & 0x10 == 0x10  # Timecode bit set


def test_header_from_bytes_10():
    """Test parsing header from 10 bytes."""
    data = bytes([65, 6, 10, 1, 0, 0, 0, 0, 0, 3])
    header = Header.from_bytes(data)

    assert header.packet_type.version == 1
    assert header.packet_type.push is True
    assert header.sequence_number == 6
    assert header.length == 3
    assert header.offset == 0


def test_header_from_bytes_14_with_timecode():
    """Test parsing header with timecode from 14 bytes."""
    data = bytes([
        0x51, 3, 0x0D, 1,  # packet_type, seq, pixel_config, id
        0, 0, 0, 100,       # offset = 100
        0, 6,               # length = 6
        0, 0, 0x30, 0x39,   # timecode = 12345
    ])
    header = Header.from_bytes(data)

    assert header.packet_type.timecode is True
    assert header.sequence_number == 3
    assert header.offset == 100
    assert header.length == 6
    assert header.time_code.value == 12345


def test_header_from_bytes_short():
    """Test parsing header from short data."""
    data = bytes([0x41, 0x01])
    header = Header.from_bytes(data)

    # Should return default header
    assert header.sequence_number == 1


def test_header_roundtrip_10_bytes():
    """Test header roundtrip with 10 bytes."""
    original = Header(
        packet_type=PacketType(version=1, push=True),
        sequence_number=5,
        pixel_config=PixelConfig.default(),
        id=ID.DEFAULT,
        offset=0,
        length=9,
        time_code=TimeCode(None),
    )

    data = original.to_bytes()
    roundtrip = Header.from_bytes(data)

    assert roundtrip.sequence_number == 5
    assert roundtrip.length == 9


def test_header_roundtrip_14_bytes():
    """Test header roundtrip with 14 bytes (timecode)."""
    original = Header(
        packet_type=PacketType(version=1, timecode=True, push=True),
        sequence_number=3,
        pixel_config=PixelConfig.default(),
        id=ID.DEFAULT,
        offset=100,
        length=6,
        time_code=TimeCode(12345),
    )

    data = original.to_bytes()
    roundtrip = Header.from_bytes(data)

    assert roundtrip.sequence_number == 3
    assert roundtrip.offset == 100
    assert roundtrip.length == 6
    assert roundtrip.time_code.value == 12345


def test_header_equality():
    """Test header equality."""
    h1 = Header(sequence_number=1, offset=0)
    h2 = Header(sequence_number=1, offset=0)
    h3 = Header(sequence_number=2, offset=0)

    assert h1 == h2
    assert h1 != h3


def test_header_hash():
    """Test header hashing."""
    h1 = Header(sequence_number=1, offset=0)
    h2 = Header(sequence_number=1, offset=0)

    assert hash(h1) == hash(h2)


def test_header_offset_large_value():
    """Test header with large offset value."""
    header = Header(offset=0xFFFFFFFF)
    data = header.to_bytes()
    parsed = Header.from_bytes(data)

    assert parsed.offset == 0xFFFFFFFF


def test_header_length_max_value():
    """Test header with max length value."""
    header = Header(length=1500)
    data = header.to_bytes()
    parsed = Header.from_bytes(data)

    assert parsed.length == 1500


def test_header_complex_scenario():
    """Test header with complex configuration."""
    header = Header(
        packet_type=PacketType(version=3, timecode=True, storage=True, reply=True, query=True, push=True),
        sequence_number=12,
        pixel_config=PixelConfig(DataType.RGB, PixelFormat.PIXEL_24_BITS, False),
        id=ID.CONTROL,
        offset=39381,
        length=281,
        time_code=TimeCode(54321),
    )

    data = header.to_bytes()
    parsed = Header.from_bytes(data)

    assert parsed.packet_type.version == 3
    assert parsed.sequence_number == 12
    assert parsed.offset == 39381
    assert parsed.length == 281
