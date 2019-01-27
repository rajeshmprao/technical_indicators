# -*- coding: utf-8 -*-

"""High Low of period indicator"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values

from datetime import timedelta
def high_low(script, from_date, to_date, days = 250):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)
    price_df["{} High".format(days)] = price_df["High"].rolling(window = days).max()
    price_df["{} Low".format(days)] = price_df["Low"].rolling(window = days).min()
    return price_df[['Close', "{} High".format(days), "{} Low".format(days)]]