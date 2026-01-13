# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""CLI entry point for validoc."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from .runner import TutorialRunner

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace

DESCRIPTION = """
validoc - Executable Tutorial Testing

A tool for running tutorials as tests. Parses markdown files
with annotated code blocks and executes them, verifying outputs.

Block annotations:
    ```bash exec                    # Execute this block
    ```bash exec dir=myapp          # Execute in directory
    ```bash exec timeout=60         # Custom timeout
    ```bash exec expect=1           # Expect non-zero exit
    ```bash exec id=step1           # Named block
    ```bash exec skip               # Skip this block
    ```bash exec continue-on-error  # Don't stop on failure

    ```file path=config.yml         # Create a file
    ```output contains              # Verify output contains text
    ```output exact                 # Verify exact output match
    ```output regex                 # Verify output matches regex
    ```assert file-exists path=x    # Assert file exists
    ```assert http url=x status=200 # Assert HTTP response
"""


def main(argv: list[str] | None = None) -> int:
    """Main entry point for validoc CLI.

    Args:
        argv: Command-line arguments. If None, uses sys.argv.

    Returns:
        Exit code (0 for success, non-zero for failure).

    """
    parser = _create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if not args.file.exists():
        print(f"Error: File not found: {args.file}")
        return 1

    runner = _create_runner(args)
    return _execute_command(args, runner)


def _create_parser() -> ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="validoc - Executable Tutorial Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=DESCRIPTION,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a tutorial")
    run_parser.add_argument("file", type=Path, help="Tutorial markdown file")
    run_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    run_parser.add_argument("--no-color", action="store_true", help="Disable colors")
    run_parser.add_argument("--workdir", type=Path, help="Working directory")
    run_parser.add_argument("--section", help="Run only this section")
    run_parser.add_argument(
        "--from", dest="from_checkpoint", help="Start from checkpoint"
    )
    run_parser.add_argument(
        "--no-teardown", action="store_true", help="Skip teardown and keep files"
    )

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Validate a tutorial without running"
    )
    check_parser.add_argument("file", type=Path, help="Tutorial markdown file")

    # List command
    list_parser = subparsers.add_parser("list", help="List blocks in a tutorial")
    list_parser.add_argument("file", type=Path, help="Tutorial markdown file")

    return parser


def _create_runner(args: Namespace) -> TutorialRunner:
    """Create a TutorialRunner from parsed arguments."""
    return TutorialRunner(
        verbose=getattr(args, "verbose", False),
        no_color=getattr(args, "no_color", False),
        workdir=getattr(args, "workdir", None),
        section_filter=getattr(args, "section", None),
        from_checkpoint=getattr(args, "from_checkpoint", None),
        no_teardown=getattr(args, "no_teardown", False),
    )


def _execute_command(args: Namespace, runner: TutorialRunner) -> int:
    """Execute the requested command. Returns exit code."""
    try:
        match args.command:
            case "run":
                return 0 if runner.run(args.file) else 1
            case "check":
                return 0 if runner.check(args.file) else 1
            case "list":
                runner.list_blocks(args.file)
                return 0
            case _:
                return 1
    except ValueError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
