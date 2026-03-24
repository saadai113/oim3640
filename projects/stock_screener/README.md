# Undervalued Stock Screener

Multi-source stock screening tool that aggregates signals from financial data APIs, SEC filings, alternative data, and macro indicators to surface potentially undervalued equities.

## What This Actually Does

Pulls data from multiple sources, normalizes each into a -1 to +1 signal, applies weighted scoring, and ranks stocks by composite score. It is a **screening tool** — it surfaces candidates for further research, not buy/sell recommendations.

## Data Sources

| Source | What It Provides | API Key Required | Reliability |
|---|---|---|---|
| **Financial Modeling Prep** | Forward P/E, comps, earnings estimates/revisions | `FMP_API_KEY` (free tier: 250 req/day) | ★★★★ Stable API |
| **SEC EDGAR** | 13F filings, company filings | `SEC_EDGAR_USER_AGENT` (free) | ★★★★★ Government API |
| **FRED** | Macro data (rates, CPI, unemployment, yield curve) | `FRED_API_KEY` (free) | ★★★★★ Government API |
| **OpenInsider** | Form 4 insider transactions | None (web scrape) | ★★★ Scraping breaks |
| **StockTwits** | Social sentiment | None (free API) | ★★★ Rate-limited |
| **QuiverQuant** | Congressional trades, gov contracts, patents, Reddit | `QUIVER_API_KEY` (paid) | ★★★★ Paid API |
| **EarningsWhispers** | Pre-earnings whisper numbers | None (web scrape) | ★★ Heavily blocked |
| **GuruFocus** | Valuation metrics | None (web scrape, usually blocked) | ★ Paywalled |

## Setup

```bash
# Install dependencies
pip install requests beautifulsoup4 pandas numpy

# Set API keys (use whichever you have)
export FMP_API_KEY="your_key"                              # https://financialmodelingprep.com/
export FRED_API_KEY="your_key"                             # https://fred.stlouisfed.org/docs/api/api_key.html
export QUIVER_API_KEY="your_key"                           # https://www.quiverquant.com/
export SEC_EDGAR_USER_AGENT="YourName your.email@example.com"  # SEC requires identification
```

## Usage

```bash
# Screen specific tickers
python main.py AAPL MSFT GOOGL

# Screen a sector
python main.py --sector Technology

# Export results
python main.py NVDA NVO CAT --export results.json --csv summary.csv

# Macro snapshot only
python main.py --macro

# Check which API keys are configured
python main.py --check-keys
```

## Signal Weights

| Signal | Weight | Rationale |
|---|---|---|
| Forward P/E vs Peers | 25% | Core valuation signal |
| Earnings Revisions | 20% | Earnings momentum is the strongest short-term predictor |
| Insider Activity | 20% | Insiders buying with their own money is high-signal |
| Macro Alignment | 10% | Sector-macro fit matters for cyclicals |
| Congressional Trades | 10% | Informational edge, though debatable |
| Social Sentiment | 5% | Used as contrarian indicator (low weight intentional) |
| Gov Contracts | 5% | Revenue visibility for defense/tech |
| Patent Activity | 5% | Innovation proxy |

## Honest Limitations

1. **Most "undervalued" stocks are cheap for a reason.** Low P/E alone is not a buy signal — it often reflects deteriorating fundamentals (see: NVO).

2. **Scraping is fragile.** OpenInsider, EarningsWhispers, and GuruFocus change layouts or block requests without notice. Budget for maintenance.

3. **Free data has gaps.** FMP free tier gives 250 requests/day. Screening 20 stocks with peer comps burns through ~150 requests. For serious use, pay for a data provider.

4. **No backtesting included.** Without historical validation, you have no idea if this score actually predicts returns. Adding a backtesting module is critical before relying on this for real money.

5. **Survivorship bias.** The peer groups in `config.py` include only current large-caps. Failed companies aren't represented, biasing comps analysis.

6. **Social sentiment is mostly noise.** The 5% weight reflects this. Academic evidence on retail sentiment as a predictor is mixed at best.

7. **Congressional trading data has a reporting lag** (up to 45 days). By the time you see the trade, the market may have already moved.

8. **This doesn't account for:** balance sheet quality, management incentives, competitive moat durability, regulatory risk, or any qualitative factors.

## File Structure

```
stock_screener/
├── main.py          # CLI entry point
├── config.py        # API keys, thresholds, peer groups
├── fetchers.py      # Data source modules (one function per source)
├── screener.py      # Scoring engine (signal normalization + composite)
└── README.md
```

## Extending

- **Add a new data source:** Write a `fetch_*()` function in `fetchers.py`, a `_score_*()` function in `screener.py`, add its weight to `SIGNAL_WEIGHTS`.
- **Adjust scoring:** All signal scoring functions return -1 to +1. Modify thresholds in the `_score_*()` functions.
- **Add backtesting:** Record historical scores and compare to subsequent 3/6/12-month returns. This is the single most valuable improvement you could make.
