#!/usr/bin/env python3
"""
Financial Deal Wording Analyzer
================================
Analyzes the actual language used in deal press releases and filings
to detect patterns that signal confidence levels, synergy inflation,
risk hedging, and vagueness in financial commitments.

Methodology:
- Categorize phrases into signal buckets (hard commitments vs. aspirational language)
- Count quantified vs. unquantified claims
- Flag hedge words, weasel phrases, and circular justifications
- Compare disclosure density between deals

Deals analyzed:
  1. VMG / Downtown Music Holdings ($775M)
  2. Playlist + EGYM Merger ($7.5B EV)

Sources: Direct quotes from press releases and public filings (cited inline).
"""

import re
from dataclasses import dataclass, field
from collections import Counter


# =============================================================================
# ANSI COLOR HELPERS
# =============================================================================

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    WHITE  = "\033[97m"


def _ansi(code: str, text: str) -> str:
    return f"{code}{text}{C.RESET}"

def bold(t):    return _ansi(C.BOLD,   t)
def cyan(t):    return _ansi(C.CYAN,   t)
def green(t):   return _ansi(C.GREEN,  t)
def red(t):     return _ansi(C.RED,    t)
def yellow(t):  return _ansi(C.YELLOW, t)
def blue(t):    return _ansi(C.BLUE,   t)
def dim(t):     return _ansi(C.DIM,    t)
def white(t):   return _ansi(C.WHITE,  t)


def strip_ansi(s: str) -> str:
    """Return string with all ANSI escape codes removed."""
    return re.sub(r'\033\[[0-9;]*m', '', s)


def cpad(s: str, width: int) -> str:
    """Left-pad a possibly-colored string to visible width."""
    return s + " " * max(0, width - len(strip_ansi(s)))


# =============================================================================
# DEAL TEXT CORPUS
# Each quote is tagged with its source URL.
# =============================================================================

DOWNTOWN_QUOTES = [
    {
        "text": "marking a significant milestone in the creation of a global, end-to-end solution that meets the evolving needs of independent entrepreneurs, artists, and rights holders",
        "source": "https://www.prnewswire.com/news-releases/virgin-music-group-completes-acquisition-of-downtown-302693634.html",
        "context": "Deal completion press release — headline framing",
    },
    {
        "text": "This combination enhances the choice, service and global reach available to the independent community",
        "source": "https://www.prnewswire.com/news-releases/virgin-music-group-completes-acquisition-of-downtown-302693634.html",
        "context": "Pieter van Rijn (new VMG COO) quote",
    },
    {
        "text": "This is about making both Virgin Music Group and Downtown even better — preserving their distinct strengths while increasing the investment, technology and global resources available to independent entrepreneurs",
        "source": "https://musically.com/2026/02/20/virgin-music-group-completes-downtown-music-holdings-acquisition/",
        "context": "Nat Pastor (VMG co-CEO) quote",
    },
    {
        "text": "Pieter's appointment signals our intent to bring these businesses together thoughtfully and strategically",
        "source": "https://www.musicweek.com/talent/read/virgin-music-group-completes-downtown-acquisition-with-new-role-for-pieter-van-rijn/093616",
        "context": "Nat Pastor quote on integration approach",
    },
    {
        "text": "Downtown is expected to generate about $40 million in EBITDA on about $130 million in net revenue, or $900 million in total revenues",
        "source": "https://www.billboard.com/pro/downtown-music-holdings-sale-board-exploring/",
        "context": "Billboard report citing 3 anonymous sources — the ONLY financial disclosure",
    },
    {
        "text": "Downtown, like most services businesses, is a single-digit margin company",
        "source": "https://www.musicbusinessworldwide.com/4-observations-on-downtowns-775-million-sale-to-universal-music-group-virgin-music-group/",
        "context": "MBW editorial analysis of Downtown's economics",
    },
    {
        "text": "the European Commission approved the $775 million acquisition but only on the condition of a full divestment of Downtown's royalty accounting platform, Curve Royalty Systems",
        "source": "https://imusician.pro/en/resources/blog/virgin-music-completes-downtown-acquisition",
        "context": "Regulatory condition — forced asset divestiture",
    },
]

PLAYLIST_EGYM_QUOTES = [
    {
        "text": "The transaction includes $785 million in new equity investments and values the combined enterprise at $7.5 billion",
        "source": "https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        "context": "Lead sentence of press release — deal terms",
    },
    {
        "text": "In 2025, Playlist and EGYM generated more than $800 million in net revenue while maintaining high-growth momentum and strong profitability",
        "source": "https://us.egym.com/en-us/playlist-egym-announce-merger",
        "context": "The ONLY financial statement in the entire announcement",
    },
    {
        "text": "the combined company will unite software, connected hardware, consumer platforms, and corporate wellness solutions to create a global destination for wellbeing",
        "source": "https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        "context": "Strategic rationale description",
    },
    {
        "text": "This merger represents a pivotal moment for both our companies as we continue to build the infrastructure behind the world's most meaningful in-person wellness experiences",
        "source": "https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        "context": "Fritz Lanman (Playlist CEO) quote",
    },
    {
        "text": "We believe the combined scale and connectivity will unlock network effects across studios, employers, and consumers, helping accelerate adoption and deepen engagement",
        "source": "https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        "context": "Monti Saroya (Vista Equity Partners co-head) quote",
    },
    {
        "text": "Bringing EGYM together with the newly created Playlist under one roof represents a profound opportunity to impact lives through preventative health",
        "source": "https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        "context": "Philipp Roesch-Schlanderer (EGYM CEO) quote",
    },
    {
        "text": "we're uniting multiple layers of wellness—software, connected hardware, consumer booking, and workplace wellbeing—into one global platform",
        "source": "https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        "context": "Lanman quote continued — platform narrative",
    },
    {
        "text": "The new equity funding will support increased investment in artificial intelligence to help fitness studios, gyms, and wellness operators run more efficiently and deepen member engagement",
        "source": "https://us.egym.com/en-us/playlist-egym-announce-merger",
        "context": "Use of proceeds — AI investment",
    },
]


# =============================================================================
# WORDING ANALYSIS FRAMEWORK
# =============================================================================

# Pattern categories — each is a signal about deal quality/confidence
PATTERNS = {
    "hard_numbers": {
        "description": "Specific quantified financial commitments (dollar amounts, percentages, timelines)",
        "signal": "POSITIVE — concrete, verifiable, management has skin in the game",
        "examples": ["$800 million in cost synergies", "18% RoTE by 2028", "7-8% EPS accretion"],
    },
    "soft_numbers": {
        "description": "Approximate or hedged quantification ('more than', 'approximately', 'about')",
        "signal": "NEUTRAL — provides a floor but avoids commitment to a specific figure",
        "examples": ["more than $800 million in net revenue", "about $40 million in EBITDA"],
    },
    "aspirational_language": {
        "description": "Forward-looking claims with no quantification ('will unlock', 'opportunity to', 'vision')",
        "signal": "NEGATIVE — no verifiable commitment, pure narrative",
        "examples": ["will unlock network effects", "represents a profound opportunity"],
    },
    "hedge_words": {
        "description": "Words that reduce commitment ('believe', 'expect', 'may', 'could', 'potential')",
        "signal": "NEGATIVE — management hedging their bets",
        "examples": ["we believe this will", "expected to", "potential to"],
    },
    "buzzword_density": {
        "description": "Industry jargon and marketing language ('AI-driven', 'global platform', 'ecosystem')",
        "signal": "NEGATIVE — substitutes substance with vocabulary",
        "examples": ["AI-enabled", "global destination for wellbeing", "end-to-end solution"],
    },
    "missing_disclosures": {
        "description": "Material information that should be present but is absent",
        "signal": "NEGATIVE — what they DON'T say matters more than what they do",
        "examples": ["No EBITDA", "No margin data", "No synergy targets", "No integration cost estimates"],
    },
}

# Regex-based detectors
HARD_NUMBER_PATTERN = re.compile(r'\$[\d,.]+\s*(million|billion|M|B|mn|bn)', re.IGNORECASE)
PERCENTAGE_PATTERN = re.compile(r'\d+(\.\d+)?%')
SOFT_QUALIFIER = re.compile(r'\b(more than|approximately|about|roughly|nearly|around|over|up to|at least)\b', re.IGNORECASE)
HEDGE_WORDS = re.compile(r'\b(believe|expect|anticipate|may|could|should|potential|likely|possible|intend|plan to|aim to|seek to|hope to|aspire)\b', re.IGNORECASE)
ASPIRATIONAL = re.compile(r'\b(will unlock|will create|will enable|opportunity to|vision|transform|pivotal moment|milestone|profound|reshape|revolutionary|game-changing|unprecedented|global destination)\b', re.IGNORECASE)
BUZZWORDS = re.compile(r'\b(AI-driven|AI-enabled|AI-powered|ecosystem|platform|end-to-end|global scale|network effects|synergies|wellbeing|wellness|innovation leader|infrastructure|personalized|hyper-personalized|smart|connected|digital transformation)\b', re.IGNORECASE)


@dataclass
class WordingAnalysis:
    deal_name: str
    quotes: list
    hard_number_count: int = 0
    soft_number_count: int = 0
    hedge_word_count: int = 0
    aspirational_count: int = 0
    buzzword_count: int = 0
    total_word_count: int = 0
    hard_numbers_found: list = field(default_factory=list)
    hedge_words_found: list = field(default_factory=list)
    aspirational_found: list = field(default_factory=list)
    buzzwords_found: list = field(default_factory=list)
    missing_disclosures: list = field(default_factory=list)

    @property
    def quantification_ratio(self) -> float:
        """Hard numbers per 100 words — higher = more concrete."""
        if self.total_word_count == 0:
            return 0
        return (self.hard_number_count / self.total_word_count) * 100

    @property
    def hedge_ratio(self) -> float:
        """Hedge words per 100 words — higher = more hedging."""
        if self.total_word_count == 0:
            return 0
        return (self.hedge_word_count / self.total_word_count) * 100

    @property
    def buzzword_ratio(self) -> float:
        """Buzzwords per 100 words — higher = more fluff."""
        if self.total_word_count == 0:
            return 0
        return (self.buzzword_count / self.total_word_count) * 100

    @property
    def substance_score(self) -> float:
        """
        Composite score: higher = more substantive disclosure.
        Formula: (hard_numbers * 3 + soft_numbers * 1) / (hedge_words + aspirational + buzzwords + 1)
        Scale is arbitrary but comparable between deals.
        """
        numerator = (self.hard_number_count * 3) + (self.soft_number_count * 1)
        denominator = self.hedge_word_count + self.aspirational_count + self.buzzword_count + 1
        return numerator / denominator


def analyze_wording(deal_name: str, quotes: list) -> WordingAnalysis:
    """Run pattern analysis across all quotes for a deal."""
    analysis = WordingAnalysis(deal_name=deal_name, quotes=quotes)

    all_text = " ".join(q["text"] for q in quotes)
    analysis.total_word_count = len(all_text.split())

    for q in quotes:
        text = q["text"]

        # Hard numbers
        hard = HARD_NUMBER_PATTERN.findall(text)
        pcts = PERCENTAGE_PATTERN.findall(text)
        analysis.hard_number_count += len(hard) + len(pcts)
        for h in hard:
            analysis.hard_numbers_found.append(f"${h[0] if isinstance(h, tuple) else h}")

        # Soft qualifiers
        soft = SOFT_QUALIFIER.findall(text)
        analysis.soft_number_count += len(soft)

        # Hedge words
        hedges = HEDGE_WORDS.findall(text)
        analysis.hedge_word_count += len(hedges)
        analysis.hedge_words_found.extend(hedges)

        # Aspirational language
        asp = ASPIRATIONAL.findall(text)
        analysis.aspirational_count += len(asp)
        analysis.aspirational_found.extend(asp)

        # Buzzwords
        buzz = BUZZWORDS.findall(text)
        analysis.buzzword_count += len(buzz)
        analysis.buzzwords_found.extend(buzz)

    return analysis


def build_word_frequencies(quotes: list) -> dict:
    """
    Count word frequencies across all quotes using a plain dictionary.
    Strips punctuation, lowercases, and skips common stop words so the
    results reflect meaningful financial/deal vocabulary.
    """
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "their", "our", "its",
        "this", "that", "these", "those", "while", "into", "through", "about",
        "more", "than", "both", "we", "they", "it", "all", "not", "no",
        "s", "us",
    }

    freq: dict = {}
    all_text = " ".join(q["text"] for q in quotes)

    for raw_word in all_text.split():
        word = re.sub(r"[^a-zA-Z']", "", raw_word).lower().strip("'")
        if len(word) < 3 or word in STOP_WORDS:
            continue
        freq[word] = freq.get(word, 0) + 1

    return freq


def word_freq_stats(deal_name: str, quotes: list) -> None:
    """Print word frequency stats: total words, unique words, top-10 with bar chart."""
    freq = build_word_frequencies(quotes)

    all_text = " ".join(q["text"] for q in quotes)
    total_words = len(all_text.split())
    unique_words = len(freq)

    top10 = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    max_count = top10[0][1] if top10 else 1

    print("  " + bold(cyan(deal_name)) + dim("  |  ") +
          "Total words: " + yellow(str(total_words)) +
          dim("  |  ") + "Unique (filtered): " + yellow(str(unique_words)))
    print()

    headers = ["Rank", "Word", "Count", "% of Total", "Frequency Bar (normalized)"]
    col_widths = [4, 22, 5, 10, 32]
    rows = []
    for rank, (word, count) in enumerate(top10, 1):
        pct = (count / total_words) * 100
        bar = draw_bar(count, max_count, bar_width=30)
        rows.append((str(rank), word, str(count), f"{pct:.1f}%", bar))

    draw_table(headers, rows, col_widths)
    print()


def identify_missing_disclosures(deal_name: str, has_ebitda: bool, has_margin: bool,
                                  has_synergy_targets: bool, has_integration_costs: bool,
                                  has_accretion: bool, has_timeline: bool,
                                  has_net_income: bool) -> list:
    """Flag what SHOULD be in a deal announcement but isn't."""
    missing = []
    if not has_ebitda:
        missing.append("EBITDA / profitability figures — cannot assess deal value vs. earnings")
    if not has_margin:
        missing.append("Margin data — cannot assess business quality")
    if not has_synergy_targets:
        missing.append("Quantified synergy targets — deal premium is unverifiable")
    if not has_integration_costs:
        missing.append("Integration cost estimates — total cost of deal ownership unknown")
    if not has_accretion:
        missing.append("EPS / earnings accretion analysis — no shareholder value math")
    if not has_timeline:
        missing.append("Synergy realization timeline — no accountability dates")
    if not has_net_income:
        missing.append("Net income — actual bottom-line profitability unknown")
    return missing


# =============================================================================
# PRINTING HELPERS
# =============================================================================

WIDTH = 90  # overall output width


def print_sep(char="=", w=WIDTH):
    print(dim(char * w))


def print_hdr(title):
    """Cyan boxed section header."""
    print()
    print(cyan("+" + "-" * (WIDTH - 2) + "+"))
    print(cyan("|") + bold(cyan(f"  {title}".ljust(WIDTH - 2))) + cyan("|"))
    print(cyan("+" + "=" * (WIDTH - 2) + "+"))
    print()


def draw_table(headers: list, rows: list, col_widths: list = None):
    """
    Print a color-aware bordered ASCII table.

    headers   : list of column header strings (may contain ANSI codes)
    rows      : list of row tuples (each element is a string, may contain ANSI codes)
    col_widths: optional list of visible widths; auto-sized from stripped text if omitted
    """
    if col_widths is None:
        all_rows = [headers] + list(rows)
        col_widths = [
            max(len(strip_ansi(str(r[i]))) for r in all_rows)
            for i in range(len(headers))
        ]

    border_line = dim("+" + "+".join("-" * (w + 2) for w in col_widths) + "+")
    header_sep  = dim("+" + "+".join("=" * (w + 2) for w in col_widths) + "+")

    def data_row(cells, color_fn=None):
        parts = []
        for cell, w in zip(cells, col_widths):
            s = str(cell)
            if color_fn:
                s = color_fn(strip_ansi(s))
            parts.append(" " + cpad(s, w) + " ")
        return dim("|") + dim("|").join(parts) + dim("|")

    print(border_line)
    print(data_row(headers, color_fn=lambda t: bold(white(t))))
    print(header_sep)
    for i, row in enumerate(rows):
        print(data_row(row))
        if i < len(rows) - 1:
            print(border_line)
    print(border_line)
    print()


def draw_bar(value: int, max_value: int, bar_width: int = 30) -> str:
    """Return a normalized, colored ASCII bar scaled to bar_width."""
    if max_value == 0:
        return ""
    filled = round((value / max_value) * bar_width)
    bar = green("#" * filled) + dim("." * (bar_width - filled))
    return dim("[") + bar + dim("]")


# =============================================================================
# SECTION FUNCTIONS
# =============================================================================

def _signal_color(signal: str) -> str:
    """Color a signal string based on its polarity keyword."""
    if "POSITIVE" in signal:
        return green(signal)
    if "NEGATIVE" in signal:
        return red(signal)
    return yellow(signal)  # NEUTRAL


def print_methodology():
    """Section 1: Explain what each language pattern signals about deal quality."""
    print_hdr("METHODOLOGY: HOW FINANCIAL WORDING ANALYSIS WORKS")
    print("  Deal announcements are not neutral documents. They are crafted by")
    print("  investment bankers, lawyers, and PR teams to control narrative.")
    print("  The language encodes signals about deal quality:")
    print()
    for cat, info in PATTERNS.items():
        print("  " + bold(cyan(f"[{cat.upper()}]")))
        print(f"    What:    {info['description']}")
        print(f"    Signal:  {_signal_color(info['signal'])}")
        print(f"    Examples: {dim(', '.join(info['examples'][:2]))}")
        print()
    print("  " + bold("The key insight:") + " WHAT IS ABSENT tells you more than what is present.")
    print("  A deal that discloses revenue but not EBITDA is hiding profitability.")
    print("  A deal that cites 'strong profitability' without numbers has no")
    print("  profitability worth disclosing.")
    print()


def _better(dt_val, pe_val, higher_is_better: bool = True) -> str:
    """Return a colored verdict string indicating which deal wins the metric."""
    if dt_val == pe_val:
        return dim("tie")
    if higher_is_better:
        return green("DT <--") if dt_val > pe_val else blue("--> PE")
    else:
        return green("DT <--") if dt_val < pe_val else blue("--> PE")


def print_pattern_counts(dt_analysis: WordingAnalysis, pe_analysis: WordingAnalysis):
    """Section 2: Bordered table of raw pattern counts, ratios, and per-metric verdict."""
    print_hdr("PATTERN DETECTION RESULTS")

    headers = ["Metric", "VMG / Downtown", "Playlist / EGYM", "Better"]
    col_widths = [34, 14, 14, 8]

    rows = [
        ("Total words analyzed",
         str(dt_analysis.total_word_count),
         str(pe_analysis.total_word_count), "--"),
        ("Hard numbers ($ or %)",
         str(dt_analysis.hard_number_count),
         str(pe_analysis.hard_number_count),
         _better(dt_analysis.hard_number_count, pe_analysis.hard_number_count)),
        ("Soft qualifiers (more than, about)",
         str(dt_analysis.soft_number_count),
         str(pe_analysis.soft_number_count),
         _better(dt_analysis.soft_number_count, pe_analysis.soft_number_count)),
        ("Hedge words (believe, may, expect)",
         str(dt_analysis.hedge_word_count),
         str(pe_analysis.hedge_word_count),
         _better(dt_analysis.hedge_word_count, pe_analysis.hedge_word_count, higher_is_better=False)),
        ("Aspirational phrases",
         str(dt_analysis.aspirational_count),
         str(pe_analysis.aspirational_count),
         _better(dt_analysis.aspirational_count, pe_analysis.aspirational_count, higher_is_better=False)),
        ("Buzzwords",
         str(dt_analysis.buzzword_count),
         str(pe_analysis.buzzword_count),
         _better(dt_analysis.buzzword_count, pe_analysis.buzzword_count, higher_is_better=False)),
        ("--- ratios (per 100 words) ---", "", "", ""),
        ("Quantification ratio",
         f"{dt_analysis.quantification_ratio:.2f}",
         f"{pe_analysis.quantification_ratio:.2f}",
         _better(dt_analysis.quantification_ratio, pe_analysis.quantification_ratio)),
        ("Hedge ratio",
         f"{dt_analysis.hedge_ratio:.2f}",
         f"{pe_analysis.hedge_ratio:.2f}",
         _better(dt_analysis.hedge_ratio, pe_analysis.hedge_ratio, higher_is_better=False)),
        ("Buzzword ratio",
         f"{dt_analysis.buzzword_ratio:.2f}",
         f"{pe_analysis.buzzword_ratio:.2f}",
         _better(dt_analysis.buzzword_ratio, pe_analysis.buzzword_ratio, higher_is_better=False)),
        ("SUBSTANCE SCORE (higher = better)",
         f"{dt_analysis.substance_score:.2f}",
         f"{pe_analysis.substance_score:.2f}",
         _better(dt_analysis.substance_score, pe_analysis.substance_score)),
    ]

    draw_table(headers, rows, col_widths)


def print_word_frequencies():
    """Section 3: Top-10 most common words and basic stats for each deal's quotes."""
    print_hdr("WORD FREQUENCY ANALYSIS — TOP 10 MOST COMMON WORDS")
    print("  Stop words and punctuation removed. Words reflect deal vocabulary.")
    print()
    word_freq_stats("VMG / Downtown", DOWNTOWN_QUOTES)
    word_freq_stats("Playlist / EGYM", PLAYLIST_EGYM_QUOTES)


def print_detected_pattern_detail(dt_analysis: WordingAnalysis, pe_analysis: WordingAnalysis):
    """Section 4: Tabular breakdown of every matched token per deal."""
    print_hdr("DETECTED PATTERNS — DETAIL")

    for a, label in [(dt_analysis, "VMG / Downtown"), (pe_analysis, "Playlist / EGYM")]:
        print("  " + bold(cyan(label)))
        print()

        hard = ", ".join(sorted(set(str(x) for x in a.hard_numbers_found))) or "NONE"
        hedge_counts = Counter(w.lower() for w in a.hedge_words_found)
        hedges = ", ".join(f"{w}({n})" for w, n in sorted(hedge_counts.items())) or "NONE"
        asp = ", ".join(sorted(set(a.aspirational_found))) or "NONE"
        buzz_counts = Counter(w.lower() for w in a.buzzwords_found)
        buzzwords = ", ".join(f"{w}({n})" for w, n in sorted(buzz_counts.items())) or "NONE"

        headers = ["Category", "Tokens Found"]
        col_widths = [22, 58]
        rows = [
            ("Hard numbers", hard),
            ("Hedge words", hedges),
            ("Aspirational", asp),
            ("Buzzwords", buzzwords),
        ]
        draw_table(headers, rows, col_widths)


def print_missing_disclosures(dt_analysis: WordingAnalysis, pe_analysis: WordingAnalysis):
    """Section 5: Side-by-side table of present vs. absent disclosures for each deal."""
    print_hdr("MISSING DISCLOSURES  (present = [YES]  /  absent = [NO])")

    disclosure_labels = [
        ("EBITDA / profitability figures",  "has_ebitda"),
        ("Margin data",                     "has_margin"),
        ("Quantified synergy targets",      "has_synergy_targets"),
        ("Integration cost estimates",      "has_integration_costs"),
        ("EPS / accretion analysis",        "has_accretion"),
        ("Synergy realization timeline",    "has_timeline"),
        ("Net income",                      "has_net_income"),
    ]

    # Reconstruct presence from missing_disclosures text (absent = appears in list)
    dt_missing_text = " ".join(dt_analysis.missing_disclosures).lower()
    pe_missing_text = " ".join(pe_analysis.missing_disclosures).lower()

    keyword_map = {
        "has_ebitda":             "ebitda",
        "has_margin":             "margin data",
        "has_synergy_targets":    "synergy targets",
        "has_integration_costs":  "integration cost",
        "has_accretion":          "accretion",
        "has_timeline":           "timeline",
        "has_net_income":         "net income",
    }

    headers = ["Disclosure", "VMG / Downtown", "Playlist / EGYM"]
    col_widths = [34, 14, 14]
    rows = []
    for label, key in disclosure_labels:
        kw = keyword_map[key]
        dt_val = red("[NO]  ") if kw in dt_missing_text else green("[YES]")
        pe_val = red("[NO]  ") if kw in pe_missing_text else green("[YES]")
        rows.append((label, dt_val, pe_val))

    draw_table(headers, rows, col_widths)

    dt_gaps = len(dt_analysis.missing_disclosures)
    pe_gaps = len(pe_analysis.missing_disclosures)
    print("  VMG / Downtown:  " + yellow(f"{dt_gaps} / 7") + " disclosures missing")
    print("  Playlist / EGYM: " + red(f"{pe_gaps} / 7") + " disclosures missing")
    print()


def _flag(quote: str, issue: str):
    """Print a single red-flag entry: yellow quote, red ISSUE label, plain explanation."""
    print("  " + yellow(f'"{quote}"'))
    lines = issue.split("\n")
    print("     " + red("ISSUE:") + " " + lines[0])
    for line in lines[1:]:
        print("     " + line)
    print()


def print_wording_red_flags():
    """Section 6: Specific quotes from each deal with explanation of why they are red flags."""
    print_hdr("SPECIFIC WORDING RED FLAGS")

    print("  " + bold(cyan("[VMG / Downtown]")))
    print()
    _flag(
        "significant milestone in the creation of a global, end-to-end solution",
        "'Milestone' and 'end-to-end solution' are marketing language.\n"
        "     They describe nothing specific about value creation or financial impact.",
    )
    _flag(
        "preserving their distinct strengths while increasing investment",
        "Contradicts typical acquisition integration. If you're preserving\n"
        "     everything distinct, where do cost synergies come from? This signals\n"
        "     the deal is about revenue growth, not cost efficiency — but no revenue\n"
        "     targets are given.",
    )
    _flag(
        "thoughtfully and strategically",
        "Filler phrase. Every deal claims to be thoughtful and strategic.\n"
        "     Tells you nothing about the actual integration plan, timeline, or KPIs.",
    )
    _flag(
        "The EBITDA figure ($40M) comes from Billboard, NOT from the companies.",
        "The acquirer chose not to disclose any financial metrics about\n"
        "     the target. When the buyer won't tell you the economics, the economics\n"
        "     probably don't support the price.",
    )

    print("  " + bold(cyan("[Playlist / EGYM]")))
    print()
    _flag(
        "more than $800 million in net revenue ... and strong profitability",
        "This is the ENTIRE financial disclosure for a $7.5B deal.\n"
        "     'More than' is deliberately vague — could be $801M or $950M.\n"
        "     'Strong profitability' with no number is meaningless.",
    )
    _flag(
        "will unlock network effects across studios, employers, and consumers",
        "'Unlock network effects' is a hypothesis, not a plan. Network\n"
        "     effects require specific conditions. None are specified here.",
    )
    _flag(
        "a global destination for wellbeing",
        "This is a tagline, not a strategy. It describes no specific\n"
        "     product, market, or financial outcome. It cannot be verified.",
    )
    _flag(
        "increased investment in artificial intelligence",
        "AI is mentioned 4+ times with zero specifics about what it does,\n"
        "     what it costs, or what return it generates.",
    )
    _flag(
        "Seven years under Vista ownership with no exit.",
        "Vista took Mindbody private in 2019. It is now 2026.\n"
        "     This merger brings in fresh equity to reset the valuation rather\n"
        "     than pursue a clean exit — suggesting a liquidity event was needed.",
    )


def print_comparative_assessment():
    """Section 7: Which deal has better disclosure and language quality, and what it implies."""
    print_hdr("COMPARATIVE ASSESSMENT")

    print("  DISCLOSURE QUALITY:")
    print()
    print("  Downtown is marginally better. It has leaked financials ($40M EBITDA,")
    print("  $130M net revenue, $900M gross) — even though these came from Billboard")
    print("  sources rather than the company itself. You can at least compute a")
    print("  multiple (19.4x) and decide if it's reasonable.")
    print()
    print("  Playlist/EGYM is worse. A $7.5B combined valuation with exactly one")
    print("  financial data point ('>$800M net revenue') and the phrase 'strong")
    print("  profitability' is insufficient for any serious analysis. You cannot")
    print("  compute EV/EBITDA, you cannot assess margins, you cannot model returns.")
    print("  You are being asked to accept a valuation on faith.")
    print()
    print("  LANGUAGE QUALITY:")
    print()
    print("  Both deals rely heavily on aspirational and buzzword-laden language.")
    print("  Playlist/EGYM is worse: higher buzzword density, more aspirational")
    print("  phrasing, and the 'AI' keyword appears repeatedly without substance.")
    print("  Downtown's language is generic but at least shorter and less inflated.")
    print()
    print("  WHAT THE WORDING TELLS YOU ABOUT DEAL QUALITY:")
    print()
    print("  The fundamental rule of deal wording analysis is:")
    print("    - If the numbers are good, they will show you the numbers.")
    print("    - If the numbers are absent, the numbers are not good.")
    print()
    print("  Downtown's $775M for $40M EBITDA (19.4x) is expensive, and UMG/VMG")
    print("  apparently knew it — they disclosed nothing and let Billboard do it.")
    print()
    print("  Playlist/EGYM's $7.5B for '>$800M revenue' and 'strong profitability'")
    print("  is unverifiable. The absence of any earnings metric in a deal this")
    print("  size is not an oversight. It is a choice. That choice tells you")
    print("  the profitability number does not support a 9.4x revenue multiple")
    print("  under normal scrutiny.")
    print()


def print_reading_framework():
    """Section 8: General rules for reading any M&A deal announcement critically."""
    print_hdr("GENERAL FRAMEWORK: HOW TO READ DEAL LANGUAGE")

    print("  1. COUNT THE NUMBERS")
    print("     A well-structured deal announcement for a $1B+ transaction should")
    print("     contain at minimum: deal value, revenue, EBITDA or net income,")
    print("     synergy targets (with timeline), integration costs, and")
    print("     accretion/dilution analysis. If any of these are missing, ask why.")
    print()
    print("  2. WATCH FOR QUALIFIERS")
    print("     'More than' and 'approximately' are not the same as exact figures.")
    print("     'Expected to' and 'we believe' are not commitments. Any claim")
    print("     preceded by a hedge word should be treated as aspirational until")
    print("     verified by filing data.")
    print()
    print("  3. MEASURE BUZZWORD DENSITY")
    print("     If a press release mentions 'AI', 'platform', 'ecosystem', or")
    print("     'global scale' more than it mentions actual financial metrics,")
    print("     the deal is being sold on narrative, not fundamentals.")
    print()
    print("  4. CHECK WHAT'S MISSING")
    print("     The most important analysis is negative: what SHOULD be disclosed")
    print("     but isn't? Missing EBITDA means hidden profitability. Missing")
    print("     synergy targets mean unverifiable deal premium. Missing integration")
    print("     costs mean understated total cost of ownership.")
    print()
    print("  5. COMPARE EXECUTIVE QUOTES TO FILINGS")
    print("     CEOs say 'transformative.' Proxy statements say 'subject to risk.'")
    print("     The legal documents tell the real story. Always read the proxy,")
    print("     the fairness opinion, and the risk factors — not the press release.")
    print()
    print("  6. FOLLOW THE STRUCTURE")
    print("     Cash deals signal buyer confidence. Stock deals signal the buyer")
    print("     thinks their stock is overvalued. New equity injections in a")
    print("     merger (like Playlist/EGYM) signal existing investors need a")
    print("     valuation reset. The consideration structure IS the signal.")
    print()


# =============================================================================
# DATA PREPARATION
# =============================================================================

def build_analyses() -> tuple:
    """Run pattern detection and flag missing disclosures for both deals."""
    dt_analysis = analyze_wording("VMG / Downtown", DOWNTOWN_QUOTES)
    pe_analysis = analyze_wording("Playlist / EGYM", PLAYLIST_EGYM_QUOTES)

    dt_analysis.missing_disclosures = identify_missing_disclosures(
        "VMG / Downtown",
        has_ebitda=True,            # ~$40M from Billboard (anonymous, unverified)
        has_margin=True,            # Derivable: 30.8% on net rev
        has_synergy_targets=False,
        has_integration_costs=False,
        has_accretion=False,
        has_timeline=False,
        has_net_income=False,
    )

    pe_analysis.missing_disclosures = identify_missing_disclosures(
        "Playlist / EGYM",
        has_ebitda=False,
        has_margin=False,
        has_synergy_targets=False,
        has_integration_costs=False,
        has_accretion=False,
        has_timeline=False,
        has_net_income=False,
    )

    return dt_analysis, pe_analysis


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def print_scorecard(dt_analysis: WordingAnalysis, pe_analysis: WordingAnalysis):
    """Visual summary scorecard shown at the top of the report."""
    print_hdr("DISCLOSURE SCORECARD  (quick summary)")
    headers = ["Metric", "VMG / Downtown", "Playlist / EGYM", "Winner"]
    col_widths = [30, 14, 14, 14]
    rows = [
        ("Substance Score",
         f"{dt_analysis.substance_score:.2f}",
         f"{pe_analysis.substance_score:.2f}",
         _better(dt_analysis.substance_score, pe_analysis.substance_score)),
        ("Hard Numbers",
         str(dt_analysis.hard_number_count),
         str(pe_analysis.hard_number_count),
         _better(dt_analysis.hard_number_count, pe_analysis.hard_number_count)),
        ("Buzzwords (fewer = better)",
         str(dt_analysis.buzzword_count),
         str(pe_analysis.buzzword_count),
         _better(dt_analysis.buzzword_count, pe_analysis.buzzword_count, higher_is_better=False)),
        ("Hedge Words (fewer = better)",
         str(dt_analysis.hedge_word_count),
         str(pe_analysis.hedge_word_count),
         _better(dt_analysis.hedge_word_count, pe_analysis.hedge_word_count, higher_is_better=False)),
        ("Missing Disclosures (fewer = better)",
         str(len(dt_analysis.missing_disclosures)),
         str(len(pe_analysis.missing_disclosures)),
         _better(len(dt_analysis.missing_disclosures), len(pe_analysis.missing_disclosures), higher_is_better=False)),
    ]
    draw_table(headers, rows, col_widths)


def run_analysis():
    """Run all analysis sections in order."""
    print()
    print_sep()
    print("  " + bold(cyan("FINANCIAL DEAL WORDING ANALYZER")))
    print("  " + white("Comparing disclosure quality and language patterns"))
    print("  " + yellow("VMG / Downtown Music") + dim("  vs.  ") + blue("Playlist + EGYM"))
    print_sep()

    dt_analysis, pe_analysis = build_analyses()

    print_scorecard(dt_analysis, pe_analysis)
    print_methodology()
    print_pattern_counts(dt_analysis, pe_analysis)
    print_word_frequencies()
    print_detected_pattern_detail(dt_analysis, pe_analysis)
    print_missing_disclosures(dt_analysis, pe_analysis)
    print_wording_red_flags()
    print_comparative_assessment()
    print_reading_framework()

    print_sep()
    print("  END OF WORDING ANALYSIS")
    print_sep()


if __name__ == "__main__":
    run_analysis()