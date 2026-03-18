"""
Data fetchers for each source.

Each fetcher returns a dict or DataFrame. If a source is unavailable
(missing API key, site down, scraping blocked), it returns None and
logs a warning — the screener continues with partial data.
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import (
    FMP_API_KEY,
    FRED_API_KEY,
    QUIVER_API_KEY,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    SEC_EDGAR_USER_AGENT,
    SEC_RATE_LIMIT,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SEC_HEADERS = {"User-Agent": SEC_EDGAR_USER_AGENT, "Accept-Encoding": "gzip, deflate"}


# ═══════════════════════════════════════════════════════════════════════════════
#  1. FORWARD P/E & COMPARABLE COMPANY ANALYSIS
#     Primary: Financial Modeling Prep (free tier)
#     Fallback: SEC EDGAR for raw financials
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_fmp_profile(ticker: str) -> Optional[dict]:
    """Company profile from Financial Modeling Prep (sector, market cap, etc.)."""
    if not FMP_API_KEY:
        log.warning("FMP_API_KEY not set — skipping company profile")
        return None
    try:
        url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}"
        r = requests.get(url, params={"apikey": FMP_API_KEY}, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data and len(data) > 0:
            return data[0]
    except Exception as e:
        log.warning(f"FMP profile failed for {ticker}: {e}")
    return None


def fetch_forward_pe(ticker: str) -> Optional[dict]:
    """
    Forward P/E and earnings estimates from Financial Modeling Prep.
    Returns: {forward_pe, forward_eps, current_price, pe_ttm, sector}
    """
    if not FMP_API_KEY:
        log.warning("FMP_API_KEY not set — cannot fetch forward P/E")
        return None
    try:
        # Key metrics endpoint includes forward P/E
        url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}"
        r = requests.get(url, params={"apikey": FMP_API_KEY}, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        metrics = r.json()

        # Also get the quote for current price
        quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}"
        r2 = requests.get(
            quote_url, params={"apikey": FMP_API_KEY}, timeout=REQUEST_TIMEOUT
        )
        r2.raise_for_status()
        quote = r2.json()

        # Analyst estimates for forward EPS
        est_url = (
            f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}"
        )
        r3 = requests.get(
            est_url,
            params={"apikey": FMP_API_KEY, "limit": 2},
            timeout=REQUEST_TIMEOUT,
        )
        r3.raise_for_status()
        estimates = r3.json()

        result = {}
        if quote and len(quote) > 0:
            result["current_price"] = quote[0].get("price")
            result["pe_ttm"] = quote[0].get("pe")
            result["market_cap"] = quote[0].get("marketCap")

        if metrics and len(metrics) > 0:
            result["pe_ttm_metrics"] = metrics[0].get("peRatioTTM")

        if estimates and len(estimates) > 0:
            # First entry is next fiscal year estimate
            fwd = estimates[0]
            result["forward_eps"] = fwd.get("estimatedEpsAvg")
            result["forward_eps_high"] = fwd.get("estimatedEpsHigh")
            result["forward_eps_low"] = fwd.get("estimatedEpsLow")
            result["forward_revenue"] = fwd.get("estimatedRevenueAvg")
            if result.get("current_price") and result.get("forward_eps"):
                if result["forward_eps"] > 0:
                    result["forward_pe"] = round(
                        result["current_price"] / result["forward_eps"], 2
                    )

        time.sleep(REQUEST_DELAY)
        return result if result else None

    except Exception as e:
        log.warning(f"Forward P/E fetch failed for {ticker}: {e}")
        return None


def fetch_peer_forward_pe(peers: list[str]) -> dict:
    """Fetch forward P/E for a list of peer tickers. Returns {ticker: forward_pe}."""
    results = {}
    for peer in peers:
        data = fetch_forward_pe(peer)
        if data and data.get("forward_pe"):
            results[peer] = data["forward_pe"]
        time.sleep(REQUEST_DELAY)
    return results


def compute_comps_discount(
    target_fwd_pe: float, peer_forward_pes: dict
) -> Optional[dict]:
    """
    Compare target forward P/E against peer median.
    Returns: {peer_median_pe, discount_pct, is_undervalued}
    """
    if not peer_forward_pes:
        return None
    values = [v for v in peer_forward_pes.values() if v and v > 0]
    if not values:
        return None
    median_pe = float(np.median(values))
    discount = (target_fwd_pe - median_pe) / median_pe
    return {
        "peer_median_forward_pe": round(median_pe, 2),
        "peer_forward_pes": peer_forward_pes,
        "target_forward_pe": target_fwd_pe,
        "discount_vs_peers_pct": round(discount * 100, 2),
        "is_undervalued_vs_peers": discount < -0.15,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  2. EARNINGS ESTIMATES & REVISIONS
#     Primary: FMP analyst estimates (free tier)
#     Note: Koyfin, SeekingAlpha, EarningsWhispers all require paid access
#           or have aggressive anti-scraping. FMP is the realistic free option.
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_earnings_revisions(ticker: str) -> Optional[dict]:
    """
    Earnings estimate revisions from FMP.
    Compares current vs prior quarter consensus to detect revision direction.
    """
    if not FMP_API_KEY:
        log.warning("FMP_API_KEY not set — skipping earnings revisions")
        return None
    try:
        url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}"
        r = requests.get(
            url, params={"apikey": FMP_API_KEY, "limit": 4}, timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()
        if not data or len(data) < 2:
            return None

        current = data[0]
        prior = data[1]

        current_eps = current.get("estimatedEpsAvg", 0)
        prior_eps = prior.get("estimatedEpsAvg", 0)
        revision_delta = current_eps - prior_eps if current_eps and prior_eps else 0

        return {
            "next_fy_eps_estimate": current_eps,
            "prior_fy_eps_estimate": prior_eps,
            "revision_delta": round(revision_delta, 4),
            "revision_direction": (
                "up" if revision_delta > 0 else "down" if revision_delta < 0 else "flat"
            ),
            "next_fy_revenue_estimate": current.get("estimatedRevenueAvg"),
            "number_of_analysts": current.get("numberAnalystEstimatedEps"),
        }
    except Exception as e:
        log.warning(f"Earnings revisions failed for {ticker}: {e}")
        return None


def scrape_earnings_whispers(ticker: str) -> Optional[dict]:
    """
    Scrape pre-earnings consensus from EarningsWhispers.
    WARNING: This breaks frequently. EW has anti-bot measures.
    """
    try:
        url = f"https://www.earningswhispers.com/stocks/{ticker}"
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            log.warning(f"EarningsWhispers returned {r.status_code} for {ticker}")
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Try to extract the whisper number and consensus
        result = {"source": "earningswhispers", "ticker": ticker}

        # Look for earnings date
        date_el = soup.find("div", class_="countdown")
        if date_el:
            result["next_earnings_text"] = date_el.get_text(strip=True)

        # Look for whisper EPS
        whisper_el = soup.find("div", class_="whisper")
        if whisper_el:
            text = whisper_el.get_text(strip=True)
            nums = re.findall(r"[-+]?\d*\.?\d+", text)
            if nums:
                result["whisper_eps"] = float(nums[0])

        # Look for consensus EPS
        consensus_el = soup.find("div", class_="consensus")
        if consensus_el:
            text = consensus_el.get_text(strip=True)
            nums = re.findall(r"[-+]?\d*\.?\d+", text)
            if nums:
                result["consensus_eps"] = float(nums[0])

        return result if len(result) > 2 else None

    except Exception as e:
        log.warning(f"EarningsWhispers scrape failed for {ticker}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  3. SEC EDGAR — 13F FILINGS (Institutional Holdings)
#     This is free and reliable. SEC rate limit: 10 req/sec.
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_13f_institutional_holders(ticker: str) -> Optional[dict]:
    """
    Search SEC EDGAR for recent 13F filings mentioning a ticker.
    Returns top institutional holders and recent changes.
    """
    try:
        # Step 1: Get the CIK for the ticker via EDGAR company search
        search_url = "https://efts.sec.gov/LATEST/search-index"
        ticker_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK={ticker}&type=13F&dateb=&owner=include&count=10&search_text=&action=getcompany"

        # Better approach: use the EDGAR full-text search API
        ftse_url = "https://efts.sec.gov/LATEST/search-index"

        # Most reliable: use the company tickers JSON
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        r = requests.get(tickers_url, headers=SEC_HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        all_tickers = r.json()
        time.sleep(SEC_RATE_LIMIT)

        # Find CIK for our ticker
        cik = None
        for entry in all_tickers.values():
            if entry.get("ticker", "").upper() == ticker.upper():
                cik = str(entry["cik_str"]).zfill(10)
                break

        if not cik:
            log.warning(f"Could not find CIK for {ticker} in EDGAR")
            return None

        # Step 2: Get recent filings for this company
        filings_url = (
            f"https://data.sec.gov/submissions/CIK{cik}.json"
        )
        r2 = requests.get(filings_url, headers=SEC_HEADERS, timeout=REQUEST_TIMEOUT)
        r2.raise_for_status()
        filings_data = r2.json()
        time.sleep(SEC_RATE_LIMIT)

        company_name = filings_data.get("name", ticker)
        recent = filings_data.get("filings", {}).get("recent", {})

        # Filter for 13F filings (these are filed BY institutional managers)
        # For a stock, we want to know WHO holds it — that requires searching
        # 13F filings from major holders. This is computationally expensive.
        # Instead, return the company's own filing history as a proxy.

        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])

        filing_summary = []
        for form, date, acc in zip(forms[:20], dates[:20], accessions[:20]):
            filing_summary.append({"form": form, "date": date, "accession": acc})

        return {
            "ticker": ticker,
            "cik": cik,
            "company_name": company_name,
            "recent_filings": filing_summary[:10],
            "note": (
                "For full 13F holder analysis, use the EDGAR full-text search "
                "or a service like SEC API (sec-api.io) which indexes 13F holdings."
            ),
        }

    except Exception as e:
        log.warning(f"SEC EDGAR fetch failed for {ticker}: {e}")
        return None


def search_13f_holders_for_stock(ticker: str) -> Optional[dict]:
    """
    Use EDGAR XBRL companyfacts to find institutional holders.
    NOTE: True 13F-based holder lookup requires parsing XML from each
    manager's filing. This is a simplified version using EDGAR search.
    """
    try:
        url = "https://efts.sec.gov/LATEST/search-index"
        params = {
            "q": f'"{ticker}"',
            "dateRange": "custom",
            "startdt": (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d"),
            "enddt": datetime.now().strftime("%Y-%m-%d"),
            "forms": "13F-HR",
        }
        # Use the full-text search endpoint
        search_url = "https://efts.sec.gov/LATEST/search-index"
        r = requests.get(
            "https://efts.sec.gov/LATEST/search-index",
            params=params,
            headers=SEC_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        # Fallback: use the simpler EDGAR search
        simple_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK=&type=13F-HR&dateb=&owner=include&count=10&search_text={ticker}&action=getcompany"

        log.info(
            f"13F holder search for {ticker} — for production use, "
            f"consider sec-api.io or similar indexed service"
        )

        return {
            "ticker": ticker,
            "note": (
                "Full 13F holder analysis requires parsing individual XML filings. "
                "For a production system, use sec-api.io ($) or build an XBRL parser. "
                "The fetch_13f_institutional_holders() function above provides "
                "the company's own filing history from EDGAR."
            ),
        }

    except Exception as e:
        log.warning(f"13F holder search failed for {ticker}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  4. QUIVER QUANT — Congressional Trading, Gov Contracts, Patents
# ═══════════════════════════════════════════════════════════════════════════════


def _quiver_get(endpoint: str, ticker: str) -> Optional[list]:
    """Generic QuiverQuant API caller."""
    if not QUIVER_API_KEY:
        log.warning("QUIVER_API_KEY not set — skipping QuiverQuant data")
        return None
    try:
        url = f"https://api.quiverquant.com/beta/{endpoint}/{ticker}"
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {QUIVER_API_KEY}"},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"QuiverQuant {endpoint} failed for {ticker}: {e}")
        return None


def fetch_congressional_trades(ticker: str) -> Optional[dict]:
    """Congressional stock trades from QuiverQuant."""
    data = _quiver_get("historical/congresstrading", ticker)
    if not data:
        return None

    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    recent = [t for t in data if t.get("Date", "") >= cutoff]

    buys = [t for t in recent if t.get("Transaction", "").lower() in ("purchase", "buy")]
    sells = [
        t for t in recent if t.get("Transaction", "").lower() in ("sale", "sell", "sale (full)", "sale (partial)")
    ]

    return {
        "ticker": ticker,
        "trades_90d": len(recent),
        "buys_90d": len(buys),
        "sells_90d": len(sells),
        "net_signal": "bullish" if len(buys) > len(sells) else "bearish" if len(sells) > len(buys) else "neutral",
        "recent_trades": recent[:10],
    }


def fetch_gov_contracts(ticker: str) -> Optional[dict]:
    """Government contract awards from QuiverQuant."""
    data = _quiver_get("historical/govcontracts", ticker)
    if not data:
        return None

    cutoff = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    recent = [c for c in data if c.get("Date", "") >= cutoff]
    total_value = sum(c.get("Amount", 0) for c in recent)

    return {
        "ticker": ticker,
        "contracts_180d": len(recent),
        "total_value_180d": total_value,
        "recent_contracts": recent[:5],
    }


def fetch_patent_data(ticker: str) -> Optional[dict]:
    """Patent analytics from QuiverQuant."""
    data = _quiver_get("historical/patents", ticker)
    if not data:
        return None

    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    recent = [p for p in data if p.get("Date", "") >= cutoff]

    return {
        "ticker": ticker,
        "patents_1yr": len(recent),
        "recent_patents": recent[:5],
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  5. SOCIAL SENTIMENT — Reddit (r/wallstreetbets) & StockTwits
#     Both are fragile scraping targets. StockTwits API is more stable.
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_stocktwits_sentiment(ticker: str) -> Optional[dict]:
    """
    StockTwits sentiment for a ticker.
    Free API endpoint — no key required but rate-limited.
    """
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            log.warning(f"StockTwits returned {r.status_code} for {ticker}")
            return None

        data = r.json()
        symbol_info = data.get("symbol", {})
        messages = data.get("messages", [])

        # Count sentiment from recent messages
        bullish = sum(
            1
            for m in messages
            if m.get("entities", {}).get("sentiment", {}).get("basic") == "Bullish"
        )
        bearish = sum(
            1
            for m in messages
            if m.get("entities", {}).get("sentiment", {}).get("basic") == "Bearish"
        )
        total_with_sentiment = bullish + bearish

        sentiment_score = (
            bullish / total_with_sentiment if total_with_sentiment > 0 else 0.5
        )

        return {
            "ticker": ticker,
            "source": "stocktwits",
            "message_count": len(messages),
            "bullish_count": bullish,
            "bearish_count": bearish,
            "sentiment_score": round(sentiment_score, 3),  # 0=all bearish, 1=all bullish
            "watchlist_count": symbol_info.get("watchlist_count"),
        }

    except Exception as e:
        log.warning(f"StockTwits fetch failed for {ticker}: {e}")
        return None


def fetch_reddit_sentiment(ticker: str) -> Optional[dict]:
    """
    Reddit sentiment from QuiverQuant (if API key available) or
    a basic scrape of r/wallstreetbets mentions.
    """
    # Try QuiverQuant first (structured data)
    if QUIVER_API_KEY:
        data = _quiver_get("historical/wallstreetbets", ticker)
        if data:
            cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            recent = [d for d in data if d.get("Date", "") >= cutoff]
            total_mentions = sum(d.get("Mentions", 0) for d in recent)
            avg_sentiment = (
                np.mean([d.get("Sentiment", 0) for d in recent if "Sentiment" in d])
                if recent
                else 0
            )
            return {
                "ticker": ticker,
                "source": "reddit_via_quiver",
                "mentions_30d": total_mentions,
                "avg_sentiment_30d": round(float(avg_sentiment), 3),
                "data_points": len(recent),
            }

    # Fallback: basic signal from StockTwits (already fetched above)
    log.info(
        f"Reddit sentiment for {ticker}: requires QUIVER_API_KEY or manual scraping"
    )
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  6. FRED — Macro Economic Data
#     Free with API key. Reliable.
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_fred_series(series_id: str, limit: int = 12) -> Optional[dict]:
    """
    Fetch a FRED economic data series.
    Common series:
        FEDFUNDS    - Federal Funds Rate
        UNRATE      - Unemployment Rate
        CPIAUCSL    - CPI (inflation)
        GDP         - Real GDP
        T10Y2Y      - 10Y-2Y Treasury spread (yield curve)
        VIXCLS      - VIX (volatility index)
        UMCSENT     - U Michigan Consumer Sentiment
        INDPRO      - Industrial Production
        HOUST       - Housing Starts
    """
    if not FRED_API_KEY:
        log.warning("FRED_API_KEY not set — skipping macro data")
        return None
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        }
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()

        observations = data.get("observations", [])
        values = []
        for obs in observations:
            try:
                values.append(
                    {"date": obs["date"], "value": float(obs["value"])}
                )
            except (ValueError, KeyError):
                continue

        if not values:
            return None

        return {
            "series_id": series_id,
            "latest_value": values[0]["value"],
            "latest_date": values[0]["date"],
            "observations": values,
        }

    except Exception as e:
        log.warning(f"FRED fetch failed for {series_id}: {e}")
        return None


def fetch_macro_snapshot() -> dict:
    """Fetch key macro indicators for context."""
    indicators = {
        "fed_funds_rate": "FEDFUNDS",
        "unemployment": "UNRATE",
        "cpi_yoy": "CPIAUCSL",
        "yield_curve_10y2y": "T10Y2Y",
        "consumer_sentiment": "UMCSENT",
        "industrial_production": "INDPRO",
    }
    snapshot = {}
    for name, series_id in indicators.items():
        data = fetch_fred_series(series_id, limit=3)
        if data:
            snapshot[name] = {
                "value": data["latest_value"],
                "date": data["latest_date"],
            }
        time.sleep(REQUEST_DELAY)
    return snapshot


# ═══════════════════════════════════════════════════════════════════════════════
#  7. OPEN INSIDER — Form 4 Insider Transactions
#     Free scraping target but layout changes often.
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_openinsider_transactions(ticker: str) -> Optional[dict]:
    """
    Scrape recent insider transactions from OpenInsider.
    Returns buy/sell counts and notable transactions.
    """
    try:
        url = f"http://openinsider.com/screener?s={ticker}&o=&pl=&ph=&ll=&lh=&fd=90&fdr=&td=0&tdr=&feession=&t=p&tc=0&cik=&q="
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            log.warning(f"OpenInsider returned {r.status_code}")
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="tinytable")
        if not table:
            log.warning(f"OpenInsider: no transaction table found for {ticker}")
            return None

        rows = table.find_all("tr")[1:]  # skip header
        transactions = []
        buys = 0
        sells = 0
        total_buy_value = 0
        total_sell_value = 0

        for row in rows[:20]:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue

            filing_date = cols[1].get_text(strip=True)
            trade_date = cols[2].get_text(strip=True)
            insider_name = cols[4].get_text(strip=True)
            title = cols[5].get_text(strip=True)
            trade_type = cols[6].get_text(strip=True)
            price_text = cols[8].get_text(strip=True).replace("$", "").replace(",", "")
            qty_text = cols[7].get_text(strip=True).replace(",", "").replace("+", "")
            value_text = cols[9].get_text(strip=True).replace("$", "").replace(",", "")

            try:
                price = float(price_text) if price_text else 0
                qty = int(qty_text) if qty_text else 0
                value = float(value_text) if value_text else 0
            except ValueError:
                price, qty, value = 0, 0, 0

            is_buy = "P" in trade_type.upper() or "BUY" in trade_type.upper()
            is_sell = "S" in trade_type.upper() and not is_buy

            if is_buy:
                buys += 1
                total_buy_value += value
            elif is_sell:
                sells += 1
                total_sell_value += value

            transactions.append(
                {
                    "date": trade_date,
                    "insider": insider_name,
                    "title": title,
                    "type": "buy" if is_buy else "sell",
                    "shares": qty,
                    "price": price,
                    "value": value,
                }
            )

        net_signal = (
            "bullish"
            if total_buy_value > total_sell_value
            else "bearish" if total_sell_value > total_buy_value else "neutral"
        )

        return {
            "ticker": ticker,
            "period": "90 days",
            "total_transactions": len(transactions),
            "buys": buys,
            "sells": sells,
            "total_buy_value": total_buy_value,
            "total_sell_value": total_sell_value,
            "net_insider_signal": net_signal,
            "buy_sell_ratio": round(buys / max(sells, 1), 2),
            "transactions": transactions[:10],
        }

    except Exception as e:
        log.warning(f"OpenInsider scrape failed for {ticker}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  8. GURUFOCUS — Valuation Metrics (Scraping)
#     Heavily paywalled. This attempts the free summary page.
# ═══════════════════════════════════════════════════════════════════════════════


def scrape_gurufocus_summary(ticker: str) -> Optional[dict]:
    """
    Attempt to scrape GuruFocus summary metrics.
    WARNING: GuruFocus aggressively blocks scrapers. This will likely fail
    without a paid API subscription ($500+/mo).
    """
    try:
        url = f"https://www.gurufocus.com/term/forwardPE/{ticker}/Forward-PE-Ratio"
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            log.warning(
                f"GuruFocus returned {r.status_code} — likely blocked. "
                f"Use their paid API or FMP as alternative."
            )
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        # Try to find the key metric
        content = soup.find("div", class_="term-content")
        if content:
            text = content.get_text()
            nums = re.findall(r"forward PE ratio is ([\d.]+)", text, re.IGNORECASE)
            if nums:
                return {
                    "ticker": ticker,
                    "source": "gurufocus",
                    "forward_pe": float(nums[0]),
                }

        return None

    except Exception as e:
        log.warning(f"GuruFocus scrape failed for {ticker}: {e}")
        return None
