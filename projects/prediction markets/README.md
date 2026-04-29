# Prediction Markets — ML Edge Detection

A research project combining Polymarket market analysis with a machine learning model that identifies mispriced Premier League outcomes in Bet365 odds.

---

## What This Does

**Track 1 — Polymarket Analysis**
Fetches live prediction market data, classifies markets into Sports / Politics / Crypto, and compares liquidity, spread, volume, and price volatility across categories.

**Track 2 — Football ML Edge Detection**
Trains a Random Forest on two seasons of Premier League data, tests against the 2024–25 season, computes per-match "edge" vs. Bet365 vig-stripped odds, and simulates flat-stake betting ROI.

---

## Project Structure

```
prediction markets/
├── polymarket_tracker_livemoment.py  # Live Polymarket market explorer (CLI)
├── categories.py                     # Fetch + classify 300 top markets by category
├── compare.py                        # Compare market metrics across categories (charts)
├── football.py                       # Premier League RF predictor (core ML class)
├── football_edge.py                  # Edge detection vs Bet365 + ROI simulation
├── refdata.py                        # FBRef advanced passing stats (utility)
└── plots/                            # All generated HTML charts land here
```

---

## Setup

```bash
pip install requests pandas numpy scikit-learn plotly
```

No API keys required — all data sources are public.

---

## How to Run

### Full Football Edge Analysis (main research)

```bash
python football_edge.py
```

Downloads 3 seasons of Premier League data with Bet365 odds, trains the Random Forest on 2022–24, evaluates on 2024–25, and saves 5 charts to `plots/`.

### Train & Predict a Single Match

```bash
python football.py
```

Trains the model and predicts a sample match. Edit the last lines to predict any home vs. away team pair.

### Explore Live Polymarket Markets

```bash
# Top 20 markets by volume
python polymarket_tracker_livemoment.py --limit 20

# Search for football markets
python polymarket_tracker_livemoment.py --search football

# Sort by liquidity, output JSON
python polymarket_tracker_livemoment.py --order liquidityNum --json

# Browse grouped events
python polymarket_tracker_livemoment.py --events
```

### Polymarket Category Comparison

```bash
python compare.py
```

Runs `categories.py` internally, then generates 6 Plotly HTML charts in `plots/`.

---

## Data Flow

```
football-data.co.uk CSVs
        │
        ▼
   football.py          ← PLPredictor class: feature engineering + RF training
        │
        ▼
 football_edge.py       ← loads PLPredictor, adds Bet365 odds, computes edge + ROI
        │
        ▼
    plots/*.html        ← calibration, scatter, edge dist, ROI curves, P&L


Polymarket Gamma API
        │
        ▼
   categories.py        ← fetch + classify 300 markets
        │
        ▼
    compare.py          ← generate spread/liquidity/volume/volatility charts
        │
        ▼
    plots/*.html
```

---

## Output Charts

All charts are interactive Plotly HTML files saved to `plots/`.

| File | What It Shows |
|------|--------------|
| `edge_calibration.html` | ML predicted probability vs. actual win rate per bucket |
| `edge_ml_vs_bookmaker.html` | Scatter of ML home-win prob vs. Bet365, colored by result |
| `edge_distribution.html` | Histogram of edge values split by ML correctness |
| `edge_roi_by_threshold.html` | ROI (%) and bet count across thresholds 0%–25% |
| `edge_cumulative_pnl.html` | Running P&L through the 2024–25 season |
| `spread.html` | Bid-ask spread by Polymarket category |
| `liquidity.html` | Liquidity (log scale) by category |
| `volume.html` | 24h volume by category |
| `volatility.html` | Price volatility by category |
| `certainty.html` | Yes-price distribution by category |
| `dashboard.html` | 2×2 combined Polymarket metrics |

---

## Key Concepts

**Vig stripping** — Bet365 sets odds that sum to >100% probability (the overround). Before comparing ML probabilities to bookmaker odds, the overround is normalized out so both are on the same scale.

**Edge** — `ML_probability − bookmaker_vig_stripped_probability` for the ML model's most confident outcome. Positive edge means the model thinks the outcome is more likely than the bookmaker does.

**Rolling features** — Team statistics (strength, form, goals) are computed from the last 5 matches using only data available before each match, preventing lookahead bias.

---

## Caveats

- All results are backtested on historical data — this is not a live trading system.
- Flat-stake sizing is used; Kelly criterion bet sizing is not implemented.
- The model retrains from scratch each run; there is no mid-season updating.
