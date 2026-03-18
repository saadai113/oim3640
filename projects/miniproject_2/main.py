#!/usr/bin/env python3
"""
Undervalued Stock Screener — CLI Entry Point

Usage:
    python main.py AAPL MSFT GOOGL          # Screen specific tickers
    python main.py --sector Technology       # Screen a sector peer group
    python main.py --macro                   # Just show macro snapshot
    python main.py AAPL --export results.json

Required environment variables (set whichever you have):
    export FMP_API_KEY="your_key"            # financialmodelingprep.com (free tier)
    export FRED_API_KEY="your_key"           # fred.stlouisfed.org (free)
    export QUIVER_API_KEY="your_key"         # quiverquant.com (paid)
    export SEC_EDGAR_USER_AGENT="Name email@example.com"

The screener degrades gracefully — it works with whatever API keys you have,
scoring only the signals that successfully return data.
"""

import argparse
import json
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SECTOR_PEERS
from screener import (
    export_results,
    print_result,
    results_to_dataframe,
    screen_multiple,
    screen_stock,
)
from fetchers import fetch_macro_snapshot


def show_macro():
    """Display current macro snapshot."""
    print("\n📊 Macro Economic Snapshot (FRED)")
    print("─" * 50)
    macro = fetch_macro_snapshot()
    if not macro:
        print("  No data — set FRED_API_KEY environment variable")
        return
    for name, data in macro.items():
        print(f"  {name:<30} {data['value']:>10.2f}  ({data['date']})")
    print()


def check_api_keys():
    """Report which API keys are configured."""
    keys = {
        "FMP_API_KEY": "Financial Modeling Prep (forward P/E, comps, estimates)",
        "FRED_API_KEY": "FRED (macro data)",
        "QUIVER_API_KEY": "QuiverQuant (congress trades, contracts, patents, Reddit)",
        "SEC_EDGAR_USER_AGENT": "SEC EDGAR (13F filings)",
    }
    print("\n🔑 API Key Status:")
    print("─" * 60)
    configured = 0
    for key, desc in keys.items():
        val = os.environ.get(key, "")
        status = "✓ SET" if val else "✗ NOT SET"
        print(f"  {status:<12} {key:<25} {desc}")
        if val:
            configured += 1
    print(f"\n  {configured}/{len(keys)} configured. The screener works with partial")
    print("  coverage but accuracy improves with more data sources.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Screen stocks for undervaluation using multi-source analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py AAPL MSFT               Screen specific tickers
  python main.py --sector Technology      Screen tech sector peers
  python main.py NVDA --export out.json   Screen and export to JSON
  python main.py --macro                  Show macro snapshot only
  python main.py --check-keys             Check API key configuration
        """,
    )
    parser.add_argument("tickers", nargs="*", help="Stock ticker(s) to screen")
    parser.add_argument(
        "--sector",
        type=str,
        choices=list(SECTOR_PEERS.keys()),
        help="Screen all stocks in a sector peer group",
    )
    parser.add_argument(
        "--export", type=str, help="Export results to JSON file"
    )
    parser.add_argument(
        "--macro", action="store_true", help="Show macro economic snapshot"
    )
    parser.add_argument(
        "--check-keys", action="store_true", help="Check API key configuration"
    )
    parser.add_argument(
        "--csv", type=str, help="Export summary to CSV file"
    )

    args = parser.parse_args()

    if args.check_keys:
        check_api_keys()
        return

    if args.macro:
        show_macro()
        return

    # Determine tickers to screen
    tickers = []
    if args.sector:
        tickers = SECTOR_PEERS[args.sector]
        print(f"\n📋 Screening {args.sector} sector: {', '.join(tickers)}")
    elif args.tickers:
        tickers = [t.upper() for t in args.tickers]
    else:
        parser.print_help()
        print("\n⚠️  Provide ticker(s) or --sector to begin screening.")
        return

    # Check keys before running
    check_api_keys()

    # Run screening
    print(f"\n🔍 Screening {len(tickers)} ticker(s)...\n")
    results = screen_multiple(tickers)

    # Print results
    for r in results:
        print_result(r)

    # Summary table
    if len(results) > 1:
        print(f"\n\n{'='*70}")
        print("  RANKING SUMMARY (sorted by composite score)")
        print(f"{'='*70}")
        df = results_to_dataframe(results)
        print(df[["ticker", "composite_score", "data_coverage", "recommendation"]].to_string(index=False))

    # Export
    if args.export:
        export_results(results, args.export)
        print(f"\n💾 Results exported to {args.export}")

    if args.csv:
        df = results_to_dataframe(results)
        df.to_csv(args.csv, index=False)
        print(f"\n💾 Summary CSV exported to {args.csv}")


if __name__ == "__main__":
    main()
