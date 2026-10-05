"""Streamlit dashboard. Run with:  streamlit run dashboard/app.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src import visualization as viz
from src.data_loader import load_config, load_prices
from src.optimization import (
    efficient_frontier, max_sharpe, min_volatility,
    portfolio_performance, random_portfolios,
)
from src.portfolio import asset_summary, portfolio_returns, portfolio_summary
from src.returns import annualized_return, daily_returns, monthly_returns, wealth_index
from src.risk_metrics import annualized_volatility, correlation_matrix, covariance_matrix, drawdown_series

st.set_page_config(page_title="BIST Portfolio Risk Analytics", layout="wide")

cfg = load_config()
TD = cfg["analysis"]["trading_days"]
NAMES = cfg["names"]
TICKERS = list(cfg["portfolio"].keys())
BENCH = cfg["data"]["benchmark"]


@st.cache_data(show_spinner="Downloading market data...")
def get_prices(refresh: bool) -> pd.DataFrame:
    return load_prices(cfg, refresh=refresh)


# ------------------------------------------------------------------ sidebar
st.sidebar.header("Settings")
if st.sidebar.button("Refresh market data"):
    st.cache_data.clear()
    st.session_state["refresh"] = True

rf = st.sidebar.number_input(
    "Risk-free rate (%, annual)", 0.0, 100.0, cfg["analysis"]["risk_free_rate"] * 100, 0.5
) / 100

st.sidebar.subheader("Portfolio weights (%)")
raw_weights = {
    t: st.sidebar.slider(NAMES.get(t, t), 0, 100, int(round(cfg["portfolio"][t] * 100)))
    for t in TICKERS
}
total = sum(raw_weights.values())
if total == 0:
    st.sidebar.error("At least one weight must be above 0.")
    st.stop()
weights = pd.Series({t: w / total for t, w in raw_weights.items()})
if total != 100:
    st.sidebar.warning(f"Weights sum to {total}%, normalized to 100%.")

n_random = st.sidebar.slider("Random portfolios", 1000, 10000, cfg["optimization"]["n_random_portfolios"], 500)

# ------------------------------------------------------------------ data
prices = get_prices(st.session_state.pop("refresh", False))
daily = daily_returns(prices)
asset_ret, bench_ret = daily[TICKERS], daily[BENCH]
port_ret = portfolio_returns(asset_ret, weights)

summary = portfolio_summary(port_ret, bench_ret, rf, TD, cfg["analysis"]["var_confidence"])

# ------------------------------------------------------------------ header + KPIs
st.title("BIST Investment Portfolio & Market Risk Analytics")
st.caption(
    f"Period: {daily.index[0].date()} to {daily.index[-1].date()}  |  "
    f"Benchmark: {BENCH}  |  Currency: TL (nominal)"
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio Return (ann.)", f"{summary['Annualized Return']:.2%}")
c2.metric("Portfolio Risk (ann. vol)", f"{summary['Annualized Volatility']:.2%}")
c3.metric("Sharpe Ratio", f"{summary['Sharpe Ratio']:.2f}")
c4.metric("Maximum Drawdown", f"{summary['Max Drawdown']:.2%}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Beta vs BIST 100", f"{summary['Beta']:.2f}")
c6.metric("Alpha (ann.)", f"{summary['Alpha']:.2%}")
c7.metric("Sortino Ratio", f"{summary['Sortino Ratio']:.2f}")
var_key = [k for k in summary if k.startswith("VaR")][0]
c8.metric(var_key, f"{summary[var_key]:.2%}")

# ------------------------------------------------------------------ tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Performance", "Allocation & Correlation", "Efficient Frontier", "Asset Metrics", "Monthly Returns"]
)

with tab1:
    wealth = wealth_index(pd.concat([port_ret, bench_ret.rename("BIST 100")], axis=1))
    st.plotly_chart(viz.cumulative_returns_chart(wealth), use_container_width=True)
    dd = pd.concat([drawdown_series(port_ret), drawdown_series(bench_ret).rename("BIST 100")], axis=1)
    st.plotly_chart(viz.drawdown_chart(dd), use_container_width=True)

with tab2:
    left, right = st.columns(2)
    left.plotly_chart(viz.allocation_pie(weights, NAMES), use_container_width=True)
    corr = correlation_matrix(asset_ret).rename(index=NAMES, columns=NAMES)
    right.plotly_chart(viz.correlation_heatmap(corr), use_container_width=True)
    with st.expander("Annualized covariance matrix"):
        st.dataframe(covariance_matrix(asset_ret, TD).rename(index=NAMES, columns=NAMES).style.format("{:.4f}"))

with tab3:
    mu = asset_ret.mean() * TD
    cov = covariance_matrix(asset_ret, TD)

    w_ms = max_sharpe(mu, cov, rf)
    w_mv = min_volatility(mu, cov)
    frontier = efficient_frontier(mu, cov, cfg["optimization"]["frontier_points"])
    cloud = random_portfolios(mu, cov, rf, n_random, cfg["optimization"]["seed"])

    r_ms, v_ms, s_ms = portfolio_performance(w_ms.values, mu.values, cov.values, rf)
    r_mv, v_mv, s_mv = portfolio_performance(w_mv.values, mu.values, cov.values, rf)
    r_cur, v_cur, s_cur = portfolio_performance(weights.values, mu.values, cov.values, rf)

    assets_pts = pd.DataFrame({"return": mu, "volatility": annualized_volatility(asset_ret, TD)})
    assets_pts.index = [NAMES.get(t, t) for t in assets_pts.index]

    fig = viz.efficient_frontier_chart(
        cloud, frontier,
        {"Max Sharpe": (v_ms, r_ms), "Min Volatility": (v_mv, r_mv), "Current Portfolio": (v_cur, r_cur)},
        assets_pts,
    )
    st.plotly_chart(fig, use_container_width=True)

    table = pd.DataFrame(
        {"Current": weights, "Max Sharpe": w_ms, "Min Volatility": w_mv}
    ).rename(index=NAMES)
    perf = pd.DataFrame(
        {"Current": [r_cur, v_cur, s_cur], "Max Sharpe": [r_ms, v_ms, s_ms], "Min Volatility": [r_mv, v_mv, s_mv]},
        index=["Expected Return", "Volatility", "Sharpe"],
    )
    a, b = st.columns(2)
    a.subheader("Weights")
    a.dataframe(table.style.format("{:.1%}"))
    b.subheader("Performance")
    b.dataframe(perf.style.format("{:.3f}"))
    st.caption("Expected return uses the historical arithmetic mean, which is backward-looking and not a forecast.")

with tab4:
    table = asset_summary(asset_ret, bench_ret, rf, TD, cfg["analysis"]["var_confidence"]).rename(index=NAMES)
    st.dataframe(table.style.format("{:.2%}", subset=[c for c in table.columns if "Ratio" not in c and c != "Beta"])
                 .format("{:.2f}", subset=["Sharpe Ratio", "Sortino Ratio", "Beta"]))

with tab5:
    st.plotly_chart(viz.monthly_returns_chart(monthly_returns(port_ret)), use_container_width=True)