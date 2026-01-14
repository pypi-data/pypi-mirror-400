import json
import queue
from pathlib import Path

import pytest

import shuttle.serial_client as serial_client


def test_sequence_tracker_handles_empty_file(tmp_path):
    meta = tmp_path / "seq.meta"
    meta.write_text("", encoding="utf-8")
    tracker = serial_client.SequenceTracker(meta)
    assert tracker._last_seq is None


def test_sequence_tracker_dir_creation_error(monkeypatch, tmp_path):
    meta = tmp_path / "seq.meta"

    def fail_mkdir(self, *args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)
    with pytest.raises(ValueError):
        serial_client.SequenceTracker(meta)


def test_sequence_tracker_read_error(monkeypatch, tmp_path):
    meta = tmp_path / "seq.meta"
    meta.write_text("42", encoding="utf-8")

    def fail_read(self, *args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(Path, "read_text", fail_read)
    with pytest.raises(ValueError):
        serial_client.SequenceTracker(meta)


def test_ndjson_serial_client_close_closes_underlying():
    class DummySerial:
        def __init__(self):
            self.is_open = True
            self.closed = False

        def close(self):
            self.closed = True
            self.is_open = False

    client = serial_client.NDJSONSerialClient.__new__(serial_client.NDJSONSerialClient)
    client._serial = DummySerial()

    client.close()

    assert client._serial.closed is True
    assert client._serial.is_open is False


def test_ndjson_serial_client_payload_builders():
    calls = []

    def _command(op, payload):
        calls.append((op, payload))
        return {"op": op, "payload": payload}

    client = serial_client.NDJSONSerialClient.__new__(serial_client.NDJSONSerialClient)
    client._command = _command
    client._seq_tracker = None

    client.spi_cfg({"hz": 123})
    client.uart_cfg({"baudrate": 9600})
    client.spi_enable()
    client.spi_disable()

    assert calls[0][0] == "spi.cfg"
    assert calls[0][1]["spi"]["hz"] == 123
    assert calls[1][0] == "uart.cfg"
    assert calls[1][1]["uart"]["baudrate"] == 9600
    assert calls[2][0] == "spi.enable"
    assert calls[3][0] == "spi.disable"


def test_record_sequence_no_tracker(monkeypatch):
    client = serial_client.NDJSONSerialClient.__new__(serial_client.NDJSONSerialClient)
    client._seq_tracker = None
    client._record_sequence({"type": "resp", "id": 1, "seq": 10})


def test_client_uses_injected_logger_and_tracker(monkeypatch):
    writes = []

    class DummySerial:
        def __init__(self, *args, **kwargs):
            self.is_open = True
            self.writes = writes

        def reset_input_buffer(self):
            pass

        def write(self, data):
            self.writes.append(data)

        def close(self):
            self.is_open = False

    logger_calls = []

    class DummyLogger:
        def log(self, direction, payload):
            logger_calls.append((direction, payload))

    class DummyTracker:
        def __init__(self):
            self.observed = []

        def observe(self, seq, source):
            self.observed.append((seq, source))

    monkeypatch.setattr(serial_client.serial, "Serial", DummySerial)
    logger = DummyLogger()
    tracker = DummyTracker()
    client = serial_client.NDJSONSerialClient(
        "/dev/null", baudrate=1, timeout=1.0, logger=logger, seq_tracker=tracker
    )

    client._log_serial("TX", b"payload")
    client._record_sequence({"type": "resp", "id": 1, "seq": 5})

    assert logger_calls == [("TX", b"payload")]
    assert tracker.observed == [(5, "response id=1")]


def test_client_no_tracker_skips_observation(monkeypatch):
    class DummySerial:
        def __init__(self, *args, **kwargs):
            self.is_open = True

        def reset_input_buffer(self):
            pass

        def write(self, data):
            pass

        def close(self):
            self.is_open = False

    monkeypatch.setattr(serial_client.serial, "Serial", DummySerial)
    client = serial_client.NDJSONSerialClient("/dev/null", baudrate=1, timeout=1.0)
    client._record_sequence({"type": "resp", "id": 9, "seq": 2})


def test_send_command_future_and_event_listener(monkeypatch):
    class DummySerial:
        def __init__(self, *args, **kwargs):
            self.lines = queue.Queue()
            self.is_open = True

        def reset_input_buffer(self):
            pass

        def write(self, data):
            pass

        def readline(self):
            try:
                return self.lines.get(timeout=0.1)
            except queue.Empty:
                return b""

        def close(self):
            self.is_open = False

    serial_obj = DummySerial()
    monkeypatch.setattr(serial_client.serial, "Serial", lambda *a, **kw: serial_obj)
    client = serial_client.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.2)
    client._next_cmd_id = lambda: 1  # type: ignore[assignment]

    irq_listener = client.register_event_listener("irq")
    future = client.send_command("ping", {})

    serial_obj.lines.put(b'{"type":"ev","ev":"irq","edge":"rising"}\n')
    serial_obj.lines.put(b'{"type":"resp","id":1,"ok":true}\n')

    assert future.result(timeout=1)["ok"] is True
    assert irq_listener.next(timeout=1)["edge"] == "rising"
    client.close()


def test_multiple_listeners_receive_same_event(monkeypatch):
    class DummySerial:
        def __init__(self, *args, **kwargs):
            self.lines = queue.Queue()
            self.is_open = True

        def reset_input_buffer(self):
            pass

        def write(self, data):
            pass

        def readline(self):
            try:
                return self.lines.get(timeout=0.1)
            except queue.Empty:
                return b""

        def close(self):
            self.is_open = False

    serial_obj = DummySerial()
    monkeypatch.setattr(serial_client.serial, "Serial", lambda *a, **kw: serial_obj)
    client = serial_client.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.2)
    listener_a = client.register_event_listener("dmx")
    listener_b = client.register_event_listener("dmx")

    serial_obj.lines.put(b'{"type":"ev","ev":"dmx","payload":1}\n')

    assert listener_a.next(timeout=1)["payload"] == 1
    assert listener_b.next(timeout=1)["payload"] == 1
    client.close()


def test_command_future_timeout():
    future = serial_client.CommandFuture(cmd_id=1, timeout=0.01)
    with pytest.raises(serial_client.ShuttleSerialError):
        future.result(timeout=1)


def test_command_future_without_timer():
    future = serial_client.CommandFuture(cmd_id=2, timeout=0)
    future.mark_result({"ok": True})
    assert future.result(timeout=1)["ok"] is True
    # Ensure duplicate completions are ignored
    future.mark_exception(RuntimeError("late"))
    assert future.result(timeout=1)["ok"] is True


def test_event_subscription_queueing():
    sub = serial_client.EventSubscription("irq")
    sub.emit({"edge": "rising"})
    sub.emit({"edge": "falling"})
    assert sub.next(timeout=1)["edge"] == "rising"
    assert sub.next(timeout=1)["edge"] == "falling"
    with pytest.raises(serial_client.ShuttleSerialError):
        sub.fail(serial_client.ShuttleSerialError("boom"))
        sub.next(timeout=0.1)
    # When already closed, additional emits are ignored and completed future is returned
    with pytest.raises(serial_client.ShuttleSerialError):
        sub.emit({"edge": "extra"})
        sub.next(timeout=0.1)


def test_response_backlog_delivered(monkeypatch):
    class DummySerial:
        def __init__(self, *args, **kwargs):
            self.lines = queue.Queue()
            self.is_open = True

        def reset_input_buffer(self):
            pass

        def write(self, data):
            pass

        def readline(self):
            try:
                return self.lines.get(timeout=0.1)
            except queue.Empty:
                return b""

        def close(self):
            self.is_open = False

    serial_obj = DummySerial()
    monkeypatch.setattr(serial_client.serial, "Serial", lambda *a, **kw: serial_obj)
    client = serial_client.NDJSONSerialClient("/dev/null", baudrate=1, timeout=0.2)
    # Simulate response arriving before the command is issued
    serial_obj.lines.put(b'{"type":"resp","id":1,"ok":true}\n')
    client._dispatch(json.loads(serial_obj.lines.get().decode()))
    future = client.send_command("ping", {})
    assert future.result(timeout=1)["ok"] is True
    client.close()
