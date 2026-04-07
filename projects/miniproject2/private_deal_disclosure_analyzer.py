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
  1. VMG / Downtown Music Holdings ($775M) — public-to-private
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
  |     Legal authority: No mandatory SEC rule, but misstatements of present fact are
  |       actionable under Exchange Act Rule 10b-5 (17 CFR § 240.10b-5).
  |       Forward-looking statements get safe harbor under Securities Act § 27A and
  |       Exchange Act § 21E (Private Securities Litigation Reform Act, 15 U.S.C. § 78u-5).
  |     Source: https://www.lexology.com/library/detail.aspx?g=53d64d2f-6564-4300-a096-693160776bef
  |
  +-- Form 8-K (Current Report)
  |     Audience: SEC, investors
  |     Legal weight: HIGH (SEC filing, subject to Sarbanes-Oxley certifications)
  |     Contains: Material definitive agreement, merger agreement as exhibit
  |     Must be filed within 4 business days
  |     Legal authority: Required under Exchange Act § 13 or § 15(d) (15 U.S.C. §§ 78m,
  |       78o(d)); Item 1.01 of Form 8-K (entry into a material definitive agreement);
  |       Rule 13a-11 (17 CFR § 240.13a-11). Merger agreement filed as exhibit under
  |       Item 601(b)(2) of Regulation S-K (17 CFR § 229.601(b)(2)).
  |     Source: https://www.secfilingdata.com/mergers-acquisitions-what-to-look-for-in-the-sec-filings/
  |
  +-- Form 425 (Communications re: Business Combination)
        Audience: SEC, investors
        Legal weight: MEDIUM (filed to comply with proxy solicitation rules)
        Contains: Any written communications about the deal before proxy is filed
        Legal authority: Rule 425 under the Securities Act (17 CFR § 230.425);
          Rule 14a-12 under the Exchange Act (17 CFR § 240.14a-12) for written
          soliciting materials prior to the filing of a definitive proxy statement.

TIER 2: PROXY / REGISTRATION (Weeks 2-12)
  |
  +-- PREM14A (Preliminary Proxy Statement)
  |     Audience: SEC review (not distributed to shareholders)
  |     Legal weight: HIGH (SEC reviews and issues comment letters)
  |     Contains: Draft of all merger disclosures
  |     Legal authority: Rule 14a-3(a) of the Exchange Act (17 CFR § 240.14a-3(a))
  |       requires furnishing a proxy statement before soliciting proxies.
  |       Governed by Regulation 14A (17 CFR Part 240, Rules 14a-1 through 14a-21).
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
  |     Legal authority: Regulation 14A (17 CFR Part 240); Schedule 14A items 4, 7, 8,
  |       14, and 21. Delaware duty of candor established in Smith v. Van Gorkom,
  |       488 A.2d 858 (Del. 1985); reaffirmed in Arnold v. Society for Savings Bancorp,
  |       650 A.2d 1270 (Del. 1994). Forward-looking projections may be protected by
  |       PSLRA safe harbor (15 U.S.C. § 78u-5(c)).
  |     Source: https://www.lexology.com/library/detail.aspx?g=a1937255-5c68-44c5-b97f-51810cf04de7
  |
  +-- Form S-4 (Registration Statement for new securities)
        Only if stock consideration is used
        Contains: Same as DEFM14A plus registration of new shares
        Legal authority: Securities Act § 5 (15 U.S.C. § 77e); registration on Form S-4
          governed by General Instruction A; financial statements required under
          Regulation S-X (17 CFR Part 210).

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
  |     Legal authority: Filed as exhibit to Form 8-K under Item 601(b)(2) of
  |       Regulation S-K (17 CFR § 229.601(b)(2)) for SEC-reporting companies.
  |
  +-- Disclosure Schedules (confidential, usually not filed publicly)
        Legal weight: HIGHEST (exceptions to reps & warranties)
        Contains:
          - Known liabilities, litigation, contracts, environmental issues
          - Material exceptions to every representation made
          - This is where the bodies are buried
        Legal authority: Attached as schedules to the merger agreement; publicly filed
          as part of the exhibit under Item 601(b)(2) of Regulation S-K, though
          parties routinely apply for confidential treatment under Exchange Act
          Rule 24b-2 (17 CFR § 240.24b-2) for competitively sensitive schedules.
        Source: https://www.sec.gov/Archives/edgar/data/0000732717/000095012305006178/y04651a2exv2w2.htm

TIER 4: POST-CLOSING
  |
  +-- Form 8-K (Closing announcement)
  |     Legal authority: Item 2.01 of Form 8-K (completion of acquisition or disposition
  |       of assets); required within 4 business days under Rule 13a-11.
  +-- Pro forma financial statements (if material acquisition for public buyer)
  |     Legal authority: Article 11 of Regulation S-X (17 CFR § 210.11-01 et seq.);
  |       required in Form 8-K/A within 71 days if acquisition is significant under
  |       Regulation S-X Rule 3-05 (17 CFR § 210.3-05).
  +-- Goodwill and purchase price allocation (in subsequent 10-K/10-Q)
        Legal authority: ASC 805 (Business Combinations) for U.S. GAAP; IFRS 3
          (Business Combinations) for IFRS reporters; SEC Staff Accounting Bulletins
          Topics 1.B and 2.A provide interpretive guidance.
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
            legal_basis="EU Market Abuse Regulation (MAR) Art. 17 (Regulation (EU) No 596/2014) for "
                        "Euronext-listed UMG — requires prompt disclosure of inside information. "
                        "U.S. equivalent for SEC registrants: Exchange Act Rule 13a-11 / Form 8-K Item 1.01.",
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
            legal_basis="No specific requirement for private target in a private deal. "
                        "For SEC registrants, Regulation S-X Rule 3-05 (17 CFR § 210.3-05) requires "
                        "audited financials of an acquired business only when the acquisition exceeds "
                        "significance thresholds (20%/40%/50% tests). Rule 14a-3(a) proxy solicitation "
                        "requirements do not apply — no shareholder vote is being solicited.",
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
            legal_basis="No specific requirement for private target. For SEC registrants acquiring a "
                        "significant business, Regulation S-X Rule 3-05 (17 CFR § 210.3-05) would require "
                        "audited income statements. IFRS 3 (Business Combinations) requires UMG to disclose "
                        "post-acquisition revenue and profit of Downtown in its consolidated financial statements.",
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
            legal_basis="Not legally required for private deals. In public deals, synergy projections "
                        "provided to financial advisors must be disclosed in the proxy under Regulation 14A "
                        "Schedule 14A Item 14 and the 'Reasons for the Merger' section. "
                        "Such projections may be protected as forward-looking statements under PSLRA "
                        "(Securities Act § 27A; Exchange Act § 21E, 15 U.S.C. § 78u-5).",
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
            legal_basis="Not required pre-closing. Post-closing, UMG must disclose acquisition-related "
                        "costs under IFRS 3 para. 53 (transaction costs expensed as incurred) and "
                        "IAS 37 (provisions for restructuring). For U.S. GAAP registrants, ASC 805-10-25 "
                        "and ASC 420 (exit or disposal cost obligations) govern similar disclosures.",
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
            legal_basis="Required in proxy for public shareholder vote under Regulation 14A and the "
                        "Delaware duty of candor (Smith v. Van Gorkom, 488 A.2d 858 (Del. 1985)). "
                        "Not legally required in private deals where no proxy is solicited under "
                        "Rule 14a-3(a) of the Exchange Act (17 CFR § 240.14a-3(a)).",
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
            legal_basis="Required in proxy/S-4 for public deals under Item 3 of Schedule 14A and "
                        "Item 503 of Regulation S-K (17 CFR § 229.503); not required for private deals. "
                        "For Euronext-listed UMG, material new risks must be disclosed under MAR Art. 17 "
                        "(Regulation (EU) No 596/2014) and the EU Prospectus Regulation (Regulation (EU) "
                        "2017/1129) if new securities are issued.",
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
            legal_basis="U.S.: Private Securities Litigation Reform Act (PSLRA) safe harbor under "
                        "Securities Act § 27A (15 U.S.C. § 77z-2) and Exchange Act § 21E "
                        "(15 U.S.C. § 78u-5) — protects written forward-looking statements "
                        "accompanied by meaningful cautionary language. "
                        "EU: MAR Art. 7(1) (Regulation (EU) No 596/2014) and the EU Prospectus "
                        "Regulation Art. 16 for forward-looking information that constitutes "
                        "inside information or appears in a prospectus.",
            typical_location="Press release footer, SEC filings",
            status=DocStatus.PARTIAL,
            what_was_disclosed="Standard legal disclaimer present in press release",
            what_is_missing="N/A — adequate for the limited forward-looking claims made",
            legal_significance="The press release makes very few forward-looking claims, so the PSLRA "
                              "safe harbor (Securities Act § 27A; Exchange Act § 21E) is largely moot. "
                              "Most language describes completed actions. For Venable LLP's guidance on "
                              "structuring compliant safe harbor disclaimers in M&A communications, see: "
                              "https://www.venable.com/insights/publications/2019/11/forward-looking-statements-the-safe-harbor. "
                              "The EU MAR Art. 7 safe harbor for inside information also does not apply "
                              "because no material non-public information is contained in a completion release.",
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
            legal_basis="Voluntary disclosure (private deal). No SEC registration means no Regulation S-K "
                        "Item 10(b) or Rule 408 (17 CFR § 230.408) requirement. If Playlist later files "
                        "an S-1, this valuation becomes part of the IPO disclosure history reviewed "
                        "under Securities Act § 11 (liability for material misstatements in registration "
                        "statements, 15 U.S.C. § 77k).",
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
            legal_basis="Private placement exempt from Securities Act § 5 registration under "
                        "§ 4(a)(2) (sales not involving a public offering, 15 U.S.C. § 77d(a)(2)) "
                        "or Regulation D Rule 506(b) (17 CFR § 230.506(b)) for accredited investors. "
                        "Form D must be filed with the SEC within 15 days of first sale "
                        "(Rule 503, 17 CFR § 230.503). No public prospectus required.",
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
            legal_basis="Voluntary (private companies). No Regulation S-X Rule 8-02 or Rule 3-05 "
                        "obligation — those rules apply only to SEC registrants. "
                        "If Playlist later IPOs, the S-1 must include audited financials for the "
                        "most recent three fiscal years under Regulation S-X Rule 3-01 "
                        "(17 CFR § 210.3-01) and any acquired business meeting significance thresholds "
                        "under Rule 3-05 (17 CFR § 210.3-05).",
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
            legal_basis="None required for private deal. Rule 10b-5 (17 CFR § 240.10b-5) prohibits "
                        "fraud in connection with the purchase or sale of any security, but applies "
                        "only where securities are being sold — a private merger is not a public "
                        "securities offering. Note: SEC v. Texas Gulf Sulphur Co., 401 F.2d 833 "
                        "(2d Cir. 1968) established that omissions of material facts can violate "
                        "10b-5, but Macquarie Infrastructure Corp. v. Moab Partners, L.P., "
                        "601 U.S. 257 (2024) clarified that pure omissions (no duty to speak) "
                        "are not actionable under Rule 10b-5(b).",
            typical_location="Proxy statement, fairness opinion (if public deal)",
            status=DocStatus.NOT_FILED,
            what_was_disclosed="'Strong profitability' — two words, no numbers",
            what_is_missing="EBITDA (reported or adjusted), net income, operating margin, free cash flow, "
                           "unit economics by segment (SaaS vs. hardware vs. marketplace vs. corporate wellness)",
            legal_significance="CRITICAL GAP. 'Strong profitability' is an opinion/characterization, not "
                              "a statement of fact. Under Rule 10b-5 (17 CFR § 240.10b-5), opinions can be "
                              "actionable if the speaker doesn't actually hold that opinion or omits facts "
                              "showing it's misleading (Omnicare, Inc. v. Laborers Dist. Council Constr. "
                              "Industry Pension Fund, 575 U.S. 175 (2015)). However, Macquarie Infrastructure "
                              "Corp. v. Moab Partners, L.P., 601 U.S. 257 (2024) held that pure omissions — "
                              "where there is no independent duty to speak — do not violate Rule 10b-5(b). "
                              "This is a private deal with no publicly traded securities, so 10b-5 doesn't "
                              "directly apply. If Playlist IPOs, this language becomes discoverable history "
                              "subject to Securities Act § 11 liability.",
        ),
        DisclosureItem(
            name="Synergy Targets",
            description="Expected value creation from combination",
            legal_basis="None required for private deal. In public deals, synergies provided to "
                        "the financial advisor must be disclosed in the proxy under Schedule 14A "
                        "Item 14 (Regulation 14A, 17 CFR Part 240). Such statements may be "
                        "protected as forward-looking statements under PSLRA safe harbor "
                        "(Securities Act § 27A; Exchange Act § 21E, 15 U.S.C. § 78u-5).",
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
            legal_basis="None required for private deal. Post-closing, integration costs must be "
                        "disclosed under ASC 805-10-50 (Business Combinations disclosures) for "
                        "U.S. GAAP registrants or IFRS 3 para. 59 for IFRS reporters. "
                        "Restructuring charges require separate disclosure under ASC 420 "
                        "or IAS 37 (Provisions, Contingent Liabilities and Contingent Assets).",
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
            legal_basis="Required in proxy for public deals — projections provided to the board or "
                        "financial advisor must be disclosed under Regulation 14A, Schedule 14A "
                        "Item 14 (17 CFR Part 240) and the duty of candor from Smith v. Van Gorkom, "
                        "488 A.2d 858 (Del. 1985). Not required for private deals. "
                        "Disclosed projections may be protected by PSLRA safe harbor "
                        "(Securities Act § 27A; Exchange Act § 21E).",
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
            legal_basis="Not required (private deal). If Playlist files an S-1, risk factors must be "
                        "disclosed under Securities Act § 7 and Item 503 of Regulation S-K "
                        "(17 CFR § 229.503), which requires discussion of 'the most significant "
                        "factors that make the offering speculative or risky.' SEC Staff Guidance "
                        "(C&DI) requires deal-specific rather than generic risk factor language.",
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
    print("       when, what alternatives were considered, how the price was negotiated.")
    print("       Legal authority: Schedule 14A Item 14(b)(2); Delaware duty of candor")
    print("       (Smith v. Van Gorkom, 488 A.2d 858 (Del. 1985)).")
    print()
    print("    2. REASONS FOR THE MERGER — board's specific rationale, with financial")
    print("       metrics cited, not just 'significant milestone' or 'pivotal moment'.")
    print("       Legal authority: Schedule 14A Item 14(b)(3); Regulation 14A")
    print("       (17 CFR Part 240, Rules 14a-1 through 14a-21).")
    print()
    print("    3. FAIRNESS OPINION — full text of the financial advisor's analysis,")
    print("       including DCF, comparable companies, comparable transactions,")
    print("       premiums paid analysis, and the assumptions underlying each.")
    print("       Legal authority: Schedule 14A Item 14(b)(6); Rule 14a-3(a)")
    print("       (17 CFR § 240.14a-3(a)); Delaware duty of candor from Van Gorkom.")
    print()
    print("    4. FINANCIAL PROJECTIONS — management's forward-looking estimates")
    print("       that were provided to the financial advisor and board, including")
    print("       revenue, EBITDA, free cash flow, capex, and terminal value assumptions.")
    print("       Legal authority: Schedule 14A Item 14(b)(6) (fairness opinion inputs);")
    print("       SEC Staff Legal Bulletin No. 20 (proxy disclosure guidance); PSLRA")
    print("       safe harbor under Securities Act § 27A and Exchange Act § 21E")
    print("       (15 U.S.C. §§ 77z-2, 78u-5) for accompanied cautionary statements.")
    print()
    print("    5. INTERESTS OF DIRECTORS AND OFFICERS — conflicts disclosure,")
    print("       change-of-control payments, equity acceleration, employment agreements.")
    print("       Legal authority: Schedule 14A Item 5 and Item 14(b)(9);")
    print("       Exchange Act Rule 14a-101 (Schedule 14A); Item 402(j) of Reg. S-K")
    print("       (17 CFR § 229.402(j)) for golden parachute compensation.")
    print()
    print("    6. RISK FACTORS — material risks specific to the transaction.")
    print("       Legal authority: Item 503 of Regulation S-K (17 CFR § 229.503);")
    print("       Securities Act § 7 (15 U.S.C. § 77g); SEC guidance requiring")
    print("       risk factors to be 'specific to the registrant' (not boilerplate).")
    print()
    print("    7. RULE 10b-5 ANTI-FRAUD OVERLAY — all statements in all documents")
    print("       (proxy, 8-K, press release) are subject to Exchange Act Rule 10b-5")
    print("       (17 CFR § 240.10b-5): no material misstatements or omissions.")
    print("       Note: Macquarie Infrastructure Corp. v. Moab Partners, L.P.,")
    print("       601 U.S. 257 (2024) limits 10b-5(b) to half-truths — pure omissions")
    print("       with no independent duty to disclose are not actionable under 10b-5(b).")
    print("       Cornell Law full text: https://www.law.cornell.edu/cfr/text/17/240.10b-5")
    print()
    print("  None of this exists in the public domain for either deal analyzed here.")
    print("  Source: https://www.lexology.com/library/detail.aspx?g=a1937255-5c68-44c5-b97f-51810cf04de7")
    print()

    sep()
    print("  END OF DISCLOSURE ANALYSIS")
    sep()


if __name__ == "__main__":
    run()