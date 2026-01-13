# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Data structures for validoc."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from .constants import BlockType


@dataclass
class Block:
    """A single executable block from the tutorial."""

    type: BlockType
    content: str
    attributes: dict[str, Any]
    line_number: int
    section: str | None = None

    @property
    def id(self) -> str:
        """Return block ID or auto-generate from line number."""
        return self.attributes.get("id", f"block-{self.line_number}")

    @property
    def language(self) -> str:
        """Return the language of the block."""
        return self.attributes.get("language", "bash")


@dataclass
class TutorialMetadata:
    """Tutorial configuration from YAML frontmatter."""

    name: str = "unnamed"
    workdir: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    setup: list[str] = field(default_factory=list)
    teardown: list[str] = field(default_factory=list)


@dataclass
class Tutorial:
    """A parsed tutorial document."""

    path: Path
    metadata: TutorialMetadata
    blocks: list[Block]


@dataclass
class BlockResult:
    """Result of executing a block."""

    block: Block
    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    error: str | None = None
