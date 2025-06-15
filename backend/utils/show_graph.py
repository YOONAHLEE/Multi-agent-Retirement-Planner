# backend/utils/show_graph.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def get_kospi_sp500_graph():
    sp = yf.download('^GSPC', start='2011-04-18')
    kospi = yf.download('^KS11', start='2011-04-18')

    sp_close = sp[('Close', '^GSPC')] if isinstance(sp.columns, pd.MultiIndex) else sp['Close']
    kospi_close = kospi[('Close', '^KS11')] if isinstance(kospi.columns, pd.MultiIndex) else kospi['Close']

    df = pd.DataFrame({'S&P500': sp_close, 'KOSPI': kospi_close})
    df = df.fillna(method='bfill').fillna(method='ffill')

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['S&P500'], 'r--', label='S&P500')
    plt.plot(df.index, df['KOSPI'], 'b', label='KOSPI')
    plt.title('S&P500 vs KOSPI')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend(loc='best')
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64