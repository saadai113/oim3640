"""
compare.py
Category comparison analysis for Polymarket markets.
Compares Sports, Politics, and Crypto markets across:
  - Bid-ask spread (market efficiency)
  - Liquidity (depth)
  - 24h trading volume (activity)
  - Price volatility (|24h change|)
  - Yes-price distribution (market certainty)

Run:  python compare.py
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from categories import load

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def _save(fig, name: str):
    path = os.path.join(PLOTS_DIR, name)
    fig.write_html(path)
    print(f"  Saved: plots/{name}")

TARGET_CATS = ["Sports", "Politics", "Crypto"]
COLORS = {"Sports": "#2196F3", "Politics": "#E53935", "Crypto": "#43A047"}


# ── Summary stats ─────────────────────────────────────────────────────────────

def summary(df: pd.DataFrame) -> pd.DataFrame:
    data = df[df["category"].isin(TARGET_CATS)].copy()
    data["abs_change"] = data["day_change"].abs()
    stats = (
        data.groupby("category")
        .agg(
            markets=("question", "count"),
            median_spread=("spread", "median"),
            median_liquidity=("liquidity", "median"),
            total_volume_24h=("volume_24h", "sum"),
            median_volatility=("abs_change", "median"),
            median_yes_price=("yes_price", "median"),
        )
        .round(4)
    )
    return stats


# ── Individual plots ───────────────────────────────────────────────────────────

def plot_spread(df: pd.DataFrame):
    data = df[df["category"].isin(TARGET_CATS) & df["spread"].notna()]
    data = data[data["spread"].between(0, 0.5)]  # drop extreme outliers
    fig = px.box(
        data, x="category", y="spread", color="category",
        color_discrete_map=COLORS,
        labels={"spread": "Bid-Ask Spread", "category": ""},
        points="outliers",
    )
    fig.update_layout(
        title="Bid-Ask Spread by Category<br><sup>Lower = more efficient market</sup>",
        template="plotly_white", showlegend=False,
    )
    _save(fig, "spread.html")


def plot_liquidity(df: pd.DataFrame):
    data = df[df["category"].isin(TARGET_CATS) & (df["liquidity"] > 0)]
    fig = px.box(
        data, x="category", y="liquidity", color="category",
        color_discrete_map=COLORS,
        log_y=True,
        labels={"liquidity": "Liquidity (USD, log scale)", "category": ""},
        points="outliers",
    )
    fig.update_layout(
        title="Market Liquidity by Category<br><sup>Higher = more capital available to trade</sup>",
        template="plotly_white", showlegend=False,
    )
    _save(fig, "liquidity.html")


def plot_volume(df: pd.DataFrame):
    data = df[df["category"].isin(TARGET_CATS)]
    totals = data.groupby("category")["volume_24h"].sum().reset_index()
    totals["volume_M"] = totals["volume_24h"] / 1_000_000
    fig = px.bar(
        totals, x="category", y="volume_M", color="category",
        color_discrete_map=COLORS,
        labels={"volume_M": "Volume (USD millions)", "category": ""},
        text=totals["volume_M"].map(lambda v: f"${v:.2f}M"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="Total 24h Trading Volume by Category",
        template="plotly_white", showlegend=False,
    )
    _save(fig, "volume.html")


def plot_volatility(df: pd.DataFrame):
    data = df[df["category"].isin(TARGET_CATS) & df["day_change"].notna()].copy()
    data["abs_change"] = data["day_change"].abs()
    fig = px.box(
        data, x="category", y="abs_change", color="category",
        color_discrete_map=COLORS,
        labels={"abs_change": "|24h Price Change|", "category": ""},
        points="outliers",
    )
    fig.update_layout(
        title="24h Price Volatility by Category<br><sup>Higher = prices moving more</sup>",
        template="plotly_white", showlegend=False,
    )
    _save(fig, "volatility.html")


def plot_certainty(df: pd.DataFrame):
    data = df[df["category"].isin(TARGET_CATS)]
    fig = px.histogram(
        data, x="yes_price", color="category",
        color_discrete_map=COLORS,
        facet_col="category",
        nbins=20,
        range_x=[0, 1],
        labels={"yes_price": "Yes Price (implied probability)", "category": ""},
    )
    fig.update_layout(
        title="Market Certainty by Category<br><sup>Peaks near 0/1 = market has made up its mind; flat = uncertain</sup>",
        template="plotly_white", showlegend=False,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    _save(fig, "certainty.html")


def plot_dashboard(df: pd.DataFrame):
    """Single combined figure with all four key metrics."""
    data = df[df["category"].isin(TARGET_CATS)].copy()
    data["abs_change"] = data["day_change"].abs()
    totals = data.groupby("category")["volume_24h"].sum().reset_index()
    totals["volume_M"] = totals["volume_24h"] / 1_000_000

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Bid-Ask Spread (lower = more efficient)",
            "Market Liquidity (USD, log scale)",
            "Total 24h Volume (USD millions)",
            "Price Volatility |24h Change|",
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    for cat in TARGET_CATS:
        color = COLORS[cat]
        cat_data = data[data["category"] == cat]

        # Spread
        spread_clean = cat_data["spread"].dropna()
        spread_clean = spread_clean[spread_clean.between(0, 0.5)]
        fig.add_trace(go.Box(y=spread_clean, name=cat, marker_color=color,
                             showlegend=True, legendgroup=cat), row=1, col=1)

        # Liquidity
        liq = cat_data[cat_data["liquidity"] > 0]["liquidity"]
        fig.add_trace(go.Box(y=liq, name=cat, marker_color=color,
                             showlegend=False, legendgroup=cat), row=1, col=2)

        # Volatility
        vol = cat_data["abs_change"].dropna()
        fig.add_trace(go.Box(y=vol, name=cat, marker_color=color,
                             showlegend=False, legendgroup=cat), row=2, col=2)

    # Volume bar (separate loop since it's per-category totals)
    for cat in TARGET_CATS:
        row = totals[totals["category"] == cat]
        fig.add_trace(go.Bar(
            x=[cat], y=row["volume_M"].values,
            marker_color=COLORS[cat], name=cat,
            showlegend=False, legendgroup=cat,
            text=[f"${row['volume_M'].values[0]:.2f}M"],
            textposition="outside",
        ), row=2, col=1)

    fig.update_yaxes(type="log", row=1, col=2)
    fig.update_layout(
        title="Polymarket Category Comparison — Sports vs Politics vs Crypto",
        template="plotly_white",
        height=700,
        font=dict(family="Inter, sans-serif", size=12),
    )
    _save(fig, "dashboard.html")


# ── Main ──────────────────────────────────────────────────────────────────────

def run(df: pd.DataFrame = None):
    if df is None:
        df = load(limit=300)

    stats = summary(df)
    print("\n=== Category Comparison Summary ===")
    print(stats.to_string())

    print(f"\nGenerating charts → plots/ folder...")
    plot_dashboard(df)
    plot_spread(df)
    plot_liquidity(df)
    plot_volume(df)
    plot_volatility(df)
    plot_certainty(df)
    print(f"\nAll charts saved to: {PLOTS_DIR}")
    print("Open any .html file in your browser to view the interactive chart.")

    return df, stats


if __name__ == "__main__":
    run()
