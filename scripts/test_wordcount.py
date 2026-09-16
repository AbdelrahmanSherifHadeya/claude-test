#!/usr/bin/env python3
"""Tests for wordcount.count_text.

Run them with:
    python3 -m unittest discover -s scripts -v

These use `unittest`, which ships with Python, so there is nothing to install.
Each test states an expected answer that was worked out by hand first. That order
matters: if you write the test by running the code and copying whatever it printed,
the test only proves the code does what it does, which is not the same as proving it
does what it should.
"""

import unittest

from wordcount import count_text

# Worked out by hand:
#   lines  3  ("hello world", "second line here", "third")
#   words  6  (hello, world, second, line, here, third)
#   chars 35  (12 + 17 + 6, counting each newline)
FIXTURE = "hello world\nsecond line here\nthird\n"


class CountTextTests(unittest.TestCase):
    def test_fixture(self):
        self.assertEqual(
            count_text(FIXTURE),
            {"lines": 3, "words": 6, "chars": 35},
        )

    def test_empty_input(self):
        self.assertEqual(
            count_text(""),
            {"lines": 0, "words": 0, "chars": 0},
        )

    def test_final_line_without_newline_still_counts(self):
        self.assertEqual(count_text("abc def")["lines"], 1)
        self.assertEqual(count_text("abc def")["words"], 2)
        self.assertEqual(count_text("abc def")["chars"], 7)

    def test_surrounding_whitespace_is_not_a_word(self):
        counts = count_text("  hello  \n\n")
        self.assertEqual(counts["words"], 1)
        self.assertEqual(counts["lines"], 2)
        self.assertEqual(counts["chars"], 11)

    def test_a_blank_line_is_still_a_line(self):
        self.assertEqual(count_text("a\n\nb\n")["lines"], 3)


if __name__ == "__main__":
    unittest.main()
