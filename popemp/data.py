#!/usr/bin/env python
# coding: utf-8

import io

import numpy as np
import pandas as pd
import geopandas
import matplotlib.pyplot as plt

from .tools import Nbd, download_file

nbd = Nbd('popemp')
data_dir = nbd.root/'data'


def geo():
    df_file = data_dir/'geo.pkl'
    if df_file.exists():
        return pd.read_pickle(df_file)
    
    f = download_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip', data_dir)
    df = geopandas.read_file(f)
    df = df.rename(columns={'STATEFP': 'st', 'NAME': 'name'})
    df = df[['st', 'name', 'geometry']]
    df['cty'] = '000'
    st = df

    f = download_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_20m.zip', data_dir)
    df = geopandas.read_file(f)
    df = df.rename(columns={'STATEFP': 'st', 'COUNTYFP': 'cty', 'NAME': 'name_cty'})
    df = df[['st', 'cty', 'name_cty', 'geometry']]
    df = df.merge(st[['st', 'name']], 'left')
    df['name'] = df['name_cty'] + ' county, ' + df['name']
    del df['name_cty']

    df = pd.concat([df, st]).sort_values(['st', 'cty'], ignore_index=True)
    df = df[['st', 'cty', 'name', 'geometry']]
    
    df.to_pickle(df_file)
    return df


def pop_2010_2019():
    f = download_file('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv', data_dir)
    cols = ['STATE', 'COUNTY'] + [f'POPESTIMATE{y}' for y in range(2010, 2020)]
    df = pd.read_csv(f, encoding='ISO-8859-1', dtype='str', usecols=cols)
    df = pd.wide_to_long(df, 'POPESTIMATE', ['STATE', 'COUNTY'], 'year')
    df = df.reset_index().rename(columns={'STATE': 'st', 'COUNTY': 'cty', 'POPESTIMATE': 'pop'})
    df['pop'] = df['pop'].astype('int')
    return df


def pop_2000_2009():
    f = download_file('https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/county/co-est00int-tot.csv', data_dir)
    cols = ['STATE', 'COUNTY'] + [f'POPESTIMATE{y}' for y in range(2000, 2010)]
    df = pd.read_csv(f, encoding='ISO-8859-1', dtype='str', usecols=cols)
    df = pd.wide_to_long(df, 'POPESTIMATE', ['STATE', 'COUNTY'], 'year')
    df = df.reset_index().rename(columns={'STATE': 'st', 'COUNTY': 'cty', 'POPESTIMATE': 'pop'})
    df['st'] = df['st'].str.pad(2, fillchar='0')
    df['cty'] = df['cty'].str.pad(3, fillchar='0')
    df['pop'] = df['pop'].astype('int')
    return df


def pop_1990_1999():
    f = download_file('https://www2.census.gov/programs-surveys/popest/tables/1990-2000/estimates-and-change-1990-2000/2000c8_00.txt', data_dir)
    with open(f, encoding='ISO-8859-1') as file:
        data = io.StringIO()
        in_table = False
        for line in file:
            if in_table:
                if line[0] == '1':
                    data.write(line)
                else:
                    break
            else:
                if line[0] == '1':
                    in_table = True
                    data.write(line)

    data.seek(0)
    df = pd.read_fwf(data, dtype='str', header=None)
    # skip first row (US total), keep fips and popest cols
    df = df.iloc[1:, 1:13]
    df.columns = ['fips'] + [f'pop{y}' for y in range(2000, 1989, -1)]
    df['fips'] = df['fips'].str.pad(5, 'right', '0')
    df['st'] = df['fips'].str[:2]
    df['cty'] = df['fips'].str[2:]
    df = df.drop(columns=['pop2000', 'fips'])
    df = pd.wide_to_long(df, 'pop', ['st', 'cty'], 'year')
    df = df.reset_index()
    df['pop'] = pd.to_numeric(df['pop'].str.replace(',', '', regex=False)).astype('int')

    return df


def pop():
    df_file = data_dir/'pop.pkl'
    if df_file.exists():
        return pd.read_pickle(df_file)
    
    d1 = pop_1990_1999()
    d2 = pop_2000_2009()
    d3 = pop_2010_2019()
    df = pd.concat([d1, d2, d3], ignore_index=True)

    d = df.query('cty == "000"').groupby('year')['pop'].sum()
    d = d.to_frame('pop').reset_index()
    d[['st', 'cty']] = ['00', '000']
    df = pd.concat([df, d], ignore_index=True)

    df = df.sort_values('year')
    df['pop_'] = df.groupby(['st', 'cty'])['pop'].shift()
    df['pop_gr'] = df.eval('(pop / pop_ - 1) * 100')
    del df['pop_']

    df = df.sort_values(['st', 'cty', 'year']).reset_index()
    df = df[['st', 'cty', 'year', 'pop', 'pop_gr']]

    df.to_pickle(df_file)
    return df


def emp():
    df_file = data_dir/'emp.pkl'
    if df_file.exists():
        return pd.read_pickle(df_file)    
    
    # economy-wide
    f = download_file('https://www2.census.gov/programs-surveys/bds/tables/time-series/bds2019.csv', data_dir)
    df = pd.read_csv(f, usecols=['year', 'emp', 'net_job_creation_rate'], dtype='str')
    df[['st', 'cty']] = ['00', '000']
    d1 = df

    # by state
    f = download_file('https://www2.census.gov/programs-surveys/bds/tables/time-series/bds2019_st.csv', data_dir)
    df = pd.read_csv(f, usecols=['year', 'st', 'emp', 'net_job_creation_rate'], dtype='str')
    df['cty'] = '000'
    d2 = df

    # by county
    f = download_file('https://www2.census.gov/programs-surveys/bds/tables/time-series/bds2019_cty.csv', data_dir)
    df = pd.read_csv(f, usecols=['year', 'st', 'cty', 'emp', 'net_job_creation_rate'], dtype='str')

    df = pd.concat([d1, d2, df])
    df = df.rename(columns={'net_job_creation_rate': 'emp_gr'})
    df['year'] = df['year'].astype('int16')
    df['emp'] = pd.to_numeric(df['emp'], 'coerce')
    df['emp_gr'] = pd.to_numeric(df['emp_gr'], 'coerce')
    df = df[['st', 'cty', 'year', 'emp', 'emp_gr']]
    df = df.query('year >= 1990').reset_index(drop=True)
    
    df.to_pickle(df_file)
    return df

