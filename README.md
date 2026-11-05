# Hiring Your First Helper Guide

A plain-English, beginner-friendly small-business manual for hiring your first
contractor or part-timer — written and published by **Asdale Dynamics, LLC**.
Step by step, never condescending, with zero jargon walls.

> **Education only, never legal or tax advice.** This guide explains concepts in
> plain language so you can have smarter conversations with professionals (an
> accountant, a lawyer, your state's business office). It does not replace them.

## Who this is for

You run (or are starting) a tiny business and you've hit the moment where one
more pair of hands would genuinely help — but every search result seems to assume
you have an HR department. This manual is for the person who *is* the HR
department.

Written in the same spirit as Dylan Asdale's *The Massive AI Manual*: like a
friend explaining it over coffee.

## What's inside (`docs/`)

| Chapter | File | What it covers |
|---|---|---|
| 0 | `00-start-here.md` | How to use this guide, plus a "you're drowning in guidance" survival note |
| 1 | `01-should-you-hire.md` | Deciding whether to hire at all (and what kind of help fits) |
| 2 | `02-writing-the-posting.md` | Writing a job posting that doesn't mislead |
| 3 | `03-fair-trial-projects.md` | Paid trial projects that respect both sides |
| 4 | `04-paying-people-plainly.md` | Rate vs. flat fee vs. hourly, paying on time, clean records |
| 5 | `05-records-you-keep.md` | A simple, boring, effective record-keeping habit |
| 6 | `06-onboarding.md` | First-week onboarding without info-flooding |
| 7 | `07-offboarding.md` | Ending work kindly and cleaning up tool access |
| 8 | `08-keeping-your-head-above-water.md` | Anti-overwhelm guidance ("do the boring next thing") |
| Extras | `interview-scorecard.md` | One page you can actually use during an interview |
| Extras | `first-week-onboarding-sheet.md` | A fill-in first-week plan for your helper |
| Extras | `glossary.md` | Plain-English definitions (W-9/1099, invoice, scope, and friends) |

## The website

`build.py` converts `docs/*.md` into a small, self-contained static site in
`site/` (one HTML file per chapter, plus an `index.html` with a table of
contents). **Local-first**: no network calls, no CDNs, no tracking. Built with
Python standard library only — no dependencies to install.

### How to run it

```bash
python3 build.py          # builds site/ from docs/
python3 test_build.py     # runs build + verification checks
```

Then open `site/index.html` in any browser. Everything works from `file://` —
nothing needs to be hosted or published.

## Companion guides

This manual assumes your business exists. Its two sibling guides fill in the
edges:

- **llc-first-year-handbook** — getting the LLC itself through year one
- **freelance-first-client-guide** — the mirror image: being the person someone hires

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
