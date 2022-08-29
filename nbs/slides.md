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

```{raw-cell}

---
title: "Jupyter notebooks"
subtitle: "Literate programming and interactive reporting"
author: "Anton Babkin (anton.babkin@uconn.edu)"
institute: UConn and UW-Madison
date: "29-30 August 2022"
format: 
  revealjs:
    progress: true
    embed-resources: true
---
```

## Scientific paper is obsolete
[The Atlantic](https://www.theatlantic.com/science/archive/2018/04/the-scientific-paper-is-obsolete/556676/), April 5, 2018

![](https://cdn.theatlantic.com/assets/media/img/mt/2018/04/FlameNew_1/facebook.gif)

+++ {"tags": []}

## Literate programming

> Let us change our traditional attitude to the construction of programs: Instead of imagining that our main task is to instruct a computer what to do, let us concentrate rather on explaining to humans what we want the computer to do.

Donald E. Knuth, Literate Programming, 1984

+++ {"tags": []}

## This workshop

- walk though all steps of a research project
- focus on documentation and modularity
- create an interactive dashboard
- we will go over many different tools
- but keep in mind bigger workflow picture

Research question:  
How states and counties in the USA compare in terms of their population and employment growth?

+++ {"tags": []}

## Output preview

- public GitHub repository
- static documentation site
- dashboard
- importable components

+++ {"tags": []}

## importable components

```{code-cell} ipython3
:tags: []

from popemp import analysis
analysis.prep_data()
analysis.plot_growth('55', '000', 2005, 2015)
```

## Tools

- Jupyter notebooks
- Git, GitHub and GitHub Pages
- Jupytext
- conda/mamba
- Quarto
- Voila
- Binder
- custom scripts in `tools.py`

+++ {"tags": []}

## Environment checklist

- install git, conda and mamba

- update local repo (will erase your changes)
```
cd workshop-notebooks
git reset --hard
git pull
```
    
- update conda env
```
mamba env update -f environment.yml
```

- run index notebook

If you do not have a local environment, use Binder.

+++ {"tags": []}

## File structure

```
README.md
environment.yml        # env reproducibility
data/                  
nbs/                   # source notebooks
    index.ipynb        # init and env test
    tools.ipynb        # (1)
    data.ipynb         # (2)
    analysis.ipynb     # (3)
    dashboard.ipynb
    popemp/            # symlink to ../popemp/
    _quarto.yml        # docs website spec
popemp/                # importable Python package
    tools.py           # (1)
    data.py            # (2)
    analysis.py        # (3)
docs/                  # docs site hosted on GitHub
    tools.html         # (1)
    data.html          # (2)
    analysis.html      # (3)
```
