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
---

+++ {"nbgrader": {"grade": false, "grade_id": "cell-bf9ca73c9aeacd67", "locked": true, "schema_version": 3, "solution": false, "task": false}}

# La Spirale


```{code-cell} ipython3
---
nbgrader:
  grade: false
  grade_id: cell-7cadb46acaf8c84f
  locked: true
  schema_version: 3
  solution: false
  task: false
---
from laby.global_fr import *
Laby(niveau = "4a")
```

```{code-cell} ipython3
---
nbgrader:
  grade: false
  grade_id: cell-ede44025f9b6e211
  locked: false
  schema_version: 3
  solution: true
  task: false
---
debut()
### BEGIN SOLUTION
while( regarde() != Sortie ):
  while( regarde() != Mur ):
    avance()
  gauche()
ouvre()
### END SOLUTION
```

```{code-cell} ipython3

```
