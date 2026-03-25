# Project Proposal: Financial Deal Comparison Tool

## What I'm Building

A side-by-side comparison tool that takes two M&A or investment deals and surfaces differences in valuation multiples, synergy assumptions, and integration cost estimates — so a user can quickly see which deal is more aggressively priced and where the numbers diverge.

## Why I Chose This

In practice, comparing two deals means toggling between spreadsheets, CIMs, and broker decks while manually normalizing metrics that each side defines differently. The work is tedious, error-prone, and time-sensitive — usually done under deadline pressure during a live process. Most of the "analysis" is actually data wrangling. A purpose-built comparison tool would eliminate the grunt work and force both deals into a common framework, making it harder to miss a buried assumption.

## Core Features

- **Entry multiple comparison:** Input purchase price, revenue, EBITDA, and other headline figures for two deals. The tool calculates and displays implied EV/Revenue, EV/EBITDA, and other entry multiples side by side with percentage deltas.
- **Historical trading range context:** Plot each deal's implied multiples against the target's (or comparable public companies') historical trading ranges (e.g., 52-week, 3-year) so the user can see how each entry price sits relative to where the market has actually traded.
- **Comparable transaction benchmarking:** Overlay implied multiples against a set of precedent transactions in the same sector, flagging where either deal falls outside the interquartile range.
- **Revenue synergy stress test:** Break down each deal's stated revenue synergies by category (cross-sell, pricing, new market, etc.) and show what percentage of the purchase price each synergy assumption is effectively subsidizing. Highlight which deal relies more heavily on synergies that have no historical precedent in the combined entity's track record.
- **Integration cost comparison:** Standardize integration cost estimates (severance, systems migration, facility consolidation, advisory fees, etc.) into common categories and show total cost as a percentage of deal value, with a flag for any category where one deal's estimate is significantly lower than the other's or below industry base rates.

## What I Don't Know Yet

- **Data input format:** Whether to support manual entry only, or also parse common formats (e.g., Excel models, PDF tear sheets). Parsing is a large scope increase and may not be worth it for a first version.
- **Source of comparable transaction data:** Public comps databases (Capital IQ, PitchBook) are expensive and have licensing restrictions. I may need to rely on user-supplied comps or a limited free dataset, which constrains the benchmarking feature significantly.
- **Historical trading data access:** Same problem — reliable historical EV multiples require a market data feed or API (Bloomberg, Refinitiv, etc.). Free alternatives exist but are spotty for enterprise value metrics specifically.
- **How to handle different accounting treatments:** Deals use adjusted vs. reported EBITDA, calendarized vs. fiscal-year revenue, run-rate vs. trailing metrics. Normalizing across two deals that define terms differently is a hard problem, and getting it wrong silently is worse than not doing it at all.
- **Synergy categorization standards:** There is no universal taxonomy for revenue vs. cost synergies. I need to decide on a classification scheme and accept that it won't perfectly map to how every deal presents its synergies.
- **Scope of "integration costs":** Some deals bury integration costs in synergy timelines, others break them out. Defining what counts — and what to do when a deal doesn't disclose a category at all — is an open design question.
- **Regulatory and confidentiality constraints:** If this tool is used during a live process, the data is highly sensitive. I need to decide early whether this runs locally, in a secure cloud environment, or whether that's out of scope for now.