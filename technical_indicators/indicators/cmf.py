# -*- coding: utf-8 -*-

"""Chaikin Money Flow indicator"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values

from datetime import timedelta
def cmf(script, from_date, to_date, days = 20):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)

    price_df["Money Flow Multiplier"] = ((price_df["Close"] - price_df["Low"]) - (price_df["High"] - price_df["Close"])) / (price_df["High"] - price_df["Low"])
    price_df["Money Flow Volume"] = price_df["Money Flow Multiplier"] * price_df["Volume"]
    price_df["Indicator"] = price_df["Money Flow Volume"].rolling(window = days).sum()/price_df["Volume"].rolling(window = days).sum()
    return price_df[['Close', "Indicator".format(days)]]