# -*- coding: utf-8 -*-

"""Framework to backtest on with ml"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..utils import list_dict_to_list, daterange, get_closest_date
from ..adjust_values import adjust_values
from nse_bhavcopy_db import select_companies
from ..indicators import price_sma, high_low, bar_width, indicator_sma, volume_sma, tmf
from datetime import datetime
import pandas as pd
import _pickle as pickle
import os

sl_multiplier = 0.85
slippage_multiplier = 0.01
max_pos = 20
parent_company = 'LUPIN'



########################################################################################

# these functions will be unique for strat. Need to work on how to do this
def hit_sl(data, pos, date):
    # global data
    try:
        if date != data["Parent Price"].index[-1] and date == data["Price"][pos["Script"]].index[-1]: # last day of back test is an exception
            return True
        correct_date = get_closest_date(date, data["Price"][pos["Script"]], pos["Script"])
        if(float(data["Price"][pos["Script"]].loc[correct_date, "Close"]) < pos["SL"]):
            return True
        
        date_index = data["Price"][pos["Script"]].index.get_loc(correct_date)
        if data["Price"][pos["Script"]]["Close"].iloc[date_index - 1] > data["Price"][pos["Script"]]["Close"].iloc[date_index] and \
        data["Price"][pos["Script"]]["Close"].iloc[date_index - 2] > data["Price"][pos["Script"]]["Close"].iloc[date_index - 1] and \
        data["Volume"][pos["Script"]]["Volume"].iloc[date_index] >= 1.5 * data["Volume"][pos["Script"]]["10 MA"].iloc[date_index] and \
        data["Price"][pos["Script"]]["Close"].iloc[date_index] < data["Sma"][pos["Script"]]["50 MA"].iloc[date_index]:
            return True


        # TODO If past 3 candles are red, with higher volumes than usual, exit
        # elif float(data["Tmf"][pos["Script"]].loc[correct_date, "Indicator"]) < 0:
        #     return True 
        
        return False
    except:
        print(pos, date)
        raise

def update_sl(data, pos, date):
    try:
        # global data
        # global sl_multiplier
        correct_date = get_closest_date(date, data["Price"][pos["Script"]], pos["Script"])
        pos["SL"] = min(max(pos["SL"], sl_multiplier * float(data["Price"][pos["Script"]].loc[correct_date, "Close"])), float(data["Sma"][pos["Script"]].loc[correct_date, "50 MA"]))
        return pos
        
    except:
        print(pos, date)
        raise        

def create_pos(data, script, date): 
    # global data
    try:
        correct_date = get_closest_date(date, data["Price"][script], script)
        if correct_date == None:
            return None
        if float(data["Price"][script].loc[correct_date, "Close"]) * float(data["Volume"][script].loc[correct_date, "Volume"]) > 10000000 and \
        float(data["Volume"][script].loc[correct_date, "Volume"]) <= float(data["Volume"][script].loc[correct_date, "50 MA"]) and \
        float(data["Sma"][script].loc[correct_date, "200 MA"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and \
        float(data["Sma"][script].loc[correct_date, "150 MA"]) <= float(data["Price"][script].loc[correct_date, "Close"])and \
        float(data["Sma"][script].loc[correct_date, "200 MA"]) <= float(data["Sma"][script].loc[correct_date, "150 MA"])and \
        float(data["Sma"][script].loc[correct_date, "150 MA"]) <= float(data["Sma"][script].loc[correct_date, "50 MA"]) and \
        float(data["Sma"][script].loc[correct_date, "200 MA"]) <= float(data["Sma"][script].loc[correct_date, "50 MA"]) and \
        2 * float(data["High Low"][script].loc[correct_date, "250 Low"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and\
        0.75 * float(data["High Low"][script].loc[correct_date, "250 High"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and \
        float(data["Sma"][script].loc[correct_date, "50 MA"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and \
        data["Bar Width"][script].loc[correct_date, "50 MA"] >= data["Bar Width"][script].loc[correct_date, "21 MA"] and \
        data["Bar Width"][script].loc[correct_date, "21 MA"] >= data["Bar Width"][script].loc[correct_date, "10 MA"] and \
        data["Bar Width"][script].loc[correct_date, "50 MA"] >= data["Bar Width"][script].loc[correct_date, "10 MA"] and \
        data["Bar Width"][script].loc[correct_date, "Indicator"] <= data["Bar Width"][script].loc[correct_date, "10 MA"] and \
        float(data["Sma"][script].loc[correct_date, "200 MA"]) >= float(data["Sma"][script]["200 MA"].shift(periods = 20)[correct_date]) and \
        float(data["Sma"][script].loc[correct_date, "200 MA"]) >= float(data["Sma"][script]["200 MA"].shift(periods = 60)[correct_date]) and \
        float(data["Sma"][script]["200 MA"].shift(periods = 20)[correct_date]) >= float(data["Sma"][script]["200 MA"].shift(periods = 60)[correct_date]) and \
        float(data["Tmf"][script].loc[correct_date, "Indicator"]) > 0:
            prev_date_index = data["Price"][script].index.get_loc(correct_date)-1
            if prev_date_index != 0:
                prev_date = data["Price"][script].index[prev_date_index]                            
                buy_price = (1+slippage_multiplier/2) *  float(data["Price"][script].loc[correct_date, "Close"])
                prev_price = float(data["Price"][script].loc[prev_date, "Close"])
                percent_change = ((buy_price-prev_price)/prev_price)*100
                pos = {"Script": script, "Buy Date": correct_date, "Buy Price": buy_price, "Percent Change": percent_change, "SL": min(sl_multiplier * buy_price, float(data["Sma"][script].loc[correct_date, "50 MA"]))} # script, buy date, buy price, percent change, SL, 
                return pos
        return None
    except:
        print(script, date)
        raise
        return None


def preprocess(universe, from_date, to_date):
    scripts = list_dict_to_list(select_companies(universe))
    # scripts = ['MINDTREE']
    data = {}
    parent_price = adjust_values(parent_company, from_date, to_date)
    data["Parent Price"] = parent_price
    data["Price"] = {}
    data["High Low"] = {}
    data["Sma"] = {}
    data["Bar Width"] = {}
    data["Volume"] = {}
    data["Tmf"] = {}
    viable_scripts = []
    for script in scripts:
        try:
            data["Price"][script] = adjust_values(script, from_date, to_date)
            if len(data["Price"][script]) == 0:
                continue
            # TODO code 1, 2, 3 month 200 day offset to check upward slope
            # TODO volume data
            temp_sma_200 = price_sma(script, from_date, to_date, 200)
            temp_sma_150 = price_sma(script, from_date, to_date, 150)
            temp_sma_50 = price_sma(script, from_date, to_date, 50)
            data["Sma"][script] = pd.concat([temp_sma_200["Close"], temp_sma_200["200 MA"], temp_sma_150["150 MA"], temp_sma_50["50 MA"]], axis = 1)
            data["High Low"][script] = high_low(script, from_date, to_date) 
            temp_bar_width = bar_width(script, from_date, to_date)
            bar_sma_50 = indicator_sma(temp_bar_width, 50)
            bar_sma_21 = indicator_sma(temp_bar_width, 21)
            bar_sma_10 = indicator_sma(temp_bar_width, 10)
            data["Bar Width"][script] = pd.concat([temp_bar_width["Indicator"], bar_sma_50["50 MA"], bar_sma_21["21 MA"], bar_sma_10["10 MA"]], axis = 1)
            temp_sma_50 = volume_sma(script, from_date, to_date, days = 50)
            temp_sma_10 = volume_sma(script, from_date, to_date, days = 10)
            data["Volume"][script] = pd.concat([temp_sma_50["Volume"], temp_sma_50["50 MA"], temp_sma_10["10 MA"]], axis = 1)
            data["Tmf"][script] = tmf(script, from_date, to_date, days = 21)
            viable_scripts.append(script)
            print(len(viable_scripts))
        except:
            input(script)
            raise
    scripts = viable_scripts
    return data, viable_scripts

def update_past_pos(data, past_pos, to_sell_pos, date):
    # global data
    # global slippage_multiplier
    # global cash
    if len(to_sell_pos) > 0:
        print("Sell:")
    for pos in to_sell_pos:
        try:
            correct_date = get_closest_date(date, data["Price"][pos["Script"]], pos["Script"])        
            pos["Sell Date"] = correct_date
            pos["Sell Price"] = (1-slippage_multiplier/2) * float(data["Price"][pos["Script"]].loc[correct_date, "Close"])
            pos["PL"] = (pos["Sell Price"] - pos["Buy Price"])*pos["Buy Quantity"]
            # cash += pos["Sell Price"] * pos["Buy Quantity"]
            print(pos)
            past_pos.append(pos)
        except:
            print(date, "UPDATE PAST POS")
            raise  
    # if len(to_sell_pos) > 0:
    #     input()
    return

def update_past_pos_real(data, past_pos, to_sell_pos, date, cash):
    # global data
    # global slippage_multiplier
    # global cash
    if len(to_sell_pos) > 0:
        print("Sell:")
    for pos in to_sell_pos:
        try:
            correct_date = get_closest_date(date, data["Price"][pos["Script"]], pos["Script"])        
            pos["Sell Date"] = correct_date
            pos["Sell Price"] = (1-slippage_multiplier/2) * float(data["Price"][pos["Script"]].loc[correct_date, "Close"])
            pos["PL"] = (pos["Sell Price"] - pos["Buy Price"])*pos["Buy Quantity"]
            cash += pos["Sell Price"] * pos["Buy Quantity"]
            print(pos)

            past_pos.append(pos)
        except:
            print(date, "UPDATE PAST POS")
            raise  
    # if len(to_sell_pos) > 0:
    #     input()
    return cash

def add_new_pos(data, date, cur_pos, viable_candidates_pos):
    # global data
    cash_per_new_pos = 500000
    viable_candidates_pos[:] = [x for x in viable_candidates_pos if x["Script"] not in [y["Script"] for y in cur_pos]]
    viable_candidates_pos.sort(key = lambda x:x["Percent Change"], reverse = True)
    final_candidates_pos = viable_candidates_pos
    if len(final_candidates_pos) > 0:
        print("Buy")
    for pos in final_candidates_pos:
        correct_date = get_closest_date(date,  data["Price"][pos["Script"]], pos["Script"])
        pos["Buy Quantity"] = cash_per_new_pos/float(data["Price"][pos["Script"]].loc[correct_date, "Close"])
        print(pos)
    # if len(final_candidates_pos) > 0:
    #     input()

    cur_pos.extend(final_candidates_pos)
    return

def add_new_pos_real(data, date, cur_pos, viable_candidates_pos, cash):
    # global data
    available_slots = max_pos - len(cur_pos)
    if available_slots == 0:
        return cash
    cash_per_new_pos = cash / available_slots
    viable_candidates_pos[:] = [x for x in viable_candidates_pos if x["Script"] not in [y["Script"] for y in cur_pos]]
    viable_candidates_pos.sort(key = lambda x:x["Percent Change"], reverse = True)
    final_candidates_pos = viable_candidates_pos[:available_slots]
    if len(final_candidates_pos) > 0:
        print("Buy")
    for pos in final_candidates_pos:
        correct_date = get_closest_date(date,  data["Price"][pos["Script"]], pos["Script"])
        pos["Buy Quantity"] = cash_per_new_pos/float(data["Price"][pos["Script"]].loc[correct_date, "Close"])
        cash -= cash_per_new_pos
        print(pos)
    # if len(final_candidates_pos) > 0:
    #     input()

    cur_pos.extend(final_candidates_pos)
    return cash

def update_parameters(date_list, cash_percent_list, drawdown_list, tot_value_list, cash, max_value, date, cur_pos, data):
    try:
        date_list.append(date)
        cur_total_value = 0
        cur_total_value += cash
        for pos in cur_pos:
            correct_date = get_closest_date(date,  data["Price"][pos["Script"]], pos["Script"])
            cur_total_value += pos["Buy Quantity"] * data["Price"][pos["Script"]].loc[correct_date, "Close"]
        
        tot_value_list.append(cur_total_value)
        cash_percent_list.append(cash*100/cur_total_value)
        if cur_total_value > max_value:
            max_value = cur_total_value
        drawdown_list.append((1 - cur_total_value/max_value)*100)
        return max_value
    except:
        print("UPDATE PARAM ERROR")
        raise

