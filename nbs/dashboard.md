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

# Population and employment dynamics in states and counties of the USA

This map shows how population and employment changed in different USA territories over time. Absolute growth is average growth rate in percentage points. Relative growth is deviation from growth in a reference territory: USA for states and state for counties.

```{code-cell} ipython3
:tags: []

import ipywidgets as widgets

# run initialization in the context of a temporary Output widget
# this has effect of concealing all output so it does not clutter the dashboard
with widgets.Output():
    # cd to project root and back for import from "popemp" package
    # this is needed to run dashboard on Binder without creating symlink
    %cd ..
    from popemp import analysis
    %cd -

    analysis.prep_data()
```

```{code-cell} ipython3
:tags: []

year_selector = widgets.IntRangeSlider(value=(2005, 2015), min=1990, max=2019)
abs_rel_selector = widgets.RadioButtons(options=[('Absolute', 'abs'), ('Relative', 'rel')])
state_selector, _ = analysis.st_cty_selectors()
update_button = widgets.Button(description='Update')

controls = widgets.VBox([
    widgets.Label('Year range'),
    year_selector,
    widgets.Label('Growth rates'),
    abs_rel_selector,
    widgets.Label('Nation-wide or state'), 
    state_selector, 
    update_button])

map_ = analysis.Map()
# this seems to glitch the map, oops!
# map_.widget.layout = widgets.Layout(height='100%')

graph = widgets.Output()
```

```{code-cell} ipython3
:tags: []

def update_graph(st, cty):
    with graph:
        graph.clear_output(True)
        fig = analysis.plot_growth(st, cty, *year_selector.value)
        fig.set_size_inches(8, 10)
        display(fig)

def update_map(*_):
    map_.upd(state_selector.value, *year_selector.value, abs_rel_selector.value)
    update_graph(state_selector.value, '000')
update_button.on_click(update_map)

def click_area(**kw):
    p = kw['properties']
    update_graph(p['st'], p['cty'])
map_.click_callback = click_area

update_map()
```

```{code-cell} ipython3
:tags: []

widgets.AppLayout(left_sidebar=controls,
                center=map_.widget, 
                right_sidebar=graph)
```

Data sources:
- [population](https://www.census.gov/programs-surveys/popest.html) - US Census Bureau, Population Estimates Program (PEP)
- [employment](https://www.census.gov/programs-surveys/bds.html) - US Census Bureau, Business Dynamics Statistics (BDS)
