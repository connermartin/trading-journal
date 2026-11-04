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
