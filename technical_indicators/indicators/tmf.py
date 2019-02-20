# -*- coding: utf-8 -*-

"""Chaikin Money Flow indicator"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..adjust_values import adjust_values
from .ema import indicator_wilder_ema

from datetime import timedelta
import numpy as np
def tmf(script, from_date, to_date, days = 21):
    new_from_date = from_date - timedelta(days = 2*days)
    price_df = adjust_values(script, new_from_date, to_date)
    price_df["Prev Close"] = price_df["Close"].shift()
    price_df = price_df.iloc[1:, :]
    price_df["TRL"] = price_df[["Low", "Prev Close"]].min(axis = 1)
    price_df["TRH"] = price_df[["High", "Prev Close"]].max(axis = 1)
    price_df["AD"] = (((price_df["Close"] - price_df["TRL"]) - (price_df["TRH"] - price_df["Close"])) * price_df["Volume"]/ (price_df["TRH"] - price_df["TRL"]))
    
    exp_AD_df = price_df[["AD"]]
    exp_AD_df.columns = ["Indicator"]
    exp_AD_df = indicator_wilder_ema(exp_AD_df, days = days)
    
    exp_vol_df = price_df[["Volume"]]
    exp_vol_df.columns = ["Indicator"]
    exp_vol_df = indicator_wilder_ema(exp_vol_df, days = days)

    price_df["Indicator"] = ((exp_AD_df["{} MA".format(days)] / exp_vol_df["{} MA".format(days)])).replace((np.inf, -np.inf), (0, 0))

    price_df = price_df[["Close", "Indicator"]]
    return price_df







