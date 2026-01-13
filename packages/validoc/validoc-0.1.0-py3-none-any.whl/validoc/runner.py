# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Tutorial runner for validoc."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .constants import BlockType
from .executor import Session
from .parser import MarkdownParser
from .reporter import ConsoleReporter

if TYPE_CHECKING:
    from .models import Block, Tutorial


@dataclass
class TutorialRunner:
    """Main runner that orchestrates parsing, execution, and reporting."""

    verbose: bool = False
    no_color: bool = False
    workdir: Path | None = None
    section_filter: str | None = None
    from_checkpoint: str | None = None
    no_teardown: bool = False

    def run(self, path: Path) -> bool:
        """Run a tutorial and return success status."""
        parser = MarkdownParser()
        tutorial = parser.parse(path)

        reporter = ConsoleReporter(verbose=self.verbose, no_color=self.no_color)
        reporter.start(tutorial)

        session = self._create_session(tutorial)

        try:
            if not self._run_setup(session, tutorial):
                return False
            success = self._execute_blocks(session, tutorial, reporter)
        finally:
            self._run_cleanup(session, tutorial)

        return reporter.finish() and success

    def _create_session(self, tutorial: Tutorial) -> Session:
        """Create execution session with appropriate working directory."""
        workdir = self.workdir
        if workdir is None and tutorial.metadata.workdir:
            workdir = Path(tutorial.metadata.workdir)

        return Session(
            _init_workdir=workdir,
            _init_env=tutorial.metadata.env,
            verbose=self.verbose,
        )

    def _run_setup(self, session: Session, tutorial: Tutorial) -> bool:
        """Run setup commands. Returns False if setup fails."""
        if not tutorial.metadata.setup:
            return True

        print(self._dim("Running setup..."))
        if not session.setup(tutorial.metadata.setup):
            print(self._red("Setup failed!"))
            return False
        return True

    def _execute_blocks(
        self, session: Session, tutorial: Tutorial, reporter: ConsoleReporter
    ) -> bool:
        """Execute tutorial blocks. Returns overall success status."""
        success = True
        checkpoint_reached = self.from_checkpoint is None

        for block in tutorial.blocks:
            if not checkpoint_reached:
                checkpoint_reached = (
                    block.attributes.get("checkpoint") == self.from_checkpoint
                )
                if not checkpoint_reached:
                    continue

            if self.section_filter and block.section != self.section_filter:
                continue

            reporter.block_start(block)
            result = session.execute(block)
            reporter.block_result(result)

            if not result.success:
                success = False
                if not block.attributes.get("continue-on-error"):
                    break

        return success

    def _run_cleanup(self, session: Session, tutorial: Tutorial) -> None:
        """Run teardown and cleanup."""
        if tutorial.metadata.teardown and not self.no_teardown:
            print(self._dim("\nRunning teardown..."))
            session.teardown(tutorial.metadata.teardown)

        if self.no_teardown:
            print(self._dim(f"\nWork directory preserved: {session.workdir}"))
        else:
            session.cleanup()

    def check(self, path: Path) -> bool:
        """Parse and validate a tutorial without executing."""
        parser = MarkdownParser()
        tutorial = parser.parse(path)

        print(f"\nTutorial: {path.name}")
        print(f"  Name: {tutorial.metadata.name}")
        print(f"  Blocks: {len(tutorial.blocks)}")

        exec_blocks = [b for b in tutorial.blocks if b.type == BlockType.EXEC]
        file_blocks = [b for b in tutorial.blocks if b.type == BlockType.FILE]
        output_blocks = [b for b in tutorial.blocks if b.type == BlockType.OUTPUT]
        assert_blocks = [b for b in tutorial.blocks if b.type == BlockType.ASSERT]

        print(f"    - exec: {len(exec_blocks)}")
        print(f"    - file: {len(file_blocks)}")
        print(f"    - output: {len(output_blocks)}")
        print(f"    - assert: {len(assert_blocks)}")

        if tutorial.metadata.setup:
            print(f"  Setup commands: {len(tutorial.metadata.setup)}")
        if tutorial.metadata.teardown:
            print(f"  Teardown commands: {len(tutorial.metadata.teardown)}")

        # Validate blocks
        errors = [
            f"Line {block.line_number}: file block missing 'path'"
            for block in tutorial.blocks
            if block.type == BlockType.FILE and "path" not in block.attributes
        ]

        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  - {error}")
            return False

        print("\nValidation: OK")
        return True

    def list_blocks(self, path: Path) -> None:
        """List all blocks in a tutorial."""
        parser = MarkdownParser()
        tutorial = parser.parse(path)

        print(f"\nBlocks in {path.name}:\n")

        current_section = None
        for i, block in enumerate(tutorial.blocks, 1):
            if block.section != current_section:
                current_section = block.section
                if current_section:
                    print(f"\n## {current_section}\n")

            attr_str = self._format_block_attrs(block)
            description = self._format_block_description(block)
            print(f"  {i}. {description}{attr_str}")

    def _format_block_attrs(self, block: Block) -> str:
        """Format block attributes for display."""
        attrs = []
        if block.attributes.get("id"):
            attrs.append(f"id={block.attributes['id']}")
        if block.attributes.get("dir"):
            attrs.append(f"dir={block.attributes['dir']}")
        if block.attributes.get("skip"):
            attrs.append("skip")
        return f" ({', '.join(attrs)})" if attrs else ""

    def _format_block_description(self, block: Block) -> str:
        """Format block description for list output."""
        match block.type:
            case BlockType.EXEC:
                preview = block.content.split("\n")[0][:40]
                return f"[EXEC] {preview}..."
            case BlockType.FILE:
                return f"[FILE] {block.attributes.get('path', '?')}"
            case BlockType.OUTPUT:
                return "[OUTPUT] verification"
            case BlockType.ASSERT:
                return f"[ASSERT] {block.content[:30]}"
            case _:
                return f"[{block.type.name}]"

    def _dim(self, text: str) -> str:
        if self.no_color:
            return text
        return f"\033[2m{text}\033[0m"

    def _red(self, text: str) -> str:
        if self.no_color:
            return text
        return f"\033[91m{text}\033[0m"
