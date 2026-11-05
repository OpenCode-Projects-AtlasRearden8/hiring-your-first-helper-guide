#!/usr/bin/env python3
"""Build the Hiring Your First Helper Guide static site from docs/ into site/.

Local-first: pure Python standard library, no network, no dependencies.
Usage:  python3 build.py
"""

import datetime
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

TITLE = "Hiring Your First Helper Guide"
SUBTITLE = (
    "A plain-English small-business manual for hiring your first "
    "contractor or part-timer"
)
FOOTER = "By Asdale Dynamics, LLC · Education only, never legal or tax advice."

# Reading order: (filename, nav label)
ORDER = [
    ("00-start-here.md", "Start Here"),
    ("01-should-you-hire.md", "1 · Should You Hire?"),
    ("02-writing-the-posting.md", "2 · Writing the Posting"),
    ("03-fair-trial-projects.md", "3 · Fair Trial Projects"),
    ("04-paying-people-plainly.md", "4 · Paying People Plainly"),
    ("05-records-you-keep.md", "5 · Records You Keep"),
    ("06-onboarding.md", "6 · Onboarding"),
    ("07-offboarding.md", "7 · Offboarding"),
    ("08-keeping-your-head-above-water.md", "8 · Keeping Your Head"),
    ("interview-scorecard.md", "Interview Scorecard"),
    ("first-week-onboarding-sheet.md", "First-Week Onboarding Sheet"),
    ("glossary.md", "Glossary"),
]

NOTICE = (
    '<div class="notice"><strong>Education only, never legal or tax advice.</strong> '
    "This guide explains concepts in plain language so you can have smarter "
    "conversations with professionals; it does not replace them.</div>"
)

CSS = """
:root { --ink:#1c2333; --paper:#fdfbf7; --accent:#7a4ea3; --accent2:#3a6ea5; }
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink);
  font:17px/1.65 Georgia, "Iowan Old Style", "Times New Roman", serif; }
header.site { background:linear-gradient(120deg,#33244d,#2b3f5e); color:#fff; padding:2rem 1rem 1.4rem; }
header.site .wrap { max-width:880px; margin:0 auto; }
header.site h1 { font-size:1.5rem; margin:0 0 .25rem; }
header.site p { margin:0; color:#cfd6e4; font-size:.95rem; }
nav.toc { background:#2b3f5e; }
nav.toc .wrap { max-width:880px; margin:0 auto; display:flex; flex-wrap:wrap; gap:.2rem .9rem; padding:.5rem 1rem; }
nav.toc a { color:#dfe6f2; text-decoration:none; font-size:.8rem; font-family:"Segoe UI", Arial, sans-serif; }
nav.toc a:hover { color:#ffcf70; text-decoration:underline; }
nav.toc a.current { color:#ffcf70; }
main { max-width:880px; margin:0 auto; padding:1.5rem 1rem 3rem; }
h1 { font-size:1.9rem; line-height:1.25; margin:.5rem 0 1rem; color:#33244d; }
h2 { font-size:1.25rem; margin:2rem 0 .5rem; color:#33244d; border-bottom:2px solid #e6ddf3; padding-bottom:.2rem; }
h3 { font-size:1.05rem; margin:1.4rem 0 .4rem; color:#3a2f55; }
p { margin:.6rem 0; }
code { background:#eee9f5; padding:.1rem .35rem; border-radius:4px;
  font:.9em "Cascadia Mono", Consolas, monospace; color:#4a2f6e; }
pre { background:#2a2140; color:#e8e0f5; padding:1rem; border-radius:8px; overflow:auto; }
pre code { background:transparent; color:inherit; padding:0; }
blockquote { background:#f6f0fa; border-left:4px solid var(--accent); margin:1rem 0;
  padding:.6rem 1rem; border-radius:0 8px 8px 0; color:#43365f; blockquote p(0) }
blockquote p { margin:.3rem 0; }
table { border-collapse:collapse; width:100%; margin:1rem 0; font-size:.92rem; }
th, td { border:1px solid #ddd5e8; padding:.45rem .6rem; vertical-align:top; }
th { background:#efe8f8; font-family:"Segoe UI", Arial, sans-serif; font-size:.85rem; }
tr:nth-child(even) td { background:#faf7fd; }
hr { border:0; border-top:1px solid #e0d8ee; margin:2rem 0; }
a { color:var(--accent2); }
li { margin:.25rem 0; }
.pn { display:flex; justify-content:space-between; gap:1rem; margin-top:2.5rem;
  border-top:1px solid #e6ddf3; padding-top:1rem;
  font-family:"Segoe UI", Arial, sans-serif; font-size:.92rem; }
footer.site { text-align:center; color:#8a8e99; font-size:.8rem; padding:1.2rem; }
.notice { background:#fff7e6; border:1px solid #ecd9a8; padding:.7rem 1rem;
  border-radius:8px; font-size:.9rem; color:#7a5b16; margin-top:2rem; }
input[type=checkbox] { accent-color:var(--accent); }
@media (prefers-color-scheme: dark) {
  :root { --ink:#e8e6ef; --paper:#191623; --accent:#b79ede; --accent2:#8db8e8; }
  code { background:#2e2840; color:#cdbcf0; }
  blockquote { background:#241f33; color:#c9c0df; }
  table { border-color:#3a3350; } th { background:#2a2440; }
  tr:nth-child(even) td { background:#211d2f; }
  pre { background:#241f33; }
  .notice { background:#33291a; border-color:#5b4a22; color:#e5c77f; }
  h1, h2, h3 { color:#cfc4e8; }
}
""".replace(" blockquote p(0) ", "").strip()


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def slugify(text: str) -> str:
    plain = re.sub(r"<[^>]+>", "", text)
    s = re.sub(r"[^\w\s-]", "", plain, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_]+", "-", s) or "section"


def render_inline(text: str) -> str:
    """Inline markdown (code, links, bold, italic) -> safe HTML."""
    out = esc(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: '<a href="%s">%s</a>' % (html.escape(m.group(2), quote=True), m.group(1)),
        out,
    )
    out = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<strong><em>\1</em></strong>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


def markdown_to_html(text: str) -> str:
    """Convert this project's markdown subset to HTML."""
    out: list[str] = []
    lines = text.splitlines()
    i = 0
    n = len(lines)

    def is_blank(idx: int) -> bool:
        return idx < n and not lines[idx].strip()

    def starts_block(idx: int) -> bool:
        if idx >= n or not lines[idx].strip():
            return True
        s = lines[idx]
        return (
            s.startswith("```")
            or s.startswith("#")
            or s.lstrip().startswith(">")
            or re.match(r"^\s*\|", s) is not None
            or re.match(r"^\s*[-*]\s+", s) is not None
            or re.match(r"^\s*\d+\.\s+", s) is not None
            or re.match(r"^\s*-{3,}\s*$", s) is not None
        )

    while i < n:
        line = lines[i]
        if is_blank(i):
            i += 1
            continue

        # fenced code
        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(buf)))
            continue

        # table
        if line.lstrip().startswith("|"):
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level, content = len(m.group(1)), m.group(2).strip()
            out.append(
                '<h%d id="%s">%s</h%d>'
                % (level, slugify(content), render_inline(content), level)
            )
            i += 1
            continue

        # horizontal rule
        if re.match(r"^\s*([-*_=])\1{2,}\s*$", line) or re.match(r"^\s*-{3,}\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # lists (with checkbox support and simple continuation lines)
        ul = re.match(r"^\s*[-*]\s+(.*)$", line)
        ol = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if ul or ol:
            ordered = bool(ol)
            indentPat = re.compile(r"^\s{2,}(\S.*)$") if not ordered else re.compile(r"^\s{3,}(\S.*)$")
            pat = re.compile(r"^\s*\d+\.\s+(.*)$") if ordered else re.compile(r"^\s*[-*]\s+(.*)$")
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and (m := pat.match(lines[i])):
                content = m.group(1)
                # checkbox syntax only in unordered lists
                cb = re.match(r"^\[([\sxX])\]\s+", content)
                if not ordered:
                    item_prefix = ""
                    if cb:
                        if cb.group(1) == " ":
                            item_prefix = '<input type="checkbox"> '
                        else:
                            item_prefix = '<input type="checkbox" checked> '
                        content = content[cb.end():]
                    items.append(item_prefix + render_inline(content.strip()))
                else:
                    items.append(render_inline(content.strip()))
                i += 1
                # continuation lines (indented text under an item)
                while i < n and not is_blank(i) and not pat.match(lines[i]) and not starts_block(i):
                    items[-1] += " " + render_inline(lines[i].strip())
                    i += 1
            out.append(
                "<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % it for it in items), tag)
            )
            continue

        # blockquote: consume '>' lines and their wrapped continuations
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and (lines[i].lstrip().startswith(">") or (not is_blank(i) and buf and not starts_block(i))):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]).strip())
                i += 1
            inner = " ".join(b for b in buf if b)
            out.append("<blockquote><p>%s</p></blockquote>" % render_inline(inner))
            continue

        # paragraph: consume until blank line or another block starts
        buf = [line]
        i += 1
        while i < n and not starts_block(i):
            buf.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % render_inline(" ".join(b.strip() for b in buf)))

    return "\n".join(out)


def render_table(rows: list[str]) -> str:
    def cells(row: str) -> list[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]

    aligns = []
    if len(rows) >= 2 and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", rows[1]):
        for c in cells(rows[1]):
            left, right = c.startswith(":"), c.endswith(":")
            aligns.append(
                "center" if left and right else "right" if right else "left"
            )
        body_rows = rows[2:]
        header_cells = cells(rows[0])
    else:
        body_rows = rows[1:]
        header_cells = None
        aligns = []

    def attr(idx: int) -> str:
        return " style=\"text-align:%s\"" % aligns[idx] if idx < len(aligns) and aligns[idx] != "left" else ""

    parts = ["<table>"]
    if header_cells:
        parts.append(
            "<thead><tr>%s</tr></thead>"
            % "".join("<th%s>%s</th>" % (attr(j), render_inline(c)) for j, c in enumerate(header_cells))
        )
    parts.append("<tbody>")
    for r in body_rows:
        parts.append(
            "<tr>%s</tr>" % "".join("<td%s>%s</td>" % (attr(j), render_inline(c)) for j, c in enumerate(cells(r)))
        )
    parts.append("</tbody></table>")
    return "".join(parts)


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def build_nav(current: str | None) -> str:
    parts = ['<a href="index.html">Home</a>']
    for fname, label in ORDER:
        href = fname.replace(".md", ".html")
        cls = ' class="current"' if fname == current else ""
        parts.append('<a href="%s"%s>%s</a>' % (href, cls, esc(label)))
    return "".join(parts)


PREV_NEXT_TEMPLATE = (
    '<div class="pn"><div>%s</div><div>%s</div></div>'
)


def render_page(title: str, body: str, nav_html: str, pn_html: str) -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>%s</title>\n"
        "<style>%s</style>\n"
        "</head>\n<body>\n"
        "<header class=\"site\"><div class=\"wrap\">\n"
        "<h1>%s</h1><p>%s</p>\n"
        "</div></header>\n"
        "<nav class=\"toc\"><div class=\"wrap\">%s</div></nav>\n"
        "<main>%s%s<div>%s</div></main>\n"
        "<footer class=\"site\">%s Built %s.</footer>\n"
        "</body>\n</html>\n"
    ) % (
        esc(title),
        CSS,
        esc(TITLE),
        esc(SUBTITLE),
        nav_html,
        body,
        NOTICE,
        pn_html,
        esc(FOOTER),
        datetime.date.today().isoformat(),
    )


def first_para(text: str) -> str:
    text = text.strip()
    if text.startswith("*") and text.endswith("*") and len(text) > 3:
        text = text[1:-1]
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("*") and s.endswith("*") and len(s) > 3:
            return s.strip("*").strip()
        if s and not s.startswith("#") and not s.startswith("**") and not s.startswith("|"):
            return s.strip("*").strip()
    return ""


def build() -> None:
    if not DOCS.is_dir():
        raise SystemExit("docs/ not found — run from the project root.")
    SITE.mkdir(exist_ok=True)

    pages = []  # (md_file, html_file, body_html)
    for fname, _label in ORDER:
        path = DOCS / fname
        if not path.exists():
            print("WARNING: missing doc %s" % fname)
            continue
        pages.append((fname, fname.replace(".md", ".html"), markdown_to_html(path.read_text(encoding="utf-8"))))

    # index.html
    toc_items = []
    for i, (fname, html_name, _body) in enumerate(pages):
        _f, label = ORDER[i] if i < len(ORDER) else (fname, esc(fname))
        desc = first_para((DOCS / fname).read_text(encoding="utf-8"))
        toc_items.append(
            '<li><a href="%s"><strong>%s</strong></a> — <small>%s</small></li>'
            % (html_name, esc(label), render_inline(esc(desc[:200])))
        )
    intro = (
        "<h1>Hiring Your First Helper</h1>"
        "<p>You're one person running a small business, and you've hit the "
        "moment where one more pair of hands would genuinely help. This manual "
        "walks the whole arc in plain English: deciding what to hire, writing "
        "the posting, paid trial projects, paying people on time, keeping just "
        "enough records, onboarding without info-flooding, kind offboarding — "
        "and staying sane about all of it.</p>"
        "<blockquote><p><strong>Education only, never legal or tax advice.</strong> "
        "This guide explains concepts so you can have better conversations with "
        "professionals (an accountant, a lawyer, your state's business office); "
        "it does not replace them.</p></blockquote>"
        '<h2>Contents</h2><ol>%s</ol>' % "".join(toc_items)
    )
    (SITE / "index.html").write_text(
        render_page(TITLE, intro, build_nav(None), ""), encoding="utf-8"
    )

    for i, (fname, html_name, body) in enumerate(pages):
        prev = (
            '<a href="%s">&larr; %s</a>' % (pages[i - 1][1], esc(ORDER[i - 1][1]))
            if i > 0
            else ""
        )
        nxt = (
            '<a href="%s">%s &rarr;</a>' % (pages[i + 1][1], esc(ORDER[i + 1][1]))
            if i + 1 < len(pages)
            else ""
        )
        title = extract_title((DOCS / fname).read_text(encoding="utf-8"))
        (SITE / html_name).write_text(
            render_page(title, body, build_nav(fname), PREV_NEXT_TEMPLATE % (prev, nxt)),
            encoding="utf-8",
        )

    print("Built %d pages into site/ from %d docs." % (len(pages) + 1, len(pages)))


if __name__ == "__main__":
    build()
