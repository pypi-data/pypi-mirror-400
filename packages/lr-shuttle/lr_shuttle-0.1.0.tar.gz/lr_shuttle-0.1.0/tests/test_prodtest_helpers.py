#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from shuttle import prodtest


def test_mask_from_hex_parses_and_formats():
    mask = prodtest.mask_from_hex("0000000000000004")
    assert mask == bytes.fromhex("0000000000000004")
    assert prodtest.mask_to_hex(mask) == "0000000000000004"


def test_mask_from_hex_validations():
    with pytest.raises(ValueError):
        prodtest.mask_from_hex("0000")
    with pytest.raises(ValueError):
        prodtest.mask_from_hex("zzzzzzzzzzzzzzzz")


def test_io_self_test_requires_eight_bytes():
    with pytest.raises(ValueError):
        prodtest.io_self_test(b"\x00")


def test_io_self_test_frames():
    mask = prodtest.mask_from_hex("000000000000000f")
    frames = prodtest.io_self_test(mask)
    assert len(frames) == 2
    assert frames[0]["tx"] == (b"T" + mask).hex()
    assert frames[0]["wait_irq"] == {
        "edge": "leading",
        "timeout_us": prodtest.IO_SELF_TEST_IRQ_TIMEOUT_US,
    }
    assert (
        frames[1]["tx"]
        == bytes(
            [prodtest.IO_SELF_TEST_DUMMY_BYTE] * prodtest.IO_SELF_TEST_MASK_LEN
        ).hex()
    )


def test_pins_from_mask_and_failures():
    requested = prodtest.mask_from_hex("000000000000000F")
    result = prodtest.mask_from_hex("0000000000000005")
    assert prodtest.pins_from_mask(result) == [1, 3]
    assert prodtest.failed_pins(requested, result) == [2, 4]


def test_command_builder_and_limits():
    cmd = prodtest.command(ord("a"), [0x00, 0xFF])
    assert cmd["tx"] == "6100ff"
    assert cmd["n"] == 3
    with pytest.raises(ValueError):
        prodtest.command(ord("a"), [256])
