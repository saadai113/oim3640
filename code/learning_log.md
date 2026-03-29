# Learning Log

Auto-generated via static analysis (no API). Started: 2026-02-23 00:36:45


## encryption.py — 2026-03-18 18:46:20

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## encryption.py — 2026-03-18 18:46:20

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-18 18:49:30

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-18 18:49:30

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-18 18:49:31

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-18 18:49:31

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## ai agent.py — 2026-03-23 14:41:27

### File Stats
- Lines: 302 total / 254 non-blank / 18 comments
- Functions: 8 | Classes: 6
- Longest function: `match_po` (97 lines)

### Concepts Detected
**Classes / OOP**
- `MatchStatus` — inherits from ['Enum']
- `LineItem` — methods: ['total']
- `PurchaseOrder` — methods: ['total']
- `Invoice` — methods: ['total']
- `GoodsReceipt` — methods: ['total']
- `MatchResult` — methods: ['summary']
**Comprehensions**
- generator expression
- dict comprehension
**Context Managers**
- with ["open(filepath, newline='', encoding='utf-8')"]
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `total()` — decorated with ['property'] — 1 param(s)
- `summary()` — 1 param(s)
- `match_po()` — 5 param(s), 3 default(s)
- `load_items_from_csv()` — 1 param(s)
- `match_from_csvs()` — 7 param(s), 3 default(s)
**Loops**
- for f in self.flags
- for (desc, inv_item) in inv_items.items()
- for desc in po_items
- for (desc, po_item) in po_items.items()
- for row in csv.DictReader(f)
**Standard Library**
- `csv`
- `dataclasses` — importing ['dataclass', 'field']
- `typing` — importing ['Optional']
- `enum` — importing ['Enum']
**Type Hints**
- description: str
- quantity: float
- unit_price: float
- po_number: str
- vendor: str
- items: list[LineItem]
- invoice_number: str
- receipt_number: str

### Potential Issues
- 12 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['load_items_from_csv', 'match_from_csvs', 'total', 'total', 'total', 'total', 'summary']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## blackrock_13f.py — 2026-03-23 14:41:27

### File Stats
- Lines: 157 total / 126 non-blank / 14 comments
- Functions: 4 | Classes: 0
- Longest function: `fetch_and_parse` (49 lines)

### Concepts Detected
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['Exception']
**Functions**
- `fetch_and_parse()` — 1 param(s)
- `get()` — 1 param(s)
- `compare()` — 2 param(s)
- `main()`
**Loops**
- for ns in [NS, '']
- for info in items
**Standard Library**
- `xml` as `ET`
- `io` — importing ['StringIO']
**Third-Party Libraries**
- `requests` (HTTP client)
- `pandas` (data analysis / DataFrames)
- `lxml` (XML/HTML parsing)

### Potential Issues
- 23 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['fetch_and_parse', 'main', 'get']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## calc.py — 2026-03-23 14:41:27

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## class 5.py — 2026-03-23 14:41:28

### File Stats
- Lines: 17 total / 13 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `calc_tax` (4 lines)

### Concepts Detected
**Functions**
- `calc_tax()` — 1 param(s)

### Potential Issues
- Functions without docstrings: ['calc_tax']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## class 8.py — 2026-03-23 14:41:28

### File Stats
- Lines: 66 total / 53 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `koch_curve` (18 lines)

### Concepts Detected
**Functions**
- `koch_curve()` — 3 param(s) ⚠ recursive
- `sierpinski()` — 3 param(s) ⚠ recursive
**Loops**
- for _ in range(3)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Line 13: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 39: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['sierpinski']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## classonline.py — 2026-03-23 14:41:28

### File Stats
- Lines: 27 total / 22 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `uses_any` (6 lines)

### Concepts Detected
**Functions**
- `uses_any()` — 2 param(s)
- `random_letter()`
**Loops**
- while n != 0
- for letter in letters
**Standard Library**
- `random`

### Potential Issues
- Line 2: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.

────────────────────────────────────────────────────────────

## encryption.py — 2026-03-23 14:41:28

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## hello.py — 2026-03-23 14:41:28

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## large files.py — 2026-03-23 14:41:28

### File Stats
- Lines: 201 total / 165 non-blank / 7 comments
- Functions: 8 | Classes: 0
- Longest function: `create_shortcuts_folder` (66 lines)

### Concepts Detected
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['FileNotFoundError', 'Exception']
- try/except — catching: ['KeyboardInterrupt']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `main()`
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 20 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## lf2.py — 2026-03-23 14:41:28

### File Stats
- Lines: 338 total / 273 non-blank / 13 comments
- Functions: 10 | Classes: 0
- Longest function: `main` (74 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
- generator expression
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['ValueError', 'KeyboardInterrupt']
- try/except — catching: ['PermissionError', 'Exception']
- try/except — catching: ['FileNotFoundError', 'Exception']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `select_files_to_delete()` — 1 param(s)
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
- for (i, (filepath, size_kb)) in enumerate(large_files, 1)
- while True
- for part in response.split(',')
- for fp in filepaths
- for filepath in filepaths
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 47 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-23 14:41:28

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-23 14:41:28

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## pythonchallenge2.py — 2026-03-23 14:41:28

### File Stats
- Lines: 1232 total / 1230 non-blank / 80 comments
- Functions: 1 | Classes: 0
- Longest function: `histogram` (4 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Functions**
- `histogram()` — 1 param(s)
**Loops**
- for c in s

### Potential Issues
- Line 1231: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['histogram']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## recursive.py — 2026-03-23 14:41:28

### File Stats
- Lines: 7 total / 6 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `groundhog_day` (3 lines)

### Concepts Detected
**Functions**
- `groundhog_day()` ⚠ recursive
**Standard Library**
- `time`

### Potential Issues
- Functions without docstrings: ['groundhog_day']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## s07.py — 2026-03-23 14:41:28

### File Stats
- Lines: 30 total / 26 non-blank / 2 comments
- Functions: 3 | Classes: 0
- Longest function: `main` (6 lines)

### Concepts Detected
**Functions**
- `draw_square()` — 2 param(s), 1 default(s)
- `draw_spiral()` — 1 param(s)
- `main()`
**Loops**
- for _ in range(4)
- for i in range(36)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee.py — 2026-03-23 14:41:28

### File Stats
- Lines: 36 total / 27 non-blank / 1 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (8 lines)

### Concepts Detected
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_words()` — 2 param(s)
**Loops**
- for letter in word.lower()
- for word in word_list
- for word in sorted(results)

### Potential Issues
- Functions without docstrings: ['is_valid', 'spelling_bee', 'find_words']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee_1.py — 2026-03-23 14:41:28

### File Stats
- Lines: 48 total / 41 non-blank / 0 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (22 lines)

### Concepts Detected
**Comprehensions**
- generator expression
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_pangrams()` — 2 param(s)
**Loops**
- for letters in word.lower()
- for word in word_list
**Standard Library**
- `os`

### Potential Issues
- Functions without docstrings: ['is_valid', 'find_pangrams']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks 2.py — 2026-03-23 14:41:28

### File Stats
- Lines: 31 total / 22 non-blank / 3 comments
- Functions: 1 | Classes: 0
- Longest function: `mc_european_call_antithetic` (26 lines)

### Concepts Detected
**Functions**
- `mc_european_call_antithetic()` — 7 param(s), 2 default(s)
**Standard Library**
- `random`
- `math`
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)

### Potential Issues
- Functions without docstrings: ['mc_european_call_antithetic']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks.py — 2026-03-23 14:41:28

### File Stats
- Lines: 466 total / 399 non-blank / 38 comments
- Functions: 23 | Classes: 0
- Longest function: `run_weekly_recommendation` (42 lines)

### Concepts Detected
**Comprehensions**
- dict comprehension
- list comprehension
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
- lambda expression
**Functions**
- `db()`
- `init_db()`
- `set_setting_if_missing()` — 2 param(s)
- `get_setting()` — 2 param(s), 1 default(s)
- `set_setting()` — 2 param(s)
- `get_universe()`
- `get_holdings()`
- `upsert_holding()` — 2 param(s)
**Loops**
- for t in tickers
- for (t, sh) in holdings.items()
- for t in sorted(tickers)
**Other Imports**
- `yfinance`
- `apscheduler`
- `pytz`
**Standard Library**
- `os`
- `json`
- `sqlite3`
- `datetime` — importing ['datetime', 'timedelta']
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)
- `pandas` (data analysis / DataFrames)
- `flask` (web framework (micro))

### Potential Issues
- Line 180: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 244: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['db', 'init_db', 'set_setting_if_missing', 'get_setting', 'set_setting', 'get_universe', 'get_holdings', 'upsert_holding', 'current_weights', 'run_weekly_recommendation', 'save_recommendation', 'latest_recommendation', 'index', 'run_now', 'update_settings', 'export_latest', 'start_scheduler']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## ai agent.py — 2026-03-24 10:02:06

### File Stats
- Lines: 302 total / 254 non-blank / 18 comments
- Functions: 8 | Classes: 6
- Longest function: `match_po` (97 lines)

### Concepts Detected
**Classes / OOP**
- `MatchStatus` — inherits from ['Enum']
- `LineItem` — methods: ['total']
- `PurchaseOrder` — methods: ['total']
- `Invoice` — methods: ['total']
- `GoodsReceipt` — methods: ['total']
- `MatchResult` — methods: ['summary']
**Comprehensions**
- generator expression
- dict comprehension
**Context Managers**
- with ["open(filepath, newline='', encoding='utf-8')"]
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `total()` — decorated with ['property'] — 1 param(s)
- `summary()` — 1 param(s)
- `match_po()` — 5 param(s), 3 default(s)
- `load_items_from_csv()` — 1 param(s)
- `match_from_csvs()` — 7 param(s), 3 default(s)
**Loops**
- for f in self.flags
- for (desc, inv_item) in inv_items.items()
- for desc in po_items
- for (desc, po_item) in po_items.items()
- for row in csv.DictReader(f)
**Standard Library**
- `csv`
- `dataclasses` — importing ['dataclass', 'field']
- `typing` — importing ['Optional']
- `enum` — importing ['Enum']
**Type Hints**
- description: str
- quantity: float
- unit_price: float
- po_number: str
- vendor: str
- items: list[LineItem]
- invoice_number: str
- receipt_number: str

### Potential Issues
- 12 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['load_items_from_csv', 'match_from_csvs', 'total', 'total', 'total', 'total', 'summary']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## blackrock_13f.py — 2026-03-24 10:02:07

### File Stats
- Lines: 157 total / 126 non-blank / 14 comments
- Functions: 4 | Classes: 0
- Longest function: `fetch_and_parse` (49 lines)

### Concepts Detected
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['Exception']
**Functions**
- `fetch_and_parse()` — 1 param(s)
- `get()` — 1 param(s)
- `compare()` — 2 param(s)
- `main()`
**Loops**
- for ns in [NS, '']
- for info in items
**Standard Library**
- `xml` as `ET`
- `io` — importing ['StringIO']
**Third-Party Libraries**
- `requests` (HTTP client)
- `pandas` (data analysis / DataFrames)
- `lxml` (XML/HTML parsing)

### Potential Issues
- 23 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['fetch_and_parse', 'main', 'get']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## calc.py — 2026-03-24 10:02:07

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## class 5.py — 2026-03-24 10:02:07

### File Stats
- Lines: 17 total / 13 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `calc_tax` (4 lines)

### Concepts Detected
**Functions**
- `calc_tax()` — 1 param(s)

### Potential Issues
- Functions without docstrings: ['calc_tax']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## class 8.py — 2026-03-24 10:02:07

### File Stats
- Lines: 66 total / 53 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `koch_curve` (18 lines)

### Concepts Detected
**Functions**
- `koch_curve()` — 3 param(s) ⚠ recursive
- `sierpinski()` — 3 param(s) ⚠ recursive
**Loops**
- for _ in range(3)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Line 13: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 39: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['sierpinski']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## classonline.py — 2026-03-24 10:02:07

### File Stats
- Lines: 27 total / 22 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `uses_any` (6 lines)

### Concepts Detected
**Functions**
- `uses_any()` — 2 param(s)
- `random_letter()`
**Loops**
- while n != 0
- for letter in letters
**Standard Library**
- `random`

### Potential Issues
- Line 2: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.

────────────────────────────────────────────────────────────

## encryption.py — 2026-03-24 10:02:07

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## hello.py — 2026-03-24 10:02:07

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## large files.py — 2026-03-24 10:02:07

### File Stats
- Lines: 201 total / 165 non-blank / 7 comments
- Functions: 8 | Classes: 0
- Longest function: `create_shortcuts_folder` (66 lines)

### Concepts Detected
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['FileNotFoundError', 'Exception']
- try/except — catching: ['KeyboardInterrupt']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `main()`
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 20 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## lf2.py — 2026-03-24 10:02:07

### File Stats
- Lines: 338 total / 273 non-blank / 13 comments
- Functions: 10 | Classes: 0
- Longest function: `main` (74 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
- generator expression
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['ValueError', 'KeyboardInterrupt']
- try/except — catching: ['PermissionError', 'Exception']
- try/except — catching: ['FileNotFoundError', 'Exception']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `select_files_to_delete()` — 1 param(s)
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
- for (i, (filepath, size_kb)) in enumerate(large_files, 1)
- while True
- for part in response.split(',')
- for fp in filepaths
- for filepath in filepaths
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 47 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-24 10:02:07

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-24 10:02:07

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## pythonchallenge2.py — 2026-03-24 10:02:07

### File Stats
- Lines: 1232 total / 1230 non-blank / 80 comments
- Functions: 1 | Classes: 0
- Longest function: `histogram` (4 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Functions**
- `histogram()` — 1 param(s)
**Loops**
- for c in s

### Potential Issues
- Line 1231: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['histogram']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## recursive.py — 2026-03-24 10:02:07

### File Stats
- Lines: 7 total / 6 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `groundhog_day` (3 lines)

### Concepts Detected
**Functions**
- `groundhog_day()` ⚠ recursive
**Standard Library**
- `time`

### Potential Issues
- Functions without docstrings: ['groundhog_day']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## s07.py — 2026-03-24 10:02:07

### File Stats
- Lines: 30 total / 26 non-blank / 2 comments
- Functions: 3 | Classes: 0
- Longest function: `main` (6 lines)

### Concepts Detected
**Functions**
- `draw_square()` — 2 param(s), 1 default(s)
- `draw_spiral()` — 1 param(s)
- `main()`
**Loops**
- for _ in range(4)
- for i in range(36)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee.py — 2026-03-24 10:02:07

### File Stats
- Lines: 36 total / 27 non-blank / 1 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (8 lines)

### Concepts Detected
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_words()` — 2 param(s)
**Loops**
- for letter in word.lower()
- for word in word_list
- for word in sorted(results)

### Potential Issues
- Functions without docstrings: ['is_valid', 'spelling_bee', 'find_words']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee_1.py — 2026-03-24 10:02:07

### File Stats
- Lines: 48 total / 41 non-blank / 0 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (22 lines)

### Concepts Detected
**Comprehensions**
- generator expression
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_pangrams()` — 2 param(s)
**Loops**
- for letters in word.lower()
- for word in word_list
**Standard Library**
- `os`

### Potential Issues
- Functions without docstrings: ['is_valid', 'find_pangrams']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks 2.py — 2026-03-24 10:02:07

### File Stats
- Lines: 31 total / 22 non-blank / 3 comments
- Functions: 1 | Classes: 0
- Longest function: `mc_european_call_antithetic` (26 lines)

### Concepts Detected
**Functions**
- `mc_european_call_antithetic()` — 7 param(s), 2 default(s)
**Standard Library**
- `random`
- `math`
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)

### Potential Issues
- Functions without docstrings: ['mc_european_call_antithetic']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks.py — 2026-03-24 10:02:08

### File Stats
- Lines: 466 total / 399 non-blank / 38 comments
- Functions: 23 | Classes: 0
- Longest function: `run_weekly_recommendation` (42 lines)

### Concepts Detected
**Comprehensions**
- dict comprehension
- list comprehension
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
- lambda expression
**Functions**
- `db()`
- `init_db()`
- `set_setting_if_missing()` — 2 param(s)
- `get_setting()` — 2 param(s), 1 default(s)
- `set_setting()` — 2 param(s)
- `get_universe()`
- `get_holdings()`
- `upsert_holding()` — 2 param(s)
**Loops**
- for t in tickers
- for (t, sh) in holdings.items()
- for t in sorted(tickers)
**Other Imports**
- `yfinance`
- `apscheduler`
- `pytz`
**Standard Library**
- `os`
- `json`
- `sqlite3`
- `datetime` — importing ['datetime', 'timedelta']
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)
- `pandas` (data analysis / DataFrames)
- `flask` (web framework (micro))

### Potential Issues
- Line 180: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 244: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['db', 'init_db', 'set_setting_if_missing', 'get_setting', 'set_setting', 'get_universe', 'get_holdings', 'upsert_holding', 'current_weights', 'run_weekly_recommendation', 'save_recommendation', 'latest_recommendation', 'index', 'run_now', 'update_settings', 'export_latest', 'start_scheduler']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## ai agent.py — 2026-03-25 09:59:53

### File Stats
- Lines: 302 total / 254 non-blank / 18 comments
- Functions: 8 | Classes: 6
- Longest function: `match_po` (97 lines)

### Concepts Detected
**Classes / OOP**
- `MatchStatus` — inherits from ['Enum']
- `LineItem` — methods: ['total']
- `PurchaseOrder` — methods: ['total']
- `Invoice` — methods: ['total']
- `GoodsReceipt` — methods: ['total']
- `MatchResult` — methods: ['summary']
**Comprehensions**
- generator expression
- dict comprehension
**Context Managers**
- with ["open(filepath, newline='', encoding='utf-8')"]
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `total()` — decorated with ['property'] — 1 param(s)
- `summary()` — 1 param(s)
- `match_po()` — 5 param(s), 3 default(s)
- `load_items_from_csv()` — 1 param(s)
- `match_from_csvs()` — 7 param(s), 3 default(s)
**Loops**
- for f in self.flags
- for (desc, inv_item) in inv_items.items()
- for desc in po_items
- for (desc, po_item) in po_items.items()
- for row in csv.DictReader(f)
**Standard Library**
- `csv`
- `dataclasses` — importing ['dataclass', 'field']
- `typing` — importing ['Optional']
- `enum` — importing ['Enum']
**Type Hints**
- description: str
- quantity: float
- unit_price: float
- po_number: str
- vendor: str
- items: list[LineItem]
- invoice_number: str
- receipt_number: str

### Potential Issues
- 12 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['load_items_from_csv', 'match_from_csvs', 'total', 'total', 'total', 'total', 'summary']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## blackrock_13f.py — 2026-03-25 09:59:53

### File Stats
- Lines: 157 total / 126 non-blank / 14 comments
- Functions: 4 | Classes: 0
- Longest function: `fetch_and_parse` (49 lines)

### Concepts Detected
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['Exception']
**Functions**
- `fetch_and_parse()` — 1 param(s)
- `get()` — 1 param(s)
- `compare()` — 2 param(s)
- `main()`
**Loops**
- for ns in [NS, '']
- for info in items
**Standard Library**
- `xml` as `ET`
- `io` — importing ['StringIO']
**Third-Party Libraries**
- `requests` (HTTP client)
- `pandas` (data analysis / DataFrames)
- `lxml` (XML/HTML parsing)

### Potential Issues
- 23 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['fetch_and_parse', 'main', 'get']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## calc.py — 2026-03-25 09:59:53

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## class 5.py — 2026-03-25 09:59:53

### File Stats
- Lines: 17 total / 13 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `calc_tax` (4 lines)

### Concepts Detected
**Functions**
- `calc_tax()` — 1 param(s)

### Potential Issues
- Functions without docstrings: ['calc_tax']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## class 8.py — 2026-03-25 09:59:53

### File Stats
- Lines: 66 total / 53 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `koch_curve` (18 lines)

### Concepts Detected
**Functions**
- `koch_curve()` — 3 param(s) ⚠ recursive
- `sierpinski()` — 3 param(s) ⚠ recursive
**Loops**
- for _ in range(3)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Line 13: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 39: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['sierpinski']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## classonline.py — 2026-03-25 09:59:53

### File Stats
- Lines: 27 total / 22 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `uses_any` (6 lines)

### Concepts Detected
**Functions**
- `uses_any()` — 2 param(s)
- `random_letter()`
**Loops**
- while n != 0
- for letter in letters
**Standard Library**
- `random`

### Potential Issues
- Line 2: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.

────────────────────────────────────────────────────────────

## encryption.py — 2026-03-25 09:59:53

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## hello.py — 2026-03-25 09:59:53

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## large files.py — 2026-03-25 09:59:53

### File Stats
- Lines: 201 total / 165 non-blank / 7 comments
- Functions: 8 | Classes: 0
- Longest function: `create_shortcuts_folder` (66 lines)

### Concepts Detected
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['FileNotFoundError', 'Exception']
- try/except — catching: ['KeyboardInterrupt']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `main()`
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 20 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## lf2.py — 2026-03-25 09:59:53

### File Stats
- Lines: 338 total / 273 non-blank / 13 comments
- Functions: 10 | Classes: 0
- Longest function: `main` (74 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
- generator expression
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['ValueError', 'KeyboardInterrupt']
- try/except — catching: ['PermissionError', 'Exception']
- try/except — catching: ['FileNotFoundError', 'Exception']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `select_files_to_delete()` — 1 param(s)
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
- for (i, (filepath, size_kb)) in enumerate(large_files, 1)
- while True
- for part in response.split(',')
- for fp in filepaths
- for filepath in filepaths
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 47 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-25 09:59:53

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-25 09:59:54

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## pythonchallenge2.py — 2026-03-25 09:59:54

### File Stats
- Lines: 1232 total / 1230 non-blank / 80 comments
- Functions: 1 | Classes: 0
- Longest function: `histogram` (4 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Functions**
- `histogram()` — 1 param(s)
**Loops**
- for c in s

### Potential Issues
- Line 1231: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['histogram']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## recursive.py — 2026-03-25 09:59:54

### File Stats
- Lines: 7 total / 6 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `groundhog_day` (3 lines)

### Concepts Detected
**Functions**
- `groundhog_day()` ⚠ recursive
**Standard Library**
- `time`

### Potential Issues
- Functions without docstrings: ['groundhog_day']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## s07.py — 2026-03-25 09:59:54

### File Stats
- Lines: 30 total / 26 non-blank / 2 comments
- Functions: 3 | Classes: 0
- Longest function: `main` (6 lines)

### Concepts Detected
**Functions**
- `draw_square()` — 2 param(s), 1 default(s)
- `draw_spiral()` — 1 param(s)
- `main()`
**Loops**
- for _ in range(4)
- for i in range(36)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee.py — 2026-03-25 09:59:54

### File Stats
- Lines: 36 total / 27 non-blank / 1 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (8 lines)

### Concepts Detected
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_words()` — 2 param(s)
**Loops**
- for letter in word.lower()
- for word in word_list
- for word in sorted(results)

### Potential Issues
- Functions without docstrings: ['is_valid', 'spelling_bee', 'find_words']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee_1.py — 2026-03-25 09:59:54

### File Stats
- Lines: 48 total / 41 non-blank / 0 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (22 lines)

### Concepts Detected
**Comprehensions**
- generator expression
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_pangrams()` — 2 param(s)
**Loops**
- for letters in word.lower()
- for word in word_list
**Standard Library**
- `os`

### Potential Issues
- Functions without docstrings: ['is_valid', 'find_pangrams']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks 2.py — 2026-03-25 09:59:54

### File Stats
- Lines: 31 total / 22 non-blank / 3 comments
- Functions: 1 | Classes: 0
- Longest function: `mc_european_call_antithetic` (26 lines)

### Concepts Detected
**Functions**
- `mc_european_call_antithetic()` — 7 param(s), 2 default(s)
**Standard Library**
- `random`
- `math`
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)

### Potential Issues
- Functions without docstrings: ['mc_european_call_antithetic']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks.py — 2026-03-25 09:59:54

### File Stats
- Lines: 466 total / 399 non-blank / 38 comments
- Functions: 23 | Classes: 0
- Longest function: `run_weekly_recommendation` (42 lines)

### Concepts Detected
**Comprehensions**
- dict comprehension
- list comprehension
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
- lambda expression
**Functions**
- `db()`
- `init_db()`
- `set_setting_if_missing()` — 2 param(s)
- `get_setting()` — 2 param(s), 1 default(s)
- `set_setting()` — 2 param(s)
- `get_universe()`
- `get_holdings()`
- `upsert_holding()` — 2 param(s)
**Loops**
- for t in tickers
- for (t, sh) in holdings.items()
- for t in sorted(tickers)
**Other Imports**
- `yfinance`
- `apscheduler`
- `pytz`
**Standard Library**
- `os`
- `json`
- `sqlite3`
- `datetime` — importing ['datetime', 'timedelta']
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)
- `pandas` (data analysis / DataFrames)
- `flask` (web framework (micro))

### Potential Issues
- Line 180: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 244: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['db', 'init_db', 'set_setting_if_missing', 'get_setting', 'set_setting', 'get_universe', 'get_holdings', 'upsert_holding', 'current_weights', 'run_weekly_recommendation', 'save_recommendation', 'latest_recommendation', 'index', 'run_now', 'update_settings', 'export_latest', 'start_scheduler']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## ai agent.py — 2026-03-26 14:47:42

### File Stats
- Lines: 302 total / 254 non-blank / 18 comments
- Functions: 8 | Classes: 6
- Longest function: `match_po` (97 lines)

### Concepts Detected
**Classes / OOP**
- `MatchStatus` — inherits from ['Enum']
- `LineItem` — methods: ['total']
- `PurchaseOrder` — methods: ['total']
- `Invoice` — methods: ['total']
- `GoodsReceipt` — methods: ['total']
- `MatchResult` — methods: ['summary']
**Comprehensions**
- generator expression
- dict comprehension
**Context Managers**
- with ["open(filepath, newline='', encoding='utf-8')"]
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `total()` — decorated with ['property'] — 1 param(s)
- `summary()` — 1 param(s)
- `match_po()` — 5 param(s), 3 default(s)
- `load_items_from_csv()` — 1 param(s)
- `match_from_csvs()` — 7 param(s), 3 default(s)
**Loops**
- for f in self.flags
- for (desc, inv_item) in inv_items.items()
- for desc in po_items
- for (desc, po_item) in po_items.items()
- for row in csv.DictReader(f)
**Standard Library**
- `csv`
- `dataclasses` — importing ['dataclass', 'field']
- `typing` — importing ['Optional']
- `enum` — importing ['Enum']
**Type Hints**
- description: str
- quantity: float
- unit_price: float
- po_number: str
- vendor: str
- items: list[LineItem]
- invoice_number: str
- receipt_number: str

### Potential Issues
- 12 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['load_items_from_csv', 'match_from_csvs', 'total', 'total', 'total', 'total', 'summary']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## blackrock_13f.py — 2026-03-26 14:47:42

### File Stats
- Lines: 157 total / 126 non-blank / 14 comments
- Functions: 4 | Classes: 0
- Longest function: `fetch_and_parse` (49 lines)

### Concepts Detected
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['Exception']
**Functions**
- `fetch_and_parse()` — 1 param(s)
- `get()` — 1 param(s)
- `compare()` — 2 param(s)
- `main()`
**Loops**
- for ns in [NS, '']
- for info in items
**Standard Library**
- `xml` as `ET`
- `io` — importing ['StringIO']
**Third-Party Libraries**
- `requests` (HTTP client)
- `pandas` (data analysis / DataFrames)
- `lxml` (XML/HTML parsing)

### Potential Issues
- 23 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['fetch_and_parse', 'main', 'get']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## calc.py — 2026-03-26 14:47:42

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## class 5.py — 2026-03-26 14:47:42

### File Stats
- Lines: 17 total / 13 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `calc_tax` (4 lines)

### Concepts Detected
**Functions**
- `calc_tax()` — 1 param(s)

### Potential Issues
- Functions without docstrings: ['calc_tax']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## class 8.py — 2026-03-26 14:47:42

### File Stats
- Lines: 66 total / 53 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `koch_curve` (18 lines)

### Concepts Detected
**Functions**
- `koch_curve()` — 3 param(s) ⚠ recursive
- `sierpinski()` — 3 param(s) ⚠ recursive
**Loops**
- for _ in range(3)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Line 13: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 39: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['sierpinski']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## classonline.py — 2026-03-26 14:47:42

### File Stats
- Lines: 27 total / 22 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `uses_any` (6 lines)

### Concepts Detected
**Functions**
- `uses_any()` — 2 param(s)
- `random_letter()`
**Loops**
- while n != 0
- for letter in letters
**Standard Library**
- `random`

### Potential Issues
- Line 2: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.

────────────────────────────────────────────────────────────

## encryption.py — 2026-03-26 14:47:43

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## hello.py — 2026-03-26 14:47:43

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## large files.py — 2026-03-26 14:47:43

### File Stats
- Lines: 201 total / 165 non-blank / 7 comments
- Functions: 8 | Classes: 0
- Longest function: `create_shortcuts_folder` (66 lines)

### Concepts Detected
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['FileNotFoundError', 'Exception']
- try/except — catching: ['KeyboardInterrupt']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `main()`
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 20 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## lf2.py — 2026-03-26 14:47:43

### File Stats
- Lines: 338 total / 273 non-blank / 13 comments
- Functions: 10 | Classes: 0
- Longest function: `main` (74 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
- generator expression
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['ValueError', 'KeyboardInterrupt']
- try/except — catching: ['PermissionError', 'Exception']
- try/except — catching: ['FileNotFoundError', 'Exception']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `select_files_to_delete()` — 1 param(s)
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
- for (i, (filepath, size_kb)) in enumerate(large_files, 1)
- while True
- for part in response.split(',')
- for fp in filepaths
- for filepath in filepaths
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 47 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-26 14:47:43

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-26 14:47:43

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## pythonchallenge2.py — 2026-03-26 14:47:43

### File Stats
- Lines: 1232 total / 1230 non-blank / 80 comments
- Functions: 1 | Classes: 0
- Longest function: `histogram` (4 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Functions**
- `histogram()` — 1 param(s)
**Loops**
- for c in s

### Potential Issues
- Line 1231: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['histogram']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## recursive.py — 2026-03-26 14:47:43

### File Stats
- Lines: 7 total / 6 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `groundhog_day` (3 lines)

### Concepts Detected
**Functions**
- `groundhog_day()` ⚠ recursive
**Standard Library**
- `time`

### Potential Issues
- Functions without docstrings: ['groundhog_day']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## s07.py — 2026-03-26 14:47:43

### File Stats
- Lines: 30 total / 26 non-blank / 2 comments
- Functions: 3 | Classes: 0
- Longest function: `main` (6 lines)

### Concepts Detected
**Functions**
- `draw_square()` — 2 param(s), 1 default(s)
- `draw_spiral()` — 1 param(s)
- `main()`
**Loops**
- for _ in range(4)
- for i in range(36)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee.py — 2026-03-26 14:47:43

### File Stats
- Lines: 36 total / 27 non-blank / 1 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (8 lines)

### Concepts Detected
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_words()` — 2 param(s)
**Loops**
- for letter in word.lower()
- for word in word_list
- for word in sorted(results)

### Potential Issues
- Functions without docstrings: ['is_valid', 'spelling_bee', 'find_words']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee_1.py — 2026-03-26 14:47:43

### File Stats
- Lines: 48 total / 41 non-blank / 0 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (22 lines)

### Concepts Detected
**Comprehensions**
- generator expression
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_pangrams()` — 2 param(s)
**Loops**
- for letters in word.lower()
- for word in word_list
**Standard Library**
- `os`

### Potential Issues
- Functions without docstrings: ['is_valid', 'find_pangrams']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks 2.py — 2026-03-26 14:47:43

### File Stats
- Lines: 31 total / 22 non-blank / 3 comments
- Functions: 1 | Classes: 0
- Longest function: `mc_european_call_antithetic` (26 lines)

### Concepts Detected
**Functions**
- `mc_european_call_antithetic()` — 7 param(s), 2 default(s)
**Standard Library**
- `random`
- `math`
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)

### Potential Issues
- Functions without docstrings: ['mc_european_call_antithetic']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks.py — 2026-03-26 14:47:44

### File Stats
- Lines: 466 total / 399 non-blank / 38 comments
- Functions: 23 | Classes: 0
- Longest function: `run_weekly_recommendation` (42 lines)

### Concepts Detected
**Comprehensions**
- dict comprehension
- list comprehension
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
- lambda expression
**Functions**
- `db()`
- `init_db()`
- `set_setting_if_missing()` — 2 param(s)
- `get_setting()` — 2 param(s), 1 default(s)
- `set_setting()` — 2 param(s)
- `get_universe()`
- `get_holdings()`
- `upsert_holding()` — 2 param(s)
**Loops**
- for t in tickers
- for (t, sh) in holdings.items()
- for t in sorted(tickers)
**Other Imports**
- `yfinance`
- `apscheduler`
- `pytz`
**Standard Library**
- `os`
- `json`
- `sqlite3`
- `datetime` — importing ['datetime', 'timedelta']
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)
- `pandas` (data analysis / DataFrames)
- `flask` (web framework (micro))

### Potential Issues
- Line 180: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 244: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['db', 'init_db', 'set_setting_if_missing', 'get_setting', 'set_setting', 'get_universe', 'get_holdings', 'upsert_holding', 'current_weights', 'run_weekly_recommendation', 'save_recommendation', 'latest_recommendation', 'index', 'run_now', 'update_settings', 'export_latest', 'start_scheduler']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## blackrock_13f.py — 2026-03-28 19:40:09

### File Stats
- Lines: 157 total / 126 non-blank / 14 comments
- Functions: 4 | Classes: 0
- Longest function: `fetch_and_parse` (49 lines)

### Concepts Detected
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['Exception']
**Functions**
- `fetch_and_parse()` — 1 param(s)
- `get()` — 1 param(s)
- `compare()` — 2 param(s)
- `main()`
**Loops**
- for ns in [NS, '']
- for info in items
**Standard Library**
- `xml` as `ET`
- `io` — importing ['StringIO']
**Third-Party Libraries**
- `requests` (HTTP client)
- `pandas` (data analysis / DataFrames)
- `lxml` (XML/HTML parsing)

### Potential Issues
- 23 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['fetch_and_parse', 'main', 'get']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## ai agent.py — 2026-03-28 19:40:15

### File Stats
- Lines: 302 total / 254 non-blank / 18 comments
- Functions: 8 | Classes: 6
- Longest function: `match_po` (97 lines)

### Concepts Detected
**Classes / OOP**
- `MatchStatus` — inherits from ['Enum']
- `LineItem` — methods: ['total']
- `PurchaseOrder` — methods: ['total']
- `Invoice` — methods: ['total']
- `GoodsReceipt` — methods: ['total']
- `MatchResult` — methods: ['summary']
**Comprehensions**
- generator expression
- dict comprehension
**Context Managers**
- with ["open(filepath, newline='', encoding='utf-8')"]
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `total()` — decorated with ['property'] — 1 param(s)
- `summary()` — 1 param(s)
- `match_po()` — 5 param(s), 3 default(s)
- `load_items_from_csv()` — 1 param(s)
- `match_from_csvs()` — 7 param(s), 3 default(s)
**Loops**
- for f in self.flags
- for (desc, inv_item) in inv_items.items()
- for desc in po_items
- for (desc, po_item) in po_items.items()
- for row in csv.DictReader(f)
**Standard Library**
- `csv`
- `dataclasses` — importing ['dataclass', 'field']
- `typing` — importing ['Optional']
- `enum` — importing ['Enum']
**Type Hints**
- description: str
- quantity: float
- unit_price: float
- po_number: str
- vendor: str
- items: list[LineItem]
- invoice_number: str
- receipt_number: str

### Potential Issues
- 12 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['load_items_from_csv', 'match_from_csvs', 'total', 'total', 'total', 'total', 'summary']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## calc.py — 2026-03-28 19:40:18

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## class 5.py — 2026-03-28 19:40:18

### File Stats
- Lines: 17 total / 13 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `calc_tax` (4 lines)

### Concepts Detected
**Functions**
- `calc_tax()` — 1 param(s)

### Potential Issues
- Functions without docstrings: ['calc_tax']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## class 8.py — 2026-03-28 19:40:18

### File Stats
- Lines: 66 total / 53 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `koch_curve` (18 lines)

### Concepts Detected
**Functions**
- `koch_curve()` — 3 param(s) ⚠ recursive
- `sierpinski()` — 3 param(s) ⚠ recursive
**Loops**
- for _ in range(3)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Line 13: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 39: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['sierpinski']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## classonline.py — 2026-03-28 19:40:18

### File Stats
- Lines: 27 total / 22 non-blank / 0 comments
- Functions: 2 | Classes: 0
- Longest function: `uses_any` (6 lines)

### Concepts Detected
**Functions**
- `uses_any()` — 2 param(s)
- `random_letter()`
**Loops**
- while n != 0
- for letter in letters
**Standard Library**
- `random`

### Potential Issues
- Line 2: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.

────────────────────────────────────────────────────────────

## encryption.py — 2026-03-28 19:40:18

### File Stats
- Lines: 299 total / 245 non-blank / 5 comments
- Functions: 12 | Classes: 3
- Longest function: `demonstration` (72 lines)

### Concepts Detected
**Classes / OOP**
- `AESEncryption` — methods: ['generate_key', 'derive_key_from_password', 'encrypt', 'decrypt']
- `RSAEncryption` — methods: ['generate_keypair', 'encrypt', 'decrypt', 'save_private_key', 'load_private_key']
- `HybridEncryption` — methods: ['encrypt', 'decrypt']
**Context Managers**
- with ["open(filename, 'rb')"]
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `generate_key()` — decorated with ['staticmethod']
- `derive_key_from_password()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `encrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `decrypt()` — decorated with ['staticmethod'] — 2 param(s)
- `generate_keypair()` — decorated with ['staticmethod'] — 1 param(s), 1 default(s)
- `save_private_key()` — decorated with ['staticmethod'] — 3 param(s), 1 default(s)
- `load_private_key()` — decorated with ['staticmethod'] — 2 param(s), 1 default(s)
- `decrypt()` — decorated with ['staticmethod'] — 3 param(s)
**Other Imports**
- `cryptography`
- `argon2`
- `stat`
**Standard Library**
- `os`
- `pathlib`
- `base64`

### Potential Issues
- 15 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## hello.py — 2026-03-28 19:40:19

### File Stats
- Lines: 1 total / 1 non-blank / 0 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
- None identified (file may be mostly data or config)

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## large files.py — 2026-03-28 19:40:19

### File Stats
- Lines: 201 total / 165 non-blank / 7 comments
- Functions: 8 | Classes: 0
- Longest function: `create_shortcuts_folder` (66 lines)

### Concepts Detected
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['FileNotFoundError', 'Exception']
- try/except — catching: ['KeyboardInterrupt']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `main()`
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 20 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## lf2.py — 2026-03-28 19:40:19

### File Stats
- Lines: 338 total / 273 non-blank / 13 comments
- Functions: 10 | Classes: 0
- Longest function: `main` (74 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
- generator expression
**Context Managers**
- with ["open(list_file, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['base Exception']
- try/except — catching: ['PermissionError']
- try/except — catching: ['Exception']
- try/except — catching: ['ImportError']
- try/except — catching: ['OSError']
- try/except — catching: ['ValueError', 'KeyboardInterrupt']
- try/except — catching: ['PermissionError', 'Exception']
- try/except — catching: ['FileNotFoundError', 'Exception']
**Functional**
- lambda expression
**Functions**
- `get_downloads_folder()`
- `get_file_size_kb()` — 1 param(s)
- `format_size()` — 1 param(s)
- `scan_large_files()` — 2 param(s), 1 default(s)
- `create_shortcuts_folder()` — 1 param(s)
- `create_text_file_list()` — 2 param(s)
- `open_folder_in_explorer()` — 1 param(s)
- `select_files_to_delete()` — 1 param(s)
**Loops**
- for (root, dirs, files) in os.walk(folder_path)
- for filename in files
- for (filepath, size_kb) in large_files
- for (i, (filepath, size_kb)) in enumerate(large_files, 1)
- while True
- for part in response.split(',')
- for fp in filepaths
- for filepath in filepaths
**Other Imports**
- `win32com`
**Standard Library**
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib` — importing ['Path']
- `tempfile`
- `shutil`

### Potential Issues
- 47 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.

────────────────────────────────────────────────────────────

## polymarket_tracker_livemoment.py — 2026-03-28 19:40:19

### File Stats
- Lines: 169 total / 142 non-blank / 1 comments
- Functions: 8 | Classes: 0
- Longest function: `main` (53 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Error Handling**
- try/except — catching: ['base Exception', 'base Exception']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `fetch_markets()` — 5 param(s), 5 default(s)
- `fetch_events()` — 5 param(s), 5 default(s)
- `search_markets()` — 2 param(s), 1 default(s)
- `parse_prices()` — 1 param(s)
- `format_usd()` — 1 param(s)
- `format_pct_change()` — 1 param(s)
- `display_market()` — 2 param(s), 1 default(s)
- `main()`
**Loops**
- for m in markets
- for (i, m) in enumerate(markets, 1)
**Standard Library**
- `json`
- `argparse`
- `datetime` — importing ['datetime']
**Third-Party Libraries**
- `requests` (HTTP client)

### Potential Issues
- 13 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## pythonchallenge.py — 2026-03-28 19:40:19

### File Stats
- Lines: 12 total / 10 non-blank / 1 comments
- Functions: 0 | Classes: 0
- Longest function: N/A

### Concepts Detected
**Loops**
- for c in encrypted

### Potential Issues
- No static issues detected.

────────────────────────────────────────────────────────────

## pythonchallenge2.py — 2026-03-28 19:40:20

### File Stats
- Lines: 1232 total / 1230 non-blank / 80 comments
- Functions: 1 | Classes: 0
- Longest function: `histogram` (4 lines)

### Concepts Detected
**Comprehensions**
- list comprehension
**Functions**
- `histogram()` — 1 param(s)
**Loops**
- for c in s

### Potential Issues
- Line 1231: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['histogram']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## recursive.py — 2026-03-28 19:40:20

### File Stats
- Lines: 7 total / 6 non-blank / 0 comments
- Functions: 1 | Classes: 0
- Longest function: `groundhog_day` (3 lines)

### Concepts Detected
**Functions**
- `groundhog_day()` ⚠ recursive
**Standard Library**
- `time`

### Potential Issues
- Functions without docstrings: ['groundhog_day']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## s07.py — 2026-03-28 19:40:20

### File Stats
- Lines: 30 total / 26 non-blank / 2 comments
- Functions: 3 | Classes: 0
- Longest function: `main` (6 lines)

### Concepts Detected
**Functions**
- `draw_square()` — 2 param(s), 1 default(s)
- `draw_spiral()` — 1 param(s)
- `main()`
**Loops**
- for _ in range(4)
- for i in range(36)
**Third-Party Libraries**
- `turtle` (turtle graphics (stdlib teaching tool))

### Potential Issues
- Functions without docstrings: ['main']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee.py — 2026-03-28 19:40:20

### File Stats
- Lines: 36 total / 27 non-blank / 1 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (8 lines)

### Concepts Detected
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_words()` — 2 param(s)
**Loops**
- for letter in word.lower()
- for word in word_list
- for word in sorted(results)

### Potential Issues
- Functions without docstrings: ['is_valid', 'spelling_bee', 'find_words']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## spelling_bee_1.py — 2026-03-28 19:40:20

### File Stats
- Lines: 48 total / 41 non-blank / 0 comments
- Functions: 3 | Classes: 0
- Longest function: `spelling_bee` (22 lines)

### Concepts Detected
**Comprehensions**
- generator expression
**Functions**
- `is_valid()` — 1 param(s)
- `spelling_bee()` — 3 param(s)
- `find_pangrams()` — 2 param(s)
**Loops**
- for letters in word.lower()
- for word in word_list
**Standard Library**
- `os`

### Potential Issues
- Functions without docstrings: ['is_valid', 'find_pangrams']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks 2.py — 2026-03-28 19:40:20

### File Stats
- Lines: 31 total / 22 non-blank / 3 comments
- Functions: 1 | Classes: 0
- Longest function: `mc_european_call_antithetic` (26 lines)

### Concepts Detected
**Functions**
- `mc_european_call_antithetic()` — 7 param(s), 2 default(s)
**Standard Library**
- `random`
- `math`
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)

### Potential Issues
- Functions without docstrings: ['mc_european_call_antithetic']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────

## stocks.py — 2026-03-28 19:40:20

### File Stats
- Lines: 466 total / 399 non-blank / 38 comments
- Functions: 23 | Classes: 0
- Longest function: `run_weekly_recommendation` (42 lines)

### Concepts Detected
**Comprehensions**
- dict comprehension
- list comprehension
**Error Handling**
- try/except — catching: ['Exception']
**Functional**
- ternary expression (x if cond else y)
- lambda expression
**Functions**
- `db()`
- `init_db()`
- `set_setting_if_missing()` — 2 param(s)
- `get_setting()` — 2 param(s), 1 default(s)
- `set_setting()` — 2 param(s)
- `get_universe()`
- `get_holdings()`
- `upsert_holding()` — 2 param(s)
**Loops**
- for t in tickers
- for (t, sh) in holdings.items()
- for t in sorted(tickers)
**Other Imports**
- `yfinance`
- `apscheduler`
- `pytz`
**Standard Library**
- `os`
- `json`
- `sqlite3`
- `datetime` — importing ['datetime', 'timedelta']
**Third-Party Libraries**
- `numpy` (numerical computing / arrays)
- `pandas` (data analysis / DataFrames)
- `flask` (web framework (micro))

### Potential Issues
- Line 180: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Line 244: use `is`/`is not` instead of `==`/`!=` when comparing to None, True, or False.
- Functions without docstrings: ['db', 'init_db', 'set_setting_if_missing', 'get_setting', 'set_setting', 'get_universe', 'get_holdings', 'upsert_holding', 'current_weights', 'run_weekly_recommendation', 'save_recommendation', 'latest_recommendation', 'index', 'run_now', 'update_settings', 'export_latest', 'start_scheduler']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────
