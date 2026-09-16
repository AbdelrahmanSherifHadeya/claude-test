# claude-test

A sandbox for learning Claude Code. Nothing here is precious, so break things freely.

This repo was set up during a first Claude Code session. Every file below exists to
demonstrate one specific thing, so you can look at it and see how a piece of the workflow
fits together.

## What is in here

| Path | What it is | Why it exists |
| --- | --- | --- |
| `site/index.html` | A Claude Code cheat sheet you can open in a browser | Shows Claude building something visual, with no build step or dependencies |
| `scripts/wordcount.py` | A mini `wc`: counts lines, words and characters | Shows real code, with the logic split from the command line wrapper so it can be tested |
| `scripts/test_wordcount.py` | Tests for the above | Shows that "it works" is something you prove, not something you claim |
| `scripts/verify.py` | Checks this whole repo and prints PASS or FAIL per item | Lets you audit the result yourself instead of trusting a summary |
| `ACCEPTANCE.md` | A short human checklist | Covers the things a script cannot judge, like whether the page actually looks good |
| `hello-world.txt` | The original placeholder file | Kept so the rename shows up in the git history |
| `.gitignore` | A list of files git should ignore | Keeps caches and editor droppings out of the repo |

## Check that everything is sound

```bash
python3 scripts/verify.py
```

That is the important command in this repo. It runs six checks and prints a line for each
one. If a check fails it tells you what it expected, what it actually found, and what to
do about it. It exits with code 0 only when everything passes.

Run it any time you or Claude change something here. If it goes red, paste the output back
into Claude and say "verify.py is failing", and that is enough to get started on a fix.

## Run the other pieces

```bash
# Run the tests
python3 -m unittest discover -s scripts -v

# Count what is in this README
python3 scripts/wordcount.py README.md

# Same thing, reading from a pipe instead of a file
cat README.md | python3 scripts/wordcount.py
```

To see the cheat sheet, open `site/index.html` in any browser. It is a single file with no
dependencies, so it works offline and works if you just double click it.

## How the git side of this works

If you have never used git, here is the whole idea in four sentences.

Git keeps a history of your project. A **commit** is one saved point in that history, with
a message explaining what changed. A **branch** is a parallel line of history, so you can
work without disturbing the main one. **Pushing** uploads your commits to GitHub so they
exist somewhere other than your machine.

This work lives on the branch `hello-claude-101`, not on `main`. That is deliberate: it
means `main` stays untouched, and you can look at the branch on GitHub and decide whether
you want to merge it in.

Useful commands:

```bash
git status          # what have I changed but not saved yet?
git log --oneline   # what is the history?
git diff            # show me exactly what changed, line by line
git branch          # which branch am I on?
```

## Things to try next

Ask Claude any of these in plain English. There is no special syntax.

- "Explain `scripts/verify.py` to me line by line, I don't know Python"
- "Add a `--json` flag to wordcount.py so it can print machine readable output"
- "The cheat sheet page needs a section about X, add it"
- "Break something in wordcount.py on purpose so I can watch verify.py catch it"
- "What would this repo need before it was a real project?"
- "Set up GitHub Actions so verify.py runs automatically on every push"

Two Claude Code features worth knowing early:

- **Plan mode** makes Claude research and propose a plan, and wait for your approval
  before touching anything. Good when you are not sure what you are asking for yet.
- **`/code-review`** reads the changes on your branch and looks for problems. Useful as a
  second opinion before you merge anything.
