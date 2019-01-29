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
def draw_results(date, equity, cash, drawdown):
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Equity', color=color)
    ax1.plot(date, equity, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:green'
    ax2.set_ylabel('Drawdown', color=color)  # we already handled the x-label with ax1
    ax2.plot(date, drawdown, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    color = 'tab:red'
    ax2.plot(date, cash, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()

def presentation():
    with open('results/2019-01-27/wi_cmf_15_200sma_sl.p', "rb") as f:
        data = pickle.load(f)
    
    date_list = data["date_list"]
    equity_list = [x/100 for x in data["equity_list"]]
    cash_list = data["cash_list"]
    drawdown_list = data["drawdown_list"]
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


    from_date = date_list[0]
    to_date = date_list[-1]
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

    max_drawdown = max(drawdown_list)
    cur_drawdown = drawdown_list[-1]
    cur_cash_pos = cash_list[-1]

    cur_value = equity_list[-1]
    beginning_value = equity_list[0]

    print("Results:")
    print("From Date = {0}\nTo Date = {1}\nTotal Positions = {2}\nProfit Positions = {3}\nLoss Positions = {4}\nWinLoss Ratio = {5}\nAverage Win = {6}\nAverage Loss = {7}\nAverage Win Days = {8}\nAverage Loss Days = {9}\nBeginning Equity = {10}\nFinal Equity = {11}\nMax Drawdown = {12}\nCurrent Drawdown = {13}\nCurrent Cash Percent = {14}\n".format(from_date, to_date, total_pos, profit_pos_number, loss_pos_number, winloss_ratio, avg_profit, avg_loss, avg_profit_days, avg_loss_days, beginning_value, cur_value, max_drawdown, cur_drawdown, cur_cash_pos))

    draw_results(date_list, equity_list, cash_list, drawdown_list)
    return


