"""
Tests for mdformat-py-edu-fr formatter.

Test structure:
- tests/examples/unformatted/ - Contains unformatted Markdown files
- tests/examples/formatted/ - Contains the expected formatted output
"""

import pytest
from pathlib import Path
from typing import List

from .conftest import run_formatter

from mdformat_py_edu_fr import format_file

EXAMPLES_DIR = Path(__file__).parent / "examples"
UNFORMATTED_DIR = EXAMPLES_DIR / "unformatted"
FORMATTED_DIR = EXAMPLES_DIR / "formatted"


def get_test_files() -> List[tuple[Path, Path]]:
    """
    Get pairs of (unformatted, formatted) test files.

    Returns:
        List of tuples (unformatted_path, formatted_path)
    """
    if not UNFORMATTED_DIR.exists() or not FORMATTED_DIR.exists():
        return []

    pairs = []
    for unformatted_file in UNFORMATTED_DIR.rglob("*.md"):
        # Get relative path from unformatted dir
        rel_path = unformatted_file.relative_to(UNFORMATTED_DIR)
        formatted_file = FORMATTED_DIR / rel_path

        if formatted_file.exists():
            pairs.append((unformatted_file, formatted_file))
        else:
            pytest.fail(f"Missing formatted version for: {rel_path}")

    return pairs


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""

    def _create_temp_file(file_path: Path) -> tuple[Path, str]:
        content = file_path.read_text(encoding="utf-8")
        temp = tmp_path / file_path.name
        temp.write_text(content, encoding="utf-8")
        return temp, content

    return _create_temp_file


class TestFormatting:
    """Test that unformatted files are correctly formatted."""

    @pytest.mark.parametrize("unformatted,formatted", get_test_files())
    def test_format_matches_expected(
        self, unformatted: Path, formatted: Path, temp_file
    ):
        """Test that formatting produces the expected output."""
        expected_content = formatted.read_text(encoding="utf-8")

        temp, _ = temp_file(unformatted)

        actual_content = format_file(temp)

        # Read the formatted output
        actual_content = temp.read_text(encoding="utf-8")

        # Compare with expected
        assert actual_content == expected_content, (
            f"Formatted output doesn't match expected for {unformatted.name}"
        )


class TestStability:
    """Test that formatting is stable (idempotent)."""

    @pytest.mark.parametrize("unformatted,formatted", get_test_files())
    def test_format_is_stable(self, formatted: Path, temp_file, unformatted: Path):
        """Test that formatting already-formatted files doesn't change them."""
        # Create a temporary file with formatted content
        temp, formatted_content = temp_file(formatted)

        # Run the formatter on already-formatted content
        result = run_formatter(temp)

        assert result.returncode == 0, f"Formatter failed: {result.stderr}"

        # Read the output
        output_content = temp.read_text(encoding="utf-8")

        # Should be identical (stable/idempotent)
        assert output_content == formatted_content, (
            f"Formatter is not stable for {formatted.name}. "
            "Running it twice produces different results."
        )

    @pytest.mark.parametrize("unformatted,formatted", get_test_files())
    def test_double_format_is_stable(
        self, unformatted: Path, temp_file, formatted: Path
    ):
        """Test that formatting twice produces the same result."""
        temp, _ = temp_file(unformatted)

        # Format once
        result1 = run_formatter(temp)
        assert result1.returncode == 0, f"First format failed: {result1.stderr}"

        first_format = temp.read_text(encoding="utf-8")

        # Format again
        result2 = run_formatter(temp)

        assert result2.returncode == 0, f"Second format failed: {result2.stderr}"

        second_format = temp.read_text(encoding="utf-8")

        # Both formats should be identical
        assert first_format == second_format, (
            f"Formatting {unformatted.name} twice produces different results"
        )


class TestCheckMode:
    """Test the --check flag behavior."""

    def test_check_unformatted_fails(self, temp_file):
        """Test that --check returns non-zero for unformatted files."""
        # Get first unformatted file
        test_files = get_test_files()
        if not test_files:
            pytest.skip("No test files found")

        unformatted, _ = test_files[0]
        temp, _ = temp_file(unformatted)

        result = run_formatter(temp, check=True, subprocess_check=False)

        # Should return non-zero (file needs formatting)
        assert result.returncode != 0

    def test_check_formatted_passes(self, temp_file):
        """Test that --check returns zero for already-formatted files."""
        # Get first formatted file
        test_files = get_test_files()
        if not test_files:
            pytest.skip("No test files found")

        _, formatted = test_files[0]
        temp, _ = temp_file(formatted)

        result = run_formatter(temp, check=True)

        # Should return zero (file is already formatted)
        assert result.returncode == 0

    def test_check_doesnt_modify_file(self, temp_file):
        """Test that --check doesn't modify files."""
        # Get first unformatted file
        test_files = get_test_files()
        if not test_files:
            pytest.skip("No test files found")

        unformatted, _ = test_files[0]
        temp, original_content = temp_file(unformatted)

        # Run with --check
        run_formatter(temp, check=True, subprocess_check=False)

        # File should be unchanged
        final_content = temp.read_text(encoding="utf-8")
        assert final_content == original_content
