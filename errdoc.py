#!/usr/bin/env python3
"""errdoc - paste an error, get a plain-English diagnosis and a fix.

Powered by the BharatCode model API (Qwen). Zero dependencies: Python 3.8+ only.

Usage:
    python3 errdoc.py "TypeError: cannot read property 'map' of undefined"
    python3 errdoc.py --file crash.log
    python3 errdoc.py --file crash.log --code app.py
    python3 errdoc.py --hint "IndexError: list index out of range"
    python3 errdoc.py            # reads the error from stdin

Set your key first:
    export BHARATCODE_API_KEY=bc_live_...
Get a free student key at https://www.bharatcode.ai/account
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_URL = "https://bharatcode.ai/api/model/v1/chat/completions"
MODEL = "qwen-3.8-27b"
MAX_ERROR_CHARS = 12000
MAX_CODE_CHARS = 8000

SYSTEM_PROMPT = """You are errdoc, a debugging assistant for students and working developers.
The user gives you an error message or stack trace, and sometimes the code that produced it.

Answer in this exact structure:

## What happened
One or two sentences, plain English, no jargon.

## Why it happened
The actual root cause, not a restatement of the error. Reference the exact line, variable or call when you can.

## Fix
Concrete corrected code or steps. If there are two reasonable fixes, show the simplest first.

## Watch out
One common way this same bug comes back, or a related edge case. One or two sentences.

Rules:
- Be specific to THIS error. Never give generic "check your syntax" advice.
- If the error text is too vague to diagnose, say exactly what extra output to capture, and stop.
- Keep the whole answer under 300 words.
"""

HINT_PROMPT = """You are errdoc in hint mode, a debugging tutor for students.
The user gives you an error message or stack trace, and sometimes the code that produced it.

Do NOT give the fix. Instead:
1. Say in one sentence which part of the error message matters most.
2. Ask one guiding question that leads them toward the root cause.
3. Name the concept they should look up (for example "off-by-one indexing" or "mutable default arguments").

Keep it under 80 words. Encouraging, never condescending.
"""


def load_key():
    key = os.environ.get("BHARATCODE_API_KEY", "").strip()
    if key:
        return key
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("BHARATCODE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def read_error(args):
    if args.error:
        return " ".join(args.error)
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError as exc:
            sys.exit(f"errdoc: cannot read {args.file}: {exc}")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.exit("errdoc: give an error to diagnose. Try: python3 errdoc.py \"<error text>\" or pipe a log in. --help for options.")


def read_code(path):
    if not path:
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as exc:
        sys.exit(f"errdoc: cannot read {path}: {exc}")


def diagnose(key, error_text, code_text, hint=False):
    parts = ["Here is the error or stack trace:\n```\n" + error_text[:MAX_ERROR_CHARS] + "\n```"]
    if code_text:
        parts.append("Here is the code that produced it:\n```\n" + code_text[:MAX_CODE_CHARS] + "\n```")
    payload = {
        "model": MODEL,
        "store": False,
        "messages": [
            {"role": "system", "content": HINT_PROMPT if hint else SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(parts)},
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
            msg = detail.get("error", {}).get("message", str(exc))
        except Exception:
            msg = str(exc)
        sys.exit(f"errdoc: API error {exc.code}: {msg}")
    except urllib.error.URLError as exc:
        sys.exit(f"errdoc: cannot reach the BharatCode API: {exc.reason}")
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        sys.exit("errdoc: unexpected API response: " + json.dumps(data)[:400])


def main():
    parser = argparse.ArgumentParser(
        prog="errdoc",
        description="Paste an error, get a plain-English diagnosis and a fix. Powered by the BharatCode API.",
    )
    parser.add_argument("error", nargs="*", help="the error text (or pipe it in / use --file)")
    parser.add_argument("--file", "-f", help="read the error from a log file")
    parser.add_argument("--code", "-c", help="source file that produced the error, for context")
    parser.add_argument("--hint", action="store_true", help="tutor mode: a nudge instead of the answer")
    args = parser.parse_args()

    key = load_key()
    if not key:
        sys.exit(
            "errdoc: no API key found.\n"
            "  export BHARATCODE_API_KEY=bc_live_...\n"
            "Get a key (free for verified students) at https://www.bharatcode.ai/account"
        )

    error_text = read_error(args).strip()
    if not error_text:
        sys.exit("errdoc: the error text is empty.")
    code_text = read_code(args.code)

    print(diagnose(key, error_text, code_text, hint=args.hint))


if __name__ == "__main__":
    main()
