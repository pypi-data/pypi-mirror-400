# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Markdown parser for validoc."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import yaml

from .constants import BlockType
from .models import Block, Tutorial, TutorialMetadata

if TYPE_CHECKING:
    from pathlib import Path


class MarkdownParser:
    """Parse markdown files with annotated code blocks."""

    # Match fenced code blocks with optional info string
    FENCE_PATTERN = re.compile(
        r"^(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)\n"
        r"(?P<content>.*?)"
        r"^(?P=fence)\s*$",
        re.MULTILINE | re.DOTALL,
    )

    # Match YAML frontmatter
    FRONTMATTER_PATTERN = re.compile(
        r"^---\s*\n(?P<yaml>.*?)\n---\s*\n",
        re.DOTALL,
    )

    # Match markdown headers
    HEADER_PATTERN = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+)$", re.MULTILINE)

    def parse(self, path: Path) -> Tutorial:
        """Parse a markdown file into a Tutorial."""
        content = path.read_text()

        # Extract frontmatter
        metadata = self._parse_frontmatter(content)

        # Remove frontmatter from content for block parsing
        content_without_frontmatter = self.FRONTMATTER_PATTERN.sub("", content)

        # Parse blocks
        blocks = self._parse_blocks(content_without_frontmatter)

        return Tutorial(path=path, metadata=metadata, blocks=blocks)

    def _parse_frontmatter(self, content: str) -> TutorialMetadata:
        """Extract tutorial metadata from YAML frontmatter."""
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            return TutorialMetadata()

        yaml_content = match.group("yaml")

        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            msg = f"Invalid YAML in frontmatter: {e}"
            raise ValueError(msg) from None

        if data and "tutorial" in data:
            t = data["tutorial"]
            return TutorialMetadata(
                name=t.get("name", "unnamed"),
                workdir=t.get("workdir"),
                env=t.get("env", {}),
                setup=t.get("setup", []),
                teardown=t.get("teardown", []),
            )

        return TutorialMetadata()

    def _parse_blocks(self, content: str) -> list[Block]:
        """Extract all annotated blocks from content."""
        blocks = []

        # Track line numbers
        lines = content.split("\n")
        char_to_line: dict[int, int] = {}
        char_pos = 0
        for line_num, line in enumerate(lines, 1):
            char_to_line[char_pos] = line_num
            char_pos += len(line) + 1  # +1 for newline

        # Find current section for each position
        section_positions = [
            (match.start(), match.group("title").strip())
            for match in self.HEADER_PATTERN.finditer(content)
        ]

        def get_section(pos: int) -> str | None:
            section = None
            for sec_pos, sec_title in section_positions:
                if sec_pos <= pos:
                    section = sec_title
                else:
                    break
            return section

        # Parse code blocks
        for match in self.FENCE_PATTERN.finditer(content):
            info = match.group("info").strip()
            content_text = match.group("content")
            start_pos = match.start()

            # Find line number
            line_num = 1
            for pos, ln in char_to_line.items():
                if pos <= start_pos:
                    line_num = ln
                else:
                    break

            # Get current section
            current_section = get_section(start_pos)

            # Parse info string
            block = self._parse_info_string(
                info, content_text, line_num, current_section
            )
            if block:
                blocks.append(block)

        return blocks

    def _parse_info_string(
        self,
        info: str,
        content: str,
        line_number: int,
        section: str | None,
    ) -> Block | None:
        """Parse the info string to determine block type and attributes."""
        if not info:
            return None

        parts = info.split()
        if not parts:
            return None

        language = parts[0]
        attributes = self._parse_attributes(language, parts[1:])
        block_type = self._determine_block_type(language, attributes)

        if block_type is None:
            return None

        return Block(
            type=block_type,
            content=content.strip(),
            attributes=attributes,
            line_number=line_number,
            section=section,
        )

    def _parse_attributes(
        self, language: str, parts: list[str]
    ) -> dict[str, str | bool]:
        """Parse key=value pairs and flags from info string parts."""
        attributes: dict[str, str | bool] = {"language": language}
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                attributes[key] = value
            else:
                attributes[part] = True
        return attributes

    def _determine_block_type(
        self, language: str, attributes: dict[str, str | bool]
    ) -> BlockType | None:
        """Determine the block type from language and attributes."""
        match language:
            case "bash" | "sh" | "shell" | "zsh" if "exec" in attributes:
                return BlockType.EXEC
            case "file":
                return BlockType.FILE
            case "output":
                return BlockType.OUTPUT
            case "assert":
                return BlockType.ASSERT
            case "include":
                return BlockType.INCLUDE
            case _:
                return None
