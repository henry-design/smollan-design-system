"""
smollan - the Smollan presentation design system, as code.
=========================================================

Install:  pip install git+https://github.com/henry-design/smollan-design-system
Then:     import smollan   (any folder)   |   smollan <command>   (CLI)
Agents:   read AGENTS.md in the repository first.

This package knows every Smollan slide (Core Template + packs 1-14), the brand
rules, and how to fill each slide with content. An agent decides WHAT to say,
picks a recipe (smollan.recipes - summary index at the top of that file), and
this package produces an on-brand, editable .pptx.

Modules: deck (Deck) | catalog (find/describe/show) | validation | recipes
(generated registry) | text/charts/tables/orgchart/shapes (fillers) | brand |
photos (assets) | cli (smollan command, JSON builder) | config | errors

Data bundled inside this package (installed with it):
    smollan_master.pptx  - every Smollan layout merged into one master, plus one
                           template slide per recipe (built by tools/build_master.py)
    assets/photos/       - opt-in stock photo library (assets.photo('<name>'))
    assets/fonts/        - Montserrat (smollan install-fonts)
In the GitHub repository (docs, not installed):
    AGENTS.md            - operating manual for AI agents (read first)
    CATALOG.md           - catalog with thumbnails;  catalog.json - machine-readable
    thumbnails/<id>.png  - preview of every recipe

---------------------------------------------------------------------------
QUICK START (for agents)
---------------------------------------------------------------------------
    from smollan import Deck, assets, find

    find("three big statistics with photos")      # -> ranked recipe ids
    d = Deck(title="Q3 BUSINESS REVIEW", presenter="Jane Doe, Client Lead",
             date="October 2026", client="Acme Foods")    # auto-adds a cover
    d.add("stats.3", heading="RESULTS AT A GLANCE",
          subheading="Year to date",
          items=[{"heading": "AVAILABILITY", "value": "87%",
                  "text": "On-shelf availability across 1,200 stores."}, ...])
    d.add("graphs.1", heading="SALES TREND",
          chart={"type": "line", "categories": ["Q1", "Q2", "Q3"],
                 "series": {"2025": [1, 2, 3], "2026": [2, 3, 4]}})
    d.add("org.tree", heading="YOUR TEAM",
          tree={"name": "A. Person", "role": "Account Director",
                "children": [{"name": "B. Person", "role": "Manager"}]})
    d.save("Acme_Q3.pptx")    # auto-adds the closing slide + runs preflight

    smollan list                 # list every recipe id + summary   (or: python -m smollan list)
    smollan show stats.3         # full spec of one recipe
    smollan find "team structure"
    smollan build deck.json      # build a deck from a JSON spec (non-Python agents)
    smollan install-fonts        # install Montserrat for this user

---------------------------------------------------------------------------
HOW CONTENT MAPS TO A RECIPE
---------------------------------------------------------------------------
Every recipe has named SLOTS. Pass them as keyword arguments to Deck.add():
  * scalar slots      heading="...", subheading="...", intro="..."
  * item slots        items=[{...}, {...}]  - one dict per repeated block
                      (stat, step, bucket, KPI, pillar, person...). The keys
                      of each dict are the recipe's item fields.
  * text values       a str, or a list[str] for multiple paragraphs/bullets.
                      Use "\\n" inside a str for a line break within a paragraph.
  * photo slots       a file path (or assets.photo(name)). Missing photos are
                      left as empty picture placeholders and reported.
  * chart slots       {"type": "column|bar|line|pie|doughnut|stacked_column|
                       stacked_bar|stacked_100|area", "categories": [...],
                       "series": {"name": [values...]}, "title": "..."}
  * table slots       {"rows": [[...], [...]], "header": True} - list of rows;
                      the first row is the header when header=True.
Slots you do not pass are removed from the slide (so no template text is
left behind) unless the recipe marks them required.

Limits: each text slot carries max_lines / max_chars derived from the
template's own instruction ("No longer than 3 lines maximum") and the box
size. Breaking a limit raises SmollanError with a suggestion - shorten the
copy or pick the suggested alternative recipe; never shrink the type.

---------------------------------------------------------------------------
BRAND RULES ENFORCED / EXPECTED
---------------------------------------------------------------------------
  * 16:9, 13.333 x 7.5 in. Montserrat headings (ALL CAPS), Calibri body.
  * Smollan greens (#16B795, #8AC546) are focal colours - one per slide.
  * Max 8 process steps per slide; org charts too big for one slide are split.
  * Never leave [Client], "Click to edit", "XX" or mojibake dashes - preflight
    checks for these on save.
"""
from __future__ import annotations

__version__ = "1.0.0"

from .brand import Brand  # noqa: E402
from .catalog import (CATEGORY_INFO, CATEGORY_ORDER, alternatives, catalog, describe, example_call,  # noqa: E402
                      find, resolve, show)
from .charts import CHART_TYPES, put_chart, style_chart  # noqa: E402
from .cli import build_from_spec, install_fonts, main  # noqa: E402
from .config import FONT_DIR, HERE, MASTER_PATH, PHOTO_DIR, REPO_ROOT  # noqa: E402
from .deck import Deck, preflight_check  # noqa: E402
from .errors import SmollanError  # noqa: E402
from .orgchart import draw_org_chart  # noqa: E402
from .photos import assets  # noqa: E402
from .recipes import RECIPES  # noqa: E402
from .tables import put_gantt, put_table  # noqa: E402
from .text import set_text  # noqa: E402
from .validation import validate  # noqa: E402

__all__ = ["Deck", "SmollanError", "Brand", "RECIPES", "CATEGORY_INFO", "CATEGORY_ORDER", "find", "describe", "show",
           "resolve", "alternatives", "example_call", "validate", "catalog", "assets", "build_from_spec",
           "install_fonts", "main", "preflight_check", "set_text", "put_chart", "style_chart", "put_table",
           "put_gantt", "draw_org_chart", "CHART_TYPES", "MASTER_PATH", "PHOTO_DIR", "FONT_DIR", "HERE",
           "REPO_ROOT", "__version__"]
