# Strategy

Status: **dry run** (2026-11-02 to 2026-11-13, hypothetical $3,000, no orders placed).
Rules approved 2026-10-31 after the backtest in `reports/backtest_2026-10-31_v1_original_rules.md and _v2_approved_rules.md`.
Every number referenced here lives in `config.yaml`.

## Big picture
- 70% stocks/ETFs (40% core growth + 30% swing momentum) and 30% crypto.
- Rebalance when either side drifts more than 10 points from 70/30.
- Every position has a stop at entry. Live, the stop is a real order resting at Robinhood,
  so it protects the account between scheduled checks. Stops only move up.
- **Swing is paper only.** It failed its fair backtest; it runs in the journal, not the account,
  until a revised version passes.

## Sleeve 1: Core growth (~40%)
- Holdings: up to 4 of QQQ, SMH, XLK, IGV, one slot each (10% of the account).
- Enter when the close is above the 200-day moving average.
- Exit on a close below the 200-day average (sold at the next open), or if the price falls
  15% below its highest close since entry (trailing stop).
- Why 200 and not 50 days: the 50-day rule whipsawed (272 trades, lost to QQQ on every
  setting tried). The 200-day rule matched QQQ's return with about half the drawdown in the
  backtest, but nearby settings (150, 250 days) did worse, so expect "QQQ with smaller crashes",
  not extra profit.

## Sleeve 2: Swing momentum (~30%, PAPER ONLY)
- Universe: the Nasdaq-100 as of January 2021, filtered to price > $5 and average volume
  > 1M shares. Each day only the 10 strongest names by 3-month return are tradable.
- Entry, with the 20-day MA above the 50-day MA and the stock beating QQQ over 3 months:
  - Breakout: close at a 20-day high on relative volume > 1.5; or
  - Pullback: RSI(14) recovers above 40 with the close within 3% of the 20-day MA.
- Stop: the tighter of the 10-day low or 2 x ATR(14) below entry. Target: 2R.
  After +1R the stop moves to breakeven, then trails 2 x ATR under the highest close.
- Backtest on the fair universe: +1.6% a year, Sharpe 0.18 (QQQ: +15.5%, 0.75). Not tradable.

## Sleeve 3: Crypto (~30%)
- Up to 3 positions: BTC, ETH, and at most one altcoin (SOL, XRP or BNB), so altcoins are
  never more than 1/3 of the sleeve.
- Enter when the close is above a rising 50-day MA (higher than 10 days ago). Altcoins also
  need a better 30-day return than BTC.
- Exit on a daily close below the 50-day MA, or a trailing stop 3 x ATR(14) under the
  highest close.
- Backtest: +26% a year, worst drop -42%, vs BTC +18% and -77%. The edge came from sitting
  out 2022; it lagged BTC badly in 2023-2024.

## Position sizing (applies to every trade)
1. Max risk = equity x 3%.
2. Shares = max risk / (entry - stop).
3. Cap at 20% of equity (15% for an altcoin) and at the sleeve's available settled cash.
4. Halve the size if earnings fall inside the expected holding window (or skip).
5. Halve all new sizes once the drawdown from the high-water mark reaches 25%; return to
   full size only after it recovers to under 15%.

## Hard stops on the system
- 50% drawdown from the high-water mark -> close everything, stop, notify, and wait for the owner.
- Bad data, a stale quote (> 5 min) or an order error -> do nothing and log it.
- Never: margin, options, leverage, shorting, deposits/withdrawals, account setting changes.
