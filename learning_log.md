# Learning Log

Auto-generated via static analysis (no API). Started: 2026-02-22 20:19:47


## learning_log_watcher.py — 2026-02-23 00:38:04

### File Stats
- Lines: 521 total / 434 non-blank / 13 comments
- Functions: 37 | Classes: 2
- Longest function: `detect_concepts` (165 lines)

### Concepts Detected
**Classes / OOP**
- `Visitor` — inherits from ['ast.NodeVisitor'] — methods: ['visit_FunctionDef', 'visit_ClassDef', 'visit_Import', 'visit_ImportFrom', 'visit_ListComp', 'visit_DictComp', 'visit_SetComp', 'visit_GeneratorExp', 'visit_Lambda', 'visit_Try', 'visit_With', 'visit_For', 'visit_While', 'visit_Global', 'visit_Nonlocal', 'visit_Yield', 'visit_YieldFrom', 'visit_Await', 'visit_Assert', 'visit_IfExp', 'visit_AnnAssign', 'visit_Match', 'visit_Dict']
- `PyFileHandler` — inherits from ['FileSystemEventHandler'] — methods: ['__init__', '_init_log', '_should_process', '_process', 'on_modified', 'on_created']
**Comprehensions**
- list comprehension
- generator expression
**Context Managers**
- with ["open(filepath, 'r', encoding='utf-8', errors='replace')"]
- with ["open(log_path, 'a', encoding='utf-8')"]
- with ["open(filepath, 'rb')"]
- with ["open(self.log_path, 'w', encoding='utf-8')"]
**Error Handling**
- try/except — catching: ['ImportError']
- try/except — catching: ['base Exception']
- try/except — catching: ['SyntaxError']
- try/except — catching: ['NameError']
- try/except — catching: ['KeyboardInterrupt']
**Functional**
- ternary expression (x if cond else y)
**Functions**
- `detect_concepts()` — 2 param(s)
- `visit_FunctionDef()` — 2 param(s)
- `visit_ClassDef()` — 2 param(s)
- `visit_Import()` — 2 param(s)
- `visit_ImportFrom()` — 2 param(s)
- `visit_ListComp()` — 2 param(s)
- `visit_DictComp()` — 2 param(s)
- `visit_SetComp()` — 2 param(s)
**Loops**
- for alias in node.names
- for k in concepts
- for item in concepts[k]
- for node in ast.walk(tree)
- for default in node.args.defaults
- for (op, comp) in zip(node.ops, node.comparators)
- for target in node.targets
- for fn in functions
**Standard Library**
- `sys`
- `os`
- `ast`
- `time`
- `hashlib`
- `argparse`
- `datetime` — importing ['datetime']
- `pathlib` — importing ['Path']
**Third-Party Libraries**
- `watchdog` (filesystem event watching)
**Type Hints**
- self.hashes: dict

### Potential Issues
- 10 print() calls — for anything beyond a throwaway script, use the `logging` module for controllable output levels.
- Functions without docstrings: ['detect_concepts', 'detect_issues', 'compute_stats', 'generate_log_entry', 'append_to_log', 'get_hash', 'main', '_categorize_import', '__init__', '_init_log', '_should_process', '_process', 'on_modified', 'on_created', 'visit_FunctionDef', 'visit_ClassDef', 'visit_Import', 'visit_ImportFrom', 'visit_ListComp', 'visit_DictComp', 'visit_SetComp', 'visit_GeneratorExp', 'visit_Lambda', 'visit_Try', 'visit_With', 'visit_For', 'visit_While', 'visit_Global', 'visit_Nonlocal', 'visit_Yield', 'visit_YieldFrom', 'visit_Await', 'visit_Assert', 'visit_IfExp', 'visit_AnnAssign', 'visit_Match', 'visit_Dict']. Undocumented functions are a maintenance liability.

────────────────────────────────────────────────────────────
