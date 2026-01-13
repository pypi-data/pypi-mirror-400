"""
glyphcore CLI

Provides validation tooling for StatusBlock outputs.
"""

import argparse
import sys
from pathlib import Path

from glyphcore.compliance import validate_statusblock


def lint_command(args: argparse.Namespace) -> int:
    """Handle `glyphcore lint`."""
    path = Path(args.file)

    if not path.exists():
        print(f"❌ File not found: {path}")
        return 1

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        print("❌ Empty file")
        return 1

    result = validate_statusblock(
        content,
        terminal_width=args.width,
    )

    if result.passed:
        print("✅ StatusBlock is compliant")
        return 0

    print("❌ StatusBlock compliance violations:")
    for v in result.violations:
        print(f" - {v}")

    return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="glyphcore",
        description="Validate StatusBlock output against glyphcore invariants",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    lint = subparsers.add_parser(
        "lint",
        help="Validate a rendered StatusBlock file",
    )
    lint.add_argument(
        "file",
        help="Path to file containing StatusBlock output",
    )
    lint.add_argument(
        "--width",
        type=int,
        default=80,
        help="Terminal width for density checks (default: 80)",
    )

    lint.set_defaults(func=lint_command)

    args = parser.parse_args()
    exit_code = args.func(args)
    sys.exit(exit_code)


# 🔑 THIS IS WHAT YOU WERE MISSING
if __name__ == "__main__":
    main()
