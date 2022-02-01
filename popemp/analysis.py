#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .tools import Nbd
from . import data

nbd = Nbd('popemp')


data_yr = data.pop().merge(data.emp(), 'left')

def data_ag(y0, y1):
    d = data_yr.query('year == @y0 or year == @y1').set_index(['st', 'cty', 'year'])[['pop', 'emp']].unstack('year')
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
    return d

def color_from_gr(df, abs_rel):
    e = df['emp_agr_' + abs_rel]
    p = df['pop_agr_' + abs_rel]
    x = pd.Series(index=df.index, dtype='str')
    x[(p >= 0) & (e >= 0)] = 'red'
    x[(p >= 0) & (e <  0)] = 'green'
    x[(p <  0) & (e >= 0)] = 'orange'
    x[(p <  0) & (e <  0)] = 'blue'
    return x

