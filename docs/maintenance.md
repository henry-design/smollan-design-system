# Maintenance: rebuilding, adding and changing recipes

You only need this page to **update the library itself**: when the Smollan PPT packs change, a recipe
needs a better description, or slot names need adjusting. Building decks doesn't require any of it.

Requirements: a source checkout (`git clone ...; pip install -e .`) and the original PPT packs.
Steps 5-6 (rendering) also need Windows with PowerPoint.

## The pipeline

```
PPT packs ──build_master──► smollan/smollan_master.pptx ──scrub_master──► (client data removed)
                                         │
                              analyze_slots ──► tools/auto_specs.json  (slots, roles, limits)
                                         │
              tools/curation.py ──gen_registry──► smollan/recipes.py   (RECIPES + summary)
                                         │
                                    selftest ──► examples/selftest_all_recipes.pptx
                                         │
                          render.ps1 ──► thumbnails/<id>.png ──catalog──► CATALOG.md, catalog.json
```

```bash
python tools/build_master.py "G:/path/to/PPT Packs"   # 1. merge packs into the master
python tools/scrub_master.py                          # 2. remove client-specific content
python tools/analyze_slots.py                         # 3. infer slots and limits
python tools/gen_registry.py                          # 4. write smollan/recipes.py
python tools/selftest.py                              # 5. build every recipe -> must print "0 recipe failures"
powershell -File tools/render.ps1 -Pptx examples/selftest_all_recipes.pptx -Out render_out -Width 960
#    copy render_out/NNN_<id>.png -> thumbnails/<id>.png (first occurrence of each id)
smollan catalog                                       # 6. regenerate CATALOG.md + catalog.json
python examples/demo.py && smollan build examples/deck_spec.json   # 7. sanity check
```

### What each tool does

| tool | input -> output | notes |
|---|---|---|
| `build_master.py` | 16 pack files -> `smollan/smollan_master.pptx`, `tools/build_info.json` | copies every used layout into the Core master (de-duplicated). Each example slide becomes a template slide named `<pack>.s<NN>`, plus hidden variants (`<pack>.h<NN>`). Moves content baked into layouts onto the slides, and stores designer sticky notes as recipe notes |
| `scrub_master.py` | master -> master | replaces client and retailer names (list in `tools/scrub_names.local.json`, **not committed**), zeroes figures in example tables, neutralises file metadata |
| `analyze_slots.py` | master -> `tools/auto_specs.json` | every fillable element with geometry, font size, prompt text, inferred role, and grouping of repeated blocks |
| `gen_registry.py` | curation + auto specs -> `smollan/recipes.py` | builds slot maps, calibrates limits, writes `RECIPES` and the summary index |
| `selftest.py` | registry -> test deck | fills every recipe with sample content. Fails on any error, reports leftover text |
| `render.ps1` | `.pptx` -> PNGs (+ PDF with `-Pdf`) | PowerPoint via COM |
| `extract_photos.py`, `photo_index.py` | master -> `smollan/assets/photos/` | one-off photo library extraction and naming |

## Editing a recipe: `tools/curation.py`

Every recipe is one `C(...)` call. **Never edit `smollan/recipes.py` by hand**, because it is regenerated.

```python
C("p13.s08", "stats.3", "3 big stats (dark band)",                     # template key, id, title
  "Dark band with three numbered columns: heading, big value, ...",    # summary (what it looks like)
  "Three headline numbers - the default stats slide.",                 # use when
  "",                                                                  # avoid when
  "stats three numbers",                                               # search tags
  # optional overrides:
  slots="heading=ph0 | subheading=ph40",
  items="label=ph71,ph75,ph79 | value=ph59,ph74,ph78 | text=ph72,ph73,ph77",
  kinds={"chart": "chart"},            # slot kind: text photo chart table gantt org video
  keep="heading",                      # template wording is real copy: keep it unless overridden
  keep_items=True,                     # items optional: keep the template's item wording
  limits={"message": 9},               # force max_lines for a slot / field
  table={"table": {"header_rows": 2, "footer_rows": 1, "fixed": True}},
  rename={"bullets_2": "detail"},      # rename an auto-generated slot or field
  remove="id16",                       # shapes or cells always cleared (designer notes etc.)
  people=True,                         # bespoke org chart: pair NAME/role boxes (+photo) into items
  notes=["Shown in describe() and CATALOG.md"],
  hints={"value": "e.g. 87%"})
```

**Reference syntax**: `ph59` is the placeholder with idx 59, `id24` is the shape with id 24, and
`c18.1.1` is cell (row 1, col 1) of table shape 18.

**Finding refs**: open `tools/auto_specs.json` and look up the template key. Each element lists its
`ref`, `role`, position (`x`, `y` in inches), size, prompt text and limits. Without overrides, the
generator names slots from the inferred roles and groups repeated blocks automatically. That works
for regular grids; asymmetric layouts need explicit `slots=` / `items=`.

After editing, run `gen_registry.py`, then `selftest.py`, then render the changed recipes and look at them.

## Adding a new pack or slide

1. Add the file to `PACKS` in `tools/build_master.py`, with a new code (e.g. `p15`) and slides to skip.
   For layouts with no example slide, add them to `HIDDEN_LAYOUTS`.
2. Run the pipeline up to `analyze_slots.py`. New template keys appear in `auto_specs.json`, and
   `gen_registry.py` warns about template slides without a recipe.
3. Add a `C(...)` entry per new slide in `curation.py`.
4. Run the rest of the pipeline. Check the renders, add thumbnails, and regenerate the catalog.
5. If the packs contain client work, extend `tools/scrub_names.local.json`
   (`[["regex", "replacement"], ...]`) and confirm the audit finds nothing (see below).

## Before publishing

- `python tools/selftest.py` prints `0 recipe failures` and `preflight: clean`.
- Run `python -m pyflakes smollan tools examples` and check it is clean.
- **Client-data audit:** search every published file, including the master's XML, for the names in
  `scrub_names.local.json`. There must be no hits.
- Bump `version` in `pyproject.toml` and `__version__` in `smollan/__init__.py`.

## Releasing

```bash
python -m build                     # optional: wheel + sdist in dist/
git commit -am "..." && git push    # users install straight from GitHub
```
