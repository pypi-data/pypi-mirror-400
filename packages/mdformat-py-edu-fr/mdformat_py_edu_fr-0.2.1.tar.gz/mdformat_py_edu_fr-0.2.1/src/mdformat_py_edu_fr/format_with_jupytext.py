import jupytext
import re
import sys

from pathlib import Path

from mdformat_py_edu_fr.util_ruff import format_code_with_ruff, RuffFormattingError


LABEL_PATTERN = re.compile("(?m)(^\\s*\\(\\w+\\)=)(\r?\n)(\\s*\r?\n)")

path_config_file = Path(__file__).absolute().parent / "jupytext.toml"
config = jupytext.config.load_jupytext_configuration_file(str(path_config_file))


def format_md_with_jupytext(text: str, path_input_file: Path | None = None) -> str:
    """Format the code of a notebook code using jupytext"""

    notebook = jupytext.reads(text, fmt="md:myst")
    if "kernelspec" not in notebook.metadata:
        return text
    language = notebook["metadata"]["kernelspec"]["language"]
    if "learning" in notebook.metadata:
        # Fix common errors in learning metadata
        learning = notebook.metadata["learning"]
        for a in ["prerequisites", "objectives"]:
            # Fix singular instead of plural
            singular = a[:-1]
            if singular in learning:
                learning[a] = learning[singular]
                del learning[singular]

            # Fix string instead of list of string
            for b in ["discover", "remember", "understand", "apply"]:
                if a in learning and isinstance(learning[a].get(b), str):
                    learning[a][b] = [s.strip() for s in learning[a][b].split(",")]

    for cell in notebook.cells:
        if (
            language == "python"
            and cell["cell_type"] == "code"
            and cell["metadata"].get("format", True)
            and not all(
                any(line.strip().startswith(char) for char in "#%!")
                for line in cell.source.splitlines()
            )
        ):
            try:
                cell.source = format_code_with_ruff(cell["source"].strip())
            except RuffFormattingError as exc:
                print(
                    f"Ruff formatting failed for file\n{path_input_file or '???'}\n"
                    f"cell source:\n{cell.source}\n",
                    exc,
                    file=sys.stderr,
                )
                sys.exit(1)

        if (
            cell.metadata is not None
            and "tags" in cell.metadata
            and cell.metadata["tags"] == []
        ):
            del cell.metadata["tags"]
        # Workaround to remove empty lines between label and subsequent item
        if cell.cell_type == "markdown":
            cell.source = re.sub(LABEL_PATTERN, r"\1\2", cell.source)

    result = jupytext.writes(notebook, fmt="md:myst", config=config)
    if language == "python":
        result = result.replace("```{code-cell} ipython3", "```{code-cell}")
    return result
