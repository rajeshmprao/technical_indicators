# from technical_indicators import adjust_values
# from technical_indicators.indicators import price_sma, indicator_sma, volume_sma, wi, cmf, high_low, bar_width
# from nse_bhavcopy_db import select_companies
# from technical_indicators.utils import list_dict_to_list
# from technical_indicators.backtesting import minervini_testing
# from technical_indicators.backtesting import minervini_live
# from technical_indicators.backtesting import wi_cmf_live
from technical_indicators.backtesting import wi_cmf_experiment

wi_cmf_experiment()
# wi_cmf_live()
# minervini_testing()
# minervini_live()

# presentation()
# from datetime import datetime
# import matplotlib.pyplot as plt
# from_date = datetime(2018, 1, 1)
# to_date = datetime(2019, 1, 25)
# script = 'AJANTPHARM'
# print(list_dict_to_list(select_companies('nse500')))
# print(df.tail())
# df2 = indicator_sma(df)
# print(df2.tail())
# df.to_csv("gg.csv")
