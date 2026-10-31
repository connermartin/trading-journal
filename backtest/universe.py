"""Trading universes.

SWING_UNIVERSE is the Nasdaq-100 as it stood in January 2021 (after the December 2020
reconstitution), so the backtest cannot "know" which stocks went on to win. It was rebuilt
from memory because no index-history source is reachable here, so a few names may be off.

Known gaps:
  * Members later acquired or delisted have no price data on Yahoo and are left out
    (ALXN, MXIM, XLNX, CERN, SPLK, ATVI, CTXS, SGEN, ANSS, WBA). The effect is small
    and could go either way.
  * Renamed tickers use today's symbol (FB -> META).
  * Market cap > $2B is not checked historically; every 2021 member was far above it.
  * Non-growth members (utilities, staples) are kept: the strength ranking filters them out.
"""

NASDAQ100_JAN2021 = [
    "AAPL", "MSFT", "AMZN", "TSLA", "META", "GOOGL", "NVDA", "PYPL", "ADBE", "CMCSA",
    "NFLX", "INTC", "PEP", "CSCO", "AVGO", "QCOM", "TXN", "COST", "TMUS", "AMGN",
    "CHTR", "SBUX", "INTU", "AMD", "ISRG", "JD", "MDLZ", "BKNG", "GILD", "ADP",
    "MU", "ZM", "FISV", "LRCX", "CSX", "ADSK", "VRTX", "MELI", "ILMN", "AMAT",
    "REGN", "PDD", "MRNA", "ADI", "ASML", "BIDU", "NXPI", "KDP", "LULU", "DOCU",
    "MNST", "KLAC", "EXC", "EA", "IDXX", "CTSH", "DXCM", "ALGN", "XEL",
    "KHC", "ORLY", "SNPS", "ROST", "PAYX", "CDNS", "MAR", "BIIB", "CTAS", "EBAY",
    "NTES", "PCAR", "WDAY", "MCHP", "SWKS", "VRSK", "CPRT", "OKTA", "TCOM", "FAST",
    "DLTR", "PTON", "CDW", "VRSN", "CHKP", "INCY", "TTWO", "FOXA",
    "BMRN", "MTCH", "AEP", "LBTYK", "SIRI",
]

SWING_UNIVERSE = NASDAQ100_JAN2021
CORE_UNIVERSE = ["QQQ", "SMH", "XLK", "IGV"]
CRYPTO_MAJORS = ["BTC-USD", "ETH-USD"]
CRYPTO_ALTS = ["SOL-USD", "XRP-USD", "BNB-USD"]
