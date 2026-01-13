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

+++ {"slideshow": {"slide_type": "slide"}}

# Sharing computational training material at larger scale: a French multi-tenant attempt

:::{image} https://py-edu-fr.pages.heptapod.net/_static/logo-py-edu-fr.svg
:width: 50%
:align: right
:style: opacity:0.8;filter:alpha(opacity=100);
:::

[Nicolas M. Thiéry](https://Nicolas.Thiery.name/), Professor, Laboratoire
Interdisciplinaire des Sciences du Numérique ([LISN](https://lisn.upsaclay.fr/)),
Université Paris-Saclay

Joint work with **Pierre Augier**, Éléonore Barthelian, Françoise Conil, Loïc Grobol,
**Chiara Marmo**, Olha Nahorna, **Pierre Poulain**, **N. T.**, Jeremy Laforet, ...

October 1st of 2025, [PyData Paris 2025](https://pydata.org/paris2025/)

% TODO: logos: Paris-Saclay, UGA, Bordeaux, SaclAI-School,

+++ {"slideshow": {"slide_type": "skip"}}

## Abstract

With the rise of computation and data as pillars of science, institutions are struggling
to provide large-scale training to their students and staff. Often, this leads to
redundant, fragmented efforts, with each organization producing its own bespoke training
material. In this talk, we report on a collaborative multi-tenant initiative to produce a
shared corpus of interactive training resources in the Python language, designed as a
digital common that can be adapted to diverse contexts and formats in French higher
education and beyond.

Despite continuous efforts like Unisciel or FUN MOOC, training material reuse remains
very limited in French higher education. To some extent, this is cultural with curricula
that are not standardized across universities and the absence of a textbook tradition.
Beyond intellectual property, language, and cultural barriers, instructors need or want
to adapt the training material to the split in teaching units, the audience, the format,
and pedagogical choices. Computational training material pose unique challenges as they
require adapting to various technological choices or constraints including programming
language, computational libraries, computing environments, and infrastructure. Also they
needs to be continuously maintained to adapt to the evolving technology which is
incompatible with reuse patterns such as "copy-and-forget".

We describe the team's use cases (from undergraduate to lifelong teaching, computer
science students to non specialists, intensive week-long workshops to unsupervised), the
sources of inspiration and reuse (MOOC's, Software Carpentry, ...), the current status
and content (introductory programming, ..., development tools, and best practices), the
computational environment and authoring tools (Jupyter, MyST, Jupyter-Book, version
control, software forge, and CI) and explore some levers to facilitate sharing and reuse
(modularity, gamification and decontextualisation, portability, adaptive learning,
machine assisted multilingual authoring).

This talk is intended for instructors, students, potential contributors, and anyone
interested in computational and scientific software engineering education.

+++ {"slideshow": {"slide_type": "slide"}}

## Menu

1. Yet another Python course. Really? Why?
2. py-edu-fr: in a nutshell
3. Design

+++ {"slideshow": {"slide_type": "slide"}}

## Yet another Python course? Really? Why?

+++ {"slideshow": {"slide_type": "fragment"}}

### Observations

:::{admonition} Rise of Computation and Data
as pillar of science, and beyond ...
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Major training needs
- Computing, data processing, machine learning, ...
- Programming, software engineering, open science, ...
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Major efforts
- MOOC's: Python, Scikit learn, FIDDLE, ...
- Online platforms: France IOI, ...
- Libraries of teaching resources: Unisciel, ...
- Software Carpentry, ...
- A flurry of courses delivered by universities, SME's, ...
:::

+++ {"slideshow": {"slide_type": "slide"}}

:::{admonition} Yet, in practice
:class: error

Very little reuse
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Example at Université Paris-Saclay
:class: warning

- aim to deliver some basic computational training to most students (and staff)
- 10+ independently crafted teaching units
  - covering about the same scope:\
    «Computing 101»: basic programming, computing and visualization
  - using about the same technology:\
    Python, Jupyter, numpy, pandas, matplotlib, ...
:::

+++ {"slideshow": {"slide_type": "slide"}}

### Barriers to reuse of computational training material in higher education

:::{admonition} Cultural barriers
:class: warning

- no standardized modular curricula
- no textbook tradition
- barely emerging open science tradition in education
- language: French? English?
- personal touch on education
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Technological barriers
:class: warning

- programming language, computational libraries, ...
- computing environment, infrastructure, ...
- quickly evolving technology, paradigms, and even science
- personal taste
:::

+++ {"slideshow": {"slide_type": "slide"}}

:::{admonition} Diversity of public
:class: warning

- complete beginners to experts (possibly in the same room)
- from math, physics, computer science, chemistry, biology, geosciences, sports sciences,
  economists, humanities, ...
- bachelor, master, PhD, engineers, researchers, ...

How to grab their interest? Fit their constraints?
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Diversity of formats
:class: warning

- online courses
- small to large scale physical courses (10-300 students, one semester)
- intensive training sessions and summer schools (3-5 days)
- lectures? recitations? projects?
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Time pressure
:class: attention

- high quality, reusable and reused: a high value long term investment
- quick and dirty: oh well, good enough for tomorrow's class
:::

+++ {"slideshow": {"slide_type": "slide"}}

## Py-edu-fr in a nutshell

:::::{admonition} An emerging cross institution cross profession community
:class: hint

> De Pierre Augier, <calcul@listes.math.cnrs.fr>, 15/01/2025:\
> «... Je me dis que travailler uniquement à l'échelle de notre petit groupe à Grenoble
> est un peu dommage et qu'un niveau national (ou même francophone) serait raisonnable.
> ...»

::::{grid} 2
:::{grid-item}
- **Pierre Augier**, Researcher in Fluid Mechanics, CNRS, Université Grenoble Alpes
- Eleonore Barthenlian, Data scientist
- Françoise Conil, CNRS Software Engineer at LIRIS laboratory in Lyon
- Loïc Grobol, Associate Professor in Computational Linguistics at Université Paris
  Nanterre
- **Chiara Marmo**, Research Software Engineer in Astronomy, Geosciences and Computer
  Science, Université Paris-Saclay
:::

:::{grid-item}
- Olha Nahorna, Research Engineer in Data Analysis, CNRS, Bordeaux Sciences Économiques
  (BSE)
- **Pierre Poulain**, Associate Professor in bioinformatics, Université Paris Cité
- **N. T.**, Professor in Computer Science, Université Paris-Saclay
- Jeremy Laforet, Research Engineer in Biomedical modeling, CNRS
- ... and you?
:::
::::
:::::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} trying to share open educational material
:class: hint

- Python based?
- for Higher Education and Research?
- for France? French speaking countries?
- FAIR principles: **F**indable, **A**ccessible, **A**ccessible, **I**nteroperable,
  **R**eusable
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{figure} https://imgs.xkcd.com/comics/standards.png
:alt: XKCD about n+1 standards
:::

+++ {"slideshow": {"slide_type": "slide"}}

### Current status

:::{admonition} Content
- *Introduction à la programmation avec Python et Jupyter* ("Programming and Computing
  101")
  - In French
  - About 80 Jupyter worksheets / 14h of course
  - Building on previous work in Paris-Saclay and elsewhere
  - Available online and beta tested
  - In planning: larger adoption in Paris-Saclay
- *Initiation to Python*
  - In English
  - A separate course? Or a translation of the above?
- *Advanced Python for sciences*
  - Plenty of material to be imported
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Infrastructure
- [Web site](https://py-edu-fr.pages.heptapod.net/edu.html) (👍 Findable, Accessible)
- [Public forge](https://foss.heptapod.net/py-edu-fr/py-edu-fr) (👍 Accessible)\
  Using mercurial
- [Mailing list](https://listes.services.cnrs.fr/wws/subscribe/py-edu-fr)
- [Tentative authoring conventions](https://py-edu-fr.pages.heptapod.net/contribute/authoring-conventions.html)
- Tooling (see below)
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Institutional support and funding
- Python work group of the CNRS professional networks "Calcul" and "DevLog"
- Funding by CMA SaclAI-School
:::

+++ {"slideshow": {"slide_type": "slide"}}

## Design

+++ {"slideshow": {"slide_type": "fragment"}}

### Engaging the student

:::{admonition} Desirable take home messages for beginners
1. **You** can do it!
2. It's **fun**!
3. It's **power**!\
   At your fingertip. In your own world.
4. It's **science** not alchemy
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### You can do it! And it's fun!

:::{admonition} Gamification
:class: hint

Can you program the ant out of the maze?
:::

```{code-cell}
from laby.global_fr import *

Laby(niveau="2a")
```

```{code-cell}
avance()
avance()
avance()
avance()
avance()
```

+++ {"slideshow": {"slide_type": "fragment"}}

Engaging, with (mostly) no prerequisites.

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} A good old effective idea
:class: sealso

- *Mindstorms: Children, Computers, and Powerful Ideas*, S. Papert, 1980
- original version of Laby by Gimenez et al.
- similar to, e.g., France IOI's robots\
  Could we share that widget?
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### It's power!

:::{admonition} Do interesting stuff ASAP
- The Python ecosystem rocks here!
- Potential: image, sound, 3D geometry, you name it
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Domain Context or not?
:class: attention

Solving problems in mathematics, biology, humanities, ...

- 💡Makes things concrete\
  "Oh that's what it means, in my world"
- 👍Engages\
  "Oh, that would be useful, in my world"
- 🫨Adds cognitive load, distracts
- Adds prerequisites (👎 Reuse)
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Tentative resolution
- Most of the material without domain context
- Select material rooted in context\
  With conclusion to abstract away
- Mini projects rooted in context
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### It's science

:::{admonition} Main learning objective
:class: hint Being able to rigorously:

- analyze programs and reason on them
- predict, and control their behavior
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Strategy
:class: tip Focus on:

- Introducing concepts
- Introducing models (for the memory, ...)\
  As simple as possible, but no simpler; and iterate\
  Example: at first, you don't need to know how integer are stored in memory
- Defining the syntax and semantic of constructs in these models
- Learning to analyze step by step (syllabic method first; then global)
:::

% - print versus return

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} A key learning tool: the step-by-step debugger
:class: tip

- simplify the JupyterLab interface
- support in JupyterLite
:::

+++ {"slideshow": {"slide_type": "slide"}}

### Fostering reusability and reuse

:::{admonition} Producing and reusing open content
:class: hint

- License: Creative Commons ShareAlike (👍 Accessible, Reusable)
- Reuse:
  - [Programmation Python pour les sciences de la vie](https://python.sdv.u-paris.fr/)
    Patrick Fuchs et Pierre Poulain
  - [Info 111 Programmation Impérative](https://nicolas.thiery.name/Enseignement/Info111/)
    T. et al.
  - [CodEx](https://codex.forge.apps.education.fr/)
  - ...
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### Modularity (👍 Reusable)

:::{admonition} A collection of {delete}`courses` learning activities
:class: hint

Learning activity (aka
[Learning nuggets](https://en.wikipedia.org/wiki/Learning_nugget)):

- A narrative
- Possibly with interactivity, self assessment, ...
- With explicit prerequisites and learning objectives (ongoing)

Example: mini course, exercise, mini-project, ...
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} From which courses can be composed
:class: tip

- Write a narrative referencing the chosen activities
- Or just steal the activities you like
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Adaptive learning?
:class: hint

1. Empower the learner: own pace, own helpers, ...
2. Offer a personalized experience to the learner
:::

+++ {"slideshow": {"slide_type": "fragment"}}

:::{admonition} Challenges
:class: attention

- Granularity?
- Decontextualize the content
- Where to host transitions?
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### Format

:::::{grid} 2
::::{grid-item-card}
:::{admonition} Learning unit = Markdown (+ MyST) file with metadata
:class: hint

- Simple and standard (👍 interoperable, reusable, sustainable)
- Can include learning metadata (👍 findable, adaptive)\
  Prerequisites, learning objectives, difficulty
- Can include solutions, instructor notes, ... (👍 adaptive)
- Can be interactive (👍 engaging)\
  Markdown based Jupyter notebooks
- Can include self assessment (👍 adaptive, engaging) nbgrader, jupylates, ...
- Can be randomized (👍 adaptive)
- Easy to version control (👍 accessible)
- Easy to export: pdf, web, ... (👍 accessible)\
  Jupyter-Book, MySTmd, Quarto, ...
- Easy to transforms\
  grammar-check, automated formatting, solution striping ... (👍 reuse)

[Authoring conventions](https://py-edu-fr.pages.heptapod.net/contribute/authoring-conventions.html)
:::
::::

::::{grid-item-card}
````markdown
---
jupytext:
  ...
learning:
  objectives:
    apply: [fonction]
  prerequisites:
    apply: [boucle for]
---

# TP : implanter la fonction exponentielle (1/5)

**Imaginez que vous développez ...**

Pour cela, on utilise la définition de $e^x$ en tant que *série* (somme infinie) :

$$e^x = \sum_{n=0}^{+\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} +\cdots+\frac{x^n}{n!}+\cdots$$

...

```{code-cell}
:tags: [answer]
def factorielle(n):
    ### BEGIN SOLUTION
    r = 1.0
    for i in range(1, n+1):
        r *= i    # Rappel: c'est équivalent à r = r * i
    return r
    ### END SOLUTION
```
````
::::
:::::

+++ {"slideshow": {"slide_type": "slide"}}

:::{figure} media/mydocker-jupyter-ai.png
:alt: working on the previous worksheet in Jupyter, with help from AI
:::

+++ {"slideshow": {"slide_type": "slide"}}

:::{figure} media/jupyter-travo-laby-jupylates.png
:alt: A typical work environment, with Jupyter, Travo, Laby and Jupylates
:width: 100%
:::

+++ {"slideshow": {"slide_type": "slide"}}

:::{admonition} Desirable tooling improvements
- standardization of markdown-based format for Jupyter
- support for macros in JupyterLab-MyST
- easy export to slides on the web
- ...
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### Adaptive learning (👍 autonomy, engaging)

:::{admonition} Tooling (work in progress)
:class: hint

- Learning records: track the student activity
- Learner model: estimate the student abilities
  - from learning records
  - from learning metadata
- Traffic lights: ready to engage into that activity?
- Student dashboard: display progress, recommend activities
:::

+++ {"slideshow": {"slide_type": "slide"}}

#### Multilingual?

:::{admonition} Aim: introductory courses in French and English
:class: attention

- A maintenance nightmare?
:::

+++ {"slideshow": {"slide_type": "fragment"}}

::::::{admonition} Use Machine Translation assistance (work in progress) (👍 reuse)
:class: hint

:::::{grid} 2
::::{grid-item-card}
Use Translate dir (beta): https://github.com/DobbiKov/translate-dir-cli

By Yehor Kotorenko (and T.)

- Incremental translation
- Preserves syntax and structure
- Preserves terminology
- Preserves post-edits and style
- Uses your favorite LLM
- Integrates in your favorite git workflow
::::

::::{grid-item-card}
:::{image} media/yehor.jpeg
:width: 50%
:::
::::
:::::
::::::

+++ {"slideshow": {"slide_type": "slide"}}

### Ease deployment

The learner can work on the courses:

- Online, with JupyterLite
- Online, with your favorite virtual environment (jupyterhub, mydocker, ...)
- Locally, on laptop, computer lab, ...

+++ {"slideshow": {"slide_type": "skip"}}

### Discussion

- notebooks ?
- Feedback from users

+++ {"slideshow": {"slide_type": "slide"}}

## Thank you for your attention!

::::::{admonition} py-edu-fr
:class: hint An emerging community, sharing FAIR Python training material:
https://py-edu-fr.pages.heptapod.net/edu.html

:::::{grid} 2
::::{grid-item-card}
:::{admonition} Get involved!
:class: tip

- talk to us at PyData!\
  Pierre Augier, Chiara Marmo, Pierre Poulain, N. T.
- try the course(s)
- test the course(s) in the classroom
- reuse worksheets
- provide feedback
- contribute worksheets, exercises
- improve the tooling: MyST, debugger
:::
::::

::::{grid-item-card}
:::{admonition} Upcoming sprints
:class: seealso

- PyData Paris 2025: Thursday afternoon
- PyConFR Lyon 2025: October 30-31, Lyon
:::

:::{admonition} Sponsors
CMA SaclAI-School, CNRS WorkGroups Calcul and DevLog, ...
:::
::::
:::::
::::::

:::{admonition} Upcoming jobs at Paris-Saclay: project [ATLAS - AI for Teaching and Learning (AI) at Scale](https://atlas.gitlab.dsi.universite-paris-saclay.fr/)
:class: seealso

- Post-doc to conduct research in education and human-centric design and computing
- Research Software Engineer: javascript, jupyter, ...
:::
