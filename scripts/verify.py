#!/usr/bin/env python3
"""Check that this repo is in the state it is supposed to be in.

Run it:
    python3 scripts/verify.py

It runs six checks and prints one line each. A failing check tells you three
things: what it expected, what it actually found, and what to do about it.
Exit code is 0 only when everything passes, so this also works in CI.

If a check goes red and you do not know what to do, paste the whole output into
Claude and say "verify.py is failing". That is enough to start from.

This file is yours. If you deliberately add a new file to the repo root, add it
to EXPECTED_ROOT below and the `files` check will stop complaining about it.
"""

import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BRANCH = "hello-claude-101"

# The counting fixture and its answers were worked out by hand before the code
# was written, and they are duplicated in scripts/test_wordcount.py on purpose.
# If someone changes the counting rules, both places have to be updated
# deliberately, which is the point.
FIXTURE = "hello world\nsecond line here\nthird\n"
FIXTURE_EXPECTED = {"lines": 3, "words": 6, "chars": 35}

# The content of the repo's original placeholder file, recorded before it was
# renamed, so we can prove the rename did not quietly alter it.
ORIGINAL_CONTENT = "just 1 file\n"
ORIGINAL_NAME = "hello world"

EXPECTED_FILES = [
    ".gitignore",
    "ACCEPTANCE.md",
    "README.md",
    "hello-world.txt",
    "scripts/test_wordcount.py",
    "scripts/verify.py",
    "scripts/wordcount.py",
    "site/index.html",
]

EXPECTED_ROOT = {
    ".gitignore",
    "ACCEPTANCE.md",
    "README.md",
    "hello-world.txt",
    "scripts",
    "site",
}

PAGE = "site/index.html"
MIN_TESTS = 3

# Tags that are never optionally closed, so an imbalance is always a real bug.
BALANCED_TAGS = {
    "html", "head", "body", "style", "script", "div", "section", "header",
    "footer", "main", "table", "thead", "tbody", "ul", "ol",
}

# Element/attribute pairs that make the browser go and fetch something.
# <a href> is navigation, not a fetch, so it is deliberately not in here.
RESOURCE_ATTRS = {
    "script": "src",
    "link": "href",
    "img": "src",
    "iframe": "src",
    "source": "src",
    "video": "src",
    "audio": "src",
    "embed": "src",
    "track": "src",
    "object": "data",
}


class Result:
    def __init__(self, name, ok, summary, expected=None, found=None, fix=None):
        self.name = name
        self.ok = ok
        self.summary = summary
        self.expected = expected
        self.found = found
        self.fix = fix


def repo_path(*parts):
    return os.path.join(REPO, *parts)


def run(args, **kwargs):
    return subprocess.run(
        args,
        cwd=REPO,
        capture_output=True,
        text=True,
        **kwargs,
    )


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def _git_visible_root():
    """Top-level names that git either tracks or would track.

    This asks git rather than the filesystem on purpose. Anything .gitignore
    covers is invisible here, so local-only files such as __pycache__ or
    .claude/settings.local.json do not trip the check. The question being
    answered is "did something unexpected get added to the repo", and a file
    git will never commit was never added to the repo.
    """
    names = set()
    for args in (
        ["git", "ls-files"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        for line in run(args).stdout.splitlines():
            line = line.strip()
            if line:
                names.add(line.split("/", 1)[0])
    return names


def check_files():
    missing = [p for p in EXPECTED_FILES if not os.path.isfile(repo_path(p))]
    if missing:
        return Result(
            "files",
            False,
            f"{len(missing)} of {len(EXPECTED_FILES)} expected files missing",
            expected=f"all {len(EXPECTED_FILES)} expected files present",
            found="missing: " + ", ".join(missing),
            fix="restore the missing file(s), or ask Claude to recreate them",
        )

    extra = sorted(_git_visible_root() - EXPECTED_ROOT)
    if extra:
        return Result(
            "files",
            False,
            f"{len(extra)} unexpected item(s) in the repo root",
            expected="nothing in the repo root beyond the known set",
            found="unexpected: " + ", ".join(extra),
            fix=(
                "if you added it on purpose, add its name to EXPECTED_ROOT in "
                "scripts/verify.py; otherwise delete it"
            ),
        )

    return Result(
        "files", True, f"all {len(EXPECTED_FILES)} expected files present"
    )


def check_rename():
    new = repo_path("hello-world.txt")
    old = repo_path(ORIGINAL_NAME)

    if not os.path.isfile(new):
        return Result(
            "rename",
            False,
            "hello-world.txt is missing",
            expected="hello-world.txt exists",
            found="no such file",
            fix="run `git mv \"hello world\" hello-world.txt`",
        )

    if os.path.exists(old):
        return Result(
            "rename",
            False,
            "the old filename is still there",
            expected=f"'{ORIGINAL_NAME}' no longer exists",
            found=f"'{ORIGINAL_NAME}' is still present",
            fix=f"delete the leftover: `git rm \"{ORIGINAL_NAME}\"`",
        )

    with open(new, "r", encoding="utf-8") as handle:
        content = handle.read()

    if content != ORIGINAL_CONTENT:
        return Result(
            "rename",
            False,
            "content changed during the rename",
            expected=f"content is exactly {ORIGINAL_CONTENT!r}",
            found=f"content is {content!r}",
            fix=(
                "a rename should not touch content; restore it with "
                "`git checkout hello-world.txt` or write the original text back"
            ),
        )

    return Result(
        "rename", True, "renamed, old name gone, content byte-identical"
    )


def check_tests():
    proc = run([sys.executable, "-m", "unittest", "discover", "-s", "scripts"])
    output = (proc.stdout or "") + (proc.stderr or "")

    match = re.search(r"Ran (\d+) test", output)
    ran = int(match.group(1)) if match else 0

    if proc.returncode != 0:
        failing = re.findall(r"^(?:FAIL|ERROR): (\S+)", output, re.MULTILINE)
        return Result(
            "tests",
            False,
            f"test run failed ({ran} ran)",
            expected="every test passes",
            found=(
                "failing: " + ", ".join(failing)
                if failing
                else output.strip().splitlines()[-1] if output.strip() else "no output"
            ),
            fix=(
                "run `python3 -m unittest discover -s scripts -v` and read the "
                "traceback, or tell Claude which test is failing"
            ),
        )

    if ran < MIN_TESTS:
        return Result(
            "tests",
            False,
            f"only {ran} test(s) ran",
            expected=f"at least {MIN_TESTS} tests run",
            found=f"{ran} ran",
            fix=(
                "a passing run with almost no tests in it proves very little; "
                "check scripts/test_wordcount.py still has its tests"
            ),
        )

    return Result("tests", True, f"{ran} tests passed")


def _parse_counts(text):
    counts = {}
    for line in text.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            try:
                counts[key.strip()] = int(value.strip())
            except ValueError:
                pass
    return counts


def check_cli():
    script = repo_path("scripts", "wordcount.py")
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    )
    try:
        handle.write(FIXTURE)
        handle.close()

        from_file = run([sys.executable, script, handle.name])
        if from_file.returncode != 0:
            return Result(
                "cli",
                False,
                "wordcount.py exited with an error",
                expected="exit code 0",
                found=(from_file.stderr or "no stderr").strip(),
                fix="run `python3 scripts/wordcount.py README.md` and read the error",
            )

        counts = _parse_counts(from_file.stdout)
        if counts != FIXTURE_EXPECTED:
            return Result(
                "cli",
                False,
                "wrong counts for the fixture",
                expected=str(FIXTURE_EXPECTED),
                found=str(counts),
                fix=(
                    "the counting rules in scripts/wordcount.py changed; either "
                    "fix count_text or, if the new rule is intentional, update "
                    "FIXTURE_EXPECTED here and in scripts/test_wordcount.py"
                ),
            )

        from_stdin = run([sys.executable, script], input=FIXTURE)
        stdin_counts = _parse_counts(from_stdin.stdout)
        if stdin_counts != counts:
            return Result(
                "cli",
                False,
                "reading a file and reading stdin disagree",
                expected=f"stdin gives the same answer as the file: {counts}",
                found=str(stdin_counts),
                fix="check the two input paths in main() in scripts/wordcount.py",
            )
    finally:
        os.unlink(handle.name)

    return Result(
        "cli",
        True,
        "fixture counts correct, file and stdin agree",
    )


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.opened = {}
        self.closed = {}
        self.has_viewport = False
        self.title = ""
        self._in_title = False
        self.external = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag in BALANCED_TAGS:
            self.opened[tag] = self.opened.get(tag, 0) + 1

        if tag == "title":
            self._in_title = True

        if tag == "meta" and (attrs.get("name") or "").lower() == "viewport":
            self.has_viewport = True

        attr = RESOURCE_ATTRS.get(tag)
        if attr:
            value = (attrs.get(attr) or "").strip()
            if value.startswith(("http://", "https://", "//")):
                self.external.append(f"<{tag} {attr}={value}>")

    def handle_endtag(self, tag):
        if tag in BALANCED_TAGS:
            self.closed[tag] = self.closed.get(tag, 0) + 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def check_html():
    path = repo_path(PAGE)
    if not os.path.isfile(path):
        return Result(
            "html",
            False,
            f"{PAGE} is missing",
            expected=f"{PAGE} exists",
            found="no such file",
            fix="ask Claude to recreate the page",
        )

    with open(path, "r", encoding="utf-8") as handle:
        markup = handle.read()

    parser = PageParser()
    try:
        parser.feed(markup)
        parser.close()
    except Exception as error:  # noqa: BLE001 - any parse blow-up is a failure
        return Result(
            "html",
            False,
            "the page could not be parsed",
            expected="valid HTML",
            found=f"{type(error).__name__}: {error}",
            fix="ask Claude to look at site/index.html",
        )

    unbalanced = []
    for tag in sorted(set(parser.opened) | set(parser.closed)):
        opened = parser.opened.get(tag, 0)
        closed = parser.closed.get(tag, 0)
        if opened != closed:
            unbalanced.append(f"{tag}: {opened} open vs {closed} close")

    if unbalanced:
        return Result(
            "html",
            False,
            "unbalanced tags",
            expected="every structural tag is closed exactly once",
            found="; ".join(unbalanced),
            fix="usually a forgotten closing tag; ask Claude to fix site/index.html",
        )

    if not parser.title.strip():
        return Result(
            "html",
            False,
            "no page title",
            expected="a non-empty <title>",
            found="missing or empty",
            fix="add a <title> inside <head>",
        )

    if not parser.has_viewport:
        return Result(
            "html",
            False,
            "no viewport meta tag",
            expected='<meta name="viewport" ...> so the page works on a phone',
            found="missing",
            fix='add <meta name="viewport" content="width=device-width, initial-scale=1">',
        )

    if parser.external:
        return Result(
            "html",
            False,
            f"{len(parser.external)} external resource(s)",
            expected="no external fetches, so the page works offline",
            found=", ".join(parser.external),
            fix=(
                "inline the resource, or embed it as a data: URI, so the single "
                "file stays self-contained"
            ),
        )

    return Result(
        "html",
        True,
        f'"{parser.title.strip()}", self-contained, phone-ready',
    )


def check_git():
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    if branch != BRANCH:
        return Result(
            "git",
            False,
            f"on branch {branch}",
            expected=f"on branch {BRANCH}",
            found=f"on branch {branch}",
            fix=f"run `git checkout {BRANCH}`",
        )

    dirty = run(["git", "status", "--porcelain"]).stdout.strip()
    if dirty:
        return Result(
            "git",
            False,
            "uncommitted changes",
            expected="working tree clean, everything committed",
            found=dirty.replace("\n", " | "),
            fix="run `git status` to see them, then commit or discard them",
        )

    remote_ref = f"refs/remotes/origin/{BRANCH}"
    remote = run(["git", "rev-parse", "--verify", "--quiet", remote_ref])
    if remote.returncode != 0:
        return Result(
            "git",
            False,
            "no local record of the remote branch",
            expected=f"origin/{BRANCH} is known locally",
            found=f"{remote_ref} not found",
            fix=f"run `git fetch origin {BRANCH}`",
        )

    local_head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    remote_head = remote.stdout.strip()
    if local_head != remote_head:
        return Result(
            "git",
            False,
            "local and GitHub disagree",
            expected=f"HEAD matches origin/{BRANCH}",
            found=f"local {local_head[:9]} vs remote {remote_head[:9]}",
            fix=(
                f"run `git push -u origin {BRANCH}` if you are ahead, or "
                f"`git pull origin {BRANCH}` if you are behind"
            ),
        )

    return Result(
        "git",
        True,
        f"on {BRANCH}, clean, in sync with GitHub ({local_head[:9]})",
    )


CHECKS = [
    check_files,
    check_rename,
    check_tests,
    check_cli,
    check_html,
    check_git,
]


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def main():
    colour = sys.stdout.isatty()
    green = "\033[32m" if colour else ""
    red = "\033[31m" if colour else ""
    dim = "\033[2m" if colour else ""
    off = "\033[0m" if colour else ""

    results = [check() for check in CHECKS]

    print()
    for result in results:
        mark = f"{green}PASS{off}" if result.ok else f"{red}FAIL{off}"
        print(f"  {mark}  {result.name:<8} {result.summary}")
        if not result.ok:
            for label, value in (
                ("expected", result.expected),
                ("found", result.found),
                ("fix", result.fix),
            ):
                if value:
                    print(f"        {dim}{label + ':':<10}{off}{value}")
            print()

    failed = [r for r in results if not r.ok]
    print()
    if failed:
        names = ", ".join(r.name for r in failed)
        print(f"  {red}{len(failed)} of {len(results)} checks failed{off}: {names}")
        print("  Paste this whole output into Claude if you want help with it.")
        print()
        return 1

    print(f"  {green}All {len(results)} checks passed.{off}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
