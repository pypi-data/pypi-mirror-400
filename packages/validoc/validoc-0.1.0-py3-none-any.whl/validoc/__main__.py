# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Abilian SAS <https://abilian.com>
"""Entry point for python -m validoc."""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
