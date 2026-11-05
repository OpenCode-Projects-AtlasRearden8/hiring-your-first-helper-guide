#!/usr/bin/env python3
"""Verification for the Hiring Your First Helper Guide.

Runs the build fresh, then checks that the generated site is complete and
well-formed. Exit code 0 = all checks pass; 1 = something failed.
Usage:  python3 test_build.py
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

EXPECTED_PAGES = [
    "index.html",
    "00-start-here.html",
    "01-should-you-hire.html",
    "02-writing-the-posting.html",
    "03-fair-trial-projects.html",
    "04-paying-people-plainly.html",
    "05-records-you-keep.html",
    "06-onboarding.html",
    "07-offboarding.html",
    "08-keeping-your-head-above-water.html",
    "interview-scorecard.html",
    "first-week-onboarding-sheet.html",
    "glossary.html",
]

REQUIRED_SNIPPETS = {
    "index.html": [
        "Hiring Your First Helper</h1>",
        "Education only, never legal or tax advice",
        "Asdale Dynamics, LLC",
    ],
    "00-start-here.html": ["do the boring next thing"],
    "01-should-you-hire.html": ["eliminate it", "Contractor vs. employee"],
    "02-writing-the-posting.html": [
        "Always put the pay in the posting",
        "Part-Time Podcast Support",
    ],
    "03-fair-trial-projects.html": ["Rule: if it looks like work, it is work. Pay for it."],
    "04-paying-people-plainly.html": ["W-9", "1099-NEC", "Pay people on the day you said you'd pay"],
    "05-records-you-keep.html": ["payment log", "Working agreement"],
    "06-onboarding.html": ["info-flooding", "Stage 1", "Stage 2", "Stage 3"],
    "07-offboarding.html": ["tool-access checklist", "rotate" ],
    "08-keeping-your-head-above-water.md-placeholder": [],
    "interview-scorecard.html": ["28+ and no gut flags", "Total:"],
    "first-week-onboarding-sheet.html": ["Monday", "Friday", "retro question"],
    "glossary.html": ["1099-NEC", "scope", "Deliverable"],
}

failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    if cond:
        print("  PASS  %s" % msg)
    else:
        failures.append(msg)
        print("  FAIL  %s" % msg)


def main() -> int:
    print("== Running build from scratch ==")
    if SITE.is_dir():
        shutil.rmtree(SITE)
    build = subprocess.run(
        [sys.executable, "build.py"], cwd=ROOT, capture_output=True, text=True
    )
    check(build.returncode == 0, "build.py exits 0 (stderr: %r)" % build.stderr[-400:])
    if build.returncode != 0:
        return 1
    print("  build output: %s" % build.stdout.strip())

    print("== All expected pages exist ==")
    for page in EXPECTED_PAGES:
        check((SITE / page).is_file(), "%s exists and is a file" % page)

    print("== Page content checks ==")
    for page, snippets in REQUIRED_SNIPPETS.items():
        if page.endswith("-placeholder"):
            continue
        path = SITE / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            check(snippet in text, "%s contains %r" % (page, snippet[:60]))

    print("== HTML sanity checks ==")
    for page in EXPECTED_PAGES:
        path = SITE / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        check(text.startswith("<!DOCTYPE html>"), "%s starts with doctype" % page)
        check(
            text.count("<main>") == 1 and text.count("</main>") == 1,
            "%s has exactly one <main>" % page,
        )
        check("utf-8" in text, "%s declares utf-8" % page)
        check("Asdale Dynamics" in text, "%s credits Asdale Dynamics, LLC" % page)
        check(
            "http://" not in text.replace("http://www.w3.org", "") and "https://" not in text,
            "%s has no external network references (local-first)" % page,
        )

    print("== Cross-page integrity ==")
    index = (SITE / "index.html").read_text(encoding="utf-8")
    for page in EXPECTED_PAGES[1:]:
        check(page in index, "index links to %s" % page)
    for page in EXPECTED_PAGES:
        path = SITE / page
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for cls, name in [('class="toc"', "top nav"), ('class="pn"', "prev/next row")]:
            has = cls in text
            if page == "index.html" and name == "prev/next row":
                check(True, "index has no prev/next (by design)")
            else:
                check(has, "%s has %s" % (page, name))
    # prev/next chain actually navigates somewhere
    p3 = (SITE / "03-fair-trial-projects.html").read_text(encoding="utf-8")
    check('href="02-writing-the-posting.html"' in p3, "ch3 links back to ch2")
    check('href="04-paying-people-plainly.html"' in p3, "ch3 links forward to ch4")

    print("== Repo honesty checks ==")
    check((ROOT / "LICENSE").is_file(), "LICENSE exists")
    if (ROOT / "LICENSE").is_file():
        lic = (ROOT / "LICENSE").read_text(encoding="utf-8")
        check(lic.startswith("MIT License"), "LICENSE is MIT")
        check(
            "Copyright (c) 2026 Asdale Dynamics, LLC" in lic,
            "LICENSE copyright line is exact",
        )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("Asdale Dynamics, LLC" in readme, "README credits Asdale Dynamics, LLC")

    print("=" * 50)
    if failures:
        print("FAILED: %d check(s):" % len(failures))
        for f in failures:
            print(" - %s" % f)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
