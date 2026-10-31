"""The three sleeves' rules, exactly as written in strategy.md."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest import indicators as ti
from backtest.engine import Position, Signal, SleeveRules


def _base_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["sma20"] = ti.sma(df["close"], 20)
    out["sma50"] = ti.sma(df["close"], 50)
    out["sma50_prev10"] = out["sma50"].shift(10)
    out["atr14"] = ti.atr(df["high"], df["low"], df["close"], 14)
    out["rsi14"] = ti.rsi(df["close"], 14)
    out["ret63"] = ti.pct_change_n(df["close"], 63)
    out["ret30"] = ti.pct_change_n(df["close"], 30)
    out["hi20"] = df["close"].rolling(20).max()
    out["low10"] = df["low"].rolling(10).min()
    out["relvol"] = ti.relative_volume(df["volume"], 20)
    return out


def _ok(*vals) -> bool:
    return all(v is not None and not (isinstance(v, float) and np.isnan(v)) for v in vals)


class CoreGrowth(SleeveRules):
    """Trend following on growth ETFs: in above a rising 50-day MA, out below it."""

    name = "Core growth"
    sleeve_share = 0.40
    trail_atr = 2.5

    def __init__(self, universe=("QQQ", "SMH", "XLK", "IGV"), max_positions=4):
        self.universe = list(universe)
        self.max_positions = max_positions

    def prepare(self, bars):
        return {s: _base_indicators(bars[s]) for s in self.universe if s in bars}

    def entry_signal(self, sym, ind, i):
        r = ind[sym].iloc[i]
        if not _ok(r["close"], r["sma50"], r["sma50_prev10"], r["atr14"], r["ret63"]):
            return None
        if r["close"] > r["sma50"] and r["sma50"] > r["sma50_prev10"]:
            return Signal(sym, r["close"] - self.trail_atr * r["atr14"], None, r["ret63"], "trend")
        return None

    def exit_on_close(self, pos: Position, row) -> bool:
        return _ok(row["sma50"]) and row["close"] < row["sma50"]

    def trail_stop(self, pos: Position, row) -> float:
        return pos.highest_close - self.trail_atr * row["atr14"] if _ok(row["atr14"]) else pos.stop


class SwingMomentum(SleeveRules):
    """Breakouts and pullbacks in liquid growth leaders, beating QQQ, with a 2R target."""

    name = "Swing momentum"
    sleeve_share = 0.30

    def __init__(self, universe, benchmark="QQQ", max_positions=3):
        self.universe = list(universe)
        self.benchmark = benchmark
        self.max_positions = max_positions

    def prepare(self, bars):
        ind = {s: _base_indicators(bars[s]) for s in self.universe if s in bars}
        bench = _base_indicators(bars[self.benchmark])
        for s, df in ind.items():
            df["bench_ret63"] = bench["ret63"].reindex(df.index)
            df["dollar_ok"] = (df["close"] > 5) & (df["volume"].rolling(50).mean() > 1_000_000)
        return ind

    def entry_signal(self, sym, ind, i):
        r = ind[sym].iloc[i]
        if not _ok(r["close"], r["sma20"], r["sma50"], r["atr14"], r["rsi14"], r["ret63"],
                   r["bench_ret63"], r["relvol"], r["low10"]) or not bool(r["dollar_ok"]):
            return None
        uptrend = r["sma20"] > r["sma50"]
        stronger = r["ret63"] > r["bench_ret63"]
        if not (uptrend and stronger):
            return None
        prev_rsi = ind[sym]["rsi14"].iloc[i - 1] if i > 0 else np.nan
        setup = None
        if r["close"] >= r["hi20"] and r["relvol"] > 1.5:
            setup = "breakout"
        elif _ok(prev_rsi) and prev_rsi < 40 <= r["rsi14"] and abs(r["close"] / r["sma20"] - 1) < 0.03:
            setup = "pullback"
        if setup is None:
            return None
        stop = max(r["low10"], r["close"] - 2 * r["atr14"])  # the tighter of the two
        if stop >= r["close"]:
            return None
        risk = r["close"] - stop
        return Signal(sym, stop, r["close"] + 2 * risk, r["ret63"] - r["bench_ret63"], setup)

    def exit_on_close(self, pos, row) -> bool:
        return False  # exits come from the stop, the 2R target, or the trail

    def trail_stop(self, pos, row) -> float:
        risk = pos.entry - pos.initial_stop
        if pos.highest_close >= pos.entry + risk and _ok(row["atr14"]):
            return max(pos.entry, pos.highest_close - 2 * row["atr14"])  # after +1R: breakeven or trail
        return pos.stop


class CryptoTrend(SleeveRules):
    """BTC/ETH trend positions plus at most one large-cap altcoin (<= 1/3 of the sleeve)."""

    name = "Crypto"
    sleeve_share = 0.30
    trail_atr = 3.0

    def __init__(self, majors=("BTC-USD", "ETH-USD"), alts=("SOL-USD", "XRP-USD", "BNB-USD")):
        self.majors = list(majors)
        self.alt_symbols = set(alts)
        self.universe = self.majors + list(alts)
        self.max_positions = 3

    def prepare(self, bars):
        ind = {s: _base_indicators(bars[s]) for s in self.universe if s in bars}
        btc30 = ind["BTC-USD"]["ret30"]
        for s, df in ind.items():
            df["btc_ret30"] = btc30.reindex(df.index)
        return ind

    def allowed(self, sym, held) -> bool:
        if sym in self.alt_symbols:
            return not any(h in self.alt_symbols for h in held)
        return True

    def entry_signal(self, sym, ind, i):
        r = ind[sym].iloc[i]
        if not _ok(r["close"], r["sma50"], r["sma50_prev10"], r["atr14"], r["ret30"]):
            return None
        if not (r["close"] > r["sma50"] and r["sma50"] > r["sma50_prev10"]):
            return None
        if sym in self.alt_symbols:
            if not _ok(r["btc_ret30"]) or r["ret30"] <= r["btc_ret30"]:
                return None
            score = r["ret30"] - r["btc_ret30"]
        else:
            score = 10 + r["ret30"]  # majors always ranked ahead of altcoins
        return Signal(sym, r["close"] - self.trail_atr * r["atr14"], None, score, "trend")

    def exit_on_close(self, pos, row) -> bool:
        return _ok(row["sma50"]) and row["close"] < row["sma50"]

    def trail_stop(self, pos, row) -> float:
        return pos.highest_close - self.trail_atr * row["atr14"] if _ok(row["atr14"]) else pos.stop
