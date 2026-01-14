import pytest
from shuttle import timo


def test_write_reg_sequence_valid():
    seq = timo.write_reg_sequence(5, b"\xca\xfe")
    assert len(seq) == 2
    assert seq[0]["tx"] == bytes([0x40 | 5]).hex()
    assert seq[1]["tx"] == bytes([timo.READ_REG_DUMMY, 0xCA, 0xFE]).hex()


def test_write_reg_sequence_invalid_addr():
    with pytest.raises(ValueError):
        timo.write_reg_sequence(64, b"\x01")


def test_write_reg_sequence_invalid_len():
    with pytest.raises(ValueError):
        timo.write_reg_sequence(1, b"")
    with pytest.raises(ValueError):
        timo.write_reg_sequence(1, b"A" * (timo.READ_REG_MAX_LEN + 1))


def test_parse_write_reg_response_errors():
    # Not enough frames
    with pytest.raises(ValueError):
        timo.parse_write_reg_response(0, b"\x01", ["00"])
    # Command frame wrong length
    with pytest.raises(ValueError):
        timo.parse_write_reg_response(0, b"\x01", ["", "00ff"])
    with pytest.raises(ValueError):
        timo.parse_write_reg_response(0, b"\x01", ["abcd", "00ff"])
    # Payload frame too short
    with pytest.raises(ValueError):
        timo.parse_write_reg_response(0, b"\x01", ["00", ""])
    # Valid parse
    result = timo.parse_write_reg_response(2, b"\xaa\xbb", ["40", "00"])
    assert result.address == 2
    assert result.data == b"\xaa\xbb"
    assert result.irq_flags_command == 0x40
    assert result.irq_flags_payload == 0x00
