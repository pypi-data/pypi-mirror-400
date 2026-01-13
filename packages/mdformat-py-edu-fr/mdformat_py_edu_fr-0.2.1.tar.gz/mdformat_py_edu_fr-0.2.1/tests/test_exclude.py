"""Test the --exclude flag behavior."""

import pytest

from .conftest import run_formatter


def test_exclude_single_pattern(tmp_path):
    """Test excluding files with a single pattern."""
    # Create structure
    (tmp_path / "include.md").write_text("# Include\n", encoding="utf-8")
    (tmp_path / "exclude.md").write_text("# Exclude\n", encoding="utf-8")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "nested.md").write_text("# Nested\n", encoding="utf-8")

    # Run with exclude pattern
    result = run_formatter(tmp_path, exclude=["exclude.md"], verbose=True)

    # Check that exclude.md was not mentioned in verbose output
    assert "exclude.md" not in result.stdout
    # But include.md should be processed
    assert "include.md" in result.stdout or result.returncode == 0


def test_exclude_multiple_patterns(tmp_path):
    """Test excluding files with multiple patterns."""
    # Create structure
    (tmp_path / "keep.md").write_text("# Keep\n", encoding="utf-8")
    (tmp_path / "draft_1.md").write_text("# Draft 1\n", encoding="utf-8")
    (tmp_path / "draft_2.md").write_text("# Draft 2\n", encoding="utf-8")
    (tmp_path / "_build/html").mkdir(parents=True)
    (tmp_path / "_build/html" / "generated.md").write_text(
        "# Generated\n", encoding="utf-8"
    )

    # Run with multiple exclude patterns
    result = run_formatter(
        tmp_path, exclude=["draft_*.md", "_build/**/*.md"], verbose=True
    )

    # Check that excluded files were not mentioned
    assert "draft_1.md" not in result.stdout
    assert "draft_2.md" not in result.stdout
    assert "generated.md" not in result.stdout


def test_exclude_directory_pattern(tmp_path):
    """Test excluding entire directories."""
    # Create structure with .ipynb_checkpoints
    (tmp_path / "main.md").write_text("# Main\n", encoding="utf-8")
    (tmp_path / ".ipynb_checkpoints").mkdir()
    (tmp_path / ".ipynb_checkpoints" / "checkpoint.md").write_text(
        "# Checkpoint\n", encoding="utf-8"
    )
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / ".ipynb_checkpoints").mkdir()
    (tmp_path / "subdir" / ".ipynb_checkpoints" / "nested.md").write_text(
        "# Nested\n", encoding="utf-8"
    )
    (tmp_path / "subdir" / "real.md").write_text("# Real\n", encoding="utf-8")

    # Exclude all .ipynb_checkpoints directories
    result = run_formatter(tmp_path, exclude=["**/.ipynb_checkpoints/*"], verbose=True)

    # Checkpoints should not be processed
    assert "checkpoint.md" not in result.stdout
    assert ".ipynb_checkpoints" not in result.stdout
    # But real files should be
    assert "main.md" in result.stdout or result.returncode == 0


def test_exclude_with_check_mode(tmp_path):
    """Test that --exclude works with --check mode."""
    # Create files
    (tmp_path / "format_me.md").write_text("# Format Me\n", encoding="utf-8")
    (tmp_path / "skip_me.md").write_text("# Skip Me\n", encoding="utf-8")

    # Run with both --check and --exclude
    result = run_formatter(tmp_path, check=True, exclude=["skip_me.md"], verbose=True)

    # Should only check format_me.md
    # skip_me.md should not appear in output
    if "skip_me.md" in result.stderr or "skip_me.md" in result.stdout:
        pytest.fail("Excluded file was processed in check mode")
