# ENTIRELY AI TRANSLATED FROM A DDP LIB I WORKED ON IN RUST!!!
DO NOT TRUST IT! UNTESTED! NOT VETTED! I DONT USE PYTHYON!


# Python DDP

Distributed Display Protocol (DDP) implementation in Python, translated from the Rust [ddp-rs](https://github.com/coral/ddp-rs) library.

This library allows you to write pixel data to LED strips over the [Distributed Display Protocol (DDP)](http://www.3waylabs.com/ddp/) by 3waylabs.

You can use this to stream pixel data to [WLED](https://github.com/Aircoookie/WLED) or any other DDP-capable receiver.

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from ddp import DDPConnection
from ddp.protocol import PixelConfig, ID

async def main():
    # Create a connection to your LED controller
    conn = await DDPConnection.create(
        "192.168.1.40:4048",       # Device IP and DDP port
        PixelConfig.default(),      # RGB, 8 bits per channel
        ID.DEFAULT,                 # Default ID
    )

    # Send RGB pixel data (2 pixels: red and blue)
    await conn.write(bytes([
        255, 0, 0,    # First pixel: Red
        0, 0, 255,    # Second pixel: Blue
    ]))

    await conn.close()

asyncio.run(main())
```

## Features

- **Async/await support** using `asyncio`
- **Automatic packet chunking** for large pixel arrays
- **Sequence numbering** with automatic wrapping
- **Offset support** for updating portions of LED strips
- **JSON control messages** for device configuration
- **Comprehensive type hints** for better IDE support

## Examples

The `examples/` directory contains several examples:

- **dev.py**: Simple color cycling example
- **consoleserver.py**: DDP server that displays received packets in the terminal
- **longstrip.py**: Demonstrates using offsets with longer LED strips

Run an example:
```bash
python examples/dev.py 192.168.1.40:4048
```

## Testing

Run the test suite:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

## Protocol Overview

DDP is designed for sending real-time data to distributed lighting displays where synchronization may be important. The protocol uses a 10 or 14 byte header followed by pixel data or JSON control messages.

### Key Features

- Small, simple, extensible protocol
- Efficient packet structure (94.9% efficiency vs 72.7% for E1.31)
- Support for up to 480 RGB pixels per packet (1440 bytes)
- Optional timecode support for synchronization
- JSON-based configuration and status messages

## API Documentation

### DDPConnection

Main class for sending pixel data to DDP displays.

#### Methods

- `create(addr, pixel_config, id)` - Create a new connection
- `write(data)` - Write pixel data starting at offset 0
- `write_offset(data, offset)` - Write pixel data at a specific offset
- `write_message(msg)` - Send a JSON control message
- `get_incoming()` - Get received packets (non-blocking)
- `close()` - Close the connection

### Protocol Types

- `PixelConfig` - Pixel format configuration (RGB, RGBW, etc.)
- `ID` - Protocol IDs (DEFAULT, CONTROL, CONFIG, STATUS, etc.)
- `Header` - DDP packet header
- `PacketType` - Packet type flags
- `TimeCode` - Optional timecode for synchronization

## License

MIT

## Credits

Translated from the Rust [ddp-rs](https://github.com/coral/ddp-rs) library.

DDP protocol specification: http://www.3waylabs.com/ddp/
