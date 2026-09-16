# Acceptance checklist

`scripts/verify.py` covers everything a machine can decide. This file covers the rest.

Work through it yourself. Every item is a yes or no question, and every item tells you
what to do if the answer is no. "I'm not sure" counts as a no.

## Run this first

```bash
python3 scripts/verify.py
```

Expected: six checks, all green, and the line `All 6 checks passed.`

If anything is red, stop here. Read the `fix:` line under the failing check, or paste the
whole output into Claude and say "verify.py is failing". Do not go through the rest of
this list until it is green, because a red check usually explains whatever else looks off.

## Then judge these yourself

**1. Does the cheat sheet actually look good on your phone?**

Open `site/index.html` on a phone, or narrow your browser window to about 390px wide.

Looking for: nothing overflows sideways, nothing overlaps, text is comfortably readable
without pinching, and the two "Cloud / Local" panels stack instead of squashing.

If no: tell Claude what specifically looks wrong and at what width. "The table runs off
the edge at phone width" is a complete bug report.

**2. Does the README make sense to you specifically?**

You started using this tool today. That is the audience.

Looking for: you could hand this repo to someone else and they would know what to run.

If no: name the sentence that lost you. A README you cannot follow is a broken README,
and that is a real defect, not a preference.

**3. Does `git log --oneline` read as a sequence of understandable steps?**

Looking for: five commits total. The first, `Create hello world`, was already there
before this work started; the four above it are new. Each of the four should tell you
what changed without having to open the diff.

If no: say which message is vague.

**4. Is there anything in the diff you do not understand?**

```bash
git fetch origin main
git diff origin/main...HEAD
```

The fetch is needed first: `main` exists on GitHub but this clone has never downloaded
it, so `git diff main...` on its own fails with `unknown revision`.

Looking for: nothing that makes you think "why is that there?"

If no, meaning something is unclear: ask about that exact line. An unexplained change is
a gap in the explanation, not a gap in you. This is the single most useful habit to build
early, because it is the thing that stops you from merging work you cannot vouch for.

**5. Does the verification script actually catch a problem?**

Do not take the green result on trust. Break something on purpose:

```bash
echo "broken" >> hello-world.txt
python3 scripts/verify.py
```

Expected: **two** checks go red, not one. `rename` reports that the content changed, and
`git` reports an uncommitted change, because appending to a tracked file also dirties the
working tree. Exit code 1.

Then put it back:

```bash
git checkout hello-world.txt
python3 scripts/verify.py
```

Expected: green again.

If the script stayed green while the repo was broken, the script is worthless and that is
the most important bug on this page. Say so.

## The point of all this

A green checklist is not the goal. The goal is that you never have to take "it works" on
somebody's word, mine included. Anything that claims to be done should come with
something you can run that disagrees with it when it is wrong.
