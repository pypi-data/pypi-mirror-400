---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Main characteristics

## Has to be there

Few characteristics of the Python language and ecosystem...

- Definition keywords and "built-in identifiers" (https://docs.python.org/3/library/builtins.html)

- Notions of assignment, names, references

- First name space / object space diagram

- Keyword `del`

- Built-in functions `type()`

- ...

- A reference interpreter and few alternative interpreters

  - CPython
  - PyPy
  - GraalPy
  - MicroPython

Take away: dynamic languages strong thanks to tooling and testing.

## Open-source language, interpreters and ecosystem

## Interpreted (but there are tools to compile Python code)

## Automatic memory management

## Dynamically strongly typed: types, objects and variables

The function `type` returns the type of an **object**:

```{code-cell} ipython3
type("hello")
```

```{code-cell} ipython3
type(2)
```

```{code-cell} ipython3
type(2.0)
```

```{code-cell} ipython3
type(2 + 2)
```

```{code-cell} ipython3
type(2 + 2.0)
```

```{code-cell} ipython3
type(True)
```

**Variables** are just tags pointing towards objects. New variables can be used when
needed. They are not associated with a type but only with an object (which has a type)...

```{code-cell} ipython3
myvar = 1
print(myvar, type(myvar))
```

```{code-cell} ipython3
myvar = "hello"
print(myvar, type(myvar))
```

### Spaces for objects and variables (names)

Objects and variables (names) are two very different concepts:

- Objects live in one "object space". They have an address in the memory.
- Names live in namespaces.

It is often interesting to represent the execution of a Python program in an **"object
space - namespaces" diagram**.

The Zen of Python says "Namespaces are one honking great idea -- let's do more of
those!". A namespace is created for every module (file) and for every function execution,

## Gradual learning curve

## A philosophy: the [Zen of Python](https://www.python.org/dev/peps/pep-0020/)

```text
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

## Very clean and readable

## Indentation defines the blocks

## Style coding is important: [PEP 8](https://www.python.org/dev/peps/pep-0008/)

```{admonition} [PEP: Python Extension Proposal](https://en.wikipedia.org/wiki/Python_Enhancement_Proposal)

From the [Wikipedia article](https://en.wikipedia.org/wiki/Python_(programming_language)#Development):

> Python's development is conducted largely through the Python Enhancement Proposal (PEP) process, the primary mechanism for proposing major new features, collecting community input on issues, and documenting Python design decisions.

```

- Code layout
- Imports
- White spaces in expressions and statements
- Comments
- Documentation strings
- Naming conventions
- Programming recommendations

### PEP8: examples of bad and good style practices

```{code-cell} ipython3
---
jupyter:
  outputs_hidden: true
---
# bad (spaces between operator)
number=0
# ok
number = 0
```

```{code-cell} ipython3
---
jupyter:
  outputs_hidden: true
---
# bad (indentation with 2 spaces, has to be 4)
if number == 0:
  number = 1

# ok
if number == 0:
    number = 1
```

```{code-cell} ipython3
---
jupyter:
  outputs_hidden: true
---
# bad (space after ,)
mylist = [1,2,3]

# ok
mylist = [1, 2, 3]
```

## Only few [keywords](https://hg.python.org/cpython/file/3.13/Lib/keyword.py) and [built-in functions](https://docs.python.org/3/library/functions.html)

- Keywords,

```{code-cell} ipython3
---
slideshow:
  slide_type: '-'
---
help("keywords")
```

- [built-in functions](https://docs.python.org/3/library/functions.html),
- [built-in constants](https://docs.python.org/3/library/constants.html),
- [built-in exceptions](https://docs.python.org/3/library/exceptions.html).

## Errors should never pass silently

## Multi-paradigm (sequential, object-oriented, functional)

## "Batteries Included": [the standard library](https://docs.python.org/3/tutorial/stdlib.html)

## Huge success, strong community and huge ecosystem

- https://www.tiobe.com/tiobe-index/
- https://spectrum.ieee.org/top-programming-languages-2024
- https://kinsta.com/blog/github-statistics/

In 2024:

> GitHub also provides insights into their users’ language preferences:
>
> - The top three programming languages are JavaScript, Python, and Java.
> - PHP has decreased in popularity, dropping from sixth to seventh place in 2022.
> - The Hashicorp Configuration Language (HCL) is the fastest-growing language on GitHub,
>   with a usage increase of 56.1 percent.
> - Rust experienced a growth rate of more than 50 percent, which GitHub attributes to
>   its security and reliability.
> - Python continues to grow in popularity, with a 22.5 percent increase per year.

- https://blog.joss.theoj.org/2023/05/JOSS-publishes-2000th-paper

> JOSS reviews are primarily about the software, and so it would be remiss of us not to
> talk about that. Python is still the #1 language for JOSS submissions, used in part for
> well over half of published papers (~1200 out of 2000). R is #2 at 445 submissions, and
> C++ #3 (although of course C++ and C may be used together with another language).
