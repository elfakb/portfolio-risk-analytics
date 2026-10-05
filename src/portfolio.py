from __future__ import annotations

import pandas as pd

from src.performance import alpha, beta, sharpe_ratio, sortino_ratio
from src.returns import annualized_return
from src.risk_metrics import (
    annualized_volatility,
    conditional_var,
    historical_var,
    max_drawdown,
)


def _to_series(weights, index) -> pd.Series:
    if isinstance(weights, dict):
        series = pd.Series(weights)
    else:
        series = pd.Series(weights, index=index)
    return series.reindex(index)


def portfolio_returns(asset_returns: pd.DataFrame, weights) -> pd.Series:
    """Daily portfolio return assuming daily rebalancing to target weights."""
    w = _to_series(weights, asset_returns.columns)
    return asset_returns.mul(w, axis=1).sum(axis=1).rename("Portfolio")


def portfolio_summary(
    port_ret: pd.Series,
    bench_ret: pd.Series,
    rf: float,
    trading_days: int = 252,
    var_conf: float = 0.95,
) -> dict:
    """All headline metrics for the portfolio as a dictionary."""
    return {
        "Annualized Return": annualized_return(port_ret, trading_days),
        "Annualized Volatility": annualized_volatility(port_ret, trading_days),
        "Sharpe Ratio": sharpe_ratio(port_ret, rf, trading_days),
        "Sortino Ratio": sortino_ratio(port_ret, rf, trading_days),
        "Max Drawdown": max_drawdown(port_ret),
        "Beta": beta(port_ret, bench_ret),
        "Alpha": alpha(port_ret, bench_ret, rf, trading_days),
        f"VaR {int(var_conf * 100)}% (1-day)": historical_var(port_ret, var_conf),
        f"CVaR {int(var_conf * 100)}% (1-day)": conditional_var(port_ret, var_conf),
    }


def asset_summary(
    asset_ret: pd.DataFrame,
    bench_ret: pd.Series,
    rf: float,
    trading_days: int = 252,
    var_conf: float = 0.95,
) -> pd.DataFrame:
    """Per-asset metrics table."""
    return pd.DataFrame(
        {
            "Annualized Return": annualized_return(asset_ret, trading_days),
            "Annualized Volatility": annualized_volatility(asset_ret, trading_days),
            "Sharpe Ratio": sharpe_ratio(asset_ret, rf, trading_days),
            "Sortino Ratio": sortino_ratio(asset_ret, rf, trading_days),
            "Max Drawdown": max_drawdown(asset_ret),
            "Beta": beta(asset_ret, bench_ret),
            "Alpha": alpha(asset_ret, bench_ret, rf, trading_days),
            f"VaR {int(var_conf * 100)}% (1-day)": historical_var(asset_ret, var_conf),
        }
    )