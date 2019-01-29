# -*- coding: utf-8 -*-

"""Framework to backtest on"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..utils import list_dict_to_list, daterange
from ..adjust_values import adjust_values
from nse_bhavcopy_db import select_companies
from ..indicators import price_sma, high_low, wi, cmf, bar_width

from datetime import datetime
import pandas as pd
import _pickle as pickle
import os
# global


cash = 10000000
max_equity = 10000000
max_pos = 20
sl_multiplier = 0.85
slippage_multiplier = 0.01

from_date = datetime(2012, 1, 2)
to_date = datetime(2019, 1, 1)


family = 'nse500'
parent_company = 'LUPIN'
parent_price = adjust_values(parent_company, from_date, to_date)
scripts = list_dict_to_list(select_companies(family))
# scripts = ["ACC"]



########################################################################################

# these functions will be unique for strat. Need to work on how to do this
def hit_sl(pos, date):
    global data
    if(float(data["Price"][pos["Script"]].loc[date, "Close"]) < pos["SL"]):
        return True
    return False

def update_sl(pos, date):
    global data
    global sl_multiplier
    pos["SL"] = max(pos["SL"], sl_multiplier * float(data["Price"][pos["Script"]].loc[date, "Close"]), float(data["Sma"][pos["Script"]].loc[date, "200 MA"]))
    return pos

def create_pos(script, date): # WI CMF 200MA
    global data
    try:
        if float(data["Sma"][script].loc[date, "200 MA"]) <= float(data["Price"][script].loc[date, "Close"]):
            prev_date_index = data["Price"][script].index.get_loc(date)-1
            # print(prev_date_index)
            if prev_date_index != 0:
                prev_date = data["Price"][script].index[prev_date_index]            
                prev_date_cmf = float(data["Cmf"][script].loc[prev_date, "Indicator"])
                cur_cmf = float(data["Cmf"][script].loc[date, "Indicator"])
                cur_wi = float(data["Wi"][script].loc[date, "Indicator"])
                if cur_cmf > 0 and prev_date_cmf < 0 and cur_wi > -20:
                    buy_price = (1+slippage_multiplier/2) *  float(data["Price"][script].loc[date, "Close"])
                    prev_price = float(data["Price"][script].loc[prev_date, "Close"])
                    percent_change = ((buy_price-prev_price)/prev_price)*100
                    if percent_change >= 3:
                        pos = {"Script": script, "Buy Date": date, "Buy Price": buy_price, "Percent Change": percent_change, "SL": max(sl_multiplier * buy_price, float(data["Sma"][script].loc[date, "200 MA"]))} # script, buy date, buy price, percent change, SL, 
                    return pos
        return None
    except:
        print(script, date)
        # raise
        return None


def preprocess(scripts, from_date, to_date):
    data = {}
    data["Price"] = {}
    data["Wi"] = {}
    data["Cmf"] = {}
    data["High Low"] = {}
    data["Sma"] = {}
    viable_scripts = []
    for script in scripts:
        try:
            data["Price"][script] = adjust_values(script, from_date, to_date)
            if len(data["Price"][script]) == 0:
                continue
            temp_sma_200 = price_sma(script, from_date, to_date, 200)
            # temp_sma_100 = sma(script, from_date, to_date, 100)
            # temp_sma_50 = sma(script, from_date, to_date, 50)
            data["Sma"][script] = temp_sma_200
            # data["Sma"][script] = pd.concat([temp_sma_200["Close"], temp_sma_200["200 MA"], temp_sma_100["100 MA"], temp_sma_50["50 MA"]], axis = 1)
            data["Wi"][script] = wi(script, from_date, to_date)
            data["Cmf"][script] = cmf(script, from_date, to_date)
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
        pos["Sell Date"] = date
        pos["Sell Price"] = (1-slippage_multiplier/2) * float(data["Price"][pos["Script"]].loc[date, "Close"])
        pos["PL"] = (pos["Sell Price"] - pos["Buy Price"])*pos["Buy Quantity"]
        cash += pos["Sell Price"] * pos["Buy Quantity"]
        print(pos)
        past_pos.append(pos)
    # if len(to_sell_pos) > 0:
    #     input()
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
        pos["Buy Quantity"] = cash_per_new_pos/float(data["Price"][pos["Script"]].loc[date, "Close"])
        print(pos)
        cash -= cash_per_new_pos
    # if len(final_candidates_pos) > 0:
    #     input()

    cur_pos.extend(final_candidates_pos)
    return
########################################################################################
# Actual Backtest
# preprocess - fetch prices of all stocks and calculate all indicators
data = preprocess(scripts, from_date, to_date) 
# for loop on days to test on
def wi_cmf_testing():
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
        date_list.append(date)
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

    # calculate current equity
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


    # add cur_pos to past_pos
    cur_pos_with_pl = []
    update_past_pos(cur_pos_with_pl, cur_pos, to_date)
    # pickle results.
    to_pickle = {"date_list": date_list, "cash_list":cash_list, "cur_pos":cur_pos_with_pl, "past_pos": past_pos, "equity_list": equity_list, "drawdown_list": drawdown_list}
    if not os.path.exists("results/{}/".format(datetime.now().strftime("%Y-%m-%d"))):
        os.mkdir("results/{}/".format(datetime.now().strftime("%Y-%m-%d")))
    with open("results/{0}/{1}_wi_cmf_15_200sma_sl.p".format(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M")), "wb") as f:
        pickle.dump(to_pickle, f)
    print(todays_equity)
    return
