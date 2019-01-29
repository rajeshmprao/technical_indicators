# -*- coding: utf-8 -*-

"""Framework to backtest on"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..utils import list_dict_to_list, daterange, get_closest_date
from ..adjust_values import adjust_values
from nse_bhavcopy_db import select_companies
from ..indicators import price_sma, high_low, bar_width, indicator_sma
from datetime import datetime
import pandas as pd
import _pickle as pickle
import os
# global


cash = 200000
max_equity = 200000
max_pos = 20
sl_multiplier = 0.85
slippage_multiplier = 0.01

from_date = datetime(2012, 1, 1)
to_date = datetime(2013, 1, 1)


family = 'nse500'
parent_company = 'LUPIN'
parent_price = adjust_values(parent_company, from_date, to_date)
scripts = list_dict_to_list(select_companies(family))
# scripts = ["ACC"]



########################################################################################

# these functions will be unique for strat. Need to work on how to do this
# if date not in parent index, 
# get previous closest number

def hit_sl(pos, date):
    global data
    try:
        correct_date = get_closest_date(date, data["Price"][pos["Script"]])
        if(float(data["Price"][pos["Script"]].loc[correct_date, "Close"]) < pos["SL"]):
            return True
        return False
    except:
        print("HIT SL: {0}, {1}".format(date, pos["Script"]))
        raise
        return False

def update_sl(pos, date):
    global data
    global sl_multiplier
    try:
        correct_date = get_closest_date(date, data["Price"][pos["Script"]])
        pos["SL"] = max(pos["SL"], sl_multiplier * float(data["Price"][pos["Script"]].loc[correct_date, "Close"]), float(data["Sma"][pos["Script"]].loc[correct_date, "200 MA"]))
        return pos
    except:
        print("UPDATE SL: {0}, {1}".format(date, pos["Script"]))
        raise
        return pos

def create_pos(script, date): # minervini
    global data
    try:
        correct_date = get_closest_date(date, data["Price"][script])
        if correct_date == None:
            return None
        prev_date_index = data["Price"][script].index.get_loc(correct_date)-1
        if prev_date_index != 0:
            prev_date = data["Price"][script].index[prev_date_index]
            if float(data["Sma"][script].loc[correct_date, "200 MA"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and float(data["Sma"][script].loc[correct_date, "150 MA"]) <= float(data["Price"][script].loc[correct_date, "Close"])and float(data["Sma"][script].loc[correct_date, "200 MA"]) <= float(data["Sma"][script].loc[correct_date, "150 MA"])and float(data["Sma"][script].loc[correct_date, "150 MA"]) <= float(data["Sma"][script].loc[correct_date, "50 MA"]) and float(data["Sma"][script].loc[correct_date, "200 MA"]) <= float(data["Sma"][script].loc[correct_date, "50 MA"]) and 1.2 * float(data["High Low"][script].loc[correct_date, "250 Low"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and float(data["High Low"][script].loc[correct_date, "250 High"]) <= 1.25 * float(data["Price"][script].loc[correct_date, "Close"]) and float(data["Sma"][script].loc[correct_date, "50 MA"]) <= float(data["Price"][script].loc[correct_date, "Close"]) and data["Bar Width"][script].loc[correct_date, "50 MA"] >= data["Bar Width"][script].loc[correct_date, "21 MA"] and data["Bar Width"][script].loc[correct_date, "21 MA"] >= data["Bar Width"][script].loc[correct_date, "10 MA"] and data["Bar Width"][script].loc[correct_date, "50 MA"] >= data["Bar Width"][script].loc[correct_date, "10 MA"] and data["Bar Width"][script].loc[correct_date, "Indicator"] <= data["Bar Width"][script].loc[correct_date, "10 MA"]:
                buy_price = (1+slippage_multiplier/2) *  float(data["Price"][script].loc[correct_date, "Close"])
                prev_price = float(data["Price"][script].loc[prev_date, "Close"])
                percent_change = ((buy_price-prev_price)/prev_price)*100
                pos = {"Script": script, "Buy Date": correct_date, "Buy Price": buy_price, "Percent Change": percent_change, "SL": max(sl_multiplier * buy_price, float(data["Sma"][script].loc[correct_date, "200 MA"]))} # script, buy date, buy price, percent change, SL, 
                return pos
        return None            
    except:
        print("CREATE POS")
        print(script, date)
        raise
        return None


def preprocess(scripts, from_date, to_date):
    data = {}
    data["Price"] = {}
    data["High Low"] = {}
    data["Sma"] = {}
    data["Bar Width"] = {}
    viable_scripts = []
    for script in scripts:
        try:
            data["Price"][script] = adjust_values(script, from_date, to_date)
            if len(data["Price"][script]) == 0:
                continue
            temp_sma_200 = price_sma(script, from_date, to_date, 200)
            temp_sma_150 = price_sma(script, from_date, to_date, 150)
            temp_sma_50 = price_sma(script, from_date, to_date, 50)
            data["Sma"][script] = pd.concat([temp_sma_200["Close"], temp_sma_200["200 MA"], temp_sma_150["150 MA"], temp_sma_50["50 MA"]], axis = 1)

            temp_bar_width = bar_width(script, from_date, to_date)
            bar_sma_50 = indicator_sma(temp_bar_width, 50)
            bar_sma_21 = indicator_sma(temp_bar_width, 21)
            bar_sma_10 = indicator_sma(temp_bar_width, 10)
            data["Bar Width"][script] = pd.concat([temp_bar_width["Indicator"], bar_sma_50["50 MA"], bar_sma_21["21 MA"], bar_sma_10["10 MA"]], axis = 1)
            data["High Low"][script] = high_low(script, from_date, to_date) 
            viable_scripts.append(script)
        except:
            input(script)
            raise
    scripts = viable_scripts
    return data

def update_past_pos(past_pos, to_sell_pos, date):
    global data
    global slippage_multiplier
    global cash
    if len(to_sell_pos) > 0:
        print("Sell:")
    for pos in to_sell_pos:
        try:
            correct_date = get_closest_date(date, data["Price"][pos["Script"]])
            pos["Sell Date"] = correct_date
            pos["Sell Price"] = (1-slippage_multiplier/2) * float(data["Price"][pos["Script"]].loc[correct_date, "Close"])
            pos["PL"] = (pos["Sell Price"] - pos["Buy Price"])*pos["Buy Quantity"]
            cash += pos["Sell Price"] * pos["Buy Quantity"]
            print(pos)
            past_pos.append(pos)
        except:
            print(date, "UPDATE PAST POS")
            raise
    if len(to_sell_pos) > 0:
        input()
    return
    

def add_new_pos(date, cur_pos, viable_candidates_pos):
    global data
    global cash 
    global max_pos   
    open_slots = max_pos - len(cur_pos)
    if open_slots == 0:
        return
    cash_per_new_pos = cash/open_slots
    viable_candidates_pos[:] = [x for x in viable_candidates_pos if x["Script"] not in [y["Script"] for y in cur_pos]]
    viable_candidates_pos.sort(key = lambda x:x["Percent Change"], reverse = True)
    final_candidates_pos = viable_candidates_pos[:open_slots]
    if len(final_candidates_pos) > 0:
        print("Buy")
    for pos in final_candidates_pos:
        correct_date = get_closest_date(date,  data["Price"][pos["Script"]])
        pos["Buy Quantity"] = cash_per_new_pos/float(data["Price"][pos["Script"]].loc[correct_date, "Close"])
        print(pos)
        cash -= cash_per_new_pos
    if len(final_candidates_pos) > 0:
        input()

    cur_pos.extend(final_candidates_pos)
    return
########################################################################################
# Actual Backtest
# preprocess - fetch prices of all stocks and calculate all indicators
data = preprocess(scripts, from_date, to_date) 
# for loop on days to test on
def minervini_live():
    cur_pos = []
    past_pos = []
    equity_list = []
    drawdown_list = []
    cash_list = []
    date_list = []
    global max_equity
    global cash
    for date in daterange(from_date, to_date):
        if date not in parent_price.index: #holiday, can skip
            continue
    #   before testing todays outcome - calculate current equity, cash, drawdown etc
        print(date)

    #   take selling decisions for today - sl
        to_sell_pos = [pos for pos in cur_pos if hit_sl(pos, date)]
        update_past_pos(past_pos, to_sell_pos, date) # Past Pos gets updated
        cur_pos[:] = [update_sl(pos, date) for pos in cur_pos if not hit_sl(pos, date)] #cur pos gets updated

    #   select viable candidates to buy
        viable_candidate_pos = []
        for script in scripts:
            pos = create_pos(script, date)
            if pos != None:
                viable_candidate_pos.append(pos)

    #   rank and position size viable candidates and buy them
        add_new_pos(date, cur_pos, viable_candidate_pos) # cur pos gets updated
        try:
        # calculate current equity
            date_list.append(date)
            todays_equity = sum([x["Buy Quantity"] * float(data["Price"][x["Script"]].loc[date, "Close"]) for x in cur_pos]) + cash
            equity_list.append(todays_equity)

            # calculate current drawdown
            if todays_equity > max_equity:
                max_equity = todays_equity
            todays_drawdown = (1 - todays_equity/max_equity)*100
            drawdown_list.append(todays_drawdown)

            # calculate current cash levels
            todays_cash_level = (cash/todays_equity)*100
            cash_list.append(todays_cash_level)
        except:
            pass



    # add cur_pos to past_pos
    cur_pos_with_pl = []
    # update_past_pos(cur_pos_with_pl, cur_pos, to_date)
    # pickle results.
    to_pickle = {"date_list": date_list, "cash_list":cash_list, "cur_pos":cur_pos_with_pl, "past_pos": past_pos, "equity_list": equity_list, "drawdown_list": drawdown_list}
    if not os.path.exists("results/{}/".format(datetime.now().strftime("%Y-%m-%d"))):
        os.mkdir("results/{}/".format(datetime.now().strftime("%Y-%m-%d")))
    with open("results/{0}/{1}_minervini_15_200sma_sl.p".format(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M")), "wb") as f:
        pickle.dump(to_pickle, f)
    print(todays_equity)
    return
