# -*- coding: utf-8 -*-

"""Framework to Present  results from pickle on"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

import pickle
import matplotlib.pyplot as plt
from technical_indicators.utils import DateTimeAwareEncoder
import pyperclip
import json
import numpy as np

def presentation_experiment():
    with open('results/2019-01-29/wi_cmf_15_200sma_sl_all.p', "rb") as f:
        data = pickle.load(f)
    
    past_pos = data["past_pos"] 
    past_pos.sort(key = lambda x:x["PL"]/(x["Buy Price"] * x["Buy Quantity"]), reverse = True)
    cur_pos = data["cur_pos"]
    cur_pos.sort(key = lambda x:x["PL"]/(x["Buy Price"] * x["Buy Quantity"]), reverse = True)

    past_pos_json = json.dumps(past_pos, cls=DateTimeAwareEncoder)
    pyperclip.copy(past_pos_json)
    input(past_pos_json)
    cur_pos_json = json.dumps(cur_pos, cls=DateTimeAwareEncoder)
    pyperclip.copy(cur_pos_json)
    input(cur_pos_json)


    # from_date = date_list[0]
    # to_date = date_list[-1]
    profit_pos = [x for x in past_pos if x["PL"] >= 0] + [x for x in cur_pos if x["PL"] >= 0]
    loss_pos = [x for x in past_pos if x["PL"] < 0] + [x for x in cur_pos if x["PL"] < 0]
    profit_pos_number = len(profit_pos)
    loss_pos_number = len(loss_pos)
    total_pos = profit_pos_number + loss_pos_number
    winloss_ratio = len(profit_pos)/ (len(profit_pos) + len(loss_pos))
    
    avg_profit = np.mean([x["PL"]/(x["Buy Price"] * x["Buy Quantity"]) for x in profit_pos])
    avg_loss = np.mean([x["PL"]/(x["Buy Price"] * x["Buy Quantity"]) for x in loss_pos])

    avg_profit_days = np.mean([(x["Sell Date"] - x["Buy Date"]).days for x in profit_pos])
    avg_loss_days = np.mean([(x["Sell Date"] - x["Buy Date"]).days for x in loss_pos])

    # max_drawdown = max(drawdown_list)
    # cur_drawdown = drawdown_list[-1]
    # cur_cash_pos = cash_list[-1]

    # cur_value = equity_list[-1]
    # beginning_value = equity_list[0]

    print("Results:")
    print("Total Positions = {0}\nProfit Positions = {1}\nLoss Positions = {2}\nWinLoss Ratio = {3}\nAverage Win = {4}\nAverage Loss = {5}\nAverage Win Days = {6}\nAverage Loss Days = {7}\n".format(total_pos, profit_pos_number, loss_pos_number, winloss_ratio, avg_profit, avg_loss, avg_profit_days, avg_loss_days))

    # draw_results(date_list, equity_list, cash_list, drawdown_list)
    return


