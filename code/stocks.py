import os
import json
import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request, redirect, url_for, flash

from apscheduler.schedulers.background import BackgroundScheduler
import pytz

APP_TZ = pytz.timezone("America/New_York")

DB_PATH = "app.db"
DEFAULT_UNIVERSE = [
    # Keep it conservative: liquid, large-cap names. Expand carefully.
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","BRK-B","JPM","LLY","AVGO",
    "XOM","UNH","V","PG","MA","COST","HD","MRK","ADBE","PEP","KO","WMT",
    "CRM","ABBV","BAC","TMO","CSCO","ACN","MCD","NFLX"
]

# Strategy params (simple and explicit; not "AI")
TOP_N = 8
MOMENTUM_LOOKBACK_DAYS = 126   # ~6 months
VOL_LOOKBACK_DAYS = 63         # ~3 months
MAX_SINGLE_WEIGHT = 0.20       # risk control
MIN_PRICE = 5.0                # avoid penny/low-price issues
CASH_TICKER = "CASH"           # pseudo ticker in DB only (not traded)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

# -----------------------
# Database helpers
# -----------------------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        k TEXT PRIMARY KEY,
        v TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS holdings (
        ticker TEXT PRIMARY KEY,
        shares REAL NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        ts TEXT PRIMARY KEY,
        payload TEXT NOT NULL
    )
    """)
    conn.commit()

    # Defaults
    set_setting_if_missing("universe", json.dumps(DEFAULT_UNIVERSE))
    set_setting_if_missing("capital_usd", "10000")
    set_setting_if_missing("top_n", str(TOP_N))
    set_setting_if_missing("max_single_weight", str(MAX_SINGLE_WEIGHT))

    # Ensure CASH exists
    cur.execute("SELECT ticker FROM holdings WHERE ticker=?", (CASH_TICKER,))
    if cur.fetchone() is None:
        cur.execute("INSERT OR REPLACE INTO holdings(ticker, shares) VALUES (?, ?)", (CASH_TICKER, 10000.0))
        conn.commit()
    conn.close()

def set_setting_if_missing(k: str, v: str):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT k FROM settings WHERE k=?", (k,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO settings(k, v) VALUES (?, ?)", (k, v))
        conn.commit()
    conn.close()

def get_setting(k: str, default=None):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT v FROM settings WHERE k=?", (k,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return default
    return row["v"]

def set_setting(k: str, v: str):
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings(k, v) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

def get_universe():
    raw = get_setting("universe", json.dumps(DEFAULT_UNIVERSE))
    try:
        u = json.loads(raw)
        if not isinstance(u, list):
            return DEFAULT_UNIVERSE
        return u
    except Exception:
        return DEFAULT_UNIVERSE

def get_holdings():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT ticker, shares FROM holdings")
    rows = cur.fetchall()
    conn.close()
    return {r["ticker"]: float(r["shares"]) for r in rows}

def upsert_holding(ticker: str, shares: float):
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO holdings(ticker, shares) VALUES (?, ?)", (ticker.upper(), float(shares)))
    conn.commit()
    conn.close()

# -----------------------
# Market data + signals
# -----------------------
def download_prices(tickers, start, end):
    """
    Pulls adjusted close. yfinance is convenient but not robust:
    - occasional missing data
    - rate limits
    - split/dividend adjustments can be inconsistent for some tickers
    """
    df = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        progress=False,
        auto_adjust=True,
        group_by="ticker",
        threads=True
    )

    # Normalize to a DataFrame of Adj Close-like series
    if isinstance(df.columns, pd.MultiIndex):
        # MultiIndex like (ticker, field)
        closes = {}
        for t in tickers:
            if (t, "Close") in df.columns:
                closes[t] = df[(t, "Close")]
        prices = pd.DataFrame(closes)
    else:
        # Single ticker returns columns: Open High Low Close Volume
        if "Close" in df.columns:
            prices = pd.DataFrame({tickers[0]: df["Close"]})
        else:
            prices = pd.DataFrame()

    prices = prices.dropna(how="all")
    return prices

def compute_signals(prices: pd.DataFrame):
    """
    Simple weekly selection model:
    - 6M momentum (total return)
    - 3M realized volatility penalty
    Score = momentum / volatility
    """
    # Basic data hygiene
    last_prices = prices.ffill().iloc[-1]
    valid = last_prices[last_prices >= MIN_PRICE].index.tolist()
    prices = prices[valid].dropna(axis=1, how="any")

    if prices.shape[1] == 0:
        return pd.DataFrame(columns=["ticker", "momentum", "vol", "score"])

    # Momentum: (P_t / P_{t-L}) - 1
    Lm = MOMENTUM_LOOKBACK_DAYS
    Lv = VOL_LOOKBACK_DAYS

    if len(prices) < max(Lm, Lv) + 5:
        # not enough history
        return pd.DataFrame(columns=["ticker", "momentum", "vol", "score"])

    mom = (prices.iloc[-1] / prices.iloc[-Lm] - 1.0)

    rets = prices.pct_change().dropna()
    vol = rets.tail(Lv).std() * np.sqrt(252.0)

    # Avoid divide-by-zero
    vol = vol.replace(0, np.nan)

    score = mom / vol

    out = pd.DataFrame({
        "ticker": score.index,
        "momentum": mom.reindex(score.index).values,
        "vol": vol.reindex(score.index).values,
        "score": score.values
    }).dropna().sort_values("score", ascending=False)

    return out

# -----------------------
# Portfolio + rebalancing
# -----------------------
def estimate_portfolio_value_usd(holdings: dict, prices: pd.Series):
    """
    holdings: {ticker: shares}, includes CASH as USD
    prices: last close series for tickers
    """
    value = 0.0
    for t, sh in holdings.items():
        if t == CASH_TICKER:
            value += float(sh)
        else:
            px = float(prices.get(t, np.nan))
            if np.isfinite(px):
                value += float(sh) * px
    return value

def current_weights(holdings: dict, last_prices: pd.Series):
    total = estimate_portfolio_value_usd(holdings, last_prices)
    w = {}
    for t, sh in holdings.items():
        if t == CASH_TICKER:
            w[t] = float(sh) / total if total > 0 else 0
        else:
            px = float(last_prices.get(t, np.nan))
            if np.isfinite(px) and total > 0:
                w[t] = (float(sh) * px) / total
    return total, w

def target_weights(selected, max_single_weight, top_n):
    """
    Equal-weight with cap; leftover goes to CASH.
    """
    if len(selected) == 0:
        return {CASH_TICKER: 1.0}

    n = min(len(selected), top_n)
    base = 1.0 / n

    # Apply cap and renormalize
    capped = [min(base, max_single_weight) for _ in range(n)]
    alloc_sum = sum(capped)
    if alloc_sum <= 0:
        return {CASH_TICKER: 1.0}

    # Renormalize within equity slice, keep any unalloc as CASH
    tw = {t: (c / alloc_sum) * min(1.0, alloc_sum) for t, c in zip(selected[:n], capped)}
    cash = max(0.0, 1.0 - sum(tw.values()))
    tw[CASH_TICKER] = cash
    return tw

def generate_trade_list(holdings, last_prices, target_w, min_trade_usd=25.0):
    """
    Generates dollar-delta trades and approximate share trades.
    Not broker-specific. No order types, no routing, no guarantees.
    """
    total_value, cw = current_weights(holdings, last_prices)

    trades = []
    tickers = set(list(cw.keys()) + list(target_w.keys()))
    tickers.discard(CASH_TICKER)

    for t in sorted(tickers):
        cur_w = cw.get(t, 0.0)
        tgt_w = target_w.get(t, 0.0)
        delta_w = tgt_w - cur_w
        delta_usd = delta_w * total_value

        if abs(delta_usd) < min_trade_usd:
            continue

        px = float(last_prices.get(t, np.nan))
        if not np.isfinite(px) or px <= 0:
            continue

        delta_shares = delta_usd / px
        trades.append({
            "ticker": t,
            "action": "BUY" if delta_usd > 0 else "SELL",
            "delta_usd": round(delta_usd, 2),
            "est_price": round(px, 2),
            "est_shares": round(delta_shares, 4),
        })

    # Sort: sells first (to fund buys), then larger magnitude
    trades = sorted(trades, key=lambda x: (0 if x["action"] == "SELL" else 1, -abs(x["delta_usd"])))
    return total_value, cw, trades

# -----------------------
# Weekly recommendation run
# -----------------------
def run_weekly_recommendation():
    universe = get_universe()
    top_n = int(float(get_setting("top_n", str(TOP_N))))
    max_single_weight = float(get_setting("max_single_weight", str(MAX_SINGLE_WEIGHT)))

    end = datetime.now(APP_TZ).date()
    start = end - timedelta(days=365)

    prices = download_prices(universe, start=start.isoformat(), end=(end + timedelta(days=1)).isoformat())
    if prices.empty:
        payload = {
            "ts": datetime.now(APP_TZ).isoformat(),
            "error": "No price data returned. yfinance can fail or rate-limit.",
        }
        save_recommendation(payload)
        return payload

    signals = compute_signals(prices)
    selected = signals["ticker"].head(top_n).tolist()

    last_prices = prices.ffill().iloc[-1]
    holdings = get_holdings()

    tw = target_weights(selected, max_single_weight=max_single_weight, top_n=top_n)
    total_value, cw, trades = generate_trade_list(holdings, last_prices, tw)

    payload = {
        "ts": datetime.now(APP_TZ).isoformat(),
        "universe_size": len(universe),
        "selected": selected,
        "signals_top": signals.head(15).to_dict(orient="records"),
        "portfolio_value_est": round(total_value, 2),
        "current_weights": {k: round(v, 4) for k, v in cw.items()},
        "target_weights": {k: round(v, 4) for k, v in tw.items()},
        "trades": trades,
        "notes": [
            "This is a naive momentum/volatility screen. It is not a guarantee of performance.",
            "Trade list ignores taxes, spreads, slippage, liquidity, corporate actions, and broker constraints.",
            "If you want auto-trading, add broker integration plus hard risk controls and testing."
        ]
    }
    save_recommendation(payload)
    return payload

def save_recommendation(payload: dict):
    conn = db()
    cur = conn.cursor()
    ts = payload.get("ts", datetime.now(APP_TZ).isoformat())
    cur.execute("INSERT OR REPLACE INTO recommendations(ts, payload) VALUES (?, ?)", (ts, json.dumps(payload)))
    conn.commit()
    conn.close()

def latest_recommendation():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT ts, payload FROM recommendations ORDER BY ts DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return json.loads(row["payload"])

# -----------------------
# Flask routes
# -----------------------
@app.route("/", methods=["GET"])
def index():
    rec = latest_recommendation()
    holdings = get_holdings()
    universe = get_universe()
    settings = {
        "top_n": get_setting("top_n", str(TOP_N)),
        "max_single_weight": get_setting("max_single_weight", str(MAX_SINGLE_WEIGHT)),
        "capital_usd": get_setting("capital_usd", "10000"),
    }
    return render_template("index.html", rec=rec, holdings=holdings, universe=universe, settings=settings)

@app.route("/run", methods=["POST"])
def run_now():
    payload = run_weekly_recommendation()
    if "error" in payload:
        flash(payload["error"], "error")
    else:
        flash("Recommendation updated.", "ok")
    return redirect(url_for("index"))

@app.route("/settings", methods=["POST"])
def update_settings():
    top_n = request.form.get("top_n", str(TOP_N))
    max_single_weight = request.form.get("max_single_weight", str(MAX_SINGLE_WEIGHT))
    universe_raw = request.form.get("universe", "")

    # Parse universe as comma-separated tickers
    if universe_raw.strip():
        u = [t.strip().upper().replace(" ", "") for t in universe_raw.split(",") if t.strip()]
        # Basic sanity
        u = [t for t in u if len(t) <= 10]
        if len(u) >= 5:
            set_setting("universe", json.dumps(u))

    # Store params
    try:
        top_n_i = max(1, min(50, int(float(top_n))))
        set_setting("top_n", str(top_n_i))
    except Exception:
        pass

    try:
        w = float(max_single_weight)
        w = max(0.01, min(1.0, w))
        set_setting("max_single_weight", str(w))
    except Exception:
        pass

    flash("Settings saved.", "ok")
    return redirect(url_for("index"))

@app.route("/holdings", methods=["POST"])
def update_holdings():
    """
    Manual holdings entry (paper portfolio).
    For real brokerage holdings, you'd pull positions via broker API instead.
    """
    ticker = request.form.get("ticker", "").upper().strip()
    shares = request.form.get("shares", "").strip()

    if not ticker:
        return redirect(url_for("index"))

    try:
        sh = float(shares)
    except Exception:
        flash("Shares must be a number.", "error")
        return redirect(url_for("index"))

    upsert_holding(ticker, sh)
    flash("Holding updated.", "ok")
    return redirect(url_for("index"))

@app.route("/export_latest.json", methods=["GET"])
def export_latest():
    rec = latest_recommendation()
    if rec is None:
        return {}, 404
    return rec

# -----------------------
# Scheduler (weekly)
# -----------------------
def start_scheduler():
    sched = BackgroundScheduler(timezone=APP_TZ)

    # Weekly run: Monday 09:35 ET (after open; still noisy but workable)
    # You can change to weekend if you want "as of Friday close" logic.
    sched.add_job(run_weekly_recommendation, "cron", day_of_week="mon", hour=9, minute=35)

    sched.start()
    return sched

if __name__ == "__main__":
    init_db()
    start_scheduler()
    # Replit: host 0.0.0.0, port from env
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
