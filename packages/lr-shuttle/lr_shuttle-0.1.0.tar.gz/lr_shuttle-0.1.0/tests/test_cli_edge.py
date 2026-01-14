import pytest
from shuttle import cli


def test_normalize_choice_invalid():
    with pytest.raises(Exception) as excinfo:
        cli._normalize_choice("invalid", name="cs_active")
    assert "cs_active must be one of" in str(excinfo.value)


def test_normalize_uart_parity_invalid():
    with pytest.raises(Exception) as excinfo:
        cli._normalize_uart_parity("bad")
    assert "parity must be one of" in str(excinfo.value)
