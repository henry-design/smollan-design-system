# Concepts

Five ideas explain the whole library: **recipes, slots, items, limits and guard-rails**.

- [Recipes](#recipes)
- [Slots](#slots)
- [Items](#items)
- [Limits](#limits)
- [Kept wording and the client name](#kept-wording-and-the-client-name)
- [Guard-rails and preflight](#guard-rails-and-preflight)
- [Reading a recipe spec](#reading-a-recipe-spec)
- [How a deck is assembled](#how-a-deck-is-assembled)

---

## Recipes

A **recipe** is one official Smollan slide design that the library knows how to fill. There are 190,
taken from the Core Template and the 14 slide packs.

Recipe ids are `category.variant`:

```
stats.3                  3 big stats on a dark band
stats.1_photo            1 big stat with a photo
process.8_circle         8-step circular process
tables.gt_scenarios      Growth Teams scenario summary table
cover.photo.merchandiser photo cover with a Smollan merchandiser
```

Each recipe records:

| field | meaning |
|---|---|
| `title`, `summary` | what it looks like |
| `use_when`, `avoid_when` | when to choose it |
| `slots`, `items` | what content it takes (see below) |
| `notes` | special rules (e.g. "max 8 steps", "fixed table grid") |
| `pack`, `layout`, `src` | where it came from (original file, original layout name, template slide) |

You can also refer to a recipe by its **original PowerPoint layout name** (e.g. `"HEAD + 3 x Stats"`)
or its template key (e.g. `"p13.s08"`). `resolve()` turns either into the recipe id.

## Slots

A **slot** is one place on the slide that takes content: a heading, a photo, a chart. You fill slots
with keyword arguments:

```python
deck.add("stats.1_photo", heading="ONE NUMBER THAT MATTERS", value="89%", photo="shelf.jpg")
```

Every slot has a **kind**, which decides what value it accepts:

| kind | you pass | details |
|---|---|---|
| `text` | `str` or `list[str]` | [content-formats.md](content-formats.md#text) |
| `photo` | image path | [content-formats.md](content-formats.md#photos) |
| `chart` | chart dict | [content-formats.md](content-formats.md#charts) |
| `table` | table dict | [content-formats.md](content-formats.md#tables) |
| `gantt` | gantt dict | [content-formats.md](content-formats.md#gantt) |
| `org` | org tree dict | [content-formats.md](content-formats.md#org-charts) |
| `video` | `.mp4` path | [content-formats.md](content-formats.md#video) |
| `logo` | image path | [content-formats.md](content-formats.md#logos): optional client logo, fitted not cropped |

Common slot names: `heading`, `subheading`, `intro`, `body`, `text`, `photo`, `chart`, `table`,
`tree`. Unusual layouts have descriptive names (`statement`, `target_value`, `circle_top`...). Always
check with `show(<id>)`. An unknown slot name raises an error that lists the valid ones.

**Slots you don't pass are removed** from the slide, so an empty sub-heading simply disappears. The
exceptions are photo slots, which stay as an empty picture placeholder and are reported, and kept
slots (see below).

## Items

Many designs repeat a block: 3 stats, 5 process steps, 6 buckets, 4 pillars. Those repeated blocks are
**items**, passed as a list of dicts in reading order:

```python
deck.add("process.5",
         heading="OUR EXECUTION MODEL",
         items=[{"heading": "PLAN",    "bullets": ["Route plans"],   "detail": "Every Monday"},
                {"heading": "EXECUTE", "bullets": ["Merchandising"], "detail": "Daily"},
                {"heading": "MEASURE", "bullets": ["Photo audits"],  "detail": "Each visit"},
                {"heading": "ANALYSE", "bullets": ["Dashboards"],    "detail": "Within 24h"},
                {"heading": "ACT",     "bullets": ["Fix gaps"],      "detail": "Within 48h"}])
```

- **The count is exact.** `process.5` takes exactly 5 items, because the design has 5 drawn steps.
  For 4 steps use `process.4_*`; for 9 or more, split across two slides. The error message lists
  recipes that take your count, and so does `alternatives(id, count)`.
- **Reading order** is left to right, then top to bottom. For circular designs it's clockwise from
  the first segment; the recipe's notes say where that is.
- A field you leave out of one item is removed from that block only.

## Limits

Every text slot knows how much text fits, from the box size, the font size and the template's own
instruction (e.g. "No longer than 3 lines maximum"):

```
text   max 5 lines, ~42 chars/line       explicit limit from the template
note   fits ~2 lines, ~44 chars/line     limit estimated from the box size
```

- `max N lines` is a hard limit stated by the designer. `fits ~N lines` is what the box holds.
- `~C chars/line` is the estimated number of characters per line in Montserrat at that size.
- So a slot holds roughly *lines × chars/line* characters. Each paragraph or bullet starts a new line.

Going over the limit raises an error before anything is built. **Shorten the copy. Never shrink
the font.** That is a brand rule. The estimate allows about 10% leeway.

## Kept wording and the client name

Some templates contain **real Smollan copy** rather than placeholder text:

- "THANK YOU / FOR THE OPPORTUNITY" on thank-you slides
- the four Why-Smollan pillars ("An exceptional offer", "A global business"...)
- "YOUR FEEDBACK HELPS US DRIVE IMPROVEMENT" on feedback slides
- "WHAT MAKES SMOLLAN UNIQUE?" on the differentiator slides

These slots are marked *optional - keeps Smollan wording*. Leave them out to keep the standard
wording, or pass your own text to override it.

**Client name:** if you create the deck with `Deck(client="Acme Foods")`, every `[Client]`,
`[CLIENT]` or `[Client X]` token in the templates becomes `Acme Foods` (or `ACME FOODS` in all-caps
text). The same applies to tokens in your own text.

## Guard-rails and preflight

Two safety nets keep decks on-brand:

1. **Validation** runs inside `add()`, before the slide is created. It checks slot names, item counts,
   text limits, the 8-step process limit and the org chart size. A problem raises `SmollanError`
   with the fix.
2. **Preflight** runs inside `save()`. It scans the finished deck for leftover template text
   ("Click to edit", "[Client]", "XX", "Name Surname", garbled characters) and reports any photo
   slots left empty. `save()` prints the issues and returns them as a list. An empty list means
   the deck is clean.

## Reading a recipe spec

`smollan show <id>` (or `show(id)` in Python) prints everything you need:

```text
process.5  -  5-step process on an arrow               <- id and title
Category : process
Source   : 10  -  Process.pptx / layout '3_Double HEAD + Intro + 5 Step' (template p10.s07)

Numbered 01-05 timeline arrow over five coloured columns ...   <- what it looks like

USE WHEN : Five-step method.
AVOID    :
NOTES:
  - Max 8 steps per slide. For more, split across two slides or use infographic.cycle.

SLOTS:                                                   <- keyword arguments
  heading        text   max 1 line, ~50 chars/line       CLICK TO INSERT ONE LINE HEADING
  subheading     text   fits ~1 line, ~60 chars/line     CLICK TO EDIT SUB-HEADING
  intro          text   max 2 lines, ~148 chars/line     Insert introductory text here...

ITEMS: exactly 5 item dicts in items=[...]               <- the repeated blocks
  heading        text   ...
  bullets        text   ...
  detail         text   ...

ALTERNATIVES: process.3, process.3_arrows, ...           <- same category

EXAMPLE:                                                 <- copy, edit, run
deck.add("process.5", heading='YOUR HEADING', ..., items=[{...}, ...])
```

The last column of each slot line is the **template's own prompt text**, which tells you what the
designer meant to go there. For tables it describes the grid instead.

## How a deck is assembled

```
Deck(...)            opens smollan_master.pptx (all layouts + one template slide per recipe)
  └ add_cover        adds the cover recipe
deck.add(id, ...)    validate -> copy the template slide (with its charts/images) -> fill slots
                     -> remove unfilled slots -> replace [Client] -> tidy shape ids
deck.save(path)      add closing -> drop template slides -> drop unused layouts -> write -> preflight
```

[architecture.md](architecture.md) explains the internals.
