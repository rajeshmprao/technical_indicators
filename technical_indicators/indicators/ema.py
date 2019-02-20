# -*- coding: utf-8 -*-

"""price, volume and indicator sma"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values

from datetime import timedelta
def price_ema(script, from_date, to_date, days = 50):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)
    price_df["{} MA".format(days)] = price_df["Close"].ewm(span = days).mean()
    
    return price_df[['Close', "{} MA".format(days)]]

# def volume_sma(script, from_date, to_date, days = 50):
#     new_from_date = from_date - timedelta(days = 2*days)
#     price_df = adjust_values(script, new_from_date, to_date)
#     price_df["{} MA".format(days)] = price_df["Volume"].rolling(window = days).mean()
#     return price_df[['Volume', "{} MA".format(days)]]    
    
def indicator_ema(indicator_df, days = 21):
    indicator_df.loc[:, "{} MA".format(days)] = indicator_df["Indicator"].ewm(span = days).mean()
    return indicator_df[["Indicator", "{} MA".format(days)]]

def indicator_wilder_ema(indicator_df, days = 21):
    span_days = 2*days - 1
    indicator_df.loc[:, "{} MA".format(days)] = indicator_df["Indicator"].ewm(span = span_days).mean()
    return indicator_df[["Indicator", "{} MA".format(days)]]
