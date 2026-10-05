from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def portfolio_performance(w: np.ndarray, mu: np.ndarray, cov: np.ndarray, rf: float):
    """Return (expected return, volatility, Sharpe) for weights `w`."""
    ret = float(w @ mu)
    vol = float(np.sqrt(w @ cov @ w))
    sharpe = (ret - rf) / vol if vol > 0 else np.nan
    return ret, vol, sharpe


def _base_setup(n: int):
    bounds = tuple((0.0, 1.0) for _ in range(n))
    x0 = np.full(n, 1.0 / n)
    sum_to_one = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    return bounds, x0, sum_to_one


def min_volatility(mu: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """Global minimum variance portfolio."""
    n = len(mu)
    bounds, x0, sum_to_one = _base_setup(n)
    res = minimize(
        lambda w: w @ cov.values @ w,
        x0, method="SLSQP", bounds=bounds, constraints=[sum_to_one],
    )
    return pd.Series(res.x, index=mu.index)


def max_sharpe(mu: pd.Series, cov: pd.DataFrame, rf: float) -> pd.Series:
    """Tangency portfolio (maximum Sharpe ratio)."""
    n = len(mu)
    bounds, x0, sum_to_one = _base_setup(n)

    def neg_sharpe(w):
        return -portfolio_performance(w, mu.values, cov.values, rf)[2]

    res = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds, constraints=[sum_to_one])
    return pd.Series(res.x, index=mu.index)


def efficient_frontier(mu: pd.Series, cov: pd.DataFrame, n_points: int = 50) -> pd.DataFrame:
    """Minimum-volatility portfolio for each target return along the frontier."""
    n = len(mu)
    bounds, x0, sum_to_one = _base_setup(n)

    w_min = min_volatility(mu, cov)
    r_min = float(w_min.values @ mu.values)
    r_max = float(mu.max())

    rows = []
    for target in np.linspace(r_min, r_max, n_points):
        constraints = [
            sum_to_one,
            {"type": "eq", "fun": lambda w, t=target: w @ mu.values - t},
        ]
        res = minimize(
            lambda w: w @ cov.values @ w,
            x0, method="SLSQP", bounds=bounds, constraints=constraints,
        )
        if res.success:
            rows.append({"return": target, "volatility": float(np.sqrt(res.fun))})
    return pd.DataFrame(rows)


def random_portfolios(
    mu: pd.Series, cov: pd.DataFrame, rf: float, n: int = 5000, seed: int = 42
) -> pd.DataFrame:
    """Monte Carlo cloud of random long-only portfolios."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        w = rng.dirichlet(np.ones(len(mu)))
        ret, vol, sharpe = portfolio_performance(w, mu.values, cov.values, rf)
        rows.append({"return": ret, "volatility": vol, "sharpe": sharpe})
    return pd.DataFrame(rows)