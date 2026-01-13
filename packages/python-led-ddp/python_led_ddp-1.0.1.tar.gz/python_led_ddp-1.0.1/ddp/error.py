"""Error types for DDP operations.

This module defines all error types that can occur when working with DDP connections.
"""

from typing import Optional


class DDPError(Exception):
    """Base exception for all DDP errors."""
    pass


class DisconnectError(DDPError):
    """Socket or network I/O error."""
    pass


class NoValidSocketAddrError(DDPError):
    """Failed to resolve the provided address."""
    def __init__(self):
        super().__init__("No valid socket addr found")


class ParseError(DDPError):
    """JSON parsing error for control messages."""
    pass


class UnknownClientError(DDPError):
    """Received data from an unknown or unexpected client."""

    def __init__(self, from_addr: tuple, data: bytes):
        self.from_addr = from_addr
        self.data = data
        super().__init__(
            f"invalid sender, did you forget to connect() (data from {from_addr} - {list(data)})"
        )


class InvalidPacketError(DDPError):
    """Received packet with invalid format or structure."""
    def __init__(self):
        super().__init__("Invalid packet")


class NothingToReceiveError(DDPError):
    """No packets are currently available to receive (non-blocking operation)."""
    def __init__(self):
        super().__init__(
            "There are no packets waiting to be read. This error should be handled explicitly"
        )
