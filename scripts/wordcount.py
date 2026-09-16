#!/usr/bin/env python3
"""A mini `wc`: count the lines, words and characters in some text.

The counting logic lives in `count_text`, which is a plain function that takes a
string and returns a dict. The command line handling lives in `main`. They are kept
apart on purpose: it means the interesting part can be tested directly, without
having to fake a terminal or a file. See scripts/test_wordcount.py.

Usage:
    python3 scripts/wordcount.py README.md
    cat README.md | python3 scripts/wordcount.py
"""

import argparse
import sys


def count_text(text):
    """Return {'lines', 'words', 'chars'} for a string.

    lines: a final line without a trailing newline still counts, so "abc" is 1 line
           and "" is 0 lines.
    words: runs of whitespace separate words, and leading or trailing whitespace is
           ignored, so "  a  b  " is 2 words.
    chars: every character, newlines included.
    """
    lines = text.count("\n")
    if text and not text.endswith("\n"):
        lines += 1

    return {
        "lines": lines,
        "words": len(text.split()),
        "chars": len(text),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Count lines, words and characters."
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="file to read; omit it to read from standard input",
    )
    args = parser.parse_args(argv)

    # `is not None`, not a truthiness test: argparse sets path to None when the
    # argument is omitted, but to "" when someone passes an empty string. A
    # truthiness test treats those the same and silently waits on stdin, which
    # looks exactly like a hang.
    if args.path is not None:
        try:
            with open(args.path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError) as error:
            # UnicodeDecodeError subclasses ValueError, not OSError, so it needs
            # naming explicitly or a binary file crashes with a raw traceback.
            print(f"wordcount: {args.path!r}: {error}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    counts = count_text(text)
    for name in ("lines", "words", "chars"):
        print(f"{name}: {counts[name]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
