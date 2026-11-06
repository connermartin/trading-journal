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
