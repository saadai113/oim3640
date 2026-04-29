# Learning Log

Auto-generated via static analysis (no API). Started: 2026-04-28 11:24:05


## public_deal_disclosure.py — 2026-04-28 11:24:06

### File Stats
- Lines: 882 total / 794 non-blank / 46 comments
- Functions: 12 | Classes: 6
- Longest function: `print_deal_analysis` (139 lines)

### Concepts Detected
**Classes / OOP**
- `C` — methods: ['score_color']
- `LegalCitation`
- `DocStatus` — inherits from ['Enum']
- `Severity` — inherits from ['Enum']
- `DisclosureRequirement`
- `PublicDeal` — methods: ['disclosure_score', 'critical_gaps']
**Comprehensions**
- list comprehension
- generator expression
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `score_color()` — decorated with ['staticmethod'] — 1 param(s)
- `disclosure_score()` — decorated with ['property'] — 1 param(s)
- `critical_gaps()` — decorated with ['property'] — 1 param(s)
- `build_capital_one_discover()`
- `analyze_deal()` — 1 param(s)
- `sep()` — 2 param(s), 2 default(s)
- `hdr()` — 1 param(s)
- `wrap()` — 3 param(s), 2 default(s)
**Loops**
- for d in disclosures
- for d in deal.disclosures
- for (key, auth) in LEGAL_AUTHORITIES.items()
- for gap in deal.critical_gaps
- for key in d.required_by
**Standard Library**
- `dataclasses` — importing ['dataclass', 'field']
- `typing` — importing ['Optional', 'List']
- `enum` — importing ['Enum']
- `json`
- `textwrap`
- `sys`
- `copy`
**Type Hints**
- name: str
- citation: str
- description: str
- source_url: str
- jurisdiction: str
- id: str
- required_by: List[str]
- where_it_lives: str

### Potential Issues
- 105 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['sep', 'hdr', 'main', 'score_color', 'disclosure_score', 'critical_gaps']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## unified_analyzer.py — 2026-04-28 11:24:06

### File Stats
- Lines: 777 total / 681 non-blank / 53 comments
- Functions: 17 | Classes: 5
- Longest function: `run_scan` (97 lines)

### Concepts Detected
**Classes / OOP**
- `LegalCitation`
- `Status` — inherits from ['Enum']
- `Severity` — inherits from ['Enum']
- `DisclosureItem` — methods: ['legal_citations']
- `Filing` — methods: ['url']
**Comprehensions**
- list comprehension
- generator expression
**Error Handling**
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
**Functional**
- ternary expression (x if cond else y)
- lambda expression
**Functions**
- `legal_citations()` — decorated with ['property'] — 1 param(s)
- `url()` — decorated with ['property'] — 1 param(s)
- `lookup_cik()` — 1 param(s)
- `get_filings()` — 2 param(s)
- `download_filing()` — 2 param(s), 1 default(s)
- `extract_sections()` — 1 param(s)
- `analyze_with_llm()` — 4 param(s)
- `score_deal()` — 1 param(s)
**Loops**
- for (i, form) in enumerate(forms)
- for (key, patterns) in SECTION_PATTERNS.items()
- for pattern in patterns
- for item in disclosures
- for (form_type, flist) in filings.items()
- for f in flist[:2]
- for s in sections_found
- for s in set(SECTION_PATTERNS.keys()) - set(sections_found)
**Standard Library**
- `argparse`
- `copy`
- `json`
- `os`
- `re`
- `sys`
- `textwrap`
- `time`
**Third-Party Libraries**
- `anthropic` (Anthropic API client)
**Type Hints**
- name: str
- citation: str
- description: str
- source_url: str
- jurisdiction: str
- id: str
- required_by: List[str]
- location: str

### Potential Issues
- 96 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['lookup_cik', 'get_filings', 'download_filing', 'extract_sections', 'score_deal', 'sep', 'hdr', 'wrap_text', 'main', 'legal_citations', 'url']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────
