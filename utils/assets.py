import yfinance as yf
import pandas as pd
import numpy as np

def get_price_data(tickers: list, period: str ):
    prices = yf.Tickers(tickers=tickers).history(period=period)
    prices= prices['Close']
    prices.columns = prices.columns.values
    prices.index = prices.index.values
    return prices

def calc_returns(prices: pd.DataFrame):
    returns = prices.pct_change().fillna(0)
    return returns

def equity_curve(returns):
    eq=(1+returns).cumprod() * 1000
    return eq

def drawdowns(returns):
    cum_returns = (1+returns).cumprod()
    running_max = np.maximum.accumulate(cum_returns)
    return (cum_returns - running_max)/running_max

p = get_price_data(['AAPL','TSLA'],'1y')
r = calc_returns(p)
eq= equity_curve(r)
dd = drawdowns(r)