"""Daily dry-run: the full system on live data, with NO orders placed.

Each run downloads fresh daily bars, replays every sleeve from the dry-run start date
(identical to stepping forward one day at a time, since the engine never looks ahead), then:
  * appends any new hypothetical entries/exits to trade_journal.md (with size math),
  * writes/updates today's row in equity_log.csv,
  * writes reports/daily/<date>.md: a 5-line summary plus the orders it would place next session.

Run after the US close (it drops any bar that isn't finished yet):
    python dry_run.py
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from backtest import data, engine
from backtest.sleeves import CoreGrowth, CryptoTrend, SwingMomentum
from backtest.universe import CORE_UNIVERSE, CRYPTO_ALTS, CRYPTO_MAJORS, SWING_UNIVERSE
from run_backtest import CRYPTO_COSTS, STOCK_COSTS

ROOT = Path(__file__).resolve().parent
START = "2026-11-02"           # first dry-run session
TRADING_DAYS = 10              # two weeks
CAPITAL = 3000.0               # hypothetical, from config.yaml
STATE = ROOT / "state" / "journaled.json"
JOURNAL = ROOT / "trade_journal.md"
EQUITY_LOG = ROOT / "equity_log.csv"
DAILY_DIR = ROOT / "reports" / "daily"
ET = ZoneInfo("America/New_York")
PAPER_ONLY = {"Swing momentum"}  # failed its backtest: tracked on paper, never traded live


def last_complete_stock_session(now_et: datetime) -> pd.Timestamp:
    d = now_et.date()
    if now_et.hour < 16 or (now_et.hour == 16 and now_et.minute < 15):
        d -= timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return pd.Timestamp(d)


def load_fresh(symbols, now_utc: datetime, log: list[str]) -> dict[str, pd.DataFrame]:
    failed = data.fetch_yahoo(symbols, "2025-06-01")
    if failed:
        log.append(f"download failed for {failed}: those symbols are skipped today")
    today_utc = pd.Timestamp(now_utc.date())
    now_et = now_utc.astimezone(ET)
    bars = {}
    for s in symbols:
        if s in failed:
            continue
        try:
            df = data.load_bars(s)
        except (OSError, ValueError) as exc:
            log.append(f"{s}: bad data ({exc}), skipped")
            continue
        if s.endswith("-USD"):
            df = df[df.index < today_utc]  # today's UTC candle is still forming
        elif df.index[-1].date() == now_et.date() and last_complete_stock_session(now_et) < df.index[-1]:
            df = df.iloc[:-1]  # today's stock bar before the close
        jump = df["close"].pct_change().abs().iloc[-1]
        if jump > 0.5:
            log.append(f"{s}: last close moved {jump:.0%} in a day; looks wrong, skipped")
            continue
        bars[s] = df
    return bars


def journal_entry(sleeve: str, t: engine.Trade, kind: str) -> str:
    paper = " · PAPER ONLY" if sleeve in PAPER_ONLY else ""
    if kind == "ENTRY":
        risk = t.entry - t.initial_stop
        return (f"\n## {t.entry_date.date()} · {t.symbol} · ENTRY · {sleeve} · DRY RUN{paper}\n"
                f"- Signal: {t.note}\n"
                f"- Entry / Stop / Target: ${t.entry:,.2f} / ${t.initial_stop:,.2f} / "
                f"{'none (trend exit)' if sleeve != 'Swing momentum' else f'${t.entry + 2 * risk:,.2f} (2R)'}"
                f"  (risk ${risk:,.2f} per share, {risk / t.entry:.1%})\n"
                f"- Size math: {t.sizing}\n"
                f"- Earnings in window: _check at entry_\n"
                f"- Order: limit buy, simulated fill ${t.entry:,.2f} ({t.shares:,.4f} units)\n"
                f"- Lesson: _to be written_\n")
    return (f"\n## {t.exit_date.date()} · {t.symbol} · EXIT · {sleeve} · DRY RUN{paper}\n"
            f"- Reason: {t.reason}\n"
            f"- Entry {t.entry_date.date()} ${t.entry:,.2f} -> exit ${t.exit:,.2f}\n"
            f"- Outcome: {t.pnl:+,.2f} ({t.exit / t.entry - 1:+.1%}), {t.r_multiple:+.2f}R, "
            f"{(t.exit_date - t.entry_date).days} days held\n"
            f"- Lesson: _to be written_\n")


def main(now_utc: datetime | None = None) -> str:
    now_utc = now_utc or datetime.now(timezone.utc)
    log: list[str] = []
    symbols = sorted(set(CORE_UNIVERSE + SWING_UNIVERSE + CRYPTO_MAJORS + CRYPTO_ALTS + ["QQQ"]))
    bars = load_fresh(symbols, now_utc, log)

    expected = last_complete_stock_session(now_utc.astimezone(ET))
    stocks_fresh = "QQQ" in bars and bars["QQQ"].index[-1] >= expected
    if not stocks_fresh:
        log.append(f"QQQ has no bar for {expected.date()} (market holiday or stale data): "
                   "stock sleeves not updated today")
    crypto_fresh = "BTC-USD" in bars and bars["BTC-USD"].index[-1] >= pd.Timestamp(now_utc.date()) - pd.Timedelta(days=1)
    if not crypto_fresh:
        log.append("BTC data is stale: crypto sleeve not updated today")

    sleeves = [
        (CoreGrowth([s for s in CORE_UNIVERSE if s in bars]), STOCK_COSTS),
        (SwingMomentum([s for s in SWING_UNIVERSE if s in bars]), STOCK_COSTS),
        (CryptoTrend([s for s in CRYPTO_MAJORS if s in bars], [s for s in CRYPTO_ALTS if s in bars]), CRYPTO_COSTS),
    ]
    started = {name: sym in bars and bars[sym].index[-1] >= pd.Timestamp(START)
               for name, sym in (("stocks", "QQQ"), ("crypto", "BTC-USD"))}
    if not any(started.values()):
        msg = f"Dry run starts {START}; no session to process yet."
        print(msg)
        return msg
    results = {}
    for rules, costs in sleeves:
        kind = "crypto" if rules.name == "Crypto" else "stocks"
        if not started[kind] or (kind == "crypto" and not crypto_fresh) or (kind == "stocks" and not stocks_fresh):
            continue
        results[rules.name] = engine.run(rules, bars, CAPITAL * rules.sleeve_share, engine.Limits(),
                                         costs, start=START)

    # Journal: append entries and exits not written before.
    done = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    new = []
    for name, res in results.items():
        for t in sorted(res.trades, key=lambda t: t.entry_date):
            k = f"{name}|{t.symbol}|{t.entry_date.date()}"
            if f"{k}|ENTRY" not in done:
                new.append((t.entry_date, journal_entry(name, t, "ENTRY"))); done.add(f"{k}|ENTRY")
            if t.reason != "open at end" and f"{k}|EXIT" not in done:
                new.append((t.exit_date, journal_entry(name, t, "EXIT"))); done.add(f"{k}|EXIT")
    if new:
        text = JOURNAL.read_text().replace("\n_No trades yet. Account unfunded; system in setup._\n", "")
        JOURNAL.write_text(text + "".join(e for _, e in sorted(new, key=lambda x: x[0])))
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(sorted(done), indent=0))

    # Account totals (sleeves not updated today keep their last value).
    if not results:
        summary = "No update today: " + "; ".join(log)
        print(summary)
        return summary
    eq = {n: r.equity.iloc[-1] for n, r in results.items()}
    for rules, _ in sleeves:
        eq.setdefault(rules.name, CAPITAL * rules.sleeve_share)
    equity = sum(eq.values())
    curves = [r.equity for r in results.values()]
    days = sorted(set().union(*(c.index for c in curves)))
    combined = sum(c.reindex(days).ffill().fillna(c.iloc[0]) for c in curves) + sum(
        CAPITAL * rules.sleeve_share for rules, _ in sleeves if rules.name not in results)
    hwm = max(CAPITAL, combined.max())
    dd = 1 - equity / hwm
    session = expected.date() if stocks_fresh else (now_utc.date() - timedelta(days=1))
    sessions_done = len(bars["QQQ"].loc[START:]) if "QQQ" in bars else 0

    qqq = bars["QQQ"]["close"].iloc[-1] if "QQQ" in bars else ""
    btc = bars["BTC-USD"]["close"].iloc[-1] if "BTC-USD" in bars else ""
    row = {"date": str(session), "mode": "dry_run", "equity_usd": f"{equity:.2f}",
           "cash_settled_usd": f"{sum(r.cash for r in results.values()):.2f}",
           "cash_unsettled_usd": f"{sum(r.unsettled for r in results.values()):.2f}",
           "stocks_usd": f"{eq['Core growth'] + eq['Swing momentum']:.2f}",
           "crypto_usd": f"{eq['Crypto']:.2f}", "high_water_mark_usd": f"{hwm:.2f}",
           "drawdown_pct": f"{dd:.2%}", "qqq_close": f"{qqq:.2f}" if qqq != "" else "",
           "btc_close": f"{btc:.2f}" if btc != "" else "",
           "notes": f"hypothetical ${CAPITAL:,.0f}; swing is paper-only"}
    rows = list(csv.DictReader(EQUITY_LOG.open())) if EQUITY_LOG.exists() else []
    rows = [r for r in rows if not (r["date"] == row["date"] and r["mode"] == "dry_run")] + [row]
    with EQUITY_LOG.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row)); w.writeheader(); w.writerows(rows)

    # Daily report.
    open_pos = [(n, p) for n, r in results.items() for p in r.open_positions]
    pending = [(n, sig, lim) for n, r in results.items() for sig, lim in r.pending_orders]
    start_q = bars["QQQ"].loc[START:, "close"] if "QQQ" in bars else pd.Series(dtype=float)
    start_b = bars["BTC-USD"].loc[START:, "close"] if "BTC-USD" in bars else pd.Series(dtype=float)
    q_ret = start_q.iloc[-1] / start_q.iloc[0] - 1 if len(start_q) > 1 else 0.0
    b_ret = start_b.iloc[-1] / start_b.iloc[0] - 1 if len(start_b) > 1 else 0.0
    lines = [
        f"1. Dry-run day {sessions_done} of {TRADING_DAYS} ({session}): hypothetical equity ${equity:,.2f} "
        f"({equity / CAPITAL - 1:+.2%} since start); QQQ {q_ret:+.2%}, BTC {b_ret:+.2%}.",
        f"2. Sleeves: core ${eq['Core growth']:,.2f}, swing (paper only) ${eq['Swing momentum']:,.2f}, "
        f"crypto ${eq['Crypto']:,.2f}.",
        f"3. New journal entries today: {len(new)}. Open positions: "
        + (", ".join(f"{p.symbol} (stop ${p.stop:,.2f})" for _, p in open_pos) or "none") + ".",
        f"4. Would place next session: "
        + (", ".join(f"{s.symbol} limit ${lim:,.2f}, stop ${s.stop:,.2f}" for _, s, lim in pending) or "nothing") + ".",
        f"5. Risk: drawdown {dd:.1%} from high-water mark ${hwm:,.2f}"
        + (" — WARNING tier (25%+)" if dd >= 0.25 else "") + (" — KILL SWITCH tier (50%+)" if dd >= 0.5 else "")
        + (f". Data issues: {'; '.join(log)}" if log else ". Data checks passed."),
    ]
    events = [f"- {n}: {e}" for n, r in results.items() for e in r.events]
    report = [f"# Dry run · {session}", "", *lines, "", "## Orders it would place next session", ""]
    report += [f"- {s.symbol} ({n}{', PAPER ONLY' if n in PAPER_ONLY else ''}): buy limit ${lim:,.2f}, "
               f"stop ${s.stop:,.2f}" + (f", target ${s.target:,.2f}" if s.target else "") +
               f". {s.note}. **Check earnings before a stock entry.**" for n, s, lim in pending] or ["- none"]
    report += ["", "## Drawdown-tier events", "", *(events or ["- none"])]
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    (DAILY_DIR / f"{session}.md").write_text("\n".join(report) + "\n")
    summary = "\n".join(lines)
    print(summary)
    return summary


if __name__ == "__main__":
    main()
