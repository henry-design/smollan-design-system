# Getting started

This guide takes you from nothing to a finished Smollan deck in about ten minutes.

- [1. Install](#1-install)
- [2. Install the font](#2-install-the-font)
- [3. Your first deck (Python)](#3-your-first-deck-python)
- [4. Your first deck (JSON, no Python code)](#4-your-first-deck-json-no-python-code)
- [5. Find the right slide](#5-find-the-right-slide)
- [6. When something goes wrong](#6-when-something-goes-wrong)
- [7. Next steps](#7-next-steps)

---

## 1. Install

You need **Python 3.10 or newer**. Check with `python --version`.

```bash
pip install git+https://github.com/henry-design/smollan-design-system
```

This installs the `smollan` Python package, the `smollan` command, and the bundled data: the master
template, 21 photos and the Montserrat fonts. Its dependencies (`python-pptx`, `lxml`, `Pillow`)
install automatically.

Check it worked:

```bash
smollan version          # -> 1.0.0
smollan list cover       # lists the 18 cover recipes
```

> **"smollan is not recognized"?** The command lives in Python's `Scripts` folder, which may not be
> on your PATH. `python -m smollan ...` always works instead of `smollan ...`.

To upgrade later, run `pip install --upgrade git+https://github.com/henry-design/smollan-design-system`.

## 2. Install the font

Smollan headings use **Montserrat**. Without it, PowerPoint substitutes another font and the decks
look slightly off. Install it once per computer:

```bash
smollan install-fonts
```

This works on Windows, macOS and Linux and needs no admin rights. Restart PowerPoint afterwards.
The font files are also in `smollan/assets/fonts/` if you prefer to install them by hand
(select all, right-click, Install).

## 3. Your first deck (Python)

Create `my_deck.py`:

```python
from smollan import Deck

deck = Deck(
    title="Q3 BUSINESS REVIEW",          # cover title (ALL CAPS by convention)
    presenter="Jane Doe, Client Lead",
    date="OCTOBER 2026",
    client="Acme Foods",                 # replaces any [Client] text in the templates
)

deck.add("title.one_line_sub",
         heading="AGENDA",
         subheading="What we will cover today",
         body=["Q3 performance", "How we delivered", "Next steps"])

deck.add("stats.3",
         heading="Q3 RESULTS AT A GLANCE",
         items=[
             {"label": "AVAILABILITY",   "value": "96%", "text": "On-shelf availability, up 4 points."},
             {"label": "SHARE OF SHELF", "value": "31%", "text": "Share of shelf in core categories."},
             {"label": "COMPLIANCE",     "value": "92%", "text": "Planogram compliance."},
         ])

deck.add("graphs.1_sub",
         heading="SELL-OUT GROWTH",
         subheading="VALUE SALES, R MILLION",
         chart={"categories": ["Jul", "Aug", "Sep"],
                "series": {"2025": [41.2, 43.0, 44.1], "2026": [45.8, 48.3, 50.6]}})

deck.save("q3_review.pptx")
```

Run it:

```bash
python my_deck.py
# saved q3_review.pptx: 5 slides; preflight: clean
```

Open `q3_review.pptx`. You get the Smollan cover, your three slides, and the Smollan closing slide,
all fully editable.

What happened:

1. `Deck(...)` opened the master template and **added a cover** (`cover.dark_blue` by default).
2. Each `deck.add(recipe_id, ...)` **copied that recipe's template slide** and replaced its
   placeholder text, table and chart with your content, keeping the template's fonts, sizes and
   colours.
3. Slots you didn't fill were **removed**, so no "Click to edit" text is left behind.
4. `save()` **added the closing slide**, removed unused layouts to keep the file small, and ran the
   **preflight check**.

## 4. Your first deck (JSON, no Python code)

Any tool or agent that can write a file and run a command can build decks. Save this as `deck.json`:

```json
{
  "deck": {"title": "Q3 BUSINESS REVIEW", "presenter": "Jane Doe", "date": "OCTOBER 2026"},
  "slides": [
    {"recipe": "stats.3", "heading": "Q3 RESULTS AT A GLANCE", "items": [
      {"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability, up 4 points."},
      {"label": "SHARE OF SHELF", "value": "31%", "text": "Share of shelf in core categories."},
      {"label": "COMPLIANCE", "value": "92%", "text": "Planogram compliance."}
    ]}
  ],
  "output": "q3_review.pptx"
}
```

```bash
smollan build deck.json
```

Exit code `0` means the deck is clean. `1` means there was an error or a preflight issue, and the
message says which. See [json-spec.md](json-spec.md) for the full format.

## 5. Find the right slide

Each slide should carry **one message**. Pick the recipe that matches its shape:

| You want to show... | Try |
|---|---|
| 3 headline numbers | `stats.3` |
| a 5-step method | `process.5` |
| 6 services / benefits | `buckets.6` |
| a trend | `graphs.1_sub` |
| a comparison table | `tables.clean` |
| a team | `org.tree` |
| why choose Smollan | `why.pillars` |

Or search:

```bash
smollan find "team structure"          # ranked suggestions
smollan list process                   # every recipe in a category
smollan show process.5                 # what that recipe needs
```

In Python, use `find(...)`, `show(...)` and `describe(...)`, which returns the text instead of printing it. For pictures of every
recipe, open [CATALOG.md](../CATALOG.md).

## 6. When something goes wrong

The library refuses to produce off-brand slides and tells you how to fix the content:

```text
SmollanError: stats.3 holds 3 items; you passed 4. Recipes in 'stats' that take 4:
['stats.4_photo', 'stats.4_cards', 'stats.bubbles', 'stats.4_rings_dark']
```

```text
SmollanError: kpis.5.intro: ~3 lines but this slot holds 2 (about 48 characters).
Shorten the copy - do not shrink the font.
```

Do what the message says: shorten the text, or switch to one of the suggested recipes.
[troubleshooting.md](troubleshooting.md) lists every error and its fix.

## 7. Next steps

- [concepts.md](concepts.md): how recipes, slots, items and limits work
- [content-formats.md](content-formats.md): every kind of value you can pass (charts, tables, org charts...)
- [api-reference.md](api-reference.md): every function and CLI command
- `examples/demo.py`: a realistic 13-slide deck to copy from
