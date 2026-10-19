# Troubleshooting

Every `SmollanError` message tells you what to change. This page explains each one and how to fix it.

## Validation errors (raised by `deck.add`)

| Message (shortened) | Cause | Fix |
|---|---|---|
| `unknown recipe 'stat.3'` | the id doesn't exist | run `smollan find "<need>"` or `smollan list <category>`. Ids are `category.variant` |
| `unknown slot 'headng' for stats.3; valid slots: [...]` | misspelt or invented slot name | use a name from the list, or check `smollan show <id>` |
| `stats.3 holds 3 items; you passed 4. Recipes in 'stats' that take 4: [...]` | wrong number of repeated blocks | use one of the suggested recipes, or change your content to fit |
| `No 'process' recipe takes 9 - split the content over two slides` | too many blocks for any design | split across slides (e.g. steps 1-5 and 6-9) |
| `stats.3 needs items=[...] with 3 dicts using the fields [...]` | `items` was forgotten | pass the item dicts |
| `stats.3.items[1]: unknown field 'title'` | wrong item field name | use the fields listed in `show()` |
| `kpis.5.intro: ~3 lines but this slot holds 2 (about 48 characters)` | the text is too long for the box | **shorten the copy.** Never reduce the font size |
| `expected text (str or list of str), got int` | a number was passed to a text slot | pass `"96%"`, not `96` |

## Content errors

| Message | Fix |
|---|---|
| `chart needs "categories" and "series"` | pass both. See [content-formats.md](content-formats.md#charts) |
| `chart series 'X' has 3 values for 4 categories` | give every series one value per category |
| `unknown chart type 'columns'` | use one of `column bar line line_plain pie doughnut stacked_column stacked_100 stacked_bar stacked_bar_100 area stacked_area waterfall` |
| `pie charts hold max 8 slices; you passed 9` | group the smallest categories into "Other", or use `"type": "bar"` |
| `a pie chart shows one series; you passed 2` | use `"type": "doughnut"` (rings), two charts (`graphs.2_intro`), or a bar chart |
| `doughnut values cannot be negative` / `is all zero` | pies and doughnuts show shares of a positive total. Use a bar or waterfall chart |
| `this table preset has 1 header row(s); you passed 2` | match the header and footer row counts shown by `show()` |
| `this table preset has a fixed structure: N body rows x C columns` | pass exactly that grid, or use `tables.clean` |
| `this table preset has merged cells, so its C columns are fixed` | pass C values per row, or use `tables.clean` |
| `org chart needs 11 columns (max 8)` | split the tree: top levels on one slide, each branch on its own |
| `org chart deeper than 5 levels` / `too tall` | remove a level, or split by branch |
| `photo not found: ...` | check the path. Relative paths are resolved from the working directory (Python) or the JSON file's folder (`smollan build`) |
| `no photo 'xyz'; see assets.photos()` | run `smollan photos` for the valid names |
| `deck already saved` | a `Deck` saves once. Create a new `Deck` |

## Preflight issues (reported by `deck.save`)

| Issue | Meaning | Fix |
|---|---|---|
| `leftover template text 'Click to edit ...'` | template wording that wasn't replaced. Usually your own text contains words like "Click to edit", "XX" or "[Client]" | change the text, or pass `client=` to `Deck` so `[Client]` is filled |
| `photo slot ph:31 left empty` | a photo slot got no image | pass a photo, or leave it for a person to add in PowerPoint |

The deck is still saved when there are preflight issues. They are reported so you can decide.

## Installation and environment

| Problem | Fix |
|---|---|
| `smollan` command not found | run `python -m smollan ...`, or add Python's `Scripts` folder to PATH |
| `No module named smollan` | install it: `pip install git+https://github.com/henry-design/smollan-design-system`. Check you used the same Python that runs your script (`python -m pip install ...`) |
| `smollan_master.pptx not found` | the package data is missing. Reinstall it (`pip install --force-reinstall git+...`). Don't copy `smollan/` without its data files |
| Headings look like the wrong font | Montserrat isn't installed. Run `smollan install-fonts`, then restart PowerPoint |
| Text slightly overflows a box when opened | the limits are estimates. Shorten that text a little. Make sure Montserrat is installed, because other fonts are wider |
| PowerPoint shows a "repair" message | please report it with the recipe ids used. Every recipe is tested to open cleanly in PowerPoint 2024 |

## Choosing better slides

| Situation | Suggestion |
|---|---|
| Too much text for any slot | it's probably two messages. Split them across slides |
| Six points but the content is really numbers | use `stats.*` or `kpis.*` instead of `buckets.*` |
| More than 8 process steps | split, or use `infographic.cycle` for a looping process |
| A large data table | `tables.clean`, max ~12 rows per slide |
| A team of 30 | `org.tree` for the leadership, then one `org.tree` slide per department |
