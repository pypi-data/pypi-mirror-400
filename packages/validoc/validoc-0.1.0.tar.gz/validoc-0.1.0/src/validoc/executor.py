# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Block execution for validoc."""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .constants import BlockType
from .models import Block, BlockResult


@dataclass(kw_only=True)
class Session:
    """Execution environment for a tutorial."""

    _init_workdir: Path | None = field(default=None, repr=False)
    _init_env: dict[str, str] | None = field(default=None, repr=False)
    verbose: bool = False

    # Actual state (set in __post_init__)
    workdir: Path = field(init=False)
    original_workdir: Path = field(init=False)
    env: dict[str, str] = field(init=False)
    created_temp: bool = field(init=False)
    last_stdout: str = field(default="", init=False)
    last_stderr: str = field(default="", init=False)
    last_exit_code: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Initialize derived attributes."""
        self.created_temp = self._init_workdir is None
        self.original_workdir = self._init_workdir or Path(
            tempfile.mkdtemp(prefix="validoc-")
        )
        self.workdir = self.original_workdir
        self.env = {**os.environ, **(self._init_env or {})}

    def setup(self, commands: list[str]) -> bool:
        """Run setup commands."""
        for cmd in commands:
            result = self._run_command(cmd, timeout=120)
            if result.exit_code != 0:
                return False
        return True

    def teardown(self, commands: list[str]) -> None:
        """Run teardown commands."""
        for cmd in commands:
            with contextlib.suppress(subprocess.SubprocessError, OSError):
                self._run_command(cmd, timeout=60)

    def cleanup(self) -> None:
        """Clean up the session."""
        if self.created_temp and self.original_workdir.exists():
            shutil.rmtree(self.original_workdir, ignore_errors=True)

    def execute(self, block: Block) -> BlockResult:
        """Execute a block and return the result."""
        start_time = time.time()

        try:
            if block.type == BlockType.EXEC:
                return self._execute_exec(block, start_time)
            if block.type == BlockType.FILE:
                return self._execute_file(block, start_time)
            if block.type == BlockType.OUTPUT:
                return self._execute_output(block, start_time)
            if block.type == BlockType.ASSERT:
                return self._execute_assert(block, start_time)
            return BlockResult(
                block=block,
                success=False,
                error=f"Unknown block type: {block.type}",
                duration=time.time() - start_time,
            )
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            return BlockResult(
                block=block,
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )

    def _execute_exec(self, block: Block, start_time: float) -> BlockResult:
        """Execute a bash command block."""
        if block.attributes.get("skip"):
            return BlockResult(
                block=block,
                success=True,
                duration=time.time() - start_time,
            )

        # Determine working directory
        workdir = self.workdir
        if "dir" in block.attributes:
            workdir = self.original_workdir / block.attributes["dir"]
            workdir.mkdir(parents=True, exist_ok=True)

        # Get timeout
        timeout = int(block.attributes.get("timeout", 30))

        # Get expected exit code
        expected_exit = int(block.attributes.get("expect", 0))

        # Execute
        result = self._run_command(
            block.content,
            workdir=workdir,
            timeout=timeout,
        )

        success = result.exit_code == expected_exit
        error = None
        if not success:
            error = f"Expected exit code {expected_exit}, got {result.exit_code}"

        return BlockResult(
            block=block,
            success=success,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=time.time() - start_time,
            error=error,
        )

    def _execute_file(self, block: Block, start_time: float) -> BlockResult:
        """Create a file from block content."""
        path_str = block.attributes.get("path")
        if not path_str:
            return BlockResult(
                block=block,
                success=False,
                error="File block missing 'path' attribute",
                duration=time.time() - start_time,
            )

        file_path = self.original_workdir / path_str
        file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if block.attributes.get("append") else "w"
        file_path.open(mode).write(block.content + "\n")

        # Set permissions if specified
        if "mode" in block.attributes:
            file_path.chmod(int(block.attributes["mode"], 8))

        return BlockResult(
            block=block,
            success=True,
            duration=time.time() - start_time,
        )

    def _execute_output(self, block: Block, start_time: float) -> BlockResult:
        """Verify output from previous command."""
        expected = block.content
        actual = self.last_stdout

        # Determine matching mode
        attrs = block.attributes

        if attrs.get("exact") or "exact" in attrs.get("language", ""):
            success = actual.strip() == expected.strip()
            mode = "exact"
        elif attrs.get("regex") or "regex" in attrs.get("language", ""):
            success = bool(re.search(expected, actual))
            mode = "regex"
        elif attrs.get("lines"):
            expected_lines = int(attrs["lines"])
            actual_lines = len(actual.strip().split("\n"))
            success = actual_lines == expected_lines
            mode = f"lines={expected_lines}"
        else:  # Default: contains
            success = expected.strip() in actual
            mode = "contains"

        error = None
        if not success:
            error = (
                f"Output mismatch ({mode}):\n"
                f"Expected:\n{expected[:200]}\n"
                f"Got:\n{actual[:200]}"
            )

        return BlockResult(
            block=block,
            success=success,
            stdout=actual,
            duration=time.time() - start_time,
            error=error,
        )

    def _execute_assert(self, block: Block, start_time: float) -> BlockResult:
        """Execute an assertion."""
        content = block.content.strip()
        attrs = block.attributes

        # Parse assertion type from content or attributes
        if content.startswith("file-exists") or attrs.get("file-exists"):
            return self._assert_file_exists(block, start_time)
        if content.startswith("http") or attrs.get("http"):
            return self._assert_http(block, start_time)
        if attrs.get("contains"):
            # Assert last output contains text
            success = attrs["contains"] in self.last_stdout
            return BlockResult(
                block=block,
                success=success,
                duration=time.time() - start_time,
                error=None
                if success
                else f"Output doesn't contain: {attrs['contains']}",
            )
        return BlockResult(
            block=block,
            success=False,
            error=f"Unknown assertion: {content[:50]}",
            duration=time.time() - start_time,
        )

    def _assert_file_exists(self, block: Block, start_time: float) -> BlockResult:
        """Assert a file exists."""
        path_str = block.attributes.get("path")
        if not path_str:
            # Try to parse from content
            match = re.search(r"path=(\S+)", block.content)
            if match:
                path_str = match.group(1)

        if not path_str:
            return BlockResult(
                block=block,
                success=False,
                error="file-exists assertion missing 'path'",
                duration=time.time() - start_time,
            )

        file_path = self.original_workdir / path_str
        success = file_path.exists()

        return BlockResult(
            block=block,
            success=success,
            duration=time.time() - start_time,
            error=None if success else f"File not found: {file_path}",
        )

    def _assert_http(self, block: Block, start_time: float) -> BlockResult:
        """Assert HTTP response."""
        url = block.attributes.get("url")
        expected_status = int(block.attributes.get("status", 200))

        if not url:
            # Try to parse from content
            match = re.search(r"url=(\S+)", block.content)
            if match:
                url = match.group(1)

        if not url:
            return BlockResult(
                block=block,
                success=False,
                error="http assertion missing 'url'",
                duration=time.time() - start_time,
            )

        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as response:
                actual_status = response.status
        except urllib.error.HTTPError as e:
            actual_status = e.code
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return BlockResult(
                block=block,
                success=False,
                error=f"HTTP request failed: {e}",
                duration=time.time() - start_time,
            )

        success = actual_status == expected_status

        return BlockResult(
            block=block,
            success=success,
            duration=time.time() - start_time,
            error=(
                None
                if success
                else f"Expected status {expected_status}, got {actual_status}"
            ),
        )

    def _run_command(
        self,
        command: str,
        workdir: Path | None = None,
        timeout: int = 30,
    ) -> BlockResult:
        """Run a shell command and capture output."""
        workdir = workdir or self.workdir
        workdir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print(f"  $ {command[:80]}{'...' if len(command) > 80 else ''}")

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=workdir,
                env=self.env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            self.last_stdout = proc.stdout
            self.last_stderr = proc.stderr
            self.last_exit_code = proc.returncode

            return BlockResult(
                block=Block(BlockType.EXEC, command, {}, 0),  # Dummy block
                success=proc.returncode == 0,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        except subprocess.TimeoutExpired:
            self.last_stdout = ""
            self.last_stderr = f"Command timed out after {timeout}s"
            self.last_exit_code = -1

            return BlockResult(
                block=Block(BlockType.EXEC, command, {}, 0),
                success=False,
                exit_code=-1,
                stderr=f"Command timed out after {timeout}s",
            )
