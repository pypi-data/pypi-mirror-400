"""Tests for TimeCode."""

import pytest
from ddp.protocol.timecode import TimeCode


def test_timecode_default():
    """Test default TimeCode creation."""
    tc = TimeCode()
    assert tc.value is None


def test_timecode_with_value():
    """Test TimeCode with a value."""
    tc = TimeCode(12345)
    assert tc.value == 12345


def test_timecode_from_bytes():
    """Test parsing TimeCode from bytes."""
    data = bytes([0x00, 0x00, 0x30, 0x39])  # 12345 in big-endian
    tc = TimeCode.from_bytes(data)
    assert tc.value == 12345


def test_timecode_from_bytes_zero():
    """Test parsing zero TimeCode."""
    data = bytes([0x00, 0x00, 0x00, 0x00])
    tc = TimeCode.from_bytes(data)
    assert tc.value == 0


def test_timecode_from_bytes_max():
    """Test parsing max TimeCode."""
    data = bytes([0xFF, 0xFF, 0xFF, 0xFF])
    tc = TimeCode.from_bytes(data)
    assert tc.value == 0xFFFFFFFF


def test_timecode_from_bytes_short():
    """Test parsing TimeCode from short data."""
    data = bytes([0x00, 0x00])
    tc = TimeCode.from_bytes(data)
    assert tc.value is None


def test_timecode_to_bytes_some():
    """Test converting TimeCode with value to bytes."""
    tc = TimeCode(12345)
    data = tc.to_bytes()
    assert data == bytes([0x00, 0x00, 0x30, 0x39])


def test_timecode_to_bytes_none():
    """Test converting TimeCode with None to bytes."""
    tc = TimeCode(None)
    data = tc.to_bytes()
    assert data == bytes([0x00, 0x00, 0x00, 0x00])


def test_timecode_to_bytes_zero():
    """Test converting zero TimeCode to bytes."""
    tc = TimeCode(0)
    data = tc.to_bytes()
    assert data == bytes([0x00, 0x00, 0x00, 0x00])


def test_timecode_to_bytes_max():
    """Test converting max TimeCode to bytes."""
    tc = TimeCode(0xFFFFFFFF)
    data = tc.to_bytes()
    assert data == bytes([0xFF, 0xFF, 0xFF, 0xFF])


def test_timecode_roundtrip():
    """Test TimeCode roundtrip conversion."""
    original = TimeCode(98765)
    data = original.to_bytes()
    roundtrip = TimeCode.from_bytes(data)
    assert original == roundtrip


def test_timecode_roundtrip_various_values():
    """Test TimeCode roundtrip with various values."""
    test_values = [0, 1, 255, 256, 65535, 65536, 16777215, 16777216, 0xFFFFFFFF]

    for value in test_values:
        original = TimeCode(value)
        data = original.to_bytes()
        roundtrip = TimeCode.from_bytes(data)
        assert original == roundtrip, f"Failed roundtrip for value {value}"


def test_timecode_equality():
    """Test TimeCode equality."""
    tc1 = TimeCode(100)
    tc2 = TimeCode(100)
    tc3 = TimeCode(200)

    assert tc1 == tc2
    assert tc1 != tc3


def test_timecode_hash():
    """Test TimeCode hashing."""
    tc1 = TimeCode(12345)
    tc2 = TimeCode(12345)
    tc3 = TimeCode(54321)

    assert hash(tc1) == hash(tc2)
    assert hash(tc1) != hash(tc3)


def test_timecode_big_endian_encoding():
    """Test that TimeCode uses big-endian byte order."""
    tc = TimeCode(0x12345678)
    data = tc.to_bytes()
    assert data[0] == 0x12  # Most significant byte first
    assert data[1] == 0x34
    assert data[2] == 0x56
    assert data[3] == 0x78  # Least significant byte last
