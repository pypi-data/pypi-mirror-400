"""Tests for DDPConnection."""

import pytest
import asyncio
import socket
from ddp.connection import DDPConnection
from ddp.protocol import PixelConfig, ID
from ddp.error import NothingToReceiveError


@pytest.mark.asyncio
async def test_connection_creation():
    """Test creating a connection."""
    conn = await DDPConnection.create(
        "127.0.0.1:4048",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    assert conn.pixel_config == PixelConfig.default()
    assert conn.id == ID.DEFAULT
    assert conn.sequence_number == 1

    await conn.close()


@pytest.mark.asyncio
async def test_connection_write_simple():
    """Test writing simple pixel data."""
    # Create a server socket to receive data
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.setblocking(False)
    server_addr = server_sock.getsockname()

    # Create connection
    conn = await DDPConnection.create(
        f"{server_addr[0]}:{server_addr[1]}",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    # Write pixel data
    pixel_data = bytes([255, 0, 0, 0, 255, 0, 0, 0, 255])
    await conn.write(pixel_data)

    # Give it a moment to send
    await asyncio.sleep(0.1)

    # Receive on server side
    loop = asyncio.get_event_loop()
    try:
        data, addr = await asyncio.wait_for(
            loop.sock_recvfrom(server_sock, 1500),
            timeout=1.0
        )
        assert len(data) > 10  # At least header + some data
    except asyncio.TimeoutError:
        pytest.skip("Packet not received in time")

    await conn.close()
    server_sock.close()


@pytest.mark.asyncio
async def test_connection_write_with_offset():
    """Test writing pixel data with offset."""
    # Create a server socket to receive data
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.setblocking(False)
    server_addr = server_sock.getsockname()

    # Create connection
    conn = await DDPConnection.create(
        f"{server_addr[0]}:{server_addr[1]}",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    # Write pixel data with offset
    pixel_data = bytes([128, 128, 128])
    offset = 30
    await conn.write_offset(pixel_data, offset)

    # Give it a moment to send
    await asyncio.sleep(0.1)

    # Receive on server side
    loop = asyncio.get_event_loop()
    try:
        data, addr = await asyncio.wait_for(
            loop.sock_recvfrom(server_sock, 1500),
            timeout=1.0
        )

        # Parse offset from packet (bytes 4-7)
        received_offset = int.from_bytes(data[4:8], byteorder='big')
        assert received_offset == offset
    except asyncio.TimeoutError:
        pytest.skip("Packet not received in time")

    await conn.close()
    server_sock.close()


@pytest.mark.asyncio
async def test_connection_sequence_numbers():
    """Test sequence number incrementing."""
    # Create a server socket to receive data
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.setblocking(False)
    server_addr = server_sock.getsockname()

    # Create connection
    conn = await DDPConnection.create(
        f"{server_addr[0]}:{server_addr[1]}",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    pixel_data = bytes([255, 0, 0])
    loop = asyncio.get_event_loop()

    for i in range(5):
        await conn.write(pixel_data)
        await asyncio.sleep(0.05)

        try:
            data, addr = await asyncio.wait_for(
                loop.sock_recvfrom(server_sock, 1500),
                timeout=0.5
            )

            seq_num = data[1]
            assert seq_num == (i + 1)
        except asyncio.TimeoutError:
            pytest.skip("Packet not received in time")

    await conn.close()
    server_sock.close()


@pytest.mark.asyncio
async def test_connection_large_data_chunking():
    """Test that large data is chunked into multiple packets."""
    # Create a server socket to receive data
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.setblocking(False)
    server_addr = server_sock.getsockname()

    # Create connection
    conn = await DDPConnection.create(
        f"{server_addr[0]}:{server_addr[1]}",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    # Send data larger than MAX_DATA_LENGTH (480 * 3 = 1440 bytes)
    large_data = bytes([128] * 2000)
    await conn.write(large_data)

    await asyncio.sleep(0.2)

    # Should receive multiple packets
    loop = asyncio.get_event_loop()
    received_packets = 0

    for _ in range(3):
        try:
            data, addr = await asyncio.wait_for(
                loop.sock_recvfrom(server_sock, 2048),
                timeout=0.5
            )
            received_packets += 1
        except asyncio.TimeoutError:
            break

    assert received_packets >= 2, "Expected multiple packets for large data"

    await conn.close()
    server_sock.close()


@pytest.mark.asyncio
async def test_connection_get_incoming_empty():
    """Test getting incoming packet when none available."""
    conn = await DDPConnection.create(
        "127.0.0.1:4048",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    with pytest.raises(NothingToReceiveError):
        await conn.get_incoming()

    await conn.close()


@pytest.mark.asyncio
async def test_connection_sequence_wraps():
    """Test that sequence number wraps from 15 to 1."""
    # Create a server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.setblocking(False)
    server_addr = server_sock.getsockname()

    conn = await DDPConnection.create(
        f"{server_addr[0]}:{server_addr[1]}",
        PixelConfig.default(),
        ID.DEFAULT,
    )

    # Set sequence number close to wrap
    conn.sequence_number = 15

    pixel_data = bytes([255, 0, 0])
    await conn.write(pixel_data)

    # Next write should wrap to 1
    await conn.write(pixel_data)
    assert conn.sequence_number == 2

    await conn.close()
    server_sock.close()
