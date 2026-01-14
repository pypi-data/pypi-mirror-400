#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared constants for Shuttle CLI and library consumers."""

from __future__ import annotations

from typing import Dict, Set


SPI_ALLOWED_FIELDS: Set[str] = {
    "cs_active",
    "setup_us",
    "bit_order",
    "byte_order",
    "clock_polarity",
    "clock_phase",
    "hz",
}


SPI_CHOICE_FIELDS: Dict[str, Set[str]] = {
    "cs_active": {"low", "high"},
    "bit_order": {"msb", "lsb"},
    "byte_order": {"big", "little"},
    "clock_polarity": {"idle_low", "idle_high"},
    "clock_phase": {"leading", "trailing"},
}


UART_PARITY_ALIASES: Dict[str, str] = {
    "n": "n",
    "none": "n",
    "e": "e",
    "even": "e",
    "o": "o",
    "odd": "o",
}


DEFAULT_BAUD = 921600
DEFAULT_TIMEOUT = 2.0
