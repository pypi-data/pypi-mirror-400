"""Tests for Packet."""

import pytest
import json
from ddp.packet import Packet
from ddp.protocol.header import Header
from ddp.protocol.packet_type import PacketType
from ddp.protocol.pixel_config import PixelConfig
from ddp.protocol.id import ID
from ddp.protocol.timecode import TimeCode
from ddp.protocol.message import ConfigRoot, Config


def test_packet_from_data():
    """Test creating packet from data."""
    header = Header()
    data = bytes([0xFF, 0x00, 0x00])
    packet = Packet.from_data(header, data)

    assert packet.header == header
    assert packet.data == data
    assert packet.parsed is None


def test_packet_from_bytes_simple():
    """Test parsing simple packet."""
    data = bytes([
        0x41, 0x01, 0x0D, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03,
        0xFF, 0x00, 0x00  # 1 RGB pixel: red
    ])
    packet = Packet.from_bytes(data)

    assert packet.header.sequence_number == 1
    assert packet.data == bytes([0xFF, 0x00, 0x00])


def test_packet_from_bytes_multiple_pixels():
    """Test parsing packet with multiple pixels."""
    data = bytes([
        0x41, 0x01, 0x0D, 0x01,           # Packet type, seq, config, id
        0x00, 0x00, 0x00, 0x00,           # Offset
        0x00, 0x06,                        # Length = 6
        0xFF, 0x00, 0x00,                 # Pixel 1: Red
        0x00, 0xFF, 0x00,                 # Pixel 2: Green
    ])
    packet = Packet.from_bytes(data)

    assert len(packet.data) == 6
    assert packet.data == bytes([0xFF, 0x00, 0x00, 0x00, 0xFF, 0x00])


def test_packet_from_bytes_short():
    """Test parsing short/invalid packet."""
    data = bytes([0x41, 0x01])
    packet = Packet.from_bytes(data)

    assert packet.data == b''


def test_packet_from_bytes_with_timecode():
    """Test parsing packet with timecode."""
    data = bytes([
        0x51, 0x01, 0x0D, 0x01,           # With timecode bit
        0x00, 0x00, 0x00, 0x00,           # Offset
        0x00, 0x03,                        # Length = 3
        0x00, 0x00, 0x30, 0x39,           # Timecode = 12345
        0xFF, 0x00, 0x00,                 # Pixel data
    ])
    packet = Packet.from_bytes(data)

    assert packet.header.packet_type.timecode is True
    assert packet.header.time_code.value == 12345
    assert packet.data == bytes([0xFF, 0x00, 0x00])


def test_packet_from_bytes_config_json():
    """Test parsing packet with JSON config."""
    json_str = '{"config":{"gw":"192.168.1.1","ip":"192.168.1.100","nm":"255.255.255.0","ports":[]}}'
    json_bytes = json_str.encode('utf-8')

    header_data = bytes([
        0x44, 0x00, 0x0D, 0xFA,            # Reply bit set, ID=CONFIG
        0x00, 0x00, 0x00, 0x00,
        (len(json_bytes) >> 8) & 0xFF,
        len(json_bytes) & 0xFF,
    ])

    data = header_data + json_bytes
    packet = Packet.from_bytes(data)

    assert packet.header.id == ID.CONFIG
    assert packet.parsed is not None
    assert isinstance(packet.parsed, ConfigRoot)
    assert packet.parsed.config.gw == "192.168.1.1"


def test_packet_from_bytes_untyped_json():
    """Test parsing packet with untyped JSON."""
    json_str = '{"hello":"ok"}'
    json_bytes = json_str.encode('utf-8')

    header_data = bytes([
        0x44, 0x00, 0x0D, 0xFA,            # Reply bit set, ID=CONFIG
        0x00, 0x00, 0x00, 0x00,
        0x00, len(json_bytes),
    ])

    data = header_data + json_bytes
    packet = Packet.from_bytes(data)

    assert packet.parsed is not None
    assert isinstance(packet.parsed, tuple)
    assert packet.parsed[0] == ID.CONFIG
    assert packet.parsed[1]["hello"] == "ok"


def test_packet_from_bytes_unparsed_string():
    """Test parsing packet with unparsed string."""
    text = "SLICKDENIS4000"
    text_bytes = text.encode('utf-8')

    header_data = bytes([
        0x44, 0x00, 0x0D, 0xFA,            # Reply bit set, ID=CONFIG
        0x00, 0x00, 0x00, 0x00,
        0x00, len(text_bytes),
    ])

    data = header_data + text_bytes
    packet = Packet.from_bytes(data)

    assert packet.parsed is not None
    assert isinstance(packet.parsed, tuple)
    assert packet.parsed[0] == ID.CONFIG
    assert packet.parsed[1] == text


def test_packet_equality():
    """Test packet equality."""
    header1 = Header(sequence_number=1)
    header2 = Header(sequence_number=1)
    header3 = Header(sequence_number=2)

    data1 = bytes([0xFF, 0x00, 0x00])

    p1 = Packet(header1, data1)
    p2 = Packet(header2, data1)
    p3 = Packet(header3, data1)

    assert p1 == p2
    assert p1 != p3


def test_packet_large_data():
    """Test packet with large pixel data."""
    num_pixels = 480  # Max size
    pixel_data = bytearray()

    for i in range(num_pixels):
        pixel_data.extend([i % 256, (i * 2) % 256, (i * 3) % 256])

    header = Header(
        packet_type=PacketType(version=1, push=True),
        sequence_number=1,
        pixel_config=PixelConfig.default(),
        id=ID.DEFAULT,
        offset=0,
        length=len(pixel_data),
        time_code=TimeCode(None),
    )

    header_bytes = header.to_bytes()
    full_packet = header_bytes + bytes(pixel_data)

    parsed = Packet.from_bytes(full_packet)
    assert len(parsed.data) == len(pixel_data)
    assert parsed.data == bytes(pixel_data)


def test_packet_with_offset():
    """Test packet with non-zero offset."""
    header = Header(
        packet_type=PacketType(version=1, push=True),
        sequence_number=1,
        pixel_config=PixelConfig.default(),
        id=ID.DEFAULT,
        offset=100,
        length=3,
        time_code=TimeCode(None),
    )

    data = bytes([128, 128, 128])
    packet = Packet.from_data(header, data)

    assert packet.header.offset == 100
    assert packet.data == data
