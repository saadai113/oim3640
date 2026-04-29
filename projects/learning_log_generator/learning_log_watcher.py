"""
learning_log_watcher.py

Watches a directory for .py file changes and automatically generates
learning log entries using static code analysis — no API, no cost.

Requirements:
    pip install watchdog

Usage:
    python learning_log_watcher.py [directory_to_watch]
    Defaults to current directory if no argument given.

Output:
    Appends to learning_log.md in the watched directory.
"""

import sys
import os
import ast
import time
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("ERROR: watchdog not installed. Run: pip install watchdog")
    sys.exit(1)


LOG_FILENAME = "learning_log.md"

# ─── Known modules for categorization ───────────────────────────────────────
STDLIB_MODULES = {
    "os", "sys", "re", "io", "abc", "ast", "csv", "json", "math", "copy",
    "enum", "time", "uuid", "random", "string", "shutil", "struct", "hashlib",
    "logging", "pathlib", "datetime", "itertools", "functools", "collections",
    "threading", "multiprocessing", "subprocess", "contextlib", "dataclasses",
    "typing", "unittest", "argparse", "socket", "http", "urllib", "email",
    "html", "xml", "sqlite3", "pickle", "shelve", "queue", "heapq", "bisect",
    "textwrap", "pprint", "traceback", "inspect", "importlib", "platform",
    "tempfile", "zipfile", "tarfile", "gzip", "base64", "hmac", "secrets",
}

POPULAR_THIRD_PARTY = {
    "numpy": "numerical computing / arrays",
    "pandas": "data analysis / DataFrames",
    "matplotlib": "plotting / visualization",
    "seaborn": "statistical visualization",
    "sklearn": "machine learning",
    "scipy": "scientific computing",
    "tensorflow": "deep learning (TF)",
    "torch": "deep learning (PyTorch)",
    "flask": "web framework (micro)",
    "django": "web framework (full)",
    "fastapi": "async web API framework",
    "sqlalchemy": "ORM / database abstraction",
    "requests": "HTTP client",
    "httpx": "async HTTP client",
    "pydantic": "data validation / schemas",
    "pytest": "testing framework",
    "click": "CLI building",
    "rich": "terminal formatting",
    "anthropic": "Anthropic API client",
    "openai": "OpenAI API client",
    "watchdog": "filesystem event watching",
    "PIL": "image processing (Pillow)",
    "cv2": "computer vision (OpenCV)",
    "bs4": "HTML parsing (BeautifulSoup)",
    "lxml": "XML/HTML parsing",
    "celery": "async task queue",
    "redis": "Redis client",
    "boto3": "AWS SDK",
    "turtle": "turtle graphics (stdlib teaching tool)",
}

# ─── Concept detectors ───────────────────────────────────────────────────────

def detect_concepts(tree: ast.AST, source: str) -> dict:
    concepts = defaultdict(list)

    class Visitor(ast.NodeVisitor):

        def visit_FunctionDef(self, node):
            info = f"`{node.name}()`"
            decorators = [ast.unparse(d) for d in node.decorator_list]
            if decorators:
                info += f" — decorated with {decorators}"
            args = node.args
            if args.args:
                info += f" — {len(args.args)} param(s)"
            if args.defaults:
                info += f", {len(args.defaults)} default(s)"
            if args.vararg:
                info += ", *args"
            if args.kwarg:
                info += ", **kwargs"
            # detect recursion
            calls = [n.func.id for n in ast.walk(node)
                     if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
            if node.name in calls:
                info += " ⚠ recursive"
            concepts["Functions"].append(info)
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            bases = [ast.unparse(b) for b in node.bases]
            info = f"`{node.name}`"
            if bases:
                info += f" — inherits from {bases}"
            methods = [n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
            if methods:
                info += f" — methods: {methods}"
            concepts["Classes / OOP"].append(info)
            self.generic_visit(node)

        def visit_Import(self, node):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                _categorize_import(mod, alias.asname)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module:
                mod = node.module.split(".")[0]
                names = [a.name for a in node.names]
                _categorize_import(mod, names=names)
            self.generic_visit(node)

        def visit_ListComp(self, node):
            concepts["Comprehensions"].append("list comprehension")
            self.generic_visit(node)

        def visit_DictComp(self, node):
            concepts["Comprehensions"].append("dict comprehension")
            self.generic_visit(node)

        def visit_SetComp(self, node):
            concepts["Comprehensions"].append("set comprehension")
            self.generic_visit(node)

        def visit_GeneratorExp(self, node):
            concepts["Comprehensions"].append("generator expression")
            self.generic_visit(node)

        def visit_Lambda(self, node):
            concepts["Functional"].append("lambda expression")
            self.generic_visit(node)

        def visit_Try(self, node):
            handlers = [h.type.id if isinstance(h.type, ast.Name) else "base Exception"
                        for h in node.handlers if h.type]
            concepts["Error Handling"].append(f"try/except — catching: {handlers or ['unspecified']}")
            self.generic_visit(node)

        def visit_With(self, node):
            ctx = [ast.unparse(i.context_expr) for i in node.items]
            concepts["Context Managers"].append(f"with {ctx}")
            self.generic_visit(node)

        def visit_For(self, node):
            target = ast.unparse(node.target)
            iter_ = ast.unparse(node.iter)
            concepts["Loops"].append(f"for {target} in {iter_}")
            self.generic_visit(node)

        def visit_While(self, node):
            concepts["Loops"].append(f"while {ast.unparse(node.test)}")
            self.generic_visit(node)

        def visit_Global(self, node):
            concepts["Scope"].append(f"global vars: {node.names}")
            self.generic_visit(node)

        def visit_Nonlocal(self, node):
            concepts["Scope"].append(f"nonlocal vars: {node.names}")
            self.generic_visit(node)

        def visit_Yield(self, node):
            concepts["Generators"].append("yield — generator function")
            self.generic_visit(node)

        def visit_YieldFrom(self, node):
            concepts["Generators"].append("yield from")
            self.generic_visit(node)

        def visit_Await(self, node):
            concepts["Async/Await"].append("await expression")
            self.generic_visit(node)

        def visit_Assert(self, node):
            concepts["Testing / Assertions"].append(f"assert {ast.unparse(node.test)}")
            self.generic_visit(node)

        def visit_IfExp(self, node):
            concepts["Functional"].append("ternary expression (x if cond else y)")
            self.generic_visit(node)

        def visit_AnnAssign(self, node):
            concepts["Type Hints"].append(
                f"{ast.unparse(node.target)}: {ast.unparse(node.annotation)}"
            )
            self.generic_visit(node)

        def visit_Match(self, node):
            concepts["Pattern Matching (3.10+)"].append(
                f"match/case on `{ast.unparse(node.subject)}`"
            )
            self.generic_visit(node)

        def visit_Dict(self, node):
            if any(k is None for k in node.keys):
                concepts["Unpacking"].append("dict unpacking (**dict merge)")
            self.generic_visit(node)

    def _categorize_import(mod, asname=None, names=None):
        if mod in STDLIB_MODULES:
            label = f"`{mod}`"
            if asname:
                label += f" as `{asname}`"
            if names:
                label += f" — importing {names}"
            concepts["Standard Library"].append(label)
        elif mod in POPULAR_THIRD_PARTY:
            desc = POPULAR_THIRD_PARTY[mod]
            concepts["Third-Party Libraries"].append(f"`{mod}` ({desc})")
        else:
            concepts["Other Imports"].append(f"`{mod}`")

    Visitor().visit(tree)

    # Deduplicate while preserving order
    for k in concepts:
        seen = set()
        deduped = []
        for item in concepts[k]:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        concepts[k] = deduped

    return dict(concepts)


def detect_issues(tree: ast.AST, source: str) -> list:
    issues = []

    # Bare except
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(
                f"Line {node.lineno}: bare `except:` catches ALL exceptions including "
                f"KeyboardInterrupt and SystemExit. Use specific exception types."
            )

    # Mutable default arguments
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(
                        f"Line {node.lineno}: `{node.name}()` has a mutable default argument "
                        f"(list/dict/set). It is shared across all calls — a common source of bugs."
                    )

    # == None/True/False instead of is/is not
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    if isinstance(comp, ast.Constant) and comp.value in (None, True, False):
                        issues.append(
                            f"Line {node.lineno}: use `is`/`is not` instead of `==`/`!=` "
                            f"when comparing to None, True, or False."
                        )

    # Shadowing builtins
    builtins = {
        "list", "dict", "set", "tuple", "str", "int", "float", "type",
        "input", "print", "open", "id", "len", "range", "map", "filter",
        "zip", "sum", "min", "max", "sorted", "reversed", "enumerate",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in builtins:
                    issues.append(
                        f"Line {node.lineno}: variable `{target.id}` shadows a Python builtin. "
                        f"This will break any code that relies on the original builtin."
                    )

    # Excessive print() calls
    print_calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "print"
    ]
    if len(print_calls) > 5:
        issues.append(
            f"{len(print_calls)} print() calls — for anything beyond a throwaway script, "
            f"use the `logging` module for controllable output levels."
        )

    # Functions without docstrings
    undocumented = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_docstring = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )
            if not has_docstring:
                undocumented.append(node.name)
    if undocumented:
        issues.append(
            f"Functions without docstrings: {undocumented}. "
            f"Undocumented functions are a maintenance liability."
        )

    return issues


def compute_stats(tree: ast.AST, source: str) -> dict:
    lines = source.splitlines()
    non_blank = [l for l in lines if l.strip()]
    comment_lines = [l for l in lines if l.strip().startswith("#")]

    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

    longest_fn = None
    longest_len = 0
    for fn in functions:
        length = fn.end_lineno - fn.lineno
        if length > longest_len:
            longest_len = length
            longest_fn = fn.name

    return {
        "total_lines": len(lines),
        "non_blank_lines": len(non_blank),
        "comment_lines": len(comment_lines),
        "num_functions": len(functions),
        "num_classes": len(classes),
        "longest_function": f"`{longest_fn}` ({longest_len} lines)" if longest_fn else "N/A",
    }


# ─── Format the log entry ────────────────────────────────────────────────────

def generate_log_entry(filepath: str) -> str | None:
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except (IOError, OSError) as e:
        return f"[Could not read file: {e}]"

    if not source.strip():
        return None

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return (
            f"**⚠ Syntax Error — file could not be fully parsed:**\n\n"
            f"```\n{e}\n```\n\nFix the syntax error before a full analysis can run."
        )

    concepts = detect_concepts(tree, source)
    issues = detect_issues(tree, source)
    stats = compute_stats(tree, source)

    lines = []

    lines.append("### File Stats")
    lines.append(
        f"- Lines: {stats['total_lines']} total / "
        f"{stats['non_blank_lines']} non-blank / "
        f"{stats['comment_lines']} comments"
    )
    lines.append(f"- Functions: {stats['num_functions']} | Classes: {stats['num_classes']}")
    lines.append(f"- Longest function: {stats['longest_function']}")
    lines.append("")

    lines.append("### Concepts Detected")
    if concepts:
        for category, items in sorted(concepts.items()):
            lines.append(f"**{category}**")
            for item in items[:8]:
                lines.append(f"- {item}")
    else:
        lines.append("- None identified (file may be mostly data or config)")
    lines.append("")

    lines.append("### Potential Issues")
    if issues:
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- No static issues detected.")
    lines.append("")

    return "\n".join(lines)


def append_to_log(log_path: str, filepath: str, entry: str):
    filename = Path(filepath).name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = f"\n## {filename} — {timestamp}\n\n{entry}\n{'─' * 60}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(block)
    print(f"  [LOG] Entry written for {filename}")


# ─── Filesystem watcher ──────────────────────────────────────────────────────

def get_hash(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except (IOError, OSError):
        return ""


class PyFileHandler(FileSystemEventHandler):
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.log_path = os.path.join(watch_dir, LOG_FILENAME)
        self.hashes: dict = {}
        self._init_log()

    def _init_log(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(
                    f"# Learning Log\n\n"
                    f"Auto-generated via static analysis (no API). "
                    f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            print(f"  [CREATED] {self.log_path}")

    def _should_process(self, filepath: str) -> bool:
        if not filepath.endswith(".py"):
            return False
        try:
            if os.path.abspath(filepath) == os.path.abspath(__file__):
                return False
        except NameError:
            pass  # __file__ not defined in some environments (interactive, frozen)
        new_hash = get_hash(filepath)
        if not new_hash or new_hash == self.hashes.get(filepath):
            return False
        self.hashes[filepath] = new_hash
        return True

    def _process(self, filepath: str):
        print(f"  [DETECTED] {Path(filepath).name}")
        try:
            entry = generate_log_entry(filepath)
            if entry:
                append_to_log(self.log_path, filepath, entry)
            else:
                print("  [SKIPPED] Empty file.")
        except Exception as e:
            print(f"  [ERROR] Failed to process {Path(filepath).name}: {e}")

    def on_modified(self, event):
        if not event.is_directory:
            if self._should_process(event.src_path):
                self._process(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            if self._should_process(event.src_path):
                self._process(event.src_path)


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate learning logs from .py files — no API required."
    )
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to watch (default: current dir)"
    )
    args = parser.parse_args()

    watch_dir = os.path.abspath(args.directory)
    if not os.path.isdir(watch_dir):
        print(f"ERROR: '{watch_dir}' is not a valid directory.")
        sys.exit(1)

    print(f"Watching : {watch_dir}")
    print(f"Log file : {os.path.join(watch_dir, LOG_FILENAME)}")
    print("Press Ctrl+C to stop.\n")

    handler = PyFileHandler(watch_dir)
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping.")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()