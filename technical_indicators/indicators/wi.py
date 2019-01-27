# -*- coding: utf-8 -*-

"""williams %R indicator"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values

from datetime import timedelta
def wi(script, from_date, to_date, days = 14):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)

    price_df["Highest High"] = price_df["High"].rolling(window = days).max() 
    price_df["Lowest Low"] = price_df["Low"].rolling(window = days).min() 
    price_df["Indicator"] = ((price_df["Highest High"] - price_df["Close"])/(price_df["Highest High"] - price_df["Lowest Low"]))*-100
    return price_df[['Close', "Indicator".format(days)]]