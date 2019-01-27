from technical_indicators import adjust_values
from technical_indicators.indicators import price_sma, indicator_sma, volume_sma, wi, cmf, high_low, bar_width


from datetime import datetime
import matplotlib.pyplot as plt
from_date = datetime(2018, 1, 1)
to_date = datetime(2019, 1, 25)
script = 'AJANTPHARM'
df = volume_sma(script, from_date, to_date)
print(df.tail())
# df2 = indicator_sma(df)
# print(df2.tail())
# df.to_csv("gg.csv")



# fig, ax = plt.subplots()
# ax2 = ax.twinx()
# ax.plot(df["Close"], label="GDP")
# ax2.plot(df["100 MA"], color="C2", label="HoursWorked")

# # ax.set_title('RealGDP and Hours Worked')

# # ax.legend(loc=2)
# plt.show()
# # adjust_values(script, from_date, to_date)