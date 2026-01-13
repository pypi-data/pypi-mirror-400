"""
Markdown formatter for py-edu-fr with mdformat, mdformat-myst, and jupytext support.
"""

import argparse
import sys

from pathlib import Path

from . import __version__, format_file, collect_markdown_files


def get_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mdformat-py-edu-fr",
        description="Format Markdown files for py-edu-fr project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files or directories to format (if omitted, reads from stdin)",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if files are formatted without modifying them (exit code 1 if changes needed)",
    )

    parser.add_argument(
        "--exclude",
        action="append",
        default=["**/_build/**", "**/.ipynb_checkpoints/**", "**/.venv/**"],
        metavar="PATTERN",
        help="Glob pattern to exclude files/directories (can be specified multiple times)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed information about processing",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Disable printing information",
    )

    return parser


def main() -> int:
    """
    Main entrypoint for the mdformat-py-edu-fr command.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = get_parser()
    args = parser.parse_args()

    # Handle stdin if no paths provided
    if not args.paths:
        print("Error: Reading from stdin not yet implemented", file=sys.stderr)
        return 1

    # Collect all Markdown files
    markdown_files = collect_markdown_files(args.paths, args.exclude)

    if not markdown_files:
        print("No Markdown files found", file=sys.stderr)
        return 1

    if not args.quiet and not all(path.name.endswith(".md") for path in args.paths):
        print(f"Processing {len(markdown_files)} Markdown file(s)")

    # Process each file
    all_formatted = True
    for filepath in markdown_files:
        formatted = format_file(filepath, check=args.check, verbose=args.verbose)
        if not formatted:
            all_formatted = False
            if args.check:
                print(f"Would reformat: {filepath}")

    # Return appropriate exit code
    if args.check and not all_formatted:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
