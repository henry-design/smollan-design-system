# Smollan Design System

**Build on-brand Smollan PowerPoint decks from code.** Every official Smollan slide design (190 of
them, from the Core Template and packs 1-14) is packaged as a ready-made **recipe**. You choose a recipe
for each slide and pass in your content, and the library produces a fully editable `.pptx` that looks
exactly like the brand templates.

> **AI agents: read [AGENTS.md](AGENTS.md) first.** It is a complete, step-by-step operating manual.
> (`llms.txt`, `CLAUDE.md`, `GEMINI.md` and `.github/copilot-instructions.md` all point there.)

```python
from smollan import Deck

deck = Deck(title="Q3 BUSINESS REVIEW", presenter="Jane Doe, Client Lead", date="OCTOBER 2026")
deck.add("stats.3", heading="Q3 RESULTS AT A GLANCE",
         items=[{"label": "AVAILABILITY",   "value": "96%", "text": "On-shelf availability, up 4 points."},
                {"label": "SHARE OF SHELF", "value": "31%", "text": "Share of shelf in core categories."},
                {"label": "COMPLIANCE",     "value": "92%", "text": "Planogram compliance."}])
deck.save("q3_review.pptx")          # cover + your slide + Smollan closing slide
```

| ![cover](thumbnails/cover.dark_blue.png) | ![stats](thumbnails/stats.3.png) | ![process](thumbnails/process.5.png) |
|---|---|---|
| ![org](thumbnails/org.tree.png) | ![graphs](thumbnails/graphs.1_sub.png) | ![why](thumbnails/why.pillars.png) |

---

## Contents

1. [Install](#1-install)
2. [Five-minute tour](#2-five-minute-tour)
3. [Three ways to use it](#3-three-ways-to-use-it)
4. [What's in the box](#4-whats-in-the-box)
5. [Documentation map](#5-documentation-map)
6. [Repository layout](#6-repository-layout)
7. [Known limits](#7-known-limits)
8. [Notice](#8-notice)

---

## 1. Install

Requires **Python 3.10+**. The template, photos and fonts ship inside the package, so it works from
any folder once installed.

```bash
pip install git+https://github.com/henry-design/smollan-design-system
smollan install-fonts        # once per computer: installs Montserrat, the Smollan typeface
smollan version              # check it works
```

Working on the library itself? Clone it and install it in editable mode:

```bash
git clone https://github.com/henry-design/smollan-design-system
cd smollan-design-system
pip install -e .
```

Full setup notes, including troubleshooting, are in [docs/getting-started.md](docs/getting-started.md).

## 2. Five-minute tour

**Step 1: find a slide for your message.**

```text
$ smollan find "three numbers with photos"
stats.3_gauges_photos        3 gauge stats with photos
stats.3                      3 big stats (dark band)
stats.5_photos               5 stats on dark panel + photos
```

**Step 2: see what the recipe needs**, including its slots, how much text fits, the number of items
and an example call.

```text
$ smollan show stats.3
SLOTS:
  heading        text   max 1 line, ~50 chars/line
  subheading     text   fits ~1 line, ~111 chars/line
ITEMS: exactly 3 item dicts in items=[...]
  label          text   fits ~1 line, ~25 chars/line
  value          text   fits ~1 line, ~5 chars/line
  text           text   max 5 lines, ~42 chars/line
  note           text   fits ~2 lines, ~44 chars/line
EXAMPLE:
deck.add("stats.3", heading='YOUR HEADING', ..., items=[{'label': ..., 'value': '87%', ...}, ...])
```

**Step 3: build.** Use Python (above), or a JSON file with the command-line tool (below). If your
content breaks a template rule (copy too long, wrong number of items, too many process steps), you
get a `SmollanError` that says exactly what to change. Nothing off-brand is produced.

## 3. Three ways to use it

| | Best for | How |
|---|---|---|
| **Python API** | scripts, notebooks, Python agents | `from smollan import Deck` - see [docs/api-reference.md](docs/api-reference.md) |
| **JSON + CLI** | any agent or language that can write a file and run a command | `smollan build deck.json` - see [docs/json-spec.md](docs/json-spec.md) |
| **Catalog** | people choosing slides | [CATALOG.md](CATALOG.md) (every recipe with a picture), `smollan list` |

JSON example (full version: [examples/deck_spec.json](examples/deck_spec.json)):

```json
{
  "deck":   {"title": "Q3 BUSINESS REVIEW", "presenter": "Jane Doe", "date": "OCTOBER 2026", "client": "Acme Foods"},
  "slides": [
    {"recipe": "stats.3", "heading": "Q3 RESULTS", "items": [
      {"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability."},
      {"label": "SHARE",        "value": "31%", "text": "Share of shelf."},
      {"label": "COMPLIANCE",   "value": "92%", "text": "Planogram compliance."}]},
    {"recipe": "org.tree", "heading": "YOUR TEAM",
     "tree": {"name": "Jane Doe", "role": "Client Lead", "children": [{"name": "Sipho Dlamini", "role": "Field Manager"}]}}
  ],
  "output": "q3.pptx"
}
```

```bash
smollan build deck.json          # -> q3.pptx next to deck.json
```

## 4. What's in the box

| Category | Recipes | What they're for |
|---|---|---|
| `cover` | 18 | Opening slides: 3 shape covers and 15 photo covers (incl. RFP and co-branded) |
| `divider` | 3 | Section breaks |
| `title` | 7 | Heading + body text: the plain-text fallback |
| `stats` | 11 | 1-5 big headline numbers, with or without photos |
| `kpis` | 8 | KPI grids, KPI tables, scorecards |
| `process` | 12 | 3-8 step methods (max 8 per slide) |
| `infographic` | 11 | Triad, pyramid, Venn / pivot point, loop, cycle, SWOT |
| `buckets` | 13 | "Here are N things": 4/5/6/8 boxes, optionally with photos |
| `graphs` | 13 | Native, editable charts: 1-2 per slide |
| `tables` | 31 | Clean tables, tick and dot matrices, gantt, Growth Teams commercial tables |
| `org` | 26 | Org charts drawn from your data, plus 15 fixed-shape designs |
| `feedback` | 4 | Client survey results with quotes |
| `devices` | 10 | Laptop / browser / phone mockups for screenshots and video |
| `why` | 6 | Why Smollan: pillars and custom differentiators |
| `thankyou` | 16 | Thank-you and next-steps slides |
| `closing` | 1 | The Smollan end slide (added automatically) |

Also included: **brand tokens** (`Brand.GREEN` and others), **21 stock photos** (`smollan photos`),
**Montserrat** in all 18 weights, **guard-rails** that stop off-brand output, and a **preflight check**
for leftover template text.

## 5. Documentation map

| If you want to... | Read |
|---|---|
| Use this as an AI agent | [AGENTS.md](AGENTS.md) |
| Install it and build a first deck | [docs/getting-started.md](docs/getting-started.md) |
| Understand recipes, slots, items and limits | [docs/concepts.md](docs/concepts.md) |
| Know exactly what to pass for text, photos, charts, tables, org charts | [docs/content-formats.md](docs/content-formats.md) |
| Build decks from JSON / any language | [docs/json-spec.md](docs/json-spec.md) |
| Look up a function or CLI command | [docs/api-reference.md](docs/api-reference.md) |
| Fix an error | [docs/troubleshooting.md](docs/troubleshooting.md) |
| Browse every slide with pictures | [CATALOG.md](CATALOG.md) |
| Rebuild from new PPT packs / add slides | [docs/maintenance.md](docs/maintenance.md) |
| Understand how it works inside | [docs/architecture.md](docs/architecture.md) |

## 6. Repository layout

```
smollan/                    the installable package
├── __init__.py             public API (re-exports everything you need)
├── deck.py                 Deck: add slides, save, preflight
├── catalog.py              find / describe / show / CATALOG.md generator
├── validation.py           rule checks before anything is built
├── text.py charts.py tables.py orgchart.py shapes.py   content fillers
├── brand.py                Smollan colours, fonts, geometry
├── photos.py               stock photo library (assets.photo / assets.photos)
├── cli.py                  `smollan` command, JSON builder, font installer
├── recipes.py              GENERATED registry of all 190 recipes
├── smollan_master.pptx     every Smollan layout + one template slide per recipe
└── assets/photos  assets/fonts
docs/                       guides (see the map above)
examples/                   demo.py, deck_spec.json and their outputs
thumbnails/<id>.png         a preview of every recipe
CATALOG.md  catalog.json    the full recipe catalog (human / machine)
tools/                      maintenance pipeline (rebuild from the original packs)
```

## 7. Known limits

- **Text limits are estimates**, based on box sizes, the templates' own "no longer than N lines"
  instructions and Montserrat's width. They err on the strict side.
- **Org charts:** SmartArt can't be generated, so org charts are drawn as shapes from your tree data,
  up to 5 levels and 8 boxes across. Split bigger teams over several slides.
- **Waterfall charts** are emulated with a native stacked-column chart, because the Office 2016
  waterfall type isn't editable through python-pptx.
- **Fixed photos:** photo covers keep their designed photography, and the gauge arcs in
  `stats.3_gauges_photos` don't resize with the value.
- **Fixed-grid tables:** presets with merged cells (mostly Growth Teams) need exactly the template's
  grid, which `smollan show <id>` describes.
- **Previews and PDFs** (`tools/render.ps1`) need Windows with PowerPoint. Building decks works anywhere
  Python runs.

## 8. Notice

- The Smollan name, logo, slide designs and photography belong to Smollan. They are included so the
  library can reproduce the brand, and are not licensed for any other use.
- Content from real client work in the source templates has been replaced with neutral placeholders
  (`tools/scrub_master.py`).
- Montserrat: (c) The Montserrat Project Authors, SIL Open Font License 1.1.
