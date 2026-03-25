#!/usr/bin/env python3
"""
Deal Document Disclosure Analyzer
===================================
Maps the complete hierarchy of M&A deal documents, identifies where
disclosures live within that hierarchy, and scores disclosure completeness
for each deal against what is legally and practically expected.

Key insight: Disclosures are NOT a single section. They are spread across
multiple documents at multiple levels, each with different legal weight,
audience, and enforceability.

Deals analyzed:
  1. VMG / Downtown Music Holdings ($775M) — private-to-private
  2. Playlist + EGYM Merger ($7.5B EV) — private-to-private

Sources cited inline.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# =============================================================================
# DEAL DOCUMENT HIERARCHY
# =============================================================================
# This is the standard structure. Not every deal produces every document.
# Private deals produce far fewer public documents than public deals.

class DocStatus(Enum):
    FILED = "FILED"              # Document exists and is publicly available
    PARTIAL = "PARTIAL"          # Document exists but with limited disclosure
    NOT_REQUIRED = "NOT_REQUIRED"  # Not legally required for this deal type
    NOT_FILED = "NOT_FILED"      # Should exist but isn't public
    UNKNOWN = "UNKNOWN"          # Can't determine


@dataclass
class DisclosureItem:
    """A specific piece of information that should be disclosed."""
    name: str
    description: str
    legal_basis: str          # Which law/rule requires it
    typical_location: str     # Where in the document hierarchy it lives
    status: DocStatus
    what_was_disclosed: str   # What the deal actually said
    what_is_missing: str      # What should be there but isn't
    legal_significance: str   # Why this matters legally
    source_url: str = ""


@dataclass
class DealDocument:
    """A document in the deal hierarchy."""
    name: str
    sec_form: str             # e.g., "8-K", "DEFM14A", "S-4", "Form 425"
    description: str
    legal_requirement: str    # When this document is required
    audience: str             # Who this is written for
    legal_weight: str         # How much liability attaches
    status: DocStatus
    note: str = ""
    source_url: str = ""


@dataclass
class DealDocumentAnalysis:
    """Complete disclosure analysis for one deal."""
    deal_name: str
    deal_type: str            # "public-public", "private-private", "public-private"
    documents: list           # List of DealDocument
    disclosures: list         # List of DisclosureItem
    disclosure_score: float = 0.0  # 0-100


# =============================================================================
# THE STANDARD DOCUMENT HIERARCHY
# (What a fully-disclosed public M&A deal looks like)
# =============================================================================

STANDARD_HIERARCHY = """
DEAL DOCUMENT HIERARCHY (Public M&A — Full Disclosure)
=======================================================

TIER 1: ANNOUNCEMENT DOCUMENTS (Days 0-4)
  |
  +-- Press Release
  |     Audience: Public, media, investors
  |     Legal weight: LOW (not an SEC filing, but statements of fact are actionable)
  |     Contains: Deal value, consideration, strategic rationale, executive quotes
  |     Source: https://www.lexology.com/library/detail.aspx?g=53d64d2f-6564-4300-a096-693160776bef
  |
  +-- Form 8-K (Current Report)
  |     Audience: SEC, investors
  |     Legal weight: HIGH (SEC filing, subject to Sarbanes-Oxley certifications)
  |     Contains: Material definitive agreement, merger agreement as exhibit
  |     Must be filed within 4 business days
  |     Source: https://www.secfilingdata.com/mergers-acquisitions-what-to-look-for-in-the-sec-filings/
  |
  +-- Form 425 (Communications re: Business Combination)
        Audience: SEC, investors
        Legal weight: MEDIUM (filed to comply with proxy solicitation rules)
        Contains: Any written communications about the deal before proxy is filed

TIER 2: PROXY / REGISTRATION (Weeks 2-12)
  |
  +-- PREM14A (Preliminary Proxy Statement)
  |     Audience: SEC review (not distributed to shareholders)
  |     Legal weight: HIGH (SEC reviews and issues comment letters)
  |     Contains: Draft of all merger disclosures
  |
  +-- DEFM14A (Definitive Merger Proxy Statement)
  |     Audience: Shareholders who must vote
  |     Legal weight: HIGHEST (fiduciary duty of candor applies)
  |     Contains:
  |       - Background of the Merger (full narrative of negotiations)
  |       - Reasons for the Merger (board's rationale)
  |       - Recommendation of the Board
  |       - Opinion of Financial Advisor (fairness opinion)
  |       - Financial Projections (management's forward-looking estimates)
  |       - Interests of Directors and Officers (conflicts disclosure)
  |       - Material Tax Consequences
  |       - Appraisal Rights
  |       - The Merger Agreement (full text as exhibit)
  |       - Disclosure Schedules (list of exceptions to reps & warranties)
  |     Source: https://www.lexology.com/library/detail.aspx?g=a1937255-5c68-44c5-b97f-51810cf04de7
  |
  +-- Form S-4 (Registration Statement for new securities)
        Only if stock consideration is used
        Contains: Same as DEFM14A plus registration of new shares

TIER 3: MERGER AGREEMENT (The actual contract)
  |
  +-- Agreement and Plan of Merger
  |     Legal weight: HIGHEST (binding contract)
  |     Contains:
  |       - Representations & Warranties (factual statements by each party)
  |       - Covenants (promises about conduct between signing and closing)
  |       - Conditions to Closing
  |       - Termination provisions and breakup fees
  |       - Indemnification
  |
  +-- Disclosure Schedules (confidential, usually not filed publicly)
        Legal weight: HIGHEST (exceptions to reps & warranties)
        Contains:
          - Known liabilities, litigation, contracts, environmental issues
          - Material exceptions to every representation made
          - This is where the bodies are buried
        Source: https://www.sec.gov/Archives/edgar/data/0000732717/000095012305006178/y04651a2exv2w2.htm

TIER 4: POST-CLOSING
  |
  +-- Form 8-K (Closing announcement)
  +-- Pro forma financial statements (if material acquisition for public buyer)
  +-- Goodwill and purchase price allocation (in subsequent 10-K/10-Q)
"""


# =============================================================================
# DEAL-SPECIFIC ANALYSIS
# =============================================================================

def build_downtown_analysis() -> DealDocumentAnalysis:
    """Analyze VMG / Downtown Music disclosure completeness."""

    documents = [
        DealDocument(
            name="Press Release (Completion)",
            sec_form="N/A (wire service)",
            description="Announcement of deal completion",
            legal_requirement="Voluntary for private deals",
            audience="Public, media, industry",
            legal_weight="LOW — not an SEC filing, but statements of present fact are actionable under common law",
            status=DocStatus.FILED,
            source_url="https://www.prnewswire.com/news-releases/virgin-music-group-completes-acquisition-of-downtown-302693634.html",
        ),
        DealDocument(
            name="Form 8-K (Deal Announcement by UMG parent Alphabet/Vivendi)",
            sec_form="8-K",
            description="Current report disclosing material event",
            legal_requirement="Required if material to UMG's public parent. UMG trades on Euronext Amsterdam.",
            audience="UMG shareholders, Euronext regulators",
            legal_weight="HIGH — subject to EU Market Abuse Regulation and Euronext rules",
            status=DocStatus.UNKNOWN,
            note="UMG is listed on Euronext Amsterdam. EU disclosure rules (MAR) apply, not SEC rules. "
                 "UMG likely disclosed this in a press release under MAR but the $775M may not be "
                 "material relative to UMG's ~€40B market cap.",
        ),
        DealDocument(
            name="Merger Agreement",
            sec_form="N/A (private)",
            description="The actual binding contract between VMG and Downtown",
            legal_requirement="Always exists but not publicly filed for private-to-private deals",
            audience="The parties and their counsel only",
            legal_weight="HIGHEST — binding contract, but not public",
            status=DocStatus.NOT_FILED,
            note="Private deal. The merger agreement, reps & warranties, disclosure schedules, "
                 "and all financial details are confidential between VMG/UMG, Downtown, and their investors.",
        ),
        DealDocument(
            name="Proxy Statement / Shareholder Vote",
            sec_form="DEFM14A",
            description="Detailed disclosure for shareholder approval",
            legal_requirement="Required only if public company shareholders must vote",
            audience="Shareholders",
            legal_weight="HIGHEST — fiduciary duty of candor",
            status=DocStatus.NOT_REQUIRED,
            note="Neither party is a U.S. public company requiring a shareholder vote on this deal. "
                 "UMG shareholders did not vote on this acquisition. No proxy was filed.",
        ),
        DealDocument(
            name="EU Regulatory Filing (European Commission)",
            sec_form="EC Merger Review",
            description="Antitrust review under EU Merger Regulation",
            legal_requirement="Required — exceeded EU merger thresholds",
            audience="European Commission, public (redacted decisions published)",
            legal_weight="HIGH — EC approval was a condition to closing",
            status=DocStatus.FILED,
            note="EC approved Feb 13, 2026 on condition of Curve divestiture. "
                 "Full decision text typically published 6-12 months after clearance (redacted).",
            source_url="https://imusician.pro/en/resources/blog/virgin-music-completes-downtown-acquisition",
        ),
    ]

    disclosures = [
        DisclosureItem(
            name="Deal Value",
            description="Total consideration paid",
            legal_basis="Material event disclosure (MAR for EU-listed UMG)",
            typical_location="Press release, 8-K, merger agreement",
            status=DocStatus.FILED,
            what_was_disclosed="$775 million, all-cash",
            what_is_missing="Nothing — deal value clearly stated",
            legal_significance="Adequate. Clear, specific, verifiable.",
            source_url="https://www.prnewswire.com/news-releases/virgin-music-group-completes-acquisition-of-downtown-302693634.html",
        ),
        DisclosureItem(
            name="Target Revenue",
            description="Downtown's annual revenue (gross and net)",
            legal_basis="No specific requirement for private target in private deal",
            typical_location="Proxy statement (if public), or fairness opinion",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="NOT disclosed by VMG/UMG. Billboard reported ~$900M gross / $130M net from anonymous sources.",
            what_is_missing="Official revenue figures from the parties. Agency vs. principal accounting distinction not explained.",
            legal_significance="LOW legal risk (private deal, no shareholder vote). HIGH analytical risk — "
                              "investors in UMG stock cannot verify the price paid relative to revenue.",
            source_url="https://www.billboard.com/pro/downtown-music-holdings-sale-board-exploring/",
        ),
        DisclosureItem(
            name="Target EBITDA / Profitability",
            description="Downtown's earnings before interest, taxes, depreciation, amortization",
            legal_basis="No specific requirement for private target",
            typical_location="Proxy statement, fairness opinion, merger agreement schedules",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="NOT disclosed by VMG/UMG. Billboard reported ~$40M EBITDA from anonymous sources.",
            what_is_missing="Official EBITDA, net income, margin data. EBITDA definition (reported vs. adjusted) unknown.",
            legal_significance="LOW legal risk (private deal). HIGH valuation risk — 19.4x implied EBITDA is "
                              "not verifiable from any official source.",
            source_url="https://www.billboard.com/pro/downtown-music-holdings-sale-board-exploring/",
        ),
        DisclosureItem(
            name="Synergy Targets",
            description="Quantified cost and/or revenue synergy expectations",
            legal_basis="Not legally required; common in public deals for shareholder context",
            typical_location="Proxy statement 'Reasons for the Merger' section, investor presentation",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="Qualitative only: 'enhances choice, service and global reach'",
            what_is_missing="Dollar value of expected synergies, timeline, cost to achieve",
            legal_significance="No legal requirement in private deal. Analytically, this means the deal "
                              "premium is entirely unverifiable.",
        ),
        DisclosureItem(
            name="Integration Costs",
            description="Expected restructuring, severance, systems migration costs",
            legal_basis="Not required pre-closing; UMG would disclose in future financial statements under IFRS",
            typical_location="Proxy statement, post-closing 10-K footnotes",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="Nothing. EU-mandated Curve divestiture is an implicit cost but not quantified.",
            what_is_missing="Total integration budget, timeline, Curve divestiture costs",
            legal_significance="UMG will need to disclose acquisition-related costs in its IFRS financial "
                              "statements. These will appear in future annual reports.",
        ),
        DisclosureItem(
            name="Fairness Opinion",
            description="Independent financial advisor's opinion on price fairness",
            legal_basis="Required in proxy for public shareholder vote; not required in private deals",
            typical_location="Proxy statement, as exhibit or summarized in body",
            status=DocStatus.NOT_REQUIRED,
            what_was_disclosed="Not applicable — no shareholder vote solicited",
            what_is_missing="N/A",
            legal_significance="No fairness opinion is required. Downtown's investors and board accepted "
                              "the price through their own process.",
        ),
        DisclosureItem(
            name="Risk Factors",
            description="Material risks related to the transaction",
            legal_basis="Required in proxy/S-4 for public deals; not required for private deals",
            typical_location="Proxy statement, S-4, or 10-K risk factors section",
            status=DocStatus.NOT_REQUIRED,
            what_was_disclosed="The press release contains no risk factors. UMG's future annual report "
                              "may include acquisition-related risks.",
            what_is_missing="Deal-specific risks: client attrition, integration, competitive response",
            legal_significance="UMG has a duty to update risk factors in its Euronext-listed annual report "
                              "if this acquisition creates material new risks.",
        ),
        DisclosureItem(
            name="Forward-Looking Statement Disclaimer",
            description="Safe harbor language protecting projections and estimates",
            legal_basis="PSLRA (U.S.), MAR (EU) for forward-looking statements",
            typical_location="Press release footer, SEC filings",
            status=DocStatus.PARTIAL,
            what_was_disclosed="Standard legal disclaimer present in press release",
            what_is_missing="N/A — adequate for the limited forward-looking claims made",
            legal_significance="The press release makes very few forward-looking claims, so the safe "
                              "harbor is largely moot. Most language describes completed actions.",
        ),
    ]

    return DealDocumentAnalysis(
        deal_name="VMG / Downtown Music Holdings",
        deal_type="private-to-private (public parent: UMG on Euronext)",
        documents=documents,
        disclosures=disclosures,
    )


def build_playlist_analysis() -> DealDocumentAnalysis:
    """Analyze Playlist / EGYM disclosure completeness."""

    documents = [
        DealDocument(
            name="Press Release (Merger Announcement)",
            sec_form="N/A (wire service)",
            description="Announcement of merger agreement and new equity investment",
            legal_requirement="Voluntary — both parties are private",
            audience="Public, media, industry, potential customers",
            legal_weight="LOW for SEC purposes. Statements of present fact still actionable under common law. "
                        "If either party later files for IPO, this becomes part of disclosure history.",
            status=DocStatus.FILED,
            source_url="https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        ),
        DealDocument(
            name="Form 8-K / SEC Filing",
            sec_form="8-K",
            description="Current report for material event",
            legal_requirement="Not required — neither party is SEC-reporting",
            audience="N/A",
            legal_weight="N/A",
            status=DocStatus.NOT_REQUIRED,
            note="Playlist (Vista portfolio company) and EGYM (German private) have no SEC reporting obligations. "
                 "Vista's fund-level entity (not Playlist) may have limited reporting, but the portfolio "
                 "company itself does not file with the SEC.",
        ),
        DealDocument(
            name="Merger Agreement",
            sec_form="N/A (private)",
            description="Binding contract for the combination",
            legal_requirement="Exists between the parties but not publicly filed",
            audience="Playlist, EGYM, Vista, Affinity Partners, and their counsel",
            legal_weight="HIGHEST — binding contract, but fully confidential",
            status=DocStatus.NOT_FILED,
            note="The merger agreement, reps & warranties, disclosure schedules, financial projections, "
                 "and valuation models are all confidential. Institutional investors (Affinity, Vista, "
                 "Temasek, L Catterton) negotiated directly with access to data rooms.",
        ),
        DealDocument(
            name="Proxy Statement / Shareholder Vote",
            sec_form="DEFM14A",
            description="Detailed disclosure for shareholder approval",
            legal_requirement="Not required — no public shareholders",
            audience="N/A",
            legal_weight="N/A",
            status=DocStatus.NOT_REQUIRED,
            note="No public shareholders on either side. Investor consent is negotiated privately.",
        ),
        DealDocument(
            name="Regulatory Filing (Antitrust)",
            sec_form="Varies by jurisdiction",
            description="Competition/antitrust review",
            legal_requirement="Subject to customary regulatory approvals per press release",
            audience="Regulators",
            legal_weight="HIGH — closing is conditioned on approval",
            status=DocStatus.UNKNOWN,
            note="Press release states 'subject to customary regulatory approvals.' Jurisdictions not specified. "
                 "Given global operations, HSR (U.S.), EC (EU), and possibly others may apply.",
            source_url="https://www.prnewswire.com/news-releases/playlist-and-egym-announce-agreement-to-merge-and-785-million-in-new-equity-investments-bringing-together-global-leaders-in-fitness-and-wellness-technology-302662191.html",
        ),
    ]

    disclosures = [
        DisclosureItem(
            name="Enterprise Value",
            description="Combined enterprise value of merged entity",
            legal_basis="Voluntary disclosure (private deal)",
            typical_location="Press release",
            status=DocStatus.FILED,
            what_was_disclosed="$7.5 billion combined enterprise value",
            what_is_missing="Breakdown: how much is attributed to Playlist vs. EGYM. "
                           "Munich Startup/Handelsblatt reported EGYM at ~$2.5B, implying Playlist at ~$5.0B.",
            legal_significance="The $7.5B figure is a combined valuation set by the investor consortium, "
                              "not a market-tested price. If Playlist later IPOs, this valuation becomes "
                              "a reference point that SEC examiners will scrutinize.",
            source_url="https://www.munich-startup.de/en/116314/egym-and-playlist-join-forces/",
        ),
        DisclosureItem(
            name="New Equity Investment",
            description="Fresh capital raised as part of the transaction",
            legal_basis="Voluntary disclosure",
            typical_location="Press release",
            status=DocStatus.FILED,
            what_was_disclosed="$785 million in new equity, led by Affinity Partners with Vista, Temasek, L Catterton",
            what_is_missing="Equity split among investors, pre-money vs. post-money valuation, "
                           "dilution to existing shareholders, liquidation preferences, governance rights",
            legal_significance="For a private placement of this size, the terms are negotiated under "
                              "exemptions from SEC registration (Reg D or similar). No public disclosure required.",
        ),
        DisclosureItem(
            name="Combined Revenue",
            description="Annual revenue of combined entity",
            legal_basis="Voluntary (private companies)",
            typical_location="Press release",
            status=DocStatus.PARTIAL,
            what_was_disclosed="'More than $800 million in net revenue' (2025, combined)",
            what_is_missing="Exact figure. Breakdown between Playlist and EGYM. Revenue growth rate. "
                           "Definition of 'net revenue' (does it exclude hardware COGS? ClassPass credits?). "
                           "Historical comparison (2023, 2024).",
            legal_significance="'More than' is deliberately imprecise. If Playlist later IPOs, the SEC "
                              "will require exact, audited figures. This vague disclosure sets no "
                              "verifiable baseline.",
            source_url="https://us.egym.com/en-us/playlist-egym-announce-merger",
        ),
        DisclosureItem(
            name="EBITDA / Profitability",
            description="Earnings metric for valuation assessment",
            legal_basis="None required for private deal",
            typical_location="Proxy statement, fairness opinion (if public deal)",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="'Strong profitability' — two words, no numbers",
            what_is_missing="EBITDA (reported or adjusted), net income, operating margin, free cash flow, "
                           "unit economics by segment (SaaS vs. hardware vs. marketplace vs. corporate wellness)",
            legal_significance="CRITICAL GAP. 'Strong profitability' is an opinion/characterization, not "
                              "a statement of fact. Under Rule 10b-5, opinions can be actionable if the "
                              "speaker doesn't actually hold that opinion or omits facts showing it's misleading "
                              "(Omnicare v. Laborers, 575 U.S. 175 (2015)). However, this is a private deal "
                              "with no securities being publicly traded, so 10b-5 doesn't directly apply. "
                              "If Playlist IPOs, this language becomes discoverable history.",
        ),
        DisclosureItem(
            name="Synergy Targets",
            description="Expected value creation from combination",
            legal_basis="None required",
            typical_location="Proxy 'Reasons for the Merger' section",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="Geographic cross-expansion, AI investment, 'network effects' — all qualitative",
            what_is_missing="Dollar value, timeline, probability-weighted scenarios, cost to achieve",
            legal_significance="No legal requirement. But the absence means the $7.5B valuation "
                              "is supported by zero verifiable financial projections in the public domain.",
        ),
        DisclosureItem(
            name="Integration Plan / Costs",
            description="How the companies will combine operations",
            legal_basis="None required for private deal",
            typical_location="Proxy statement, investor presentation",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="Brands preserved, dual co-founders, EGYM as subsidiary",
            what_is_missing="Technology integration plan, org structure, headcount changes, cost estimates, timeline",
            legal_significance="Four different business models (SaaS, hardware, marketplace, corporate wellness) "
                              "under one roof. Integration complexity is a material risk not addressed.",
        ),
        DisclosureItem(
            name="Financial Projections",
            description="Forward-looking financial estimates used to justify valuation",
            legal_basis="Required in proxy for public deals; not required for private",
            typical_location="Proxy 'Financial Projections' section, fairness opinion inputs",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="Nothing. 'High-growth momentum' is not a projection.",
            what_is_missing="Revenue growth forecast, EBITDA trajectory, capex requirements, working capital needs",
            legal_significance="Institutional investors (Vista, Affinity, Temasek) have these projections — "
                              "they just aren't public. The information asymmetry is by design.",
        ),
        DisclosureItem(
            name="Risk Factors",
            description="Material risks to the transaction and combined business",
            legal_basis="Not required (private deal)",
            typical_location="Proxy statement, S-1 (if IPO follows)",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="'Subject to customary regulatory approvals' — one sentence",
            what_is_missing="Competition risks, integration risks, technology risks, key person risks, "
                           "customer concentration, regulatory risks, macroeconomic sensitivity",
            legal_significance="If Playlist files an S-1 for IPO, ALL of these risks must be disclosed "
                              "retrospectively. The current absence is a deferral, not an exemption.",
        ),
    ]

    return DealDocumentAnalysis(
        deal_name="Playlist + EGYM Merger",
        deal_type="private-to-private (PE-backed: Vista, Affinity, Temasek, L Catterton)",
        documents=documents,
        disclosures=disclosures,
    )


# =============================================================================
# SCORING ENGINE
# =============================================================================

def score_disclosures(analysis: DealDocumentAnalysis) -> float:
    """
    Score disclosure completeness: 0-100.
    
    Scoring:
      FILED = full points
      PARTIAL = half points
      NOT_FILED (but should exist) = 0 points
      NOT_REQUIRED = excluded from denominator
    """
    total_applicable = 0
    points = 0

    for d in analysis.disclosures:
        if d.status == DocStatus.NOT_REQUIRED:
            continue  # Don't penalize for things that aren't required
        total_applicable += 1
        if d.status == DocStatus.FILED:
            points += 1.0
        elif d.status == DocStatus.PARTIAL:
            points += 0.5

    if total_applicable == 0:
        return 0.0
    return (points / total_applicable) * 100


# =============================================================================
# OUTPUT
# =============================================================================

def sep(c="=", w=90):
    print(c * w)


def hdr(title):
    print()
    sep()
    print(f"  {title}")
    sep()
    print()


def run():
    print()
    sep()
    print("  DEAL DOCUMENT DISCLOSURE ANALYZER")
    print("  Where disclosures live in the deal document hierarchy")
    print("  and what's missing from each deal")
    sep()

    # --- Print the standard hierarchy ---
    hdr("STANDARD M&A DOCUMENT HIERARCHY")
    print(STANDARD_HIERARCHY)

    hdr("WHY THIS MATTERS: DISCLOSURES ARE NOT ONE SECTION")
    print("  Disclosures in an M&A deal are distributed across multiple documents,")
    print("  each with different legal weight and audience:")
    print()
    print("  PRESS RELEASE:     Marketing document. Lowest legal weight. Statements")
    print("                     of present fact can still be actionable, but forward-")
    print("                     looking claims get safe harbor protection.")
    print()
    print("  FORM 8-K:          SEC filing. Higher legal weight. Must be filed within")
    print("                     4 business days. Merger agreement attached as exhibit.")
    print()
    print("  PROXY STATEMENT:   Highest legal weight for shareholders. Board has a")
    print("  (DEFM14A)          fiduciary duty of candor. Must disclose background,")
    print("                     reasons, fairness opinion, projections, conflicts.")
    print("                     THIS is where the real disclosure happens.")
    print()
    print("  MERGER AGREEMENT:  The binding contract. Contains reps & warranties,")
    print("                     disclosure schedules (exceptions to reps), covenants.")
    print("                     Disclosure schedules are usually confidential.")
    print()
    print("  For PRIVATE deals, most of these documents don't exist publicly.")
    print("  The press release becomes the ONLY public disclosure — which means")
    print("  its wording carries disproportionate analytical weight even though")
    print("  it carries the LOWEST legal weight.")
    print()

    # --- Analyze each deal ---
    dt = build_downtown_analysis()
    pe = build_playlist_analysis()
    dt.disclosure_score = score_disclosures(dt)
    pe.disclosure_score = score_disclosures(pe)

    # --- Document hierarchy per deal ---
    hdr("DOCUMENT STATUS BY DEAL")

    for a in [dt, pe]:
        print(f"  [{a.deal_name}]")
        print(f"  Deal Type: {a.deal_type}")
        print()
        for doc in a.documents:
            status_marker = {
                DocStatus.FILED: "[FILED]     ",
                DocStatus.PARTIAL: "[PARTIAL]   ",
                DocStatus.NOT_REQUIRED: "[NOT REQ'D] ",
                DocStatus.NOT_FILED: "[NOT FILED] ",
                DocStatus.UNKNOWN: "[UNKNOWN]   ",
            }[doc.status]
            print(f"    {status_marker} {doc.name}")
            print(f"                   Form: {doc.sec_form}")
            print(f"                   Legal weight: {doc.legal_weight}")
            if doc.note:
                print(f"                   Note: {doc.note}")
            if doc.source_url:
                print(f"                   Source: {doc.source_url}")
            print()
        sep("-")
        print()

    # --- Disclosure completeness ---
    hdr("DISCLOSURE COMPLETENESS ANALYSIS")

    for a in [dt, pe]:
        print(f"  [{a.deal_name}]  Score: {a.disclosure_score:.0f}/100")
        print()
        for d in a.disclosures:
            if d.status == DocStatus.NOT_REQUIRED:
                marker = "  [N/A]    "
            elif d.status == DocStatus.FILED:
                marker = "  [OK]     "
            elif d.status == DocStatus.PARTIAL:
                marker = "  [WEAK]   "
            else:
                marker = "  [MISSING]"

            print(f"  {marker} {d.name}")
            print(f"             Disclosed: {d.what_was_disclosed[:100]}{'...' if len(d.what_was_disclosed) > 100 else ''}")
            if d.what_is_missing and d.status != DocStatus.NOT_REQUIRED:
                print(f"             Missing:   {d.what_is_missing[:120]}{'...' if len(d.what_is_missing) > 120 else ''}")
            print(f"             Legal:     {d.legal_significance[:120]}{'...' if len(d.legal_significance) > 120 else ''}")
            print()
        sep("-")
        print()

    # --- Comparative ---
    hdr("COMPARATIVE ASSESSMENT")

    row = "  {:<40s} {:>18s} {:>18s}"
    print(row.format("Metric", "VMG/Downtown", "Playlist/EGYM"))
    print(row.format("-" * 40, "-" * 18, "-" * 18))
    print(row.format("Deal type", "Private-Private", "Private-Private"))
    print(row.format("Public parent?", "Yes (UMG/Euronext)", "No"))
    print(row.format("SEC filings required?", "Indirect (via UMG)", "No"))
    print(row.format("Shareholder vote required?", "No", "No"))
    print(row.format("Proxy statement filed?", "No", "No"))
    print(row.format("Fairness opinion public?", "No", "No"))
    print(row.format("Merger agreement public?", "No", "No"))
    print(row.format("Regulatory review?", "Yes (EC)", "Pending"))
    print(row.format("Financial data disclosed?", "Leaked (Billboard)", "Minimal (rev only)"))
    print(row.format("EBITDA disclosed?", "Leaked (~$40M)", "No"))
    print(row.format("Synergies quantified?", "No", "No"))
    print(row.format("Integration costs?", "No", "No"))
    print(row.format("DISCLOSURE SCORE", f"{dt.disclosure_score:.0f}/100", f"{pe.disclosure_score:.0f}/100"))
    print()

    print("  INTERPRETATION:")
    print()
    print("  Both deals are private-to-private transactions, which means MOST of")
    print("  the disclosure infrastructure that exists in public M&A does not apply.")
    print("  There is no proxy statement, no fairness opinion, no financial projections,")
    print("  no risk factors, and no merger agreement in the public domain for either deal.")
    print()
    print("  The ONLY public disclosure for both deals is the press release.")
    print()
    print("  Downtown scores higher because Billboard independently reported financial")
    print("  details ($40M EBITDA, $130M net revenue, $900M gross) that the parties")
    print("  themselves chose not to disclose. Without that reporting, Downtown's")
    print("  disclosure score would be nearly identical to Playlist/EGYM's.")
    print()
    print("  Playlist/EGYM is a $7.5B combined valuation supported by exactly two")
    print("  data points in the public domain: deal value and approximate revenue.")
    print("  Everything else — profitability, growth rate, margins, projections,")
    print("  synergies, integration plan, risk factors — is behind the wall of")
    print("  private company confidentiality.")
    print()
    print("  This is not unusual for private deals. But it means that any external")
    print("  analysis of these transactions is inherently limited. The real disclosures")
    print("  exist in the merger agreement, disclosure schedules, investor side letters,")
    print("  and data room materials — none of which are public.")
    print()

    hdr("WHAT WOULD BE DIFFERENT IN A PUBLIC DEAL")
    print("  For reference, if either of these were public-company deals requiring")
    print("  a shareholder vote, the proxy statement (DEFM14A) would need to contain:")
    print()
    print("    1. BACKGROUND OF THE MERGER — full narrative of who contacted whom,")
    print("       when, what alternatives were considered, how the price was negotiated")
    print()
    print("    2. REASONS FOR THE MERGER — board's specific rationale, with financial")
    print("       metrics cited, not just 'significant milestone' or 'pivotal moment'")
    print()
    print("    3. FAIRNESS OPINION — full text of the financial advisor's analysis,")
    print("       including DCF, comparable companies, comparable transactions,")
    print("       premiums paid analysis, and the assumptions underlying each")
    print()
    print("    4. FINANCIAL PROJECTIONS — management's forward-looking estimates")
    print("       that were provided to the financial advisor and board, including")
    print("       revenue, EBITDA, free cash flow, capex, and terminal value assumptions")
    print()
    print("    5. INTERESTS OF DIRECTORS AND OFFICERS — conflicts disclosure,")
    print("       change-of-control payments, equity acceleration, employment agreements")
    print()
    print("    6. RISK FACTORS — material risks specific to the transaction")
    print()
    print("  None of this exists in the public domain for either deal analyzed here.")
    print("  Source: https://www.lexology.com/library/detail.aspx?g=a1937255-5c68-44c5-b97f-51810cf04de7")
    print()

    sep()
    print("  END OF DISCLOSURE ANALYSIS")
    sep()


if __name__ == "__main__":
    run()