"""Tests for PacketType."""

import pytest
from ddp.protocol.packet_type import PacketType


def test_packet_type_default():
    """Test default PacketType creation."""
    pt = PacketType()
    assert pt.version == 1
    assert pt.timecode is False
    assert pt.storage is False
    assert pt.reply is False
    assert pt.query is False
    assert pt.push is False


def test_packet_type_from_byte():
    """Test parsing PacketType from byte."""
    byte = 0b00010110
    pt = PacketType.from_byte(byte)

    assert pt.version == 0
    assert pt.timecode is True
    assert pt.storage is False
    assert pt.reply is True
    assert pt.query is True
    assert pt.push is False


def test_packet_type_to_byte():
    """Test converting PacketType to byte."""
    pt = PacketType(
        version=1,
        timecode=True,
        storage=False,
        reply=True,
        query=True,
        push=False,
    )

    byte = pt.to_byte()
    assert byte == 0x56


def test_packet_type_set_push():
    """Test setting push flag."""
    pt = PacketType()
    assert pt.push is False

    pt.set_push(True)
    assert pt.push is True

    pt.set_push(False)
    assert pt.push is False


def test_packet_type_version_bits():
    """Test version bit encoding."""
    for version in range(4):
        pt = PacketType(version=version)
        byte = pt.to_byte()
        parsed = PacketType.from_byte(byte)
        assert parsed.version == version


def test_packet_type_all_flags():
    """Test all flag combinations."""
    pt = PacketType(
        version=3,
        timecode=True,
        storage=True,
        reply=True,
        query=True,
        push=True,
    )

    byte = pt.to_byte()
    parsed = PacketType.from_byte(byte)

    assert parsed.version == 3
    assert parsed.timecode is True
    assert parsed.storage is True
    assert parsed.reply is True
    assert parsed.query is True
    assert parsed.push is True


def test_packet_type_equality():
    """Test PacketType equality."""
    pt1 = PacketType(version=1, push=True)
    pt2 = PacketType(version=1, push=True)
    pt3 = PacketType(version=2, push=True)

    assert pt1 == pt2
    assert pt1 != pt3


def test_packet_type_hash():
    """Test PacketType hashing."""
    pt1 = PacketType(version=1, push=True)
    pt2 = PacketType(version=1, push=True)

    assert hash(pt1) == hash(pt2)


def test_packet_type_roundtrip():
    """Test PacketType roundtrip conversion."""
    original = PacketType(version=2, timecode=True, push=True)
    byte = original.to_byte()
    roundtrip = PacketType.from_byte(byte)

    assert original == roundtrip
