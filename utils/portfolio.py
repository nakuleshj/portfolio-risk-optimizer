import pandas as pd
import numpy as np

def gen_eq_weights(n):
    return np.repeat(1/n, n)

def _gen_random_weights(n):
    r=np.random.random(5)
    return r/sum(r)

def gen_random_pfs(n_pfs, tickers):
    pfs = pd.DataFrame(columns=tickers)
    for i in range(n_pfs):
        pf = _gen_random_weights(len(tickers))
        pfs.loc[i] = pf
    return pfs

def calc_pf_metrics(pfs, ann_avg_ret, ann_cov):
    return None

def calc_pf_returns(asset_returns, w):
    return asset_returns.mul(w, axis=1).sum(axis = 1)