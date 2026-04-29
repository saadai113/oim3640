# Learning Log — Prediction Markets Project

---

## Phase 1 — Exploring Polymarket (polymarket_tracker_livemoment.py, categories.py)

### What I Did
Built a CLI tool to pull live market data from the Polymarket Gamma API and a classification pipeline that categorizes 300 top markets into Sports, Politics, and Crypto buckets using keyword matching.

### What I Learned

**APIs don't always return what you expect.** The Gamma API returns markets where `outcomePrices` is sometimes a JSON string inside a JSON field rather than a parsed array. I had to handle `json.loads()` inside the price parser defensively.

**Keyword classification is brittle but fast.** Assigning markets to categories by matching substrings against question text works well for obvious cases ("Will Bitcoin hit $100k?") but fails on ambiguous ones ("Will there be a ceasefire?" — politics or geopolitics?). For a first pass it's sufficient; real classification would need NLP.

**Bid-ask spread as an efficiency proxy.** Markets with tighter spreads have more professional market makers keeping them honest. Sports markets tend to be the most liquid and efficient on Polymarket because of high retail interest.

---

## Phase 2 — Comparing Market Segments (compare.py)

### What I Did
Used Plotly to generate comparative visualizations of spread, liquidity, volume, and price volatility across the three market categories.

### What I Learned

**Log scale is essential for liquidity.** Raw liquidity values span many orders of magnitude — a box plot on a linear scale makes most of the distribution invisible. Log scale is the right default for financial depth data.

**Volatility and uncertainty are different things.** High 24h price movement (volatility) doesn't mean a market is uncertain — it can mean new information just arrived. A market priced at $0.98 might have high volatility if a political event is imminent but low uncertainty about the ultimate outcome.

**Plotly subplots need careful layout tuning.** When combining multiple chart types (bar + box + histogram) in a single `make_subplots()` figure, axis labels and tick formats need to be explicitly assigned per subplot rather than globally, otherwise they bleed into adjacent panels.

---

## Phase 3 — Building the Football Predictor (football.py)

### What I Did
Built the `PLPredictor` class: downloads 3 seasons of Premier League CSV data, computes rolling 5-game team statistics, and trains a Random Forest to predict H/D/A.

### What I Learned

**Rolling statistics need a warm-up period.** A team's "recent form" is meaningless before they've played enough matches. I skip the first 50 matches of the dataset when building training features to ensure every row has a full rolling window — otherwise the model trains on NaN-filled rows.

**Feature engineering matters more than model choice.** The 5 features used (strength, form, goals for, goals against) are simple but domain-relevant. The RF doesn't struggle to learn from them. Swapping to a gradient boosted model would be marginal improvement without better features.

**Draw prediction is the hardest.** Football has three outcomes, and draws are the least predictable — bookmakers price them worst too. The model systematically under-predicts draws, which is a known challenge across all football prediction literature.

**Random Forest gives probability estimates that need calibration checking.** `predict_proba()` outputs raw softmax-like probabilities from vote counts across trees. These are not always well-calibrated, especially on smaller datasets. The calibration plot (Phase 4) confirms this.

---

## Phase 4 — Edge Detection vs. Bet365 (football_edge.py)

### What I Learned

**Vig stripping is non-negotiable for fair comparison.** Bookmakers embed a ~5–8% overround into their odds so that their implied probabilities sum to >100%. If you compare ML probabilities (which sum to 100%) directly against raw implied bookmaker probabilities, you're comparing apples to oranges — you'll always think the bookmaker is systematically underestimating every outcome. Normalizing the overround out is the correct baseline.

**How to normalize out the vig:**
```python
total_implied = (1/B365H) + (1/B365D) + (1/B365A)
bk_prob_H = (1/B365H) / total_implied
```

**Temporal correctness requires care.** Even though I trained on 2022–24, the rolling features for 2024–25 matches must reference 2023–24 late-season results. Computing features on the full dataset first (before splitting on season) ensures this — but it means the feature DataFrame must be assembled on all rows before filtering to the test set.

**High edge ≠ guaranteed profit.** There's a tradeoff between edge threshold and sample size. At a 12% edge threshold, only a handful of matches qualify — too small a sample for meaningful ROI measurement. At 2%, almost every match qualifies and the "edge" includes noise. The ROI-by-threshold chart makes this tradeoff visual.

**Calibration reveals model overconfidence.** The calibration plot showed the model is overconfident at high predicted probabilities — it assigns 80% probability to outcomes that actually happen ~65% of the time. This is a known RF artifact and means ML "edge" at extreme probability values is partially illusory.

**Cumulative P&L shows variance, not just mean.** A positive average ROI can hide a terrible drawdown period early in the season followed by recovery. The cumulative P&L plot across the 2024–25 season makes the betting trajectory visible, which is more honest than a single ROI number.

---

## Technical Skills Developed

| Skill | Where Applied |
|-------|--------------|
| REST API consumption with `requests` | Polymarket Gamma API |
| `pandas` rolling window operations | Football feature engineering |
| `scikit-learn` Random Forest, `predict_proba`, feature importances | football.py, football_edge.py |
| Vig/overround normalization | football_edge.py |
| Plotly `express`, `graph_objects`, `make_subplots` | compare.py, football_edge.py |
| Temporal train/test splitting (no lookahead) | football_edge.py |
| CSV download with `io.StringIO` for in-memory parsing | football.py |

---

## Challenges & How I Resolved Them

**Challenge:** FBRef blocks scraping requests with a 403.
**Resolution:** Added a `User-Agent` header mimicking a browser in `refdata.py`. For production use, a dedicated sports data API would be more reliable.

**Challenge:** Early matches in a season have no rolling history (NaN features).
**Resolution:** Filter training rows to indices where team history is at least 5 games deep. Late matches from the prior season provide context for early 2024–25 matches because features are computed across the full concatenated dataset.

**Challenge:** Plotly HTML charts opened in browser but were blank on first render.
**Resolution:** Some charts used a `log` axis scale with zero values present. Added a small epsilon (`+ 1e-6`) to prevent `log(0)` errors before passing to Plotly.

---

## What I Would Do Differently / Next Steps

1. **Integrate `refdata.py` advanced stats** — xAG, progressive passes, and key passes would add predictive signal beyond simple rolling averages
2. **Walk-forward cross-validation** — instead of a single 80/20 split, retrain the model monthly through the test season to simulate real deployment
3. **Kelly criterion bet sizing** — flat stakes are simple but suboptimal; size bets proportionally to edge and estimated edge reliability
4. **Expand to Polymarket soccer markets** — overlay ML predictions on live Polymarket contracts to compare market consensus with model output in real time
5. **Draw-specific model** — train a separate binary classifier for "draw vs. decisive result" as a first-stage filter before the three-way outcome model
