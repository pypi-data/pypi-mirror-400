#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for the prodtest SPI command protocol."""

from __future__ import annotations

from typing import Iterable, Sequence

from . import timo

RESET_OPCODE = ord("?")
PLUS_OPCODE = ord("+")
IO_SELF_TEST_OPCODE = ord("T")
IO_SELF_TEST_MASK_LEN = 8
IO_SELF_TEST_DUMMY_BYTE = 0xFF
IO_SELF_TEST_IRQ_TIMEOUT_US = 1_000_000


def _ensure_byte(value: int) -> int:
    if not 0 <= value <= 0xFF:
        raise ValueError("Prodtest arguments must be in range 0..255")
    return value


def _build_command_bytes(opcode: int, arguments: Iterable[int] | bytes = ()) -> bytes:
    """Build raw bytes from an opcode and a sequence of byte arguments."""

    if isinstance(arguments, bytes):
        payload = arguments
    else:
        payload = bytes(_ensure_byte(arg) for arg in arguments)
    return bytes([opcode]) + payload


def command(opcode: int, arguments: Iterable[int] | bytes = ()) -> dict:
    """Build an NDJSON-ready spi.xfer payload for a prodtest command."""

    return timo.command_payload(_build_command_bytes(opcode, arguments))


def reset() -> dict:
    """Return the prodtest reset command (single '?' byte)."""

    return command(RESET_OPCODE)


def reset_transfer() -> dict:
    """Reset command packaged as an NDJSON-ready payload."""

    return reset()


def ping_sequence() -> Sequence[dict]:
    """Return the two SPI frames for the prodtest ping action ('+' then dummy)."""
    # First transfer: send '+' (PLUS_OPCODE), expect response (should be ignored)
    # Second transfer: send dummy (0xFF), expect '-' (0x2D) back
    return [
        timo.command_payload(bytes([PLUS_OPCODE])),
        timo.command_payload(bytes([0xFF])),
    ]


def io_self_test(mask: bytes) -> Sequence[dict]:
    """Return the two SPI frames required to run the GPIO self-test."""

    if len(mask) != IO_SELF_TEST_MASK_LEN:
        raise ValueError("IO self-test mask must be exactly 8 bytes")
    command = _build_command_bytes(IO_SELF_TEST_OPCODE, mask)
    readback = bytes([IO_SELF_TEST_DUMMY_BYTE] * IO_SELF_TEST_MASK_LEN)
    return (
        timo.command_payload(
            command,
            params={
                "wait_irq": {
                    "edge": "leading",
                    "timeout_us": IO_SELF_TEST_IRQ_TIMEOUT_US,
                }
            },
        ),
        timo.command_payload(readback),
    )


def mask_from_hex(value: str) -> bytes:
    """Parse a hex-encoded mask and ensure it is 8 bytes long."""

    trimmed = value.strip().lower()
    if len(trimmed) != IO_SELF_TEST_MASK_LEN * 2:
        raise ValueError("Mask must be 16 hex characters (8 bytes)")
    try:
        decoded = bytes.fromhex(trimmed)
    except ValueError as exc:
        raise ValueError("Mask must be a valid hex string") from exc
    return decoded


def mask_to_hex(mask: bytes) -> str:
    """Render the mask as an uppercase hex string."""

    return mask.hex().upper()


def pins_from_mask(mask: bytes) -> list[int]:
    """Return the 1-indexed pin numbers enabled in the bitmask."""

    pins: list[int] = []
    for byte_offset, byte_value in enumerate(reversed(mask)):
        for bit in range(8):
            if byte_value & (1 << bit):
                pins.append(byte_offset * 8 + bit + 1)
    return pins


def failed_pins(request_mask: bytes, result_mask: bytes) -> list[int]:
    """Return sorted pin numbers that were requested but did not pass."""

    requested = set(pins_from_mask(request_mask))
    passed = set(pins_from_mask(result_mask))
    failures = sorted(requested - passed)
    return failures
