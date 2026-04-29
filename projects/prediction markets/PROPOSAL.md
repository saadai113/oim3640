# Project Proposal: Finding Edge in Prediction Markets Using Machine Learning

## Problem Statement

Prediction markets and sports betting odds are set by professional bookmakers who charge a margin (the "vig" or overround). This built-in fee makes beating the market difficult — but not impossible. Bookmakers set lines for hundreds of matches simultaneously, creating opportunities where their implied probabilities diverge from true outcome likelihoods.

This project asks: **can a machine learning model trained on historical Premier League data identify matches where bookmakers have mispriced the outcome, and can systematically betting those discrepancies generate positive returns?**

---

## Research Hypothesis

A Random Forest classifier trained on rolling team performance statistics will assign probabilities that meaningfully differ from Bet365's vig-stripped implied probabilities on a subset of Premier League matches. Betting only on matches where the model's estimated probability exceeds the bookmaker's by a meaningful margin (the "edge") will produce positive ROI over the 2024–25 season.

---

## Scope

The project has two distinct analytical tracks:

### Track 1 — Polymarket Market Analysis
Explore the structure of the Polymarket prediction market ecosystem by:
- Fetching live market data via the Gamma API
- Categorizing markets into Sports, Politics, and Crypto segments
- Comparing market quality metrics (bid-ask spread, liquidity, 24h volume, price volatility) across categories to identify where markets are most and least efficient

### Track 2 — Football ML Edge Detection *(primary research)*
- Train a Random Forest model on two seasons (2022–23, 2023–24) of Premier League match data
- Test on the held-out 2024–25 season against Bet365's published odds
- Compute per-match "edge" (ML probability minus vig-stripped bookmaker probability)
- Simulate flat-stake betting across edge thresholds (2%–25%) and measure ROI

---

## Data Sources

| Source | What It Provides |
|--------|-----------------|
| [football-data.co.uk](https://www.football-data.co.uk) | Premier League results + Bet365 decimal odds (3 seasons, ~380 matches/season) |
| Polymarket Gamma API | Real-time market questions, Yes/No prices, volume, spread, liquidity |
| FBRef | Advanced team passing statistics (assists, xAG, progressive passes) — for future feature expansion |

---

## Methodology

### Feature Engineering
For each match, compute rolling 5-game team statistics available strictly before kick-off:
- **Team strength** — points-per-game scaled to a 10–90 index
- **Recent form** — raw points from last 5 matches
- **Goals for / against** — rolling averages

Rolling statistics are computed on the full three-season dataset before the train/test split, ensuring early 2024–25 matches still have prior-season context without any lookahead into the test period.

### Model
- `RandomForestClassifier(n_estimators=100)` — chosen for robustness to noisy features and interpretable feature importances
- Target variable: match result (Home Win / Draw / Away Win)
- Training set: 2022–23 and 2023–24 seasons
- Test set: 2024–25 season (temporally separated)

### Edge Calculation
For each test match, the bookmaker's decimal odds are converted to implied probabilities and normalized to remove the overround:

```
total_implied = 1/B365H + 1/B365D + 1/B365A
bk_prob_H = (1/B365H) / total_implied
```

Edge for each match = ML probability of most likely outcome − bookmaker's vig-stripped probability for that same outcome.

### ROI Simulation
Flat-stake betting: place €1 on the ML-favored outcome whenever edge exceeds a threshold. Record:
- Profit: `(odds − 1)` on a win, `−1` on a loss
- ROI per bet, total P&L, and bet count at each threshold (0%–25%)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| ML model accuracy | Competitive with Bet365 accuracy on 2024–25 |
| ROI at ≥5% edge threshold | Positive (> 0%) |
| Calibration | ML probability buckets within 5pp of actual win rates |

---

## Visualizations Produced

- **Calibration plot** — model reliability (predicted prob vs. actual win rate)
- **ML vs. Bookmaker scatter** — where the two probability estimates diverge
- **Edge distribution** — histogram split by whether the ML outcome was correct
- **ROI by threshold curve** — tradeoff between bet volume and returns
- **Cumulative P&L** — profit trajectory through the 2024–25 season
- **Polymarket dashboard** — spread, liquidity, volume, volatility by category

---

## Limitations & Caveats

- Backtesting only — results are in-sample to the 2024–25 historical season, not live trading
- Flat-stake sizing ignores Kelly-optimal bet sizing
- Single train/test split; no walk-forward cross-validation
- Advanced stats (xAG, progressive passes) available in `refdata.py` but not yet integrated into the model
- Model retraining is static; no mid-season updating

---

## Tools & Libraries

`Python 3`, `pandas`, `numpy`, `scikit-learn`, `plotly`, `requests`
