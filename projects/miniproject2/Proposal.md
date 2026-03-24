# Project Proposal: Financial News Headline Tracker

## What I'm Building

A tool that collects financial news headlines from multiple sources over time and analyzes them for linguistic patterns — word frequency shifts during market events, framing differences across outlets, and sentiment trends correlated with economic indicators.

## Why I Chose This

Financial headlines are one of the few domains where language has measurable, near-immediate real-world consequences — markets move on headlines before anyone reads the article. Studying how outlets frame the same event differently (a rate hike as "aggressive" vs. "decisive" vs. "expected") reveals editorial bias in a way that's quantifiable rather than anecdotal. The data is also more accessible than song lyrics: RSS feeds and news APIs exist, and headlines are short enough that NLP tools perform better on them than on long-form text.

That said, the project's value depends entirely on whether the analysis surfaces patterns that aren't obvious. "Headlines get more negative during crashes" is not an insight. The bar is higher than it looks.

## Core Features

1. **Headline collection pipeline** — automated ingestion from multiple financial news sources (RSS feeds, news APIs) with deduplication, timestamping, and source tagging
2. **Event-correlated word frequency** — track which words spike during specific market events (Fed announcements, earnings seasons, crashes, rallies) compared to baseline periods
3. **Cross-source framing analysis** — compare how different outlets headline the same event, measuring differences in word choice, sentiment, and tone
4. **Sentiment time series** — headline-level sentiment scores plotted against market indices (S&P 500, VIX) to visualize correlation (not causation — an important distinction)
5. **Searchable archive with filters** — browse collected headlines by date range, source, keyword, or sentiment score

## What I Don't Know Yet

### Data Acquisition (Medium-High Risk)

- **Which sources and how?** Major financial outlets (Reuters, Bloomberg, CNBC, WSJ, FT) all have different access models. RSS feeds are free but often truncated or delayed. News APIs (NewsAPI, Finnhub, Alpha Vantage news) have free tiers with tight rate limits and inconsistent coverage. Bloomberg and WSJ are paywalled.
- **How far back can I go?** Most free APIs only return recent headlines (days to weeks). Building a meaningful historical dataset requires either paying for archive access, finding a pre-existing dataset, or waiting weeks/months while your collector runs. The project is less interesting without historical depth.
- **Deduplication is harder than it sounds.** The same story gets syndicated across wire services and rewritten by multiple outlets. Exact string matching won't catch these; fuzzy matching introduces false positives. How aggressively do I deduplicate, and does that distort cross-source comparisons?

### Defining "Events" (High Risk)

- The most interesting analysis requires correlating headlines with market events, but "event" is poorly defined. Is a Fed rate decision one event or a week-long news cycle? Does an earnings miss count if the stock barely moves?
- Manual event tagging doesn't scale. Automated event detection from market data (unusual price moves, volatility spikes) is a separate engineering problem that could easily consume the entire project.
- Without clean event boundaries, the word frequency analysis degrades to "words that were popular in March" rather than "words that spike during rate hikes."

### NLP on Headlines (Medium Risk)

- Headlines are short (5-15 words), which is both an advantage (less noise) and a disadvantage (less signal per unit). Sentiment tools work better here than on poetry, but financial language has its own problems: "beat expectations" is positive, "beat down" is negative, and generic sentiment tools don't know the difference.
- Financial-specific sentiment lexicons exist (Loughran-McDonald) but were built for 10-K filings, not headlines. They're better than VADER for this domain but still imperfect.
- Sarcasm and editorializing in opinion-adjacent headlines ("The Fed's Latest Magic Trick") will confuse any automated approach.

### Framing Analysis (High Risk)

- "Framing differences across sources" sounds compelling but is methodologically slippery. How do I operationalize "framing"? Word choice differences? Sentiment polarity? Presence/absence of causal attribution? Each approach captures a different slice of what "framing" means, and none captures all of it.
- Sample size per event per source may be too small. If Reuters publishes 3 headlines about a rate decision and CNBC publishes 5, is that enough to draw conclusions about systematic framing differences?
- Survivorship bias: I'll only capture headlines that exist in my data sources. Outlets that don't headline a story are making an editorial choice I can't measure.

### Correlation vs. Causation Trap

- The temptation to claim "negative headlines predict market drops" will be strong. This is a well-studied area in academic finance, and the results are mixed at best. Headline sentiment and market moves are both driven by the same underlying events — any correlation is largely spurious.
- If the project presents correlations without heavy caveats, it will look like a trading signal generator, which it isn't and shouldn't pretend to be.

## Realistic Scope and Constraints

- **MVP scope:** Collect headlines from 3 sources via RSS/free API for 2-4 weeks. Compute daily word frequencies and basic sentiment. Plot sentiment against S&P 500 closing prices. No event detection, no framing analysis in v1.
- **Time allocation:** ~40% on the collection pipeline and storage, ~20% on cleaning/deduplication, ~30% on analysis and visualization, ~10% on everything else.
- **Primary failure mode:** Collecting a pile of headlines, computing sentiment scores, plotting them against a stock chart, and discovering the correlation is ~0.05. This is the most likely outcome, and the project needs to be structured so that the infrastructure and analysis process are the deliverables, not the correlation.

## Technology Stack (Tentative)

| Layer | Tool | Risk Level |
|---|---|---|
| Data collection | feedparser (RSS), NewsAPI or Finnhub (API) | Medium — free tier limits, source availability |
| Storage | SQLite (MVP) or PostgreSQL (if scaling) | Low |
| Scheduling | cron job or APScheduler | Low |
| Text processing | spaCy or NLTK for tokenization | Low |
| Sentiment | Loughran-McDonald lexicon (finance-specific), VADER as baseline | Medium |
| Market data | yfinance (Yahoo Finance API wrapper) | Low-Medium — unofficial, can break |
| Visualization | Plotly or Streamlit dashboard | Low |
| Language | Python 3.10+ | Low |

## Success Criteria

The project succeeds if:

1. The collection pipeline runs unattended for 2+ weeks without data loss or silent failures
2. I can query headlines by date, source, and keyword with sub-second response times
3. Word frequency analysis reveals at least one non-obvious pattern (something I wouldn't have guessed before looking at the data)
4. Sentiment time series is presentable alongside market data, with appropriate disclaimers about what it does and doesn't show
5. The infrastructure is reusable — I could point it at a different domain (politics, tech, sports) without rewriting the core

The project fails if:

1. Free data sources are too limited and I can't collect enough headlines to analyze
2. Deduplication is unsolved and the analysis is dominated by wire service reprints
3. Every "insight" is either trivially obvious ("headlines were negative during the crash") or noise
4. I fall into the correlation-as-causation trap and build a pseudo-trading-signal dashboard

## Next Steps

1. Audit 3-5 free headline sources (RSS feeds, NewsAPI free tier, Finnhub) for coverage, latency, and format consistency
2. Build the collection pipeline for one source and run it for 48 hours to assess data quality and volume
3. Design the database schema with source attribution, timestamps, and deduplication hashes
4. Compute baseline word frequencies on the initial dataset before attempting any event correlation