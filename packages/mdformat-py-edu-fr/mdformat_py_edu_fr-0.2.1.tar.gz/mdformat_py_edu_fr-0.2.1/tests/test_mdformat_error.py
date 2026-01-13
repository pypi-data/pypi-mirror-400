from pathlib import Path

from .conftest import run_formatter


def test_mdformat_error():
    path_mdformat_error = Path(__file__).parent / "examples/mdformat_error.md"
    assert path_mdformat_error.exists()

    process = run_formatter(path_mdformat_error, subprocess_check=False)
    assert process.returncode
    assert process.stderr.startswith("Error: mdformat exception for file")
    assert "examples/mdformat_error.md" in process.stderr
