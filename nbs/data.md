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
:tags: []

---
title: "Retrieve and prepare data"
format:
  html: 
    code-fold: true
    ipynb-filters:
      - popemp/tools.py filter-docs
---
```

+++ {"tags": ["nbd-docs"]}

In this module we download, process and store geographic shapes, population and employment data from US Census Bureau.

```{code-cell} ipython3
:tags: [nbd-module]

import io

import numpy as np
import pandas as pd
import geopandas
import matplotlib.pyplot as plt

from popemp.tools import Nbd, download_file

nbd = Nbd('popemp')
data_dir = nbd.root/'data'
```

+++ {"tags": ["nbd-docs"]}

# Geography

We need state and county FIPS codes and names, and their shapes for map visualizations. Here we use [2018 Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.2018.html) - simplified representations of selected geographic areas from the Census Bureau’s MAF/TIGER geographic database. These boundary files are specifically designed for small scale thematic mapping.

Function `geo()` downloads state and county 1:20,000,000 shapefiles using [geopandas](https://geopandas.org) library, reshapes and combines them into single a GeoDataFrame. We use county code `"000"` as indicator of state rows. Resulting dataframe is cached on disk as a binary `pickle` file, and when subsequent calls of `geo()` will simply read and return the dataframe from cache to save time and avoid work. Delete `data/geo.pkl` if you want to re-create the dataframe, for example, after you changed the function. Similarly, `download_file()` also caches files on disk.

```{code-cell} ipython3
:tags: [nbd-module]

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
```

+++ {"tags": ["nbd-docs"]}

This is the top of the dataframe.

```{code-cell} ipython3
:tags: [nbd-docs]

geo().head()
```

+++ {"tags": ["nbd-docs"]}

`geopandas` stores shapes as [shapely](https://shapely.readthedocs.io) polygons in the `geometry` column. You can perform various geometric operations with these objects, refer to `geopandas` and `shapely` documentation. For example, let's select and plot all states that cross the band between -120 and -110 degrees of longitude, roughly US Pacific coast.

```{code-cell} ipython3
:tags: [nbd-docs]

d = geo().cx[-120:-110, :].query('cty == "000"')
d.plot();
```

+++ {"tags": ["nbd-docs"]}

Be mindful of Coordinate Reference System ([CRS](https://en.wikipedia.org/wiki/Spatial_reference_system)) when working with shapefiles. If you combine shapefiles from multiple sources, make sure to align their CRS's. Census shapefiles come in `EPSG:4269`. The same map in "Spherical Mercator" (`EPSG:3857`, used in Google Maps) will look like this.

```{code-cell} ipython3
:tags: [nbd-docs]

d.to_crs(epsg=3857).plot();
```

+++ {"tags": ["nbd-docs"]}

# Population

We are using annual state and county population 1990-2019 from Census Population Estimates Program ([PEP](https://www.census.gov/programs-surveys/popest.html)). Data are available in 10 year blocks for [2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html), [2000-2010](https://www.census.gov/data/datasets/time-series/demo/popest/intercensal-2000-2010-counties.html) and [1990-1999](https://www2.census.gov/programs-surveys/popest/tables/1990-2000/).

Note on [character encoding](https://www.census.gov/programs-surveys/geography/technical-documentation/user-note/special-characters.html) of plain text files, including CSV: newer files use `"UTF-8"`, older use `"ISO-8859-1"`.

Post-2000 files are simple CSV tables. Functions `pop_2010_2019()` and `pop_2000_2009()` download and read them into dataframes with minor manipulation.

```{code-cell} ipython3
:tags: [nbd-module]

def pop_2010_2019():
    f = download_file('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv', data_dir)
    cols = ['STATE', 'COUNTY'] + [f'POPESTIMATE{y}' for y in range(2010, 2020)]
    df = pd.read_csv(f, encoding='ISO-8859-1', dtype='str', usecols=cols)
    df = pd.wide_to_long(df, 'POPESTIMATE', ['STATE', 'COUNTY'], 'year')
    df = df.reset_index().rename(columns={'STATE': 'st', 'COUNTY': 'cty', 'POPESTIMATE': 'pop'})
    df['pop'] = df['pop'].astype('int')
    return df
```

```{code-cell} ipython3
:tags: [nbd-module]

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
```

+++ {"tags": ["nbd-docs"]}

1990-1999 data are in a long text file. `pop_1990_1999()` does some more elaborate parsing. Table with state and county population has `"1"` as the first character in every line. We use this to read necessary lines into a temporary string buffer, and then parse the buffer into a dataframe.

```{code-cell} ipython3
:tags: [nbd-module]

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
```

+++ {"tags": ["nbd-docs"]}

Finally, in `pop()` we call the three above functions to create three frames, combine them and add aggregated rows of national totals with state code `"00"` and county code `"000"`. We also compute year-to-year growth rate in percentage points in column `pop_gr`. Final dataframe is pickled for easy access.

```{code-cell} ipython3
:tags: [nbd-module]

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
```

```{code-cell} ipython3
:tags: [nbd-docs]

pop().head()
```

+++ {"tags": ["nbd-docs"]}

Quick visual inspection of the data reveals an abnormal population jump between 1999 and 2000. It is clear on national and state level, but not so on county level. I could not find out the cause, but it is most likely a data artifact. This is something to be aware of, but it does not matter for the purposes of this project.

```{code-cell} ipython3
:tags: [nbd-docs]

d = pop().set_index('year')
fig, ax = plt.subplots(1, 3, figsize=(16, 4))
d.query('st == "00" and cty == "000"')['pop'].plot(ax=ax[0])
ax[0].set_title('National')
d.query('st == "55" and cty == "000"')['pop'].plot(ax=ax[1])
ax[1].set_title('Wisconsin')
d.query('st == "55" and cty == "025"')['pop'].plot(ax=ax[2])
ax[2].set_title('Wisconsin, Dane county');
```

+++ {"tags": ["nbd-docs"]}

# Employment

State and county employment comes from Census Business Dynamics Statistics ([BDS](https://www.census.gov/programs-surveys/bds.html)). This product has some improvements over more widely used County Business Patterns, and entire history can be downloaded in a single table from [here](https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html).

Data does not require much processing which is done in the `emp()`. National, state and county tables are downloaded and combined, again using convention of setting state to `"00"` for national and county to `"000"` for national and state rows. Percentage year-to-year growth rate is renamed from `net_job_creation_rate` to `emp_gr`. Data goes back to 1978, but we only need from 1990 for combination with population.

```{code-cell} ipython3
:tags: [nbd-module]

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
```

```{code-cell} ipython3
:tags: [nbd-docs]

emp().head()
```

```{code-cell} ipython3
:tags: [nbd-docs]

d = emp().set_index('year')
fig, ax = plt.subplots(1, 3, figsize=(16, 4))
d.query('st == "00" and cty == "000"')['emp'].plot(ax=ax[0])
ax[0].set_title('National')
d.query('st == "55" and cty == "000"')['emp'].plot(ax=ax[1])
ax[1].set_title('Wisconsin')
d.query('st == "55" and cty == "025"')['emp'].plot(ax=ax[2])
ax[2].set_title('Wisconsin, Dane county');
```

+++ {"tags": ["nbd-docs"]}

# API

Here is a little demo of retrieving a table from a data provider using API. We are not going to use it in this project, because bulk data download as readily available as CSV files, and API access rates are often limited and may require access key. However for some other data sources API access may be the only option. Another good use case is when whole data is huge, and you are building a web app (dashboard) that only needs to pull small pieces of data at a time.

Here I show how to query a portion of the BDS dataset from [Census Bureau API](https://www.census.gov/data/developers/guidance.html). Most of Census data products can be accessed like this, and BDS specific documentation is [here](https://www.census.gov/data/developers/data-sets/business-dynamics.html) with some query examples [there](https://api.census.gov/data/timeseries/bds/examples.html).

Typically, to use an API you need to submit a HTTP request and receive back a response. Request queries are customized by chanding parameters of the URL string, and responses return data in JSON, XML or some other format. Python [requests](https://docs.python-requests.org) library hides a lot of technical details and is easy to use. When you are constructing your query URL, you can also just open it in a browser for a quick preview.

Here is a query line that will pull employment data for all counties in Wisconsin from 2015 to 2019.
```
https://api.census.gov/data/timeseries/bds?get=NAME,ESTAB,EMP,YEAR&for=county:*&in=state:55&time=from+2015+to+2019&NAICS=00&key=YOUR_KEY_GOES_HERE
```

Everything to the left of `?` is the base URL or endpoint: `https://api.census.gov/data/timeseries/bds`.

Everything to the right are key-value parameter pairs, separated by `&`:  
`get=NAME,ESTAB,EMP,YEAR` *data columns*  
`for=county:*` *all counties*  
`in=state:55` *state FIPS code "55" for Wisconsin*  
`time=from+2015+to+2019` *time series range*  
`NAICS=00` *"00" for economy-wide employment*  
`key=YOUR_KEY_GOES_HERE` *drop this part if you don't have a key*

Query limits:
> You can include up to 50 variables in a single API query and can make up to 500 queries per IP address per day. More than 500 queries per IP address per day requires that you register for a Census key. That key will be part of your data request URL string.

Querying without a key will probably work for you, unless you are sharing your IP with many other users. You can obtain a key for free, but you should keep it secret and not accidentally share, for example, by hard-coding it in your code or commiting a file. Here I have my key in a text file that is ignored in `.gitignore` and only exists in my local copy of the repo. Another common appoach is to store keys in OS environment variables.

```{code-cell} ipython3
:tags: [nbd-docs]

import requests

p = nbd.root/'census_api_key.txt'
if p.exists():
    key = '&key=' + p.read_text()
else:
    key = ''

base_url = 'https://api.census.gov/data/timeseries/bds'
st = '55'
y0, y1 = 2015, 2019
response = requests.get(f'{base_url}?get=NAME,ESTAB,EMP,YEAR&for=county:*&in=state:{st}&time=from+{y0}+to+{y1}&NAICS=00{key}')
response_body = response.json()
response_body[:5]
```

```{code-cell} ipython3
:tags: [nbd-docs]

df = pd.DataFrame(response_body[1:], columns=response_body[0])
df.query('county == "025"').head()
```

# Build this module

```{code-cell} ipython3
:tags: []

nbd.nb2mod('data.ipynb')
```
