# Dry run final report · 2026-11-02 to 2026-11-13

**Everything here is hypothetical.** No orders were placed and no money moved. The account is still unfunded.

## Results (10 trading days, hypothetical $3,000)

| Sleeve | Start | End | Return | Benchmark |
|---|---|---|---|---|
| Core growth (70%) | $2,100.00 | $2,091.48 | -0.41% | QQQ -0.18% (681.09 -> 679.89) |
| Crypto (30%) | $900.00 | $900.00 | 0.00% | BTC -10.99% (76,677 -> 68,249) |
| **Account total** | **$3,000.00** | **$2,991.48** | **-0.28%** | |
| Swing (separate paper $900, not in account) | $900.00 | $855.80 | -4.91% | QQQ -0.18% |

- High-water mark $3,017.00 (2026-11-04). Worst drawdown 2.19% (2026-11-05). Close: 0.85% below the high.
- No drawdown tier was hit (25% halve / 50% kill switch).
- Crypto made no trades: BTC and ETH never closed above a rising 50-day MA, so the sleeve stayed in cash and avoided BTC's 11% drop.
- QQQ cross-check against Robinhood passed every day (gap under 1%).

## Every trade

| # | Sleeve | Symbol | Entry | Exit | P&L | R |
|---|---|---|---|---|---|---|
| 1 | Core | IGV | 11-03 $101.05 | open (11-13 $101.16, stop $88.03) | about +$0.57 | — |
| 2 | Core | XLK | 11-03 $175.18 | 11-06 $166.88 (close under 200-day MA) | -$24.88 | -0.31 |
| 3 | Core | XLK | 11-10 $168.76 | 11-11 $173.69 (close under 200-day MA) | +$15.17 | +0.21 |
| 4 | Core | XLK | 11-12 $169.93 | open (11-13 $170.25, stop $148.21) | about +$0.99 | — |
| 5 | Core | QQQ | 11-12 $680.66 | open (11-13 $679.90, stop $586.82) | about -$0.59 | — |
| 6 | Swing paper | MAR | 11-03 $417.61 | open (11-13 $423.17) | about +$3.99 | — |
| 7 | Swing paper | ISRG | 11-05 $483.12 | 11-06 $451.57 (stop) | -$19.71 | -1.01 |
| 8 | Swing paper | CDW | 11-05 $169.68 | 11-06 $153.47 (stop) | -$28.49 | -1.00 |
| — | Swing paper | KDP | skipped 11-03 | earnings inside the holding window | — | — |

- Best: XLK 11-10 to 11-11, +$15.17 (+0.21R). Worst: CDW, -$28.49 (-1.00R).
- Core realized -$9.71; swing realized -$48.20. Open-position values are from Robinhood's last regular-session trades on 11-13.

## What was learned

1. **The risk rules worked as written.** Every loss stayed at or under 1R; the two swing stops each lost almost exactly the planned 1R.
2. **XLK whipsawed three times in ten days** because it sat right on its 200-day average. That cost about $10 in total. Expect this whenever price is near the line.
3. **Crypto's trend filter earned its keep.** Staying in cash beat BTC by about 11 points. Ten days is too short to treat this as an edge.
4. **Swing stayed weak on paper** (-4.9% vs QQQ -0.2%), which matches its failed backtest. Keep it paper only.
5. **The earnings rule fired once** (KDP was skipped), and its data came from Robinhood.
6. Ten days is far too short to judge returns. This run tested the plumbing, the sizing and the discipline, not profitability.

## Suggested changes (suggestions only; nothing was edited)

- **Label bug:** core exits are logged as "close below 50-day MA", but the code uses the approved 200-day MA (`backtest/engine.py:76` default label). Fix the label so the journal matches the rule.
- **Optional whipsaw filter:** to cut repeated XLK-style round trips, consider requiring 2 closes below the 200-day MA (or a 1% band) before exiting. This would need a backtest and your approval first.
- **Cross-check source:** Robinhood's official close lags by a session on weekends, so the cross-check should fall back to the last regular-session trade (as was done today).

## Going live

Nothing goes live automatically. Going live needs all three steps from you:
1. Approve the live version of the rules and config (`status.mode: live`, `live_approved: true`).
2. Fund the account (the starting equity and high-water mark get recorded that day).
3. Type **"go live"**.

Until then, `config.yaml` stays at `mode: dry_run` and no orders will be placed.
