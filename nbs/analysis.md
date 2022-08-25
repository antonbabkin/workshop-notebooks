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

[nbd]: # "docs"
# Analysis of population and employment dynamics

In this module we will combine economic, demographic and geographic data to explore patterns of population and employment dynamics across states and counties.

```{code-cell} ipython3
#nbd module
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
import ipyleaflet as leaflet

from popemp.tools import Nbd
from popemp import data
nbd = Nbd('popemp')
```

[nbd]: # "docs"
Main dataframes are stored in a global dict `DF`. During interactive notebook execution it is populated as needed. If imported as a module, function `prep_data()` should be called before using other module functions.

```{code-cell} ipython3
#nbd module docs
DF = {}

def prep_data():
    DF['geo'] = data.geo()
    DF['by year'] = data_by_year()
```

```{code-cell} ipython3
DF['geo'] = data.geo()
```

[nbd]: # "docs"
In `data_by_year()` we simply merge employment and population dataframes available from `popemp.data` module.

```{code-cell} ipython3
#nbd module
def data_by_year():
    df = data.pop().merge(data.emp(), 'left').query('pop.notna() and emp.notna()')
    return df
```

```{code-cell} ipython3
#nbd docs
DF['by year'] = data_by_year()
DF['by year'].head()
```

[nbd]: # "docs"
# Dynamics in a given geographic area

+++

Let's explore the data a little. I will pretend that I am seeing it for the first time and do a bit of live coding resembling my typical approach. I start with a small and simple snippet, gradually add details and continuously test, and when if something useful comes out of it, I clean it up and wrap in a function. This is scratch work, and neither these comments nor code goes to documentation or module, but it stays in the notebook as a record of the thought process.

```{code-cell} ipython3
# YOUR CODE GOES HERE
```

[nbd]: # "docs"
Function `plot_growth(st, cty, y0, y1)` makes a plot with population and employment dynamic in a chosen geographic area. Level series are normalized to 100 in base year `y0`. Year-to-year growth rates are shown in a separate panel. For states and counties we also add lines for a bigger reference geography: states are compared to entire country, counties are compared to their state.

```{code-cell} ipython3
#nbd module
def plot_growth(st, cty, y0, y1):
    
    def _df(s, c, y0, y1):
        """Select state `s` and county `c` and compute indices."""
        d = DF['by year'].query('st == @s and cty == @c and year >= @y0 and year <= @y1')
        d = d.set_index('year').sort_index()
        d['pop_idx'] = d['pop'] / d.loc[y0, 'pop'] * 100
        d['emp_idx'] = d['emp'] / d.loc[y0, 'emp'] * 100
        return d
    
    d = _df(st, cty, y0, y1)
    if cty == '000':
        reference = 'United States'
        d0 = _df('00', '000', y0, y1)
    else:
        reference = DF['geo'].query('st == @st and cty == "000"')['name'].iloc[0]
        d0 = _df(st, '000', y0, y1)

    fig, ax = plt.subplots(2, sharex=True)
    plt.close()
    if st == '00':
        title = f'United States, {y0}-{y1}'
    else:
        nm = DF['geo'].query('st == @st and cty == @cty')['name'].iloc[0]
        title = f'{nm}, {y0}-{y1}'
    fig.suptitle(title)

    a = ax[0]
    a.set_title(f'Pop and emp index, {y0} = 100 (dotted {reference})')
    l_pop = a.plot(d.index, d['pop_idx'])[0]
    l_emp = a.plot(d.index, d['emp_idx'])[0]
    a.plot(d0.index, d0['pop_idx'], ls=':', c=l_pop.get_color())
    a.plot(d0.index, d0['emp_idx'], ls=':', c=l_emp.get_color())
    a.set_xticks(d.index)
    a.set_xticks([], minor=True)
    a.grid(True)

    a = ax[1]
    d1 = d.query('year > @y0')
    a.bar(d1.index, d1['pop_gr'], width=-0.4, align='edge')
    a.bar(d1.index, d1['emp_gr'], width=0.4, align='edge')
    a.set_title(f'Population and employment growth rate, %')
    a.legend(['Population', 'Employment'])
    a.grid(True)

    return fig
```

[nbd]: # "docs"
We can see that Wisconsin population was growing slower than national, and that post-recession employment recovery was also slower.

```{code-cell} ipython3
#nbd docs
plot_growth('55', '000', 2005, 2015)
```

[nbd]: # "docs"
## Widgets

Jupyter [widgets](https://ipywidgets.readthedocs.io) are like other Python objects such as strings, lists or pandas dataframes. Like other objects widgets also store their state, have methods to do something useful with that state and have a representation suitable for rich rendering in a HTML view of a Jupyter notebook. Additional feature of widgets is that their visual representation can be updated dynamically and they can respond to user interaction.

Here is a simple slider. We can read it's value in code from another cell and also change it's value programmatically.

```{code-cell} ipython3
#nbd docs
w = widgets.IntSlider(value=4, min=0, max=10, description='How many?')
w
```

```{code-cell} ipython3
#nbd docs
print('He says', w.value)
```

```{code-cell} ipython3
#nbd docs
w.value = 5
```

```{code-cell} ipython3
#nbd docs
print('Now he says', w.value)
```

[nbd]: # "docs"
We can combine multiple widgets and make them do something useful together. A button here will add up two numbers and display result in a separate label widget. We can even be fancy and use $\LaTeX$ in text labels.

```{code-cell} ipython3
#nbd docs
# create widgets
wx = widgets.IntSlider(2, 0, 5, description='$x$')
wy = widgets.IntSlider(2, 0, 5, description='$y$')
wb = widgets.Button(description='Add')
wz = widgets.Label('$x + y = ?$')

# useful function
def how_many(x, y):
    z = x + y
    return 5

def click_handler(*args):
    # "*args" captures arguments passed from calling widget, but we ignore them here
    x = wx.value
    y = wy.value
    z = how_many(x, y)
    wz.value = f'${x} + {y} = {z}$'
# run handler to fill initial values
click_handler()
# register handler with button widget
wb.on_click(click_handler)

# display widgets in a simple vertical layout
widgets.VBox([wx, wy, wb, wz])
```

[nbd]: # "docs"
Function `st_cty_selectors()` creates two dropdown widgets that can be used to select state and county using their names instead of codes, while codes are used internally to work with our dataframes. Lists of states and counties are populated from our global tables. Additional logic, wrapping inside of the function, updates list of counties dynamically every time the state is changed. We can now create a pair of linked widgets anywhere we need them later.

```{code-cell} ipython3
#nbd module
def st_cty_selectors():
    st_codes = DF['by year']['st'].unique().tolist()
    d = DF['geo'].query('st != "00" and cty == "000"')
    d = d.loc[d['st'].isin(st_codes), ['name', 'st']].sort_values('name')
    w_st = widgets.Dropdown(options=[['United States', '00']] + d.values.tolist())

    w_cty = widgets.Dropdown(options=[('----', '000')])

    def update_cty_list(change):
        st = change['new']
        opts = [('----', '000')]
        if st != '00':
            cty_codes = DF['by year'].query('st == @st')['cty'].unique().tolist()
            d = DF['geo'].query('st == @st and cty != "000"')
            d = d.loc[(d['st'] == st) & d['cty'].isin(cty_codes), ['name', 'cty']].sort_values('name')
            opts += [(n.split(', ')[0], c) for n, c in d.values]
        w_cty.options = opts
    w_st.observe(update_cty_list, 'value')
    
    return w_st, w_cty
```

Here we use widgets to control and update plot generated by `plot_growth()` function defined above. A special `Output` widget is used to display the figure, otherwise it would be hidden in a log.

```{code-cell} ipython3
y = widgets.IntRangeSlider(value=(2005, 2015), min=1990, max=2019)
s, c = st_cty_selectors()
o = widgets.Output()
b = widgets.Button(description='Update')
def upd(*_):
    with o:
        o.clear_output(True)
        fig = plot_growth(s.value, c.value, *y.value)
        fig.set_size_inches(12, 6)
        display(fig)
b.on_click(upd)
upd()

widgets.VBox([
    widgets.HBox([y, s, c, b]),
    o])
```

[nbd]: # "docs"
# Compare different areas

We will now turn to comparing diffent areas in a cross-section. Function `compute_agr(y0, y1)` calculates average annual growth rate of population and employment in every area between `y0` and `y1`. Average growth rate of variable $x_t$ between years $s$ and $t$ is calculated as $x_{agr} = \left(\frac{x_t}{x_s}\right)^{\frac{1}{t-s+1}}$. Every area is also labelled according as `pop+ emp+`, `pop+ emp-`, `pop- emp+` and `pop- emp-` using two growth measures: absolute percentage growth and relative to reference geographic area.

`color_from_agr_cat(df, abs_rel)` returns a column of HEX color codes useful for plotting.

```{code-cell} ipython3
#nbd module
def compute_agr(y0, y1):
    d = DF['by year'].query('year == @y0 or year == @y1').set_index(['st', 'cty', 'year'])[['pop', 'emp']].unstack('year')
    d = d[(d.notna() & (d > 0)).all(1)]
    d = d.stack(0)
    d = np.power(d[y1] / d[y0], 1/(y1-y0+1)).unstack().add_suffix('_agr_abs')
    d = (d - 1) * 100
    d = d.reset_index()

    d1 = d.query('cty == "000"').rename(columns={'pop_agr_abs': 'ref_pop_agr', 'emp_agr_abs': 'ref_emp_agr'})
    d = d.merge(d1.drop(columns='cty'), 'left')
    d.loc[d['cty'] == '000', ['ref_pop_agr', 'ref_emp_agr']] = d.loc[d['st'] == '00', ['ref_pop_agr', 'ref_emp_agr']].values
    d['pop_agr_rel'] = d['pop_agr_abs'] - d['ref_pop_agr']
    d['emp_agr_rel'] = d['emp_agr_abs'] - d['ref_emp_agr']

    for abs_rel in ['abs', 'rel']:
        e = d['emp_agr_' + abs_rel]
        p = d['pop_agr_' + abs_rel]
        x = pd.Series(index=d.index, dtype='str')
        x[(p >= 0) & (e >= 0)] = 'pop+ emp+'
        x[(p >= 0) & (e <  0)] = 'pop+ emp-'
        x[(p <  0) & (e >= 0)] = 'pop- emp+'
        x[(p <  0) & (e <  0)] = 'pop- emp-'
        d['agr_cat_' + abs_rel] = x
    
    return d
```

```{code-cell} ipython3
#nbd module
agr_colors = {
    'pop+ emp+': '#d95f02',
    'pop+ emp-': '#1b9e77',
    'pop- emp+': '#e7298a',
    'pop- emp-': '#7570b3'
}     

def color_from_agr_cat(df, abs_rel):       
    return df['agr_cat_' + abs_rel].map(agr_colors)
```

```{code-cell} ipython3
#nbd docs
d = compute_agr(2000, 2010)
d['c'] = color_from_agr_cat(d, 'abs')
d.head()
```

[nbd]: # "docs"
As with dynamics plot, `plot_agr(st, y0, y1, abs_rel)` can be used to generate figures with state or county average growth rates as a scatterplot.

```{code-cell} ipython3
#nbd module
def plot_agr(st, y0, y1, abs_rel):
    d = compute_agr(y0, y1)
    if st == '00':
        d = d.query('st != "00" and cty == "000"')
        where = 'states'
        if abs_rel == 'rel':
            where += ' (relative to USA)'
    else:
        d = d.query('st == @st')
        name = DF['geo'].query('st == @st and cty == "000"')['name'].iloc[0]
        where = f'{name} counties'
        if abs_rel == 'rel':
            where += ' (relative to state)'
    d = d.copy()
    d['cat'] = color_from_agr_cat(d, abs_rel)

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.close()
    
    d.plot.scatter(f'pop_agr_{abs_rel}', f'emp_agr_{abs_rel}', ax=ax, c='cat')
    xlim = abs(max(ax.get_xlim(), key=abs))
    ax.set_xlim(-xlim, xlim)
    ylim = abs(max(ax.get_ylim(), key=abs))
    ax.set_ylim(-ylim, ylim)
    ax.axvline(0, ls='-')
    ax.axhline(0, ls='-')
    if abs_rel == 'abs':
        ax.axvline(d['ref_pop_agr'].iloc[0], ls=':')
        ax.axhline(d['ref_emp_agr'].iloc[0], ls=':')
        
    ax.set_title(f'Average growth rate in {where}, {y0}-{y1}')
    ax.set_xlabel('Population')
    ax.set_ylabel('Employment')
    
    return fig
```

```{code-cell} ipython3
#nbd docs
plot_agr('55', 2005, 2015, 'rel')
```

We can again use widgets to explore the results more interactively.

```{code-cell} ipython3
y = widgets.IntRangeSlider(value=(2005, 2015), min=1990, max=2019)
s, _ = st_cty_selectors()
r = widgets.RadioButtons(options=[('Absolute', 'abs'), ('Relative', 'rel')])
o = widgets.Output()
b = widgets.Button(description='Update')
def upd(*_):
    with o:
        o.clear_output(True)
        fig = plot_agr(s.value, *y.value, r.value)
        display(fig)
b.on_click(upd)
upd()

widgets.VBox([
    widgets.HBox([y, s, r, b]),
    o])
```

If only we could show all these dots on a map...

+++

[nbd]: # "docs"
# Map

Python package [ipyleaflet](https://ipyleaflet.readthedocs.io) is a wrapper around `Leaflet.js` and can generate customizable maps. Map objects are also Jupyter widgets, and so we can mix and match them with all other widgets and layout.

It is helpful to wrap map widget in a class `Map` that stores map state and exposes interaction via `click_callback` and `upd()` methods.

```{code-cell} ipython3
#nbd module
class Map:
    def __init__(self, click_callback=None):
        self.widget = leaflet.Map(center=(40, -95), zoom=4)
        self.widget.add_control(leaflet.LegendControl(agr_colors, position='topright'))
        if click_callback is None:
            self.click_callback = self.dummy_callback
        else:
            self.click_callback = click_callback
        
    @staticmethod
    def dummy_callback(**kw):
        pass

    @staticmethod
    def area_gdf(st, y0, y1, abs_rel):
        if st == '00':
            df = DF['geo'].query('cty == "000"')
        else:
            df = DF['geo'].query('st == @st')

        df = df.merge(compute_agr(y0, y1))
        df['color'] = color_from_agr_cat(df, abs_rel)
        df = df[['st', 'cty', 'name', 'geometry', 'color']]
        return df
    
    @staticmethod
    def area_style(feature):
        style = dict(fillColor=feature['properties']['color'])
        return style
    
    def upd(self, st, y0, y1, abs_rel):
        # ipyleaflet.GeoData is a natural choice for area layer, but it does not support style_callback()
        # so we use ipyleaflet.GeoJSON instead
        # proposed fix: https://github.com/jupyter-widgets/ipyleaflet/pull/786
        gdf = self.area_gdf(st, y0, y1, abs_rel)
        layer = leaflet.GeoJSON(data=json.loads(gdf.to_json()),
                        style={'stroke': False, 'fillOpacity': 0.6},
                        hover_style={'stroke': True},
                        style_callback=self.area_style)
        layer.on_click(self.click_callback)
    
        if len(self.widget.layers) == 2:
            self.widget.remove_layer(self.widget.layers[1])
        self.widget.add_layer(layer)
        
```

```{code-cell} ipython3
m = Map()
m.upd('00', 2005, 2015, 'rel')
m.widget
```

```{code-cell} ipython3
def print_area_id(**kw):
    p = kw['properties']
    print(p['st'], p['cty'], p['name'])
m.click_callback = print_area_id
m.upd('55', 2005, 2015, 'rel')
```

+++ {"tags": []}

# Build this module

```{code-cell} ipython3
nbd.nb2mod('analysis.ipynb')
```
