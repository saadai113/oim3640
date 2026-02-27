#!/usr/bin/env python3
"""
quiz_game.py — CLI trivia game with score tracking and feedback.

Usage:
    python quiz_game.py

Questions are loaded from questions.json in the same directory as this script.

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

QUESTIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")

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
    qs = random.sample(questions, 10)  # pick 10 random questions from the pool
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
    questions = load_questions(QUESTIONS_FILE)

    clear()
    divider('═')
    print(f"{BOLD}{Y}  PYTHON QUIZ GAME{RESET}")
    divider('═')
    print(f"\n  Source:     {C}questions.json{RESET}")
    print(f"  Questions:  {len(questions)}; 10 randomly selected")
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