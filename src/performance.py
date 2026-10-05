from __future__ import annotations

import numpy as np
import pandas as pd


def sharpe_ratio(daily, rf: float, trading_days: int = 252):
    """Annualized Sharpe ratio."""
    excess = daily.mean() * trading_days - rf
    vol = daily.std() * np.sqrt(trading_days)
    return excess / vol


def sortino_ratio(daily, rf: float, trading_days: int = 252):
    """Sharpe-like ratio that only penalizes downside deviation."""
    target = rf / trading_days
    downside = np.minimum(daily - target, 0)
    downside_dev = np.sqrt((downside ** 2).mean()) * np.sqrt(trading_days)
    excess = daily.mean() * trading_days - rf
    return excess / downside_dev


def beta(daily, benchmark: pd.Series):
    """Sensitivity to the benchmark: cov(asset, bench) / var(bench)."""
    if isinstance(daily, pd.DataFrame):
        return daily.apply(lambda col: beta(col, benchmark))
    return daily.cov(benchmark) / benchmark.var()


def alpha(daily, benchmark: pd.Series, rf: float, trading_days: int = 252):
    """Annualized Jensen's alpha."""
    b = beta(daily, benchmark)
    asset_excess = daily.mean() * trading_days - rf
    bench_excess = benchmark.mean() * trading_days - rf
    return asset_excess - b * bench_excess