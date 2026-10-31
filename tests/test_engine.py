"""Engine tests on hand-built price series, so every fill and size can be checked by hand."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest import engine, indicators as ti  # noqa: E402
from backtest.engine import Signal, SleeveRules  # noqa: E402
from backtest.sleeves import CoreGrowth, CryptoTrend  # noqa: E402

NO_COSTS = engine.Costs(slippage=0.0, limit_offset=0.0)


def bars_from_close(closes, spread=0.5, start="2022-01-03"):
    closes = np.asarray(closes, dtype=float)
    idx = pd.bdate_range(start, periods=len(closes))
    return pd.DataFrame({"open": closes, "high": closes + spread, "low": closes - spread,
                         "close": closes, "volume": 2_000_000}, index=idx)


class OneShot(SleeveRules):
    """Signals once on day `day` with a fixed stop/target, to test fills and sizing."""

    name = "test"
    sleeve_share = 1.0

    def __init__(self, day, stop, target=None, max_positions=1):
        self.universe = ["X"]
        self.day, self.stop, self.target, self.max_positions = day, stop, target, max_positions

    def prepare(self, bars):
        return {"X": bars["X"]}

    def entry_signal(self, sym, ind, i):
        return Signal("X", self.stop, self.target, 1.0, "test") if i == self.day else None

    def exit_on_close(self, pos, row):
        return False


def test_three_percent_risk_sizing_and_stop_fill():
    # Entry at 100 with stop 95: risk $5/share. 3% of $10,000 = $300 -> 60 shares,
    # but the 20% position cap allows only $2,000 / 100 = 20 shares.
    closes = [100, 100, 100, 100, 90, 90]
    df = bars_from_close(closes)
    res = engine.run(OneShot(day=1, stop=95), {"X": df}, 10_000, costs=NO_COSTS)
    t = res.trades[0]
    assert t.shares == pytest.approx(20)
    assert t.reason == "stop"
    assert t.exit == pytest.approx(90)          # gapped through the stop: filled at the open
    assert t.r_multiple == pytest.approx(-2.0)  # gap made the loss twice the plan


def test_risk_cap_binds_when_stop_is_wide():
    # Stop 40 below entry: 3% x 10,000 / 40 = 7.5 shares (below the 20-share cap).
    df = bars_from_close([100] * 5)
    res = engine.run(OneShot(day=1, stop=60), {"X": df}, 10_000, costs=NO_COSTS)
    assert res.trades[0].shares == pytest.approx(7.5)


def test_target_fill_and_r_multiple():
    df = bars_from_close([100, 100, 100, 101, 112, 112])
    res = engine.run(OneShot(day=1, stop=95, target=110), {"X": df}, 10_000, costs=NO_COSTS)
    t = res.trades[0]
    assert t.reason == "target" and t.exit == pytest.approx(112)  # opened above the target
    assert t.r_multiple == pytest.approx(12 / 5)


def test_limit_order_expires_when_price_runs_away():
    closes = [100, 100, 110, 110]  # next day's low (109.5) never reaches the 100 limit
    res = engine.run(OneShot(day=1, stop=95), {"X": bars_from_close(closes)}, 10_000, costs=NO_COSTS)
    assert res.trades == []


def test_kill_switch_at_fifty_percent():
    closes = [100, 100, 100] + [100 * 0.8 ** k for k in range(1, 6)] + [30, 30]

    class AllIn(OneShot):
        def entry_signal(self, sym, ind, i):
            return Signal("X", 1.0, None, 1.0, "test") if i == 1 else None

    lim = engine.Limits(max_risk_per_trade=1.0, max_position_pct=1.0)
    res = engine.run(AllIn(day=1, stop=1.0), {"X": bars_from_close(closes, spread=0.01)},
                     10_000, limits=lim, costs=NO_COSTS)
    assert any("KILL SWITCH" in e for e in res.events)
    assert any("halved" in e for e in res.events)
    assert res.trades[0].reason == "kill switch"  # sold at the next open


def test_stops_never_move_down():
    rules = CoreGrowth(["X"])
    closes = list(np.linspace(100, 160, 260)) + list(np.linspace(160, 150, 10))
    res = engine.run(rules, {"X": bars_from_close(closes)}, 10_000, costs=NO_COSTS)
    assert res.trades, "uptrend should trigger a trend entry"


def test_crypto_allows_one_altcoin_at_most():
    rules = CryptoTrend(majors=["BTC-USD"], alts=["A-USD", "B-USD"])
    assert rules.allowed("A-USD", {"BTC-USD": None})
    assert not rules.allowed("B-USD", {"A-USD": None})


def test_rsi_bounds_and_sma():
    s = pd.Series(np.linspace(1, 50, 60))
    assert ti.rsi(s).iloc[-1] == pytest.approx(100.0)
    assert ti.sma(pd.Series([1, 2, 3, 4]), 2).tolist()[1:] == [1.5, 2.5, 3.5]


def test_stock_sale_proceeds_settle_next_bar():
    # Sell on day 4 (stop); the cash is unsettled that day and settled the next.
    df = bars_from_close([100, 100, 100, 100, 90, 90])
    costs = engine.Costs(slippage=0.0, limit_offset=0.0, settle_bars=1)
    res = engine.run(OneShot(day=1, stop=95), {"X": df.iloc[:5]}, 10_000, costs=costs)
    assert res.unsettled == pytest.approx(20 * 90)
    res = engine.run(OneShot(day=1, stop=95), {"X": df}, 10_000, costs=costs)
    assert res.unsettled == 0 and res.cash == pytest.approx(10_000 - 20 * 10)


def test_full_size_resumes_only_under_fifteen_percent():
    lim = engine.Limits(max_risk_per_trade=1.0, max_position_pct=1.0)
    closes = [100, 100, 100, 70, 80, 90]  # dd 30% -> 20% (still halved) -> 10% (full size)

    class AllIn(OneShot):
        def entry_signal(self, sym, ind, i):
            return Signal("X", 1.0, None, 1.0, "test") if i == 1 else None

    res = engine.run(AllIn(day=1, stop=1.0), {"X": bars_from_close(closes, spread=0.01)},
                     10_000, limits=lim, costs=NO_COSTS)
    assert [e.split(": ")[1][:8] for e in res.events] == ["drawdown", "drawdown"]
    assert "back under 15%" in res.events[1] and res.events[1].startswith(str(bars_from_close(closes).index[5].date()))
