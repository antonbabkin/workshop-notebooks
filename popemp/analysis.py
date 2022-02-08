#!/usr/bin/env python
# coding: utf-8

import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
import ipyleaflet as leaflet

from .tools import Nbd
from . import data
nbd = Nbd('popemp')


DF = {}

def prep_data():
    DF['geo'] = data.geo()
    DF['by year'] = data_by_year()


def data_by_year():
    df = data.pop().merge(data.emp(), 'left').query('pop.notna() and emp.notna()')
    return df


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


def color_from_agr_cat(df, abs_rel):
    m = {
        'pop+ emp+': 'red',
        'pop+ emp-': 'green',
        'pop- emp+': 'orange',
        'pop- emp-': 'blue'
    }        
    return df['agr_cat_' + abs_rel].map(m)


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


class Map:
    def __init__(self, click_callback=None):
        self.widget = leaflet.Map(center=(40, -95), zoom=4)
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
                        style={'stroke': False, 'fillOpacity': 0.5},
                        hover_style={'stroke': True},
                        style_callback=self.area_style)
        layer.on_click(self.click_callback)
    
        if len(self.widget.layers) == 2:
            self.widget.remove_layer(self.widget.layers[1])
        self.widget.add_layer(layer)
        

