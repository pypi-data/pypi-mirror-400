import pytest
from shuttle import prodtest


def test_command_ensure_byte_raises():
    with pytest.raises(ValueError, match="Prodtest arguments must be in range 0..255"):
        prodtest.command(0x01, [256])


def test_command_bytes_argument():
    # Should not raise
    cmd = prodtest.command(0x01, b"\x01\x02")
    assert cmd["tx"] == "010102"
