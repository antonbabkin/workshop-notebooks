---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# Literate programming and interactive reporting with Jupyter notebooks
*aka Notebok Imperialism*

**Anton Babkin**  
UConn and UW-Madison  
anton.babkin@uconn.edu

UW-Madison Data Science Research Bazaar  
9 February 2022

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# Scientific paper is obsolete
[The Atlantic](https://www.theatlantic.com/science/archive/2018/04/the-scientific-paper-is-obsolete/556676/), April 5, 2018

![atlantic](https://cdn.theatlantic.com/assets/media/img/mt/2018/04/FlameNew_1/facebook.gif)

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# Literate programming

> Let us change our traditional attitude to the construction of programs: Instead of imagining that our main task is to instruct a computer what to do, let us concentrate rather on explaining to humans what we want the computer to do.

Donald E. Knuth, Literate Programming, 1984

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# This workshop

- walk though all steps of a research project
- focus on documentation and modularity
- create an interactive dashboard
- we will go over many different tools
- but keep in mind bigger workflow picture

Research question:  
How states and counties in the USA compare in terms of their population and employment growth?

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# Output preview

- public GitHub repository
- static documentation site
- dashboard on Binder
- importable components

+++ {"slideshow": {"slide_type": "subslide"}, "tags": []}

## importable components

```{code-cell} ipython3
:tags: []

from popemp import analysis
analysis.prep_data()
analysis.plot_growth('55', '000', 2005, 2015)
```

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# Environment

If you have a local Python/conda environment, pull most recent copy of the repo. Easiest way to do this is to delete everything and make a fresh clone.

If you do not have local environment, *try* to use Binder.

+++ {"slideshow": {"slide_type": "slide"}, "tags": []}

# File structure

```
README.md
environment.yml        # env reproducibility
mkdocs.yml             # docs config
nbs/
    __init__.ipynb     # control panel
    tools.ipynb
    data.ipynb
    analysis.ipynb
    dashboard.ipynb
popemp/
    tools.py
    data.py
    analysis.py
docs_src/              # temporary docs files, gitignore
    tools.md
    data.md
    analysis.md
docs/                  # docs site hosted on GitHub
    tools.html         # actual files are different
    data.html          # but they are HTML versions
    analysis.html      # of notebooks
```
