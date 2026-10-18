# AGENTS.md - how an AI agent uses the Smollan Design System

You are building a **Smollan-branded PowerPoint deck**. Do not draw slides from scratch. This repo
contains every official Smollan slide design as a **recipe**: 190 recipes across 16 categories. You
pick a recipe for each message and pass your content, and `smollan.py` produces an editable `.pptx`
that matches the brand templates.

## 1. Setup (once)

```bash
pip install -r requirements.txt          # python-pptx (+ lxml, Pillow)
```

- Run from the repo root, or put it on `sys.path`. `smollan.py` needs `smollan_master.pptx` and
  `assets/` beside it. Never move it on its own.
- Fonts: install `assets/fonts/*.ttf` (Montserrat) on the machine that opens the decks.

## 2. Workflow (follow it in order)

1. **Plan the story.** List the slides as one message each, grouped into sections.
2. **Choose a recipe per slide.**
   - Look at the category table (section 4), or
   - run `find("plain English need")`, which returns ranked recipe ids, or
   - read the `CATALOG SUMMARY` comment block at the top of `smollan.py`, or browse `CATALOG.md`
     (it has thumbnails at `thumbnails/<id>.png`).
3. **Read the recipe spec** before filling it: `describe("<id>")` returns a string; `show("<id>")`
   prints it; on the command line, `python smollan.py show <id>`. It gives every slot, its kind, line and
   character limits, the exact item count, notes and a ready-to-edit example call.
4. **Build:** `Deck(...)`, then `deck.add("<id>", **slots)` for each slide, then `deck.save("out.pptx")`.
5. **Handle `SmollanError`.** The message says exactly what is wrong and what to do: shorten the
   copy, or use one of the recipe ids it lists. Fix it and call `add` again. Never work around a
   limit by shrinking fonts or editing the XML.
6. **Read the preflight list** that `save()` prints and returns: leftover template text and empty
   photo slots. Fix what matters and save to a new `Deck`.

## 3. API

```python
from smollan import Deck, find, describe, show, alternatives, assets, RECIPES, SmollanError

deck = Deck(title="Q3 BUSINESS REVIEW", presenter="Name Surname, Title", date="OCTOBER 2026",
            subtitle=None, client="Acme Foods",          # client replaces every [Client] token
            cover="cover.dark_blue", closing="closing",  # any cover.* / closing recipe
            auto_cover=True, auto_closing=True)
deck.add("<recipe id>", heading="...", items=[{...}, ...], ...)   # returns the slide
issues = deck.save("deck.pptx")      # adds closing, removes unused layouts, runs preflight
```

| call | purpose |
|---|---|
| `find(query, n=8)` | ranked recipe ids for a need, e.g. `find("4 steps with timeline")` (prints + returns list) |
| `describe(id)` / `show(id)` | full spec of one recipe (string / printed) |
| `alternatives(id, count)` | other recipes in the same category that take `count` items |
| `RECIPES[id]` | raw spec dict: `slots`, `items`, limits, `summary`, `use_when`, `avoid_when`, `notes` |
| `assets.photos(tag)` / `assets.photo(name)` | list / get stock photos (opt-in) |
| `python smollan.py list [category] \| show <id> \| find <words> \| photos [tag] \| catalog` | CLI |

A `Deck` can be saved once; create a new one to start over.

## 4. Choosing a recipe

| Message type | Category | Good default | Notes |
|---|---|---|---|
| Opening | `cover` | `cover.dark_blue` | `cover.photo.*` = photo-led; `cover.photo.rfp_client` for tenders |
| Section break | `divider` | `divider.dark_blue` | match the cover's colour tone |
| Heading + text / bullets | `title` | `title.one_line_sub` | the fallback for plain text |
| 1-5 headline numbers | `stats` | `stats.3` | `stats.1_photo`, `stats.4_cards`, `stats.5_photos`... |
| What we will measure | `kpis` | `kpis.5` | `kpis.6`, `kpis.7`, `kpis.table`, `kpis.strategic_table` |
| Step-by-step method | `process` | `process.5` | 3-8 steps. **Max 8 per slide** |
| Concept / framework | `infographic` | `infographic.triad` | triangle, Venn (`pivot_point`), loop, cycle, `swot` |
| N parallel points | `buckets` | `buckets.6` | 4/5/6/8, with or without photos |
| Chart | `graphs` | `graphs.1` | 1 or 2 charts; with intro / text column / takeaways |
| Table | `tables` | `tables.clean` | many presets: gantt, tick matrix, comparisons, Growth Teams styles |
| Team structure | `org` | `org.tree` | drawn from tree data; `org.bespoke_*` = fixed shapes |
| Client survey results | `feedback` | `feedback.chart_quote` | |
| App / dashboard screenshot | `devices` | `devices.laptop_large` | phones, browser, video |
| Why choose Smollan | `why` | `why.pillars` | `why.differentiators*` for up to 8 custom reasons |
| Thank you / next steps | `thankyou` | `thankyou.c` | ends the deck instead of `closing` |
| End | `closing` | `closing` | added automatically |

Item counts are exact. For example, `stats.3` takes exactly 3 items. If your content has a different
count, use a sibling recipe (`alternatives(id, count)`) or split the content across slides.

## 5. Slot values

Pass slots as keyword arguments. Repeated blocks go in `items=[{field: value}, ...]`, one dict per
block, in reading order (left to right, then top to bottom; process steps in step order).

| kind | value |
|---|---|
| text | `str`, or `list[str]` = paragraphs/bullets. `"- "` prefix = indented bullet, `"\n"` = line break, `**bold**` = emphasis |
| photo | file path, or `assets.photo("<name>")`. Cropped to fill. Omit = empty picture slot |
| chart | `{"type": T, "categories": [...], "series": {"Name": [numbers]}, "title": opt, "labels": opt bool, "number_format": opt}`. T is one of `column bar line line_plain pie doughnut stacked_column stacked_100 stacked_bar stacked_bar_100 area stacked_area waterfall`. **Omit `type` to keep the template chart's own type and styling.** Waterfall: one series plus `"totals": [index, ...]` |
| table | `{"header": [...] or [[...]], "rows": [[...], ...], "footer": [...]}`. Cell values: `str`, `list[str]`, `True` = tick/dot, `False` = cross, `None` = blank. Free-form presets clone rows/columns; **fixed presets** (merged cells) need the exact grid stated in the slot hint |
| gantt | `{"periods": ["1", ...], "tasks": [{"label": "...", "start": 1, "end": 3}], "corner": "WEEK"}` (`tables.gantt`) |
| org | `{"name": "...", "role": "...", "photo": optional path, "children": [ ...same shape... ]}`. Max 5 levels / 8 columns; leaf groups stack automatically |
| video | path to an `.mp4` (`devices.laptop_video`) |

- **Omitted slots** are removed from the slide, so no template text is left behind.
- **Slots marked `keep`** hold standard Smollan wording ("THANK YOU", the four pillars, "WHAT MAKES
  SMOLLAN UNIQUE?"). It stays unless you pass your own text.

## 6. Rules

- **One message per slide.** If content doesn't fit, pick a bigger recipe or split it. Never shrink the type.
- **Headings are short and ALL CAPS** by template convention. Respect each slot's `max_lines` / `cpl` (characters per line).
- **Greens are the focal colour**, used for one thing per slide. Use `Brand.*` colours if you style anything yourself.
- **Do not alter the brand**: no recolouring, font swaps or removing the Smollan logo or footer.
- **Do not invent recipe ids or slot names.** Use `find` / `describe`; an unknown name raises `SmollanError` with the valid list.
- **Never claim a deck is final** while preflight reports leftover text.

## 7. Complete example

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

There is a longer version in `examples/demo.py`, and its output is `examples/demo_client_review.pdf`.

## 8. Where things are

| file | what |
|---|---|
| `smollan.py` | everything: catalog summary (top), brand tokens, engine, `RECIPES` (generated, the full spec of every recipe), CLI |
| `CATALOG.md` | human-readable catalog with thumbnails, slot tables and example calls |
| `catalog.json` | machine-readable `{"categories": {...}, "recipes": {...}}` |
| `thumbnails/<id>.png` | preview of each recipe filled with sample content |
| `assets/photos/index.json` | stock photo names, descriptions, tags |
| `tools/` | maintenance pipeline (rebuild from the original PPT packs). Agents building decks don't need it |
