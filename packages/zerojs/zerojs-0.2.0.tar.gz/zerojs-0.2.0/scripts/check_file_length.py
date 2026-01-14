#!/usr/bin/env python3
"""Check that files don't exceed maximum line count."""

import sys

MAX_LINES = 1000


def main() -> int:
    """Check file lengths and return exit code."""
    failed = False

    for filepath in sys.argv[1:]:
        with open(filepath) as f:
            lines = sum(1 for _ in f)

        if lines > MAX_LINES:
            print(f"{filepath} has {lines} lines (max {MAX_LINES})")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
