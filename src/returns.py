"""Return calculations: daily, monthly, annualized, cumulative."""
from __future__ import annotations

import pandas as pd


def daily_returns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Simple daily percentage returns."""
    return prices.pct_change().dropna()


def monthly_returns(daily: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Compound daily returns into calendar-month returns."""
    return (1 + daily).resample("ME").prod() - 1


def annualized_return(daily: pd.DataFrame | pd.Series, trading_days: int = 252):
    """Geometric (compound) annualized return (CAGR)."""
    n = len(daily)
    growth = (1 + daily).prod()
    return growth ** (trading_days / n) - 1


def wealth_index(daily: pd.DataFrame | pd.Series, start_value: float = 1.0):
    """Growth of `start_value` invested at the beginning."""
    return start_value * (1 + daily).cumprod()