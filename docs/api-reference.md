# API reference

Everything below can be imported from the top-level package: `from smollan import ...`.

- [Deck](#deck)
- [Finding and inspecting recipes](#finding-and-inspecting-recipes)
- [Building from JSON](#building-from-json)
- [Photos and fonts](#photos-and-fonts)
- [Brand tokens](#brand-tokens)
- [Errors](#errors)
- [Low-level helpers](#low-level-helpers)
- [Command line](#command-line)
- [Module map](#module-map)

---

## Deck

```python
Deck(title=None, presenter=None, date=None, subtitle=None, client=None,
     cover="cover.dark_blue", closing="closing", auto_cover=True, auto_closing=True,
     logo=None, master=MASTER_PATH)
```

Creates a new deck from the bundled master template.

| parameter | meaning |
|---|---|
| `title` | cover title. Use `"\n"` for a second line. ALL CAPS by convention |
| `presenter`, `date`, `subtitle` | cover text. Each is only used if the chosen cover has that slot |
| `client` | client name: replaces `[Client]` / `[CLIENT]` / `[Client X]` tokens on every slide |
| `logo` | path to the client's logo: placed on every slide that has a `logo` slot (RFP cover, many tables). Without it, those logo spots are removed |
| `cover` | any `cover.*` recipe id |
| `closing` | the recipe added at the end (`"closing"` by default) |
| `auto_cover` | `False` = no cover. Add one yourself with `add_cover` or `add` |
| `auto_closing` | `False` = don't add the closing slide on save |
| `master` | path to an alternative master file (advanced) |

### `deck.add(recipe, **content) -> Slide`

Adds one slide built from `recipe` (an id, an original layout name or a template key) and fills it
with `content`: keyword arguments named after the recipe's slots, plus `items=[...]` for repeated
blocks.

- Validates everything first, so nothing is added if there's a problem: it raises `SmollanError`.
- Returns the python-pptx `Slide`, so advanced users can adjust it further.

```python
deck.add("stats.3", heading="RESULTS", items=[{...}, {...}, {...}])
```

### `deck.add_cover(recipe="cover.dark_blue", title=None, subtitle=None, presenter=None, date=None, **extra)`

Adds a cover. Only the arguments the cover recipe has slots for are used, so you can pass the same
values to any cover. Use it with `auto_cover=False` to place the cover yourself.

### `deck.save(path, preflight=True) -> list[str]`

Finishes and writes the `.pptx`:

1. Adds the closing slide (unless `auto_closing=False`, or the last slide is already a `closing` or
   `thankyou` recipe).
2. Removes the template slides and every unused layout.
3. Writes the file.
4. Runs the preflight check and prints the result.

Returns the list of issues: leftover template text and empty photo slots. An empty list means the
deck is clean. A `Deck` can only be saved once.

### Attributes

| attribute | meaning |
|---|---|
| `deck.prs` | the underlying python-pptx `Presentation` |
| `deck.recipes_used` | recipe ids added so far, in order |
| `deck.log` | notes collected while building (e.g. empty photo slots) |

## Finding and inspecting recipes

| function | returns | description |
|---|---|---|
| `find(query, n=8, show=True)` | `list[str]` | rank recipes for a plain-English need, e.g. `find("5 steps with photos")`. Understands synonyms (team = org, steps = process, chart = graphs...) and boosts recipes that hold the number you mention. Prints unless `show=False` |
| `describe(rid)` | `str` | the full spec as text: summary, use / avoid, notes, slots with limits, items, alternatives, example call |
| `show(rid)` | `None` | prints `describe(rid)` |
| `resolve(name)` | `str` | turns a recipe id, an original layout name (`"HEAD + 3 x Stats"`) or a template key (`"p13.s08"`) into a recipe id |
| `alternatives(rid, count=None)` | `list[str]` | other recipes in the same category (that take `count` items, if given) |
| `example_call(rid)` | `str` | a ready-to-edit `deck.add(...)` snippet |
| `validate(rid, content)` | `list[str]` | the checks `add()` runs, without building anything. Returns error messages |
| `RECIPES` | `dict` | the raw registry: `{id: spec}` |
| `CATEGORY_INFO` / `CATEGORY_ORDER` | `dict` / `list` | category descriptions and display order |
| `catalog(write=True, out_dir=None)` | `str` | regenerates `CATALOG.md` + `catalog.json` (in the repo root, or `out_dir`) |

A recipe spec (`RECIPES[id]`) looks like:

```python
{"src": "p13.s08", "category": "stats", "title": "3 big stats (dark band)", "summary": "...",
 "use_when": "...", "avoid_when": "...", "tags": [...], "pack": "13  -  Stats.pptx",
 "layout": "HEAD + 3 x Stats", "notes": [...],
 "slots": {"heading": {"ref": "ph:0", "kind": "text", "max_lines": 1, "cpl": 50, "cap": 1, "hint": "..."}},
 "items": {"n": 3, "min": 3, "fields": {"value": {"refs": ["ph:59", "ph:74", "ph:78"], "kind": "text", ...}}}}
```

`ref` / `refs` point to shapes on the template slide (`ph:<placeholder idx>`, `id:<shape id>`,
`cell:<table id>:<row>:<col>`). They're internal; you never pass them.

## Building from JSON

### `build_from_spec(spec, out=None, base_dir=None) -> list[str]`

Builds and saves a deck from a JSON file path or a dict. See [json-spec.md](json-spec.md). Returns
the preflight issues. Raises `SmollanError` naming the failing slide (`slides[3] (stats.3): ...`).

## Photos and fonts

| call | description |
|---|---|
| `assets.photos(tag=None, show=True)` | `[(name, description), ...]` for the bundled photos, optionally filtered by a tag or word ("merchandiser", "beauty", "office", "shelf"...) |
| `assets.photo(name)` | absolute path of a bundled photo, to pass as a photo slot value |
| `install_fonts()` | installs Montserrat for the current user (Windows, macOS, Linux) and returns the installed paths |
| `PHOTO_DIR`, `FONT_DIR`, `MASTER_PATH`, `HERE` | paths inside the installed package |

## Brand tokens

`Brand` holds the Smollan design constants. Use them if you add anything custom to a slide.

| token | value | use |
|---|---|---|
| `Brand.DARK_BLUE` | `#00284E` | primary brand colour, covers, headings |
| `Brand.BLUE` | `#005083` | primary accent, table headers, first chart series |
| `Brand.CYAN_BLUE` | `#0079C0` | accent |
| `Brand.BRIGHT_CYAN` | `#00BBF0` | tertiary accent |
| `Brand.MID_BLUE` | `#549AD3` | soft accent |
| `Brand.CHARCOAL` | `#37465B` | body emphasis |
| `Brand.NEAR_BLACK` | `#0E1D29` | dark backgrounds |
| `Brand.GREEN` | `#16B795` | **focal colour**: one element per slide |
| `Brand.LIME` | `#8AC546` | positive deltas |
| `Brand.PALE` | `#EFF2F6` | panels, zebra rows |
| `Brand.GREY_BLUE` | `#B4C3CE` | dividers, connectors |
| `Brand.WHITE` | `#FFFFFF` | |
| `Brand.SERIES` | list | chart series colour order |
| `Brand.HEADING_FONT` / `BODY_FONT` | `"Montserrat"` / `"Calibri"` | typography |
| `Brand.SLIDE_W`, `SLIDE_H`, `MARGIN`, `CONTENT_TOP`, `CONTENT_BOTTOM` | EMU | 16:9 geometry |
| `Brand.LEFTOVER_PATTERNS` | list of regex | what preflight treats as leftover template text |

## Errors

`SmollanError` (a subclass of `ValueError`) is raised for any content that breaks a rule. Its message
always says what to change. See [troubleshooting.md](troubleshooting.md) for the full list.

## Low-level helpers

For custom slides or advanced tweaks to a `Slide` returned by `deck.add`:

| function | description |
|---|---|
| `set_text(shape_or_cell, value)` | replace text while keeping the template formatting (str / list, `- ` levels, `\n`, `**bold**`) |
| `put_chart(slide, shape, spec)` | fill a chart frame or placeholder (see content-formats) |
| `style_chart(chart, spec)` | apply Smollan chart styling to a python-pptx chart |
| `put_table(shape, spec, header_rows=1, footer_rows=0, fixed=False)` | fill and resize a styled table |
| `put_gantt(shape, spec)` | fill the gantt preset table |
| `draw_org_chart(slide, x, y, w, h, tree, max_cols=8)` | draw an org chart in a box (EMU units) |
| `preflight_check(prs)` | run the leftover-text scan on any python-pptx `Presentation` |

## Command line

`smollan <command>` (or `python -m smollan <command>`):

| command | description |
|---|---|
| `smollan list [category]` | list recipe ids and titles |
| `smollan show <id>` | full recipe spec |
| `smollan find <words...>` | rank recipes for a need |
| `smollan build <spec.json> [out.pptx]` | build a deck from JSON. Exit code 0 = clean, 1 = error or preflight issue |
| `smollan photos [tag]` | list the bundled stock photos |
| `smollan install-fonts` | install Montserrat for the current user |
| `smollan catalog [dir]` | write `CATALOG.md` + `catalog.json` |
| `smollan path` | print the installed package folder |
| `smollan version` | print the version |

## Module map

| module | contents |
|---|---|
| `smollan.deck` | `Deck`, `preflight_check` |
| `smollan.catalog` | `find`, `describe`, `show`, `resolve`, `alternatives`, `example_call`, `catalog`, category info |
| `smollan.validation` | `validate` |
| `smollan.recipes` | `RECIPES` (generated) |
| `smollan.text` / `charts` / `tables` / `orgchart` / `shapes` | content fillers |
| `smollan.brand` | `Brand` |
| `smollan.photos` | `assets` |
| `smollan.cli` | `main`, `build_from_spec`, `install_fonts` |
| `smollan.config` | package paths |
| `smollan.errors` | `SmollanError` |
| `smollan._opc` | internal: copying slides and parts between presentations |
