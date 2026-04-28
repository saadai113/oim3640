"""
Polymarket Market Tracker
Fetches active markets from the Polymarket Gamma API and displays them cleanly.

Usage:
    python polymarket_tracker.py                  # Top 20 markets by volume
    python polymarket_tracker.py --limit 50       # Top 50
    python polymarket_tracker.py --search "trump"  # Search by keyword
    python polymarket_tracker.py --json            # Raw JSON output
"""

import requests
import json
import argparse
from datetime import datetime


GAMMA_API_URL = "https://gamma-api.polymarket.com"


def fetch_markets(limit=20, active=True, closed=False, order="volume24hr", ascending=False):
    """Fetch markets from the Polymarket Gamma API."""
    params = {
        "limit": limit,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "order": order,
        "ascending": str(ascending).lower(),
    }
    resp = requests.get(f"{GAMMA_API_URL}/markets", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_events(limit=20, active=True, closed=False, order="volume24hr", ascending=False):
    """Fetch events (grouped markets) from the Gamma API."""
    params = {
        "limit": limit,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "order": order,
        "ascending": str(ascending).lower(),
    }
    resp = requests.get(f"{GAMMA_API_URL}/events", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def search_markets(query, limit=20):
    """Search markets by keyword."""
    params = {"limit": limit, "active": "true", "closed": "false"}
    markets = fetch_markets(limit=200)
    query_lower = query.lower()
    return [m for m in markets if query_lower in m.get("question", "").lower()][:limit]


def parse_prices(market):
    """Parse outcome prices from a market dict. Returns (yes_price, no_price) as floats."""
    raw = market.get("outcomePrices", '["0","0"]')
    if isinstance(raw, str):
        prices = json.loads(raw)
    else:
        prices = raw
    yes = float(prices[0]) if len(prices) > 0 else 0.0
    no = float(prices[1]) if len(prices) > 1 else 0.0
    return yes, no


def format_usd(value):
    """Format a number as compact USD."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:.0f}"


def format_pct_change(change):
    """Format a price change as a signed percentage string."""
    if change is None:
        return "  n/a"
    pct = change * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def display_market(market, index=None):
    """Print a single market in a readable format."""
    question = market.get("question", "Unknown")
    yes_price, no_price = parse_prices(market)
    volume_total = market.get("volumeNum", 0)
    volume_24h = market.get("volume24hr", 0)
    liquidity = market.get("liquidityNum", 0)
    last_trade = market.get("lastTradePrice", "?")
    best_bid = market.get("bestBid", "?")
    best_ask = market.get("bestAsk", "?")
    spread = market.get("spread", None)
    day_change = market.get("oneDayPriceChange", None)
    end_date = market.get("endDateIso", "?")
    slug = market.get("slug", "")

    prefix = f"[{index}] " if index is not None else ""
    print(f"{prefix}{question}")
    print(f"    Yes: {yes_price:.1%}  |  No: {no_price:.1%}  |  24h: {format_pct_change(day_change)}")
    print(f"    Bid/Ask: {best_bid}/{best_ask}  |  Spread: {spread}")
    print(f"    Vol 24h: {format_usd(volume_24h)}  |  Total: {format_usd(volume_total)}  |  Liq: {format_usd(liquidity)}")
    print(f"    Ends: {end_date}  |  https://polymarket.com/event/{slug}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Polymarket Market Tracker")
    parser.add_argument("--limit", type=int, default=20, help="Number of markets to fetch (default: 20)")
    parser.add_argument("--search", type=str, default=None, help="Search markets by keyword")
    parser.add_argument("--order", type=str, default="volume24hr",
                        help="Sort field: volume24hr, volumeNum, liquidityNum, startDate, endDate (default: volume24hr)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--events", action="store_true", help="Fetch events instead of individual markets")
    args = parser.parse_args()

    try:
        if args.search:
            print(f"Searching for: '{args.search}'\n")
            markets = search_markets(args.search, limit=args.limit)
        elif args.events:
            markets = fetch_events(limit=args.limit, order=args.order)
        else:
            markets = fetch_markets(limit=args.limit, order=args.order)

        if not markets:
            print("No markets found.")
            return

        if args.json:
            # Dump filtered fields only
            slim = []
            for m in markets:
                yes, no = parse_prices(m)
                slim.append({
                    "question": m.get("question") or m.get("title", "?"),
                    "slug": m.get("slug", ""),
                    "yes_price": yes,
                    "no_price": no,
                    "volume_24h": m.get("volume24hr", 0),
                    "volume_total": m.get("volumeNum", 0),
                    "liquidity": m.get("liquidityNum", 0),
                    "best_bid": m.get("bestBid"),
                    "best_ask": m.get("bestAsk"),
                    "last_trade": m.get("lastTradePrice"),
                    "day_change": m.get("oneDayPriceChange"),
                    "end_date": m.get("endDateIso", ""),
                })
            print(json.dumps(slim, indent=2))
        else:
            header = "Events" if args.events else "Markets"
            print(f"=== Polymarket {header} (sorted by {args.order}, top {len(markets)}) ===")
            print(f"    Fetched at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
            for i, m in enumerate(markets, 1):
                display_market(m, index=i)

    except requests.RequestException as e:
        print(f"API error: {e}")
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Parse error: {e}")


if __name__ == "__main__":
    main()