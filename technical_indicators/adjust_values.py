# -*- coding: utf-8 -*-

"""Adjust db price and volume for split and bonus"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from nse_bhavcopy_db import select_price, select_split_bonus

import pandas as pd

def adjust_values(script, from_date, to_date):
    price_list = select_price(script, from_date, to_date)
    price_df = pd.DataFrame(price_list)
    price_df.set_index("Date", inplace = True)
    split_bonus_list = select_split_bonus(script, from_date, to_date)
    split_bonus_df = pd.DataFrame(split_bonus_list)
    if len(split_bonus_df) == 0:
        return price_df
    split_bonus_df = split_bonus_df.groupby(['Ex Date']).prod().sort_values(by="Ex Date", ascending = False).reset_index() # takes care of same day split and bonus

    cum_multiplier = 1
    for i, event in split_bonus_df.iterrows():
        temp = (split_bonus_df.loc[i, 'Ex Date'])
        cum_multiplier *= event["Multiplier"]
        if i == len(split_bonus_df)-1:
            price_df.loc[(price_df.index < split_bonus_df.loc[i, 'Ex Date']), ["Close", "High", "Low", "Open"]] *= cum_multiplier
            price_df.loc[(price_df.index < split_bonus_df.loc[i, 'Ex Date']), ["Volume"]] /= cum_multiplier
        else:
            price_df.loc[(price_df.index >= (split_bonus_df.loc[i+1, 'Ex Date'])) & (price_df.index < split_bonus_df.loc[i, 'Ex Date']), ["Close", "High", "Low", "Open"]] *= cum_multiplier
            price_df.loc[(price_df.index >= (split_bonus_df.loc[i+1, 'Ex Date'])) & (price_df.index < split_bonus_df.loc[i, 'Ex Date']), ["Volume"]] /= cum_multiplier

    return price_df