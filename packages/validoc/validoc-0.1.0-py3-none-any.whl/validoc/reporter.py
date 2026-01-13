# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Console reporter for validoc."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .constants import BlockType

if TYPE_CHECKING:
    from .models import Block, BlockResult, Tutorial


@dataclass(kw_only=True)
class ConsoleReporter:
    """Report results to the console with colors."""

    verbose: bool = False
    no_color: bool = False

    # ANSI colors (class-level constants)
    GREEN: str = field(default="\033[92m", init=False, repr=False)
    RED: str = field(default="\033[91m", init=False, repr=False)
    YELLOW: str = field(default="\033[93m", init=False, repr=False)
    BLUE: str = field(default="\033[94m", init=False, repr=False)
    BOLD: str = field(default="\033[1m", init=False, repr=False)
    DIM: str = field(default="\033[2m", init=False, repr=False)
    RESET: str = field(default="\033[0m", init=False, repr=False)
    results: list[BlockResult] = field(default_factory=list, init=False)
    current_section: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Adjust no_color based on terminal detection."""
        self.no_color = self.no_color or not sys.stdout.isatty()

    def _c(self, color: str, text: str) -> str:
        """Colorize text if colors are enabled."""
        if self.no_color:
            return text
        return f"{color}{text}{self.RESET}"

    def start(self, tutorial: Tutorial) -> None:
        """Report tutorial start."""
        print(self._c(self.BOLD, f"\n{'=' * 60}"))
        print(self._c(self.BOLD, f"Tutorial: {tutorial.path.name}"))
        print(self._c(self.BOLD, f"{'=' * 60}\n"))

    def block_start(self, block: Block) -> None:
        """Report block execution start."""
        if block.section != self.current_section:
            self.current_section = block.section
            if block.section:
                print(self._c(self.BLUE, f"\n## {block.section}\n"))

    def block_result(self, result: BlockResult) -> None:
        """Report block execution result."""
        self.results.append(result)

        block = result.block
        status = (
            self._c(self.GREEN, "PASS") if result.success else self._c(self.RED, "FAIL")
        )

        # Format block description
        if block.type == BlockType.EXEC:
            desc = block.content.split("\n")[0][:50]
            desc = f"exec: {desc}{'...' if len(block.content) > 50 else ''}"
        elif block.type == BlockType.FILE:
            desc = f"file: {block.attributes.get('path', '?')}"
        elif block.type == BlockType.OUTPUT:
            desc = "output verification"
        elif block.type == BlockType.ASSERT:
            desc = f"assert: {block.content[:30]}"
        else:
            desc = str(block.type)

        duration = f"{result.duration:.2f}s" if result.duration > 0.01 else ""

        print(f"  [{status}] {desc} {self._c(self.DIM, duration)}")

        if not result.success and result.error:
            print(self._c(self.RED, f"       Error: {result.error}"))

        if self.verbose and result.stdout:
            for line in result.stdout.strip().split("\n")[:5]:
                print(self._c(self.DIM, f"       | {line}"))

    def finish(self) -> bool:
        """Report final summary. Returns True if all tests passed."""
        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed
        total_time = sum(r.duration for r in self.results)

        print(self._c(self.BOLD, f"\n{'=' * 60}"))
        print("Results: ", end="")

        if failed == 0:
            print(self._c(self.GREEN, f"{passed} passed"), end="")
        else:
            print(self._c(self.GREEN, f"{passed} passed"), end="")
            print(", ", end="")
            print(self._c(self.RED, f"{failed} failed"), end="")

        print(f" in {total_time:.2f}s")
        print(self._c(self.BOLD, f"{'=' * 60}\n"))

        return failed == 0
