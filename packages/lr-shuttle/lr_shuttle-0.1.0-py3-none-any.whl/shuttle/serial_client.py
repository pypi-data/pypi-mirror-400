#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Serial transport helpers for the Shuttle bridge."""

from __future__ import annotations

import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from collections import deque
from concurrent.futures import Future
import serial
from serial import SerialException
from .constants import DEFAULT_BAUD, DEFAULT_TIMEOUT


class ShuttleSerialError(Exception):
    """Raised when serial transport encounters an unrecoverable error."""


class CommandFuture(Future):
    """Future representing a pending device command."""

    def __init__(self, *, cmd_id: int, timeout: Optional[float]):
        super().__init__()
        self.cmd_id = cmd_id
        self._timer: Optional[threading.Timer] = None
        if timeout and timeout > 0:
            self._timer = threading.Timer(timeout, self._set_timeout)
            self._timer.daemon = True
            self._timer.start()

    def mark_result(self, result: Dict[str, Any]) -> None:
        self._cancel_timer()
        if not self.done():
            self.set_result(result)

    def mark_exception(self, exc: BaseException) -> None:
        self._cancel_timer()
        if not self.done():
            self.set_exception(exc)

    def _set_timeout(self) -> None:
        self.mark_exception(ShuttleSerialError("Timed out waiting for device response"))

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None


class EventSubscription:
    """Multiple-use future that resolves every time an event arrives."""

    def __init__(
        self,
        event: str,
        teardown: Optional[Callable[["EventSubscription"], None]] = None,
    ):
        self.event = event
        self._teardown = teardown
        self._lock = threading.Lock()
        self._queue = deque()
        self._current: Future = Future()
        self._closed = False

    def next(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Block until the next event payload is available."""

        with self._lock:
            if self._current.done():
                result = self._current.result()
                self._advance_locked()
                return result
            if self._queue:
                payload = self._queue.popleft()
                self._advance_locked()
                return payload
            current = self._current
        try:
            return current.result(timeout=timeout)
        finally:
            if current.done():
                self._advance()

    def future(self) -> Future:
        with self._lock:
            if self._current.done():
                return self._current
            if self._queue:
                completed: Future = Future()
                completed.set_result(self._queue.popleft())
                self._advance_locked()
                return completed
            return self._current

    def emit(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            if self._closed:
                return
            if not self._current.done():
                self._current.set_result(payload)
            else:
                self._queue.append(payload)

    def fail(self, exc: BaseException) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            current = self._current
        if not current.done():
            current.set_exception(exc)
        self._teardown_if_needed()

    def close(self) -> None:
        self.fail(ShuttleSerialError("Event subscription closed"))

    def _advance(self) -> None:
        with self._lock:
            self._advance_locked()

    def _advance_locked(self) -> None:
        if self._closed:
            return
        if self._current.done():
            if self._queue:
                self._current = Future()
                payload = self._queue.popleft()
                self._current.set_result(payload)
            else:
                self._current = Future()

    def _teardown_if_needed(self) -> None:
        if self._teardown is not None:
            self._teardown(self)


class SerialLogger:
    """Persist human-readable logs of the NDJSON serial stream."""

    def __init__(self, path: Path):
        self._path = Path(path)
        self._file = self._path.open("a", encoding="utf-8")

    def log(self, direction: str, data: bytes) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        text = data.decode("utf-8", errors="replace").lstrip().rstrip("\r\n")
        self._file.write(f"{timestamp} {direction} {text}\n")
        self._file.flush()

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()


class SequenceTracker:
    """Verify monotonic `seq` values and optionally persist the last seen value."""

    def __init__(self, path: Optional[Path] = None):
        self._path = path
        self._last_seq: Optional[int] = None
        if self._path is not None:
            self._initialize_from_file()

    def _initialize_from_file(self) -> None:
        assert self._path is not None
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ValueError(
                f"Unable to create sequence meta directory: {exc}"
            ) from exc
        if not self._path.exists():
            return
        try:
            contents = self._path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ValueError(f"Unable to read sequence meta file: {exc}") from exc
        if not contents:
            return
        try:
            self._last_seq = int(contents)
        except ValueError as exc:
            raise ValueError("Sequence meta file must contain an integer") from exc

    def observe(self, seq: int, *, source: str) -> None:
        if self._last_seq is None:
            self._last_seq = seq
            self._persist()
            return
        expected = self._last_seq + 1
        if seq != expected:
            # Persist the out-of-order value so subsequent runs expect the device's current counter
            self._last_seq = seq
            self._persist()
            raise ShuttleSerialError(
                f"Detected gap in device sequence numbers (expected {expected}, got {seq}) while processing {source}"
            )
        self._last_seq = seq
        self._persist()

    def _persist(self) -> None:
        if self._path is None:
            return
        try:
            self._path.write_text(str(self._last_seq), encoding="utf-8")
        except OSError as exc:
            raise ShuttleSerialError(
                f"Unable to write sequence meta file: {exc}"
            ) from exc


class NDJSONSerialClient:
    """Minimal NDJSON transport over a serial link."""

    def __init__(
        self,
        port: str,
        *,
        baudrate: int = DEFAULT_BAUD,
        timeout: float = DEFAULT_TIMEOUT,
        logger: Optional[SerialLogger] = None,
        seq_tracker: Optional[SequenceTracker] = None,
    ):
        try:
            self._serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        except SerialException as exc:  # pragma: no cover - hardware specific
            raise ShuttleSerialError(f"Unable to open {port}: {exc}") from exc
        self._serial.reset_input_buffer()
        self._lock = threading.Lock()
        self._pending: Dict[int, CommandFuture] = {}
        self._response_backlog: Dict[int, Dict[str, Any]] = {}
        self._event_listeners: Dict[str, List[EventSubscription]] = {}
        self._stop_event = threading.Event()
        self._response_timeout = timeout
        self._logger = logger
        self._seq_tracker = seq_tracker
        self._reader: Optional[threading.Thread] = None

    def __enter__(self) -> "NDJSONSerialClient":
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        if getattr(self, "_reader", None) and self._reader.is_alive():
            self._reader.join(timeout=getattr(self, "_response_timeout", 0.1) or 0.1)
        if hasattr(self, "_pending"):
            self._fail_all(ShuttleSerialError("Serial client closed"))
        if getattr(self, "_serial", None) and self._serial.is_open:
            self._serial.close()

    def send_command(self, op: str, params: Dict[str, Any]) -> CommandFuture:
        """Send a command without blocking, returning a future for the response."""

        cmd_id = self._next_cmd_id()
        message: Dict[str, Any] = {"type": "cmd", "id": cmd_id, "op": op}
        message.update(params)
        future = CommandFuture(cmd_id=cmd_id, timeout=self._response_timeout)
        with self._lock:
            self._pending[cmd_id] = future

        def _cleanup(_future: Future) -> None:
            if hasattr(self, "_lock"):
                self._remove_pending(cmd_id)
            elif hasattr(self, "_pending"):
                self._pending.pop(cmd_id, None)

        future.add_done_callback(_cleanup)
        self._write(message)

        # Start reader after pending entry exists so early responses can be matched
        self._ensure_reader_started()

        # If a response already arrived, deliver immediately
        with self._lock:
            backlog = self._response_backlog.pop(cmd_id, None)
        if backlog is not None:
            future.mark_result(backlog)
        return future

    def register_event_listener(self, event: str) -> EventSubscription:
        """Subscribe to a device event; each emission resolves the subscription future."""

        def teardown(listener: EventSubscription) -> None:
            with self._lock:
                listeners = self._event_listeners.get(event, [])
                if listener in listeners:
                    listeners.remove(listener)
                if not listeners and event in self._event_listeners:
                    self._event_listeners.pop(event, None)

        listener = EventSubscription(event, teardown=teardown)
        with self._lock:
            self._event_listeners.setdefault(event, []).append(listener)
        self._ensure_reader_started()
        return listener

    def spi_xfer(
        self, *, tx: str, n: Optional[int] = None, **overrides: Any
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"tx": tx}
        payload.update(overrides)
        payload["n"] = n if n is not None else len(tx) // 2
        return self._command("spi.xfer", payload)

    def spi_enable(self) -> Dict[str, Any]:
        return self._command("spi.enable", {})

    def spi_disable(self) -> Dict[str, Any]:
        return self._command("spi.disable", {})

    def get_info(self) -> Dict[str, Any]:
        return self._command("get.info", {})

    def ping(self) -> Dict[str, Any]:
        return self._command("ping", {})

    def spi_cfg(self, spi: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if spi:
            payload["spi"] = spi
        return self._command("spi.cfg", payload)

    def uart_cfg(self, uart: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if uart:
            payload["uart"] = uart
        return self._command("uart.cfg", payload)

    def uart_tx(self, data: str, port: Optional[int] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"data": data}
        if port is not None:
            payload["port"] = port
        return self._command("uart.tx", payload)

    def _command(self, op: str, params: Dict[str, Any]) -> Dict[str, Any]:
        future = self.send_command(op, params)
        return future.result()

    def _next_cmd_id(self) -> int:
        with self._lock:
            if self._response_backlog:
                return next(iter(self._response_backlog))
        while True:
            candidate = secrets.randbits(16)
            with self._lock:
                if (
                    candidate != 0
                    and candidate not in self._pending
                    and candidate not in self._response_backlog
                ):
                    return candidate

    def _remove_pending(self, cmd_id: int) -> None:
        with self._lock:
            self._pending.pop(cmd_id, None)

    def _reader_loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                if not self._pending and not self._event_listeners:
                    break
            try:
                message = self._read()
            except ShuttleSerialError as exc:
                self._fail_all(exc)
                break
            if message is None:
                continue
            try:
                self._dispatch(message)
            except ShuttleSerialError as exc:
                self._fail_all(exc)
                return

    def _ensure_reader_started(self) -> None:
        if self._reader is None or not self._reader.is_alive():
            self._reader = threading.Thread(target=self._reader_loop, daemon=True)
            self._reader.start()

    def _write(self, message: Dict[str, Any]) -> None:
        serialized = json.dumps(message, separators=(",", ":"))
        payload = serialized.encode("utf-8") + b"\n"
        with self._lock:
            self._serial.write(payload)
        self._log_serial("TX", payload)

    def _read(self) -> Optional[Dict[str, Any]]:
        try:
            line = self._serial.readline()
        except SerialException as exc:  # pragma: no cover - hardware specific
            raise ShuttleSerialError(f"Serial read failed: {exc}") from exc
        if not line:
            return None
        self._log_serial("RX", line)
        stripped = line.strip()
        if not stripped:
            return None
        try:
            decoded = stripped.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ShuttleSerialError(f"Invalid UTF-8 from device: {exc}") from exc
        try:
            message = json.loads(decoded)
        except json.JSONDecodeError as exc:
            raise ShuttleSerialError(
                f"Invalid JSON from device: {decoded} ({exc})"
            ) from exc
        self._record_sequence(message)
        return message

    def _dispatch(self, message: Dict[str, Any]) -> None:
        mtype = message.get("type")
        if mtype == "resp":
            resp_id = message.get("id")
            if resp_id is None:
                raise ShuttleSerialError("Device response missing id field")
            with self._lock:
                future = self._pending.pop(resp_id, None)
            if future is None:
                with self._lock:
                    self._response_backlog[resp_id] = message
                return
            future.mark_result(message)
        elif mtype == "ev":
            ev_name = message.get("ev")
            if not isinstance(ev_name, str):
                raise ShuttleSerialError("Device event missing ev field")
            with self._lock:
                listeners = list(self._event_listeners.get(ev_name, []))
            for listener in listeners:
                listener.emit(message)
        else:
            raise ShuttleSerialError(f"Received unexpected payload: {message}")

    def _log_serial(self, direction: str, payload: bytes) -> None:
        logger = getattr(self, "_logger", None)
        if logger is not None:
            logger.log(direction, payload)

    def _record_sequence(self, message: Dict[str, Any]) -> None:
        tracker = getattr(self, "_seq_tracker", None)
        if tracker is None:
            return
        seq_value = message.get("seq")
        if not isinstance(seq_value, int):
            return
        mtype = message.get("type", "?")
        if mtype == "resp" and "id" in message:
            source = f"response id={message['id']}"
        elif mtype == "ev" and "ev" in message:
            source = f"event {message['ev']}"
        else:
            source = mtype
        tracker.observe(seq_value, source=source)

    def _fail_all(self, exc: BaseException) -> None:
        with self._lock:
            pending = list(self._pending.values())
            self._pending.clear()
            self._response_backlog.clear()
            listeners: List[EventSubscription] = []
            for group in self._event_listeners.values():
                listeners.extend(group)
            self._event_listeners.clear()
        for future in pending:
            future.mark_exception(exc)
        for listener in listeners:
            listener.fail(exc)
