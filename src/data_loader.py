"""Data loading: config, price download (yfinance) and cleaning."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yaml
import yfinance as yf

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Synthetic asset: gram gold priced in TL, built from gold futures (USD/oz) and USD/TRY
GOLD_TICKER = "GOLD_TRY"
GOLD_FUTURES = "GC=F"
USDTRY = "TRY=X"
GRAMS_PER_OUNCE = 31.1034768


def load_config(path: str | Path | None = None) -> dict:
    """Read config.yaml and validate that portfolio weights sum to 1."""
    path = Path(path) if path else PROJECT_ROOT / "config.yaml"
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    total = sum(cfg["portfolio"].values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Portfolio weights must sum to 1.0, got {total:.4f}")
    return cfg


def clean_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Sort, remove timezone, forward-fill short gaps and drop remaining NaNs."""
    prices = prices.sort_index()
    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)
    prices = prices.ffill(limit=5).dropna()
    return prices


def _download_close(tickers: list[str], start: date, end: date) -> pd.DataFrame:
    """Download adjusted close prices as a DataFrame with one column per ticker."""
    raw = yf.download(
        tickers,
        start=start.isoformat(),
        end=end.isoformat(),
        auto_adjust=True,
        progress=False,
    )
    if raw.empty:
        raise RuntimeError("No data returned from Yahoo Finance. Check your internet connection.")

    close = raw["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(name=tickers[0])
    return close


def download_prices(tickers: list[str], years: int = 5) -> pd.DataFrame:
    """Download prices for the given tickers (GOLD_TRY is built synthetically)."""
    end = date.today()
    start = end - timedelta(days=365 * years)

    need_gold = GOLD_TICKER in tickers
    real_tickers = [t for t in tickers if t != GOLD_TICKER]
    to_fetch = real_tickers + ([GOLD_FUTURES, USDTRY] if need_gold else [])

    close = _download_close(to_fetch, start, end)

    if need_gold:
        for needed in (GOLD_FUTURES, USDTRY):
            if needed not in close.columns or close[needed].dropna().empty:
                raise ValueError(f"Could not download {needed}, needed to build {GOLD_TICKER}.")
        # Different trading calendars: forward-fill each series before combining
        gold_usd = close[GOLD_FUTURES].ffill()
        fx = close[USDTRY].ffill()
        close[GOLD_TICKER] = gold_usd * fx / GRAMS_PER_OUNCE
        close = close.drop(columns=[GOLD_FUTURES, USDTRY])

    missing = [t for t in tickers if t not in close.columns or close[t].dropna().empty]
    if missing:
        raise ValueError(
            f"No data found for: {missing}. "
            "Replace these tickers in config.yaml (names and portfolio sections)."
        )

    prices = clean_prices(close[tickers])

    first_date = prices.index[0].date()
    if first_date > start + timedelta(days=15):
        print(f"[warning] Common history starts at {first_date}, "
              f"shorter than the requested {years} years (a ticker has less history).")
    return prices


def load_prices(cfg: dict, refresh: bool = False) -> pd.DataFrame:
    """Load prices from the local CSV cache, or download them when missing/refresh."""
    raw_dir = PROJECT_ROOT / cfg["data"]["raw_dir"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_file = raw_dir / "prices.csv"

    tickers = list(cfg["portfolio"].keys())
    benchmark = cfg["data"]["benchmark"]
    all_tickers = tickers + ([benchmark] if benchmark not in tickers else [])

    if cache_file.exists() and not refresh:
        cached = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        if set(all_tickers).issubset(cached.columns):
            return cached[all_tickers]

    prices = download_prices(all_tickers, years=cfg["data"]["years"])
    prices.to_csv(cache_file)
    return prices