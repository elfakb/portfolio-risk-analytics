import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.optimization import max_sharpe, min_volatility, portfolio_performance
from src.performance import beta, sharpe_ratio
from src.portfolio import portfolio_returns
from src.returns import annualized_return
from src.risk_metrics import drawdown_series, historical_var, max_drawdown


@pytest.fixture
def sample_returns():
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2023-01-02", periods=500)
    return pd.DataFrame(rng.normal(0.0008, 0.015, (500, 3)), index=idx, columns=["A", "B", "C"])


def test_max_drawdown_known_value():
    r = pd.Series([0.10, -0.20, 0.05])
    assert max_drawdown(r) == pytest.approx(-0.20)


def test_drawdown_is_never_positive(sample_returns):
    assert (drawdown_series(sample_returns["A"]) <= 1e-12).all()


def test_annualized_return_constant_growth():
    r = pd.Series([0.001] * 252)
    assert annualized_return(r, 252) == pytest.approx(1.001 ** 252 - 1)


def test_beta_of_scaled_series(sample_returns):
    bench = sample_returns["A"]
    assert beta(2 * bench, bench) == pytest.approx(2.0)
    assert beta(bench, bench) == pytest.approx(1.0)


def test_sharpe_sign(sample_returns):
    # A risk-free rate far above any return must give a negative Sharpe
    assert sharpe_ratio(sample_returns["A"], rf=0.9) < 0


def test_var_is_positive_loss(sample_returns):
    assert historical_var(sample_returns["A"], 0.95) > 0


def test_portfolio_returns_weighted_sum(sample_returns):
    w = {"A": 0.5, "B": 0.3, "C": 0.2}
    expected = 0.5 * sample_returns["A"] + 0.3 * sample_returns["B"] + 0.2 * sample_returns["C"]
    pd.testing.assert_series_equal(portfolio_returns(sample_returns, w), expected, check_names=False)


def test_optimizers_beat_equal_weight(sample_returns):
    mu = sample_returns.mean() * 252
    cov = sample_returns.cov() * 252
    rf = 0.05
    eq = np.full(3, 1 / 3)
    _, eq_vol, eq_sharpe = portfolio_performance(eq, mu.values, cov.values, rf)

    w_mv = min_volatility(mu, cov)
    w_ms = max_sharpe(mu, cov, rf)

    assert w_mv.sum() == pytest.approx(1.0)
    assert w_ms.sum() == pytest.approx(1.0)
    assert (w_mv >= -1e-9).all() and (w_ms >= -1e-9).all()
    assert portfolio_performance(w_mv.values, mu.values, cov.values, rf)[1] <= eq_vol + 1e-9
    assert portfolio_performance(w_ms.values, mu.values, cov.values, rf)[2] >= eq_sharpe - 1e-9