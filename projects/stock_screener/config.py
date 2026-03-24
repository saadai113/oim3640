"""
Configuration for the Undervalued Stock Screener.

REALITY CHECK:
- Most financial data APIs (Koyfin, SeekingAlpha, GuruFocus) require paid subscriptions
  and/or have aggressive anti-scraping measures. This tool uses FREE endpoints where
  available and clearly marks where you need API keys or subscriptions.
- Web scraping is fragile. Sites change layouts frequently. Expect breakage.
- SEC EDGAR and FRED are the only truly reliable free data sources here.
- For production use, pay for proper data feeds (e.g., FactSet, Bloomberg, Refinitiv).

API KEYS (set as environment variables):
    FRED_API_KEY        - Free from https://fred.stlouisfed.org/docs/api/api_key.html
    QUIVER_API_KEY      - From https://www.quiverquant.com/ (paid plans)
    FMP_API_KEY         - Financial Modeling Prep (free tier: 250 req/day)
                          https://financialmodelingprep.com/ — used as fallback for
                          forward P/E, comps, and earnings estimates since Koyfin/SA
                          require paid access or scraping that breaks constantly.
"""

import os

# ── Free & Reliable ──────────────────────────────────────────────────────────
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
SEC_EDGAR_USER_AGENT = os.environ.get(
    "SEC_EDGAR_USER_AGENT", "YourName your.email@example.com"
)

# ── Paid / Rate-Limited ──────────────────────────────────────────────────────
QUIVER_API_KEY = os.environ.get("QUIVER_API_KEY", "")
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")  # Financial Modeling Prep

# ── Request Settings ─────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15  # seconds
REQUEST_DELAY = 0.5   # seconds between requests (rate limiting)
SEC_RATE_LIMIT = 0.15 # SEC asks for max 10 req/sec; we do ~7

# ── Screening Thresholds ─────────────────────────────────────────────────────
# These are starting points. Adjust based on sector, market regime, etc.
THRESHOLDS = {
    "forward_pe_discount_vs_peers": -0.15,  # 15%+ cheaper than peer median
    "forward_pe_max": 25.0,                 # absolute ceiling
    "earnings_revision_positive": True,     # net upward revisions preferred
    "insider_net_buy_90d": True,            # net insider buying in 90 days
    "congressional_buy_signal": True,       # any congressional buys in 90 days
    "social_sentiment_floor": 0.4,          # 0-1 scale, avoid universally hated
}

# ── Sector → Peer Group Mapping ──────────────────────────────────────────────
# Used for comparable company analysis. Expand as needed.
SECTOR_PEERS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ORCL", "CRM", "ADBE"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "NVO", "AMGN"],
    "Financials": ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SCHW"],
    "Consumer Discretionary": ["AMZN", "TSLA", "HD", "NKE", "MCD", "SBUX", "TJX"],
    "Industrials": ["CAT", "HON", "UPS", "RTX", "GE", "DE", "LMT", "BA"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO"],
    "Consumer Staples": ["PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "CL"],
    "Communication Services": ["GOOGL", "META", "DIS", "NFLX", "T", "VZ", "CMCSA"],
    "Utilities": ["NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL"],
    "Real Estate": ["AMT", "PLD", "CCI", "EQIX", "SPG", "O", "PSA", "DLR"],
    "Materials": ["LIN", "APD", "SHW", "ECL", "NEM", "FCX", "NUE", "DD"],
}
