# Backtest report v1: original draft rules (2026-10-31)

Period: 2021-01-04 to 2026-10-30. Hypothetical account: $3,000 (core 40%, swing 30%, crypto 30%).

## Whole account

| | Total return | CAGR | Volatility | Sharpe | Max drawdown | CAGR / MaxDD |
|---|---|---|---|---|---|---|
| All three sleeves | +140.7% | +16.3% | 19.3% | 0.88 | -29.2% | 0.56 |
| 70% QQQ / 30% BTC, held | +134.0% | +15.8% | 28.1% | 0.66 | -51.2% | 0.31 |

## Each sleeve vs. its benchmark

| | Total return | CAGR | Volatility | Sharpe | Max drawdown | CAGR / MaxDD |
|---|---|---|---|---|---|---|
| Core growth | +47.3% | +6.9% | 14.7% | 0.53 | -20.5% | 0.34 |
| Hold QQQ | +130.8% | +15.5% | 22.4% | 0.75 | -35.1% | 0.44 |
| Swing momentum | +168.6% | +18.6% | 20.3% | 0.94 | -28.0% | 0.66 |
| Hold QQQ | +130.8% | +15.5% | 22.4% | 0.75 | -35.1% | 0.44 |
| Crypto | +277.3% | +25.6% | 33.6% | 0.85 | -43.6% | 0.59 |
| Hold BTC-USD | +163.4% | +18.1% | 56.7% | 0.58 | -76.6% | 0.24 |

## Trades

| | Trades | Win rate | Avg win | Avg loss | Expectancy (R) | Avg days held | Time invested |
|---|---|---|---|---|---|---|---|
| Core growth | 272 | 40% | $18 (+5.2%) | $-9 (-2.3%) | +0.20 | 17 | 70% |
| Swing momentum | 200 | 50% | $44 (+9.5%) | $-29 (-6.2%) | +0.25 | 17 | 80% |
| Crypto | 202 | 31% | $119 (+27.4%) | $-35 (-6.4%) | +0.28 | 15 | 62% |

### Core growth ($1,200)
- Beats its benchmark on a risk-adjusted basis (Sharpe AND CAGR/MaxDD): **NO**
- No drawdown-tier events.
- Trades by setup: {'trend': 272}

### Swing momentum ($900)
- Beats its benchmark on a risk-adjusted basis (Sharpe AND CAGR/MaxDD): **yes**
- 2022-12-15: drawdown 26%, new position sizes halved
- 2023-01-06: drawdown back under 25%, full size
- 2023-01-09: drawdown 25%, new position sizes halved
- 2023-01-23: drawdown back under 25%, full size
- 2023-01-30: drawdown 25%, new position sizes halved
- 2023-01-31: drawdown back under 25%, full size
- 2023-02-21: drawdown 27%, new position sizes halved
- 2023-03-14: drawdown back under 25%, full size
- Trades by setup: {'breakout': 173, 'pullback': 28}

### Crypto ($900)
- Beats its benchmark on a risk-adjusted basis (Sharpe AND CAGR/MaxDD): **yes**
- 2021-05-21: drawdown 27%, new position sizes halved
- 2021-08-20: drawdown back under 25%, full size
- 2021-08-21: drawdown 26%, new position sizes halved
- 2021-08-23: drawdown back under 25%, full size
- 2021-08-24: drawdown 27%, new position sizes halved
- 2021-09-01: drawdown back under 25%, full size
- 2021-09-07: drawdown 27%, new position sizes halved
- 2021-10-20: drawdown back under 25%, full size
- 2021-10-22: drawdown 25%, new position sizes halved
- 2021-10-23: drawdown back under 25%, full size
- 2021-10-27: drawdown 27%, new position sizes halved
- 2021-10-28: drawdown back under 25%, full size
- 2021-11-18: drawdown 27%, new position sizes halved
- 2023-11-09: drawdown back under 25%, full size
- 2024-04-13: drawdown 25%, new position sizes halved
- 2024-04-22: drawdown back under 25%, full size
- 2024-04-26: drawdown 25%, new position sizes halved
- 2024-04-28: drawdown back under 25%, full size
- 2024-04-29: drawdown 25%, new position sizes halved
- 2024-11-21: drawdown back under 25%, full size
- 2024-11-25: drawdown 27%, new position sizes halved
- 2024-11-27: drawdown back under 25%, full size
- 2024-11-28: drawdown 25%, new position sizes halved
- 2024-11-29: drawdown back under 25%, full size
- 2024-12-02: drawdown 26%, new position sizes halved
- 2024-12-06: drawdown back under 25%, full size
- 2024-12-09: drawdown 27%, new position sizes halved
- Trades by setup: {'trend': 202}

## Caveats

- The swing list is today's leaders, so it suffers from survivorship bias (it flatters past results).
- Earnings dates are not modelled; the live rule cuts size or skips around earnings.
- Fills assume limit orders at the signal close +0.5%, with slippage of 0.05% (stocks) and 0.50% (crypto) per fill.
- Sharpe uses a 0% risk-free rate. Past results do not predict future results.
## Robustness checks

### Calendar-year returns (%)
| Year | Core | Swing | QQQ | Crypto | BTC |
|---|---|---|---|---|---|
| 2021 | +3.7 | +32.0 | +29.2 | +139.2 | +57.6 |
| 2022 (bear) | -14.5 | -25.0 | -32.6 | -15.3 | -64.3 |
| 2023 | +37.2 | +42.5 | +54.9 | +85.8 | +155.4 |
| 2024 | +11.4 | +22.8 | +25.6 | -3.8 | +121.1 |
| 2025 | +4.7 | +16.9 | +20.8 | +1.2 | -6.3 |
| 2026 YTD | +3.9 | +32.6 | +12.8 | +3.0 | -11.6 |

### Swing: survivorship test
Profit by symbol is concentrated: MU, CRWD, NVDA, AMD and NFLX earned more than the whole sleeve's net profit.
Without those five: CAGR +5.1%, Sharpe 0.37, max drawdown -26.3%, well below holding QQQ.
**Verdict: the swing edge is not proven.** Most of it came from picking today's winners with hindsight.

### Core: parameter checks
Exit buffers (0-5% below the 50-day MA) and trailing stops (2.5-5 ATR) all give CAGR 6.7-7.7% and Sharpe 0.48-0.54,
versus QQQ at 15.5% / 0.75. The 50-day rule loses on every setting tried, so this is not a tuning problem.

Slower alternative (hold while above the N-day MA, percentage trailing stop):
| MA | Trail 12% | Trail 15% | Trail 20% |
|---|---|---|---|
| 150-day | Sharpe 0.69 / DD -23.8% | 0.68 / -24.0% | 0.75 / -24.0% |
| 200-day | 0.90 / -17.9% | 0.90 / -19.2% | 0.97 / -18.8% |
| 250-day | 0.80 / -24.8% | 0.77 / -26.5% | 0.87 / -26.1% |
200-day looks best, but 150 and 250 are clearly worse, so part of that is luck. Averaged over the neighbours it is
about QQQ's Sharpe with a smaller drawdown: a defensive rule, not a proven edge.

### Crypto
Beat BTC on a risk-adjusted basis mainly by sitting out 2022 (-15% vs -64%), but lagged badly in 2023-2024
(2024: -3.8% vs +121%). Its edge is avoiding crashes, and it pays for that by missing big rallies.
The 25% size-halving tier switched on and off many times around the threshold; it needs a recovery buffer.
