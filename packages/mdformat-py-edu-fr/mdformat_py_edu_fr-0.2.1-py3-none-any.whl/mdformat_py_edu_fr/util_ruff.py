import subprocess


class RuffFormattingError(Exception):
    """Exception raised when ruff formatting fails."""


def format_code_with_ruff(code: str) -> str:
    """Format Python code using ruff.

    Returns formatted code.

    Raises:
        RuffFormattingError: If ruff formatting fails.
    """
    ends_with_semicolon = code.endswith(";")
    if ends_with_semicolon:
        code = code[:-1]

    result = subprocess.run(
        ["ruff", "format", "-"],
        input=code.encode("utf-8"),
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8")
        raise RuffFormattingError(error_msg)

    code_out = result.stdout.decode("utf-8")
    if ends_with_semicolon:
        code_out = code_out[:-1] + ";\n"
    return code_out
