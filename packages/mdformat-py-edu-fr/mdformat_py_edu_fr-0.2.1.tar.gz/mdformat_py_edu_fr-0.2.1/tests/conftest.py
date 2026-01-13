import subprocess
import sys

from pathlib import Path
from typing import Optional, List


def run_formatter(
    path: Path or str or None = None,
    check: bool = False,
    version: bool = False,
    verbose: bool = False,
    exclude: Optional[List[str]] = None,
    subprocess_check: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run the mdformat-py-edu-fr formatter on a path.

    Args:
        path: Path to file or directory to format
        check: If True, run in check mode (--check flag)

    Returns:
        CompletedProcess instance
    """
    cmd = [sys.executable, "-m", "mdformat_py_edu_fr"]
    if check:
        cmd.append("--check")

    if version:
        cmd.append("--version")

    if verbose:
        cmd.append("-v")

    if path is not None:
        cmd.append(str(path))

    if exclude:
        for pattern in exclude:
            cmd.extend(["--exclude", pattern])

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=subprocess_check,
    )
