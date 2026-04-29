# Learning Log Generator

Watches a directory for `.py` file changes and auto-generates learning log entries using static code analysis — no API, no cost.

## Setup

```bash
pip install watchdog
```

## Usage

```bash
# Watch current directory
python learning_log_watcher.py

# Watch a specific directory
python learning_log_watcher.py path/to/your/project
```

Appends to `learning_log.md` in the watched directory. Press `Ctrl+C` to stop.

## What Gets Logged

For every saved `.py` file:

| Section | What It Contains |
|---------|-----------------|
| **File Stats** | Total lines, functions, classes, longest function |
| **Concepts Detected** | Functions, classes, comprehensions, error handling, generators, async, type hints, libraries |
| **Potential Issues** | Bare `except`, mutable defaults, builtin shadowing, missing docstrings, excessive prints |

## Files

| File | Purpose |
|------|---------|
| `learning_log_watcher.py` | Main watcher script |
| `learning_log.md` | Auto-generated output (grows over time) |
| `final_learning_log.md` | Compiled/finalized log |
