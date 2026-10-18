"""
Hand-written curation for every template slide in smollan_master.pptx.

Each C(...) call turns one template slide (src) into a RECIPE (id) with a title,
summary, when-to-use guidance and - where the automatic slot inference is not good
enough - explicit slot maps.

Slot map syntax (strings):
    slots="heading=ph0 | intro=ph57"          name=ref
    items="value=ph59,ph74 | text=ph72,ph73"  field=ref per item (reading order)
    refs: ph<idx> placeholder, id<shape id>, c<table id>.<row>.<col> table cell, '-' none
Other keys:
    kinds   {"slot": "photo|chart|table|gantt|org|video|logo|text"}
    keep    "slot,slot"   template wording is final copy - kept when not supplied
    table   {"slot": {"header_rows": 1, "footer_rows": 0, "fixed": False}}
    remove  "id16,c24.2.1"  shapes/cells always cleared
    people  True          bespoke org chart - pair NAME/role boxes (+photo) into items
    hints   {"slot": "what goes here"}
"""
CURATION = []


def C(src, id, title, summary, use="", avoid="", tags="", **kw):
    CURATION.append(dict(src=src, id=id, title=title, summary=summary, use=use, avoid=avoid, tags=tags, **kw))


# ---------------------------------------------------------------------------
# CORE TEMPLATE - covers, dividers, title slides, closing
# ---------------------------------------------------------------------------
COVER_SLOTS = "heading=ph0 | presenter=ph10 | date=ph11"
C("core.s01", "cover.dark_blue", "Shape cover - dark blue",
  "Full-bleed dark-blue cover with Smollan geometric shapes (rings, plus, circles) and the SMOLLAN wordmark; "
  "title over two lines, presenter line and date beneath.",
  "Default opening slide of any Smollan deck.", "You want a photo-led opening - use cover.photo.*.",
  "cover opening title start", slots=COVER_SLOTS,
  hints={"heading": "presentation title, max 2 lines", "presenter": "NAME SURNAME, TITLE", "date": "e.g. OCTOBER 2026"})
C("core.s03", "cover.blue", "Shape cover - Smollan blue",
  "Same geometric cover in the lighter Smollan blue tone; title upper-left, presenter and date beneath.",
  "Opening slide when a lighter, brighter feel suits the client.", "Photo-led opening - use cover.photo.*.",
  "cover opening title start", slots=COVER_SLOTS,
  hints={"heading": "presentation title, max 2 lines", "presenter": "NAME SURNAME, TITLE", "date": "e.g. OCTOBER 2026"})
C("core.s05", "cover.charcoal", "Shape cover - charcoal",
  "Geometric cover in charcoal / near-black with a green accent; title lower-left.",
  "Opening slide for a sober, premium feel or when the client brand is dark.", "Photo-led opening.",
  "cover opening title start dark", slots=COVER_SLOTS,
  hints={"heading": "presentation title, max 2 lines", "presenter": "NAME SURNAME, TITLE", "date": "e.g. OCTOBER 2026"})
DIV_SLOTS = "heading=ph0 | section=ph10"
DIV_HINTS = {"heading": "short section title, max 2 lines", "section": "section number / label, e.g. SECTION 02"}
C("core.s02", "divider.dark_blue", "Section divider - dark blue",
  "Dark-blue divider with the small Smollan shape cluster on the left; section number and a short title on the right.",
  "Start of each major section of a deck.", "More than ~6 sections (dividers lose meaning).", "divider section break chapter",
  slots=DIV_SLOTS, hints=DIV_HINTS)
C("core.s04", "divider.blue", "Section divider - Smollan blue",
  "Divider in Smollan blue with the shape cluster; section number and title.",
  "Section break in a deck that opened with cover.blue.", "", "divider section break chapter",
  slots=DIV_SLOTS, hints=DIV_HINTS)
C("core.s06", "divider.charcoal", "Section divider - charcoal",
  "Divider in charcoal with the shape cluster; section number and title.",
  "Section break in a deck that opened with cover.charcoal.", "", "divider section break chapter dark",
  slots=DIV_SLOTS, hints=DIV_HINTS)
C("core.s07", "title.one_line", "Heading + body",
  "White content slide: one-line ALL-CAPS heading with a short rule, and a large body area for paragraphs or bullets.",
  "Any text content that has no better-structured recipe; agendas; short narratives.",
  "Content that is really N parallel points (use buckets.*), numbers (stats.*) or steps (process.*).",
  "text bullets agenda body content generic", hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s09", "title.one_line_sub", "Heading + sub-heading + body",
  "One-line heading, a sentence-case sub-heading directly beneath, then a body area.",
  "Text slide that needs a one-line framing statement under the heading.", "", "text bullets body content sub-heading",
  hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s10", "title.one_line_sub_caps", "Heading + CAPS sub-heading + body",
  "One-line heading, larger ALL-CAPS blue sub-heading beneath, then body.",
  "Text slide where the sub-heading is a strong second headline.", "", "text bullets body content sub-heading",
  hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s08", "title.one_line_sub_below", "Heading + body with sub-heading above body",
  "One-line heading; the sub-heading sits lower, as a lead-in line right above the body text.",
  "Text slide with a lead-in sentence introducing the body.", "", "text bullets body content",
  hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s11", "title.two_line", "Two-line heading + body",
  "Heading over two lines, body area beneath.", "When the heading needs two lines.", "", "text bullets body content",
  hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s13", "title.two_line_sub", "Two-line heading + sub-heading + body",
  "Two-line heading, sub-heading directly beneath, body.", "Two-line heading plus a framing line.", "",
  "text bullets body content sub-heading", hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s12", "title.two_line_sub_below", "Two-line heading + lead-in + body",
  "Two-line heading; sub-heading placed lower as the body lead-in.", "", "", "text bullets body content",
  hints={"body": "paragraphs or bullets ('- ' for level 2)"})
C("core.s14", "closing", "Smollan closing slide",
  "Dark-blue end slide: centred SMOLLAN logo, 'WINNING AT THE POINT OF PURCHASE' strapline, brand icons and a small "
  "contact line.", "Always the last slide (added automatically by Deck.save).", "", "closing end final contact",
  slots="contact=ph44 | email=ph45", hints={"contact": "NAME SURNAME   |   +27 000 0000", "email": "name.surname@smollan.com"})

# ---------------------------------------------------------------------------
# 1 - PHOTO COVERS / 2 - PHOTO + CLIENT
# ---------------------------------------------------------------------------
PC = "heading=ph0 | subheading=ph10"
PCD = "heading=ph0 | subheading=ph10 | date=ph11"
PH = {"heading": "presentation title (2-3 lines)", "subheading": "one line, e.g. client / purpose", "date": "e.g. OCTOBER 2026"}
C("p01.s02", "cover.photo.laptop_sofa", "Photo cover - woman with laptop",
  "Dark-blue cover, large cyan ring and blue plus shapes; photo of a smiling woman on a sofa with a laptop on the right; "
  "SMOLLAN wordmark left; title and sub-heading lower-left.",
  "Digital / e-commerce / connected-shopper themed opening.", "", "cover photo opening digital ecommerce", slots=PC, hints=PH)
C("p01.s03", "cover.photo.beauty", "Photo cover - beauty consultant",
  "Blue cover with green and cyan geometric shapes; photo of a woman applying make-up (beauty / cosmetics); title lower-left.",
  "Beauty, personal care, cosmetics or in-store promoter themes.", "", "cover photo opening beauty cosmetics", slots=PC, hints=PH)
C("p01.s04", "cover.photo.shoppers", "Photo cover - two shoppers",
  "Dark-blue cover with green ring and cyan plus; photo of two women shopping in a store, one holding a phone.",
  "Shopper marketing / shopper insight themes.", "", "cover photo opening shopper", slots=PC, hints=PH)
C("p01.s05", "cover.photo.merchandiser", "Photo cover - Smollan merchandiser",
  "Full-bleed photo of a Smollan merchandiser (branded polo) working a store aisle, framed by a dark-blue curve; "
  "SMOLLAN bottom-right.", "Field execution / merchandising / retail services decks.", "", "cover photo opening merchandising field",
  slots=PC, hints=PH)
C("p01.s06", "cover.photo.shelf_curve", "Photo cover - shelf (curved mask)",
  "Dark-blue cover, photo of a man stocking a shelf of jars inside a large curved mask on the right; title, sub-heading "
  "upper-left; date bottom-left.", "Retail execution / availability themes.", "", "cover photo opening shelf retail",
  slots=PCD, hints=PH)
C("p01.s07", "cover.photo.rfp_client", "Photo cover - RFP response with client logo",
  "Photo of a couple choosing fresh produce, green arc top-right with an 'RFP RESPONSE' label, client name, date and a "
  "white circle for the client logo; SMOLLAN bottom-right.",
  "Responses to RFPs / tenders, co-branded with the client.", "", "cover photo opening rfp tender client co-branded",
  slots="heading=ph0 | subheading=ph10 | client=ph13 | date=ph12 | label=id2", keep="label",
  hints={"client": "client name", "date": "e.g. 18 OCTOBER 2026", "label": "default 'RFP RESPONSE'"})
C("p01.s08", "cover.photo.shelf_glasses", "Photo cover - shopper in glasses (curved mask)",
  "Dark-blue cover; photo of a man in glasses examining a product at the shelf inside a curved mask; date bottom-left.",
  "Shopper insight, product / pack decks.", "", "cover photo opening shopper", slots=PCD, hints=PH)
C("p01.s09", "cover.photo.shelf_curve_dark", "Photo cover - shelf (curved mask, darker)",
  "Darker variant of cover.photo.shelf_curve (same shelf photo, deeper blue).", "", "", "cover photo opening shelf retail",
  slots=PCD, hints=PH)
C("p01.s10", "cover.photo.woman_left", "Photo cover - woman, photo left",
  "Photo of a smiling woman on the left inside a curved mask; title, sub-heading and date on the right.",
  "Opening where the text should sit on the right.", "", "cover photo opening people", slots=PCD, hints=PH)
C("p01.s11", "cover.photo.woman_left_dark", "Photo cover - woman, photo left (darker)",
  "Darker variant of cover.photo.woman_left.", "", "", "cover photo opening people", slots=PCD, hints=PH)
C("p01.s12", "cover.photo.shelf_top", "Photo cover - shelf photo top",
  "Photo of a man at a well-stocked shelf across the top inside a curved mask; title lower-left; date bottom-right; no sub-heading.",
  "", "", "cover photo opening shelf retail", slots="heading=ph0 | date=ph11", hints=PH)
C("p01.s13", "cover.photo.shelf_top_sub", "Photo cover - shelf photo top, with sub-heading",
  "As cover.photo.shelf_top, plus a sub-heading line under the title.", "", "", "cover photo opening shelf retail",
  slots="heading=ph0 | subheading=ph10 | date=ph12", hints=PH)
C("p01.s14", "cover.photo.pharmacy", "Photo cover - pharmacy shelf",
  "Photo of a woman choosing a product in a pharmacy / health-and-beauty aisle inside a large curve; title right; date bottom-left.",
  "Pharmacy, health, personal-care themes.", "", "cover photo opening pharmacy health", slots="heading=ph0 | date=ph11", hints=PH)
C("p01.s15", "cover.photo.pharmacy_dark", "Photo cover - pharmacy shelf (darker)",
  "Darker variant of cover.photo.pharmacy.", "", "", "cover photo opening pharmacy health", slots="heading=ph0 | date=ph11", hints=PH)
C("p02.s03", "cover.photo.client_logo", "Photo cover - co-branded with client logo",
  "cover.photo.laptop_sofa with a white circle inside the cyan ring that holds the client's logo.",
  "Co-branded opening when the client logo must appear on the cover.", "", "cover photo opening client co-branded logo",
  slots=PC, hints=PH)

# ---------------------------------------------------------------------------
# 3 - THANK YOU
# ---------------------------------------------------------------------------
TY_KEEP = "heading,heading_2"
TYH = {"heading": "default 'THANK YOU'", "heading_2": "default 'FOR THE OPPORTUNITY'", "message": "short personal message",
       "subheading": "e.g. NEXT STEPS", "body": "paragraphs or bullets"}
TY_LIM = {"message": 9, "heading_2": 1}
TY5 = "heading=ph0 | heading_2=ph39 | message=ph42 | subheading=ph41 | body=ph40"
TY4 = "heading=ph0 | heading_2=ph39 | message=ph42 | body=ph40"
C("p03.s02", "thankyou.a", "Thank you - A (pale band, dark message panel)",
  "Pale top band with brand icons; 'THANK YOU / FOR THE OPPORTUNITY' with a white circle accent; dark-blue panel lower-left "
  "for a personal message; sub-heading + body on the right (e.g. next steps).",
  "Closing a pitch with a thank-you message and next steps.", "", "thankyou thanks closing next steps",
  slots=TY5, keep=TY_KEEP, hints=TYH, limits=TY_LIM)
C("p03.s03", "thankyou.c", "Thank you - C (dark band, blue circle)",
  "Dark-blue top band with brand icons; THANK YOU heading left; big blue circle holding the message; sub-heading + body right.",
  "Closing with a thank-you message and next steps.", "", "thankyou thanks closing next steps", slots=TY5, keep=TY_KEEP, hints=TYH, limits=TY_LIM)
for key, vid, fam, sub in [("h02", "thankyou.a_1", "A", False), ("h03", "thankyou.a_2", "A", True), ("h04", "thankyou.a_3", "A", False),
                           ("h05", "thankyou.b_1", "B", True), ("h06", "thankyou.b_2", "B", False), ("h07", "thankyou.b_3", "B", True),
                           ("h08", "thankyou.b_4", "B", False), ("h09", "thankyou.c_2", "C", True), ("h10", "thankyou.c_4", "C", False),
                           ("h12", "thankyou.c_7", "C", False), ("h13", "thankyou.c_3", "C", True), ("h14", "thankyou.c_5", "C", False),
                           ("h15", "thankyou.c_8", "C", True), ("h16", "thankyou.c_9", "C", False)]:
    C(f"p03.{key}", vid, f"Thank you - {fam} variant ({'with' if sub else 'no'} sub-heading)",
      f"Hidden master variant of the Thank-you {fam} family: THANK YOU / FOR THE OPPORTUNITY, a message panel and a body area"
      f"{' with a sub-heading' if sub else ''}. See its thumbnail for the colour treatment.",
      "Alternative thank-you treatment when thankyou.a / thankyou.c do not suit.", "", "thankyou thanks closing",
      slots=TY5 if sub else TY4, keep=TY_KEEP, hints=TYH, limits=TY_LIM)

# ---------------------------------------------------------------------------
# 4 - TABLES (+ Growth Teams styles)
# ---------------------------------------------------------------------------
TBL_NOTE = "Pass the table as {'header': [...], 'rows': [[...], ...]}; rows/columns are added by cloning the template's."
FIXED_NOTE = "Fixed-structure preset (merged cells): pass the full grid with exactly the template's rows x columns; values at merged positions are ignored."
C("p04.s02", "tables.text_table", "Intro + text column + table",
  "Intro line under the heading; a narrow left column (sub-heading + bullets) and a wide table on the right with green/blue "
  "header row and a 'Sub Section' second header row.",
  "A table that needs a short explanation beside it.", "", "tables table text comparison",
  slots="heading=ph0 | intro=ph39 | subheading=ph40 | body=ph38 | table=id31",
  table={"table": {"header_rows": 2}}, notes=[TBL_NOTE + " This preset has 2 header rows."])
C("p04.s03", "tables.gantt", "Gantt / milestone timeline",
  "12-week gantt grid: WEEK header row with numbered periods, milestone rows on the left, coloured bars across the periods.",
  "Project plans, roll-out timelines, implementation schedules.", "Fewer than 3 milestones (use process.*).",
  "tables gantt timeline plan milestones roadmap schedule",
  slots="heading=ph0 | intro=ph39 | gantt=id4", kinds={"gantt": "gantt"},
  hints={"gantt": "{'periods': ['1',...,'12'], 'tasks': [{'label': 'MILESTONE', 'start': 1, 'end': 3}], 'corner': 'WEEK'}"})
C("p04.s04", "tables.region_totals", "Regional table with sub-totals",
  "Dense table: division / cluster rows with retailer columns, sub-total rows per region and a GRAND TOTAL bar.",
  "Headcount / store-count breakdowns by region and retailer.", "Free-form data (use tables.clean).",
  "tables regional totals headcount breakdown", table={"table": {"header_rows": 1, "footer_rows": 1, "fixed": True}},
  notes=[FIXED_NOTE])
C("p04.s05", "tables.abc_matrix", "A/B/C row matrix",
  "Three-row matrix: dark-blue row labels (A, B, C) on the left, coloured column headings, a tall middle row for bullet "
  "benefits and a bottom row of sub-headings.", "Comparing 4 options across 3 aspects.", "",
  "tables matrix comparison options", table={"table": {"header_rows": 1, "fixed": True}}, notes=[FIXED_NOTE])
C("p04.s06", "tables.numbered_list", "Numbered improvement-areas table",
  "Green header bar (e.g. 'OPPORTUNITIES / IMPROVEMENT AREAS') over numbered rows, each with a bold title and a description.",
  "Lists of opportunities / improvement areas / recommendations (3-10).", "", "tables list opportunities recommendations",
  table={"table": {"header_rows": 1}}, notes=[TBL_NOTE + " Each body row: [number, 'TITLE\\nDescription'] or ['1.', ['TITLE', 'Description']]."])
C("p04.s07", "tables.tick_matrix", "Tick matrix (rows x channels)",
  "Rows of headings with blue A/B/C columns and green channel columns (Retail, Franchise, Wholesale, Liquor, Pharmacy, "
  "Independent) filled with green ticks.", "Coverage / capability by channel or retailer; yes/no matrices.", "",
  "tables matrix ticks coverage channels capability", notes=[TBL_NOTE + " Use True for a tick, False/None for blank."])
C("p04.s08", "tables.tick_matrix_b", "Tick matrix (variant)",
  "Variant of tables.tick_matrix with the same structure.", "", "", "tables matrix ticks coverage channels",
  notes=[TBL_NOTE + " Use True for a tick."])
C("p04.s09", "tables.contents", "Table of contents",
  "Centred 'TABLE OF CONTENTS' heading with a slim numbered list; each row has a coloured left bar.",
  "Agenda / contents slide.", "", "tables contents agenda index", notes=[TBL_NOTE + " Rows: ['1', 'SECTION NAME', '']"])
C("p04.s10", "tables.measure_optimise", "Measure / optimise framework table",
  "Grouped header ('DC TO STORE', 'IN-STORE EXECUTION', 'INFLUENCING OFF-TAKE') over sub-columns, with MEASURE and OPTIMISE "
  "row groups and a colour key.", "Mapping services / KPIs across the route to market.", "",
  "tables framework measure optimise", table={"table": {"header_rows": 2, "fixed": True}}, notes=[FIXED_NOTE])
C("p04.s11", "tables.two_tables_text", "Two tables with titles and intros",
  "Two side-by-side tables, each with a 'Table N: Title' line and an intro; left one has a TOTAL row.",
  "Comparing two related data sets.", "", "tables two comparison data",
  slots="heading=ph0", items="title=ph39,ph44 | intro=ph43,ph45 | table=ph42,ph41", kinds={"table": "table"},
  notes=[TBL_NOTE])
C("p04.s12", "tables.two_tables", "Two tables with totals",
  "Intro line then two equal tables (green and blue headers) each ending in a total row.", "Two data sets side by side.", "",
  "tables two comparison data totals", table={"table": {"header_rows": 1, "footer_rows": 1}, "table_2": {"header_rows": 1, "footer_rows": 1}},
  notes=[TBL_NOTE + " Each table has 1 header row and 1 footer (total) row."])
C("p04.s13", "tables.option_compare", "Option comparison with ticks / crosses",
  "Options as columns (with a price / value row under each name), row titles on the left, green ticks and grey crosses; "
  "one column highlighted.", "Comparing service tiers / packages / options.", "", "tables comparison options tiers packages ticks",
  table={"table": {"header_rows": 2}}, notes=[TBL_NOTE + " 2 header rows: names, then value (e.g. price). True=tick, False=cross."])
C("p04.s14", "tables.kpi_values", "Values table with intro and two text boxes",
  "Intro line, a bullets box and a sub-headed bullets box above a table with coloured column headings and a totals row.",
  "Numeric results by category with commentary.", "", "tables values results data",
  rename={"body": "body_left", "body_2": "body_right"},
  table={"table": {"header_rows": 1, "footer_rows": 1}}, notes=[TBL_NOTE])
C("p04.s15", "tables.dot_matrix", "Dot matrix",
  "Coloured column headers (One...Five) with row labels; coloured dots mark membership.",
  "Showing which items apply to which groups.", "", "tables matrix dots coverage", notes=[TBL_NOTE + " True = dot."])
C("p04.s16", "tables.progress_list", "Rows with % and up/down change",
  "Row titles with colour bars, a details column, a % value and a coloured change cell with an up/down arrow.",
  "Performance lists with change vs. previous period.", "", "tables performance change progress",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[FIXED_NOTE])
C("p04.s17", "tables.numbered_steps", "Numbered list with dots and arrow",
  "Ten numbered rows (coloured number squares, heading + text, a status dot) beside a tall downward arrow.",
  "Ranked lists / priorities top-to-bottom.", "", "tables list ranked priorities",
  table={"table": {"header_rows": 0}}, notes=[TBL_NOTE + " No header row; each row: ['1', 'Heading\\nText', True]."])
C("p04.s15", "tables.clean", "Clean general-purpose table",
  "Coloured header row, grey row-label column and pale zebra rows; any number of rows and columns (same template as "
  "tables.dot_matrix). The default choice for free-form data.",
  "Any general data / comparison table.", "Very dense data (>12 rows - split it).", "tables table clean generic data",
  table={"table": {"header_rows": 1}}, notes=[TBL_NOTE + " True = coloured dot, plain strings for values."])
GT = "Growth Teams styling - use in Growth Teams decks (the styles are allowed anywhere)."
C("p04gt.s02", "tables.gt_year_costs", "Year / cost / hours table (Growth Teams)",
  "Rows per business unit (Unit A, Unit B...) with year, cost, hours of service, store coverage and a comments column.",
  "Service history / renewal comparisons by year.", "", "tables growth teams renewal costs hours",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s03", "tables.gt_year_costs_2line", "Year / cost table with two-line heading (Growth Teams)",
  "As tables.gt_year_costs with a centred two-line heading.", "", "", "tables growth teams renewal costs",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s04", "tables.gt_service_matrix", "Service offering matrix (Growth Teams)",
  "Category rows vs. service columns (shelf packing, replenishment, merchandising, POS capability...) with ticks and a merged note cell.",
  "Defining the service offering per category / retailer.", "", "tables growth teams services matrix ticks",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s05", "tables.gt_enable_basics", "Enable-the-basics table with chevrons (Growth Teams)",
  "Chevron arrow strip of five objectives above a dense table: focus area, objective, how we measure, frequency, time, reporting.",
  "Operating rhythm / measurement plan.", "", "tables growth teams measurement plan basics",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s06", "tables.gt_pros_cons", "Pros & cons, two approaches (Growth Teams)",
  "Two PRO/CON tables side by side under green 'NATIONAL APPROACH' / 'REGIONAL APPROACH' headings.",
  "Comparing two approaches.", "", "tables growth teams pros cons comparison", notes=[GT, FIXED_NOTE],
  table={"table": {"header_rows": 1, "fixed": True}, "table_2": {"header_rows": 1, "fixed": True}})
C("p04gt.s07", "tables.gt_capability_dots", "Capability overview dot matrix (Growth Teams)",
  "Account groups (rows) vs. services (coloured columns) with dots marking what each account receives.",
  "Capability / service coverage per retailer.", "", "tables growth teams capability coverage dots",
  table={"table": {"header_rows": 1}}, notes=[GT, TBL_NOTE + " True = dot."])
C("p04gt.s08", "tables.gt_capability_dots_centred", "Capability dot matrix, centred heading (Growth Teams)",
  "As tables.gt_capability_dots with a centred heading + sub-heading.", "", "", "tables growth teams capability dots",
  table={"table": {"header_rows": 1}}, notes=[GT, TBL_NOTE])
C("p04gt.s09", "tables.gt_hours_region", "Hours by buying group and region (Growth Teams)",
  "Numeric grid: buying groups (coloured row labels) vs. regions, row and column totals; vertical 'DRIVE EFFECTIVENESS' label.",
  "Merchandising hours / headcount by region.", "", "tables growth teams hours region numbers",
  table={"table": {"header_rows": 1, "footer_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s10", "tables.gt_resource_callage", "Resource and callage table (Growth Teams)",
  "Grouped rows per retailer with roles needed, weekly hours and % of hours; grand total.",
  "Resourcing plans.", "", "tables growth teams resource hours callage",
  table={"table": {"header_rows": 1, "footer_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s11", "tables.gt_scenarios", "Scenario summary (Growth Teams)",
  "Current vs. 4 scenarios (dashed outline columns) across service, stores, hours, share of voice and commercials.",
  "Presenting commercial scenarios.", "", "tables growth teams scenarios options commercial",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s12", "tables.gt_scenarios_colour", "Scenario summary, coloured (Growth Teams)",
  "Coloured variant of tables.gt_scenarios.", "", "", "tables growth teams scenarios commercial",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s13", "tables.gt_structure_options", "Structure options comparison (Growth Teams)",
  "Current vs. 3 structure options, with tiered store rows, hours rows and up/down arrows.",
  "Comparing organisational structure options.", "", "tables growth teams structure options",
  table={"table": {"header_rows": 2, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s14", "tables.gt_structure_ratios", "Structure & ratios (Growth Teams)",
  "Numbered rows (coloured squares) with improvements and current vs. new values.",
  "Showing structure changes and ratios.", "", "tables growth teams structure ratios",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])
C("p04gt.s15", "tables.gt_commercials", "Commercial considerations (Growth Teams)",
  "Estimated-cost column (green header) with mark-up rows, plus 'What is included' and 'Key benefits' columns.",
  "Commercial proposal summary.", "", "tables growth teams commercials cost proposal",
  table={"table": {"header_rows": 1, "fixed": True}}, notes=[GT, FIXED_NOTE])

# ---------------------------------------------------------------------------
# 5 - GRAPHS (native charts)
# ---------------------------------------------------------------------------
CH = "chart = {'type': column|bar|line|pie|doughnut|stacked_column|stacked_bar|stacked_100|area|waterfall, 'categories': [...], 'series': {'name': [...]}}. Omitting 'type' keeps the template chart type and styling."
C("p05.s03", "graphs.1", "One chart, full width",
  "One-line heading and a single full-width chart (template shows a waterfall).",
  "One clear chart message.", "Two data stories (use graphs.2_*).", "graphs chart one single", kinds={"chart": "chart"},
  notes=[CH, "Template chart is an Office waterfall; a native chart is created - 'type': 'waterfall' emulates it."])
C("p05.s04", "graphs.1_intro", "One chart with intro line",
  "Centred heading, one-line intro, full-width chart.", "One chart that needs a one-line explanation.", "",
  "graphs chart one intro", kinds={"chart": "chart"}, notes=[CH, "Template chart is an Office waterfall (see graphs.1)."])
C("p05.s05", "graphs.1_sub", "One chart with sub-heading",
  "Heading + CAPS sub-heading over a clustered column chart.", "", "", "graphs chart one column sub-heading", notes=[CH])
C("p05.s06", "graphs.2_sub", "Two charts with sub-heading",
  "Heading + sub-heading over two charts side by side (clustered bar left, stacked column + line right).",
  "Two related charts.", "", "graphs chart two comparison", notes=[CH])
C("p05.s07", "graphs.2_desc", "Two charts in cards with descriptions",
  "Two bordered chart cards (area chart, doughnut) each with a one-line heading and a two-line description beneath.",
  "Two charts that each need their own takeaway.", "", "graphs chart two description takeaway",
  slots="heading=ph0", items="chart=ph46,ph47 | heading=ph39,ph48 | text=ph43,ph49", kinds={"chart": "chart"}, notes=[CH])
C("p05.s08", "graphs.2_notes", "Two line charts with descriptor and footnote",
  "Two bordered line-chart cards with a centred descriptor line and a footnote beneath.", "", "",
  "graphs chart two line trend", slots="heading=ph0 | text=ph44 | note=ph48",
  items="chart=ph46,ph47", kinds={"chart": "chart"}, notes=[CH])
C("p05.s09", "graphs.text_left_intro", "Intro + text column + chart",
  "Intro under the heading, left text column (short sub-heading + bullets), 100% stacked column chart on the right.",
  "A chart with commentary.", "", "graphs chart text commentary", notes=[CH])
C("p05.s10", "graphs.text_left", "Text column + doughnut chart",
  "Left text column (short sub-heading + bullets) and a large doughnut chart in a pale panel.", "", "",
  "graphs chart text doughnut", notes=[CH])
C("p05.s11", "graphs.text_left_sub", "Sub-heading, text column + chart",
  "Heading + CAPS sub-heading; left bullets column; bordered clustered-column chart on the right.", "", "",
  "graphs chart text column", notes=[CH])
C("p05.s12", "graphs.takeaways", "Chart with key-takeaways panel",
  "Line chart on the left; 'KEY TAKEAWAYS' panel with bullets and two numbered short descriptors on the right.",
  "A chart with 2-4 explicit takeaways.", "", "graphs chart takeaways insights line",
  slots="heading=ph0 | subheading=ph48 | chart=ph47 | label=ph40 | body=ph38 | note_1=ph49 | note_2=ph50",
  kinds={"chart": "chart"}, keep="label", hints={"label": "default 'KEY TAKEAWAYS'"}, notes=[CH])
C("p05.s13", "graphs.1_intro_wide", "Intro + wide combo chart",
  "Two-line intro then a wide column + line combo chart.", "", "", "graphs chart combo column line", notes=[CH])
C("p05.s14", "graphs.1_sub_bar", "Stacked bar with sub-heading",
  "Centred heading and sub-heading over a stacked horizontal bar chart.", "", "", "graphs chart bar stacked", notes=[CH])
C("p05.s15", "graphs.2_intro", "Two pie charts with intro",
  "Centred heading, intro, two bordered pie charts (e.g. year vs. year).", "Year-on-year mix comparisons.", "",
  "graphs chart pie two comparison mix", notes=[CH])

# ---------------------------------------------------------------------------
# 6 - INFO BUCKETS
# ---------------------------------------------------------------------------
C("p06.s02", "buckets.4", "4 numbered buckets",
  "Four tall columns, each with a numbered circle, coloured header (heading over two lines + intro) and a bullets panel.",
  "Four parallel points / services / pillars with detail.", "", "buckets four list points services")
C("p06.s03", "buckets.5", "5 numbered buckets",
  "Five coloured columns: numbered badge, heading over two lines, bullets and a short paragraph below.", "", "",
  "buckets five list points", rename={"bullets_2": "detail"})
C("p06.s04", "buckets.6_highlights", "3 highlights + 6 columns",
  "A row of three highlight figures (e.g. '5 388 PEOPLE' with descriptor) above six coloured columns with headings and bullets.",
  "Headline facts plus six supporting areas.", "", "buckets six highlights facts",
  slots="heading=ph0 | intro=ph81 | highlight_1=ph40 | highlight_1_note=ph57 | highlight_2=ph83 | highlight_2_note=ph82 | "
        "highlight_3=ph85 | highlight_3_note=ph84",
  items="heading=ph58,ph70,ph71,ph72,ph73,ph74 | bullets=ph39,ph75,ph76,ph77,ph78,ph79")
C("p06.s05", "buckets.6", "6 numbered buckets",
  "Six coloured columns with numbered badges, a heading over two lines and bullets.", "Six parallel points.", "",
  "buckets six list points")
C("p06.s06", "buckets.8", "8 buckets (2 x 4, paragraphs)",
  "Pale header band; two rows of four coloured boxes, each numbered with a heading over two lines and a paragraph.",
  "Eight parallel points.", "", "buckets eight list points grid")
C("p06.s07", "buckets.8_bullets", "8 buckets (2 x 4, bullets)",
  "Two rows of four coloured boxes with a heading and bullets each.", "", "", "buckets eight list bullets grid")
C("p06.s08", "buckets.8_intro", "8 buckets with intro",
  "Intro paragraph then two rows of four numbered boxes with heading + paragraph.", "", "", "buckets eight list grid intro")
C("p06.s09", "buckets.4_photo_intro", "4 photo buckets with intro",
  "Intro, then four photo tiles over dark numbered panels with heading + description.", "Four points that each have a photo.",
  "", "buckets four photos")
C("p06.s10", "buckets.4_photo", "4 tall photo buckets (dark band)",
  "Dark heading band; four tall photos with a heading over two lines and a short description beneath each.", "", "",
  "buckets four photos tall", slots="heading=ph0 | subheading=ph40",
  items="photo=ph75,ph74,ph73,ph72 | heading=ph49,ph76,ph77,ph78 | text=ph59,ph60,ph62,ph64")
C("p06.s11", "buckets.5_photo", "5 photo buckets (dark band)",
  "Dark heading band; five photos with two-line heading and description each.", "", "", "buckets five photos")
C("p06.s12", "buckets.6_photo", "6 photo buckets (dark band)",
  "Dark heading band; six narrow photos with heading over three lines and description each.", "", "", "buckets six photos")
C("p06.s13", "buckets.6_photo_intro", "6 photo buckets with intro (dark band)",
  "Dark heading band with intro; six photos with heading and description.", "", "", "buckets six photos intro")
C("p06.s14", "buckets.8_photo", "8 photo buckets (2 x 4)",
  "Dark heading band; two rows of four photos each with a two-line heading and description.", "", "", "buckets eight photos grid")

# ---------------------------------------------------------------------------
# 7 - ORG CHARTS
# ---------------------------------------------------------------------------
TREE_NOTE = ("tree = {'name': 'JANE DOE', 'role': 'Account Director', 'photo': optional path, 'children': [...]}. "
             "Up to 5 levels / 8 columns; leaf groups stack vertically automatically. Too big -> SmollanError: split by branch.")
BESPOKE = "Bespoke fixed-shape chart: pass exactly one item per person box in reading order (top-down, left-right)."
for src, vid, desc in [
        ("p07.s02", "org.bespoke_1", "1 head -> 3 managers -> 6 team members (2 under each), blue boxes."),
        ("p07.s03", "org.bespoke_2", "1 head -> 3 green managers, each with 2 people stacked beneath."),
        ("p07.s04", "org.bespoke_3", "1 head -> 4 green managers, each with 2 stacked reports."),
        ("p07.s05", "org.bespoke_4", "1 head -> 2 green managers -> 4 reports each in two stacked rows."),
        ("p07.s06", "org.bespoke_5", "1 head -> 6 columns of role headers with tall team boxes beneath."),
        ("p07.s07", "org.bespoke_6", "1 head -> 3 managers with a role-description paragraph and 2 sub-teams each."),
        ("p07.s08", "org.bespoke_7", "1 head -> 4 green leads -> a second manager -> 4 blue leads -> 8 small team boxes."),
        ("p07.s09", "org.bespoke_8", "1 head -> two rows of 4 managers, each with 2 role boxes."),
        ("p07.s10", "org.bespoke_9_photo", "Photo org chart: head with photo -> 3 managers with photos -> 6 people with small photos."),
        ("p07.s11", "org.bespoke_9_photo_b", "Variant of org.bespoke_9_photo with filled photo placeholders."),
        ("p07.s12", "org.bespoke_10_photo", "Photo org chart: head -> 4 columns x 3 people, each with a photo."),
        ("p07.s13", "org.bespoke_11_photo", "Photo org chart: head -> 4 columns x 3 people with photos and arrows."),
        ("p07.s14", "org.bespoke_12_regional", "Regional accountability: top role -> region line -> 5 regional managers with photos."),
        ("p07.s15", "org.bespoke_13_team_intros", "Team intros: two team rows of 7 people with photos, name and role.")]:
    C(src, vid, f"Bespoke org chart - {vid.split('_', 1)[1].replace('_', ' ')}", desc,
      "When the team matches this exact shape and you want the polished bespoke look.",
      "Any other team shape - use org.tree.", "org team structure people hierarchy bespoke" + (" photo" if "photo" in vid else ""),
      people=True, notes=[BESPOKE])
C("p07.s16", "org.bespoke_14_roles", "Bespoke org chart - role description boxes with key",
  "Outline boxes of role descriptions in columns with arrows, a few coloured highlight boxes and a 3-item colour key.",
  "Role-based structures (no names).", "Named people - use org.tree.", "org structure roles bespoke",
  slots="heading=ph0 | key_1=ph102 | key_2=ph100 | key_3=ph101",
  items="role=ph95,ph94,ph93,ph96,ph98,ph97,ph99,ph90,ph91,ph92,ph86,ph87,ph88,ph89,ph82,ph83,ph85,ph84,ph78,ph79,ph80",
  notes=[BESPOKE])
TREE_SLOTS = {"p07.s17": "heading=ph0 | tree=ph40", "p07.s18": "heading=ph0 | subheading=ph39 | tree=ph41",
              "p07.s19": "heading=ph0 | subheading=ph40 | tree=ph41", "p07.s20": "heading=ph0 | subheading=ph40 | tree=ph41",
              "p07.s21": "heading=ph0 | tree=ph40", "p07.s22": "heading=ph0 | subheading=ph41 | tree=ph40",
              "p07.s23": "heading=ph0 | subheading=ph41 | tree=ph40", "p07.s24": "heading=ph0 | intro=ph44 | tree=ph40",
              "p07.s25": "heading=ph0 | subheading=ph40 | tree=ph48"}
for src, vid, title, desc in [
        ("p07.s17", "org.tree", "Org chart from data", "One-line heading; the org chart is drawn from your tree data in Smollan colours."),
        ("p07.s19", "org.tree_sub", "Org chart from data + sub-heading", "Heading, sentence-case sub-heading, drawn org chart."),
        ("p07.s20", "org.tree_sub_caps", "Org chart from data + CAPS sub-heading", "Heading, CAPS sub-heading, drawn org chart."),
        ("p07.s18", "org.tree_sub_below", "Org chart from data, sub-heading as lead-in", "Heading; sub-heading lower as a lead-in; drawn org chart."),
        ("p07.s21", "org.tree_two_line", "Org chart from data, two-line heading", "Two-line heading; drawn org chart."),
        ("p07.s22", "org.tree_two_line_sub", "Org chart from data, two-line heading + sub-heading", "Two-line heading, sub-heading, chart."),
        ("p07.s23", "org.tree_two_line_sub_b", "Org chart from data, two-line heading + sub-heading (tight)", "Variant with the sub-heading tight under the heading."),
        ("p07.s24", "org.tree_intro", "Org chart from data + intro line", "Heading, one-line intro, drawn org chart."),
        ("p07.s25", "org.tree_band", "Org chart from data, pale heading band", "Pale heading band with heading + CAPS sub-heading; drawn org chart.")]:
    C(src, vid, title, desc, "Any team / reporting structure - the default org-chart choice.",
      "More than ~8 people in one row or deeper than 5 levels - split by branch.", "org team structure people hierarchy reporting",
      slots=TREE_SLOTS[src], kinds={"tree": "org"}, notes=[TREE_NOTE])
C("p07.s26", "org.tree_x2", "Two org charts + one descriptor",
  "Two drawn org charts side by side with a shared heading + two-line descriptor strip beneath.",
  "Two teams / before-and-after structures.", "", "org team two comparison before after",
  slots="heading=ph0 | tree=ph40 | tree_2=ph44 | title=ph39 | text=ph43", kinds={"tree": "org", "tree_2": "org"}, notes=[TREE_NOTE])
C("p07.s27", "org.tree_x2_desc", "Two org charts, each with a descriptor",
  "Two drawn org charts, each with its own heading + descriptor strip.", "Two teams with separate explanations.", "",
  "org team two comparison", slots="heading=ph0", items="tree=ph40,ph44 | title=ph39,ph48 | text=ph43,ph49",
  kinds={"tree": "org"}, notes=[TREE_NOTE])

# ---------------------------------------------------------------------------
# 8 - CLIENT FEEDBACK
# ---------------------------------------------------------------------------
FB = ("chart = survey scores as a bar chart: {'categories': ['Quality of Work', ...], 'series': {'Score': [8, 7, ...]}} "
      "(omit 'type' to keep the template's bar styling).")
FBK = "heading,heading_2,survey_label,action_plan"
FBH = {"heading": "default 'YOUR FEEDBACK HELPS US DRIVE'", "heading_2": "default 'IMPROVEMENT'",
       "survey_label": "default 'Smollan Client Survey'", "year": "survey year", "action_plan": "default 'Our Action Plan will be presented back to you on:'",
       "action_date": "e.g. 25 SEPTEMBER 2026", "quote": "client verbatim(s) - list of 1-3 quotes"}
C("p08.s02", "feedback.chart_quote", "Client feedback - quotes, survey chart, action-plan date",
  "Left: 'YOUR FEEDBACK HELPS US DRIVE IMPROVEMENT', survey label and year; top: quote mark and client verbatims; green "
  "action-plan date box; bottom-right: dark panel with the survey bar chart.",
  "Presenting client-survey results back to the client.", "", "feedback client survey quote testimonial results",
  slots="heading=id31 | heading_2=id34 | survey_label=id57 | year=ph41 | quote=ph38 | action_plan=id18 | action_date=ph42 | chart=ph39",
  kinds={"chart": "chart"}, keep=FBK, hints=FBH, notes=[FB])
C("p08.s03", "feedback.chart_numbered", "Client feedback - numbered points, survey chart",
  "As feedback.chart_quote but the verbatims are a numbered list and the action-plan box sits bottom-left.", "", "",
  "feedback client survey results",
  slots="heading=id31 | heading_2=id34 | survey_label=id57 | year=ph41 | quote=ph38 | action_plan=id15 | action_date=ph42 | chart=ph39",
  kinds={"chart": "chart"}, keep=FBK, hints=FBH, notes=[FB])
C("p08.s04", "feedback.photo", "Client feedback with photo",
  "Heading top-left, numbered verbatims, survey bar chart bottom-left; tall photo with a dark action-plan date bar on the right.",
  "", "", "feedback client survey photo",
  slots="heading=id7 | heading_2=id8 | quote=ph38 | chart=ph39 | photo=ph31 | action_plan=id37 | action_date=ph42",
  kinds={"chart": "chart"}, keep="heading,heading_2,action_plan", hints=FBH, notes=[FB])
C("p08.s05", "feedback.dark", "Client feedback - dark header",
  "Dark-blue top band with the heading and action-plan box; survey bar chart left; quote mark and numbered verbatims in a pale panel right.",
  "", "", "feedback client survey results",
  slots="heading=id7 | heading_2=id8 | action_plan=id17 | action_date=ph42 | chart=id5 | quote=ph38",
  kinds={"chart": "chart"}, keep="heading,heading_2,action_plan", hints=FBH, notes=[FB])

# ---------------------------------------------------------------------------
# 9 - KPIs
# ---------------------------------------------------------------------------
C("p09.s02", "kpis.6", "6 KPI columns with icons (dark)",
  "Dark-blue slide: numbered 01-06 timeline, six brand icons and under each a short list of measures.",
  "Our commitment: six KPI areas with their measures.", "", "kpis measures commitment six",
  slots="heading=ph0 | subheading=ph40", items="measures=ph46,ph45,ph44,ph43,ph42,ph41",
  hints={"measures": "list of 3-5 short measures (CAPS)"}, notes=["Heading template wording 'OUR COMMITMENT TO [CLIENT] KPIs' - [Client] is replaced by Deck(client=...)."])
C("p09.s03", "kpis.5", "5 suggested KPIs",
  "Left: 'SUGGESTED KPIs' + intro; right: five coloured KPI labels joined to description boxes.",
  "Proposing KPIs to co-create with the client.", "", "kpis suggested proposal five",
  slots="heading=ph0 | intro=ph83", items="label=ph81,ph84,ph86,ph88,ph90 | text=ph82,ph85,ph87,ph89,ph91",
  hints={"label": "one-two line KPI name (CAPS)"})
C("p09.s04", "kpis.4_callouts", "4 highlight callouts + 4 statements",
  "Left panel heading + intro; four icon highlight callouts across the top; four arrowed statements beneath.",
  "Performance principles / team commitments.", "", "kpis principles callouts four",
  slots="heading=ph0 | intro=ph83", items="callout=ph81,ph93,ph94,ph95 | text=ph96,ph97,ph98,ph99")
C("p09.s05", "kpis.3_callouts", "3 highlight callouts + 5 statements",
  "Left panel heading + intro; three icon callouts and five arrowed statements.", "", "", "kpis principles callouts",
  slots="heading=ph0 | intro=ph83 | callout_1=ph81 | callout_2=ph93 | callout_3=ph94", items="text=ph96,ph97,ph98,ph99,ph100")
C("p09.s06", "kpis.7", "7 business KPIs (dark panel)",
  "Dark left panel with heading, intro and bullets; seven coloured KPI labels with descriptions on the right.",
  "Listing up to seven KPIs with definitions.", "", "kpis business seven list",
  slots="heading=ph0 | intro=ph83 | body=ph87",
  items="label=ph81,ph98,ph100,ph102,ph104,ph106,ph108 | text=ph97,ph99,ph101,ph103,ph105,ph107,ph109")
C("p09.s07", "kpis.table", "Objective / key-result table + notes",
  "Objective vs. key-result table (4 objectives) with an arrowed note beside each row.",
  "OKR-style measurement framework.", "", "kpis okr objectives key results table",
  slots="heading=ph0 | table=id6", items="note=ph103,ph104,ph105,ph106",
  table={"table": {"header_rows": 1, "fixed": True}},
  notes=["Table rows: ['Service Perception\\n\\nYour objective...', ['Key result one', 'Key result two']] - 4 body rows."])
C("p09.s08", "kpis.strategic_table", "Strategic KPI table",
  "Strategic priorities / KPI / weighting / target / YTD score & actual table with a TOTAL row.",
  "Weighted KPI scorecards.", "", "kpis scorecard weighting target strategic table",
  slots="heading=ph0 | table=id2", table={"table": {"header_rows": 2, "footer_rows": 1, "fixed": True}}, notes=[FIXED_NOTE])
C("p09.s09", "kpis.scorecard", "KPI scorecard image + metrics",
  "Large image (e.g. dashboard screenshot) with a heading line; six bullet metrics on the right.",
  "Showing a live scorecard / dashboard with example metrics.", "", "kpis scorecard dashboard metrics",
  slots="heading=ph0 | title=ph83 | text=ph40 | photo=ph65", items="metric=ph84,ph85,ph86,ph87,ph88,ph89")

# ---------------------------------------------------------------------------
# 10 - PROCESS
# ---------------------------------------------------------------------------
P8 = "Max 8 steps per slide. For more, split across two slides or use infographic.cycle."
C("p10.s02", "process.3", "3-step process (plus signs)",
  "Three tall coloured cards (01. 02. 03.) joined by plus signs: concept heading + descriptive text.",
  "Three components that add up.", "", "process three steps components", notes=[P8])
C("p10.s03", "process.3_arrows", "3-step process (arrows)",
  "Three tall coloured cards joined by chevron arrows.", "A three-step sequence.", "", "process three steps sequence", notes=[P8])
C("p10.s04", "process.phases_matrix", "4 phases x 3 rows matrix",
  "Phase columns (Phase 1-4 + heading) on an arrow, three numbered row headings on the left, bullet cells in the grid.",
  "Phased plans where each phase covers the same 3 workstreams.", "Fewer than 4 phases.", "process phases plan matrix workstreams",
  slots="heading=ph0 | subheading=ph40 | row_1=ph57 | row_2=ph58 | row_3=ph59",
  items="phase=ph53,ph54,ph55,ph56 | heading=ph49,ph50,ph51,ph52 | row_1=ph60,ph63,ph66,ph69 | row_2=ph61,ph64,ph67,ph70 | row_3=ph62,ph65,ph68,ph71",
  notes=[P8])
C("p10.s05", "process.4_quad", "4-step quadrant + side text",
  "Four numbered quadrant tiles (2 x 2) around a ring; two-line heading, intro and bullets on the right.",
  "Four steps of a cycle with explanation.", "", "process four steps quadrant cycle",
  slots="heading=ph0 | intro=ph57 | body=ph39", items="heading=ph49,ph64,ph66,ph68 | text=ph59,ph63,ph65,ph67", notes=[P8])
C("p10.s06", "process.4_timeline", "4 steps with timeframe arrow",
  "Process title, four STEP columns (coloured tabs, heading, bullets), descriptive text and a green timeframe arrow.",
  "Four-step plan with a timeframe.", "", "process four steps timeline plan",
  slots="heading=ph0 | subheading=ph40 | title=ph42 | text=ph57 | timeframe=ph81",
  items="step=id24,id25,id26,id28 | heading=ph49,ph61,ph63,ph65 | bullets=ph76,ph82,ph83,ph84", keep="",
  hints={"step": "tab label, e.g. STEP 1 / WEEK 1-2", "timeframe": "e.g. 12-WEEK ROLL-OUT"}, notes=[P8])
C("p10.s07", "process.5", "5-step process on an arrow",
  "Numbered 01-05 timeline arrow over five coloured columns (heading, bullets) with a detail line under each.",
  "Five-step method.", "", "process five steps timeline", notes=[P8], rename={"bullets_2": "detail"})
C("p10.s08", "process.5_photos", "5-step process with photos",
  "Numbered timeline over five coloured headings, each with a photo and descriptive text.", "", "",
  "process five steps photos", notes=[P8])
C("p10.s09", "process.6_circle", "6-step circular process",
  "Six-segment ring (short headings) around a centre; six sub-headed descriptions in two side columns.",
  "Six-step cycles.", "", "process six steps circle cycle",
  slots="heading=ph0",
  items="label=ph77,ph58,ph79,ph78,ph61,ph76 | heading=ph39,ph64,ph65,ph71,ph70,id11 | text=ph66,ph67,ph68,ph74,ph73,ph72",
  hints={"label": "1-2 word segment label"}, notes=[P8, "Steps run clockwise from the top-right segment; descriptions: right column top-down then left column bottom-up."])
C("p10.s10", "process.7", "6 steps + result",
  "Three section headings over six numbered columns (two-line heading + bullets) leading to a result box.",
  "Six steps grouped into three phases, ending in an outcome.", "", "process six seven steps result outcome",
  slots="heading=ph0 | subheading=ph40 | intro=ph57 | section_1=ph78 | section_2=ph79 | section_3=ph80 | "
        "result_heading=ph77 | result_text=ph76 | footnote=ph81",
  items="heading=ph59,ph82,ph83,ph84,ph85,ph86 | bullets=ph58,ph70,ph71,ph72,ph73,ph74", notes=[P8])
C("p10.s11", "process.8_circle", "8-step circular process",
  "Eight-segment wheel around a centre heading; eight numbered sub-headings with descriptions in two columns.",
  "Eight-step cycles.", "", "process eight steps circle cycle wheel",
  slots="heading=ph0 | diagram_heading=ph40",
  items="label=ph81,ph82,ph83,ph84,ph85,ph86,ph87,ph88 | heading=ph39,ph67,ph69,ph71,ph73,ph75,ph77,ph79 | "
        "text=ph66,ph68,ph70,ph72,ph74,ph76,ph78,ph80",
  notes=[P8, "Wheel segments run clockwise from the top-right; descriptions 1-4 left column, 5-8 right column."])
C("p10.s12", "process.8", "8 steps (2 rows of 4)",
  "Two rows of four numbered coloured cards with heading + text, joined by arrows (snake order).", "Eight-step method.", "",
  "process eight steps", notes=[P8])
C("p10.s13", "process.8_loop", "8 steps repeating loop",
  "Two rows of four cards with loop arrows at both ends - an 8-step cycle that repeats.",
  "Continuous improvement loops.", "More than 8 steps (this is NOT a 9+ step layout).", "process eight steps loop cycle repeat",
  notes=[P8])

# ---------------------------------------------------------------------------
# 11 - INFOGRAPHIC
# ---------------------------------------------------------------------------
C("p11.s02", "infographic.triad", "Triad (3 circles in a cycle)",
  "Three circles in a triangle joined by arrows (each with a short descriptor) around a centre heading; three numbered "
  "sub-headed descriptions on the left.", "Three-part models where each part leads to the next.", "",
  "infographic triad three cycle model",
  slots="heading=ph0 | intro=ph57 | diagram_title=ph87 | centre=ph41",
  items="label=ph81,ph83,ph82 | heading=ph84,ph88,ph89 | text=ph66,ph68,ph70 | note=ph85,ph86,ph39",
  hints={"note": "arrow descriptor from this node to the next (2-3 words)"})
C("p11.s03", "infographic.triangle", "Triangle / pyramid (4 levels)",
  "Four-level pyramid (green to blue) with short headings; four sub-headed bullet blocks on the right.",
  "Hierarchies of need / maturity levels / layered models.", "", "infographic pyramid triangle levels hierarchy",
  slots="heading=ph0 | diagram_title=ph45", items="label=ph41,ph42,ph43,ph44 | heading=ph39,ph83,ph85,ph87 | bullets=ph82,ph84,ph86,ph88",
  remove="id16")
C("p11.s04", "infographic.circular_photo", "Circular infographic around a photo (5 points)",
  "A round photo inside a ring with five numbered nodes; five headed bullet blocks around it.",
  "Five aspects of one central idea.", "", "infographic circular five photo",
  slots="heading=ph0 | subheading=ph40 | diagram_title=ph45 | photo=ph46",
  items="heading=ph57,ph72,ph73,ph74,ph75 | bullets=ph67,ph69,ph71,ph77,ph76")
C("p11.s05", "infographic.photo_list", "Photo circle + 5 numbered points",
  "Intro and bullets on the left; a circular photo with five numbered points fanning out to the right; caption beneath.",
  "", "", "infographic photo five points",
  slots="heading=ph0 | intro=ph57 | body=ph40 | photo=ph46 | caption=ph87",
  items="heading=ph88,ph89,ph91,ph93,ph95 | text=ph82,ph90,ph92,ph94,ph96")
C("p11.s06", "infographic.pivot_point", "Pivot point (3-circle Venn)",
  "Three overlapping circles (top / left / right) meeting at a centre point labelled SMOLLAN; outer labels; text panel on the left.",
  "Showing Smollan at the intersection of three parties (e.g. retailer, shopper, brand owner).", "", "infographic venn pivot three",
  slots="heading=ph0 | intro=ph39 | subheading=ph40 | body=ph38 | circle_top=ph81 | circle_left=ph82 | circle_right=ph83 | "
        "outer_left=ph84 | outer_right=ph67 | outer_bottom=ph85")
C("p11.s07", "infographic.pivot_point_data", "Pivot point - people, technology, data",
  "Three-circle Venn (TECHNOLOGY / PEOPLE / DATA) with a centre statement and outer labels; text panel left.", "", "",
  "infographic venn pivot three technology data people",
  slots="heading=ph0 | intro=ph39 | subheading=ph40 | body=ph38 | circle_top=ph81 | circle_left=ph82 | circle_right=ph83 | "
        "centre=id9 | outer_left=ph84 | outer_right=ph86 | outer_bottom=ph85", keep="centre")
C("p11.s08", "infographic.four_circle", "Four overlapping circles + 8 descriptions",
  "Four overlapping circles around a centre model title; eight headed descriptions in two side columns.",
  "Four-part models.", "", "infographic four circles model",
  slots="heading=ph0 | model_title=ph85 | circle_top=ph81 | circle_right=ph86 | circle_bottom=ph88 | circle_left=ph87",
  items="heading=ph95,ph97,ph99,ph101,ph84,ph89,ph91,ph93 | text=ph76,ph103,ph104,ph105,ph66,ph90,ph92,ph94")
C("p11.s09", "infographic.loop", "Loop (4 arrows)",
  "Four circular arrows in a row, each with a heading, a descriptive text inside and a detail line beneath.",
  "Four-stage continuous loops.", "", "infographic loop four cycle",
  slots="heading=ph0 | subheading=ph40", items="label=ph81,ph89,ph83,ph90 | text=ph82,ph100,ph103,ph104 | detail=ph99,ph96,ph97,ph98")
C("p11.h09", "infographic.loop_intro", "Loop (4 arrows) with intro",
  "Hidden master variant of infographic.loop with an intro paragraph under the heading.", "", "", "infographic loop four cycle intro")
C("p11.s10", "infographic.cycle", "Cycle / hourglass model",
  "Hourglass of bands (top: experiences, storytellers; centre: stories; bottom: channels, audience) with side labels and "
  "two text columns.", "Two-way flows (develop / communicate).", "", "infographic cycle hourglass flow",
  slots="heading=ph0 | band_1=ph84 | band_2=ph83 | centre=ph89 | band_3=ph86 | band_4=ph85 | left_label=ph82 | right_label=ph81 | "
        "left_heading=ph88 | left_body=ph87 | right_heading=ph91 | right_body=ph90")
C("p11.s11", "infographic.swot", "SWOT analysis",
  "S / W / O / T circles around a 'SWOT Analysis' centre, with Strength, Weakness, Opportunity and Threat bullet lists.",
  "SWOT analyses.", "", "infographic swot analysis strengths weaknesses",
  slots="heading=ph0 | subheading=ph40 | strengths=ph92 | weaknesses=ph90 | opportunities=ph93 | threats=ph91")

# ---------------------------------------------------------------------------
# 12 - DEVICES
# ---------------------------------------------------------------------------
SG = "photo = screenshot image path; it is cropped to fill the screen area."
C("p12.s02", "devices.laptop_large", "Large laptop screenshot",
  "Large laptop mockup on the right; sub-heading, third heading and bullets on the left.", "Showing a dashboard / web tool.", "",
  "devices laptop screenshot dashboard", notes=[SG])
C("p12.s03", "devices.laptop_video", "Video on a laptop",
  "Large laptop mockup holding a video; text on the left.", "Embedding a demo video.", "", "devices laptop video demo",
  kinds={"video": "video"}, notes=["video = path to an .mp4 file."])
C("p12.s04", "devices.browser", "Browser-window screenshot",
  "Browser window frame on the right; heading, sub-heading, intro and bullets on the left.", "Web pages / portals.", "",
  "devices browser screenshot web", notes=[SG])
C("p12.s05", "devices.laptop_medium", "Medium laptop screenshot",
  "Medium laptop bottom-right with a caption heading; intro and bullets top-left.", "", "", "devices laptop screenshot",
  notes=[SG])
C("p12.s06", "devices.laptop_small", "Small laptop screenshot",
  "Small laptop top-right with caption heading and description beneath; sub-heading and bullets on the left.", "", "",
  "devices laptop screenshot small", slots="heading=ph0 | subheading=ph39 | body=ph40 | photo=ph69 | caption_heading=ph89 | caption=ph90",
  notes=[SG])
C("p12.s07", "devices.laptop_phone", "Laptop + phone",
  "Phone and laptop mockups side by side with captions; bullets on the left.", "Showing desktop and mobile versions.", "",
  "devices laptop phone mobile", notes=[SG])
C("p12.s08", "devices.phone", "One phone",
  "Single phone mockup on the right; heading, intro and bullets on the left.", "Mobile app screens.", "", "devices phone mobile app",
  notes=[SG])
C("p12.s09", "devices.phone_features", "Phone + 5 features",
  "Phone mockup on the right; five numbered feature headings with short descriptions on the left.", "App feature tours.", "",
  "devices phone features app", slots="heading=ph0 | intro=ph57 | photo=ph91",
  items="heading=ph84,ph88,ph89,ph92,ph94 | text=ph66,ph68,ph70,ph93,ph95", notes=[SG])
C("p12.s10", "devices.phones_2", "Two phones",
  "Two large phone mockups on the right; heading, intro and bullets on the left.", "", "", "devices phone two mobile", notes=[SG])
C("p12.s11", "devices.phones_3", "Three phones",
  "Three phone mockups on the right; sub-heading, heading and bullets on the left.", "App flows (3 screens).", "",
  "devices phone three mobile flow", notes=[SG])

# ---------------------------------------------------------------------------
# 13 - STATS
# ---------------------------------------------------------------------------
C("p13.s02", "stats.1_photo", "1 big stat + photo",
  "One huge statistic with title, descriptive text and secondary note on the left; large photo on the right.",
  "One headline proof point.", "", "stats one big number photo")
C("p13.s03", "stats.3_gauges_photos", "3 gauge stats with photos",
  "Left panel heading + intro; three ring gauges (percentage), each with a short heading, a photo and bullets.",
  "Three percentage results with visuals.", "", "stats three gauges percentages photos",
  slots="heading=ph0 | intro=ph57", items="value=id30,id41,id44 | label=ph62,ph63,ph64 | photo=ph31,ph65,ph66 | bullets=ph38,ph58,ph60",
  notes=["The gauge arcs are drawn shapes - their length does not change with the value; adjust them in PowerPoint if needed."])
C("p13.s04", "stats.4_photo", "4 stats + tall photo",
  "Heading, sub-heading and intro; four stats in a 2 x 2 grid (value, title, text); tall photo on the right.", "", "",
  "stats four numbers photo", rename={"subheading_2": "intro"})
C("p13.s05", "stats.4_cards", "4 stat cards",
  "Four coloured cards (green to blue) with big value, title and a numbered badge; description panels beneath.",
  "Four headline numbers with explanation.", "", "stats four numbers cards")
C("p13.s06", "stats.5_photos", "5 stats on dark panel + photos",
  "Two-line heading, intro, bullets and three photos on the left; dark panel with five stat rows on the right.", "", "",
  "stats five numbers photos")
C("p13.s07", "stats.2_doughnut", "2 stats with doughnut",
  "Left panel: heading, intro and a doughnut chart with the two values; right: sub-heading, paragraph and two value boxes with text.",
  "A two-part split (e.g. 70 / 30).", "", "stats two split doughnut percentage",
  slots="heading=ph0 | intro=ph57 | subheading=ph40 | text=ph61 | chart=id8 | chart_value_1=ph59 | chart_value_2=ph60",
  items="value=ph63,ph64 | text=ph62,ph65", kinds={"chart": "chart"},
  notes=["chart = {'categories': ['A', 'B'], 'series': {'Split': [70, 30]}}; chart_value_1/2 are the labels inside the ring."])
C("p13.s08", "stats.3", "3 big stats (dark band)",
  "Dark band with three numbered columns: heading, big value, descriptive text and a secondary note.",
  "Three headline numbers - the default stats slide.", "", "stats three numbers")
C("p13.s09", "stats.bubbles", "4 bubble values + year target",
  "Four overlapping coloured bubbles (value + title, e.g. quarters) and a large target value on the right.",
  "Quarterly figures adding up to a target.", "", "stats four bubbles quarters target",
  slots="heading=ph0 | intro=ph57 | text=ph71 | target_title=ph60 | target_value=ph59 | conclusion=ph70",
  items="value=ph61,ph65,ph63,ph67 | label=ph62,ph66,ph64,ph68")
C("p13.s10", "stats.mosaic_2", "Mosaic: 2 stats, photos, statement",
  "Tile mosaic: intro box, big stat with arrow to text, large statement tile; bottom row photo, text, circle stat, wide photo.",
  "", "", "stats two mosaic photos statement",
  slots="heading=ph0 | subheading=ph40 | intro=ph79 | side_intro=ph44 | statement=ph62 | photo=ph31 | photo_2=ph41",
  items="value=ph73,ph77 | label=ph74,ph78 | text=ph76,ph61")
C("p13.s11", "stats.mosaic_3", "Mosaic: 3 stats, 2 statements",
  "Tile mosaic with three stats (two in cyan tiles, one in a circle), each with descriptive text, and two statement tiles.",
  "", "", "stats three mosaic statements",
  slots="heading=ph0 | subheading=ph40 | intro=ph79 | statement=ph84 | statement_2=ph62",
  items="value=ph73,ph82,ph77 | label=ph74,ph83,ph78 | text=ph76,ph85,ph71")
C("p13.s12", "stats.4_rings_dark", "4 ring stats on dark photo",
  "Dark photographic background; four circular rings with value and title, bullets under each.", "", "",
  "stats four rings dark")

# ---------------------------------------------------------------------------
# 14 - WHY SMOLLAN
# ---------------------------------------------------------------------------
PILLAR_NOTE = "Default pillar wording is Smollan's own (An exceptional offer / A global business / An advanced operating model / A great place to work) and is kept unless you pass items."
C("p14.s02", "why.pillars", "Why Smollan - 4 pillars",
  "Dark band with brand shapes; four coloured pillar cards (01.-04.) each with a title and a one-line description; strapline beneath.",
  "Why choose Smollan.", "", "why smollan pillars differentiators unique",
  slots="heading=ph0 | subheading=ph40", items="heading=id54,id55,id56,id57 | text=id58,id59,id60,id61",
  keep="heading", keep_items=True, notes=[PILLAR_NOTE])
C("p14.s03", "why.pillars_photos", "Why Smollan - 4 pillars with photos",
  "As why.pillars with a photo above each pillar card.", "", "", "why smollan pillars photos",
  slots="heading=ph0 | subheading=ph40", items="photo=ph75,ph76,ph77,ph78 | heading=id54,id55,id56,id57 | text=id58,id59,id60,id61",
  keep="heading,subheading", keep_items=True, notes=[PILLAR_NOTE])
DIFF_ITEMS = ("heading=c18.0.1,c25.0.1,c24.1.1,c31.1.1,c26.1.1,c33.1.1,c27.1.1,c34.1.1 | "
              "text=c18.1.1,c25.1.1,c24.2.1,c31.2.1,c26.2.1,c33.2.1,c27.2.1,c34.2.1")
for src, vid, title, desc, heading_ref in [
        ("p14.s04", "why.differentiators", "Custom differentiators (pale panel)",
         "Pale left panel: 'WHAT MAKES SMOLLAN UNIQUE?', strapline and a client-specific intro; eight differentiators (heading + description) in two columns.", "ph0"),
        ("p14.s05", "why.differentiators_photo", "Custom differentiators (photo panel)",
         "As why.differentiators with a dark photographic left panel.", "ph0"),
        ("p14.s06", "why.differentiators_full_photo", "Custom differentiators (full photo background)",
         "Full dark photographic background; heading + intro left, eight differentiators right.", "ph0"),
        ("p14.s07", "why.differentiators_shapes", "Custom differentiators (brand shapes)",
         "Dark-blue left panel with brand shapes; eight differentiators.", "ph0")]:
    intro = "id3" if src == "p14.s06" else "ph40"
    C(src, vid, title, desc, "Client-specific reasons to choose Smollan (up to 8).", "", "why smollan differentiators unique custom",
      slots=f"heading={heading_ref} | intro={intro}", items=DIFF_ITEMS, keep="heading", limits={"heading": 2, "text": 3},
      hints={"heading": "default 'WHAT MAKES SMOLLAN UNIQUE?'", "intro": "client-specific intro paragraph"})
