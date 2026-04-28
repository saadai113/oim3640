"""
football_edge.py
Compares our Random Forest model against Bet365 bookmaker odds for Premier League matches.

Trains on 2022-24 seasons, tests on 2024-25.
Finds where the model and the market disagree ("edge"), and tests whether
betting on those disagreements is profitable via ROI simulation.

Research question: can a simple ML model identify mispriced outcomes
in professional bookmaker markets?

Run:  python football_edge.py
"""

import os
import requests
import numpy as np
import pandas as pd
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from football import PLPredictor

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def _save(fig, name: str):
    path = os.path.join(PLOTS_DIR, name)
    fig.write_html(path)
    print(f"  Saved: plots/{name}")

SEASON_URLS = {
    "2022-23": "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
    "2023-24": "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
    "2024-25": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
}

OUTCOME_LABELS = {"H": "Home Win", "D": "Draw", "A": "Away Win"}


# ── Data loading ───────────────────────────────────────────────────────────────

def load_season_with_odds(url: str, season: str) -> pd.DataFrame:
    """Download a season CSV keeping match results and Bet365 odds."""
    r = requests.get(url, timeout=10)
    df = pd.read_csv(StringIO(r.text))
    df.columns = [c.lstrip("﻿") for c in df.columns]  # strip BOM

    needed = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "B365H", "B365D", "B365A"]
    df = df[[c for c in needed if c in df.columns]].dropna()
    df["season"] = season
    df = df.rename(columns={
        "HomeTeam": "home_team", "AwayTeam": "away_team",
        "FTHG": "home_goals",   "FTAG": "away_goals",
        "FTR": "result",
    })
    df["home_goals"] = df["home_goals"].astype(int)
    df["away_goals"] = df["away_goals"].astype(int)

    # Convert decimal odds → normalized implied probabilities (strips bookmaker vig)
    for col, src in [("H", "B365H"), ("D", "B365D"), ("A", "B365A")]:
        df[f"bk_odds_{col}"] = df[src].astype(float)
    total_implied = 1/df["bk_odds_H"] + 1/df["bk_odds_D"] + 1/df["bk_odds_A"]
    df["bk_prob_H"] = (1 / df["bk_odds_H"]) / total_implied
    df["bk_prob_D"] = (1 / df["bk_odds_D"]) / total_implied
    df["bk_prob_A"] = (1 / df["bk_odds_A"]) / total_implied

    return df[[
        "season", "home_team", "away_team", "home_goals", "away_goals", "result",
        "bk_prob_H", "bk_prob_D", "bk_prob_A",
        "bk_odds_H", "bk_odds_D", "bk_odds_A",
    ]]


def load_all_seasons() -> pd.DataFrame:
    frames = []
    for season, url in SEASON_URLS.items():
        df = load_season_with_odds(url, season)
        print(f"  {season}: {len(df)} matches")
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ── Edge computation ──────────────────────────────────────────────────────────

def build_edge_table(predictor: PLPredictor, full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the trained model on 2024-25 matches and compute edge vs Bet365.
    Features are computed using only history that would have been available
    at prediction time (no lookahead).
    """
    # calculate_simple_features sorts by season then computes rolling stats —
    # 2024-25 rows naturally come last, so earlier rows are the only history available.
    # Passing full_df (not just test) ensures rich 2022-24 history for the first 2024-25 games.
    print("Computing rolling features for all seasons (this takes ~1 min)...")
    feature_df = predictor.calculate_simple_features(full_df)

    feature_cols = [
        "home_team_strength", "away_team_strength",
        "home_recent_form", "away_recent_form", "home_goals_avg",
    ]
    test_mask = feature_df["season"] == "2024-25"
    X_test = feature_df.loc[test_mask, feature_cols]
    ml_probs_arr = predictor.model.predict_proba(X_test)
    classes = list(predictor.model.classes_)

    rows = []
    for i, (feat_idx, feat_row) in enumerate(feature_df[test_mask].iterrows()):
        probs = dict(zip(classes, ml_probs_arr[i]))
        rows.append({
            "home_team":  feat_row["home_team"],
            "away_team":  feat_row["away_team"],
            "result":     feat_row["result"],
            "ml_prob_H":  probs.get("H", 0.0),
            "ml_prob_D":  probs.get("D", 0.0),
            "ml_prob_A":  probs.get("A", 0.0),
            "bk_prob_H":  feat_row["bk_prob_H"],
            "bk_prob_D":  feat_row["bk_prob_D"],
            "bk_prob_A":  feat_row["bk_prob_A"],
            "bk_odds_H":  feat_row["bk_odds_H"],
            "bk_odds_D":  feat_row["bk_odds_D"],
            "bk_odds_A":  feat_row["bk_odds_A"],
        })

    df = pd.DataFrame(rows)

    # Edge on the outcome the model is most confident about
    df["ml_best"] = df[["ml_prob_H", "ml_prob_D", "ml_prob_A"]].idxmax(axis=1).str[-1]
    df["ml_prob_best"] = df[["ml_prob_H", "ml_prob_D", "ml_prob_A"]].max(axis=1)
    df["bk_prob_best"] = df.apply(lambda r: r[f"bk_prob_{r['ml_best']}"], axis=1)
    df["edge"] = df["ml_prob_best"] - df["bk_prob_best"]

    df["ml_correct"] = df["ml_best"] == df["result"]
    df["bk_best"] = df[["bk_prob_H", "bk_prob_D", "bk_prob_A"]].idxmax(axis=1).str[-1]
    df["bk_correct"] = df["bk_best"] == df["result"]

    return df.sort_values("edge", ascending=False).reset_index(drop=True)


# ── ROI simulation ────────────────────────────────────────────────────────────

def simulate_roi(edge_df: pd.DataFrame, threshold: float = 0.05):
    """Flat-stake bet whenever model edge exceeds threshold."""
    bets = edge_df[edge_df["edge"] > threshold]
    if bets.empty:
        return 0.0, 0.0, 0

    profits = []
    for _, row in bets.iterrows():
        outcome = row["ml_best"]
        odds = row[f"bk_odds_{outcome}"]
        profit = (float(odds) - 1) if (outcome == row["result"]) else -1.0
        profits.append(profit)

    total = sum(profits)
    n = len(profits)
    return total / n, total, n


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_calibration(edge_df: pd.DataFrame):
    """Are ML probabilities actually calibrated? Predicted prob vs actual win rate."""
    records = []
    for outcome in ["H", "D", "A"]:
        sub = edge_df[["ml_prob_" + outcome, "result"]].copy()
        sub["ml_prob"] = sub["ml_prob_" + outcome]
        sub["hit"] = (sub["result"] == outcome).astype(int)
        sub["bucket"] = pd.cut(sub["ml_prob"], bins=6)
        grp = (
            sub.groupby("bucket", observed=True)
            .agg(ml_mean=("ml_prob", "mean"), actual=("hit", "mean"), n=("hit", "count"))
            .dropna()
            .reset_index()
        )
        grp["outcome"] = OUTCOME_LABELS[outcome]
        records.append(grp)

    calib = pd.concat(records, ignore_index=True)
    fig = px.scatter(
        calib, x="ml_mean", y="actual", color="outcome", size="n",
        color_discrete_map={v: c for v, c in zip(
            OUTCOME_LABELS.values(), ["#2196F3", "#FF9800", "#E53935"])},
        labels={"ml_mean": "ML Predicted Probability", "actual": "Actual Win Rate",
                "outcome": "Outcome"},
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(color="gray", dash="dash"))
    fig.update_layout(
        title="Model Calibration: ML Predicted vs Actual Win Rate<br>"
              "<sup>Points on the diagonal = perfectly calibrated</sup>",
        template="plotly_white",
    )
    _save(fig, "edge_calibration.html")


def plot_ml_vs_bookmaker(edge_df: pd.DataFrame):
    """Scatter: ML home-win prob vs Bet365 home-win prob. Color by actual result."""
    fig = px.scatter(
        edge_df, x="bk_prob_H", y="ml_prob_H",
        color="result",
        color_discrete_map={"H": "#43A047", "D": "#FF9800", "A": "#E53935"},
        labels={
            "bk_prob_H": "Bet365 Implied P(Home Win)",
            "ml_prob_H": "ML P(Home Win)",
            "result": "Actual Result",
        },
        hover_data=["home_team", "away_team", "edge"],
        opacity=0.7,
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(color="gray", dash="dash"))
    fig.update_layout(
        title="ML vs Bet365: Home Win Probability (2024-25)<br>"
              "<sup>Above diagonal = model more bullish on home win than bookmaker</sup>",
        template="plotly_white",
    )
    _save(fig, "edge_ml_vs_bookmaker.html")


def plot_edge_distribution(edge_df: pd.DataFrame):
    """Distribution of model edge, split by whether the bet won."""
    fig = px.histogram(
        edge_df, x="edge", color="ml_correct", nbins=25,
        color_discrete_map={True: "#43A047", False: "#E53935"},
        barmode="overlay", opacity=0.7,
        labels={"edge": "Edge (ML prob - Bet365 prob)", "ml_correct": "ML Correct"},
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title="Edge Distribution by Outcome Correctness<br>"
              "<sup>Do positive-edge bets actually win more often?</sup>",
        template="plotly_white",
    )
    _save(fig, "edge_distribution.html")


def plot_roi_by_threshold(edge_df: pd.DataFrame):
    """ROI and bet count as edge threshold increases."""
    thresholds = [t / 100 for t in range(0, 26, 2)]
    rois, n_bets = [], []
    for t in thresholds:
        roi, _, n = simulate_roi(edge_df, threshold=t)
        rois.append(roi * 100)
        n_bets.append(n)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=thresholds, y=rois, mode="lines+markers",
                   name="ROI (%)", line=dict(color="#43A047", width=2)),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=thresholds, y=n_bets, name="Bets placed",
               opacity=0.3, marker_color="#2196F3"),
        secondary_y=True,
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", secondary_y=False)
    fig.update_yaxes(title_text="ROI (%)", secondary_y=False)
    fig.update_yaxes(title_text="Number of Bets", secondary_y=True)
    fig.update_layout(
        title="Simulated ROI by Minimum Edge Threshold (2024-25)<br>"
              "<sup>Higher threshold = fewer but more confident bets</sup>",
        xaxis_title="Minimum Edge to Place Bet",
        template="plotly_white",
    )
    _save(fig, "edge_roi_by_threshold.html")


def plot_cumulative_pnl(edge_df: pd.DataFrame, threshold: float = 0.05):
    """Cumulative P&L over the season for bets above threshold."""
    bets = edge_df[edge_df["edge"] > threshold].copy()
    if bets.empty:
        print(f"No bets at edge > {threshold:.0%}")
        return

    bets["pnl"] = bets.apply(
        lambda r: (float(r[f"bk_odds_{r['ml_best']}"]) - 1)
        if r["ml_best"] == r["result"] else -1.0,
        axis=1,
    )
    bets["cumulative_pnl"] = bets["pnl"].cumsum()
    bets["bet_num"] = range(1, len(bets) + 1)

    color = "#43A047" if bets["cumulative_pnl"].iloc[-1] >= 0 else "#E53935"
    fig = go.Figure(go.Scatter(
        x=bets["bet_num"], y=bets["cumulative_pnl"],
        mode="lines", line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=color.replace(")", ", 0.1)").replace("rgb", "rgba"),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title=f"Cumulative P&L: Bets with Edge > {threshold:.0%} (2024-25 season)<br>"
              f"<sup>{len(bets)} bets placed | "
              f"Final P&L: {bets['cumulative_pnl'].iloc[-1]:+.1f} units</sup>",
        xaxis_title="Bet Number",
        yaxis_title="Cumulative P&L (units)",
        template="plotly_white",
    )
    _save(fig, "edge_cumulative_pnl.html")


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print("=== Football Edge Analysis: ML Model vs Bet365 ===\n")

    print("Downloading match data...")
    full_df = load_all_seasons()
    train_df = full_df[full_df["season"].isin(["2022-23", "2023-24"])].copy()
    test_df  = full_df[full_df["season"] == "2024-25"].copy()
    print(f"\nTrain: {len(train_df)} matches | Test: {len(test_df)} matches")

    print("\nTraining Random Forest on 2022-24...")
    predictor = PLPredictor()
    # Feed only training seasons to the predictor for model fitting
    predictor.match_data = train_df[[
        "season", "home_team", "away_team", "home_goals", "away_goals", "result"
    ]].copy()
    predictor.train_model()

    print("\nComputing edges on 2024-25 season...")
    edge_df = build_edge_table(predictor, full_df)

    # ── Print summary ──────────────────────────────────────────────────────────
    acc_ml = edge_df["ml_correct"].mean()
    acc_bk = edge_df["bk_correct"].mean()

    print(f"\n{'='*55}")
    print(f"Results on 2024-25 season ({len(edge_df)} matches)")
    print(f"{'='*55}")
    print(f"  ML model accuracy:  {acc_ml:.1%}")
    print(f"  Bet365 accuracy:    {acc_bk:.1%}")

    print(f"\n  {'Threshold':>10}  {'Bets':>6}  {'ROI':>8}  {'P&L':>8}")
    print(f"  {'-'*38}")
    for t in [0.02, 0.05, 0.08, 0.12]:
        roi, pnl, n = simulate_roi(edge_df, threshold=t)
        print(f"  {t:>9.0%}  {n:>6}  {roi:>+7.1%}  {pnl:>+7.1f}")

    print(f"\n  Top 5 highest-edge matches:")
    top = edge_df.head(5)[["home_team", "away_team", "ml_best", "ml_prob_best",
                            "bk_prob_best", "edge", "result"]]
    top["edge"] = top["edge"].map(lambda v: f"{v:+.3f}")
    top["ml_prob_best"] = top["ml_prob_best"].map(lambda v: f"{v:.1%}")
    top["bk_prob_best"] = top["bk_prob_best"].map(lambda v: f"{v:.1%}")
    print(top.to_string(index=False))

    print("\nGenerating plots -> plots/ folder...")
    plot_calibration(edge_df)
    plot_ml_vs_bookmaker(edge_df)
    plot_edge_distribution(edge_df)
    plot_roi_by_threshold(edge_df)
    plot_cumulative_pnl(edge_df, threshold=0.05)
    print(f"\nAll charts saved to: {PLOTS_DIR}")
    print("Open any .html file in your browser to view the interactive chart.")

    return edge_df, predictor


if __name__ == "__main__":
    run()
