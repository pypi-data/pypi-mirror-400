import re

from mdformat_py_edu_fr.format_with_jupytext import LABEL_PATTERN


def test_label_pattern():
    assert (
        re.sub(
            LABEL_PATTERN,
            r"\1\2",
            """
                  (label)=


                  bla
                  """,
        )
        == """
                  (label)=
                  bla
                  """
    )
    assert (
        re.sub(
            LABEL_PATTERN,
            r"\1\2",
            """
                  (oper)=

                  :::{admonition} Opérations arithmétiques sur les entiers
                  """,
        )
        == """
                  (oper)=
                  :::{admonition} Opérations arithmétiques sur les entiers
                  """
    )
