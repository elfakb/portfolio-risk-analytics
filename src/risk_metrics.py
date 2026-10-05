"""Risk metrics: volatility, covariance, correlation, drawdown, VaR."""
from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_volatility(daily, trading_days: int = 252):
    """Annualized standard deviation of returns."""
    return daily.std() * np.sqrt(trading_days)


def covariance_matrix(daily: pd.DataFrame, trading_days: int = 252) -> pd.DataFrame:
    """Annualized covariance matrix."""
    return daily.cov() * trading_days


def correlation_matrix(daily: pd.DataFrame) -> pd.DataFrame:
    return daily.corr()


def drawdown_series(daily):
    """Percentage decline from the running peak (values are <= 0)."""
    wealth = (1 + daily).cumprod()
    peak = wealth.cummax()
    return wealth / peak - 1


def max_drawdown(daily):
    """Worst peak-to-trough decline (negative number)."""
    return drawdown_series(daily).min()


def historical_var(daily, confidence: float = 0.95):
    """Historical 1-day Value at Risk, returned as a positive loss."""
    return -daily.quantile(1 - confidence)


def conditional_var(daily, confidence: float = 0.95):
    """Expected Shortfall: average loss beyond the VaR threshold (positive)."""
    if isinstance(daily, pd.DataFrame):
        return daily.apply(conditional_var, confidence=confidence)
    threshold = daily.quantile(1 - confidence)
    return -daily[daily <= threshold].mean()