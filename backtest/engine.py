"""Daily-bar backtest engine for one sleeve, enforcing the hard risk limits from config.yaml.

Timing (no look-ahead):
  * Signals are computed on day t's CLOSE.
  * Entries are LIMIT orders for day t+1: limit = close_t x (1 + limit_offset). Filled at
    min(open, limit) if the day's low reaches the limit; otherwise the order expires.
  * Stops are resting stop orders: if a day's low <= stop, the exit is at min(open, stop)
    (a gap down fills at the open, below the stop: this is real slippage risk).
  * Targets are resting limit sells: if high >= target, exit at max(open, target).
    If stop and target are both touched on one day, the stop is assumed to hit first.
  * "Close below the 50-day MA" exits are sold at the next day's open.
  * Slippage is charged on every fill. Commissions are $0 (Robinhood); crypto pays a spread.

Position sizing (every entry):
  risk_budget = account_equity x max_risk_per_trade (3%), halved in a 25%+ drawdown
  shares      = min(risk_budget / (entry - stop),        # 3% risk rule
                    slot_value / entry,                   # sleeve slot
                    account_equity x max_position / entry, # 20% (15% altcoin) cap
                    cash / entry)                          # never spend money we don't have
  Fractional shares/coins are allowed.

account_equity is estimated as sleeve_equity / sleeve_share, so a sleeve tested on its own
uses the same per-trade dollar limits it would have inside the full account.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Limits:
    max_risk_per_trade: float = 0.03
    max_position_pct: float = 0.20
    max_position_pct_alt: float = 0.15
    max_new_entries_per_day: int = 3
    dd_halve_size: float = 0.25
    dd_kill: float = 0.50


@dataclass
class Costs:
    slippage: float = 0.0005      # 5 bps per fill (stocks); crypto uses a wider spread
    limit_offset: float = 0.005   # entry limit = signal close + 0.5%


@dataclass
class Signal:
    symbol: str
    stop: float
    target: float | None
    score: float          # higher = preferred when slots are scarce
    setup: str            # e.g. "breakout", "pullback", "trend"


@dataclass
class Position:
    symbol: str
    entry_date: pd.Timestamp
    entry: float
    shares: float
    stop: float
    initial_stop: float
    target: float | None
    setup: str
    highest_close: float
    exit_next_open: bool = False
    exit_reason: str = "close below 50-day MA"


@dataclass
class Trade:
    symbol: str
    setup: str
    entry_date: pd.Timestamp
    entry: float
    exit_date: pd.Timestamp
    exit: float
    shares: float
    initial_stop: float
    reason: str

    @property
    def pnl(self) -> float:
        return (self.exit - self.entry) * self.shares

    @property
    def r_multiple(self) -> float:
        risk = self.entry - self.initial_stop
        return (self.exit - self.entry) / risk if risk > 0 else float("nan")


@dataclass
class Result:
    name: str
    equity: pd.Series
    trades: list[Trade]
    events: list[str] = field(default_factory=list)
    exposure: float = 0.0  # fraction of days with at least one position


class SleeveRules:
    """Interface each sleeve implements. `ind` holds precomputed indicator frames per symbol."""

    name = "sleeve"
    universe: list[str] = []
    max_positions = 4
    sleeve_share = 0.40
    alt_symbols: set[str] = set()

    def prepare(self, bars: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        raise NotImplementedError

    def entry_signal(self, sym: str, ind: dict[str, pd.DataFrame], i: int) -> Signal | None:
        raise NotImplementedError

    def exit_on_close(self, pos: Position, row: pd.Series) -> bool:
        raise NotImplementedError

    def trail_stop(self, pos: Position, row: pd.Series) -> float:
        return pos.stop

    def slot_value(self, sleeve_equity: float) -> float:
        return sleeve_equity / self.max_positions

    def allowed(self, sym: str, held: dict[str, Position]) -> bool:
        return True


def run(rules: SleeveRules, bars: dict[str, pd.DataFrame], initial: float,
        limits: Limits = Limits(), costs: Costs = Costs(),
        start: str | None = None) -> Result:
    ind = rules.prepare(bars)
    index = sorted(set().union(*(df.index for df in ind.values())))
    index = pd.DatetimeIndex(index)
    if start:
        index = index[index >= pd.Timestamp(start)]
    frames = {s: df.reindex(index) for s, df in ind.items()}

    cash = initial
    positions: dict[str, Position] = {}
    pending: list[tuple[Signal, float]] = []  # (signal, limit price) for the next bar
    trades: list[Trade] = []
    events: list[str] = []
    equity_curve = []
    last_close: dict[str, float] = {}
    hwm = initial
    killed = False
    halved = False
    days_exposed = 0

    def close_position(pos: Position, date, price: float, reason: str):
        nonlocal cash
        fill = price * (1 - costs.slippage)
        cash += pos.shares * fill
        trades.append(Trade(pos.symbol, pos.setup, pos.entry_date, pos.entry, date, fill,
                            pos.shares, pos.initial_stop, reason))
        del positions[pos.symbol]

    for i, date in enumerate(index):
        rows = {s: f.iloc[i] for s, f in frames.items()}

        # 1. Exits flagged at yesterday's close, sold at today's open.
        for pos in list(positions.values()):
            row = rows[pos.symbol]
            if pos.exit_next_open and not np.isnan(row["open"]):
                close_position(pos, date, row["open"], pos.exit_reason)

        # 2. Yesterday's entry orders (limit orders, valid for this bar only).
        equity_now = cash + sum(p.shares * last_close.get(p.symbol, p.entry) for p in positions.values())
        account_equity = equity_now / rules.sleeve_share
        for sig, limit in pending:
            row = rows[sig.symbol]
            if killed or sig.symbol in positions or len(positions) >= rules.max_positions:
                continue
            if np.isnan(row["open"]) or row["low"] > limit:
                continue  # data gap or limit never reached: order expires unfilled
            fill = min(row["open"], limit) * (1 + costs.slippage)
            risk_per_share = fill - sig.stop
            if risk_per_share <= 0:
                continue  # opened below the planned stop: setup is void
            risk_budget = account_equity * limits.max_risk_per_trade * (0.5 if halved else 1.0)
            cap_pct = limits.max_position_pct_alt if sig.symbol in rules.alt_symbols else limits.max_position_pct
            slot = rules.slot_value(equity_now) * (0.5 if halved else 1.0)
            shares = min(risk_budget / risk_per_share, slot / fill,
                         account_equity * cap_pct / fill, cash / fill)
            if shares * fill < 1.0:
                continue
            cash -= shares * fill
            positions[sig.symbol] = Position(sig.symbol, date, fill, shares, sig.stop, sig.stop,
                                             sig.target, sig.setup, fill)
        pending = []

        # 3. Intraday: resting stop and target orders.
        for pos in list(positions.values()):
            row = rows[pos.symbol]
            if np.isnan(row["low"]):
                continue
            if row["low"] <= pos.stop:
                price = pos.stop if date == pos.entry_date else min(row["open"], pos.stop)
                close_position(pos, date, price, "stop")
            elif pos.target is not None and row["high"] >= pos.target:
                price = pos.target if date == pos.entry_date else max(row["open"], pos.target)
                close_position(pos, date, price, "target")

        # 4. Close: mark to market, drawdown tiers, trail stops, close-based exits.
        for s, row in rows.items():
            if not np.isnan(row["close"]):
                last_close[s] = row["close"]
        equity = cash + sum(p.shares * last_close[p.symbol] for p in positions.values())
        equity_curve.append(equity)
        if positions:
            days_exposed += 1
        hwm = max(hwm, equity)
        dd = 1 - equity / hwm
        if not killed and dd >= limits.dd_kill:
            killed = True
            events.append(f"{date.date()}: KILL SWITCH at {dd:.0%} drawdown, all positions closed")
            for pos in list(positions.values()):
                pos.exit_next_open = True
                pos.exit_reason = "kill switch"
        elif not halved and dd >= limits.dd_halve_size:
            halved = True
            events.append(f"{date.date()}: drawdown {dd:.0%}, new position sizes halved")
        elif halved and dd < limits.dd_halve_size:
            halved = False
            events.append(f"{date.date()}: drawdown back under {limits.dd_halve_size:.0%}, full size")

        for pos in positions.values():
            row = rows[pos.symbol]
            if np.isnan(row["close"]):
                continue
            pos.highest_close = max(pos.highest_close, row["close"])
            pos.stop = max(pos.stop, rules.trail_stop(pos, row))  # stops only move up
            if not pos.exit_next_open and rules.exit_on_close(pos, row):
                pos.exit_next_open = True

        # 5. New entry signals for tomorrow.
        if killed or i == len(index) - 1:
            continue
        candidates = []
        for s in rules.universe:
            if s in positions or s not in frames or not rules.allowed(s, positions):
                continue
            sig = rules.entry_signal(s, frames, i)
            if sig is not None:
                candidates.append(sig)
        candidates.sort(key=lambda c: c.score, reverse=True)
        slots = rules.max_positions - len(positions)
        chosen: list[Signal] = []
        for c in candidates:
            if len(chosen) >= min(slots, limits.max_new_entries_per_day):
                break
            if rules.allowed(c.symbol, {**positions, **{x.symbol: None for x in chosen}}):
                chosen.append(c)
        pending = [(c, rows[c.symbol]["close"] * (1 + costs.limit_offset)) for c in chosen]

    # Mark open positions at the last close (not sold: the curve already values them).
    eq = pd.Series(equity_curve, index=index, name=rules.name)
    for pos in positions.values():
        trades.append(Trade(pos.symbol, pos.setup, pos.entry_date, pos.entry, index[-1],
                            last_close[pos.symbol], pos.shares, pos.initial_stop, "open at end"))
    return Result(rules.name, eq, trades, events, days_exposed / max(len(index), 1))


def buy_and_hold(bars: pd.DataFrame, index: pd.DatetimeIndex, initial: float, name: str) -> pd.Series:
    close = bars["close"].reindex(index).ffill().bfill()
    return (initial * close / close.iloc[0]).rename(name)
