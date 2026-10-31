"""Performance statistics for strategies and benchmarks."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import Result


def curve_stats(equity: pd.Series, periods_per_year: int) -> dict:
    rets = equity.pct_change().dropna()
    years = max(len(equity) - 1, 1) / periods_per_year
    total = equity.iloc[-1] / equity.iloc[0] - 1
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1 if years > 0 else np.nan
    vol = rets.std() * np.sqrt(periods_per_year)
    sharpe = rets.mean() / rets.std() * np.sqrt(periods_per_year) if rets.std() > 0 else np.nan
    max_dd = (equity / equity.cummax() - 1).min()
    return {
        "total_return": total,
        "cagr": cagr,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "return_per_drawdown": cagr / abs(max_dd) if max_dd < 0 else np.nan,
    }


def trade_stats(result: Result) -> dict:
    closed = [t for t in result.trades if t.reason != "open at end"]
    if not closed:
        return {"trades": 0}
    pnl = np.array([t.pnl for t in closed])
    rs = np.array([t.r_multiple for t in closed])
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    return {
        "trades": len(closed),
        "win_rate": len(wins) / len(closed),
        "avg_win": wins.mean() if len(wins) else 0.0,
        "avg_loss": losses.mean() if len(losses) else 0.0,
        "avg_win_pct": np.mean([t.exit / t.entry - 1 for t in closed if t.pnl > 0] or [0]),
        "avg_loss_pct": np.mean([t.exit / t.entry - 1 for t in closed if t.pnl <= 0] or [0]),
        "expectancy_r": np.nanmean(rs),
        "avg_days_held": np.mean([(t.exit_date - t.entry_date).days for t in closed]),
        "exposure": result.exposure,
    }


def fmt_pct(x) -> str:
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.1%}"


def comparison_table(rows: list[tuple[str, dict]]) -> str:
    head = "| | Total return | CAGR | Volatility | Sharpe | Max drawdown | CAGR / MaxDD |\n|---|---|---|---|---|---|---|"
    lines = [head]
    for name, s in rows:
        lines.append(
            f"| {name} | {fmt_pct(s['total_return'])} | {fmt_pct(s['cagr'])} | {s['volatility']:.1%} | "
            f"{s['sharpe']:.2f} | {s['max_drawdown']:.1%} | {s['return_per_drawdown']:.2f} |"
        )
    return "\n".join(lines)


def trade_table(rows: list[tuple[str, dict]]) -> str:
    head = ("| | Trades | Win rate | Avg win | Avg loss | Expectancy (R) | Avg days held | Time invested |\n"
            "|---|---|---|---|---|---|---|---|")
    lines = [head]
    for name, s in rows:
        if s.get("trades", 0) == 0:
            lines.append(f"| {name} | 0 | | | | | | |")
            continue
        lines.append(
            f"| {name} | {s['trades']} | {s['win_rate']:.0%} | ${s['avg_win']:.0f} ({s['avg_win_pct']:+.1%}) | "
            f"${s['avg_loss']:.0f} ({s['avg_loss_pct']:+.1%}) | {s['expectancy_r']:+.2f} | "
            f"{s['avg_days_held']:.0f} | {s['exposure']:.0%} |"
        )
    return "\n".join(lines)
