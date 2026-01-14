import pytest
import tempfile
from pathlib import Path
import shuttle.cli as cli_module
import shuttle.serial_client as serial_client_module


class DummyError(Exception):
    pass


def test_normalize_choice_none():
    assert cli_module._normalize_choice(None, name="cs_active") is None


def test_normalize_choice_unknown_field():
    assert cli_module._normalize_choice("foo", name="unknown") == "foo"


def test_normalize_choice_invalid():
    with pytest.raises(Exception):
        cli_module._normalize_choice("invalid", name="cs_active")


def test_normalize_choice_valid():
    assert cli_module._normalize_choice("low", name="cs_active") == "low"
    assert cli_module._normalize_choice("HIGH", name="cs_active") == "high"


def test_normalize_uart_parity_none():
    assert cli_module._normalize_uart_parity(None) is None


def test_normalize_uart_parity_empty():
    assert cli_module._normalize_uart_parity("   ") is None


def test_normalize_uart_parity_alias():
    assert cli_module._normalize_uart_parity("even") == "e"
    assert cli_module._normalize_uart_parity("odd") == "o"
    assert cli_module._normalize_uart_parity("none") == "n"


def test_normalize_uart_parity_first_letter():
    assert cli_module._normalize_uart_parity("Oddball") == "o"
    assert cli_module._normalize_uart_parity("Evening") == "e"
    assert cli_module._normalize_uart_parity("Normal") == "n"


def test_normalize_uart_parity_invalid():
    with pytest.raises(Exception):
        cli_module._normalize_uart_parity("bad")


def test_sequence_tracker_file(tmp_path):
    meta = tmp_path / "seq.meta"
    # Write a valid integer
    meta.write_text("42")
    tracker = serial_client_module.SequenceTracker(meta)
    assert tracker._last_seq == 42
    # Write a non-integer
    meta.write_text("notanint")
    with pytest.raises(Exception):
        serial_client_module.SequenceTracker(meta)


def test_sequence_tracker_observe_gap(tmp_path):
    meta = tmp_path / "seq.meta"
    tracker = serial_client_module.SequenceTracker(meta)
    tracker.observe(1, source="test")
    assert tracker._last_seq == 1
    # Should persist and raise on gap
    with pytest.raises(Exception):
        tracker.observe(3, source="test")
    # Should accept next in sequence
    tracker.observe(4, source="test")
    assert tracker._last_seq == 4


def test_sequence_tracker_persist_error(monkeypatch, tmp_path):
    meta = tmp_path / "seq.meta"
    tracker = serial_client_module.SequenceTracker(meta)

    def fail_write(*a, **k):
        raise OSError("fail")

    monkeypatch.setattr("pathlib.Path.write_text", fail_write)
    tracker._last_seq = 1
    with pytest.raises(Exception):
        tracker._persist()
