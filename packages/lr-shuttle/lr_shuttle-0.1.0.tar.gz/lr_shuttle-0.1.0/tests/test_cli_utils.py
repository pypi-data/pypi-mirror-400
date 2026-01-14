import pytest
import shuttle.cli as cli_module
from rich.table import Table


def test_format_hex():
    assert cli_module._format_hex("") == "—"
    assert cli_module._format_hex("00ff") == "00 ff"
    assert cli_module._format_hex("a1b2c3") == "a1 b2 c3"


def test_decode_hex_response_valid():
    resp = {"rx": "deadbeef"}
    assert cli_module._decode_hex_response(resp, label="test") == bytes.fromhex(
        "deadbeef"
    )


def test_decode_hex_response_missing(monkeypatch):
    with pytest.raises(Exception):
        cli_module._decode_hex_response({}, label="test")


def test_decode_hex_response_invalid(monkeypatch):
    with pytest.raises(Exception):
        cli_module._decode_hex_response({"rx": "nothex"}, label="test")


def test_format_failed_pins_line():
    assert cli_module._format_failed_pins_line([]) == "Test failed on pins: [ ]"
    assert (
        cli_module._format_failed_pins_line([1, 2, 3])
        == "Test failed on pins: [ 1, 2, 3 ]"
    )


def test_build_status_table_error():
    resp = {"ok": False, "err": {"code": "ERR", "msg": "fail"}}
    table = cli_module._build_status_table("title", resp)
    assert isinstance(table, Table)


def test_build_status_table_ok():
    resp = {"ok": True}
    table = cli_module._build_status_table("title", resp)
    assert isinstance(table, Table)
