# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 14:24:43 2020

@author: oisin
"""


import polars as pl
from datetime import datetime
import pandas as pd


def nominalRates(date_start=None, date_end=None):
    current_year = datetime.today().strftime('%Y')
    csv_archive = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives'
    z = pd.read_html(csv_archive)
    base_url = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives/'
    z = z[3]
    latest_filename = z['Download Archive File'].iloc[-1]
    latest_file_link = fr'{base_url}{latest_filename}'
    archive = pl.read_csv(latest_file_link)
    archive = archive.with_columns(pl.col("Date").str.to_datetime("%m/%d/%y"))
    archive = archive.with_columns(pl.all().exclude(archive.columns[0]).cast(pl.Float64, strict=False))
    cdfs = []
    for year in [x for x in range(2023, int(current_year) + 1)]:
        cdf = pl.read_csv(f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv')
        cdfs.append(cdf)
    current = pl.concat(cdfs, how='diagonal')
    current = current.with_columns(pl.col("Date").str.to_datetime("%m/%d/%Y"))
    current = current.with_columns(pl.all().exclude(current.columns[0]).cast(pl.Float64, strict=False))
    df = pl.concat([current, archive], how='diagonal')
    df = df.rename(lambda name: name.replace(' Month', 'm').replace(' Yr', 'y').replace(' Mo', 'm').lower())
    df = df.sort('date')
    if date_start is not None:
        df = df.filter(pl.col('date') >= pl.lit(date_start).str.to_date())
    if date_end is not None:
        df = df.filter(pl.col('date') <= pl.lit(date_end).str.to_date())
    return df.to_pandas()


