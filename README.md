# Microeconomics

Material from my microeconomics course, *Microeconomics I* (Spring 2013).

Course site: https://gcallah.github.io/microeconomics/

## Building the site

The site is built entirely from files in this repo. My own course documents
(the elasticity homework and the 2013 final exam) were converted once into
`content/*.html`; the original Word files are no longer used. The supply and
demand schedules in the final, which were pictures in the original, are now
ordinary HTML tables.

- `make html` rebuilds `index.html`, `homework/` and `exams/` from `content/`.
  To fix a page, edit `content/<page>.html` (its `<h1>` is the page title) and
  run `make html`. Needs Python 3 only.
- `make clean` removes the generated pages; `content/` and `graphics/` are kept.

The class schedule, and which homework and exams go with which class, are set by
the tables at the top of `bin/build.py` (`TOPICS`, `HOMEWORK`, `EXAMS`). Colours,
fonts and widths are set once, in `:root` at the top of `style.css`. Images live
in `graphics/`.

Only my own work is published: the publisher's lecture decks, solutions manual
and test bank, and the tests built from that test bank, are left out (the list
is in `bin/build.py`).

Background painting: Joachim Beuckelaer, *Market in the Square* (1566), public
domain, via Wikimedia Commons.
