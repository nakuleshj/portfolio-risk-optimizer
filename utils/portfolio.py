import pandas as pd
import numpy as np


def gen_eq_weights(n):
    return np.repeat(1 / n, n)


def _gen_random_weights(n):
    r = np.random.random(n)
    return r / sum(r)


def gen_random_pfs(n_pfs, tickers):
    pfs = pd.DataFrame(columns=tickers)
    for i in range(n_pfs):
        pf = _gen_random_weights(len(tickers))
        pfs.loc[i] = pf
    return pfs


def calc_pf_metrics(pfs: pd.DataFrame, asset_returns: pd.DataFrame, rf):
    ann_avg_ret = (1 + asset_returns.mean()) ** 252 - 1
    ann_cov = asset_returns.cov() * 252
    vols = []
    pf_returns = []
    for i, r in pfs.iterrows():
        pf_returns.append(ann_avg_ret.mul(r).sum())
        vols.append(np.sqrt(r.T @ ann_cov @ r))
    pfs["Return"] = pf_returns
    pfs["Volatility"] = vols
    pfs["Sharpe"] = (pfs["Return"] - rf) / pfs["Volatility"]
    return pfs


def calc_pf_pnl(asset_returns, w):
    return asset_returns.mul(w, axis=1).sum(axis=1)