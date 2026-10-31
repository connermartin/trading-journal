"""Technical indicators used by the strategy rules. All take/return pandas Series."""

from __future__ import annotations

import pandas as pd


def sma(close: pd.Series, n: int) -> pd.Series:
    """Simple moving average of the last n closes."""
    return close.rolling(n, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """Wilder's RSI (0-100). Above 70 = stretched up, below 30 = stretched down."""
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, min_periods=n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, min_periods=n, adjust=False).mean()
    rs = gain / loss
    out = 100 - 100 / (1 + rs)
    return out.where(loss != 0, 100.0).where(gain.notna())


def atr(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 14) -> pd.Series:
    """Average True Range: the typical daily price range, used to set stops."""
    prev = close.shift(1)
    tr = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()


def pct_change_n(close: pd.Series, n: int) -> pd.Series:
    """Return over the last n bars, e.g. 63 trading days ~ 3 months."""
    return close / close.shift(n) - 1


def relative_volume(volume: pd.Series, n: int = 20) -> pd.Series:
    """Today's volume divided by the average of the previous n days."""
    return volume / volume.shift(1).rolling(n, min_periods=n).mean()
