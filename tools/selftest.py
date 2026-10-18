"""
Self-test: build one deck that uses EVERY recipe with generated sample content.

    python tools/selftest.py [out.pptx] [recipe-prefix]

Fails loudly on any SmollanError; prints preflight issues (template text left behind =
a slot the registry is missing). Render the result with tools/render.ps1 to eyeball it.
"""
import json
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from smollan import RECIPES, Deck, assets  # noqa: E402

WORDS = ("Smollan field teams drive availability visibility and sales growth across modern and traditional trade "
         "with real time data smarter routes trained merchandisers and clear weekly reporting for every store "
         "cluster channel and category so brands win at the point of purchase").split()
PHOTOS = [n for n, _ in assets.photos(show=False)]
AUTO = json.load(open(os.path.join(ROOT, "tools", "auto_specs.json"), encoding="utf-8"))


def text_for(spec, name, i=0):
    limit = spec.get("max_lines") or spec.get("cap") or 1
    cpl = spec.get("cpl") or 30
    target = max(3, int(limit * cpl * 0.55))
    if name in ("value", "chart_value_1", "chart_value_2", "target_value") or name.endswith("value"):
        vals = [v for v in ["87%", "56%", "R2.4m", "38%", "12", "74%", "9/10", "67%"] if len(v) <= cpl] or ["9"]
        return vals[i % len(vals)]
    words, out = WORDS[i % 7:] + WORDS, []
    for w in words:
        if len(" ".join(out + [w])) > target:
            break
        out.append(w)
    s = " ".join(out) or "Retail"
    if spec.get("hint", "").isupper() or name in ("heading", "label", "title", "callout", "step", "phase", "measures"):
        s = s.upper()
    if name in ("body", "bullets", "measures", "strengths", "weaknesses", "opportunities", "threats", "quote") and limit >= 3:
        n = 3 if limit >= 6 else 2
        per = max(3, target // n)
        return [s[:per].rsplit(" ", 1)[0] for _ in range(n)]
    return s[: max(3, target)].rsplit(" ", 1)[0] if len(s) > target else s


def table_for(rid, spec):
    ref = spec["ref"]
    el = next(e for e in AUTO[RECIPES[rid]["src"]]["elements"] if e["ref"] == ref)
    rows, cols = el.get("rows") or 6, el.get("cols") or 4
    opts = spec.get("table", {})
    h, f = opts.get("header_rows", 1), opts.get("footer_rows", 0)
    body = rows - h - f
    if not opts.get("fixed") and not el.get("merged"):
        body = max(2, body - 1)
    head = [[("HEAD " + str(c + 1)) if c else "ITEM" for c in range(cols)] for _ in range(h)]
    rows_ = [[f"Row {r + 1}"] + [(True if (r + c) % 3 == 0 else f"{(r + 1) * (c + 2)}") for c in range(1, cols)] for r in range(body)]
    foot = [["TOTAL"] + [str(99 + c) for c in range(1, cols)] for _ in range(f)]
    spec_ = {"header": head, "rows": rows_}
    if f:
        spec_["footer"] = foot
    return spec_


TREE = {"name": "Thandi Mokoena", "role": "Account Director", "children": [
    {"name": "Sipho Dlamini", "role": "Field Manager", "children": [{"name": "Ann Lee", "role": "Merchandiser"}, {"name": "Raj Patel", "role": "Merchandiser"}]},
    {"name": "Maria Silva", "role": "Insights Lead", "children": [{"name": "Tom Berg", "role": "Analyst"}]},
    {"name": "Ken Otieno", "role": "Trade Marketing", "children": [{"name": "Lea Roux", "role": "Promoter"}, {"name": "Ola Ade", "role": "Promoter"}]}]}


def value_for(rid, name, spec, i=0):
    k = spec["kind"]
    if k == "photo":
        return assets.photo(PHOTOS[(i + len(name)) % len(PHOTOS)])
    if k == "chart":
        c = {"categories": ["Q1", "Q2", "Q3", "Q4"], "series": {"2025": [4.2, 5.1, 5.8, 6.4], "2026": [4.8, 5.9, 6.6, 7.3]}}
        if rid.startswith("graphs.1") and RECIPES[rid]["src"] in ("p05.s03", "p05.s04"):
            c = {"type": "waterfall", "categories": ["Start", "Volume", "Price", "Mix", "Cost", "End"],
                 "series": {"Value": [100, 20, 15, -10, -8, None]}, "totals": [0, 5]}
        if rid.startswith("feedback"):
            c = {"categories": ["Quality of Work", "Communication", "Value for Money", "Leadership", "Proactivity"],
                 "series": {"Score": [8, 7, 9, 8, 7]}}
        if rid == "stats.2_doughnut":
            c = {"categories": ["Modern trade", "Traditional"], "series": {"Split": [70, 30]}}
        return c
    if k == "table":
        return table_for(rid, spec) if "ref" in spec else None
    if k == "gantt":
        return {"periods": [str(n) for n in range(1, 13)],
                "tasks": [{"label": f"MILESTONE {n}", "start": n, "end": n + 2} for n in range(1, 8)]}
    if k == "org":
        return TREE
    if k == "video":
        return None
    return text_for(spec, name, i)


def content_for(rid):
    r = RECIPES[rid]
    c = {name: value_for(rid, name, s) for name, s in r["slots"].items() if not s.get("keep")}
    it = r.get("items")
    if it:
        items = []
        for i in range(it["n"]):
            item = {}
            for f, s in it["fields"].items():
                if s["kind"] == "table":
                    ref = s["refs"][i]
                    item[f] = table_for(rid, {**s, "ref": ref})
                else:
                    item[f] = value_for(rid, f, s, i)
            items.append(item)
        c["items"] = items
    return {k: v for k, v in c.items() if v is not None}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "examples", "selftest_all_recipes.pptx")
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""
    d = Deck(title="SMOLLAN DESIGN SYSTEM SELF-TEST", presenter="Design System", date="OCTOBER 2026", client="Acme Foods")
    failures = []
    for rid in RECIPES:
        if not rid.startswith(prefix):
            continue
        try:
            d.add(rid, **content_for(rid))
        except Exception as e:  # noqa: BLE001
            failures.append((rid, e))
            traceback.print_exc(limit=2)
    d.save(out)
    print(f"\n{len(failures)} recipe failures")
    for rid, e in failures:
        print(f"  FAIL {rid}: {e}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
