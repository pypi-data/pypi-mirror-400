"""Test command-line interface behavior."""

from .conftest import run_formatter


def test_version_flag():
    """Test that --version works."""

    result = run_formatter(version=True)

    assert result.returncode == 0
    assert "mdformat-py-edu-fr" in result.stdout


def test_nonexistent_file():
    """Test behavior with non-existent file."""
    result = run_formatter("/nonexistent/file.md", subprocess_check=False)

    # Should fail gracefully
    assert result.returncode != 0


def test_directory_processing(tmp_path):
    """Test that directories are processed recursively."""
    # Create nested structure
    (tmp_path / "subdir").mkdir()
    (tmp_path / "test1.md").write_text("# Test 1\n", encoding="utf-8")
    (tmp_path / "subdir" / "test2.md").write_text("# Test 2\n", encoding="utf-8")

    result = run_formatter(tmp_path)

    assert result.returncode == 0
