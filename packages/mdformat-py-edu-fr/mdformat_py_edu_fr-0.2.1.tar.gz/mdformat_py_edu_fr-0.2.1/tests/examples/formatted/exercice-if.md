---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
learning:
  objectives:
    understand: [conditionnelles]
  prerequisites:
    understand: [variable, affectation, "cha\xEEne de caract\xE8res"]
---

This case is interesting since it contains:

- "chaîne de caractères" (with accents) in the frontmatter,
- tabulations in Python code,
- `{code-cell} ipython3`,
- a `code-cell` without a line at the beginning and with two lines at the end.

```{code-cell}
:tags: [hide-cell, substitutions]

from random import randint
from jupylates.jupylates_helpers import SUBSTITUTE, INPUT_TEXT

SUBSTITUTE(N=randint(0, 20), T1=randint(3, 8), T2=randint(12, 17))
```

And now a cell that cannot be formatted (IPython syntax).

```{code-cell}
:format: false

run ../common/examples/helloworld.py
```

A cell that should not be formatted:

```{code-cell}
%run ../common/examples/helloworld.py
```

A cell ending with a semicolon:

```{code-cell}
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(1, 1);
```
