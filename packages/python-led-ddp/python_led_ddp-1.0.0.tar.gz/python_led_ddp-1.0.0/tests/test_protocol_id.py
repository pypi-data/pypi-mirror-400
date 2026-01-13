"""Tests for ID."""

import pytest
from ddp.protocol.id import ID


def test_id_reserved():
    """Test reserved ID."""
    assert ID.RESERVED == 0


def test_id_default():
    """Test default ID."""
    assert ID.DEFAULT == 1


def test_id_control():
    """Test control ID."""
    assert ID.CONTROL == 246


def test_id_config():
    """Test config ID."""
    assert ID.CONFIG == 250


def test_id_status():
    """Test status ID."""
    assert ID.STATUS == 251


def test_id_dmx():
    """Test DMX ID."""
    assert ID.DMX == 254


def test_id_broadcast():
    """Test broadcast ID."""
    assert ID.BROADCAST == 255


def test_id_from_value_standard():
    """Test creating ID from standard values."""
    assert ID.from_value(0) == ID.RESERVED
    assert ID.from_value(1) == ID.DEFAULT
    assert ID.from_value(246) == ID.CONTROL
    assert ID.from_value(250) == ID.CONFIG
    assert ID.from_value(251) == ID.STATUS
    assert ID.from_value(254) == ID.DMX
    assert ID.from_value(255) == ID.BROADCAST


def test_id_from_value_custom():
    """Test creating ID from custom values."""
    custom_id = ID.from_value(42)
    assert custom_id == 42


def test_id_to_byte():
    """Test converting ID to byte."""
    assert ID.DEFAULT.to_byte() == 1
    assert ID.CONTROL.to_byte() == 246
    assert ID.STATUS.to_byte() == 251


def test_id_is_custom():
    """Test checking if value is custom ID."""
    assert ID.is_custom(42) is True
    assert ID.is_custom(245) is True
    assert ID.is_custom(247) is True
    assert ID.is_custom(248) is True
    assert ID.is_custom(249) is True
    assert ID.is_custom(252) is True
    assert ID.is_custom(253) is True

    assert ID.is_custom(0) is False
    assert ID.is_custom(1) is False
    assert ID.is_custom(246) is False
    assert ID.is_custom(250) is False
    assert ID.is_custom(251) is False
    assert ID.is_custom(254) is False
    assert ID.is_custom(255) is False
