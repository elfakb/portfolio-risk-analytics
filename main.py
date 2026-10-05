"""Run the full pipeline from the terminal:  python main.py [--refresh]"""
import argparse

import pandas as pd

from src.data_loader import PROJECT_ROOT, load_config, load_prices
from src.optimization import efficient_frontier, max_sharpe, min_volatility, portfolio_performance
from src.portfolio import asset_summary, portfolio_returns, portfolio_summary
from src.returns import daily_returns, monthly_returns
from src.risk_metrics import correlation_matrix, covariance_matrix


def main(refresh: bool = False) -> None:
    cfg = load_config()
    td = cfg["analysis"]["trading_days"]
    rf = cfg["analysis"]["risk_free_rate"]
    conf = cfg["analysis"]["var_confidence"]
    tickers = list(cfg["portfolio"].keys())
    bench = cfg["data"]["benchmark"]

    prices = load_prices(cfg, refresh=refresh)
    daily = daily_returns(prices)
    asset_ret, bench_ret = daily[tickers], daily[bench]
    weights = pd.Series(cfg["portfolio"])
    port_ret = portfolio_returns(asset_ret, weights)

    print(f"\nPeriod: {daily.index[0].date()} -> {daily.index[-1].date()} ({len(daily)} trading days)")

    print("\n=== PORTFOLIO SUMMARY ===")
    for key, value in portfolio_summary(port_ret, bench_ret, rf, td, conf).items():
        print(f"{key:<28}{value:>10.4f}")

    print("\n=== ASSET METRICS ===")
    assets = asset_summary(asset_ret, bench_ret, rf, td, conf)
    print(assets.round(4).to_string())

    print("\n=== CORRELATION MATRIX ===")
    print(correlation_matrix(asset_ret).round(2).to_string())

    mu = asset_ret.mean() * td
    cov = covariance_matrix(asset_ret, td)
    w_ms, w_mv = max_sharpe(mu, cov, rf), min_volatility(mu, cov)
    optimal = pd.DataFrame({"Current": weights, "Max Sharpe": w_ms, "Min Volatility": w_mv})

    print("\n=== OPTIMAL WEIGHTS ===")
    print(optimal.round(3).to_string())
    for label, w in [("Max Sharpe", w_ms), ("Min Volatility", w_mv)]:
        r, v, s = portfolio_performance(w.values, mu.values, cov.values, rf)
        print(f"{label:<15} return={r:.2%}  vol={v:.2%}  sharpe={s:.2f}")

    out = PROJECT_ROOT / cfg["data"]["processed_dir"]
    out.mkdir(parents=True, exist_ok=True)
    daily.to_csv(out / "daily_returns.csv")
    monthly_returns(daily).to_csv(out / "monthly_returns.csv")
    port_ret.to_csv(out / "portfolio_returns.csv")
    assets.to_csv(out / "asset_summary.csv")
    optimal.to_csv(out / "optimal_weights.csv")
    efficient_frontier(mu, cov, cfg["optimization"]["frontier_points"]).to_csv(out / "efficient_frontier.csv", index=False)
    print(f"\nResults saved to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="re-download market data")
    main(parser.parse_args().refresh)