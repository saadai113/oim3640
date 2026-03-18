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
