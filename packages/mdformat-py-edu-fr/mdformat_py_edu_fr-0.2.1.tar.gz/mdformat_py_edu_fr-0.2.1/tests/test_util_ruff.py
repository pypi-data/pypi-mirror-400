import pytest

from pathlib import Path

from markdown_it.utils import read_fixture_file

from mdformat_py_edu_fr.util_ruff import format_code_with_ruff, RuffFormattingError


TEST_CASES = read_fixture_file(Path(__file__).parent / "./fixtures_ruff.txt")


@pytest.mark.parametrize(
    "line,title,text,expected", TEST_CASES, ids=[f[1] for f in TEST_CASES]
)
def test_format_with_ruff(line, title, text, expected):
    assert format_code_with_ruff(text) == expected


def test_error():
    code = "a ==== 1"

    with pytest.raises(RuffFormattingError, match="error: Failed to parse"):
        format_code_with_ruff(code)
