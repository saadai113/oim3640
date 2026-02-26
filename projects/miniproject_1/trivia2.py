#!/usr/bin/env python3
"""
quiz_game.py — CLI trivia game with score tracking, feedback, and JSON file loading.

Usage:
    python quiz_game.py               # uses built-in sample questions
    python quiz_game.py questions.json  # loads from a JSON file

JSON format:
    [
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "answer": 1,
            "explanation": "Basic arithmetic."
        }
    ]
    'answer' is the 0-based index of the correct option.
    'explanation' is optional.
"""

import sys
import json
import random
import os
import time
import threading

# ── Terminal colors (gracefully degrade if unsupported) ──────────────────────

def supports_color():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

if supports_color():
    R  = "\033[91m"   # red
    G  = "\033[92m"   # green
    Y  = "\033[93m"   # yellow
    B  = "\033[94m"   # blue
    C  = "\033[96m"   # cyan
    W  = "\033[97m"   # white
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
else:
    R = G = Y = B = C = W = DIM = BOLD = RESET = ""

KEYS = "ABCDEFGHIJ"

# ── Built-in sample questions ─────────────────────────────────────────────────

SAMPLE_QUESTIONS = [
    {
        "question": "What keyword turns a Python function into a generator?",
        "options": ["return", "yield", "generate", "async"],
        "answer": 1,
        "explanation": "'yield' pauses the function and returns a value; the function resumes on next()."
    },
    {
        "question": "Which built-in function returns the memory address of a Python object?",
        "options": ["ref()", "addr()", "id()", "mem()"],
        "answer": 2,
        "explanation": "id() returns the identity (memory address) of an object in CPython."
    },
    {
        "question": "What does *args capture in a function definition?",
        "options": [
            "Keyword arguments as a dict",
            "Positional arguments as a tuple",
            "All arguments as a list",
            "Only integer arguments"
        ],
        "answer": 1,
        "explanation": "*args collects extra positional arguments into a tuple. **kwargs handles keyword arguments."
    },
    {
        "question": "Which data structure guarantees O(1) average-case lookup?",
        "options": ["list", "tuple", "dict", "deque"],
        "answer": 2,
        "explanation": "dict (hash map) uses hashing for O(1) average lookup. Lists require O(n) linear search."
    },
    {
        "question": "What is the output of: bool(0), bool(''), bool([0])?",
        "options": [
            "False, False, False",
            "False, False, True",
            "True, False, True",
            "False, True, False"
        ],
        "answer": 1,
        "explanation": "0 and '' are falsy. [0] is a non-empty list — truthy even if its element is 0."
    },
    {
        "question": "What does list comprehension [x**2 for x in range(5) if x % 2 == 0] produce?",
        "options": ["[0, 4, 16]", "[1, 9, 25]", "[0, 2, 4]", "[0, 1, 4, 9, 16]"],
        "answer": 0,
        "explanation": "Filters even x (0, 2, 4) then squares them: [0, 4, 16]."
    },
    {
        "question": "Which module provides high-precision decimal arithmetic in Python?",
        "options": ["math", "fractions", "decimal", "numbers"],
        "answer": 2,
        "explanation": "The 'decimal' module provides arbitrary-precision fixed-point and floating-point arithmetic."
    },
    {
        "question": "What is the time complexity of Python's list.append()?",
        "options": ["O(n)", "O(log n)", "O(1) amortized", "O(n²)"],
        "answer": 2,
        "explanation": "append() is O(1) amortized. Occasional resizes are O(n) but averaged out over many appends."
    },
    {
        "question": "What does the 'with' statement ensure when opening a file?",
        "options": [
            "The file is read-only",
            "The file is closed automatically via __exit__",
            "The file is loaded into memory",
            "The file is locked for concurrent access"
        ],
        "answer": 1,
        "explanation": "'with' uses the context manager protocol (__enter__/__exit__), ensuring cleanup even on exceptions."
    },
    {
        "question": "Which of these is an immutable sequence type in Python?",
        "options": ["list", "bytearray", "tuple", "dict"],
        "answer": 2,
        "explanation": "Tuples are immutable — you cannot modify them after creation. Lists and bytearrays are mutable."
    },
]

# ── Utilities ─────────────────────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def divider(char='─', width=60):
    print(DIM + char * width + RESET)

def header(score, total_q, current_q):
    divider('═')
    print(f"{BOLD}{Y}  PYTHON QUIZ{RESET}  {DIM}│{RESET}  "
          f"Question {current_q}/{total_q}  {DIM}│{RESET}  "
          f"Score: {G}{score}{RESET}/{current_q - 1}")
    divider('═')

def grade(score, total):
    pct = score / total if total else 0
    if pct >= 0.9:  return f"{G}EXCEPTIONAL{RESET}", G
    if pct >= 0.7:  return f"{Y}PASSING{RESET}", Y
    if pct >= 0.5:  return f"{R}MARGINAL{RESET}", R
    return f"{R}INADEQUATE{RESET}", R

def progress_bar(current, total, width=40):
    filled = int(width * current / total)
    bar = G + '█' * filled + DIM + '░' * (width - filled) + RESET
    return f"[{bar}]"

# ── File loading ──────────────────────────────────────────────────────────────

def load_questions(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"{R}Error:{RESET} File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{R}Error:{RESET} Invalid JSON — {e}")
        sys.exit(1)

    if not isinstance(data, list) or len(data) == 0:
        print(f"{R}Error:{RESET} File must contain a non-empty JSON array.")
        sys.exit(1)

    for i, q in enumerate(data):
        if not isinstance(q.get('question'), str):
            print(f"{R}Error:{RESET} Question {i+1} missing 'question' string.")
            sys.exit(1)
        if not isinstance(q.get('options'), list) or len(q['options']) < 2:
            print(f"{R}Error:{RESET} Question {i+1} must have at least 2 options.")
            sys.exit(1)
        if not isinstance(q.get('answer'), int) or not (0 <= q['answer'] < len(q['options'])):
            print(f"{R}Error:{RESET} Question {i+1} 'answer' must be a valid option index.")
            sys.exit(1)

    print(f"{G}✓{RESET} Loaded {len(data)} questions from {filepath}")
    time.sleep(0.8)
    return data

# ── Auto-advance countdown ────────────────────────────────────────────────────

def auto_advance(seconds=2):
    """Show a countdown then continue — no Enter required."""
    for remaining in range(seconds, 0, -1):
        print(f"\r  {DIM}Next question in {remaining}...{RESET}  ", end='', flush=True)
        time.sleep(1)
    print(f"\r{' ' * 35}\r", end='', flush=True)  # clear the line

# ── Ask a single question ─────────────────────────────────────────────────────

def ask_question(q, q_num, total, score):
    clear()
    header(score, total, q_num)

    # Progress
    print(f"\n  {progress_bar(q_num - 1, total)} {DIM}{q_num-1}/{total}{RESET}\n")

    # Question
    print(f"  {BOLD}{W}{q['question']}{RESET}\n")

    options = q['options']
    for i, opt in enumerate(options):
        print(f"  {Y}{KEYS[i]}{RESET}  {opt}")

    print()
    divider()

    # Input loop
    valid = set(KEYS[:len(options)].lower()) | set(KEYS[:len(options)])
    while True:
        raw = input(f"  {C}Answer [{KEYS[:len(options)]}]:{RESET} ").strip()
        if raw.upper() in set(KEYS[:len(options)]):
            break
        print(f"  {R}Enter one of: {KEYS[:len(options)]}{RESET}")

    chosen = KEYS.index(raw.upper())
    correct = chosen == q['answer']

    # Feedback
    print()
    if correct:
        print(f"  {G}✓ CORRECT{RESET}")
    else:
        print(f"  {R}✗ WRONG  — correct answer: {KEYS[q['answer']]}. {options[q['answer']]}{RESET}")

    if q.get('explanation'):
        print(f"\n  {DIM}{q['explanation']}{RESET}")

    print()
    auto_advance(seconds=2)

    return correct, chosen

# ── Results screen ────────────────────────────────────────────────────────────

def show_results(history, questions):
    clear()
    total = len(questions)
    score = sum(1 for h in history if h['correct'])
    label, color = grade(score, total)

    divider('═')
    print(f"{BOLD}{Y}  RESULTS{RESET}")
    divider('═')
    print(f"\n  Final score:  {color}{score} / {total}{RESET}  →  {label}")
    print(f"\n  {progress_bar(score, total)} {int(score/total*100)}%\n")
    divider()

    print(f"\n  {BOLD}QUESTION REVIEW{RESET}\n")

    for i, h in enumerate(history):
        q = h['q']
        icon = f"{G}✓{RESET}" if h['correct'] else f"{R}✗{RESET}"
        print(f"  {icon} {i+1}. {W}{q['question']}{RESET}")

        if not h['correct']:
            print(f"      {R}You:     {q['options'][h['selected']]}{RESET}")
            print(f"      {G}Correct: {q['options'][q['answer']]}{RESET}")
        if q.get('explanation'):
            print(f"      {DIM}{q['explanation']}{RESET}")
        print()

    divider('═')

# ── Main game loop ────────────────────────────────────────────────────────────

def run_game(questions):
    qs = random.sample(questions, len(questions))  # shuffle
    score = 0
    history = []

    for i, q in enumerate(qs, 1):
        correct, chosen = ask_question(q, i, len(qs), score)
        if correct:
            score += 1
        history.append({'q': q, 'correct': correct, 'selected': chosen})

    show_results(history, qs)

    print(f"\n  Play again? {Y}[y/n]{RESET} ", end='')
    return input().strip().lower() == 'y'

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        questions = load_questions(sys.argv[1])
    else:
        questions = SAMPLE_QUESTIONS

    clear()
    divider('═')
    print(f"{BOLD}{Y}  PYTHON QUIZ GAME{RESET}")
    divider('═')
    src = sys.argv[1] if len(sys.argv) > 1 else "built-in sample"
    print(f"\n  Source:     {C}{src}{RESET}")
    print(f"  Questions:  {len(questions)}")
    print(f"  Order:      randomized each round")
    print(f"\n  {DIM}No hints. No retries per question.{RESET}\n")
    divider()
    input(f"\n  {C}Press Enter to start...{RESET}")

    while True:
        if not run_game(questions):
            print(f"\n  {DIM}Session ended.{RESET}\n")
            break

if __name__ == '__main__':
    main()