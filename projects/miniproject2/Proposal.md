## My Project Proposal

**What I'm building:** A Python tool that analyzes product reviews for statistical and linguistic patterns commonly associated with fake or manufactured reviews.

**Why I chose this:** Online reviews heavily influence purchasing decisions, and a significant percentage of them are fabricated. I want a practical way to flag suspicious reviews before I (or anyone) waste money on a product propped up by astroturfing. It also forces me to work with real text data, which is messier and more instructive than toy datasets.

**Core features:**

- Detect repetitive or templated phrasing across a set of reviews (e.g., near-duplicate sentences, copy-paste patterns)
- Flag unusual word choices that deviate from how normal buyers write (overly promotional language, unnatural sentence structure, keyword stuffing)
- Measure review similarity using text comparison techniques (cosine similarity, Jaccard index) to catch coordinated fake review campaigns
- Analyze metadata signals where available: review timing clusters, reviewer history patterns, rating distribution anomalies (e.g., a product with 90% five-star and 10% one-star, nothing in between)
- Generate a per-review suspicion score with a plain-language explanation of why it was flagged

**What I don't know yet:**

- Where to get a reliably labeled dataset of confirmed fake vs. real reviews (the Ott et al. dataset exists but is small and old; scraping live data raises legal and ethical questions)
- How to set meaningful thresholds for "suspicious" without generating a flood of false positives — base rates for fake reviews vary wildly by product category and platform
- Whether simple heuristic/statistical methods will be good enough, or if this will require actual ML classifiers (and if so, whether I have enough labeled data to train one that isn't just memorizing noise)
- How to handle adversarial evolution — fake review operations constantly change tactics, so any detection rules I write today may be stale quickly
- How to evaluate accuracy honestly when ground truth is inherently uncertain (you often can't prove a review is fake without internal platform data)