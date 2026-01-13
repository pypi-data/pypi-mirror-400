import sys
from pathlib import Path
from typing import List

import mdformat

from .format_with_jupytext import format_md_with_jupytext

try:
    from importlib.metadata import version

    __version__ = version("mdformat-py-edu-fr")
except Exception:
    __version__ = "unknown"

from mdformat._conf import DEFAULT_OPTS

options = DEFAULT_OPTS.copy()
options.update({"number": True, "wrap": 89, "end_of_line": "lf"})


def _match_patterns(path: Path, patterns: List[str]) -> bool:
    """
    Check if a path matches any of the given glob patterns.

    Args:
        path: Path to check
        patterns: List of glob patterns

    Returns:
        True if path matches any pattern, False otherwise
    """
    for pattern in patterns:
        if path.match(pattern) or path.full_match(pattern):
            return True
    return False


def collect_markdown_files(
    paths: List[Path], exclude_patterns: List[str] = None
) -> List[Path]:
    """
    Collect all Markdown files from the given paths.

    Args:
        paths: List of file or directory paths
        exclude_patterns: List of glob patterns to exclude

    Returns:
        List of Path objects pointing to Markdown files
    """
    if exclude_patterns is None:
        exclude_patterns = []

    markdown_files = []

    for path in paths:
        if not path.exists():
            print(f"Error: Path does not exist: {path}", file=sys.stderr)
            continue

        if path.is_file():
            if path.suffix in {".md", ".markdown"}:
                # Check if file matches any exclude pattern
                if not _match_patterns(path, exclude_patterns):
                    markdown_files.append(path)
            else:
                print(f"Warning: Skipping non-Markdown file: {path}", file=sys.stderr)
        elif path.is_dir():
            # Recursively find all Markdown files
            for md_file in path.rglob("*.md"):
                if not _match_patterns(md_file, exclude_patterns):
                    markdown_files.append(md_file)
            for md_file in path.rglob("*.markdown"):
                if not _match_patterns(md_file, exclude_patterns):
                    markdown_files.append(md_file)
        else:
            print(f"Warning: Skipping special file: {path}", file=sys.stderr)

    return sorted(set(markdown_files))


def format_file(filepath: Path, check: bool = False, verbose: bool = False) -> bool:
    """
    Format a single Markdown file.

    Args:
        filepath: Path to the file to format
        check: If True, only check formatting without modifying
        verbose: If True, print detailed information

    Returns:
        True if file is properly formatted (or was formatted), False otherwise
    """
    if verbose:
        print(f"Processing: {filepath}")

    original_str = filepath.read_text()

    enabled_parserplugins = mdformat.plugins.PARSER_EXTENSIONS

    try:
        formatted_str = mdformat.text(
            original_str,
            options=options,
            extensions=enabled_parserplugins,
            _filename=str(filepath),
        )
    except Exception as exc:
        print(f"Error: mdformat exception for file {filepath}", file=sys.stderr)
        raise exc

    formatted_str = format_md_with_jupytext(formatted_str, filepath)

    formatted = formatted_str == original_str

    if check or formatted:
        return formatted

    filepath.write_text(formatted_str)
    print(f"{filepath} reformatted")
    return formatted
