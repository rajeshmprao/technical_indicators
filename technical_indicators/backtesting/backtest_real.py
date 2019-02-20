# -*- coding: utf-8 -*-

"""Framework to backtest on with ml"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from ..utils import daterange
from datetime import datetime
import pandas as pd
import _pickle as pickle
import os
import importlib

# Actual Backtest
# preprocess - fetch prices of all stocks and calculate all indicators
# for loop on days to test on
def backtest_real(from_date, to_date, strategy, file_name, universe = 'nse'):
    strategy = '.'+strategy
    model = importlib.import_module(strategy, 'technical_indicators.backtesting')
    cur_pos = []
    past_pos = []
    
    tot_value_list = []
    cash_percent_list = []
    date_list = []
    drawdown_list = []

    equity = 0
    max_value = 10000000
    cash = 10000000


    data, scripts = model.preprocess(universe, from_date, to_date) 
    for date in daterange(from_date, to_date):
        if date not in data["Parent Price"].index: #holiday, can skip
            continue
        print(date)

    #   take selling decisions for today - sl
    # TODO give it sl hit true if today is last day of trading
        to_sell_pos = [pos for pos in cur_pos if model.hit_sl(data, pos, date)]
        cash = model.update_past_pos_real(data, past_pos, to_sell_pos, date, cash) # Past Pos gets updated
        cur_pos[:] = [model.update_sl(data, pos, date) for pos in cur_pos if not model.hit_sl(data, pos, date)] #cur pos gets updated

    #   select viable candidates to buy
        viable_candidate_pos = []
        for script in scripts:
            # TODO get closest data - modify to ensure stock existed on given date. Also input when today is not traded by stock
            pos = model.create_pos(data, script, date)
            if pos != None:
                viable_candidate_pos.append(pos)

    #   rank and position size viable candidates and buy them
    # TODO add position sizing metrics
        cash = model.add_new_pos_real(data, date, cur_pos, viable_candidate_pos, cash) # cur pos gets updated
        max_value = model.update_parameters(date_list, cash_percent_list, drawdown_list, tot_value_list, cash, max_value, date, cur_pos, data)
    cur_pos_with_pl = []
    cash = model.update_past_pos_real(data, cur_pos_with_pl, cur_pos, to_date, cash)
    # pickle results.
    to_pickle = {"cur_pos":cur_pos_with_pl, "past_pos": past_pos, "date_list": date_list, "cash_percent_list": cash_percent_list, "drawdown_list": drawdown_list, "tot_value_list": tot_value_list}
    if not os.path.exists("results/{}/".format(datetime.now().strftime("%Y-%m-%d"))):
        os.mkdir("results/{}/".format(datetime.now().strftime("%Y-%m-%d")))
    with open("results/{0}/{1}_{2}.p".format(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M"), file_name), "wb") as f:
        pickle.dump(to_pickle, f)
    # print(todays_equity)
    return
