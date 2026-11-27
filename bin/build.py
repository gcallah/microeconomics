#!/usr/bin/env python3
"""Build the Microeconomics I static site from the files in this repo.

The course documents were converted once into content/*.html; this script never
reads the original material. It wraps each content file in the site chrome
(homework -> homework/<slug>.html, exams -> exams/<slug>.html) and writes
index.html, organised around the Spring 2013 class schedule.

Usage: python3 bin/build.py [--out DIR]
Needs: Python 3 only.
"""

import argparse
import hashlib
import html
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------- course data
#
# Everything about *what* goes on the site lives in these tables.
#
# Only the instructor's own work is published. Deliberately left out of the
# original course folder:
#   23759-Heyne, EWT11_ppts/          publisher's (Pearson) lecture decks for the textbook
#   Chapter03/Chapter03.ppt,
#   Chapter04/Chapter04.pptx          publisher's decks, lightly revised; still Pearson's
#   Chapter03/*.jpg, Chapter04/*.jpg  pictures pasted into those decks, of unknown origin
#   93915-0136039588_ism/             publisher's instructor's solutions manual
#   Tests/                            publisher's test-item file
#   MicroeconomicsTest1, SampleTest2, TestTwo*, TestThree*, ChapterNineHomework
#                                     built largely from the publisher's test-item file
#   TestTwo.txt                       plain-text copy of TestTwo.docx
#   Spring2013Syllabus.doc            contains office phone number; its schedule is TOPICS below
#   beer.gif                          1x1 spacer image

CONTENT_DIR = "content"  # converted course documents; edit these to fix a page

# Homework and exams: slug -> section. Titles come from each file's <h1>.
HOMEWORK = ["elasticity-homework"]
EXAMS = ["final-2013"]
SECTIONS = {"homework": HOMEWORK, "exams": EXAMS}

TEXTBOOK = ("Paul Heyne, Peter Boettke and David Prychitko, "
            "<cite>The Economic Way of Thinking</cite>")
PENCIL = ('<a href="https://fee.org/ebooks/i-pencil">Leonard Read, '
          '&ldquo;I, Pencil&rdquo;</a>')

# The Spring 2013 class schedule. "ch" is the textbook chapter to read; each
# entry may list homework or exams that go with it.
TOPICS = [
    {"date": "Jan 29", "title": "Introduction", "reading": "Preface"},
    {"date": "Feb 1", "title": "Economics and the economic way of thinking", "ch": 1,
     "extra": PENCIL},
    {"date": "Feb 5", "title": "Efficiency and trade", "ch": 2},
    {"date": "Feb 8", "title": "What makes something valuable?", "ch": 3},
    {"date": "Feb 12", "title": "What is demand?", "ch": 3},
    {"date": "Feb 15", "title": "What is cost?", "ch": 4, "event": "Quiz 1"},
    {"date": "Feb 19", "title": "What is supply?", "ch": 4},
    {"date": "Feb 22", "title": "How do market demand and supply interact?", "ch": 5},
    {"date": "Feb 26", "title": "Applications of demand and supply analysis", "ch": 6,
     "homework": ["elasticity-homework"]},
    {"date": "Mar 1", "title": "More applications", "ch": 6},
    {"date": "Mar 5", "title": "Profit and loss", "ch": 7},
    {"date": "Mar 8", "title": "Competition and monopoly", "ch": 8, "event": "Quiz 2"},
    {"date": "Mar 12", "title": "Competition and monopoly, continued", "ch": 8},
    {"date": "Mar 15", "title": "Midterm exam"},
    {"date": "Mar 19", "title": "Price searching and market power", "ch": 9},
    {"date": "Mar 22", "title": "Public policy toward competition and monopoly", "ch": 10},
    {"date": "Apr 2", "title": "Public policy, continued", "ch": 10},
    {"date": "Apr 5", "title": "What determines the distribution of income?", "ch": 11,
     "event": "Quiz 3"},
    {"date": "Apr 9", "title": "Income distribution, continued", "ch": 11},
    {"date": "Apr 12", "title": "Externalities and conflicting rights", "ch": 12},
    {"date": "Apr 16", "title": "Externalities and conflicting rights, continued", "ch": 12},
    {"date": "Apr 19", "title": "Markets and government", "ch": 13, "event": "Quiz 4"},
    {"date": "Apr 23", "title": "Markets and government, continued", "ch": 13},
    {"date": "Apr 26", "title": "The theory of government failure"},
    {"date": "Apr 30", "title": "Comparative economic systems", "ch": 14},
    {"date": "May 3", "title": "Comparative economic systems, continued", "ch": 14,
     "event": "Quiz 5"},
    {"date": "May 7", "title": "Review"},
    {"date": "May 10", "title": "Review"},
    {"date": "Final", "title": "Final exam", "exams": ["final-2013"]},
]

# ---------------------------------------------------------------- site chrome

SITE_TITLE = "Microeconomics I"
TAGLINE = "The economic way of thinking"
DESCRIPTION = ("An introduction to how economists explain the social world: choice and "
               "opportunity cost, trade and comparative advantage, demand and supply, profit "
               "and competition, and the parts played by markets and government.")
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900"
             "&family=Crimson+Pro:ital,wght@0,400;0,600;1,400"
             "&family=IBM+Plex+Sans:wght@500;600&display=swap")
BACKDROP_CREDIT = ("Background: Joachim Beuckelaer, <cite>Market in the Square</cite> (1566). "
                   "Public domain, via "
                   '<a href="https://commons.wikimedia.org/wiki/'
                   'File:Joachim_Beuckelaer_-_Market_in_the_Square.jpg">Wikimedia Commons</a>.')
FOOTER = f"{SITE_TITLE}: schedule, homework and exams from Gene Callahan's course."

CSS_VERSION = ""


def esc(text):
    return html.escape(text, quote=True)


def page(title, body, root="", body_class="", hero=None):
    """Wrap body in the site chrome. root is the path from this page to the site root."""
    hero_html = ""
    if hero:
        kicker, heading, sub = hero
        hero_html = f"""<header class="hero">
  {f'<p class="kicker">{kicker}</p>' if kicker else ''}
  <h1>{heading}</h1>
  {f'<p class="sub">{sub}</p>' if sub else ''}
</header>"""
    doc_title = SITE_TITLE if title == SITE_TITLE else f"{title} · {SITE_TITLE}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(doc_title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="{FONTS_URL}">
    <link rel="stylesheet" href="{root}style.css?v={CSS_VERSION}">
</head>
<body class="{body_class}">
<nav class="site-nav">
  <a class="brand" href="{root}index.html">{SITE_TITLE}</a>
  <span class="links">
    <a href="{root}index.html#schedule">Schedule</a>
    <a href="{root}index.html#homework">Homework</a>
    <a href="{root}index.html#exams">Exams</a>
  </span>
</nav>
<div class="sheet">
{hero_html}
<main>
{body}
</main>
</div>
<footer class="site-footer">
  <p>{FOOTER}</p>
  <p class="credit">{BACKDROP_CREDIT}</p>
</footer>
</body>
</html>
"""


def load_content(src, slug):
    """Return (title, body) of content/<slug>.html; the <h1> is the title."""
    text = (src / CONTENT_DIR / f"{slug}.html").read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->\s*", "", text, flags=re.S)
    m = re.search(r"<h1>(.*?)</h1>\s*", text, re.S)
    if not m:
        raise SystemExit(f"{CONTENT_DIR}/{slug}.html has no <h1> title")
    return html.unescape(m.group(1)), text[:m.start()] + text[m.end():]


def topic_of(kind, slug):
    for t in TOPICS:
        if slug in t.get(kind, []):
            return t
    return None


def reading(t):
    parts = []
    if t.get("ch"):
        parts.append(f"Heyne, ch. {t['ch']}")
    if t.get("reading"):
        parts.append(f"Heyne, {esc(t['reading'])}")
    if t.get("extra"):
        parts.append(t["extra"])
    return "; ".join(parts)


def build_pages(src, out):
    """Write homework/ and exams/ pages; return {section: [(href, title)]}."""
    built = {}
    for section, slugs in SECTIONS.items():
        outdir = out / section
        if outdir.exists():
            shutil.rmtree(outdir)
        outdir.mkdir(parents=True)
        built[section] = []
        for slug in slugs:
            title, body = load_content(src, slug)
            t = topic_of(section, slug)
            sub = f"{esc(t['date'])}: {esc(t['title'])}" if t else ""
            (outdir / f"{slug}.html").write_text(
                page(title, f'<article class="paper">\n{body}</article>', root="../",
                     body_class=section, hero=(section.capitalize(), esc(title), sub)),
                encoding="utf-8")
            built[section].append((f"{section}/{slug}.html", title, slug))
        print(f"  {len(slugs)} {section}")
    return built


def build_index(out, built):
    chip_class = {"homework": "homework", "exams": "exam"}
    lookup = {(sec, slug): (href, title) for sec, items in built.items()
              for href, title, slug in items}
    rows = []
    for t in TOPICS:
        chips = [f'<a class="chip {chip_class[sec]}" href="{lookup[(sec, s)][0]}">'
                 f'{esc(lookup[(sec, s)][1])}</a>'
                 for sec in SECTIONS for s in t.get(sec, [])]
        event = f'<span class="event">{esc(t["event"])}</span>' if t.get("event") else ""
        read = reading(t)
        rows.append(
            f'<li class="topic"><span class="date">{esc(t["date"])}</span>'
            f'<div><span class="title">{esc(t["title"])}</span>{event}'
            + (f'<span class="reading">{read}</span>' if read else "")
            + (f'<span class="chips">{"".join(chips)}</span>' if chips else "")
            + "</div></li>")

    def cards(section, label):
        return "\n".join(
            f'<li><a class="card" href="{href}"><span class="label">{label}</span>'
            f'<span class="title">{esc(title)}</span></a></li>'
            for href, title, _ in built[section])

    body = f"""<section id="schedule">
<h2>Schedule</h2>
<p class="lede">{esc(DESCRIPTION)} Textbook: {TEXTBOOK}. Dates are from the Spring 2013
term; there were quizzes on the days marked.</p>
<ol class="schedule">
{chr(10).join(rows)}
</ol>
</section>
<section id="homework">
<h2>Homework</h2>
<ul class="cards">
{cards("homework", "Homework")}
</ul>
</section>
<section id="exams">
<h2>Exams</h2>
<ul class="cards">
{cards("exams", "Exam")}
</ul>
</section>"""
    (out / "index.html").write_text(
        page(SITE_TITLE, body, body_class="home",
             hero=(esc(TAGLINE), SITE_TITLE,
                   "Choice, cost, trade and prices: how markets coordinate the plans of "
                   "people who have never met.")),
        encoding="utf-8")


def main():
    global CSS_VERSION
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent,
                    help="site root (default: the repo)")
    args = ap.parse_args()
    out = args.out
    CSS_VERSION = hashlib.md5((out / "style.css").read_bytes()).hexdigest()[:8]
    print(f"Building {SITE_TITLE} in {out}")
    built = build_pages(out, out)
    build_index(out, built)
    print("  index.html")


if __name__ == "__main__":
    main()
