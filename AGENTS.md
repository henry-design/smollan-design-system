# AGENTS.md - how an AI agent uses the Smollan Design System

You are building a **Smollan-branded PowerPoint deck**. Do **not** draw slides from scratch or with
another library. This package contains every official Smollan slide design as a **recipe**: 190
recipes across 16 categories. You pick a recipe for each message and pass your content, and the
package produces an editable `.pptx` that matches the brand templates exactly.

This file is self-contained. Deeper references are in `docs/` (links at the end).

---

## 1. Setup (once per machine)

```bash
pip install git+https://github.com/henry-design/smollan-design-system
smollan install-fonts        # Montserrat, the Smollan typeface (no admin rights needed)
smollan version              # -> 1.0.0  (use `python -m smollan ...` if `smollan` isn't on PATH)
```

The package bundles its own master template, photos and fonts. You can work from any folder; no
repository checkout is needed.

## 2. Two ways to build

| | When | How |
|---|---|---|
| **A. Python** | you can run Python | `from smollan import Deck` - sections 4-5 |
| **B. JSON + CLI** | you can only write files and run commands, or you prefer data over code | write `deck.json`, run `smollan build deck.json` - section 6 |

Both use the same recipe ids, slot names and value formats.

## 3. Workflow (follow it in order)

1. **Plan the story.** List the slides as **one message each**, grouped into sections.
2. **Choose a recipe per slide.**
   - Look at the category table (section 7), or
   - run `smollan find "plain english need"` or `find("...")`, which returns ranked recipe ids, or
   - run `smollan list <category>`.
3. **Read the recipe spec** before filling it: `smollan show <id>` (or `describe(id)`, which returns a
   string). It lists every slot, its kind, how many lines and characters fit, the exact item count,
   notes, alternatives and a ready-to-edit example call.
4. **Build** the deck (sections 5 and 6).
5. **Handle `SmollanError`.** The message says exactly what is wrong and how to fix it: shorten the
   copy, or use a recipe id it suggests. Fix and retry. Never work around a limit by shrinking fonts,
   editing XML or drawing your own shapes.
6. **Check the preflight result.** `save()` (and `smollan build`) reports leftover template text and
   empty photo slots. An empty list or `preflight: clean` means done.

## 4. Python API (essentials)

```python
from smollan import Deck, find, describe, alternatives, assets, SmollanError

deck = Deck(title="Q3 BUSINESS REVIEW", presenter="Name Surname, Title", date="OCTOBER 2026",
            client="Acme Foods",            # replaces every [Client] token in the templates
            logo=None,                      # optional client logo path, used wherever a recipe has a logo spot
            cover="cover.dark_blue")        # any cover.* recipe; a cover is added automatically
deck.add("<recipe id>", heading="...", items=[{...}, ...])   # one call per slide
issues = deck.save("deck.pptx")              # adds the closing slide, runs preflight
```

| call | purpose |
|---|---|
| `find(query, n=8, show=True)` | ranked recipe ids for a need (`find("4 steps with timeline")`) |
| `describe(id)` | full spec as a string |
| `alternatives(id, count)` | recipes in the same category that take `count` items |
| `assets.photos(tag)` / `assets.photo(name)` | list / get bundled stock photos |
| `Deck(..., auto_cover=False, auto_closing=False)` | turn off the automatic cover or closing slide |

## 5. Slot values

Pass slots as keyword arguments. Repeated blocks go in `items=[{field: value}, ...]`, one dict per
block, in **reading order** (left to right, then top to bottom; step order for processes). **Item
counts are exact.**

| kind | value |
|---|---|
| text | `str`, or `list[str]` = paragraphs/bullets. `"- "` prefix = indented bullet, `"\n"` = line break, `**bold**` = emphasis. Numbers as strings (`"96%"`) |
| photo | image path or `assets.photo("<name>")` (JSON: `"asset:<name>"`). Cropped to fill. Omit = empty slot |
| chart | `{"categories": [...], "series": {"Name": [numbers]}, "type": opt, "title": opt, "labels": opt}`. **Omit `type` to keep the template chart's styling.** Types: `column bar line line_plain pie doughnut stacked_column stacked_100 stacked_bar stacked_bar_100 area stacked_area waterfall`. Waterfall: one series + `"totals": [indexes]`, `None` = running total |
| table | `{"header": [...], "rows": [[...]], "footer": [...]}`. Cells: str, list, `True` = tick/dot, `False` = cross. `show()` says if the grid is flexible or **FIXED** (fixed = pass exactly the template grid described in the hint) |
| gantt | `{"periods": [...], "tasks": [{"label", "start", "end"}], "corner": "WEEK"}` (`tables.gantt`) |
| org | `{"name", "role", "photo"?, "children": [...]}`. Max 5 levels / 8 across; bigger means split by branch |
| video | `.mp4` path (`devices.laptop_video`) |
| logo | client logo image path. Optional slot on the RFP cover and many tables; fitted, not cropped. Omit = spot removed. `Deck(logo=...)` applies it everywhere |

- **Omitted slots are removed**, so no template text is left behind.
- **Slots marked "keeps Smollan wording"** (THANK YOU headings, the four pillars, feedback headings)
  keep the standard copy unless you pass your own.

## 6. JSON route

```json
{
  "deck": {"title": "Q3 BUSINESS REVIEW", "presenter": "Jane Doe, Client Lead", "date": "OCTOBER 2026",
           "client": "Acme Foods"},
  "slides": [
    {"recipe": "stats.3", "heading": "Q3 RESULTS AT A GLANCE", "items": [
      {"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability, up 4 points."},
      {"label": "SHARE OF SHELF", "value": "31%", "text": "Share of shelf in core categories."},
      {"label": "COMPLIANCE", "value": "92%", "text": "Planogram compliance."}]},
    {"recipe": "stats.1_photo", "heading": "ONE NUMBER THAT MATTERS", "value": "89%",
     "label": "RESOLVED IN 48H", "text": "Out-of-stocks fixed within two days.",
     "photo": "asset:merchandiser_snacks_aisle"}
  ],
  "output": "q3.pptx"
}
```

```bash
smollan build deck.json     # exit 0 = clean; 1 = error (stderr names the slide) or preflight issues
```

Relative paths (output, photos) are resolved from the JSON file's folder. `null` means not provided.

## 7. Choosing a recipe

| Message type | Category | Good default | Notes |
|---|---|---|---|
| Opening | `cover` | `cover.dark_blue` | `cover.photo.*` = photo-led; `cover.photo.rfp_client` for tenders |
| Section break | `divider` | `divider.dark_blue` | match the cover's colour tone |
| Heading + text / bullets | `title` | `title.one_line_sub` | the fallback for plain text |
| 1-5 headline numbers | `stats` | `stats.3` | `stats.1_photo`, `stats.4_cards`, `stats.5_photos`... |
| What we will measure | `kpis` | `kpis.5` | `kpis.6`, `kpis.7`, `kpis.table`, `kpis.strategic_table` |
| Step-by-step method | `process` | `process.5` | 3-8 steps. **Max 8 per slide** |
| Concept / framework | `infographic` | `infographic.triad` | `triangle`, `pivot_point` (Venn), `loop`, `cycle`, `swot` |
| N parallel points | `buckets` | `buckets.6` | 4/5/6/8, with or without photos |
| Chart | `graphs` | `graphs.1` | 1 or 2 charts; with intro / text column / takeaways |
| Table | `tables` | `tables.clean` | gantt, tick and dot matrices, comparisons, Growth Teams styles |
| Team structure | `org` | `org.tree` | drawn from tree data; `org.bespoke_*` = fixed shapes |
| Client survey results | `feedback` | `feedback.chart_quote` | |
| App / dashboard screenshot | `devices` | `devices.laptop_large` | phones, browser, video |
| Why choose Smollan | `why` | `why.pillars` | `why.differentiators*` for up to 8 custom reasons |
| Thank you / next steps | `thankyou` | `thankyou.c` | ends the deck instead of `closing` |
| End | `closing` | `closing` | added automatically |

If the content doesn't match a recipe's item count, use `alternatives(id, count)` or split across slides.

## 8. Rules

- **One message per slide.** If content doesn't fit, pick a bigger recipe or split it. Never shrink the type.
- **Headings are short and ALL CAPS.** Stay within each slot's limits (`max N lines`, `~C chars/line`).
- **Do not invent recipe ids or slot names.** Use `find` / `show`. Unknown names raise an error that lists the valid ones.
- **Do not change the brand**: no recolouring, font swaps or removing logos. If you add anything custom, use `Brand.*` colours; green is the focal colour, for one element per slide.
- **Don't call a deck finished** while preflight reports leftover text.

## 9. Complete Python example

```python
from smollan import Deck, assets

d = Deck(title="Q3 BUSINESS REVIEW\nACME FOODS", presenter="Jane Doe, Client Lead", date="OCTOBER 2026",
         client="Acme Foods")
d.add("divider.dark_blue", heading="Q3 PERFORMANCE", section="SECTION 01")
d.add("stats.3", heading="Q3 RESULTS AT A GLANCE", subheading="Across 1,240 stores",
      items=[{"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability, up 4 points."},
             {"label": "SHARE OF SHELF", "value": "31%", "text": "Core categories."},
             {"label": "COMPLIANCE", "value": "92%", "text": "Planogram compliance."}])
d.add("graphs.1_sub", heading="SELL-OUT GROWTH", subheading="VALUE SALES, R MILLION",
      chart={"categories": ["Jul", "Aug", "Sep"], "series": {"2025": [41.2, 43.0, 44.1], "2026": [45.8, 48.3, 50.6]}})
d.add("tables.clean", heading="PERFORMANCE BY ACCOUNT", intro="Q3 actuals",
      table={"header": ["ACCOUNT", "OSA", "SHARE", "PROMO"],
             "rows": [["Retailer A", "97%", "33%", True], ["Retailer B", "95%", "30%", False]]})
d.add("org.tree", heading="YOUR TEAM", tree={"name": "Jane Doe", "role": "Client Lead", "children": [
      {"name": "Sipho Dlamini", "role": "Field Manager"}, {"name": "Maria Silva", "role": "Insights Lead"}]})
d.add("stats.1_photo", heading="ONE NUMBER THAT MATTERS", value="89%", label="RESOLVED IN 48H",
      text="Out-of-stocks fixed within two days.", photo=assets.photo("merchandiser_snacks_aisle"))
d.add("thankyou.c", subheading="NEXT STEPS", message="Thank you for a strong quarter.",
      body=["Agree Q4 targets", "Monthly reviews"])
d.save("acme_q3.pptx")
```

## 10. More detail

| need | file |
|---|---|
| every value format with examples | [docs/content-formats.md](docs/content-formats.md) |
| recipes, slots, items, limits explained | [docs/concepts.md](docs/concepts.md) |
| JSON format and exit codes | [docs/json-spec.md](docs/json-spec.md) |
| every function / CLI command | [docs/api-reference.md](docs/api-reference.md) |
| every error and its fix | [docs/troubleshooting.md](docs/troubleshooting.md) |
| every recipe with a thumbnail | [CATALOG.md](CATALOG.md) / [catalog.json](catalog.json) |
| a 13-slide worked example | [examples/demo.py](examples/demo.py), [examples/deck_spec.json](examples/deck_spec.json) |
