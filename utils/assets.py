import yfinance as yf
import pandas as pd
import numpy as np
import scipy.stats as s

def get_tickers():
    tickers = pd.read_json('company_tickers.json', orient="records")
    return tickers.T['ticker'].to_list()


def get_price_data(tickers: list, period: str ):
    prices = yf.Tickers(tickers=tickers).history(period=period)
    prices= prices['Close']
    prices.columns = prices.columns.values
    prices.index = prices.index.values
    return prices

def calc_returns(prices: pd.DataFrame):
    returns = prices.pct_change().fillna(0)
    return returns

def equity_curve(returns, initial_capital = 1000):
    eq=(1+returns).cumprod() * initial_capital
    return eq

def drawdowns(returns):
    cum_returns = (1+returns).cumprod()
    running_max = np.maximum.accumulate(cum_returns)
    return (cum_returns - running_max)/running_max

def summary_stats(returns, rf=0.02):
    d_vol = returns.std()
    ann_vol = returns.std() * np.sqrt(252)
    avg_ret = returns.mean()
    ann_avg_ret = (1+avg_ret) ** 252 - 1
    skew = s.skew(returns)
    kurtosis = s.kurtosis(returns)
    stats = pd.DataFrame(
        {
            "Avg. Daily Return": returns.mean(),
            "Avg. Annual Return": ((1+returns.mean()) ** 252-1),
            "Daily Volatility": d_vol,
            "Annualized Volatility": ann_vol,
            "Skew": skew,
            "Excess Kurtosis": kurtosis,
            "Sharpe Ratio": (ann_avg_ret - rf) / ann_vol
        },
        index=returns.columns.values
    )
    return stats.T


p = get_price_data(['AAPL','TSLA'],'1y')
r = calc_returns(p)
eq= equity_curve(r)
dd = drawdowns(r)