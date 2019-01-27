# -*- coding: utf-8 -*-

"""price, volume and indicator sma"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values

from datetime import timedelta
def price_sma(script, from_date, to_date, days = 200):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)
    price_df["{} MA".format(days)] = price_df["Close"].rolling(window = days).mean()
    
    return price_df[['Close', "{} MA".format(days)]]

def volume_sma(script, from_date, to_date, days = 50):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)
    price_df["{} MA".format(days)] = price_df["Volume"].rolling(window = days).mean()
    return price_df[['Volume', "{} MA".format(days)]]    
    
def indicator_sma(indicator_df, days = 20):
    indicator_df["{} MA".format(days)] = indicator_df["Indicator"].rolling(window = days).mean()
    return indicator_df[["Indicator", "{} MA".format(days)]]