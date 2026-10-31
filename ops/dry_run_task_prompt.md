# Prompt for the "Trading dry run (daily)" scheduled task

Schedule: every day at 9:07 PM America/New_York. New session each run. Connector: Robinhood.

---

You are running one scheduled step of the owner's trading-system DRY RUN. HARD RULE: this is a dry run. NEVER place, cancel or change any order, never move money, never change account settings. Robinhood is used read-only (quotes, earnings dates) and only if its tools are available.

1. Attach and clone the private repo: call add_repo with owner "connermartin", repo "trading-journal", access "push", then clone it as that tool instructs (to /home/user/trading-journal). Read README.md, config.yaml and strategy.md.
2. If config.yaml shows status.mode is not "dry_run", or today's date (America/New_York) is after 2026-11-14, do nothing else: reply "Dry run is finished or paused; nothing to do." and stop.
3. Install deps (pip install -r requirements.txt) and run: python dry_run.py   (it downloads fresh daily bars, replays the rules from 2026-11-02, and updates trade_journal.md, equity_log.csv and reports/daily/<date>.md). If it fails or reports stale or wrong data, do not guess or fill numbers in: record the problem in that day's report and continue to step 7.
4. Cross-check data: if Robinhood tools are available, compare the latest QQQ and BTC closes in equity_log.csv with Robinhood quotes. A gap over 1% means the data is suspect: note it in the daily report as "data mismatch, results for today unreliable".
5. For each stock entry the daily report says it would place next session, check for earnings within the next 10 trading days (Robinhood earnings calendar if available). Note "earnings in window: yes -> half size or skip" or "no" in the daily report, and fill the matching "Earnings in window" line in trade_journal.md for entries dated today. If Robinhood is unavailable, write "earnings: not checked (no Robinhood access)".
6. Teaching: in trade_journal.md replace every "Lesson: _to be written_" with one concrete sentence a finance student should take from that trade (e.g. why the size was capped, what a gap through a stop costs, what the R-multiple says). Keep the rest of each entry unchanged.
7. If today (America/New_York) is Saturday, also write reports/weekly/<date>.md: hypothetical P&L by sleeve vs QQQ and BTC since 2026-11-02, best and worst trades, rule changes you would suggest (suggest only; never edit config.yaml or rules), and one concept explained simply (position sizing, expectancy, drawdown math, settlement, etc.). On Saturday 2026-11-14 write reports/dry_run_final.md instead: the full hypothetical results, every trade, what was learned, and a clear note that going live needs the owner to fund the account and type "go live".
8. Commit with a short message and push to main of connermartin/trading-journal (end the commit message with the line: Co-Authored-By: Claude <noreply@anthropic.com>).
9. Your final reply is the notification the owner reads on their phone: the 5-line summary from the daily report (plus one line if a weekly or final report was written, or if anything went wrong). Nothing else.
