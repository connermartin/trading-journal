"""Load daily OHLCV bars from data/prices/<SYMBOL>.csv, and fetch them when the network allows.

CSV format: date,open,high,low,close,volume  (split/dividend-adjusted daily bars).
Crypto symbols are stored as e.g. BTC-USD.csv.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRICE_DIR = ROOT / "data" / "prices"
COLUMNS = ["open", "high", "low", "close", "volume"]


def load_bars(symbol: str, price_dir: Path = PRICE_DIR) -> pd.DataFrame:
    """Read one symbol's bars, validated and sorted. Raises if the file is missing or bad."""
    path = price_dir / f"{symbol}.csv"
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing columns {missing}")
    df = df[COLUMNS].apply(pd.to_numeric, errors="coerce")
    df = df[~df.index.duplicated(keep="last")].dropna(subset=["open", "high", "low", "close"])
    bad = (df[["open", "high", "low", "close"]] <= 0).any(axis=1) | (df["high"] < df["low"])
    if bad.any():
        raise ValueError(f"{path.name}: {int(bad.sum())} bars with non-positive or inverted prices")
    return df


def load_many(symbols: list[str], price_dir: Path = PRICE_DIR) -> dict[str, pd.DataFrame]:
    return {s: load_bars(s, price_dir) for s in symbols}


def fetch_yahoo(symbols: list[str], start: str, price_dir: Path = PRICE_DIR) -> list[str]:
    """Download adjusted daily bars with yfinance and save them. Returns the symbols that failed."""
    import yfinance as yf

    price_dir.mkdir(parents=True, exist_ok=True)
    failed = []
    for sym in symbols:
        try:
            raw = yf.download(sym, start=start, interval="1d", auto_adjust=True,
                              progress=False, threads=False)
            if raw is None or raw.empty:
                raise ValueError("no data returned")
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            out = raw.rename(columns=str.lower)[COLUMNS]
            out.index.name = "date"
            out.to_csv(price_dir / f"{sym}.csv")
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"  {sym}: download failed ({exc})")
            failed.append(sym)
    return failed
