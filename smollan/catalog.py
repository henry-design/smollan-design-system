"""Recipe lookup, search, human/agent-readable specs and the CATALOG.md generator."""
from __future__ import annotations

import json
import os
import re

from .config import REPO_ROOT
from .errors import SmollanError
from .recipes import RECIPES


def _all_recipes():
    return RECIPES


def resolve(recipe: str) -> str:
    """Accept a recipe id, a template key ('p13.s08') or an exact original layout name."""
    if recipe in RECIPES:
        return recipe
    for rid, r in RECIPES.items():
        if recipe == r["src"] or recipe == r.get("layout"):
            return rid
    close = [rid for rid in RECIPES if recipe.split(".")[0] in rid][:8]
    raise SmollanError(f"unknown recipe {recipe!r}. Try find('<what you want to show>'). "
                       f"Similar ids: {close or sorted(RECIPES)[:10]}")


_SYNONYMS = {
    "team": "org", "structure": "org", "hierarchy": "org", "people": "org", "organisation": "org",
    "organization": "org", "kpi": "kpis", "measure": "kpis", "measures": "kpis", "metric": "kpis",
    "scorecard": "kpis", "step": "process", "steps": "process", "phases": "process", "timeline": "process",
    "roadmap": "process", "methodology": "process", "number": "stats", "numbers": "stats", "percent": "stats",
    "percentage": "stats", "statistic": "stats", "statistics": "stats", "chart": "graphs", "graph": "graphs",
    "trend": "graphs", "data": "graphs", "quote": "feedback", "testimonial": "feedback", "survey": "feedback",
    "differentiators": "why", "unique": "why", "pillars": "why", "intro": "cover", "opening": "cover",
    "title": "cover", "section": "divider", "break": "divider", "end": "closing", "thanks": "thankyou",
    "thank": "thankyou", "screenshot": "devices", "app": "devices", "phone": "devices", "laptop": "devices",
    "dashboard": "devices", "list": "buckets", "things": "buckets", "points": "buckets", "diagram": "infographic",
    "framework": "infographic", "swot": "infographic", "venn": "infographic", "cycle": "infographic",
    "comparison": "tables", "matrix": "tables", "grid": "tables", "gantt": "tables", "table": "tables",
}
_NUMWORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}


def find(query: str, n: int = 8, show: bool = True):
    """Rank recipes for a plain-English need, e.g. find('3 statistics with photos')."""
    words = re.findall(r"[a-z0-9]+", query.lower())
    count = next((int(w) if w.isdigit() else _NUMWORDS[w] for w in words if w.isdigit() or w in _NUMWORDS), None)
    terms = set(words) | {_SYNONYMS[w] for w in words if w in _SYNONYMS}
    scored = []
    for rid, r in RECIPES.items():
        fields = [(r["category"], 5), (" ".join(r.get("tags", [])), 3), (r["title"], 3),
                  (r["summary"], 2), (r.get("use_when", ""), 2), (rid, 2)]
        s = 0.0
        for text, w in fields:
            toks = set(re.findall(r"[a-z0-9]+", text.lower()))
            s += w * len(terms & toks)
        if count is not None and r.get("items") and r["items"]["min"] <= count <= r["items"]["n"]:
            s += 6
        if s:
            scored.append((s, rid))
    scored.sort(key=lambda t: (-t[0], t[1]))
    hits = [rid for _, rid in scored[:n]]
    if show:
        for rid in hits:
            print(f"{rid:<28} {RECIPES[rid]['title']}")
    return hits


def alternatives(rid: str, count: int | None = None) -> list[str]:
    r = RECIPES[rid]
    out = []
    for oid, o in RECIPES.items():
        if oid == rid or o["category"] != r["category"]:
            continue
        if count is None or (o.get("items") and o["items"]["min"] <= count <= o["items"]["n"]):
            out.append(oid)
    return out


def _example_value(name, spec, kind=None):
    kind = kind or spec["kind"]
    if kind == "photo":
        return "path/to/photo.jpg"
    if kind == "chart":
        return {"type": "column", "categories": ["Q1", "Q2", "Q3"], "series": {"2026": [4.1, 5.2, 6.3]}}
    if kind == "table":
        return {"header": ["COLUMN A", "COLUMN B"], "rows": [["Row 1", "Value"], ["Row 2", "Value"]]}
    if kind == "gantt":
        return {"periods": ["1", "2", "3", "4"], "tasks": [{"label": "KICK-OFF", "start": 1, "end": 2}]}
    if kind == "org":
        return {"name": "Jane Doe", "role": "Account Director",
                "children": [{"name": "John Roe", "role": "Field Manager"}]}
    if kind == "video":
        return "path/to/video.mp4"
    if kind == "logo":
        return "path/to/client_logo.png"
    if name in ("heading",):
        return "YOUR HEADING"
    if name == "value":
        return "87%"
    return f"{name.replace('_', ' ').capitalize()} text"


def example_call(rid: str) -> str:
    r = RECIPES[rid]
    lines = [f'deck.add("{rid}",']
    for name, spec in r["slots"].items():
        lines.append(f"    {name}={_example_value(name, spec)!r},")
    if r.get("items"):
        it = r["items"]
        one = {f: _example_value(f, s) for f, s in it["fields"].items()}
        lines.append(f"    items=[{one!r},  # x{it['n'] if it['min'] == it['n'] else str(it['min']) + '-' + str(it['n'])}")
        lines.append("           ...],")
    lines.append(")")
    return "\n".join(lines)


def _limit_text(spec):
    bits = []
    if spec.get("max_lines"):
        bits.append(f"max {spec['max_lines']} line{'s' if spec['max_lines'] > 1 else ''}")
    elif spec.get("cap"):
        bits.append(f"fits ~{spec['cap']} line{'s' if spec['cap'] > 1 else ''}")
    if spec.get("cpl") and spec["kind"] == "text":
        bits.append(f"~{spec['cpl']} chars/line")
    if spec["kind"] == "table":
        t = spec.get("table", {})
        bits.append(f"{t.get('header_rows', 1)} header row(s)")
        if t.get("footer_rows"):
            bits.append(f"{t['footer_rows']} footer row(s)")
        bits.append("FIXED grid" if t.get("fixed") else "rows/cols flexible")
    if spec.get("keep"):
        bits.append("optional - keeps Smollan wording")
    return ", ".join(bits)


def describe(rid: str) -> str:
    """Full human/agent-readable spec of one recipe."""
    rid = resolve(rid)
    r = RECIPES[rid]
    out = [f"{rid}  -  {r['title']}", "=" * (len(rid) + len(r['title']) + 5),
           f"Category : {r['category']}", f"Source   : {r['pack']} / layout '{r['layout']}' (template {r['src']})",
           "", r["summary"], "", f"USE WHEN : {r.get('use_when', '')}", f"AVOID    : {r.get('avoid_when', '')}"]
    if r.get("notes"):
        out += ["", "NOTES:"] + [f"  - {n}" for n in r["notes"]]
    out += ["", "SLOTS:"]
    for name, s in r["slots"].items():
        req = " (required)" if s.get("required") else ""
        out.append(f"  {name:<14} {s['kind']:<6} {_limit_text(s):<32} {s.get('hint', '')}{req}")
    if r.get("items"):
        it = r["items"]
        cnt = it["n"] if it["min"] == it["n"] else f"{it['min']}-{it['n']}"
        out += ["", f"ITEMS: exactly {cnt} item dicts in items=[...]" if it["min"] == it["n"]
                else f"ITEMS: {cnt} item dicts in items=[...] (unused blocks are removed)"]
        for f, s in it["fields"].items():
            out.append(f"  {f:<14} {s['kind']:<6} {_limit_text(s):<32} {s.get('hint', '')}")
    alts = alternatives(rid)
    if alts:
        out += ["", "ALTERNATIVES: " + ", ".join(alts[:10])]
    out += ["", "EXAMPLE:", example_call(rid)]
    return "\n".join(out)


def show(rid: str):
    print(describe(rid))


CATEGORY_ORDER = ["cover", "divider", "title", "closing", "thankyou", "stats", "kpis", "process",
                  "infographic", "buckets", "graphs", "tables", "org", "feedback", "devices", "why"]
CATEGORY_INFO = {
    "cover": "Opening slides. Core shape covers (3 colour tones) and photo-led covers (6 photo families).",
    "divider": "Section breaks between chapters of the deck.",
    "title": "Plain content slides: heading (+ sub-heading) and a body text area. The fallback for anything.",
    "closing": "The Smollan end slide (logo, contact line).",
    "thankyou": "Thank-you slides with a personal message and next steps.",
    "stats": "Big-number proof points: 1-5 statistics, with or without photos.",
    "kpis": "What we will measure: KPI grids, KPI tables and scorecards.",
    "process": "Step-by-step methods: 3 to 8 steps (hard ceiling 8 per slide).",
    "infographic": "Concept diagrams: triad, triangle, circular, pivot-point (Venn), loop, cycle, SWOT.",
    "buckets": "'Here are N things' grids: 4-8 text buckets, optionally with a photo per bucket.",
    "graphs": "Native, editable charts: 1 or 2 per slide, with intro, description or text columns.",
    "tables": "Styled tables: comparison grids, tick matrices, gantt, scenario tables (incl. Growth Teams styles).",
    "org": "Team structures: drawn from tree data, or bespoke fixed-shape org charts (with photos).",
    "feedback": "Client survey feedback: quote + survey bar chart + action-plan date.",
    "devices": "Screens on devices: laptop, browser, phone(s) and video frames for app/dashboard shots.",
    "why": "Why Smollan: 4 pillars and custom differentiator grids.",
}


def catalog(write: bool = True, out_dir: str | None = None):
    """Regenerate CATALOG.md and catalog.json from RECIPES (repo root in a checkout, else the cwd)."""
    out_dir = out_dir or REPO_ROOT or os.getcwd()
    cats = {}
    for rid, r in RECIPES.items():
        cats.setdefault(r["category"], []).append(rid)
    md = ["# Smollan Design System - Slide Catalog", "",
          f"{len(RECIPES)} slide recipes across {len(cats)} categories. Every recipe is one on-brand slide "
          "that the `smollan` Python package fills with your content.", "",
          "**How to use:** pick a recipe below (or `find('what you want to show')`), check its slots with "
          "`show('<id>')`, then `deck.add('<id>', **slots)`. AI agents: start with [AGENTS.md](AGENTS.md); people: see [docs/](docs/).", "",
          "## Quick picker", "", "| I want to show... | Category | Start with |", "|---|---|---|"]
    picks = {
        "a title / opening slide": ("cover", "cover.dark_blue"), "a new section": ("divider", "divider.dark_blue"),
        "a heading and some text / bullets": ("title", "title.one_line_sub"),
        "1-5 headline numbers": ("stats", "stats.3"), "what we will measure": ("kpis", "kpis.6"),
        "a step-by-step method": ("process", "process.5"), "a concept / framework": ("infographic", "infographic.triad"),
        "N points / benefits / services": ("buckets", "buckets.6"), "a chart / trend": ("graphs", "graphs.1"),
        "a data table / comparison": ("tables", "tables.clean"), "a team structure": ("org", "org.tree"),
        "client survey results": ("feedback", "feedback.chart_quote"), "an app or dashboard screenshot": ("devices", "devices.laptop_large"),
        "why choose Smollan": ("why", "why.pillars"), "the end": ("closing", "closing"),
    }
    for need, (cat, rid) in picks.items():
        if rid in RECIPES:
            md.append(f"| {need} | {cat} | `{rid}` |")
    md.append("")
    for cat in sorted(cats, key=lambda c: CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else 99):
        md += [f"## {cat}", "", CATEGORY_INFO.get(cat, ""), ""]
        md += ["| id | what it is |", "|---|---|"]
        for rid in cats[cat]:
            md.append(f"| [`{rid}`](#{rid.replace('.', '')}) | {RECIPES[rid]['title']} |")
        md.append("")
        for rid in cats[cat]:
            r = RECIPES[rid]
            md += [f"### {rid}", ""]
            thumb = f"thumbnails/{rid}.png"
            if os.path.exists(os.path.join(out_dir, thumb)):
                md += [f"![{rid}]({thumb})", ""]
            md += [f"**{r['title']}** - {r['summary']}", "",
                   f"- **Use when:** {r.get('use_when', '')}", f"- **Avoid when:** {r.get('avoid_when', '')}",
                   f"- **Source:** `{r['pack']}` -> layout `{r['layout']}`"]
            for n_ in r.get("notes", []):
                md.append(f"- **Note:** {n_}")
            md += ["", "| slot | kind | limit | what goes here |", "|---|---|---|---|"]
            for name, s in r["slots"].items():
                md.append(f"| `{name}` | {s['kind']} | {_limit_text(s)} | {s.get('hint', '')} |")
            if r.get("items"):
                it = r["items"]
                cnt = it["n"] if it["min"] == it["n"] else f"{it['min']}-{it['n']}"
                for f, s in it["fields"].items():
                    md.append(f"| `items[{cnt}].{f}` | {s['kind']} | {_limit_text(s)} | {s.get('hint', '')} |")
            md += ["", "```python", example_call(rid), "```", ""]
    if write:
        with open(os.path.join(out_dir, "CATALOG.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        with open(os.path.join(out_dir, "catalog.json"), "w", encoding="utf-8") as f:
            json.dump({"categories": CATEGORY_INFO, "recipes": RECIPES}, f, indent=1, ensure_ascii=False)
    return "\n".join(md)
