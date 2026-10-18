# Smollan Design System

> **AI agents: read [AGENTS.md](AGENTS.md) first.** It is the complete manual for building decks with this repo.
> (`llms.txt`, `CLAUDE.md`, `GEMINI.md` and `.github/copilot-instructions.md` all point to it.)

`smollan.py` is the Smollan PowerPoint template system as code. All 190 slide designs from the
Core Template and packs 1-14 (Growth Teams tables included) are **recipes**. An agent decides
what to say, picks the recipe that fits each message, and the script builds an on-brand,
fully editable `.pptx`.

```
smollan_design_system/
├── smollan.py              <- the design system: brand tokens, 190 recipes, Deck API, validation, CLI
├── smollan_master.pptx     <- every Smollan layout merged into one master + one template slide per recipe
├── CATALOG.md              <- quick picker + every recipe with thumbnail, slots, limits and an example call
├── catalog.json            <- the same data, machine-readable
├── thumbnails/<id>.png     <- what each recipe looks like filled with content
├── assets/photos/          <- 21 opt-in stock photos from the packs (index.json has descriptions/tags)
├── assets/fonts/           <- Montserrat, all 18 weights (OFL licence) - install on any PC that builds or opens the decks
├── examples/demo.py        <- a realistic 13-slide client review deck (+ its .pptx and .pdf)
├── examples/selftest_all_recipes.pptx  <- every recipe filled with sample content
└── tools/                  <- rebuild pipeline (only needed when the PPT packs change)
```

## Setup

Requires Python 3.10+ and `python-pptx` (`pip install python-pptx`). Keep `smollan_master.pptx`
and `assets/` next to `smollan.py`. Rendering previews/PDFs (`tools/render.ps1`) needs Windows with
PowerPoint; building decks does not.

## How an agent uses it

1. **Plan the story**: sections, with one message per slide.
2. **Pick a recipe for each message**: use the *Quick picker* in `CATALOG.md`, the one-line index at the top
   of `smollan.py`, or `find("three statistics with photos")`.
3. **Check its slots**: run `show("stats.3")` (or `python smollan.py show stats.3`) to see the slots,
   line/character limits, item count and an example call.
4. **Build**:

```python
from smollan import Deck, assets

deck = Deck(title="Q3 BUSINESS REVIEW", presenter="Jane Doe, Client Lead", date="OCTOBER 2026",
            client="Acme Foods")                       # cover added automatically
deck.add("stats.3", heading="Q3 RESULTS AT A GLANCE",
         items=[{"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability, up 4 pts."},
                {"label": "SHARE OF SHELF", "value": "31%", "text": "Core categories."},
                {"label": "COMPLIANCE", "value": "92%", "text": "Planogram compliance."}])
deck.add("graphs.1_sub", heading="SELL-OUT GROWTH", subheading="R MILLION",
         chart={"categories": ["Jul", "Aug", "Sep"], "series": {"2025": [41, 43, 44], "2026": [46, 48, 51]}})
deck.add("org.tree", heading="YOUR TEAM", tree={"name": "Jane Doe", "role": "Client Lead",
         "children": [{"name": "Sipho Dlamini", "role": "Field Manager"}]})
deck.save("acme_q3.pptx")                              # closing slide + preflight check
```

**Slot values:**
- **text:** a `str`, or a `list[str]` for bullets/paragraphs. `"- "` indents a bullet one level, `"\n"` adds a line break, `**bold**` makes text bold.
- **photo:** a file path or `assets.photo("merchandiser_snacks_aisle")`. Missing photos leave an empty picture slot, which the save step reports.
- **chart:** `{"type": "column|bar|line|pie|doughnut|stacked_*|area|waterfall", "categories": [...], "series": {...}}`. Leave out `type` to keep the template's own chart styling.
- **table:** `{"header": [...], "rows": [[...]], "footer": [...]}`. In cells, `True` means a tick or dot and `False` a cross.
- **tree** (org charts): nested `{"name", "role", "photo"?, "children": [...]}`.

**Guard-rails:** content that breaks a template rule raises `SmollanError` with the fix. This covers
text longer than a box holds, the wrong number of items (it lists the recipes that do fit), more than
8 process steps, and org charts too big for one slide. Shorten the copy or switch recipe; never shrink
the type. Any `[Client]` in the template wording is replaced with `Deck(client=...)`.
Fixed Smollan wording (Thank You headings, Why-Smollan pillars, feedback headings) is kept unless you
override it.

## Rebuilding after the PPT packs change

```
python tools/build_master.py "G:/Other computers/My Computer/SMOLLAN/PPT Packs"   # merge packs -> smollan_master.pptx
python tools/scrub_master.py           # remove client-specific example content (names list: tools/scrub_names.local.json)
python tools/analyze_slots.py          # infer slots/limits -> tools/auto_specs.json
python tools/gen_registry.py           # curation.py + auto specs -> RECIPES block in smollan.py
python tools/selftest.py               # build every recipe; must report 0 failures, preflight clean
powershell -File tools/render.ps1 -Pptx examples/selftest_all_recipes.pptx -Out <dir>   # eyeball + thumbnails
python smollan.py catalog              # regenerate CATALOG.md / catalog.json
```

Recipe ids, descriptions and slot overrides live in `tools/curation.py`. Edit that file, not the
generated `RECIPES` block.

## Known limits

- **Montserrat** must be installed to see decks true to brand: install the fonts in `assets/fonts/`
  (select all -> right-click -> Install). Thumbnails and the demo PDF are rendered in Montserrat.
- **Line limits** are estimates from box size and the templates' own "no longer than N lines"
  instructions. They err on the strict side.
- **SmartArt** org-chart placeholders are replaced by charts drawn from your tree data, in Smollan colours.
- **The graphs pack waterfall** is an Office 2016 chart type that python-pptx cannot edit, so `"type": "waterfall"`
  emulates it with a native stacked column chart.
- **Photo covers** keep their designed photography. The gauge arcs in `stats.3_gauges_photos` are drawn
  shapes and do not resize with the value.
- **Fixed-structure tables:** presets with merged cells, mostly Growth Teams, need the exact template grid,
  which each table slot's hint describes.

## Notice

- The Smollan name, logo, slide designs and photography are the property of Smollan and are included
  so the design system can reproduce the brand. They are not licensed for other use.
- Example content from client work has been replaced with neutral placeholders (`tools/scrub_master.py`).
- Montserrat is (c) The Montserrat Project Authors, licensed under the SIL Open Font License 1.1.
