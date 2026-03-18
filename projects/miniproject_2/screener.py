"""
Screening Engine — Combines all data sources into a composite score.

This is the core logic. It:
1. Fetches data from all available sources
2. Normalizes signals into a common framework
3. Applies weighted scoring
4. Flags potential undervaluation

IMPORTANT CAVEATS:
- This is a screening tool, not an oracle. It surfaces candidates for
  further research. Most "undervalued" stocks are cheap for a reason.
- Quantitative screens systematically miss qualitative factors:
  management quality, competitive dynamics, regulatory risk, etc.
- Backtesting this on historical data would likely show mediocre returns
  after transaction costs, especially for retail investors.
- Survivorship bias in peer groups is real. Adjust accordingly.
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

import pandas as pd

from config import SECTOR_PEERS, THRESHOLDS, REQUEST_DELAY
from fetchers import (
    compute_comps_discount,
    fetch_13f_institutional_holders,
    fetch_congressional_trades,
    fetch_earnings_revisions,
    fetch_fmp_profile,
    fetch_forward_pe,
    fetch_fred_series,
    fetch_gov_contracts,
    fetch_macro_snapshot,
    fetch_openinsider_transactions,
    fetch_patent_data,
    fetch_peer_forward_pe,
    fetch_reddit_sentiment,
    fetch_stocktwits_sentiment,
    scrape_earnings_whispers,
    scrape_gurufocus_summary,
)

log = logging.getLogger(__name__)


@dataclass
class SignalScore:
    """Individual signal with its score and metadata."""

    name: str
    score: float  # -1 (very bearish) to +1 (very bullish)
    weight: float  # importance weight
    available: bool  # whether data was successfully fetched
    detail: str = ""
    raw_data: dict = field(default_factory=dict)


@dataclass
class ScreenResult:
    """Complete screening result for a single ticker."""

    ticker: str
    timestamp: str
    composite_score: float = 0.0
    signals: list = field(default_factory=list)
    macro_context: dict = field(default_factory=dict)
    recommendation: str = ""
    data_coverage: float = 0.0  # % of data sources that returned data

    def to_dict(self):
        d = asdict(self)
        return d


# ── Signal Weights ───────────────────────────────────────────────────────────
# Higher weight = more influence on composite score.
# These are debatable. Adjust based on your investment philosophy.

SIGNAL_WEIGHTS = {
    "forward_pe_vs_peers": 0.25,      # Comparable company valuation
    "earnings_revisions": 0.20,        # Earnings momentum
    "insider_activity": 0.20,          # Skin in the game
    "congressional_trades": 0.10,      # Informational edge (debatable)
    "social_sentiment": 0.05,          # Contrarian signal (low weight intentionally)
    "macro_alignment": 0.10,           # Sector-macro fit
    "gov_contracts": 0.05,             # Revenue visibility
    "patent_activity": 0.05,           # Innovation proxy
}


def _score_forward_pe(fwd_pe_data: Optional[dict], comps: Optional[dict]) -> SignalScore:
    """Score based on forward P/E vs peers."""
    if not fwd_pe_data or not fwd_pe_data.get("forward_pe"):
        return SignalScore(
            name="forward_pe_vs_peers",
            score=0,
            weight=SIGNAL_WEIGHTS["forward_pe_vs_peers"],
            available=False,
            detail="Forward P/E data unavailable",
        )

    fwd_pe = fwd_pe_data["forward_pe"]
    detail_parts = [f"Forward P/E: {fwd_pe}"]

    score = 0.0
    if comps:
        discount = comps["discount_vs_peers_pct"]
        detail_parts.append(
            f"Peer median: {comps['peer_median_forward_pe']}, "
            f"Discount: {discount}%"
        )
        # Scale: -30% discount = +1, +30% premium = -1
        score = max(-1, min(1, -discount / 30))
    else:
        # No peer data — just penalize very high P/E
        if fwd_pe > 30:
            score = -0.5
        elif fwd_pe > 20:
            score = 0.0
        elif fwd_pe > 10:
            score = 0.3
        else:
            score = 0.5  # could be a value trap, don't go full bullish

    return SignalScore(
        name="forward_pe_vs_peers",
        score=round(score, 3),
        weight=SIGNAL_WEIGHTS["forward_pe_vs_peers"],
        available=True,
        detail="; ".join(detail_parts),
        raw_data={"forward_pe": fwd_pe_data, "comps": comps},
    )


def _score_earnings_revisions(revisions: Optional[dict]) -> SignalScore:
    """Score based on earnings estimate revision direction."""
    if not revisions:
        return SignalScore(
            name="earnings_revisions",
            score=0,
            weight=SIGNAL_WEIGHTS["earnings_revisions"],
            available=False,
            detail="Earnings revision data unavailable",
        )

    direction = revisions.get("revision_direction", "flat")
    delta = revisions.get("revision_delta", 0)

    if direction == "up":
        # Scale by magnitude relative to estimate
        prior = revisions.get("prior_fy_eps_estimate", 1)
        if prior and prior > 0:
            pct_change = delta / prior
            score = min(1, pct_change * 10)  # 10% revision = full score
        else:
            score = 0.3
    elif direction == "down":
        score = -0.5
    else:
        score = 0.0

    return SignalScore(
        name="earnings_revisions",
        score=round(score, 3),
        weight=SIGNAL_WEIGHTS["earnings_revisions"],
        available=True,
        detail=f"Direction: {direction}, Delta: {delta}",
        raw_data=revisions,
    )


def _score_insider_activity(insider_data: Optional[dict]) -> SignalScore:
    """Score based on insider buying/selling from OpenInsider."""
    if not insider_data:
        return SignalScore(
            name="insider_activity",
            score=0,
            weight=SIGNAL_WEIGHTS["insider_activity"],
            available=False,
            detail="Insider transaction data unavailable",
        )

    signal = insider_data.get("net_insider_signal", "neutral")
    buy_val = insider_data.get("total_buy_value", 0)
    sell_val = insider_data.get("total_sell_value", 0)
    ratio = insider_data.get("buy_sell_ratio", 1)

    if signal == "bullish":
        # Scale by conviction — larger buys = stronger signal
        if buy_val > 1_000_000:
            score = 0.8
        elif buy_val > 100_000:
            score = 0.5
        else:
            score = 0.3
    elif signal == "bearish":
        # Insider selling is noisier — could be diversification, tax, etc.
        # Weight it less harshly than buying
        if sell_val > 10_000_000:
            score = -0.5
        elif sell_val > 1_000_000:
            score = -0.3
        else:
            score = -0.1
    else:
        score = 0.0

    buys = insider_data.get("buys", 0)
    sells = insider_data.get("sells", 0)

    return SignalScore(
        name="insider_activity",
        score=round(score, 3),
        weight=SIGNAL_WEIGHTS["insider_activity"],
        available=True,
        detail=f"Signal: {signal}, Buys: {buys} (${buy_val:,.0f}), Sells: {sells} (${sell_val:,.0f})",
        raw_data=insider_data,
    )


def _score_congressional_trades(congress_data: Optional[dict]) -> SignalScore:
    """Score based on congressional trading activity."""
    if not congress_data:
        return SignalScore(
            name="congressional_trades",
            score=0,
            weight=SIGNAL_WEIGHTS["congressional_trades"],
            available=False,
            detail="Congressional trade data unavailable (needs QUIVER_API_KEY)",
        )

    signal = congress_data.get("net_signal", "neutral")
    buys = congress_data.get("buys_90d", 0)
    sells = congress_data.get("sells_90d", 0)

    if signal == "bullish":
        score = min(0.5, buys * 0.15)  # Cap at 0.5, each buy adds 0.15
    elif signal == "bearish":
        score = max(-0.5, -sells * 0.15)
    else:
        score = 0.0

    return SignalScore(
        name="congressional_trades",
        score=round(score, 3),
        weight=SIGNAL_WEIGHTS["congressional_trades"],
        available=True,
        detail=f"Signal: {signal}, Buys: {buys}, Sells: {sells} (90d)",
        raw_data=congress_data,
    )


def _score_social_sentiment(
    stocktwits: Optional[dict], reddit: Optional[dict]
) -> SignalScore:
    """
    Score based on social sentiment.
    NOTE: Used as a CONTRARIAN signal at low weight. Extreme bullishness
    on social media is often a sell signal, not a buy signal.
    """
    scores = []
    details = []

    if stocktwits:
        st_score = stocktwits.get("sentiment_score", 0.5)
        # Contrarian: extreme bullishness is bad, moderate is ok
        if st_score > 0.8:
            scores.append(-0.3)  # too crowded
            details.append(f"StockTwits: {st_score:.2f} (crowded bullish)")
        elif st_score < 0.3:
            scores.append(0.2)  # contrarian buy
            details.append(f"StockTwits: {st_score:.2f} (contrarian opportunity)")
        else:
            scores.append(0.0)
            details.append(f"StockTwits: {st_score:.2f} (neutral)")

    if reddit:
        r_sent = reddit.get("avg_sentiment_30d", 0)
        mentions = reddit.get("mentions_30d", 0)
        if mentions > 100 and r_sent > 0.6:
            scores.append(-0.2)  # meme risk
            details.append(f"Reddit: high mentions ({mentions}) + bullish = meme risk")
        elif r_sent < -0.2:
            scores.append(0.1)
            details.append(f"Reddit: negative sentiment = possible contrarian")
        else:
            scores.append(0.0)
            details.append(f"Reddit: mentions={mentions}, sentiment={r_sent:.2f}")

    avg_score = sum(scores) / len(scores) if scores else 0

    return SignalScore(
        name="social_sentiment",
        score=round(avg_score, 3),
        weight=SIGNAL_WEIGHTS["social_sentiment"],
        available=bool(scores),
        detail="; ".join(details) if details else "No social data available",
        raw_data={"stocktwits": stocktwits, "reddit": reddit},
    )


def _score_gov_contracts(contracts: Optional[dict]) -> SignalScore:
    """Score based on government contract activity."""
    if not contracts:
        return SignalScore(
            name="gov_contracts",
            score=0,
            weight=SIGNAL_WEIGHTS["gov_contracts"],
            available=False,
            detail="Gov contract data unavailable (needs QUIVER_API_KEY)",
        )

    count = contracts.get("contracts_180d", 0)
    value = contracts.get("total_value_180d", 0)

    if count > 5 and value > 100_000_000:
        score = 0.5
    elif count > 0:
        score = 0.2
    else:
        score = 0.0

    return SignalScore(
        name="gov_contracts",
        score=round(score, 3),
        weight=SIGNAL_WEIGHTS["gov_contracts"],
        available=True,
        detail=f"Contracts (180d): {count}, Value: ${value:,.0f}",
        raw_data=contracts,
    )


def _score_patents(patents: Optional[dict]) -> SignalScore:
    """Score based on patent filing activity."""
    if not patents:
        return SignalScore(
            name="patent_activity",
            score=0,
            weight=SIGNAL_WEIGHTS["patent_activity"],
            available=False,
            detail="Patent data unavailable (needs QUIVER_API_KEY)",
        )

    count = patents.get("patents_1yr", 0)
    if count > 50:
        score = 0.4
    elif count > 10:
        score = 0.2
    else:
        score = 0.0

    return SignalScore(
        name="patent_activity",
        score=round(score, 3),
        weight=SIGNAL_WEIGHTS["patent_activity"],
        available=True,
        detail=f"Patents filed (1yr): {count}",
        raw_data=patents,
    )


def _assess_macro_alignment(macro: dict, sector: str) -> SignalScore:
    """
    Basic macro-sector alignment check.
    E.g., rising rates hurt growth/tech, help financials.
    """
    if not macro:
        return SignalScore(
            name="macro_alignment",
            score=0,
            weight=SIGNAL_WEIGHTS["macro_alignment"],
            available=False,
            detail="Macro data unavailable (needs FRED_API_KEY)",
        )

    score = 0.0
    details = []

    fed_rate = macro.get("fed_funds_rate", {}).get("value")
    yield_curve = macro.get("yield_curve_10y2y", {}).get("value")
    consumer = macro.get("consumer_sentiment", {}).get("value")

    if yield_curve is not None:
        if yield_curve < 0:
            # Inverted yield curve — recession signal
            score -= 0.3
            details.append(f"Yield curve inverted ({yield_curve}bp) — recession risk")
            if sector in ("Consumer Discretionary", "Financials"):
                score -= 0.2
                details.append(f"  → extra negative for {sector}")
        else:
            score += 0.1
            details.append(f"Yield curve normal ({yield_curve}bp)")

    if consumer is not None:
        if consumer < 65:
            score -= 0.2
            details.append(f"Consumer sentiment weak ({consumer})")
        elif consumer > 80:
            score += 0.1
            details.append(f"Consumer sentiment solid ({consumer})")

    if fed_rate is not None:
        if fed_rate > 5.0 and sector in ("Technology", "Real Estate"):
            score -= 0.2
            details.append(f"High rates ({fed_rate}%) headwind for {sector}")
        elif fed_rate < 3.0 and sector in ("Technology", "Real Estate"):
            score += 0.2
            details.append(f"Low rates ({fed_rate}%) tailwind for {sector}")

    return SignalScore(
        name="macro_alignment",
        score=round(max(-1, min(1, score)), 3),
        weight=SIGNAL_WEIGHTS["macro_alignment"],
        available=True,
        detail="; ".join(details) if details else "Macro neutral",
        raw_data=macro,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN SCREENING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════


def screen_stock(ticker: str, macro_cache: Optional[dict] = None) -> ScreenResult:
    """
    Run the full screening pipeline on a single ticker.

    Args:
        ticker: Stock ticker symbol
        macro_cache: Pre-fetched macro data (to avoid redundant FRED calls)

    Returns:
        ScreenResult with composite score and all signal details
    """
    ticker = ticker.upper()
    log.info(f"\n{'='*60}")
    log.info(f"  SCREENING: {ticker}")
    log.info(f"{'='*60}")

    result = ScreenResult(
        ticker=ticker, timestamp=datetime.now().isoformat()
    )

    # ── 1. Company Profile & Sector ─────────────────────────────────────────
    log.info(f"[1/8] Fetching company profile...")
    profile = fetch_fmp_profile(ticker)
    sector = profile.get("sector", "Unknown") if profile else "Unknown"
    peers = SECTOR_PEERS.get(sector, [])
    peers = [p for p in peers if p.upper() != ticker.upper()][:6]  # max 6 peers
    log.info(f"  Sector: {sector}, Peers: {peers}")

    # ── 2. Forward P/E & Comps ──────────────────────────────────────────────
    log.info(f"[2/8] Fetching forward P/E and peer comps...")
    fwd_pe_data = fetch_forward_pe(ticker)
    peer_pes = fetch_peer_forward_pe(peers) if peers else {}
    comps = None
    if fwd_pe_data and fwd_pe_data.get("forward_pe") and peer_pes:
        comps = compute_comps_discount(fwd_pe_data["forward_pe"], peer_pes)

    pe_signal = _score_forward_pe(fwd_pe_data, comps)
    result.signals.append(pe_signal)

    # ── 3. Earnings Revisions ───────────────────────────────────────────────
    log.info(f"[3/8] Fetching earnings revisions...")
    revisions = fetch_earnings_revisions(ticker)
    rev_signal = _score_earnings_revisions(revisions)
    result.signals.append(rev_signal)

    # ── 4. Insider Activity (OpenInsider) ───────────────────────────────────
    log.info(f"[4/8] Fetching insider transactions...")
    insider_data = fetch_openinsider_transactions(ticker)
    insider_signal = _score_insider_activity(insider_data)
    result.signals.append(insider_signal)

    # ── 5. Congressional Trading (QuiverQuant) ──────────────────────────────
    log.info(f"[5/8] Fetching congressional trades...")
    congress_data = fetch_congressional_trades(ticker)
    congress_signal = _score_congressional_trades(congress_data)
    result.signals.append(congress_signal)

    # ── 6. Social Sentiment ─────────────────────────────────────────────────
    log.info(f"[6/8] Fetching social sentiment...")
    stocktwits = fetch_stocktwits_sentiment(ticker)
    reddit = fetch_reddit_sentiment(ticker)
    social_signal = _score_social_sentiment(stocktwits, reddit)
    result.signals.append(social_signal)

    # ── 7. QuiverQuant (Gov Contracts + Patents) ────────────────────────────
    log.info(f"[7/8] Fetching gov contracts & patents...")
    contracts = fetch_gov_contracts(ticker)
    patents = fetch_patent_data(ticker)
    result.signals.append(_score_gov_contracts(contracts))
    result.signals.append(_score_patents(patents))

    # ── 8. Macro Context (FRED) ─────────────────────────────────────────────
    log.info(f"[8/8] Assessing macro alignment...")
    macro = macro_cache if macro_cache else fetch_macro_snapshot()
    result.macro_context = macro
    macro_signal = _assess_macro_alignment(macro, sector)
    result.signals.append(macro_signal)

    # ── Compute Composite Score ─────────────────────────────────────────────
    available_signals = [s for s in result.signals if s.available]
    result.data_coverage = (
        len(available_signals) / len(result.signals) if result.signals else 0
    )

    if available_signals:
        total_weight = sum(s.weight for s in available_signals)
        if total_weight > 0:
            weighted_sum = sum(s.score * s.weight for s in available_signals)
            result.composite_score = round(weighted_sum / total_weight, 4)

    # ── Generate Recommendation ─────────────────────────────────────────────
    cs = result.composite_score
    coverage = result.data_coverage

    if coverage < 0.3:
        result.recommendation = (
            "INSUFFICIENT DATA — Too few signals available for meaningful analysis. "
            f"Only {coverage:.0%} of data sources returned results."
        )
    elif cs > 0.4:
        result.recommendation = (
            f"POTENTIALLY UNDERVALUED (score: {cs:+.3f}) — "
            "Multiple signals align positively. Warrants deeper fundamental analysis. "
            "Check: balance sheet quality, management track record, competitive moat."
        )
    elif cs > 0.15:
        result.recommendation = (
            f"MILDLY POSITIVE (score: {cs:+.3f}) — "
            "Some favorable signals but not strongly compelling. "
            "Could be a watch-list candidate."
        )
    elif cs > -0.15:
        result.recommendation = (
            f"NEUTRAL (score: {cs:+.3f}) — "
            "Mixed or insufficient signals. No clear edge."
        )
    elif cs > -0.4:
        result.recommendation = (
            f"CAUTION (score: {cs:+.3f}) — "
            "More negative signals than positive. "
            "May be cheap for a reason (value trap risk)."
        )
    else:
        result.recommendation = (
            f"AVOID (score: {cs:+.3f}) — "
            "Strong negative signals across multiple dimensions."
        )

    return result


def screen_multiple(tickers: list[str]) -> list[ScreenResult]:
    """
    Screen a list of tickers. Fetches macro data once and reuses.
    Returns results sorted by composite score (highest first).
    """
    log.info(f"Fetching macro snapshot (shared across all tickers)...")
    macro = fetch_macro_snapshot()

    results = []
    for ticker in tickers:
        try:
            r = screen_stock(ticker, macro_cache=macro)
            results.append(r)
        except Exception as e:
            log.error(f"Failed to screen {ticker}: {e}")
        time.sleep(REQUEST_DELAY * 2)

    results.sort(key=lambda x: x.composite_score, reverse=True)
    return results


def print_result(result: ScreenResult):
    """Pretty-print a screening result."""
    print(f"\n{'━'*70}")
    print(f"  {result.ticker}  |  Score: {result.composite_score:+.4f}  |  Data Coverage: {result.data_coverage:.0%}")
    print(f"{'━'*70}")
    print(f"  {result.recommendation}")
    print(f"\n  Signal Breakdown:")
    print(f"  {'Signal':<25} {'Score':>8} {'Weight':>8} {'Available':>10}")
    print(f"  {'─'*55}")
    for s in result.signals:
        avail = "✓" if s.available else "✗"
        print(f"  {s.name:<25} {s.score:>+8.3f} {s.weight:>8.2f} {avail:>10}")
        if s.detail:
            print(f"    └─ {s.detail}")
    print(f"{'━'*70}")


def export_results(results: list[ScreenResult], filepath: str = "screen_results.json"):
    """Export results to JSON."""
    data = [r.to_dict() for r in results]
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    log.info(f"Results exported to {filepath}")


def results_to_dataframe(results: list[ScreenResult]) -> pd.DataFrame:
    """Convert results to a summary DataFrame."""
    rows = []
    for r in results:
        row = {
            "ticker": r.ticker,
            "composite_score": r.composite_score,
            "data_coverage": r.data_coverage,
            "recommendation": r.recommendation.split("—")[0].strip(),
        }
        for s in r.signals:
            row[f"signal_{s.name}"] = s.score if s.available else None
        rows.append(row)
    return pd.DataFrame(rows)
