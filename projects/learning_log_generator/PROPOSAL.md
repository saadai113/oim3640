# Proposal: Automatic Learning Log Generator

## Problem

Writing learning logs by hand after every coding session is tedious and inconsistent. Students skip it, forget what they did, or write vague summaries.

## Solution

A filesystem watcher that monitors a directory for `.py` file saves and automatically appends a structured learning log entry to `learning_log.md` — with zero API calls, zero cost.

## How It Works

Uses Python's `ast` module to statically analyze each saved file and extract:
- **Concepts used** — functions, classes, comprehensions, error handling, generators, async/await, type hints, etc.
- **Libraries imported** — categorized as stdlib, popular third-party, or other
- **Code stats** — total lines, functions, classes, longest function
- **Potential issues** — bare `except`, mutable default args, builtin shadowing, missing docstrings

## Why Static Analysis

No LLM API = no cost, no latency, no keys. The AST captures objective facts about the code. Entries are generated in under a second.

## Output

A `learning_log.md` file that grows automatically as the student codes, timestamped per file save.
