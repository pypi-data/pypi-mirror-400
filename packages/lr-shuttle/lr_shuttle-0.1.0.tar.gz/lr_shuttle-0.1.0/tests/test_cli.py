def test_timo_read_dmx_executes_two_phase_sequence(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    calls = []

    class ReadDMXClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_xfer(self, *, tx: str, n: int, **_overrides):
            calls.append({"tx": tx, "n": n})
            if len(calls) == 1:
                return {"type": "resp", "id": 1, "ok": True, "rx": "81", "seq": 10}
            return {"type": "resp", "id": 2, "ok": True, "rx": "00cafe", "seq": 11}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", ReadDMXClient)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "read-dmx", "--port", "/dev/ttyUSB0", "--length", "2"],
    )
    assert result.exit_code == 0
    assert "TiMo read-dmx" in result.stdout
    assert "ca fe" in result.stdout or "cafe" in result.stdout
    assert calls == [{"tx": "81", "n": 1}, {"tx": "ff0000", "n": 3}]


def test_timo_read_dmx_invalid_length(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(
        app, ["timo", "read-dmx", "--port", "/dev/ttyUSB0", "--length", "0"]
    )
    assert result.exit_code != 0
    # Accept Typer's error message for out-of-range values
    assert (
        "Invalid value for '--length'" in result.stdout
        or "Invalid value for '--length'" in result.stderr
        or "length must be 1" in result.stdout
        or "length must be 1" in result.stderr
    )


def test_timo_read_dmx_handles_failed_phase(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [{"type": "resp", "id": 1, "ok": False, "rx": "", "seq": 1}]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app, ["timo", "read-dmx", "--port", "/dev/ttyUSB0", "--length", "2"]
    )
    assert result.exit_code == 1
    assert "command" in result.stdout.lower()


def test_timo_read_dmx_handles_missing_responses(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return []

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app, ["timo", "read-dmx", "--port", "/dev/ttyUSB0", "--length", "2"]
    )
    assert result.exit_code == 1
    assert "no response" in result.stdout.lower()


def test_timo_read_dmx_detects_short_sequence(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [{"type": "resp", "id": 1, "ok": True, "rx": "81", "seq": 1}]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app, ["timo", "read-dmx", "--port", "/dev/ttyUSB0", "--length", "2"]
    )
    assert result.exit_code == 1
    assert "SPI phases" in result.stdout


def test_timo_read_dmx_reports_parse_error(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [
            {"type": "resp", "id": 1, "ok": True, "rx": "81", "seq": 1},
            {"type": "resp", "id": 2, "ok": True, "rx": "", "seq": 2},
        ]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app, ["timo", "read-dmx", "--port", "/dev/ttyUSB0", "--length", "2"]
    )
    assert result.exit_code == 1
    assert "Unable to parse" in result.stdout


def test_timo_write_reg_executes_two_phase_sequence(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    calls = []

    class WriteRegClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_xfer(self, *, tx: str, n: int, **_overrides):
            calls.append({"tx": tx, "n": n})
            if len(calls) == 1:
                return {"type": "resp", "id": 1, "ok": True, "rx": "01", "seq": 10}
            return {"type": "resp", "id": 2, "ok": True, "rx": "00", "seq": 11}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", WriteRegClient)
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "write-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0x5",
            "--data",
            "cafe",
        ],
    )
    assert result.exit_code == 0
    assert "0x05" in result.stdout
    assert "Data written" in result.stdout
    assert calls == [{"tx": "45", "n": 1}, {"tx": "ffcafe", "n": 3}]


def test_timo_write_reg_invalid_addr(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "write-reg", "--port", "/dev/ttyUSB0", "--addr", "64", "--data", "01"],
    )
    assert result.exit_code != 0
    assert "range 0-63" in result.stdout or "range 0-63" in result.stderr


def test_timo_write_reg_invalid_data(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "write-reg", "--port", "/dev/ttyUSB0", "--addr", "1", "--data", "zz"],
    )
    assert result.exit_code != 0
    assert "Invalid hex" in result.stdout or "Invalid hex" in result.stderr


def test_timo_write_reg_handles_failed_phase(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [{"type": "resp", "id": 1, "ok": False, "rx": "", "seq": 1}]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "write-reg", "--port", "/dev/ttyUSB0", "--addr", "1", "--data", "01"],
    )
    assert result.exit_code == 1
    assert "command" in result.stdout.lower()


def test_timo_write_reg_handles_missing_responses(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return []

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "write-reg", "--port", "/dev/ttyUSB0", "--addr", "1", "--data", "01"],
    )
    assert result.exit_code == 1
    assert "no response" in result.stdout.lower()


def test_timo_write_reg_detects_short_sequence(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [{"type": "resp", "id": 1, "ok": True, "rx": "45", "seq": 1}]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "write-reg", "--port", "/dev/ttyUSB0", "--addr", "1", "--data", "01"],
    )
    assert result.exit_code == 1
    assert "SPI phases" in result.stdout


def test_timo_write_reg_reports_parse_error(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [
            {"type": "resp", "id": 1, "ok": True, "rx": "45", "seq": 1},
            {"type": "resp", "id": 2, "ok": True, "rx": "", "seq": 2},
        ]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["timo", "write-reg", "--port", "/dev/ttyUSB0", "--addr", "1", "--data", "01"],
    )
    assert result.exit_code == 1
    assert "Unable to parse" in result.stdout


#! /usr/bin/env python
# -*- coding: utf-8 -*-

import io
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
import typer
from rich.console import Console
from typer.testing import CliRunner

from shuttle.cli import app
import shuttle.cli as cli_module
import shuttle.serial_client as serial_client_module
from shuttle import timo


@contextmanager
def _noop_spinner(*_args, **_kwargs):
    yield


class SerialStub:
    def __init__(self, lines):
        self._lines = list(lines)
        self.writes = []
        self.is_open = True
        self.reset_calls = 0

    def write(self, data):
        self.writes.append(data)

    def readline(self):
        if self._lines:
            return self._lines.pop(0)
        return b""

    def reset_input_buffer(self):
        self.reset_calls += 1

    def close(self):
        self.is_open = False


def _install_serial_stub(monkeypatch, lines):
    stub = SerialStub(lines)
    monkeypatch.setattr(
        serial_client_module.serial, "Serial", lambda *args, **kwargs: stub
    )
    return stub


@pytest.fixture
def dummy_serial(monkeypatch):
    """Patch NDJSONSerialClient so tests can run without hardware."""

    record = SimpleNamespace(
        init_args=None,
        spi_args=None,
        spi_calls=[],
        closed=False,
        logger=None,
        spi_response={"type": "resp", "id": 1, "ok": True, "rx": "beef", "seq": 1},
        spi_responses=[],
    )

    class DummyClient:
        def __init__(
            self,
            port: str,
            *,
            baudrate: int,
            timeout: float,
            logger=None,
            seq_tracker=None,
        ):
            record.init_args = {"port": port, "baudrate": baudrate, "timeout": timeout}
            record.logger = logger

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            record.closed = True

        def spi_xfer(self, *, tx: str, n: int, **overrides):
            call = {"tx": tx, "n": n, "overrides": overrides}
            record.spi_args = call
            record.spi_calls.append(call)
            if record.spi_responses:
                return record.spi_responses.pop(0)
            return record.spi_response

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", DummyClient)
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    return record


@pytest.fixture
def recorded_console(monkeypatch):
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=80)
    monkeypatch.setattr(cli_module, "console", console)
    return buffer


@pytest.fixture(autouse=True)
def reset_sequence_tracker():
    yield


def test_timo_nop_invokes_spi_transfer(dummy_serial):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "nop",
            "--port",
            "/dev/ttyACM0",
            "--baud",
            "921600",
            "--timeout",
            "1.5",
        ],
    )

    assert result.exit_code == 0
    assert "spi.xfer (NOP)" in result.stdout

    expected_hex = cli_module.timo.nop_frame_hex()
    assert dummy_serial.init_args == {
        "port": "/dev/ttyACM0",
        "baudrate": 921600,
        "timeout": 1.5,
    }
    assert dummy_serial.spi_args["tx"] == expected_hex
    assert dummy_serial.spi_args["n"] == len(expected_hex) // 2
    assert dummy_serial.closed is True


def test_timo_status_reads_register(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {
            "type": "resp",
            "id": 2,
            "ok": True,
            "rx": "0008",
            "seq": 2,
        },  # status byte 0x08 (DMX set)
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "status",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    output = recorded_console.getvalue()
    assert "TiMo STATUS" in output
    assert "DMX" in output


def test_timo_link_sets_rf_link(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "00", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "00", "seq": 2},
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "link",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    assert dummy_serial.spi_calls[0]["tx"] == "41"  # write-reg STATUS
    assert dummy_serial.spi_calls[1]["tx"] == "ff02"  # payload with RF_LINK bit set
    output = recorded_console.getvalue()
    assert "TiMo link" in output
    assert "RF_LINK" in output


def test_timo_unlink_sets_linked(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "00", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "00", "seq": 2},
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "unlink",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    assert dummy_serial.spi_calls[0]["tx"] == "41"  # write-reg STATUS
    assert dummy_serial.spi_calls[1]["tx"] == "ff01"  # payload with LINKED bit set
    output = recorded_console.getvalue()
    assert "TiMo unlink" in output


def test_timo_antenna_read(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {
            "type": "resp",
            "id": 2,
            "ok": True,
            "rx": "0001",
            "seq": 2,
        },  # antenna byte = 1 -> ipex
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "antenna",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    output = recorded_console.getvalue()
    assert "ANTENNA" in output
    assert "ipex" in output.lower()


def test_timo_antenna_write(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "00", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "00", "seq": 2},
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "antenna",
            "on-board",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    assert dummy_serial.spi_calls[0]["tx"] == "47"  # write-reg ANTENNA
    assert dummy_serial.spi_calls[1]["tx"] == "ff00"
    output = recorded_console.getvalue()
    assert "antenna" in output.lower()


def test_timo_link_quality(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "00aa", "seq": 2},  # PDR=0xAA
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "link-quality",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    assert dummy_serial.spi_calls[0]["tx"] == "06"  # read-reg LINK_QUALITY
    assert dummy_serial.spi_calls[1]["tx"] == "ff00"
    output = recorded_console.getvalue()
    assert "Link Quality" in output
    assert "aa" in output.lower()


def test_timo_dmx_read(dummy_serial, recorded_console):
    # Two responses per register (command + payload) for window, spec, control
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {
            "type": "resp",
            "id": 2,
            "ok": True,
            "rx": "0002000001",
            "seq": 2,
        },  # window size=0x0200, start=1
        {"type": "resp", "id": 3, "ok": True, "rx": "", "seq": 3},
        {"type": "resp", "id": 4, "ok": True, "rx": "00000a0005000061a8", "seq": 4},
        {"type": "resp", "id": 5, "ok": True, "rx": "", "seq": 5},
        {"type": "resp", "id": 6, "ok": True, "rx": "0001", "seq": 6},  # enable=1
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "dmx",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    # First two transfers are for DMX_WINDOW read
    assert dummy_serial.spi_calls[0]["tx"] == "04"
    assert dummy_serial.spi_calls[1]["tx"] == "ff00000000"
    output = recorded_console.getvalue()
    assert "Window size" in output
    assert "512" in output


def test_timo_dmx_write(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {
            "type": "resp",
            "id": 2,
            "ok": True,
            "rx": "0000000000",
            "seq": 2,
        },  # zeroed window
        {"type": "resp", "id": 3, "ok": True, "rx": "", "seq": 3},
        {
            "type": "resp",
            "id": 4,
            "ok": True,
            "rx": "000000000000000000",
            "seq": 4,
        },  # zeroed spec
        {"type": "resp", "id": 5, "ok": True, "rx": "", "seq": 5},
        {"type": "resp", "id": 6, "ok": True, "rx": "0000", "seq": 6},  # control
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "dmx",
            "--window-size",
            "256",
            "--start-address",
            "2",
            "--channels",
            "3",
            "--interslot",
            "4",
            "--refresh",
            "5",
            "--enable",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    # Writes begin after reads: expect write-reg DMX_WINDOW first
    writes = dummy_serial.spi_calls[6:]
    assert writes[0]["tx"] == "44"
    assert writes[1]["tx"] == "ff01000002"
    output = recorded_console.getvalue()
    assert "DMX" in output


def test_timo_radio_mode_read(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {
            "type": "resp",
            "id": 2,
            "ok": True,
            "rx": "0088",
            "seq": 2,
        },  # CONFIG byte 0x88 (RADIO_ENABLE + SPI_RDM)
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "radio-mode",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    output = recorded_console.getvalue()
    assert "CONFIG" in output
    assert "rx" in output.lower()
    assert "SPI_RDM" in output


def test_timo_radio_mode_write(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "0000", "seq": 2},  # initial CONFIG
        {"type": "resp", "id": 3, "ok": True, "rx": "00", "seq": 3},
        {"type": "resp", "id": 4, "ok": True, "rx": "00", "seq": 4},
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "radio-mode",
            "--mode",
            "tx",
            "--enable",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    # read-reg CONFIG first
    assert dummy_serial.spi_calls[0]["tx"] == "00"
    # write-reg CONFIG after
    assert dummy_serial.spi_calls[2]["tx"] == "40"
    # payload should have mode bit (bit1) and radio_enable (bit7) set -> 0x82
    assert dummy_serial.spi_calls[3]["tx"] == "ff82"


def test_timo_device_name_read(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "0048656c6c6f00", "seq": 2},
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "device-name",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    output = recorded_console.getvalue()
    assert "Hello" in output


def test_timo_device_name_write(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "0000000000", "seq": 2},
        {"type": "resp", "id": 3, "ok": True, "rx": "00", "seq": 3},
        {"type": "resp", "id": 4, "ok": True, "rx": "004d7900", "seq": 4},
    ]
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "device-name",
            "My",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    # write-reg DEVICE_NAME should occur after initial read
    tx_values = [call["tx"] for call in dummy_serial.spi_calls]
    assert "76" in tx_values  # write opcode for DEVICE_NAME
    assert any(call["tx"].startswith("ff") for call in dummy_serial.spi_calls)
    output = recorded_console.getvalue()
    assert "My" in output


def test_timo_nop_requires_port(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    monkeypatch.delenv("SHUTTLE_PORT", raising=False)
    runner = CliRunner()
    result = runner.invoke(app, ["timo", "nop"])

    assert result.exit_code != 0
    assert "Serial port is required" in result.stderr


def test_timo_nop_handles_serial_error(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class FailingClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            raise cli_module.ShuttleSerialError("boom")

        def __exit__(self, exc_type, exc, exc_tb):
            return False

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", FailingClient)
    runner = CliRunner()
    result = runner.invoke(app, ["timo", "nop", "--port", "/dev/ttyACM0"])

    assert result.exit_code == 1
    assert "boom" in result.stdout


def test_prodtest_ping_sends_question_mark(dummy_serial):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "prodtest",
            "reset",
            "--port",
            "/dev/ttyACM1",
            "--baud",
            "460800",
            "--timeout",
            "1.25",
        ],
    )

    assert result.exit_code == 0
    assert "spi.xfer (prodtest)" in result.stdout
    assert dummy_serial.init_args == {
        "port": "/dev/ttyACM1",
        "baudrate": 460800,
        "timeout": 1.25,
    }
    assert dummy_serial.spi_args == {"tx": "3f", "n": 1, "overrides": {}}
    assert dummy_serial.closed is True


def test_prodtest_io_self_test_reports_failures(dummy_serial):
    dummy_serial.spi_responses = [
        {
            "type": "resp",
            "id": 11,
            "ok": True,
            "rx": "54000000000000000f",
            "seq": 1,
        },
        {
            "type": "resp",
            "id": 12,
            "ok": True,
            "rx": "0000000000000005",
            "seq": 2,
        },
    ]

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "prodtest",
            "io-self-test",
            "000000000000000F",
            "--port",
            "/dev/ttyUSB2",
        ],
    )

    assert result.exit_code == 0
    assert "PINS TO TEST BASE16 ENCODED: 000000000000000F" in result.stdout
    assert "RESULT OF TEST BASE16 ENCODED: 0000000000000005" in result.stdout
    assert "Test failed on pins: [ 2, 4 ]" in result.stdout
    timeout = cli_module.prodtest.IO_SELF_TEST_IRQ_TIMEOUT_US
    assert dummy_serial.spi_calls == [
        {
            "tx": "54000000000000000f",
            "n": 9,
            "overrides": {"wait_irq": {"edge": "leading", "timeout_us": timeout}},
        },
        {"tx": "ffffffffffffffff", "n": 8, "overrides": {}},
    ]


def test_prodtest_ping_success(dummy_serial, recorded_console):
    dummy_serial.spi_responses = [
        {"type": "resp", "id": 1, "ok": True, "rx": "00", "seq": 1},
        {"type": "resp", "id": 2, "ok": True, "rx": "2d", "seq": 2},
    ]

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "prodtest",
            "ping",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    output = recorded_console.getvalue()
    assert "Ping successful" in output


def test_prodtest_io_self_test_validates_mask_length(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["prodtest", "io-self-test", "abcd", "--port", "/dev/ttyUSB0"],
    )

    assert result.exit_code != 0
    assert "16 hex characters" in result.stderr


def test_timo_read_reg_executes_two_phase_sequence(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    calls = []

    class ReadRegClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_xfer(self, *, tx: str, n: int, **_overrides):
            calls.append({"tx": tx, "n": n})
            if len(calls) == 1:
                return {"type": "resp", "id": 1, "ok": True, "rx": "01", "seq": 10}
            return {"type": "resp", "id": 2, "ok": True, "rx": "000102", "seq": 11}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", ReadRegClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "read-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0x5",
            "--length",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert "0x05" in result.stdout
    assert "Data" in result.stdout
    assert calls == [{"tx": "05", "n": 1}, {"tx": "ff0000", "n": 3}]


def test_timo_read_reg_warns_on_irq_busy(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class ReadRegClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_xfer(self, *, tx: str, n: int, **_overrides):
            if tx == "05":
                return {"type": "resp", "id": 1, "ok": True, "rx": "80", "seq": 20}
            return {"type": "resp", "id": 2, "ok": True, "rx": "80aa", "seq": 21}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", ReadRegClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "read-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0x5",
            "--length",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert "IRQ warning" in result.stdout
    assert "bit7" in result.stdout


def test_timo_read_reg_handles_missing_responses(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return []

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "read-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0",
            "--length",
            "1",
        ],
    )

    assert result.exit_code == 1
    assert "no response" in result.stdout.lower()


def test_timo_read_reg_handles_failed_phase(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [{"type": "resp", "id": 1, "ok": False, "rx": "", "seq": 1}]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "read-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0",
            "--length",
            "1",
        ],
    )

    assert result.exit_code == 1
    assert "command" in result.stdout.lower()


def test_timo_read_reg_detects_short_sequence(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [{"type": "resp", "id": 1, "ok": True, "rx": "05", "seq": 1}]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "read-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0",
            "--length",
            "1",
        ],
    )

    assert result.exit_code == 1
    assert "SPI phases" in result.stdout


def test_timo_read_reg_reports_parse_error(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    def fake_exec(**_kwargs):
        return [
            {"type": "resp", "id": 1, "ok": True, "rx": "05", "seq": 1},
            {"type": "resp", "id": 2, "ok": True, "rx": "00", "seq": 2},
        ]

    monkeypatch.setattr(cli_module, "_execute_timo_sequence", fake_exec)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "timo",
            "read-reg",
            "--port",
            "/dev/ttyUSB0",
            "--addr",
            "0",
            "--length",
            "2",
        ],
    )

    assert result.exit_code == 1
    assert "Unable to parse" in result.stdout


def test_get_info_prints_payload(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class InfoClient:
        def __init__(
            self,
            port: str,
            *,
            baudrate: int,
            timeout: float,
            logger=None,
            seq_tracker=None,
        ):
            self.args = {
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout,
                "logger": logger,
            }

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def get_info(self):
            return {
                "type": "resp",
                "id": 2,
                "ok": True,
                "seq": 1,
                "uptime_ms": 99,
                "uart": {"baudrate": 115200},
                "spi_caps": {"hz_max": 8000000},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", InfoClient)

    runner = CliRunner()
    result = runner.invoke(app, ["get-info", "--port", "/dev/ttyUSB1"])

    assert result.exit_code == 0
    text = recorded_console.getvalue()
    assert "get.info payload" in text
    assert "uptime_ms" in text
    assert "spi_caps" in text


def test_get_info_handles_device_error(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class InfoClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def get_info(self):
            return {
                "type": "resp",
                "id": 3,
                "ok": False,
                "seq": 1,
                "err": {"code": "EIO", "msg": "nope"},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", InfoClient)

    runner = CliRunner()
    result = runner.invoke(app, ["get-info", "--port", "/dev/ttyUSB1"])

    assert result.exit_code == 0
    text = recorded_console.getvalue()
    assert "EIO" in text
    assert "nope" in text


def test_ping_prints_payload(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class PingClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def ping(self):
            return {
                "type": "resp",
                "id": 4,
                "ok": True,
                "fw": "fw",
                "proto": 1,
                "seq": 1,
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", PingClient)
    runner = CliRunner()
    result = runner.invoke(app, ["ping", "--port", "/dev/ttyUSB2"])

    assert result.exit_code == 0
    text = recorded_console.getvalue()
    assert "ping payload" in text
    assert "fw" in text


def test_ping_handles_device_error(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class PingClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def ping(self):
            return {
                "type": "resp",
                "id": 5,
                "ok": False,
                "seq": 1,
                "err": {"code": "EIO", "msg": "bad"},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", PingClient)
    runner = CliRunner()
    result = runner.invoke(app, ["ping", "--port", "/dev/ttyUSB2"])

    assert result.exit_code == 0
    text = recorded_console.getvalue()
    assert "bad" in text


def test_spi_cfg_queries_device(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(spi_args=None)

    class SpiClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_cfg(self, spi=None):
            record.spi_args = spi
            return {
                "type": "resp",
                "id": 1,
                "ok": True,
                "seq": 1,
                "spi": {"hz": 1270000},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", SpiClient)

    runner = CliRunner()
    result = runner.invoke(app, ["spi-cfg", "--port", "/dev/ttyUSB0"])

    assert result.exit_code == 0
    assert record.spi_args is None
    text = recorded_console.getvalue()
    assert "spi.cfg payload" in text
    assert "hz" in text


def test_spi_cfg_applies_cli_overrides(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(spi_args=None)

    class SpiClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_cfg(self, spi=None):
            record.spi_args = spi
            return {"type": "resp", "id": 1, "ok": True, "seq": 1, "spi": spi or {}}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", SpiClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "spi-cfg",
            "--port",
            "/dev/ttyUSB0",
            "--cs-active",
            "HIGH",
            "--bit-order",
            "LSB",
            "--byte-order",
            "Little",
            "--clock-polarity",
            "IDLE_HIGH",
            "--clock-phase",
            "Trailing",
            "--hz",
            "2000000",
            "--setup-us",
            "15",
        ],
    )

    assert result.exit_code == 0
    assert record.spi_args == {
        "cs_active": "high",
        "bit_order": "lsb",
        "byte_order": "little",
        "clock_polarity": "idle_high",
        "clock_phase": "trailing",
        "hz": 2000000,
        "setup_us": 15,
    }


def test_spi_enable_command(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(open_args=None, enable_called=False)

    class SpiClient:
        def __init__(self, *args, **kwargs):
            record.open_args = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_enable(self):
            record.enable_called = True
            return {
                "type": "resp",
                "id": 1,
                "ok": True,
                "seq": 1,
                "spi": {"enabled": True},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", SpiClient)
    runner = CliRunner()
    result = runner.invoke(app, ["spi-enable", "--port", "/dev/ttyUSB0"])

    assert result.exit_code == 0
    assert record.enable_called is True
    assert record.open_args["port"] == "/dev/ttyUSB0"
    assert "spi.enable payload" in recorded_console.getvalue()


def test_spi_disable_command(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(open_args=None, disable_called=False)

    class SpiClient:
        def __init__(self, *args, **kwargs):
            record.open_args = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def spi_disable(self):
            record.disable_called = True
            return {
                "type": "resp",
                "id": 2,
                "ok": True,
                "seq": 2,
                "spi": {"enabled": False},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", SpiClient)
    runner = CliRunner()
    result = runner.invoke(app, ["spi-disable", "--port", "/dev/ttyUSB0"])

    assert result.exit_code == 0
    assert record.disable_called is True
    assert record.open_args["port"] == "/dev/ttyUSB0"
    assert "spi.disable payload" in recorded_console.getvalue()


def test_uart_cfg_queries_device(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(uart_args=None)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_cfg(self, uart=None):
            record.uart_args = uart
            return {
                "type": "resp",
                "id": 1,
                "ok": True,
                "seq": 1,
                "uart": {"baudrate": 115200},
            }

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(app, ["uart-cfg", "--port", "/dev/ttyUSB0"])

    assert result.exit_code == 0
    assert record.uart_args is None
    text = recorded_console.getvalue()
    assert "uart.cfg payload" in text
    assert "baudrate" in text


def test_uart_cfg_applies_cli_overrides(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(uart_args=None)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_cfg(self, uart=None):
            record.uart_args = uart
            return {"type": "resp", "id": 1, "ok": True, "seq": 1, "uart": uart or {}}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "uart-cfg",
            "--port",
            "/dev/ttyUSB0",
            "--baudrate",
            "230400",
            "--stopbits",
            "2",
            "--parity",
            "Even",
        ],
    )

    assert result.exit_code == 0
    assert record.uart_args == {"baudrate": 230400, "stopbits": 2, "parity": "e"}


def test_uart_cfg_rejects_invalid_parity(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_cfg(self, uart=None):  # pragma: no cover - shouldn't be called
            return {}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["uart-cfg", "--port", "/dev/ttyUSB0", "--parity", "weird"],
    )

    assert result.exit_code != 0
    assert "parity" in result.stderr.lower()


def test_uart_tx_hex_payload(monkeypatch, recorded_console):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(sent=None)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_tx(self, data, port=None):
            record.sent = {"data": data, "port": port}
            return {"type": "resp", "id": 1, "ok": True, "n": len(data) // 2}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["uart-tx", "--port", "/dev/ttyUSB0", "deadbeef"],
    )

    assert result.exit_code == 0
    assert record.sent == {"data": "deadbeef", "port": None}
    assert "uart.tx payload" in recorded_console.getvalue()


def test_uart_tx_invalid_hex(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["uart-tx", "--port", "/dev/ttyUSB0", "abc"],
    )

    assert result.exit_code != 0
    combined = (result.stdout + result.stderr).lower()
    assert "hex" in combined


def test_uart_tx_text_payload(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(sent=None)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_tx(self, data, port=None):
            record.sent = {"data": data, "port": port}
            return {"type": "resp", "id": 2, "ok": True, "n": len(data) // 2}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "uart-tx",
            "--port",
            "/dev/ttyUSB0",
            "--text",
            "Hi",
            "--newline",
            "--uart-port",
            "1",
        ],
    )

    assert result.exit_code == 0
    # "Hi" + newline => 0x48 0x69 0x0a
    assert record.sent == {"data": "48690a", "port": 1}


def test_uart_tx_reads_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    payload_file = tmp_path / "payload.bin"
    payload_file.write_bytes(b"abc")
    record = SimpleNamespace(data=None)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_tx(self, data, port=None):
            record.data = data
            return {"type": "resp", "id": 3, "ok": True, "n": len(data) // 2}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "uart-tx",
            "--port",
            "/dev/ttyUSB0",
            "--file",
            str(payload_file),
        ],
    )

    assert result.exit_code == 0
    assert record.data == "616263"


def test_uart_tx_conflicting_sources(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "uart-tx",
            "--port",
            "/dev/ttyUSB0",
            "dead",
            "--text",
            "hi",
        ],
    )

    assert result.exit_code != 0
    assert "payload source" in (result.stdout + result.stderr).lower()


def test_uart_tx_stdin(monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    record = SimpleNamespace(data=None)

    class UartClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def uart_tx(self, data, port=None):
            record.data = data
            return {"type": "resp", "id": 4, "ok": True, "n": len(data) // 2}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", UartClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["uart-tx", "--port", "/dev/ttyUSB0", "-", "--newline"],
        input="OK",
    )

    assert result.exit_code == 0
    # stdin text "OK" + newline => 4f 4b 0a
    assert record.data == "4f4b0a"


def test_ndjson_serial_client_handles_event_and_response(monkeypatch, recorded_console):
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    stub = _install_serial_stub(
        monkeypatch,
        [
            b'{"type":"ev","ev":"spi.irq","seq":1}\n',
            b'{"type":"resp","id":1,"ok":true,"rx":"aa","seq":2}\n',
        ],
    )

    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        response = client.spi_xfer(tx="ff")

    payload = stub.writes[0].decode().strip()
    assert '"op":"spi.xfer"' in payload
    assert '"tx":"ff"' in payload
    assert response["rx"] == "aa"
    assert recorded_console.getvalue() == ""


def test_ndjson_serial_client_skips_out_of_order_messages(
    monkeypatch, recorded_console
):
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    _install_serial_stub(
        monkeypatch,
        [
            b'{"type":"resp","id":99,"ok":true,"seq":1}\n',
            b'{"type":"mystery","seq":2}\n',
            b'{"type":"resp","id":1,"ok":true,"seq":3}\n',
        ],
    )
    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        with pytest.raises(cli_module.ShuttleSerialError):
            client.spi_xfer(tx="ff")


def test_ndjson_serial_client_randomizes_id(monkeypatch):
    stub = _install_serial_stub(
        monkeypatch,
        [b'{"type":"resp","id":123,"ok":true,"seq":1}\n'],
    )

    ids = iter([0, 123])

    def fake_randbits(bits):  # pragma: no cover - fallback unused
        try:
            return next(ids)
        except StopIteration:
            return 123

    monkeypatch.setattr(serial_client_module.secrets, "randbits", fake_randbits)

    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        client.spi_xfer(tx="ff")

    payload = stub.writes[0].decode()
    assert '"id":123' in payload


def test_ndjson_serial_client_requires_response_id(monkeypatch):
    _install_serial_stub(
        monkeypatch,
        [b'{"type":"resp","ok":true,"seq":1}\n'],
    )

    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        with pytest.raises(cli_module.ShuttleSerialError):
            client.spi_xfer(tx="ff")


def test_ndjson_serial_client_timeout(monkeypatch, recorded_console):
    _install_serial_stub(monkeypatch, [])
    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        with pytest.raises(cli_module.ShuttleSerialError):
            client.spi_xfer(tx="ff")


def test_ndjson_serial_client_detects_sequence_gap(monkeypatch):
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    stub = _install_serial_stub(
        monkeypatch,
        [
            b'{"type":"resp","id":1,"ok":true,"seq":1}\n',
            b'{"type":"resp","id":1,"ok":true,"seq":3}\n',
        ],
    )
    tracker = cli_module._SequenceTracker()
    with cli_module.NDJSONSerialClient(
        "/dev/null", baudrate=1, timeout=0.1, seq_tracker=tracker
    ) as client:
        client.spi_xfer(tx="aa")
        with pytest.raises(cli_module.ShuttleSerialError) as excinfo:
            client.spi_xfer(tx="bb")

    assert "sequence numbers" in str(excinfo.value)


def test_ndjson_serial_client_decoder_errors(monkeypatch, recorded_console):
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    stub = _install_serial_stub(monkeypatch, [b"\xff\xfe\n"])
    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        with pytest.raises(cli_module.ShuttleSerialError):
            client._read()
        stub._lines = [b"not-json\n"]
        with pytest.raises(cli_module.ShuttleSerialError):
            client._read()
        stub._lines = [b'{"type":"resp","id":1,"ok":true,"seq":1}\n']
        response = client.spi_xfer(tx="ff")

    assert recorded_console.getvalue() == ""
    assert response["ok"] is True


def test_ndjson_serial_client_blank_line(monkeypatch):
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    stub = _install_serial_stub(monkeypatch, [b"\n"])
    with cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1) as client:
        assert client._read() is None
        stub._lines = [b'{"type":"resp","id":1,"ok":true,"seq":1}\n']
        response = client.spi_xfer(tx="ff")

    assert response["ok"] is True


def test_ndjson_serial_client_close(monkeypatch):
    stub = _install_serial_stub(monkeypatch, [])
    client = cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1)
    client.close()
    assert stub.is_open is False


def test_ndjson_serial_client_open_error(monkeypatch):
    def _boom(*_args, **_kwargs):
        raise serial_client_module.SerialException("boom")

    monkeypatch.setattr(serial_client_module.serial, "Serial", _boom)
    with pytest.raises(cli_module.ShuttleSerialError):
        cli_module.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.1)


def test_require_port_helpers():
    assert cli_module._require_port("/dev/ttyACM0") == "/dev/ttyACM0"
    with pytest.raises(typer.BadParameter):
        cli_module._require_port(None)


def test_format_hex_and_render_response(monkeypatch):
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=80)
    monkeypatch.setattr(cli_module, "console", console)
    formatted = cli_module._format_hex("aabb")
    assert formatted == "aa bb"
    assert cli_module._format_hex("") == "—"

    cli_module._render_spi_response(
        "test",
        {"ok": False, "rx": "aabb", "err": {"code": "E", "msg": "nope"}},
        command_label="spi.xfer",
    )
    text = buffer.getvalue()
    assert "aa bb" not in text
    assert "E: nope" in text

    buffer.truncate(0)
    buffer.seek(0)
    cli_module._render_spi_response(
        "test", {"ok": True, "rx": "aabb"}, command_label="spi.xfer"
    )
    text = buffer.getvalue()
    assert "aa bb" in text


def test_render_spi_response_without_optionals(monkeypatch):
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=False, width=80)
    monkeypatch.setattr(cli_module, "console", console)
    cli_module._render_spi_response("test", {"ok": True}, command_label="spi.xfer")
    text = buffer.getvalue()
    assert "RX" not in text
    assert "Error" not in text


def test_spinner_uses_status_when_tty(monkeypatch):
    calls = []

    @contextmanager
    def fake_status(message, spinner="dots"):
        calls.append((message, spinner))
        yield

    fake_stdout = SimpleNamespace(isatty=lambda: True)
    monkeypatch.setattr(cli_module, "sys", SimpleNamespace(stdout=fake_stdout))
    monkeypatch.setattr(cli_module.console, "status", fake_status)

    with cli_module.spinner("hello"):
        pass

    assert calls == [("hello", "dots")]


def test_spinner_skips_when_disabled(monkeypatch):
    calls = []

    @contextmanager
    def fake_status(message, spinner="dots"):
        calls.append((message, spinner))
        yield

    fake_stdout = SimpleNamespace(isatty=lambda: True)
    monkeypatch.setattr(cli_module, "sys", SimpleNamespace(stdout=fake_stdout))
    monkeypatch.setattr(cli_module.console, "status", fake_status)

    with cli_module.spinner("noop", enabled=False):
        pass

    assert calls == []


def test_timo_nop_helpers():
    frame = timo.nop_frame()
    assert len(frame) == 1
    assert timo.nop_frame_hex() == frame.hex()

    seq = timo.read_reg_sequence(5, 2)
    assert len(seq) == 2
    assert seq[0]["tx"] == bytes([5]).hex()
    assert seq[1]["tx"] == bytes([timo.READ_REG_DUMMY, 0x00, 0x00]).hex()
    # Check wait_irq param for command phase (first transfer)
    assert "wait_irq" in seq[0]
    assert seq[0]["wait_irq"]["edge"] == "trailing"
    assert isinstance(seq[0]["wait_irq"]["timeout_us"], int)
    # Second transfer should not have wait_irq
    assert "wait_irq" not in seq[1]

    result = timo.parse_read_reg_response(5, 2, ["40", "00cafe"])
    assert result.address == 5
    assert result.length == 2
    assert result.data == bytes.fromhex("cafe")
    assert result.irq_flags_command == 0x40
    assert result.irq_flags_payload == 0x00
    assert timo.format_bytes(result.data) == "ca fe"
    assert timo.requires_restart(0x80) is True
    assert timo.requires_restart(0x00) is False
    assert timo.format_bytes(b"") == "—"

    with pytest.raises(ValueError):
        timo.read_reg_sequence(-1, 1)
    with pytest.raises(ValueError):
        timo.read_reg_sequence(0, 0)
    with pytest.raises(ValueError):
        timo.parse_read_reg_response(0, 1, ["ff"])
    with pytest.raises(ValueError):
        timo.parse_read_reg_response(0, 1, ["ffff", "00"])
    with pytest.raises(ValueError):
        timo.parse_read_reg_response(0, 2, ["00", "00"])


def test_parse_int_option_errors():
    with pytest.raises(typer.BadParameter):
        cli_module._parse_int_option("xyz", name="address")
    with pytest.raises(typer.BadParameter):
        cli_module._parse_int_option("-1", name="address")


def test_normalize_choice_handles_unknown_field_and_invalid_value():
    assert cli_module._normalize_choice("Foo", name="hz") == "Foo"
    with pytest.raises(typer.BadParameter):
        cli_module._normalize_choice("invalid", name="cs_active")


def test_normalize_uart_parity_handles_empty_and_prefix_values():
    assert cli_module._normalize_uart_parity("   ") is None
    assert cli_module._normalize_uart_parity("Oddball") == "o"


def test_seq_meta_option_rejects_non_integer_file(tmp_path, monkeypatch):
    meta_path = tmp_path / "seq.meta"
    meta_path.write_text("notanint", encoding="utf-8")

    class PingClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def ping(self):
            return {"type": "resp", "id": 1, "ok": True}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", PingClient)
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--seq-meta",
            str(meta_path),
            "ping",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code != 0
    assert "integer" in result.stderr.lower() or "integer" in result.stdout.lower()


def test_serial_logger_writes_entries(tmp_path):
    log_path = tmp_path / "serial.log"
    logger = cli_module._SerialLogger(log_path)
    logger.log("TX", b'{"hello":1}\n')
    logger.log("RX", b"world\n")
    logger.close()

    lines = log_path.read_text().strip().splitlines()
    assert lines[0].endswith('TX {"hello":1}')
    assert lines[1].endswith("RX world")


def test_ndjson_serial_client_logs_lines(monkeypatch):
    entries = []

    class Logger:
        def log(self, direction, data):
            entries.append((direction, data))

    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    _install_serial_stub(monkeypatch, [b'{"type":"resp","id":1,"ok":true}\n'])
    with cli_module.NDJSONSerialClient(
        "/dev/null",
        baudrate=1,
        timeout=0.1,
        logger=Logger(),
    ) as client:
        client.spi_xfer(tx="ff")

    assert entries[0][0] == "TX"
    assert entries[1][0] == "RX"


def test_cli_global_log_option(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    log_path = tmp_path / "serial.log"
    record = SimpleNamespace(logger=None)

    class PingClient:
        def __init__(self, *_args, **kwargs):
            record.logger = kwargs.get("logger")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            return False

        def ping(self):
            return {"type": "resp", "id": 1, "ok": True, "seq": 1}

    monkeypatch.setattr(cli_module, "NDJSONSerialClient", PingClient)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--log",
            str(log_path),
            "ping",
            "--port",
            "/dev/ttyUSB0",
        ],
    )

    assert result.exit_code == 0
    assert record.logger is not None
    record.logger.log("RX", b'{"ok":true}\n')
    record.logger.close()
    contents = log_path.read_text()
    assert 'RX {"ok":true}' in contents


def test_seq_meta_option_detects_gap_between_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    seq_meta_path = tmp_path / "seq.meta"
    runner = CliRunner()

    def _invoke_with_seq(seq_value: int):
        payload = f'{{"type":"resp","id":1,"ok":true,"seq":{seq_value}}}\n'.encode(
            "utf-8"
        )
        _install_serial_stub(monkeypatch, [payload])
        return runner.invoke(
            app,
            [
                "--seq-meta",
                str(seq_meta_path),
                "ping",
                "--port",
                "/dev/ttyUSB0",
            ],
        )

    first = _invoke_with_seq(5)
    assert first.exit_code == 0
    assert seq_meta_path.read_text().strip() == "5"

    second = _invoke_with_seq(7)
    assert second.exit_code == 1
    assert "sequence numbers" in second.stdout.lower()
    assert seq_meta_path.read_text().strip() == "7"

    third = _invoke_with_seq(8)
    assert third.exit_code == 0
    assert seq_meta_path.read_text().strip() == "8"


def test_seq_meta_option_updates_existing_file_after_gap(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    monkeypatch.setattr(serial_client_module.secrets, "randbits", lambda bits: 1)
    seq_meta_path = tmp_path / "seq.meta"
    seq_meta_path.write_text("33")
    runner = CliRunner()

    def _invoke(seq_value: int):
        payload = f'{{"type":"resp","id":1,"ok":true,"seq":{seq_value}}}\n'.encode(
            "utf-8"
        )
        _install_serial_stub(monkeypatch, [payload])
        return runner.invoke(
            app,
            [
                "--seq-meta",
                str(seq_meta_path),
                "ping",
                "--port",
                "/dev/ttyUSB0",
            ],
        )

    failure = _invoke(35)
    assert failure.exit_code == 1
    assert "sequence numbers" in failure.stdout.lower()
    assert seq_meta_path.read_text().strip() == "35"

    success = _invoke(36)
    assert success.exit_code == 0
    assert seq_meta_path.read_text().strip() == "36"
