# Building decks from JSON

Agents and tools that don't write Python can describe a deck as **JSON** and build it with one command:

```bash
smollan build deck.json                 # output path taken from the file ("output")
smollan build deck.json out/q3.pptx     # or given explicitly
python -m smollan build deck.json       # same, if the smollan command isn't on PATH
```

From Python: `smollan.build_from_spec("deck.json")` or `build_from_spec(dict_spec, out="q3.pptx")`.

## Format

```json
{
  "deck": {
    "title": "Q3 BUSINESS REVIEW\nACME FOODS",
    "presenter": "Jane Doe, Client Lead",
    "date": "OCTOBER 2026",
    "client": "Acme Foods",
    "cover": "cover.photo.merchandiser"
  },
  "slides": [
    {"recipe": "stats.3", "heading": "Q3 RESULTS", "items": [ {...}, {...}, {...} ]},
    {"recipe": "graphs.1_sub", "heading": "SALES", "chart": {"categories": [...], "series": {...}}}
  ],
  "output": "q3_review.pptx"
}
```

| key | required | meaning |
|---|---|---|
| `deck` | no | arguments for `Deck(...)`: `title`, `presenter`, `date`, `subtitle`, `client`, `logo` (path), `cover`, `closing`, `auto_cover`, `auto_closing` |
| `slides` | yes | the slides in order. Each object has a `"recipe"` id plus the recipe's slots, exactly as in Python |
| `output` | no | the `.pptx` path (default `deck.pptx`). A relative path is resolved from the JSON file's folder |

**Values** follow [content-formats.md](content-formats.md). JSON-specific points:

- `true` / `false` in table cells become ticks and crosses; `null` means not provided (or a running
  total in a waterfall).
- **Photos:** `"asset:merchandiser_woman_shelf"` uses a bundled photo. A relative image or video
  path (`"photos/store.jpg"`) is resolved from the JSON file's folder.
- **Line breaks:** write `\n` inside strings.

## Results and errors

| exit code | meaning |
|---|---|
| `0` | deck saved, preflight clean |
| `1` | a `SmollanError` (printed to stderr, naming the slide: `slides[3] (stats.3): ...`), or the deck saved with preflight issues (printed) |
| `2` | unknown command |

When a slide fails, nothing is saved. Fix that slide's content and run the command again.

## Complete example

[examples/deck_spec.json](../examples/deck_spec.json) builds a 9-slide deck: photo cover, agenda,
divider, stats, waterfall chart, table, stat with stock photo, org chart and thank-you slide.

```bash
smollan build examples/deck_spec.json
# saved examples/deck_from_json.pptx: 9 slides; preflight: clean
```

## Discovering recipes without Python

```bash
smollan list                 # every recipe id + title
smollan list stats           # one category
smollan find "team chart"    # ranked suggestions
smollan show org.tree        # slots, limits, item count, example
```

The machine-readable catalog is in [catalog.json](../catalog.json):
`{"categories": {name: description}, "recipes": {id: spec}}`. Each spec has the same `slots`,
`items`, limits and descriptions that `show` prints.
