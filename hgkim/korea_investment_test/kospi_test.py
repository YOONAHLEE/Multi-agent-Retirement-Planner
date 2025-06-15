import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# yfinance로 직접 다운로드
sp = yf.download('^GSPC', start='2011-04-18')
kospi = yf.download('^KS11', start='2011-04-18')

# MultiIndex 컬럼에서 'Close' 값만 추출
sp_close = sp[('Close', '^GSPC')] if isinstance(sp.columns, pd.MultiIndex) else sp['Close']
kospi_close = kospi[('Close', '^KS11')] if isinstance(kospi.columns, pd.MultiIndex) else kospi['Close']

# 데이터가 비어있지 않은지 확인
if not sp.empty and not kospi.empty:
    # 데이터프레임으로 합치기
    df = pd.DataFrame({'S&P500': sp_close, 'KOSPI': kospi_close})

    # 결측치 보정 (휴장일 등)
    df = df.fillna(method='bfill')
    df = df.fillna(method='ffill')

    # 그래프 그리기
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['S&P500'], 'r--', label='S&P500')
    plt.plot(df.index, df['KOSPI'], 'b', label='KOSPI')
    plt.title('S&P500 vs KOSPI')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()
else:
    print("데이터를 불러오지 못했습니다.")