"""Tests for error types."""

import pytest
from ddp.error import (
    DDPError,
    DisconnectError,
    NoValidSocketAddrError,
    ParseError,
    UnknownClientError,
    InvalidPacketError,
    NothingToReceiveError,
)


def test_ddp_error_base():
    """Test base DDPError exception."""
    error = DDPError("test error")
    assert str(error) == "test error"
    assert isinstance(error, Exception)


def test_disconnect_error():
    """Test DisconnectError exception."""
    error = DisconnectError("socket error")
    assert str(error) == "socket error"
    assert isinstance(error, DDPError)


def test_no_valid_socket_addr_error():
    """Test NoValidSocketAddrError exception."""
    error = NoValidSocketAddrError()
    assert "No valid socket addr found" in str(error)
    assert isinstance(error, DDPError)


def test_parse_error():
    """Test ParseError exception."""
    error = ParseError("json parse failed")
    assert str(error) == "json parse failed"
    assert isinstance(error, DDPError)


def test_unknown_client_error():
    """Test UnknownClientError exception."""
    addr = ("192.168.1.1", 8080)
    data = bytes([0x01, 0x02, 0x03])
    error = UnknownClientError(addr, data)

    assert error.from_addr == addr
    assert error.data == data
    assert "192.168.1.1" in str(error)
    assert "8080" in str(error)
    assert "[1, 2, 3]" in str(error)
    assert isinstance(error, DDPError)


def test_invalid_packet_error():
    """Test InvalidPacketError exception."""
    error = InvalidPacketError()
    assert "Invalid packet" in str(error)
    assert isinstance(error, DDPError)


def test_nothing_to_receive_error():
    """Test NothingToReceiveError exception."""
    error = NothingToReceiveError()
    assert "no packets waiting" in str(error).lower()
    assert isinstance(error, DDPError)
