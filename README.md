# Trading journal (private)

Rules, limits, backtests, and the record of every trade for my automated Robinhood system.

| File | What it is |
|---|---|
| `config.yaml` | Every hard limit and the system's current mode |
| `strategy.md` | The rules in plain English |
| `trade_journal.md` | Every entry and exit, with size math and one lesson |
| `equity_log.csv` | Daily equity, high-water mark, drawdown, benchmarks |
| `backtest/`, `run_backtest.py` | Backtester (`python run_backtest.py --fetch`) |
| `reports/` | Backtest, daily, and weekly reports |

Run the tests with `python -m pytest`.
