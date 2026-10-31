"""Backtest all three sleeves against QQQ and BTC and write a markdown report.

Usage:
    python run_backtest.py --fetch            # download bars (needs network), then backtest
    python run_backtest.py                    # backtest using data/prices/*.csv
    python run_backtest.py --start 2021-01-01 --capital 3000
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from backtest import data, engine, report
from backtest.sleeves import CoreGrowth, CryptoTrend, SwingMomentum

from backtest.universe import CORE_UNIVERSE as CORE, CRYPTO_ALTS, CRYPTO_MAJORS, SWING_UNIVERSE as SWING

STOCK_COSTS = engine.Costs(slippage=0.0005, limit_offset=0.005)
CRYPTO_COSTS = engine.Costs(slippage=0.0050, limit_offset=0.005, settle_bars=0)  # ~0.5% spread per fill


def main(argv=None) -> Path:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download bars before testing")
    ap.add_argument("--start", default="2021-01-01", help="first trading day of the test")
    ap.add_argument("--capital", type=float, default=3000.0, help="hypothetical account size")
    ap.add_argument("--price-dir", type=Path, default=data.PRICE_DIR)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "reports")
    args = ap.parse_args(argv)

    symbols = sorted(set(CORE + SWING + CRYPTO_MAJORS + CRYPTO_ALTS))
    if args.fetch:
        warmup = (pd.Timestamp(args.start) - pd.Timedelta(days=200)).strftime("%Y-%m-%d")
        failed = data.fetch_yahoo(symbols, warmup, args.price_dir)
        if failed:
            print(f"Missing data for {failed}; those symbols are skipped.")
    bars = {}
    for s in symbols:
        try:
            bars[s] = data.load_bars(s, args.price_dir)
        except (OSError, ValueError) as exc:
            print(f"  skipping {s}: {exc}")
    for needed in ("QQQ", "BTC-USD"):
        if needed not in bars:
            raise SystemExit(f"{needed} data is required for the benchmarks.")

    limits = engine.Limits()
    sleeves = [
        (CoreGrowth([s for s in CORE if s in bars]), STOCK_COSTS, "QQQ", 252),
        (SwingMomentum([s for s in SWING if s in bars]), STOCK_COSTS, "QQQ", 252),
        (CryptoTrend([s for s in CRYPTO_MAJORS if s in bars], [s for s in CRYPTO_ALTS if s in bars]),
         CRYPTO_COSTS, "BTC-USD", 365),
    ]

    sections, curves, rows_perf, rows_trades = [], {}, [], []
    for rules, costs, bench, ppy in sleeves:
        capital = args.capital * rules.sleeve_share
        res = engine.run(rules, bars, capital, limits, costs, start=args.start)
        bh = engine.buy_and_hold(bars[bench], res.equity.index, capital, f"Hold {bench}")
        s_stats, b_stats = report.curve_stats(res.equity, ppy), report.curve_stats(bh, ppy)
        t_stats = report.trade_stats(res)
        curves[rules.name] = res.equity
        rows_perf += [(rules.name, s_stats), (f"Hold {bench}", b_stats)]
        rows_trades.append((rules.name, t_stats))
        beat = s_stats["sharpe"] > b_stats["sharpe"] and s_stats["return_per_drawdown"] > b_stats["return_per_drawdown"]
        sections.append((rules.name, capital, res, s_stats, b_stats, t_stats, beat))

    # Whole account: the three sleeves together vs. 70% QQQ / 30% BTC.
    days = curves["Core growth"].index
    account = sum(c.reindex(days).ffill() for c in curves.values()).dropna()
    blend = (engine.buy_and_hold(bars["QQQ"], account.index, args.capital * 0.7, "QQQ")
             + engine.buy_and_hold(bars["BTC-USD"], account.index, args.capital * 0.3, "BTC"))
    acct_stats, blend_stats = report.curve_stats(account, 252), report.curve_stats(blend, 252)

    first, last = days[0].date(), days[-1].date()
    out = [f"# Backtest report ({date.today()})", "",
           f"Period: {first} to {last}. Hypothetical account: ${args.capital:,.0f} "
           f"(core {0.4:.0%}, swing {0.3:.0%}, crypto {0.3:.0%}).", "",
           "## Whole account", "",
           report.comparison_table([("All three sleeves", acct_stats), ("70% QQQ / 30% BTC, held", blend_stats)]),
           "", "## Each sleeve vs. its benchmark", "",
           report.comparison_table(rows_perf), "", "## Trades", "", report.trade_table(rows_trades), ""]
    for name, capital, res, s, b, t, beat in sections:
        out += [f"### {name} (${capital:,.0f})",
                f"- Beats its benchmark on a risk-adjusted basis (Sharpe AND CAGR/MaxDD): **{'yes' if beat else 'NO'}**"]
        out += [f"- {e}" for e in res.events] or ["- No drawdown-tier events."]
        by_setup = pd.Series([tr.setup for tr in res.trades]).value_counts().to_dict()
        out += [f"- Trades by setup: {by_setup}", ""]
    out += ["## Caveats", "",
            "- Swing universe: Nasdaq-100 as of Jan 2021 (rebuilt from memory; acquired names missing), "
            "ranked daily by 3-month strength, top 10 tradable.",
            "- Earnings dates are not modelled; the live rule cuts size or skips around earnings.",
            "- Fills assume limit orders at the signal close +0.5%, with slippage of "
            f"{STOCK_COSTS.slippage:.2%} (stocks) and {CRYPTO_COSTS.slippage:.2%} (crypto) per fill.",
            "- Sharpe uses a 0% risk-free rate. Past results do not predict future results."]
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"backtest_{date.today()}.md"
    path.write_text("\n".join(out))
    print("\n".join(out))
    return path


if __name__ == "__main__":
    main()
