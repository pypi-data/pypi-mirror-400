"""Distributed Display Protocol (DDP) implementation in Python.

This package allows you to write pixel data to LED strips over the
Distributed Display Protocol (DDP) by 3waylabs.

You can use this to stream pixel data to WLED or any other DDP-capable receiver.

Example:
    >>> import asyncio
    >>> from ddp import DDPConnection
    >>> from ddp.protocol import PixelConfig, ID
    >>>
    >>> async def main():
    ...     conn = await DDPConnection.create(
    ...         "192.168.1.40:4048",
    ...         PixelConfig.default(),
    ...         ID.DEFAULT
    ...     )
    ...     await conn.write(bytes([255, 0, 0, 0, 255, 0, 0, 0, 255]))
    >>>
    >>> asyncio.run(main())
"""

from ddp.connection import DDPConnection
from ddp.protocol import PixelConfig, ID, Header, PacketType
from ddp.packet import Packet
from ddp.error import DDPError

__version__ = "1.0.0"
__all__ = [
    "DDPConnection",
    "PixelConfig",
    "ID",
    "Header",
    "PacketType",
    "Packet",
    "DDPError",
]
