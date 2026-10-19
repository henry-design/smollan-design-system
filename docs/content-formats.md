# Content formats

Exactly what to pass for each kind of slot. Run `smollan show <recipe>` to see each slot's kind.

- [Text](#text)
- [Photos](#photos)
- [Charts](#charts)
- [Tables](#tables)
- [Gantt](#gantt)
- [Org charts](#org-charts)
- [Logos](#logos)
- [Video](#video)
- [Items (repeated blocks)](#items-repeated-blocks)

---

## Text

A text slot takes a **string** or a **list of strings**.

```python
heading="Q3 RESULTS AT A GLANCE"                     # one paragraph
body=["First point", "Second point", "Third point"]  # three paragraphs / bullets
body=["Main point", "- sub-point", "- - sub-sub"]    # "- " indents one level per prefix
text="Line one\nline two of the same paragraph"      # \n = line break inside a paragraph
text="Up **4 points** on Q2"                         # **...** = bold
```

- **Formatting comes from the template**: font, size, colour, bullets and alignment. You only
  supply words.
- **Numbers must be strings**: `value="96%"`, not `value=96`.
- **Headings are ALL CAPS** by Smollan convention. Write them in caps; many templates also force caps.
- **Respect the limits** shown by `show()`. Each list item starts a new line, so 5 bullets need at
  least 5 lines.
- **An empty string or `None`** counts as "not provided", so the slot is removed.

## Photos

A photo slot takes a **path to an image file** (`.jpg` / `.png`).

```python
photo="C:/images/store_visit.jpg"
photo=assets.photo("merchandiser_snacks_aisle")      # bundled stock photo
```

- The image is **cropped to fill** the frame, centred, so any aspect ratio works. Put the
  subject near the centre.
- **Stock library:** run `smollan photos` (or `assets.photos()`) to list the 21 bundled photos, and
  `assets.photos("merchandiser")` to filter by tag. The library is opt-in: nothing is filled
  automatically.
- **Leaving a photo out** keeps an empty picture placeholder. It is invisible in slideshow, and
  `save()` reports it so a person can add a picture later.
- **Screenshots** for `devices.*` recipes work the same way and are cropped to the screen area.
- **In JSON**, use `"asset:<name>"` for library photos and relative paths for your own (resolved
  from the JSON file's folder).

## Charts

A chart slot takes a dict:

```python
chart={
    "type": "column",                                # optional - see below
    "categories": ["Q1", "Q2", "Q3", "Q4"],          # x-axis labels / pie slices
    "series": {"2025": [4.2, 5.1, 5.8, 6.4],         # one entry per series, same length
               "2026": [4.8, 5.9, 6.6, 7.3]},
    "title": "Value sales (R m)",                    # optional chart title
    "labels": True,                                  # optional: True = values, "percent" (pie/doughnut), False = none
    "number_format": "0.0",                          # optional Excel number format
}
```

**`type` values**

| type | chart |
|---|---|
| `column` / `stacked_column` / `stacked_100` | vertical bars: clustered / stacked / 100% stacked |
| `bar` / `stacked_bar` / `stacked_bar_100` | horizontal bars |
| `line` / `line_plain` | line with / without markers |
| `pie` / `doughnut` | one series only; categories become slices |
| `area` / `stacked_area` | area charts |
| `waterfall` | bridge chart (see below) |

- **Omit `type` to keep the template's own chart**, with its exact Smollan styling. Most graph
  recipes come with a styled chart, and their summary says which type it is (e.g. `graphs.1_sub_bar`
  is a stacked bar). Only the data changes.
- **Give a different `type`** and a new native chart is created in the same place, styled in
  Smollan colours (series order: blue, green, cyan-blue, bright cyan, charcoal, lime...).
- **Charts are fully editable** in PowerPoint (right-click, Edit Data).
- **A shorthand** for a single series: `"series": [1, 2, 3]` (named via `"series_name"`).

**Pie and doughnut charts**

```python
chart={"type": "pie", "categories": ["Modern", "Traditional", "Wholesale"],
       "series": {"Share": [52, 31, 17]}, "labels": "percent"}
```

- **Up to 8 slices.** Group the smallest into "Other", or use a bar chart for more categories.
- **Pie = one series.** For two series use `"type": "doughnut"`, which draws concentric rings
  (inner = first series), or two charts side by side (`graphs.2_intro`).
- **No negative values, and not all zeros.** Use a bar or waterfall chart for gains and losses.
- **Colours:** every slice gets a Smollan colour in order (blue, green, cyan-blue, bright cyan,
  charcoal, lime, mid blue, dark blue) with white edges. Template charts keep their own colours for
  the first slices and continue in that order.
- **Labels:** new charts show white bold values; `"labels": "percent"` shows each slice's share
  (PowerPoint calculates it). Template charts keep their own label style unless you pass `labels`.
- **Titles:** template pies (`graphs.2_intro`) and the template doughnut on `graphs.text_left` show
  the **series name** as their title, so name the series meaningfully
  (`"series": {"Channel mix 2026": [...]}`) or pass `"title"`.
- **`stats.2_doughnut`** draws the split in the ring, and the big numbers inside it are separate
  slots (`chart_value_1`, `chart_value_2`). Keep them consistent with the chart data.

**Waterfall** (bridge from a start value to an end value):

```python
chart={"type": "waterfall",
       "categories": ["Q2", "Volume", "Price", "Mix", "Cost", "Q3"],
       "series": {"Value": [100, 12, 6, -3, -2, None]},
       "totals": [0, 5]}            # indexes drawn as full bars (start/end); None = running total
```

Positive steps are green, negative steps cyan and totals blue. `totals` defaults to the last index.

**Survey charts** (`feedback.*`): `{"categories": ["Quality of Work", "Communication", ...],
"series": {"Score": [8, 7, ...]}}`. Omit `type` to keep the dark survey bar styling.

## Tables

A table slot takes a dict with optional `header`, `rows` and `footer`:

```python
table={
    "header": ["ACCOUNT", "OSA", "SHARE OF SHELF", "PROMO"],     # one row (or a list of rows)
    "rows":   [["Retailer A", "97%", "33%", True],
               ["Retailer B", "95%", "30%", False]],
    "footer": ["TOTAL", "96%", "31%", ""],                       # only if the preset has a total row
}
```

**Cell values**

| value | result |
|---|---|
| `"text"` | text in the template's cell style |
| `["line 1", "line 2"]` | several paragraphs in one cell |
| `True`, `"tick"`, `"yes"` | the preset's own tick / dot symbol in that column's colour |
| `False`, `"cross"`, `"no"` | the preset's cross symbol, or blank if it has none |
| `None` or `""` | empty cell |

**Free-form versus fixed presets.** `show()` says which one a preset is:

- **`rows/cols flexible`**: pass any number of rows and columns. Extra rows are cloned from the
  template's rows, so zebra striping and coloured row labels carry on. Extra columns are cloned
  from the last column. The table keeps its overall size. `tables.clean` is the go-to free-form table.
- **`FIXED grid`**: the preset has merged cells (most `tables.gt_*`, `tables.region_totals`,
  `kpis.strategic_table`...). Pass **exactly** the template's grid: the same number of body rows
  and of values per row. Values at merged positions are ignored. The slot hint gives the grid size
  and the first-row labels:
  `template grid 7 rows x 12 cols (merged cells); first row: NATIONAL GROUP | - | Eastern Cape | ...`

**Header and footer rows**: `show()` states how many the preset has (`1 header row(s), 1 footer
row(s)`). Your `header` and `footer` must match those counts. You can also pass the table as a plain
list of rows, in which case the first *header_rows* rows become the header.

Tips: keep tables to about 12 body rows; split larger data over two slides. Write numbers as
strings so you control their formatting ("1 240", "96%").

## Gantt

`tables.gantt` takes a `gantt` slot:

```python
gantt={"periods": ["1", "2", "3", "4", "5", "6"],               # column headers (weeks, months...)
       "tasks": [{"label": "KICK-OFF",   "start": 1, "end": 1},
                 {"label": "PILOT",      "start": 2, "end": 4},  # 1-based, inclusive
                 {"label": "ROLL-OUT",   "start": 4, "end": 6}],
       "corner": "WEEK"}                                         # top-left header text
```

Each task's bar uses the template's row colours in turn.

## Org charts

`org.tree*` recipes take a `tree` slot, a nested dict:

```python
tree={"name": "Jane Doe", "role": "Client Lead", "photo": "jane.jpg",      # photo optional
      "children": [
          {"name": "Sipho Dlamini", "role": "Field Manager",
           "children": [{"name": "Ann Lee", "role": "Team Leader"},
                        {"name": "Raj Patel", "role": "Team Leader"}]},
          {"name": "Maria Silva", "role": "Insights Lead"}]}
```

- **Drawn as native PowerPoint shapes:** boxes and connectors in level colours (dark blue, green,
  blue, charcoal, cyan-blue). Names are set in caps.
- **Size limits:** up to **5 levels** and **8 boxes across**. When a team is too wide, groups of
  leaf members are stacked vertically under their manager automatically.
- **Too big** raises `SmollanError`. Split the chart: put the top levels on one slide and each branch
  on its own slide (pass the branch as the tree).
- **Two charts side by side:** `org.tree_x2` (slots `tree`, `tree_2`) or `org.tree_x2_desc` (items
  with `tree`, `title`, `text`).
- **Bespoke org charts** (`org.bespoke_*`) are fixed designs. Pass one item per person box (`name`,
  `role`, and `photo` for photo designs) in reading order, and match the exact count.

## Logos

Some templates have a spot for the **client's logo**: the white circle on `cover.photo.rfp_client`,
and the corner of many `tables.*` and `graphs.2_notes` slides. Those recipes have an optional
`logo` slot that takes an image path:

```python
deck.add("tables.clean", heading="...", table={...}, logo="acme_logo.png")
deck = Deck(..., logo="acme_logo.png")      # or set it once for every slide with a logo spot
```

- The logo is **scaled to fit** its box and centred. It is never cropped or stretched. Use a PNG
  with a transparent background.
- **Without a logo** the spot is removed, so the template's "CLIENT LOGO GOES HERE" image never
  appears in a finished deck.

## Video

`devices.laptop_video` takes `video="demo.mp4"`. The video plays inside the laptop frame in slideshow.

## Items (repeated blocks)

`items` is a list of dicts, one per repeated block, in reading order (left to right, then top to
bottom). Each dict's keys are the recipe's item fields, and the values use the formats above:

```python
items=[{"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability.", "note": "Source: audits"},
       ...]
```

- **The count is exact.** `describe(id)` says `exactly N item dicts`.
- **Missing fields** are removed for that block only.
- **Items can hold photos, charts or trees** when the field kind says so (e.g. `graphs.2_desc` items
  have a `chart`; `org.tree_x2_desc` items have a `tree`).
- **Default items:** `why.pillars` and `why.pillars_photos` can be used without `items`, which keeps
  Smollan's four standard pillars.
