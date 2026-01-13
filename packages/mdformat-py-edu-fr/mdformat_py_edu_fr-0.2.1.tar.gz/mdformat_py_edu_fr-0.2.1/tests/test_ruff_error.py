from pathlib import Path

from .conftest import run_formatter


def test_ruff_error():
    path_ruff_error = Path(__file__).parent / "examples/ruff_error.md"
    assert path_ruff_error.exists()

    process = run_formatter(path_ruff_error, subprocess_check=False)
    assert process.returncode
    assert process.stderr.startswith("Ruff formatting failed for file")
