#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Helpers for TiMo SPI command sequences."""
from __future__ import annotations
from typing import Any, Dict, Sequence

NOP_OPCODE = 0xFF
READ_REG_BASE = 0b00000000
READ_REG_ADDR_MASK = 0x3F
READ_REG_MAX_LEN = 32
READ_REG_DUMMY = 0xFF
WRITE_REG_BASE = 0b01000000  # 0x40, 01AAAAAA
WRITE_REG_ADDR_MASK = 0x3F
DMX_READ_CMD = 0x81  # 1000 0001: Read latest received DMX values
DMX_READ_MAX_LEN = 512  # Arbitrary, adjust as needed for DMX universe
READ_ASC_CMD = 0x82  # 1000 0010: Read latest ASC frame
READ_RDM_CMD = 0x83  # 1000 0011: Read received RDM request
WRITE_DMX_CMD = 0x91  # 1001 0001: Write DMX generation buffer
WRITE_RDM_CMD = 0x92  # 1001 0010: Write an RDM response

IRQ_FLAG_RESTART = 0x80  # Bit 7 signals the slave could not process the transfer
IRQ_WAIT_TIMEOUT_US = 1_000  # 1 millisecond

# Selected register map and field descriptions from TiMo SPI interface docs
REGISTER_MAP: Dict[str, Dict[str, Any]] = {
    "CONFIG": {
        "address": 0x00,
        "length": 1,
        "fields": {
            "UART_EN": {
                "bits": (0, 0),
                "access": "R/W",
                "reset": 1,
                "desc": "Enable UART DMX output",
            },
            "RADIO_TX_RX_MODE": {"bits": (1, 1), "access": "R/W", "desc": "0=RX, 1=TX"},
            "SPI_RDM": {
                "bits": (3, 3),
                "access": "R/W",
                "desc": "0=UART RDM, 1=SPI RDM",
            },
            "RADIO_ENABLE": {
                "bits": (7, 7),
                "access": "R/W",
                "reset": 1,
                "desc": "Enable wireless",
            },
        },
    },
    "STATUS": {
        "address": 0x01,
        "length": 1,
        "fields": {
            "LINKED": {
                "bits": (0, 0),
                "access": "R/W",
                "desc": "1=linked (write 1 to unlink)",
            },
            "RF_LINK": {
                "bits": (1, 1),
                "access": "R/W",
                "reset": 0,
                "desc": "Radio link active",
            },
            "IDENTIFY": {
                "bits": (2, 2),
                "access": "R/W",
                "reset": 0,
                "desc": "RDM identify active",
            },
            "DMX": {"bits": (3, 3), "access": "R", "reset": 0, "desc": "DMX available"},
            "UPDATE_MODE": {
                "bits": (7, 7),
                "access": "R",
                "reset": 0,
                "desc": "1=driver update mode",
            },
        },
    },
    "IRQ_MASK": {
        "address": 0x02,
        "length": 1,
        "fields": {
            "RX_DMX_IRQ_EN": {"bits": (0, 0), "access": "R/W", "reset": 0},
            "LOST_DMX_IRQ_EN": {"bits": (1, 1), "access": "R/W", "reset": 0},
            "DMX_CHANGED_IRQ_EN": {"bits": (2, 2), "access": "R/W", "reset": 0},
            "RF_LINK_IRQ_EN": {"bits": (3, 3), "access": "R/W", "reset": 0},
            "ASC_IRQ_EN": {"bits": (4, 4), "access": "R/W", "reset": 0},
            "IDENTIFY_IRQ_EN": {"bits": (5, 5), "access": "R/W", "reset": 0},
            "EXTENDED_IRQ_EN": {"bits": (6, 6), "access": "R/W", "reset": 0},
        },
    },
    "IRQ_FLAGS": {
        "address": 0x03,
        "length": 1,
        "fields": {
            "RX_DMX_IRQ": {"bits": (0, 0), "access": "R", "reset": 0},
            "LOST_DMX_IRQ": {"bits": (1, 1), "access": "R", "reset": 0},
            "DMX_CHANGED_IRQ": {"bits": (2, 2), "access": "R", "reset": 0},
            "RF_LINK_IRQ": {"bits": (3, 3), "access": "R", "reset": 0},
            "ASC_IRQ": {"bits": (4, 4), "access": "R", "reset": 0},
            "IDENTIFY_IRQ": {"bits": (5, 5), "access": "R", "reset": 0},
            "EXTENDED_IRQ": {"bits": (6, 6), "access": "R", "reset": 0},
            "SPI_DEVICE_BUSY": {"bits": (7, 7), "access": "R", "reset": 0},
        },
    },
    "DMX_WINDOW": {
        "address": 0x04,
        "length": 4,
        "fields": {
            "WINDOW_SIZE": {"bits": (0, 15), "access": "R/W", "reset": 512},
            "START_ADDRESS": {"bits": (16, 31), "access": "R/W", "reset": 0},
        },
    },
    "ASC_FRAME": {
        "address": 0x05,
        "length": 3,
        "fields": {
            "START_CODE": {"bits": (0, 7), "access": "R", "reset": 0},
            "ASC_FRAME_LENGTH": {"bits": (8, 23), "access": "R", "reset": 0},
        },
    },
    "LINK_QUALITY": {
        "address": 0x06,
        "length": 1,
        "fields": {
            "PDR": {"bits": (0, 7), "access": "R", "desc": "0=0%, 255=100%"},
        },
    },
    "ANTENNA": {
        "address": 0x07,
        "length": 1,
        "fields": {
            "ANT_SEL": {
                "bits": (0, 0),
                "access": "R/W",
                "reset": 0,
                "desc": "0=on-board,1=IPEX",
            },
        },
    },
    "DMX_SPEC": {
        "address": 0x08,
        "length": 8,
        "fields": {
            "N_CHANNELS": {"bits": (0, 15), "access": "R/W", "reset": 512},
            "INTERSLOT_TIME": {"bits": (16, 31), "access": "R/W", "reset": 0},
            "REFRESH_PERIOD": {"bits": (32, 63), "access": "R/W", "reset": 25000},
        },
    },
    "DMX_CONTROL": {
        "address": 0x09,
        "length": 1,
        "fields": {
            "ENABLE": {"bits": (0, 0), "access": "R/W", "reset": 0},
        },
    },
    "EXTENDED_IRQ_MASK": {
        "address": 0x0A,
        "length": 4,
        "fields": {
            "RDM_REQUEST_EN": {"bits": (0, 0), "access": "R"},
            "UNIV_META_CHANGED_EN": {"bits": (6, 6), "access": "R/W", "reset": 0},
        },
    },
    "EXTENDED_IRQ_FLAGS": {
        "address": 0x0B,
        "length": 4,
        "fields": {
            "RDM_REQUEST": {"bits": (0, 0), "access": "R"},
            "UNIV_META_CHANGED": {"bits": (6, 6), "access": "R/W", "reset": 0},
        },
    },
    "RF_PROTOCOL": {
        "address": 0x0C,
        "length": 1,
        "fields": {
            "TX_PROTOCOL": {
                "bits": (0, 7),
                "access": "R/W",
                "desc": "0=CRMX,1=G3,3=G4S",
            },
        },
    },
    "VERSION": {
        "address": 0x10,
        "length": 8,
        "fields": {
            "FW_VERSION": {"bits": (0, 31), "access": "R"},
            "HW_VERSION": {"bits": (32, 63), "access": "R"},
        },
    },
    "RF_POWER": {
        "address": 0x11,
        "length": 1,
        "fields": {
            "OUTPUT_POWER": {"bits": (0, 7), "access": "R/W", "reset": 3},
        },
    },
    "BLOCKED_CHANNELS": {
        "address": 0x12,
        "length": 11,
        "fields": {
            "FLAGS": {"bits": (0, 87), "access": "R/W", "reset": 0},
        },
    },
    "BINDING_UID": {
        "address": 0x20,
        "length": 6,
        "fields": {
            "UID": {"bits": (0, 47), "access": "R/W", "reset": 0},
        },
    },
    "LINKING_KEY": {
        "address": 0x21,
        "length": 10,
        "fields": {
            "CODE": {"bits": (0, 63), "access": "W"},
            "MODE": {"bits": (64, 71), "access": "W"},
            "UNIVERSE": {"bits": (72, 79), "access": "W"},
        },
    },
    "UNIVERSE_COLOR": {
        "address": 0x33,
        "length": 3,
        "fields": {
            "RGB_VALUE": {"bits": (0, 23), "access": "R/W"},
        },
    },
    "DEVICE_NAME": {
        "address": 0x36,
        "length": 16,
        "fields": {
            "DEVICE_NAME": {"bits": (0, 128), "access": "R/W"},
        },
    },
    "UNIVERSE_NAME": {
        "address": 0x37,
        "length": 16,
        "fields": {
            "UNIVERSE_NAME": {"bits": (0, 128), "access": "R/W"},
        },
    },
    "PRODUCT_ID": {
        "address": 0x3F,
        "length": 4,
        "fields": {
            "PRODUCT_ID": {
                "bits": (0, 32),
                "access": "R",
                "desc": "TiMo product ID 0xF1,0x32,0x00,0x00",
            },
        },
    },
}


def slice_bits(data: bytes, lo: int, hi: int) -> int:
    # inclusive bit range, big-endian bytes
    bit_len = hi - lo + 1
    full = int.from_bytes(data, "big")
    shift = len(data) * 8 - hi - 1
    return (full >> shift) & ((1 << bit_len) - 1)


def command_payload(
    tx: bytes, *, n: int | None = None, params: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Build an NDJSON-friendly spi.xfer payload from raw bytes."""

    payload: Dict[str, Any] = {"tx": tx.hex(), "n": n if n is not None else len(tx)}
    if params:
        payload.update(params)
    return payload


class ReadDMXResult:
    def __init__(
        self, length: int, data: bytes, irq_flags_command: int, irq_flags_payload: int
    ):
        self.length = length
        self.data = data
        self.irq_flags_command = irq_flags_command
        self.irq_flags_payload = irq_flags_payload


def read_dmx_sequence(length: int) -> Sequence[Dict[str, Any]]:
    """Build the SPI transfer sequence to read DMX values from TiMo."""
    if not 1 <= length <= DMX_READ_MAX_LEN:
        raise ValueError(f"length must be 1..{DMX_READ_MAX_LEN}")
    command_transfer = command_payload(
        bytes([DMX_READ_CMD]),
        params={"wait_irq": {"edge": "trailing", "timeout_us": IRQ_WAIT_TIMEOUT_US}},
    )
    payload_transfer = command_payload(bytes([READ_REG_DUMMY] + [0x00] * (length)))
    return [command_transfer, payload_transfer]


def parse_read_dmx_response(length: int, rx_frames: Sequence[str]) -> ReadDMXResult:
    """Parse the RX frames returned from a read-dmx sequence."""
    if len(rx_frames) != 2:
        raise ValueError("read-dmx expects exactly two RX frames")
    cmd_frame = bytes.fromhex(rx_frames[0]) if rx_frames[0] else b""
    payload_frame = bytes.fromhex(rx_frames[1]) if rx_frames[1] else b""
    if len(cmd_frame) != 1:
        raise ValueError("Command frame must contain exactly one byte")
    if len(payload_frame) < length + 1:
        raise ValueError("Payload frame shorter than expected")
    irq_cmd = cmd_frame[0]
    irq_payload = payload_frame[0]
    data = payload_frame[1 : 1 + length]
    return ReadDMXResult(
        length=length,
        data=data,
        irq_flags_command=irq_cmd,
        irq_flags_payload=irq_payload,
    )


class WriteRegisterResult:
    def __init__(
        self, address: int, data: bytes, irq_flags_command: int, irq_flags_payload: int
    ):
        self.address = address
        self.data = data
        self.irq_flags_command = irq_flags_command
        self.irq_flags_payload = irq_flags_payload


def write_reg_sequence(address: int, data: bytes) -> Sequence[Dict[str, Any]]:
    """Build the SPI transfer sequence to write a TiMo register."""
    if not 0 <= address <= WRITE_REG_ADDR_MASK:
        raise ValueError("Register address must be in range 0-63")
    if not 1 <= len(data) <= READ_REG_MAX_LEN:
        raise ValueError(f"data length must be 1..{READ_REG_MAX_LEN}")
    command_byte = WRITE_REG_BASE | (address & WRITE_REG_ADDR_MASK)
    command_transfer = command_payload(
        bytes([command_byte]),
        params={"wait_irq": {"edge": "trailing", "timeout_us": IRQ_WAIT_TIMEOUT_US}},
    )
    payload_transfer = command_payload(bytes([READ_REG_DUMMY]) + data)
    return [command_transfer, payload_transfer]


def parse_write_reg_response(
    address: int, data: bytes, rx_frames: Sequence[str]
) -> WriteRegisterResult:
    """Parse the RX frames returned from a write-register sequence."""
    if len(rx_frames) != 2:
        raise ValueError("write-reg expects exactly two RX frames")
    cmd_frame = bytes.fromhex(rx_frames[0]) if rx_frames[0] else b""
    payload_frame = bytes.fromhex(rx_frames[1]) if rx_frames[1] else b""
    if len(cmd_frame) != 1:
        raise ValueError("Command frame must contain exactly one byte")
    if len(payload_frame) < 1:
        raise ValueError("Payload frame shorter than expected")
    irq_cmd = cmd_frame[0]
    irq_payload = payload_frame[0]
    return WriteRegisterResult(
        address=address,
        data=data,
        irq_flags_command=irq_cmd,
        irq_flags_payload=irq_payload,
    )


def read_asc_sequence(length: int) -> Sequence[Dict[str, Any]]:
    """Build the SPI transfer sequence to read an ASC frame."""

    if not 1 <= length <= DMX_READ_MAX_LEN:
        raise ValueError(f"length must be 1..{DMX_READ_MAX_LEN}")
    command_transfer = command_payload(
        bytes([READ_ASC_CMD]),
        params={"wait_irq": {"edge": "trailing", "timeout_us": IRQ_WAIT_TIMEOUT_US}},
    )
    payload_transfer = command_payload(bytes([READ_REG_DUMMY] + [0x00] * length))
    return [command_transfer, payload_transfer]


def read_rdm_sequence(length: int) -> Sequence[Dict[str, Any]]:
    """Build the SPI transfer sequence to read an RDM request frame."""

    if not 1 <= length <= DMX_READ_MAX_LEN:
        raise ValueError(f"length must be 1..{DMX_READ_MAX_LEN}")
    command_transfer = command_payload(
        bytes([READ_RDM_CMD]),
        params={"wait_irq": {"edge": "trailing", "timeout_us": IRQ_WAIT_TIMEOUT_US}},
    )
    payload_transfer = command_payload(bytes([READ_REG_DUMMY] + [0x00] * length))
    return [command_transfer, payload_transfer]


def write_dmx_command(payload: bytes) -> Dict[str, Any]:
    """Build a single-frame command to write DMX data."""

    return command_payload(bytes([WRITE_DMX_CMD]) + payload)


def write_rdm_command(payload: bytes) -> Dict[str, Any]:
    """Build a single-frame command to write an RDM response."""

    return command_payload(bytes([WRITE_RDM_CMD]) + payload)


def nop_frame() -> bytes:
    """Return the raw bytes that implement the TiMo NOP SPI transfer."""

    return bytes([NOP_OPCODE])


def nop_frame_hex() -> str:
    """Return the compact hexadecimal string for the TiMo NOP SPI transfer."""

    return nop_frame().hex()


def nop_sequence() -> Sequence[Dict[str, Any]]:
    """Sequence describing the TiMo NOP command (single transfer)."""

    return [command_payload(nop_frame())]


def read_reg_sequence(address: int, length: int) -> Sequence[Dict[str, Any]]:
    """Build the SPI transfer sequence to read a TiMo register."""

    if not 0 <= address <= READ_REG_ADDR_MASK:
        raise ValueError("Register address must be in range 0-63")
    if not 1 <= length <= READ_REG_MAX_LEN:
        raise ValueError(f"length must be 1..{READ_REG_MAX_LEN}")

    command_byte = READ_REG_BASE | (address & READ_REG_ADDR_MASK)
    # Wait for IRQ trailing edge (high-to-low) after command phase
    command_transfer = command_payload(
        bytes([command_byte]),
        params={"wait_irq": {"edge": "trailing", "timeout_us": IRQ_WAIT_TIMEOUT_US}},
    )
    payload_transfer = command_payload(bytes([READ_REG_DUMMY] + [0x00] * length))
    return [command_transfer, payload_transfer]


class ReadRegisterResult:
    def __init__(
        self,
        address: int,
        length: int,
        data: bytes,
        irq_flags_command: int,
        irq_flags_payload: int,
    ):
        self.address = address
        self.length = length
        self.data = data
        self.irq_flags_command = irq_flags_command
        self.irq_flags_payload = irq_flags_payload


def parse_read_reg_response(
    address: int,
    length: int,
    rx_frames: Sequence[str],
) -> ReadRegisterResult:
    """Parse the RX frames returned from a read-register sequence."""

    if len(rx_frames) != 2:
        raise ValueError("read-reg expects exactly two RX frames")

    cmd_frame = bytes.fromhex(rx_frames[0]) if rx_frames[0] else b""
    payload_frame = bytes.fromhex(rx_frames[1]) if rx_frames[1] else b""

    if len(cmd_frame) != 1:
        raise ValueError("Command frame must contain exactly one byte")
    if len(payload_frame) < length + 1:
        raise ValueError("Payload frame shorter than expected")

    irq_cmd = cmd_frame[0]
    irq_payload = payload_frame[0]
    data = payload_frame[1 : 1 + length]
    return ReadRegisterResult(
        address=address,
        length=length,
        data=data,
        irq_flags_command=irq_cmd,
        irq_flags_payload=irq_payload,
    )


def format_bytes(data: bytes) -> str:
    """Pretty hex representation grouped in bytes."""

    if not data:
        return "—"
    hex_pairs = [data[i : i + 1].hex() for i in range(len(data))]
    return " ".join(hex_pairs)


def requires_restart(irq_flags: int) -> bool:
    """Return True when bit 7 indicates the command must be retried."""

    return bool(irq_flags & IRQ_FLAG_RESTART)
