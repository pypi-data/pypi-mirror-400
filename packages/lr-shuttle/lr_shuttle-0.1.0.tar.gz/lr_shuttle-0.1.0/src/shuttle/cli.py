#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import string
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import atexit
import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

from . import prodtest, timo
from .constants import (
    DEFAULT_BAUD,
    DEFAULT_TIMEOUT,
    SPI_CHOICE_FIELDS,
    UART_PARITY_ALIASES,
)
from .serial_client import (
    NDJSONSerialClient,
    SerialLogger,
    SequenceTracker,
    ShuttleSerialError,
)

app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="Shuttle command-line utility"
)
timo_app = typer.Typer(help="TiMo SPI helpers")
app.add_typer(timo_app, name="timo", help="Interact with TiMo over SPI")
prodtest_app = typer.Typer(help="Prodtest SPI helpers")
app.add_typer(
    prodtest_app, name="prodtest", help="Interact with prodtest firmware over SPI"
)

console = Console()

# Backwards-compatible aliases for tests and external callers
_SerialLogger = SerialLogger
_SequenceTracker = SequenceTracker


def _ctx_resources(ctx: typer.Context) -> Dict[str, Optional[object]]:
    return ctx.obj or {}


@contextmanager
def spinner(message: str, enabled: bool = True):
    """Show a Rich spinner while the body executes."""

    if enabled and sys.stdout.isatty():
        with console.status(message, spinner="dots"):
            yield
    else:
        yield


def _normalize_choice(value: Optional[str], *, name: str) -> Optional[str]:
    if value is None:
        return None
    choices = SPI_CHOICE_FIELDS.get(name)
    if choices is None:
        return value
    normalized = value.lower()
    if normalized not in choices:
        allowed = ", ".join(sorted(choices))
        raise typer.BadParameter(f"{name} must be one of: {allowed}")
    return normalized


def _normalize_uart_parity(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    trimmed = value.strip().lower()
    if not trimmed:
        return None
    mapped = UART_PARITY_ALIASES.get(trimmed)
    if mapped is not None:
        return mapped
    first = trimmed[0]
    if first in ("n", "e", "o"):
        return first
    allowed = ", ".join(sorted({"n", "e", "o", "none", "even", "odd"}))
    raise typer.BadParameter(f"parity must be one of: {allowed}")


def _normalize_hex_payload(value: str) -> str:
    cleaned = "".join(ch for ch in value if not ch.isspace() and ch != "_")
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]
    if not cleaned:
        raise typer.BadParameter("UART payload cannot be empty")
    if len(cleaned) % 2 != 0:
        raise typer.BadParameter(
            "UART payload must contain an even number of hex digits"
        )
    if any(ch not in string.hexdigits for ch in cleaned):
        raise typer.BadParameter("UART payload must be valid hex")
    return cleaned.lower()


def _resolve_uart_payload(
    *,
    data_arg: Optional[str],
    text_payload: Optional[str],
    file_path: Optional[Path],
    encoding: str,
    append_newline: bool,
) -> Tuple[str, int]:
    sources = {
        "hex": data_arg not in (None, "-"),
        "stdin": data_arg == "-",
        "text": text_payload is not None,
        "file": file_path is not None,
    }
    used = [name for name, active in sources.items() if active]
    if not used:
        raise typer.BadParameter(
            "Provide UART data as HEX argument, --text, --file, or '-' for stdin"
        )
    if len(used) > 1:
        raise typer.BadParameter(
            "Specify exactly one UART payload source (HEX, --text, --file, or '-')"
        )

    source = used[0]
    if source == "hex":
        if append_newline:
            raise typer.BadParameter(
                "--newline is only valid with --text, --file, or '-' payloads"
            )
        normalized = _normalize_hex_payload(data_arg or "")
        length = len(normalized) // 2
        if length == 0:
            raise typer.BadParameter("UART payload cannot be empty")
        return normalized, length

    if source == "text":
        assert text_payload is not None
        try:
            payload_bytes = text_payload.encode(encoding)
        except LookupError as exc:
            raise typer.BadParameter(f"Unknown encoding '{encoding}'") from exc
    elif source == "file":
        assert file_path is not None
        try:
            payload_bytes = file_path.read_bytes()
        except OSError as exc:
            raise typer.BadParameter(f"Unable to read {file_path}: {exc}") from exc
    else:  # stdin
        payload_bytes = sys.stdin.buffer.read()

    if append_newline:
        payload_bytes += b"\n"

    if not payload_bytes:
        raise typer.BadParameter("UART payload cannot be empty")

    return payload_bytes.hex(), len(payload_bytes)


def _require_port(port: Optional[str]) -> str:
    if port:
        return port
    raise typer.BadParameter("Serial port is required (use --port or SHUTTLE_PORT)")


def _parse_int_option(value: str, *, name: str) -> int:
    try:
        parsed = int(value, 0)
    except ValueError as exc:
        raise typer.BadParameter(
            f"{name} must be an integer literal (e.g. 5 or 0x05)"
        ) from exc
    if parsed < 0:
        raise typer.BadParameter(f"{name} must be non-negative")
    return parsed


def _parse_prodtest_mask(value: str) -> bytes:
    try:
        return prodtest.mask_from_hex(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _format_hex(hex_str: str) -> str:
    if not hex_str:
        return "—"
    grouped = [hex_str[i : i + 2] for i in range(0, len(hex_str), 2)]
    return " ".join(grouped)


def _decode_hex_response(response: Dict[str, Any], *, label: str) -> bytes:
    data = response.get("rx")
    if not isinstance(data, str):
        console.print(f"[red]{label} missing RX payload[/]")
        raise typer.Exit(1)
    try:
        return bytes.fromhex(data)
    except ValueError as exc:
        console.print(f"[red]{label} RX payload is not valid hex[/]")
        raise typer.Exit(1) from exc


def _format_failed_pins_line(failed: Sequence[int]) -> str:
    if not failed:
        return "Test failed on pins: [ ]"
    joined = ", ".join(str(pin) for pin in failed)
    return f"Test failed on pins: [ {joined} ]"


def _build_status_table(title: str, response: Dict[str, Any]) -> Table:
    table = Table(title=title, show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    status = "OK" if response.get("ok") else "ERROR"
    status_color = "green" if response.get("ok") else "red"
    table.add_row("Status", f"[{status_color}]{status}[/]")
    if response.get("err"):
        err = response["err"]
        code = err.get("code", "?")
        msg = err.get("msg", "")
        table.add_row("Error", f"{code}: {msg}")
    return table


def _render_spi_response(
    title: str, response: Dict[str, Any], *, command_label: str
) -> None:
    table = _build_status_table(title, response)
    table.add_row("Command", command_label)
    if response.get("ok") and "rx" in response:
        table.add_row("RX", _format_hex(response.get("rx", "")))
    irq_level = response.get("irq")
    if irq_level is not None:
        table.add_row("IRQ level", str(irq_level))
    console.print(table)


def _render_read_reg_result(
    result: timo.ReadRegisterResult, rx_frames: Sequence[str]
) -> None:
    data_table = Table(title="TiMo read-reg", show_header=False, box=None)
    data_table.add_column("Field", style="cyan", no_wrap=True)
    data_table.add_column("Value", style="white")
    data_table.add_row("Address", f"0x{result.address:02X}")
    data_table.add_row("Length", str(result.length))
    data_table.add_row("Data", timo.format_bytes(result.data))
    data_table.add_row("IRQ (command)", f"0x{result.irq_flags_command:02X}")
    data_table.add_row("IRQ (payload)", f"0x{result.irq_flags_payload:02X}")
    data_table.add_row("Command RX", _format_hex(rx_frames[0]))
    data_table.add_row("Payload RX", _format_hex(rx_frames[1]))
    console.print(data_table)

    warnings: List[str] = []
    for label, value in ("command", result.irq_flags_command), (
        "payload",
        result.irq_flags_payload,
    ):
        if timo.requires_restart(value):
            warnings.append(
                f"IRQ bit7 asserted during {label} phase — resend the entire sequence per TiMo spec."
            )
    if warnings:
        console.print(
            Panel("\n".join(warnings), title="IRQ warning", border_style="yellow")
        )


def _render_write_reg_result(
    result: timo.WriteRegisterResult, rx_frames: Sequence[str]
) -> None:
    data_table = Table(title="TiMo write-reg", show_header=False, box=None)
    data_table.add_row("Address", f"0x{result.address:02X}")
    data_table.add_row("Data written", timo.format_bytes(result.data))
    data_table.add_row("IRQ flags (cmd)", f"0x{result.irq_flags_command:02X}")
    data_table.add_row("IRQ flags (payload)", f"0x{result.irq_flags_payload:02X}")
    console.print(data_table)
    for label, value in zip(
        ["command", "payload"], [result.irq_flags_command, result.irq_flags_payload]
    ):
        if timo.requires_restart(value):
            console.print(
                f"[yellow]IRQ bit7 asserted during {label} phase — resend the entire sequence per TiMo spec.[/]"
            )


def _render_read_dmx_result(result, rx_frames):
    data_table = Table(title="TiMo read-dmx", show_header=False, box=None)
    data_table.add_row("Length", str(result.length))
    data_table.add_row("Data", timo.format_bytes(result.data))
    data_table.add_row("IRQ (command phase)", f"0x{result.irq_flags_command:02X}")
    data_table.add_row("IRQ (payload phase)", f"0x{result.irq_flags_payload:02X}")
    console.print(data_table)
    for label, value in zip(
        ["command", "payload"], [result.irq_flags_command, result.irq_flags_payload]
    ):
        if timo.requires_restart(value):
            console.print(
                f"[yellow]IRQ bit7 asserted during {label} phase — resend the entire sequence per TiMo spec.[/]"
            )


def _execute_timo_sequence(
    *,
    port: Optional[str],
    baudrate: int,
    timeout: float,
    sequence: Sequence[Dict[str, Any]],
    spinner_label: str,
    logger: Optional[SerialLogger],
    seq_tracker: Optional[SequenceTracker],
) -> List[Dict[str, Any]]:
    resolved_port = _require_port(port)
    responses: List[Dict[str, Any]] = []
    with spinner(f"{spinner_label} over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=logger,
                seq_tracker=seq_tracker,
            ) as client:
                for transfer in sequence:
                    response = client.spi_xfer(**transfer)
                    responses.append(response)
                    if not response.get("ok"):
                        break
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc
    return responses


def _render_payload_response(
    title: str, response: Dict[str, Any], *, drop_fields: Optional[Set[str]] = None
) -> None:
    table = _build_status_table(title, response)
    console.print(table)
    if not response.get("ok"):
        return
    drop = drop_fields if drop_fields is not None else {"type", "id", "ok"}
    payload = {k: v for k, v in response.items() if k not in drop}
    if not payload:
        console.print("[yellow]Device returned no additional info[/]")
        return
    console.print(
        Panel(
            Pretty(payload, expand_all=True),
            title=f"{title} payload",
            border_style="cyan",
        )
    )


def _render_info_response(response: Dict[str, Any]) -> None:
    _render_payload_response("get.info", response)


def _render_ping_response(response: Dict[str, Any]) -> None:
    _render_payload_response("ping", response)


@app.callback()
def main(
    ctx: typer.Context,
    log: Optional[Path] = typer.Option(
        None,
        "--log",
        help="Append raw serial RX/TX lines with timestamps to the given file",
        show_default=False,
        metavar="FILE",
    ),
    seq_meta: Optional[Path] = typer.Option(
        None,
        "--seq-meta",
        help="Persist last observed device sequence number to ensure gap detection across runs",
        show_default=False,
        metavar="FILE",
    ),
) -> None:
    """Interact with the Shuttle devboard over the JSON serial link."""

    logger = SerialLogger(log) if log else None
    tracker: Optional[SequenceTracker]
    try:
        tracker = (
            SequenceTracker(seq_meta) if seq_meta is not None else SequenceTracker()
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    ctx.obj = {"logger": logger, "seq_tracker": tracker}
    if logger is not None:
        atexit.register(logger.close)


@timo_app.command("nop")
def timo_nop(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Send a TiMo NOP SPI transfer over the Shuttle link."""

    resources = _ctx_resources(ctx)
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=timo.nop_sequence(),
        spinner_label="Sending TiMo NOP",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)
    _render_spi_response("TiMo NOP", responses[0], command_label="spi.xfer (NOP)")


@timo_app.command("read-reg")
def timo_read_reg(
    ctx: typer.Context,
    address: str = typer.Option(
        ..., "--addr", "--address", help="Register address (decimal or 0x-prefixed)"
    ),
    length: int = typer.Option(
        1,
        "--length",
        min=1,
        max=timo.READ_REG_MAX_LEN,
        help=f"Bytes to read (1..{timo.READ_REG_MAX_LEN})",
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read a TiMo register via a two-phase SPI sequence."""

    resources = _ctx_resources(ctx)
    addr_value = _parse_int_option(address, name="address")
    try:
        sequence = timo.read_reg_sequence(addr_value, length)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label=f"Reading TiMo register 0x{addr_value:02X}",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )

    if not responses:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)

    failed_idx = next(
        (idx for idx, resp in enumerate(responses) if not resp.get("ok")), None
    )
    if failed_idx is not None:
        phase = "command" if failed_idx == 0 else "payload"
        _render_spi_response(
            f"TiMo read-reg ({phase})",
            responses[failed_idx],
            command_label=f"spi.xfer ({phase} phase)",
        )
        raise typer.Exit(1)

    if len(responses) != len(sequence):
        console.print("[red]Command halted before completing all SPI phases[/]")
        raise typer.Exit(1)

    rx_frames = [resp.get("rx", "") for resp in responses]
    try:
        parsed = timo.parse_read_reg_response(addr_value, length, rx_frames)
    except ValueError as exc:
        console.print(f"[red]Unable to parse read-reg response: {exc}[/]")
        raise typer.Exit(1) from exc

    _render_spi_response(
        "TiMo read-reg",
        responses[-1],
        command_label="spi.xfer (payload phase)",
    )
    _render_read_reg_result(parsed, rx_frames)


@timo_app.command("status")
def timo_status(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read and render the TiMo STATUS register with bit breakdown."""

    resources = _ctx_resources(ctx)
    reg_meta = timo.REGISTER_MAP["STATUS"]
    length = reg_meta.get("length", 1)
    sequence = timo.read_reg_sequence(reg_meta["address"], length)

    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label="Reading TiMo STATUS",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses or not responses[-1].get("ok"):
        console.print("[red]Failed to read STATUS register[/]")
        raise typer.Exit(1)

    rx = responses[-1].get("rx", "")
    payload = bytes.fromhex(rx) if isinstance(rx, str) else b""
    irq_flags = payload[:1]
    data = payload[1:] if len(payload) > 1 else b""
    status_byte = data[0] if data else 0

    table = Table(title="TiMo STATUS (0x01)", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Raw", f"0x{status_byte:02X}")
    table.add_row("IRQ flags", timo.format_bytes(irq_flags))

    fields = reg_meta["fields"]

    def bit_set(bit: int) -> bool:
        return bool(status_byte & (1 << bit))

    for name, meta in fields.items():
        lo, hi = meta["bits"]
        if lo != hi:
            val = (status_byte >> lo) & ((1 << (hi - lo + 1)) - 1)
            display = f"{val}"
        else:
            display = "ON" if bit_set(lo) else "off"
        table.add_row(name, display)

    console.print(table)


@timo_app.command("link")
def timo_link(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Force TiMo into link mode by setting RF_LINK bit in STATUS register."""

    resources = _ctx_resources(ctx)
    # Set RF_LINK bit in STATUS.
    sequence = timo.write_reg_sequence(0x01, bytes([0x02]))  # RF_LINK bit set
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label="Setting TiMo RF_LINK",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if (
        not responses
        or len(responses) < len(sequence)
        or not all(resp.get("ok") for resp in responses)
    ):
        console.print("[red]Failed to set RF_LINK[/]")
        raise typer.Exit(1)

    table = Table(title="TiMo link", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Register", "STATUS (0x01) RF_LINK=1")
    table.add_row("Result", "[green]OK[/]")
    console.print(table)


@timo_app.command("unlink")
def timo_unlink(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Unlink TiMo by setting the LINKED bit in STATUS to 1 (write-to-unlink)."""

    resources = _ctx_resources(ctx)
    status_sequence = timo.write_reg_sequence(0x01, bytes([0x01]))  # LINKED bit set
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=status_sequence,
        spinner_label="Clearing TiMo link",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses or not all(resp.get("ok") for resp in responses):
        console.print("[red]Failed to unlink[/]")
        raise typer.Exit(1)

    table = Table(title="TiMo unlink", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Register", "STATUS (0x01) LINKED=1 (unlink)")
    table.add_row("Result", "[green]OK[/]")
    console.print(table)


@timo_app.command("antenna")
def timo_antenna(
    ctx: typer.Context,
    value: Optional[str] = typer.Argument(
        None,
        metavar="[on-board|ipex]",
        help="Read current antenna when omitted; set antenna when provided",
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Get or set the selected antenna (on-board or IPEX/u.FL)."""

    resources = _ctx_resources(ctx)
    reg_meta = timo.REGISTER_MAP["ANTENNA"]
    spinner_label = "Reading TiMo antenna"
    sequence = timo.read_reg_sequence(reg_meta["address"], reg_meta.get("length", 1))

    set_value: Optional[int] = None
    if value is not None:
        normalized = value.strip().lower()
        if normalized not in ("on-board", "ipex", "ipx", "u.fl", "u-fl", "ufl"):
            raise typer.BadParameter("antenna must be 'on-board' or 'ipex'")
        set_value = 0 if normalized == "on-board" else 1
        spinner_label = f"Setting TiMo antenna to {normalized}"
        sequence = timo.write_reg_sequence(reg_meta["address"], bytes([set_value]))

    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label=spinner_label,
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses or not responses[-1].get("ok"):
        console.print("[red]Antenna operation failed[/]")
        raise typer.Exit(1)

    table = Table(
        title="TiMo antenna",
        show_header=False,
        box=None,
    )
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    if set_value is None:
        rx = responses[-1].get("rx", "")
        payload = bytes.fromhex(rx) if isinstance(rx, str) else b""
        antenna_byte = payload[1] if len(payload) > 1 else 0  # skip IRQ flags
        selection = "on-board" if (antenna_byte & 0x01) == 0 else "ipex"
        table.add_row("Register", "ANTENNA (0x07)")
        table.add_row("Selected", selection)
    else:
        table.add_row("Action", f"Set to {'on-board' if set_value == 0 else 'ipex'}")
        table.add_row("Status", "[green]OK[/]")

    console.print(table)


@timo_app.command("link-quality")
def timo_link_quality(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read TiMo link quality register and render packet delivery rate."""

    resources = _ctx_resources(ctx)
    reg_meta = timo.REGISTER_MAP["LINK_QUALITY"]
    sequence = timo.read_reg_sequence(reg_meta["address"], reg_meta.get("length", 1))
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label="Reading TiMo link quality",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses or not responses[-1].get("ok"):
        console.print("[red]Failed to read link quality[/]")
        raise typer.Exit(1)

    rx = responses[-1].get("rx", "")
    payload = bytes.fromhex(rx) if isinstance(rx, str) else b""
    pdr = payload[1] if len(payload) > 1 else 0  # skip IRQ flags
    percent = pdr / 255 * 100

    table = Table(title="TiMo Link Quality", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Register", "LINK_QUALITY (0x06)")
    table.add_row("Raw", f"0x{pdr:02X}")
    table.add_row("PDR", f"{percent:.1f}%")
    console.print(table)


@timo_app.command("dmx")
def timo_dmx(
    ctx: typer.Context,
    window_size: Optional[str] = typer.Option(
        None,
        "--window-size",
        help="DMX window size (0-65535)",
    ),
    start_address: Optional[str] = typer.Option(
        None,
        "--start-address",
        help="DMX window start address",
    ),
    n_channels: Optional[str] = typer.Option(
        None,
        "--channels",
        help="Number of channels to generate",
    ),
    interslot_time: Optional[str] = typer.Option(
        None,
        "--interslot",
        help="Interslot spacing in microseconds",
    ),
    refresh_period: Optional[str] = typer.Option(
        None,
        "--refresh",
        help="DMX frame length in microseconds",
    ),
    enable: bool = typer.Option(
        False, "--enable", help="Enable internal DMX generation", show_default=False
    ),
    disable: bool = typer.Option(
        False, "--disable", help="Disable internal DMX generation", show_default=False
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read or update TiMo DMX registers (window, spec, control)."""

    resources = _ctx_resources(ctx)
    desired_enable: Optional[bool] = True if enable else False if disable else None

    def _parse_opt(value: Optional[str], name: str) -> Optional[int]:
        return _parse_int_option(value, name=name) if value is not None else None

    parsed_window = _parse_opt(window_size, "window_size")
    parsed_start = _parse_opt(start_address, "start_address")
    parsed_channels = _parse_opt(n_channels, "channels")
    parsed_interslot = _parse_opt(interslot_time, "interslot_time")
    parsed_refresh = _parse_opt(refresh_period, "refresh_period")

    reg_window = timo.REGISTER_MAP["DMX_WINDOW"]
    reg_spec = timo.REGISTER_MAP["DMX_SPEC"]
    reg_ctrl = timo.REGISTER_MAP["DMX_CONTROL"]

    resolved_port = _require_port(port)

    def _read_register(client, reg_meta):
        seq = timo.read_reg_sequence(reg_meta["address"], reg_meta.get("length", 1))
        responses = [client.spi_xfer(**cmd) for cmd in seq]
        rx = responses[-1].get("rx", "")
        payload = bytes.fromhex(rx) if isinstance(rx, str) else b""
        return payload[1:] if payload else b""

    def _set_bits(base: int, lo: int, hi: int, value: int, total_bits: int) -> int:
        width = hi - lo + 1
        mask = ((1 << width) - 1) << (total_bits - hi - 1)
        return (base & ~mask) | ((value & ((1 << width) - 1)) << (total_bits - hi - 1))

    with NDJSONSerialClient(
        resolved_port,
        baudrate=baudrate,
        timeout=timeout,
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    ) as client:
        # Read current values
        window_bytes = _read_register(client, reg_window)
        spec_bytes = _read_register(client, reg_spec)
        ctrl_bytes = _read_register(client, reg_ctrl)

        window_int = int.from_bytes(
            window_bytes.ljust(reg_window["length"], b"\x00"), "big"
        )
        spec_int = int.from_bytes(spec_bytes.ljust(reg_spec["length"], b"\x00"), "big")
        ctrl_int = int.from_bytes(ctrl_bytes.ljust(reg_ctrl["length"], b"\x00"), "big")

        # Apply updates if provided
        any_change = False
        total_window_bits = reg_window["length"] * 8
        if parsed_window is not None:
            window_int = _set_bits(
                window_int,
                *reg_window["fields"]["WINDOW_SIZE"]["bits"],
                parsed_window,
                total_window_bits,
            )
            any_change = True
        if parsed_start is not None:
            window_int = _set_bits(
                window_int,
                *reg_window["fields"]["START_ADDRESS"]["bits"],
                parsed_start,
                total_window_bits,
            )
            any_change = True

        total_spec_bits = reg_spec["length"] * 8
        if parsed_channels is not None:
            spec_int = _set_bits(
                spec_int,
                *reg_spec["fields"]["N_CHANNELS"]["bits"],
                parsed_channels,
                total_spec_bits,
            )
            any_change = True
        if parsed_interslot is not None:
            spec_int = _set_bits(
                spec_int,
                *reg_spec["fields"]["INTERSLOT_TIME"]["bits"],
                parsed_interslot,
                total_spec_bits,
            )
            any_change = True
        if parsed_refresh is not None:
            spec_int = _set_bits(
                spec_int,
                *reg_spec["fields"]["REFRESH_PERIOD"]["bits"],
                parsed_refresh,
                total_spec_bits,
            )
            any_change = True

        if desired_enable is not None:
            total_ctrl_bits = reg_ctrl["length"] * 8
            ctrl_int = _set_bits(
                ctrl_int,
                *reg_ctrl["fields"]["ENABLE"]["bits"],
                1 if desired_enable else 0,
                total_ctrl_bits,
            )
            any_change = True

        if any_change:
            # Write back registers that changed
            write_sequences = [
                timo.write_reg_sequence(
                    reg_window["address"],
                    window_int.to_bytes(reg_window["length"], "big"),
                ),
                timo.write_reg_sequence(
                    reg_spec["address"], spec_int.to_bytes(reg_spec["length"], "big")
                ),
                timo.write_reg_sequence(
                    reg_ctrl["address"], ctrl_int.to_bytes(reg_ctrl["length"], "big")
                ),
            ]
            for seq in write_sequences:
                for cmd in seq:
                    client.spi_xfer(**cmd)

        # Prepare display values (after potential updates)
        window_size_val = timo.slice_bits(
            window_int.to_bytes(reg_window["length"], "big"),
            *reg_window["fields"]["WINDOW_SIZE"]["bits"],
        )
        start_val = timo.slice_bits(
            window_int.to_bytes(reg_window["length"], "big"),
            *reg_window["fields"]["START_ADDRESS"]["bits"],
        )
        channels_val = timo.slice_bits(
            spec_int.to_bytes(reg_spec["length"], "big"),
            *reg_spec["fields"]["N_CHANNELS"]["bits"],
        )
        interslot_val = timo.slice_bits(
            spec_int.to_bytes(reg_spec["length"], "big"),
            *reg_spec["fields"]["INTERSLOT_TIME"]["bits"],
        )
        refresh_val = timo.slice_bits(
            spec_int.to_bytes(reg_spec["length"], "big"),
            *reg_spec["fields"]["REFRESH_PERIOD"]["bits"],
        )
        enable_val = bool(
            timo.slice_bits(
                ctrl_int.to_bytes(reg_ctrl["length"], "big"),
                *reg_ctrl["fields"]["ENABLE"]["bits"],
            )
        )

    table = Table(title="TiMo DMX", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Window size", str(window_size_val))
    table.add_row("Start address", str(start_val))
    table.add_row("Channels", str(channels_val))
    table.add_row("Interslot (us)", str(interslot_val))
    table.add_row("Refresh (us)", str(refresh_val))
    table.add_row("Enable", "ON" if enable_val else "off")
    console.print(table)


@timo_app.command("radio-mode")
def timo_radio_mode(
    ctx: typer.Context,
    mode: Optional[str] = typer.Option(
        None, "--mode", help="Set radio mode: rx or tx", case_sensitive=False
    ),
    enable: bool = typer.Option(
        False, "--enable", help="Enable wireless operation", show_default=False
    ),
    disable: bool = typer.Option(
        False, "--disable", help="Disable wireless operation", show_default=False
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read or set TiMo radio mode and wireless enable (CONFIG register)."""

    if enable and disable:
        raise typer.BadParameter("Cannot specify both --enable and --disable")
    desired_mode: Optional[int] = None
    if mode:
        normalized = mode.strip().lower()
        if normalized not in ("rx", "tx"):
            raise typer.BadParameter("mode must be rx or tx")
        desired_mode = 0 if normalized == "rx" else 1

    resources = _ctx_resources(ctx)
    reg_meta = timo.REGISTER_MAP["CONFIG"]
    seq = timo.read_reg_sequence(reg_meta["address"], reg_meta.get("length", 1))

    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=seq,
        spinner_label="Reading TiMo CONFIG",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses or not responses[-1].get("ok"):
        console.print("[red]Failed to read CONFIG[/]")
        raise typer.Exit(1)

    payload = (
        bytes.fromhex(responses[-1].get("rx", ""))
        if isinstance(responses[-1].get("rx"), str)
        else b""
    )
    config_byte = payload[1] if len(payload) > 1 else 0
    new_byte = config_byte

    if desired_mode is not None:
        new_byte = (new_byte & ~(1 << 1)) | (desired_mode << 1)
    if enable:
        new_byte = new_byte | (1 << 7)
    if disable:
        new_byte = new_byte & ~(1 << 7)

    if new_byte != config_byte:
        write_seq = timo.write_reg_sequence(reg_meta["address"], bytes([new_byte]))
        for cmd in write_seq:
            resp = _execute_timo_sequence(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                sequence=[cmd],
                spinner_label="Writing TiMo CONFIG",
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            )
            if not resp or not resp[-1].get("ok"):
                console.print("[red]Failed to update CONFIG[/]")
                raise typer.Exit(1)
        config_byte = new_byte

    table = Table(title="TiMo Radio Mode", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("CONFIG (0x00)", f"0x{config_byte:02X}")
    mode_str = "tx" if config_byte & (1 << 1) else "rx"
    table.add_row("RADIO_TX_RX_MODE", mode_str)
    table.add_row("SPI_RDM", "enabled" if config_byte & (1 << 3) else "disabled")
    table.add_row("RADIO_ENABLE", "ON" if config_byte & (1 << 7) else "off")
    console.print(table)


@timo_app.command("device-name")
def timo_device_name(
    ctx: typer.Context,
    name: Optional[str] = typer.Argument(
        None,
        help="New device name (omit to read current). Will be truncated to register length.",
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read or write the TiMo device name register."""

    resources = _ctx_resources(ctx)
    reg_meta = timo.REGISTER_MAP["DEVICE_NAME"]
    resolved_port = _require_port(port)

    def _read_name(client) -> str:
        seq = timo.read_reg_sequence(reg_meta["address"], reg_meta.get("length", 16))
        responses = [client.spi_xfer(**cmd) for cmd in seq]
        rx = responses[-1].get("rx", "")
        payload = bytes.fromhex(rx) if isinstance(rx, str) else b""
        data = payload[1:] if payload else b""
        return data.split(b"\x00", 1)[0].decode("ascii", errors="replace")

    with NDJSONSerialClient(
        resolved_port,
        baudrate=baudrate,
        timeout=timeout,
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    ) as client:
        if name is None:
            current = _read_name(client)
            table = Table(title="TiMo device name", show_header=False, box=None)
            table.add_column("Field", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            table.add_row("Current", current)
            console.print(table)
            return

        encoded = name.encode("ascii", errors="ignore")[: reg_meta["length"]]
        payload = encoded.ljust(reg_meta["length"], b"\x00")
        write_seq = timo.write_reg_sequence(reg_meta["address"], payload)
        for cmd in write_seq:
            resp = client.spi_xfer(**cmd)
            if not resp.get("ok"):
                console.print("[red]Failed to write device name[/]")
                raise typer.Exit(1)

        updated = _read_name(client)

    table = Table(title="TiMo device name", show_header=False, box=None)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Updated", updated)
    console.print(table)


@timo_app.command("write-reg")
def timo_write_reg(
    ctx: typer.Context,
    address: str = typer.Option(
        ..., "--addr", "--address", help="Register address (decimal or 0x-prefixed)"
    ),
    data: str = typer.Option(..., "--data", help="Hex bytes to write (e.g. cafebabe)"),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Write a TiMo register via a two-phase SPI sequence."""
    resources = _ctx_resources(ctx)
    addr_value = _parse_int_option(address, name="address")
    try:
        data_bytes = bytes.fromhex(data)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid hex for data: {exc}") from exc
    try:
        sequence = timo.write_reg_sequence(addr_value, data_bytes)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label=f"Writing TiMo register 0x{addr_value:02X}",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )

    if not responses:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)

    failed_idx = next(
        (idx for idx, resp in enumerate(responses) if not resp.get("ok")), None
    )
    if failed_idx is not None:
        phase = "command" if failed_idx == 0 else "payload"
        _render_spi_response(
            f"TiMo write-reg ({phase})",
            responses[failed_idx],
            command_label=f"spi.xfer ({phase} phase)",
        )
        raise typer.Exit(1)

    if len(responses) != len(sequence):
        console.print("[red]Command halted before completing all SPI phases[/]")
        raise typer.Exit(1)

    rx_frames = [resp.get("rx", "") for resp in responses]
    try:
        parsed = timo.parse_write_reg_response(addr_value, data_bytes, rx_frames)
    except ValueError as exc:
        console.print(f"[red]Unable to parse write-reg response: {exc}[/]")
        raise typer.Exit(1) from exc

    _render_spi_response(
        "TiMo write-reg",
        responses[-1],
        command_label="spi.xfer (payload phase)",
    )
    _render_write_reg_result(parsed, rx_frames)


@timo_app.command("read-dmx")
def timo_read_dmx(
    ctx: typer.Context,
    length: int = typer.Option(
        32,
        "--length",
        min=1,
        max=timo.DMX_READ_MAX_LEN,
        help=f"Bytes to read (1..{timo.DMX_READ_MAX_LEN})",
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Read the latest received DMX values from TiMo via a two-phase SPI sequence."""
    resources = _ctx_resources(ctx)
    try:
        sequence = timo.read_dmx_sequence(length)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label=f"Reading DMX values (length={length})",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )

    if not responses:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)

    failed_idx = next(
        (idx for idx, resp in enumerate(responses) if not resp.get("ok")), None
    )
    if failed_idx is not None:
        phase = "command" if failed_idx == 0 else "payload"
        _render_spi_response(
            f"TiMo read-dmx ({phase})",
            responses[failed_idx],
            command_label=f"spi.xfer ({phase} phase)",
        )
        raise typer.Exit(1)

    if len(responses) != len(sequence):
        console.print("[red]Command halted before completing all SPI phases[/]")
        raise typer.Exit(1)

    rx_frames = [resp.get("rx", "") for resp in responses]
    try:
        parsed = timo.parse_read_dmx_response(length, rx_frames)
    except ValueError as exc:
        console.print(f"[red]Unable to parse read-dmx response: {exc}[/]")
        raise typer.Exit(1) from exc

    _render_spi_response(
        "TiMo read-dmx",
        responses[-1],
        command_label="spi.xfer (payload phase)",
    )
    _render_read_dmx_result(parsed, rx_frames)


@prodtest_app.command("reset")
def prodtest_reset(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyACM0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Send the prodtest '?' command to reset the attached module over SPI."""

    resources = _ctx_resources(ctx)
    sequence = [prodtest.reset_transfer()]
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label="Sending prodtest reset",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)
    _render_spi_response(
        "prodtest reset", responses[0], command_label="spi.xfer (prodtest)"
    )


@prodtest_app.command("ping")
def prodtest_ping(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyACM0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Send the prodtest 'ping' command: send '+' and expect '-' back."""
    resources = _ctx_resources(ctx)
    sequence = prodtest.ping_sequence()
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label="Sending prodtest ping",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )
    if not responses or len(responses) < 2:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)
    rx2 = responses[1].get("rx", "")
    if rx2 and isinstance(rx2, str):
        rx_bytes = bytes.fromhex(rx2)
        if rx_bytes and rx_bytes[0] == 0x2D:  # ord('-')
            console.print("[green]Ping successful: got '-' response[/]")
            return
    console.print(f"[red]Ping failed: expected '-' (0x2D), got: {rx2}[/]")
    raise typer.Exit(1)


@prodtest_app.command("io-self-test")
def prodtest_io_self_test(
    ctx: typer.Context,
    pins_mask: str = typer.Argument(
        ...,
        metavar="PINS",
        help="Eight-byte hex mask describing pins 1-64 (e.g. 0000000000000004)",
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyACM0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Perform the prodtest GPIO self-test (opcode 'T')."""

    resources = _ctx_resources(ctx)
    mask_bytes = _parse_prodtest_mask(pins_mask)
    sequence = prodtest.io_self_test(mask_bytes)
    responses = _execute_timo_sequence(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        sequence=sequence,
        spinner_label="Running prodtest IO self-test",
        logger=resources.get("logger"),
        seq_tracker=resources.get("seq_tracker"),
    )

    if not responses:
        console.print("[red]Device returned no response[/]")
        raise typer.Exit(1)

    if len(responses) != len(sequence):
        console.print(
            "[red]Prodtest command halted before completing all SPI phases[/]"
        )
        raise typer.Exit(1)

    stage_labels = ("command", "result")
    failed_idx = next(
        (idx for idx, resp in enumerate(responses) if not resp.get("ok")), None
    )
    if failed_idx is not None:
        stage = stage_labels[failed_idx]
        _render_spi_response(
            f"prodtest io-self-test ({stage})",
            responses[failed_idx],
            command_label=f"spi.xfer (prodtest {stage})",
        )
        raise typer.Exit(1)

    result_response = responses[-1]
    _render_spi_response(
        "prodtest io-self-test",
        result_response,
        command_label="spi.xfer (prodtest result)",
    )

    rx_bytes = _decode_hex_response(
        result_response, label="prodtest io-self-test result"
    )
    if len(rx_bytes) < prodtest.IO_SELF_TEST_MASK_LEN:
        console.print("[red]Prodtest response shorter than expected[/]")
        raise typer.Exit(1)

    result_mask = rx_bytes[-prodtest.IO_SELF_TEST_MASK_LEN :]
    pins_hex = prodtest.mask_to_hex(mask_bytes)
    result_hex = prodtest.mask_to_hex(result_mask)
    failures = prodtest.failed_pins(mask_bytes, result_mask)

    console.print(f"PINS TO TEST BASE16 ENCODED: {pins_hex}")
    console.print(f"RESULT OF TEST BASE16 ENCODED: {result_hex}")
    console.print(_format_failed_pins_line(failures))


@app.command("spi-cfg")
def spi_cfg_command(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
    hz: Optional[int] = typer.Option(
        None,
        "--hz",
        help="SPI clock frequency in Hz",
        min=1,
    ),
    setup_us: Optional[int] = typer.Option(
        None,
        "--setup-us",
        help="Delay after asserting CS, in microseconds",
        min=0,
    ),
    cs_active: Optional[str] = typer.Option(
        None,
        "--cs-active",
        help="CS polarity (low/high)",
    ),
    bit_order: Optional[str] = typer.Option(
        None,
        "--bit-order",
        help="Bit order (msb/lsb)",
    ),
    byte_order: Optional[str] = typer.Option(
        None,
        "--byte-order",
        help="Byte order (big/little)",
    ),
    clock_polarity: Optional[str] = typer.Option(
        None,
        "--clock-polarity",
        help="Clock polarity (idle_low/idle_high)",
    ),
    clock_phase: Optional[str] = typer.Option(
        None,
        "--clock-phase",
        help="Clock phase (leading/trailing)",
    ),
):
    """Query or update the devboard SPI defaults."""

    resources = _ctx_resources(ctx)
    spi_payload: Dict[str, Any] = {}

    str_fields = {
        "cs_active": cs_active,
        "bit_order": bit_order,
        "byte_order": byte_order,
        "clock_polarity": clock_polarity,
        "clock_phase": clock_phase,
    }
    for name, raw_value in str_fields.items():
        normalized = _normalize_choice(raw_value, name=name)
        if normalized is not None:
            spi_payload[name] = normalized

    for name, numeric_value in (("hz", hz), ("setup_us", setup_us)):
        if numeric_value is not None:
            spi_payload[name] = numeric_value

    resolved_port = _require_port(port)
    action = "Updating" if spi_payload else "Querying"
    with spinner(f"{action} spi.cfg over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.spi_cfg(spi=spi_payload if spi_payload else None)
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc

    _render_payload_response("spi.cfg", response)


@app.command("spi-enable")
def spi_enable_command(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Enable SPI on the devboard using the persisted configuration."""

    resources = _ctx_resources(ctx)
    resolved_port = _require_port(port)
    with spinner(f"Enabling SPI over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                port=resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.spi_enable()
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc
    _render_payload_response("spi.enable", response)


@app.command("spi-disable")
def spi_disable_command(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Disable SPI on the devboard and tri-state SPI pins."""

    resources = _ctx_resources(ctx)
    resolved_port = _require_port(port)
    with spinner(f"Disabling SPI over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                port=resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.spi_disable()
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc
    _render_payload_response("spi.disable", response)


@app.command("uart-cfg")
def uart_cfg_command(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
    cfg_baudrate: Optional[int] = typer.Option(
        None,
        "--baudrate",
        help="UART baudrate in Hz",
        min=1200,
        max=4_000_000,
    ),
    stopbits: Optional[int] = typer.Option(
        None,
        "--stopbits",
        help="Stop bits (1 or 2)",
        min=1,
        max=2,
    ),
    parity: Optional[str] = typer.Option(
        None,
        "--parity",
        help="Parity (n/none, e/even, o/odd)",
    ),
):
    """Query or update the devboard UART defaults."""

    resources = _ctx_resources(ctx)
    uart_payload: Dict[str, Any] = {}
    normalized_parity = _normalize_uart_parity(parity)
    if normalized_parity is not None:
        uart_payload["parity"] = normalized_parity

    if stopbits is not None:
        uart_payload["stopbits"] = stopbits

    if cfg_baudrate is not None:
        uart_payload["baudrate"] = cfg_baudrate

    resolved_port = _require_port(port)
    action = "Updating" if uart_payload else "Querying"
    with spinner(f"{action} uart.cfg over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.uart_cfg(uart=uart_payload if uart_payload else None)
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc

    _render_payload_response("uart.cfg", response)


@app.command("uart-tx")
def uart_tx_command(
    ctx: typer.Context,
    data: Optional[str] = typer.Argument(
        None,
        metavar="[HEX|'-']",
        help="Hex payload to send; pass '-' to read raw bytes from stdin",
        show_default=False,
    ),
    text: Optional[str] = typer.Option(
        None,
        "--text",
        help="Literal text payload to encode using --encoding",
        show_default=False,
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Read raw bytes from FILE instead of specifying HEX on the command line",
        show_default=False,
    ),
    newline: bool = typer.Option(
        False,
        "--newline",
        help="Append a newline when using --text/--file/stdin payloads",
        show_default=False,
    ),
    encoding: str = typer.Option(
        "utf-8",
        "--encoding",
        help="Text encoding for --text payloads",
    ),
    uart_port: Optional[int] = typer.Option(
        None,
        "--uart-port",
        min=0,
        help="Target device UART index (defaults to firmware's primary UART)",
    ),
    port: Optional[str] = typer.Option(
        None,
        "--port",
        envvar="SHUTTLE_PORT",
        help="Serial port (e.g., /dev/ttyUSB0)",
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Send raw UART bytes using the uart.tx protocol command."""

    resources = _ctx_resources(ctx)
    payload_hex, payload_len = _resolve_uart_payload(
        data_arg=data,
        text_payload=text,
        file_path=file,
        encoding=encoding,
        append_newline=newline,
    )
    resolved_port = _require_port(port)
    byte_label = "byte" if payload_len == 1 else "bytes"
    with spinner(f"Sending {payload_len} UART {byte_label} over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.uart_tx(payload_hex, port=uart_port)
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc

    _render_payload_response("uart.tx", response)


@app.command("get-info")
def get_info(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None, "--port", envvar="SHUTTLE_PORT", help="Serial port (e.g., /dev/ttyUSB0)"
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Fetch device capabilities using the get.info command."""

    resources = _ctx_resources(ctx)
    resolved_port = _require_port(port)
    with spinner(f"Querying get.info over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.get_info()
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc
    _render_info_response(response)


@app.command("ping")
def ping(
    ctx: typer.Context,
    port: Optional[str] = typer.Option(
        None, "--port", envvar="SHUTTLE_PORT", help="Serial port (e.g., /dev/ttyUSB0)"
    ),
    baudrate: int = typer.Option(DEFAULT_BAUD, "--baud", help="Serial baud rate"),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT, "--timeout", help="Read timeout in seconds"
    ),
):
    """Send a ping command to get firmware/protocol metadata."""

    resources = _ctx_resources(ctx)
    resolved_port = _require_port(port)
    with spinner(f"Pinging device over {resolved_port}"):
        try:
            with NDJSONSerialClient(
                resolved_port,
                baudrate=baudrate,
                timeout=timeout,
                logger=resources.get("logger"),
                seq_tracker=resources.get("seq_tracker"),
            ) as client:
                response = client.ping()
        except ShuttleSerialError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc
    _render_ping_response(response)


if __name__ == "__main__":
    app()
