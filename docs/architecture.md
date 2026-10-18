# Architecture

How the library turns Smollan's PowerPoint packs into code, and why it's built this way.

## Core idea: a "hybrid" template

Redrawing 190 designed slides in code would never match the originals pixel for pixel. Instead:

1. **One master file** (`smollan/smollan_master.pptx`) holds *every* Smollan layout (172 of them,
   merged from the Core Template and 15 pack files) plus **one template slide per design**, filled with
   the designer's example content.
2. **A registry** (`smollan/recipes.py`) describes each template slide as a *recipe*: which shapes are
   fillable slots, what kind of content each takes, how much text fits, and when to use it.
3. **The engine** copies a template slide, swaps in your content while keeping the slide's own
   formatting, deletes what you didn't use, and saves only the layouts your deck needs.

The output is a normal PowerPoint deck built on the real Smollan master, so it is identical to
hand-made work and fully editable.

## Package layout

```
smollan/
  __init__.py     public API: re-exports, version
  config.py       paths to bundled data (MASTER_PATH, PHOTO_DIR, FONT_DIR)
  errors.py       SmollanError
  brand.py        Brand tokens
  recipes.py      RECIPES - generated registry (data only)
  catalog.py      resolve / find / describe / show / alternatives / CATALOG.md generator
  validation.py   validate(): limits, counts, names
  deck.py         Deck (+ preflight_check, client-name replacement)
  text.py         set_text(): formatting-preserving text replacement
  shapes.py       slot reference lookup (ph:/id:/cell:), photos, video, safe shape removal
  charts.py       chart data, Smollan chart styling, waterfall emulation
  tables.py       table resizing by cloning rows/columns, tick symbols, gantt
  orgchart.py     org chart layout and drawing
  photos.py       stock photo library
  cli.py          `smollan` command, JSON builder, font installer
  _opc.py         copying slides/parts between and within packages (internal)
```

Dependencies only point downwards (`deck` uses the fillers, which use `brand`, `errors` and `text`),
so there are no import cycles. Generated data (`recipes.py`) is kept apart from hand-written code.

## What happens in `deck.add(id, **content)`

1. **Resolve** the id (also accepts original layout names).
2. **Validate**: slot names, item counts, text length estimates and special rules. On failure,
   raise `SmollanError` before touching the deck.
3. **Copy the template slide** into the deck. Its charts get fresh copies of their parts and
   embedded workbooks. Images are shared by hash. The layout link is kept.
4. **Fill each slot** by looking up its shape (`ph:<idx>` placeholder, `id:<shape id>`, or
   `cell:<table>:<r>:<c>`):
   - **text**: rebuild the paragraphs, using the template's own paragraph and run properties as
     the model for each level.
   - **photo**: reset to the layout's picture placeholder and insert the image, cropped to fill.
   - **chart**: `replace_data` on the template chart when the type matches; otherwise a new
     native chart is created and styled.
   - **table**: clone or remove rows and columns, then write cells, reusing the template's tick
     and dot runs.
   - **org**: remove the placeholder and draw boxes and connectors in its area.
5. **Remove unfilled slots**: placeholders are deleted, so their layout prompts never render.
   Office 2016 chart blocks (`mc:AlternateContent`) are removed whole.
6. **Replace `[Client]`** tokens, renumber shape ids and drop unused relationships.

## What happens in `deck.save(path)`

Add the closing slide, delete all template slides, delete unused layouts (which removes their
images from the file), make part names unique, write the file, then run the preflight scan.

## How the registry was made

`tools/build_master.py` merges the packs. Their slide masters were verified identical apart from
their layout lists, so all layouts can live in the Core master. Content that designers had baked
into layouts (Why-Smollan pillars and differentiator tables, KPI tables, a doughnut chart, feedback
headings, SWOT labels) is moved onto the template slides so it becomes editable.
`tools/analyze_slots.py` infers slot roles from each placeholder's prompt text ("Insert
introductory text..." means intro, "56%" means value) and groups repeated same-size blocks into
items in reading order. Text limits come from box geometry, calibrated with Montserrat character
widths and the templates' "no longer than N lines" instructions. `tools/curation.py` adds the human
part: ids, descriptions, when to use each recipe, and explicit slot maps for irregular layouts.
See [maintenance.md](maintenance.md).

## Design decisions

| Topic | Decision | Why |
|---|---|---|
| Fidelity | template slides from a merged master, not shapes drawn in code | pixel-identical to the brand packs |
| Interface | Python API + JSON/CLI | Python for scripts and agents; JSON for any other tool |
| Org charts | drawn from tree data | SmartArt can't be generated by python-pptx |
| Layout-baked content | moved onto slides | makes it editable |
| Charts | native and editable; template styling reused when the type matches | clients can edit the data |
| Rule breaks | error with a suggested fix | never produce off-brand output silently |
| Missing photos | empty slot, reported | no surprise stock imagery |
| Client data | scrubbed before publishing (`scrub_master.py`) | the repository is public |
| Packaging | installable package with bundled data | `pip install`, then use it from anywhere |

## Testing

`tools/selftest.py` builds all 190 recipes with generated sample content and fails on any error.
Each release is also opened and rendered in PowerPoint (`tools/render.ps1`) and checked by eye. The
self-test deck and examples must report `preflight: clean`.
