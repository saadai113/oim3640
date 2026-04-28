"""
categories.py
Fetches active Polymarket markets and classifies each into Sports, Politics, Crypto, or Other.
Exposes a single load() function that returns a clean DataFrame.
"""

import json
import requests
import pandas as pd

GAMMA_API_URL = "https://gamma-api.polymarket.com"

# Keyword sets checked against tag slugs + lowercased question text
_SPORTS_KW = {
    "sport", "soccer", "football", "nfl", "nba", "mlb", "nhl", "tennis",
    "golf", "cricket", "rugby", "hockey", "mma", "ufc", "boxing", "f1",
    "formula", "premier-league", "champions-league", "serie-a", "bundesliga",
    "la-liga", "ligue-1", "premier", "champions", "euros", "world-cup",
    "wimbledon", "masters", "pga", "ncaa", "march-madness",
}
_CRYPTO_KW = {
    "crypto", "bitcoin", "ethereum", "btc", "eth", "solana", "defi",
    "nft", "token", "blockchain", "binance", "xrp", "dogecoin", "doge",
    "altcoin", "web3", "stablecoin",
}
_POLITICS_KW = {
    "politic", "election", "trump", "biden", "congress", "senate",
    "president", "government", "democrat", "republican", "tariff",
    "federal-reserve", "fed", "vote", "nato", "ukraine", "geopolit",
    "war", "sanction", "legislation", "supreme-court",
}


def _fetch_raw(limit: int) -> list:
    resp = requests.get(
        f"{GAMMA_API_URL}/markets",
        params={
            "limit": limit,
            "active": "true",
            "closed": "false",
            "order": "volume24hr",
            "ascending": "false",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _tag_slugs(market: dict) -> list:
    tags = market.get("tags", [])
    out = []
    for t in tags:
        if isinstance(t, dict):
            out.append(t.get("slug", t.get("label", "")).lower())
        elif isinstance(t, str):
            out.append(t.lower())
    return out


def _classify(market: dict) -> str:
    tags = _tag_slugs(market)
    text = " ".join(tags) + " " + market.get("question", "").lower()
    if any(kw in text for kw in _SPORTS_KW):
        return "Sports"
    if any(kw in text for kw in _CRYPTO_KW):
        return "Crypto"
    if any(kw in text for kw in _POLITICS_KW):
        return "Politics"
    return "Other"


def _parse_yes_price(market: dict) -> float:
    raw = market.get("outcomePrices", '["0","0"]')
    prices = json.loads(raw) if isinstance(raw, str) else raw
    return float(prices[0]) if prices else 0.0


def _safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def load(limit: int = 300) -> pd.DataFrame:
    """Fetch markets from Polymarket and return a categorized DataFrame."""
    markets = _fetch_raw(limit)
    rows = []
    for m in markets:
        bid = _safe_float(m.get("bestBid"))
        ask = _safe_float(m.get("bestAsk"))
        spread = (ask - bid) if (bid is not None and ask is not None) else _safe_float(m.get("spread"))

        rows.append({
            "question":     m.get("question", ""),
            "slug":         m.get("slug", ""),
            "category":     _classify(m),
            "yes_price":    _parse_yes_price(m),
            "spread":       spread,
            "volume_24h":   float(m.get("volume24hr", 0) or 0),
            "volume_total": float(m.get("volumeNum", 0) or 0),
            "liquidity":    float(m.get("liquidityNum", 0) or 0),
            "day_change":   _safe_float(m.get("oneDayPriceChange")),
            "tags":         _tag_slugs(m),
        })

    df = pd.DataFrame(rows)
    print(f"Loaded {len(df)} markets")
    print(df["category"].value_counts().to_string())
    return df


if __name__ == "__main__":
    df = load()
    focused = df[df["category"] != "Other"]
    print("\nSample markets per category:")
    for cat, group in focused.groupby("category"):
        print(f"\n--- {cat} ---")
        print(group["question"].head(3).to_string(index=False))
