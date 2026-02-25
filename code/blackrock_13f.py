"""
BlackRock 13F New Position Finder
----------------------------------
Compares two quarters of BlackRock's 13F filings to find:
- New positions (bought this quarter, not in prior quarter)
- Increased positions (significant share count increases)
- Exited positions (sold completely)

HOW TO USE:
1. Find the XML URLs for the current and prior quarter on SEC EDGAR
2. Replace the URLs below with the correct ones
3. Run: python blackrock_13f_compare.py

To find prior quarter XML:
Go to: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0002012383&type=13F-HR
Click the filing before the most recent one, then find form13fInfoTable.xml
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO

# ── CONFIGURE THESE ──────────────────────────────────────────────────────────
CURRENT_Q_URL = "https://www.sec.gov/Archives/edgar/data/2012383/000201238326000920/form13fInfoTable.xml"
PRIOR_Q_URL   = ""  # <-- Paste prior quarter XML URL here

# Threshold: only flag increases above this percentage
INCREASE_THRESHOLD_PCT = 20
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {"User-Agent": "research-script saad@example.com"}  # SEC requires a User-Agent

NS = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"


def fetch_and_parse(url: str) -> pd.DataFrame:
    print(f"Fetching: {url}")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    
    # Debug: check what we're actually getting
    content = r.text
    print(r.text[2000:3000])  # <-- add this line
    print(f"First 500 chars: {content[:500]}")
    
    # Try parsing as XML
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        # If it's HTML/XSL output, try with lxml
        try:
            from lxml import etree
            root = etree.fromstring(r.content)
        except Exception as e:
            print(f"Parse failed: {e}")
            print("Try using the raw XML URL without xslForm13F_X02 in the path")
            raise

    records = []
    # Try both with and without namespace
    for ns in [NS, ""]:
        items = root.findall(f".//{ns}infoTable")
        if items:
            break
    
    for info in items:
        def get(tag):
            for ns in [NS, ""]:
                el = info.find(f"{ns}{tag}")
                if el is not None and el.text:
                    return el.text.strip()
            return None

        records.append({
        "name":       get("nameOfIssuer"),
        "cusip":      get("cusip"),
        "value_usd":  int(get("value") or 0),  # rename, no *1000
        "shares":     int(info.findtext(f".//{NS}sshPrnamt") or 
                      info.findtext(".//sshPrnamt") or 0),
        "put_call":   get("putCall"),
        "discretion": get("investmentDiscretion"),
})

    df = pd.DataFrame(records)
    return df

def compare(current: pd.DataFrame, prior: pd.DataFrame):
    """Compare two quarters and print findings."""

    # Merge on CUSIP (unique per security)
    merged = current.merge(
        prior[["cusip", "shares", "value_000"]],
        on="cusip",
        how="outer",
        suffixes=("_cur", "_prior"),
        indicator=True
    )

    # 1. New positions — in current but not prior
    new_positions = merged[merged["_merge"] == "left_only"].copy()
    new_positions = new_positions.sort_values("value_usd", ascending=False)

    # 2. Exited positions — in prior but not current
    exited = merged[merged["_merge"] == "right_only"].copy()

    # 3. Increased positions
    both = merged[merged["_merge"] == "both"].copy()
    both["shares_prior"] = both["shares_prior"].fillna(0)
    both["shares_cur"]   = both["shares_cur"].fillna(0)
    both["pct_change"]   = ((both["shares_cur"] - both["shares_prior"]) / both["shares_prior"].replace(0, 1)) * 100
    increased = both[both["pct_change"] >= INCREASE_THRESHOLD_PCT].sort_values("pct_change", ascending=False)

    # ── PRINT RESULTS ────────────────────────────────────────────────────────

    print("\n" + "="*70)
    print(f"NEW POSITIONS ({len(new_positions)} stocks)")
    print("="*70)
    print(new_positions[["name", "cusip", "shares_cur", "value_usd", "discretion"]].to_string(index=False))

    print("\n" + "="*70)
    print(f"SIGNIFICANTLY INCREASED (>{INCREASE_THRESHOLD_PCT}%) — {len(increased)} stocks")
    print("="*70)
    print(increased[["name", "cusip", "shares_prior", "shares_cur", "pct_change", "value_usd"]].to_string(index=False))

    print("\n" + "="*70)
    print(f"EXITED POSITIONS ({len(exited)} stocks)")
    print("="*70)
    print(exited[["name", "cusip"]].to_string(index=False))

    # Save to CSV
    new_positions.to_csv("new_positions.csv", index=False)
    increased.to_csv("increased_positions.csv", index=False)
    exited.to_csv("exited_positions.csv", index=False)
    print("\nSaved: new_positions.csv, increased_positions.csv, exited_positions.csv")


def main():
    current = fetch_and_parse(CURRENT_Q_URL)
    print(f"Current quarter: {len(current)} holdings, total value ${current['value_usd'].sum():,.0f}")

    if not PRIOR_Q_URL:
        # No prior quarter — just show current holdings sorted by value
        print("\nNo prior quarter URL set. Showing top 50 current holdings:\n")
        top = current.sort_values("value_usd", ascending=False).head(50)
        print(top[["name", "cusip", "shares", "value_usd", "discretion"]].to_string(index=False))
        current.to_csv("blackrock_current_holdings.csv", index=False)
        print("\nFull holdings saved to: blackrock_current_holdings.csv")
        return

    prior = fetch_and_parse(PRIOR_Q_URL)
    print(f"Prior quarter: {len(prior)} holdings")
    compare(current, prior)


if __name__ == "__main__":
    main()