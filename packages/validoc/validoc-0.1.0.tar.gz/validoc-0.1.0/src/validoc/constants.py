# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Constants and enums for validoc."""

from __future__ import annotations

from enum import Enum, auto


class BlockType(Enum):
    """Types of executable blocks in a tutorial."""

    EXEC = auto()
    FILE = auto()
    OUTPUT = auto()
    ASSERT = auto()
    INCLUDE = auto()


class OutputMode(Enum):
    """Matching modes for output verification."""

    EXACT = auto()
    CONTAINS = auto()
    REGEX = auto()
    LINES = auto()
