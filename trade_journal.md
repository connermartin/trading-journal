# Trade Journal

Every entry and exit, real or dry-run, gets an entry here in this format:

```
## YYYY-MM-DD HH:MM ET · TICKER · ENTRY|EXIT · sleeve · [DRY RUN|LIVE]
- Signal: what triggered it, with the indicator values
- Entry / Stop / Target: $x / $y / $z  (risk per share $x - $y)
- Size math: equity $E x 3% = max risk $R; $R / risk per share = N shares;
  capped by 20% position limit at M shares -> N used
- Earnings in window: yes/no
- Order: type, limit price, order id, fill
- Outcome (on exit): P&L $ and %, R-multiple, days held
- Lesson: one sentence
```

---

## 2026-11-03 · IGV · ENTRY · Core growth · DRY RUN
- Signal: close 101.90 > 200-day MA 93.96
- Entry / Stop / Target: $101.05 / $86.62 / none (trend exit)  (risk $14.44 per share, 14.3%)
- Size math: account $3,000 x 3% = risk $90; / $14.44 risk per share = 6.235; slot $525 = 5.195; 20% cap = 5.938; settled cash $1,575 = 15.586 -> 5.1954 used ($525)
- Earnings in window: no (ETF, no single-company earnings)
- Order: limit buy, simulated fill $101.05 (5.1954 units)
- Lesson: Buying an index-style ETF only after it closes above its 200-day average keeps you with the long-term trend, but a 14% stop shows how much room a trend trade needs, so size the position to the stop, not the other way round.

## 2026-11-03 · XLK · ENTRY · Core growth · DRY RUN
- Signal: close 174.22 > 200-day MA 169.38
- Entry / Stop / Target: $175.18 / $148.09 / none (trend exit)  (risk $27.09 per share, 15.5%)
- Size math: account $3,000 x 3% = risk $90; / $27.09 risk per share = 3.322; slot $525 = 2.997; 20% cap = 3.425; settled cash $1,050 = 5.994 -> 2.9969 used ($525)
- Earnings in window: no (ETF, no single-company earnings)
- Order: limit buy, simulated fill $175.18 (2.9969 units)
- Lesson: A wide stop (15.5% here) forces a small share count: the 3% risk rule sets position size from the stop distance, which is why volatile trades get smaller positions.

## 2026-11-03 · MAR · ENTRY · Swing momentum · DRY RUN · PAPER ONLY
- Signal: breakout: close 416.30, 20-day high 416.30, MA20 385.26 > MA50 361.40, RSI 75, rel. volume 1.8, 3-mo return +20.8% vs QQQ -5.8% (strength rank 7)
- Entry / Stop / Target: $417.61 / $396.65 / $459.53 (2R)  (risk $20.96 per share, 5.0%)
- Size math: account $3,000 x 3% = risk $90; / $20.96 risk per share = 4.294; slot $300 = 0.718; 20% cap = 1.437; settled cash $600 = 1.437 -> 0.7184 used ($300)
- Earnings in window: no (last report 2026-11-02, next 2027-02-09 per state/earnings.json)
- Order: limit buy, simulated fill $417.61 (0.7184 units)
- Lesson: Breakouts with high relative strength can keep running, but a 75 RSI means you are paying up; the 2R target and tight stop cap the loss at a known amount if it fails.

## 2026-11-05 · ISRG · ENTRY · Swing momentum · DRY RUN · PAPER ONLY
- Signal: breakout: close 482.10, 20-day high 482.10, MA20 437.07 > MA50 406.25, RSI 73, rel. volume 1.9, 3-mo return +29.0% vs QQQ -3.1% (strength rank 5)
- Entry / Stop / Target: $483.12 / $451.80 / $545.77 (2R)  (risk $31.33 per share, 6.5%)
- Size math: account $3,017 x 3% = risk $91; / $31.33 risk per share = 2.890; slot $302 = 0.625; 20% cap = 1.249; settled cash $298 = 0.617 -> 0.6246 used ($302)
- Earnings in window: no (last report 2026-10-20, next 2027-01-21 per state/earnings.json)
- Order: limit buy, simulated fill $483.12 (0.6246 units)
- Lesson: A stop 6.5% below entry means the share count is set by the dollar risk you accept, not by how much you like the stock, so a wider stop automatically shrinks the position.

## 2026-11-05 · CDW · ENTRY · Swing momentum · DRY RUN · PAPER ONLY
- Signal: breakout: close 168.75, 20-day high 168.75, MA20 155.19 > MA50 148.23, RSI 64, rel. volume 2.1, 3-mo return +19.4% vs QQQ -3.1% (strength rank 10)
- Entry / Stop / Target: $169.68 / $153.55 / $201.94 (2R)  (risk $16.13 per share, 9.5%)
- Size math: account $3,017 x 3% = risk $91; / $16.13 risk per share = 5.613; slot $302 = 1.778; 20% cap = 3.557; settled cash $0 = 0.000 -> 1.7578 used ($298)
- Earnings in window: no (last report 2026-11-04, next 2027-02-03 per state/earnings.json)
- Order: limit buy, simulated fill $169.68 (1.7578 units)
- Lesson: A 9.5% stop is wide, so the same 3% risk budget buys fewer dollars of stock; buying right after a report (CDW reported yesterday) also means the biggest scheduled surprise has already passed.

## 2026-11-06 · XLK · EXIT · Core growth · DRY RUN
- Reason: close below 50-day MA
- Entry 2026-11-03 $175.18 -> exit $166.88
- Outcome: -24.88 (-4.7%), -0.31R, 3 days held
- Lesson: A small loss taken when the rule says exit is the system working: you cap the damage at a fraction of one risk unit (-0.31R) instead of hoping the trade recovers.

## 2026-11-06 · ISRG · EXIT · Swing momentum · DRY RUN · PAPER ONLY
- Reason: stop
- Entry 2026-11-05 $483.12 -> exit $451.57
- Outcome: -19.71 (-6.5%), -1.01R, 1 days held
- Lesson: A stop only protects you if you honor it: this one-day loss of about 1R is exactly the loss that was planned at entry, which is why sizing by risk matters more than predicting direction.

## 2026-11-06 · CDW · EXIT · Swing momentum · DRY RUN · PAPER ONLY
- Reason: stop
- Entry 2026-11-05 $169.68 -> exit $153.47
- Outcome: -28.49 (-9.6%), -1.00R, 1 days held
- Lesson: Stops can fill at or near the planned level when price gaps through it; a -1.00R result right after entry shows a breakout can fail immediately, and the fixed risk budget is what kept it small.

## 2026-11-10 · XLK · ENTRY · Core growth · DRY RUN
- Signal: close 170.88 > 200-day MA 170.04
- Entry / Stop / Target: $168.76 / $145.25 / none (trend exit)  (risk $23.52 per share, 13.9%)
- Size math: account $2,967 x 3% = risk $89; / $23.52 risk per share = 3.786; slot $519 = 3.077; 20% cap = 3.517; settled cash $1,031 = 6.108 -> 3.0771 used ($519)
- Earnings in window: no (ETF, no single-company earnings)
- Order: limit buy, simulated fill $168.76 (3.0771 units)
- Lesson: Re-entering soon after a trend exit is normal for a trend rule: XLK closed back above its 200-day average, so the system buys again with a fresh stop, accepting that some whipsaw losses are the price of staying with the trend.
