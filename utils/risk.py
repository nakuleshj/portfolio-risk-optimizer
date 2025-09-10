import numpy as np
import pandas as pd


def calc_var_es(returns, confidence_level=95):
    var = np.percentile(returns,100-confidence_level)
    es = returns[returns<=var].mean()
    return var, es