import mplfinance as mpf
import yfinance as yf
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt



data = pdr.get_data_yahoo("005930.KS", start="2023-10-01", end="2023-12-31")
print(data)
# mpf.plot(data, type= "candle")   # mpf.plot(data, type= [line, candle])
mc = mpf.make_marketcolors(up="r", down="b")
s = mpf.make_mpf_style(base_mpf_style='starsandstripes', marketcolors=mc)
mpf.plot(data, type='candle', style=s, volume=True, mav=(5,10,60), savefig='chart.png')
# plt.show()