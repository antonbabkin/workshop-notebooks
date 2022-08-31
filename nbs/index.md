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

This notebook contains code for project initialization and testing.
Run all cells in order.
If you see outputs and no errors, your environment is probably working correctly.
Cells in this notebook are safe to run multiple times.

+++

# Initialize paths

File organization in this project requires package directory `popemp` to be visible inside of the notebooks directory `nbs`. When you clone this repository for the first time, you need to run the below cell to create a symbolic link that points to `popemp`. IPython cross-platform `%cd` magics are used to temporarily move up one level to project root and then back. Calling `Nbd` class constructor creates symlinks and other neccesy directories.

```{code-cell} ipython3
:tags: []

%cd ..
from popemp.tools import Nbd
nbd = Nbd('popemp')
%cd -
# verify that project root is the folder into which you cloned the repository
print(f'Project root: "{nbd.root}"')
# make sure that "nbs/popemp" contains "analysis.py", "data.py" and "tools.py"
print('"nbs/popemp/" folder contents:')
%ls "{nbd.root/'nbs/popemp'}/"
```

# Python environment

The code cell below will test main packages that should be available in active Conda/Python environment.
If the environment works, you should see a map with an interactive slider in the output.

```{code-cell} ipython3
:tags: []

import numpy as np
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import ipywidgets as widgets

df = pd.read_csv('https://www2.census.gov/programs-surveys/bds/tables/time-series/bds2019_st.csv', dtype=str)
df = df[['year', 'st', 'emp']]
df['year'] = pd.to_numeric(df['year'])
df['emp'] = pd.to_numeric(df['emp'])
df = df.query('year >= 1990')
emp = df

df = geopandas.read_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip')
df = df.rename(columns={'STATEFP': 'st'})
df = df[['st', 'geometry']]
df = df.query('st != "02" and st != "15"')
geo = df

def plot(y0, y1):
    df = emp.copy()
    df = df.query('year == @y0 or year == @y1').set_index(['st', 'year'])['emp']
    df = df.unstack()
    df = np.power(df[y1] / df[y0], 1/(y1-y0-1))*100 - 100
    df = df.to_frame('emp_gr').reset_index()
    df = geo.merge(df)
    fig, ax = plt.subplots(figsize=(12, 8))
    df.plot(ax=ax, column='emp_gr', legend=True,
            legend_kwds={'label': f'Average annual employment growth by state, {y0}-{y1}' ,'orientation': 'horizontal'})
    plt.close()
    return fig

def upd(change):
    with out:
        out.clear_output(True)
        display(plot(*change['new']))
years = widgets.IntRangeSlider(value=(2005, 2015), min=1990, max=2019, continuous_update=False)
out = widgets.Output()
years.observe(upd, 'value')
upd({'new': years.value})
widgets.VBox([years, out])
```

# Project modules

The cells below test modules of this project.
Running them should display a few maps and figures.

```{code-cell} ipython3
:tags: [nbd-docs]

from popemp import tools
nbd = tools.Nbd('popemp')
f = tools.download_file('https://raw.githubusercontent.com/antonbabkin/workshop-notebooks/main/LICENSE', nbd.root, 'LICENSE_COPY')
assert open(nbd.root/'LICENSE').read() == open(f).read()
f.unlink()
```

```{code-cell} ipython3
:tags: [nbd-docs]

import plotly.express as px
from popemp import data
wi = 'st == "55" and cty == "000"'
display(data.geo().query(wi).explore(width=600, height=400))
data.pop().query(wi).set_index('year')['pop'].plot(title='Wisconsin population')
fig = px.line(data.emp().query(wi), x='year', y='emp', title='Wisconsin employment')
fig.show()
```

```{code-cell} ipython3
:tags: []

from popemp import analysis
analysis.prep_data()
display(analysis.plot_agr('55', 2005, 2015, 'rel'))

m = analysis.Map()
m.upd('00', 2005, 2015, 'rel')
m.widget
```
