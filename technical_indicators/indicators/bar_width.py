# -*- coding: utf-8 -*-

"""Bar width indicator"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values

from datetime import timedelta
def bar_width(script, from_date, to_date):
    price_df = adjust_values(script, from_date, to_date)
    price_df["Indicator"] = ((price_df["High"] - price_df["Low"]) + abs(price_df["Close"] - price_df["Open"]))/2
    return price_df[['Close', "Indicator"]]