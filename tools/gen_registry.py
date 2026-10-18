"""
Generate the RECIPES block inside smollan.py.

    python tools/gen_registry.py

Inputs : tools/auto_specs.json  (from analyze_slots.py - geometry, prompts, roles)
         tools/build_info.json  (from build_master.py - source pack/slide, designer notes)
         tools/curation.py      (hand-written ids, descriptions and slot overrides)
Output : the section between '# >>> RECIPES' and '# <<< RECIPES' in smollan.py
"""
import json
import math
import os
import pprint
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from curation import CURATION  # noqa: E402

ROLE_TO_SLOT = {"heading": "heading", "subheading": "subheading", "intro": "intro", "bullets": "body",
                "text": "text", "label": "label", "value": "value", "note": "note", "item_heading": "title",
                "photo": "photo", "chart": "chart", "table": "table", "org_area": "tree", "video": "video",
                "presenter": "presenter", "date": "date"}
ROLE_TO_FIELD = {"item_heading": "heading", "label": "label", "value": "value", "text": "text",
                 "bullets": "bullets", "note": "note", "photo": "photo", "subheading": "heading",
                 "intro": "text", "chart": "chart", "table": "table", "org_area": "tree"}
KIND = {"photo": "photo", "chart": "chart", "table": "table", "org_area": "org", "video": "video"}


def parse_ref(tok):
    tok = tok.strip()
    if tok in ("-", "none", "None"):
        return None
    m = re.match(r"^ph(\d+)$", tok)
    if m:
        return f"ph:{m.group(1)}"
    m = re.match(r"^id(\d+)$", tok)
    if m:
        return f"id:{m.group(1)}"
    m = re.match(r"^c(\d+)\.(\d+)\.(\d+)$", tok)
    if m:
        return f"cell:{m.group(1)}:{m.group(2)}:{m.group(3)}"
    if re.match(r"^(ph|id|cell):", tok):
        return tok
    raise ValueError(f"bad ref token {tok!r}")


def parse_map(s):
    """'heading=ph0 | text=ph59,ph63' -> {'heading': ['ph:0'], 'text': ['ph:59', 'ph:63']}"""
    out = {}
    if not s:
        return out
    for part in s.split("|"):
        part = part.strip()
        if not part:
            continue
        name, _, refs = part.partition("=")
        out[name.strip()] = [parse_ref(t) for t in refs.split(",")]
    return out


def clean_hint(prompt):
    p = re.sub(r"\s+", " ", (prompt or "").replace("\x0b", " ")).strip()
    return (p[:70] + "...") if len(p) > 73 else p


def limits(e, kind, override=None):
    """Estimate chars-per-line (cpl) and line capacity for a text slot.

    Montserrat is wide: ~0.72 em per capital, ~0.56 em per lower-case / digit glyph.
    Instructional prompts often overflow their own box in the templates, so they are
    only trusted for calibration on body text that states 'no longer than N lines';
    real example copy (designer-filled slides) is trusted everywhere.
    """
    if kind != "text" or not e or not e.get("w"):
        return {"max_lines": override} if override else {}
    size = e.get("size") or 12
    caps = e.get("caps")
    role = e.get("role")
    em = 0.72 if caps else (0.7 if role == "value" else 0.56)
    cpl = max(3, math.floor(e["w"] * 72 / (size * em)))
    cap = max(1, math.floor(e.get("h", 0.3) * 72 / (size * 1.2) + 0.25))
    max_lines = override or e.get("max_lines")
    samples = []
    ex, pr = (e.get("example") or ""), (e.get("prompt") or "")
    if ex and ex.strip() != pr.strip():
        samples.append(ex)
    if pr and role not in ("heading", "subheading", "label", "item_heading", "value") and re.search(r"longer than|maximum", pr, re.I):
        samples.append(pr)
    for sample in samples:
        paras = [p for p in re.split("[\n\x0b]", sample) if p.strip()]
        need = sum(max(1, math.ceil(len(p) / int(cpl * 1.1))) for p in paras)
        limit = max_lines or cap
        if need > limit:
            if max_lines:
                while sum(max(1, math.ceil(len(p) / int(cpl * 1.1))) for p in paras) > limit and cpl < 400:
                    cpl += 1
            else:
                cap = need
    out = {"cpl": cpl, "cap": cap}
    if max_lines:
        out["max_lines"] = max_lines
    return out


def slot_spec(ref, e, kind=None, hint=None, lim=None):
    kind = kind or (KIND.get(e["role"], "text") if e else "text")
    spec = {"ref": ref, "kind": kind}
    spec.update(limits(e, kind, lim))
    h = hint if hint is not None else (clean_hint(e.get("prompt") or e.get("example")) if e else "")
    if e and e.get("cells") and hint is None:
        head = [re.sub(r"\s+", " ", c).strip()[:18] for c in e["cells"][0]]
        h = (f"template grid {e['rows']} rows x {e['cols']} cols{' (merged cells)' if e.get('merged') else ''}; "
             f"first row: {' | '.join(x or '-' for x in head)}")
    if h:
        spec["hint"] = h
    return spec


def reading_key(e):
    return (round(e["y"] / 0.45), e["x"])


def people_items(els):
    texts = [e for e in els if e["role"] not in ("heading", "photo", "subheading") and e.get("prompt") is not None
             and e.get("kind") in ("ph", "shape") and e["role"] != "table"]
    photos = [e for e in els if e["role"] == "photo"]
    used, people = set(), []
    for a in sorted(texts, key=reading_key):
        if a["ref"] in used:
            continue
        pa = (a.get("prompt") or a.get("example") or "")
        if not pa.strip() or pa != pa.upper():
            continue
        role = None
        for b in texts:
            pb = b.get("prompt") or b.get("example") or ""
            if b["ref"] in used or b is a or pb == pb.upper():
                continue
            if abs(b["x"] - a["x"]) < 0.2 and 0 < b["y"] - a["y"] < 0.7:
                role = b
                break
        used.add(a["ref"])
        if role:
            used.add(role["ref"])
        photo = None
        for p in photos:
            if p["ref"] in used:
                continue
            if -0.4 < a["x"] - (p["x"] + p["w"]) < 0.4 and abs((p["y"] + p["h"] / 2) - (a["y"] + 0.2)) < 0.7:
                photo = p
                break
        if photo:
            used.add(photo["ref"])
        people.append((a, role, photo))
    leftovers = [e for e in texts if e["ref"] not in used]
    return people, leftovers, [p for p in photos if p["ref"] not in used]


def build_recipe(c, auto, info):
    src = c["src"]
    a = auto[src]
    els = a["elements"]
    by_ref = {e["ref"]: e for e in els}
    # drop layout-only table/chart placeholders when the slide has its own table/chart
    kinds_present = {e["role"] for e in els if not e.get("layout_only")}
    els = [e for e in els if not (e.get("layout_only") and e["role"] in kinds_present and e["role"] in ("table", "chart"))]
    kinds = c.get("kinds", {})
    hints = c.get("hints", {})
    slots, items = {}, None

    if c.get("slots") is not None or c.get("items") is not None:
        for name, refs in parse_map(c.get("slots", "")).items():
            ref = refs[0]
            slots[name] = slot_spec(ref, by_ref.get(ref), kinds.get(name), hints.get(name), c.get("limits", {}).get(name))
        im = parse_map(c.get("items", ""))
        if im:
            n = max(len(v) for v in im.values())
            fields = {}
            for f, refs in im.items():
                refs = refs + [None] * (n - len(refs))
                first = next((by_ref.get(r) for r in refs if r and by_ref.get(r)), None)
                spec = slot_spec(None, first, kinds.get(f), hints.get(f), c.get("limits", {}).get(f))
                spec.pop("ref")
                spec["refs"] = refs
                fields[f] = spec
            items = {"n": n, "min": c.get("min_items", n), "fields": fields}
    elif c.get("people"):
        people, leftovers, spare_photos = people_items(els)
        for e in sorted([e for e in els if e["role"] in ("heading", "subheading")], key=reading_key):
            nm = e["role"] if e["role"] not in slots else e["role"] + "_2"
            slots[nm] = slot_spec(e["ref"], e)
        fields = {"name": [p[0]["ref"] for p in people], "role": [p[1]["ref"] if p[1] else None for p in people]}
        if any(p[2] for p in people):
            fields["photo"] = [p[2]["ref"] if p[2] else None for p in people]
        items = {"n": len(people), "min": len(people), "fields": {}}
        for f, refs in fields.items():
            first = next((by_ref[r] for r in refs if r), None)
            spec = slot_spec(None, first, "photo" if f == "photo" else "text",
                             {"name": "person's name (caps)", "role": "title / designation",
                              "photo": "head-and-shoulders photo"}[f])
            spec.pop("ref")
            spec["refs"] = refs
            items["fields"][f] = spec
        for i, e in enumerate(sorted(leftovers, key=reading_key)):
            slots[f"text_{i + 1}"] = slot_spec(e["ref"], e)
        for i, e in enumerate(sorted(spare_photos, key=reading_key)):
            slots[f"photo_{i + 1}"] = slot_spec(e["ref"], e)
    else:
        it = a.get("items")
        grouped = set()
        if it:
            fields = {}
            for f, refs in it["fields"].items():
                role = f.rstrip("2")
                name = ROLE_TO_FIELD.get(role, role)
                if name in fields:
                    name = f"{name}_2"
                if name == "heading" and "heading" in fields:
                    name = "subheading"
                spec = slot_spec(None, by_ref.get(refs[0]))
                spec.pop("ref")
                spec["refs"] = refs
                fields[name] = spec
                grouped |= set(refs)
            items = {"n": it["n"], "min": c.get("min_items", it["n"]), "fields": fields}
        counts = {}
        for e in sorted([e for e in els if e["ref"] not in grouped], key=reading_key):
            base = ROLE_TO_SLOT.get(e["role"], e["role"])
            counts[base] = counts.get(base, 0) + 1
            name = base if counts[base] == 1 else f"{base}_{counts[base]}"
            slots[name] = slot_spec(e["ref"], e, kinds.get(name), hints.get(name))
    for name, opts in c.get("table", {}).items():
        if name in slots:
            slots[name]["table"] = opts
        elif items and name in items["fields"]:
            items["fields"][name]["table"] = opts
    for old, new in c.get("rename", {}).items():
        if old in slots:
            slots = {(new if k == old else k): v for k, v in slots.items()}
        elif items and old in items["fields"]:
            items["fields"] = {(new if k == old else k): v for k, v in items["fields"].items()}
    if items and c.get("keep_items"):
        items["keep_default"] = True
    for name in [k.strip() for k in c.get("keep", "").split(",") if k.strip()]:
        if name in slots:
            slots[name]["keep"] = True
            e = by_ref.get(slots[name]["ref"])
            if e and not (e.get("example") or "").strip() and e.get("prompt"):
                # wording lives only in the layout prompt (never rendered) - write it explicitly
                slots[name]["default"] = e["prompt"].replace("\x0b", "\n")
        elif items and name in items["fields"]:
            items["fields"][name]["keep"] = True
    for name, k in kinds.items():
        for tgt in ([slots[name]] if name in slots else []) + ([items["fields"][name]] if items and name in items["fields"] else []):
            tgt["kind"] = k
            if k != "text":
                for key in ("cpl", "cap", "max_lines"):
                    tgt.pop(key, None)
    for name, h in hints.items():
        if name in slots:
            slots[name]["hint"] = h
        elif items and name in items["fields"]:
            items["fields"][name]["hint"] = h
    if "heading" in slots and "heading" in c.get("required", ["heading"]):
        slots["heading"]["required"] = False
    # order: heading first
    order = ["heading", "subheading", "intro"]
    slots = {k: slots[k] for k in sorted(slots, key=lambda k: (order.index(k) if k in order else 9))}
    bi = info.get(src, {})
    r = {
        "src": src, "category": c["id"].split(".")[0], "title": c["title"], "summary": c["summary"],
        "use_when": c.get("use", ""), "avoid_when": c.get("avoid", ""), "tags": c.get("tags", "").split(),
        "pack": bi.get("pack", ""), "layout": a["layout"].split(" | ", 1)[-1],
        "slots": slots, "items": items,
    }
    notes = list(c.get("notes", [])) + [n for n in bi.get("notes", []) if n not in c.get("notes", [])
                                         and not re.search(r"EDIT TABLES? IN MASTER", n, re.I)]
    if notes:
        r["notes"] = notes
    if c.get("remove"):
        r["remove"] = [parse_ref(t) for t in c["remove"].split(",")]
    if c.get("special"):
        r["special"] = c["special"]
    return r


def main():
    auto = json.load(open(os.path.join(HERE, "auto_specs.json"), encoding="utf-8"))
    info = json.load(open(os.path.join(HERE, "build_info.json"), encoding="utf-8"))
    recipes = {}
    seen_src = set()
    for c in CURATION:
        if c["id"] in recipes:
            raise SystemExit(f"duplicate id {c['id']}")
        recipes[c["id"]] = build_recipe(c, auto, info)
        seen_src.add(c["src"])
    missing = [k for k in auto if k not in seen_src]
    if missing:
        print("WARNING: template slides without a recipe:", missing)
    body = pprint.pformat(recipes, width=118, sort_dicts=False)
    block = ("# >>> RECIPES (generated by tools/gen_registry.py - edit tools/curation.py, not this block)\n"
             f"RECIPES = {body}\n# <<< RECIPES\n")
    path = os.path.join(ROOT, "smollan.py")
    src = open(path, encoding="utf-8").read()
    # one-line-per-recipe summary index near the top of the file
    order = ["cover", "divider", "title", "closing", "thankyou", "stats", "kpis", "process", "infographic",
             "buckets", "graphs", "tables", "org", "feedback", "devices", "why"]
    cats = {}
    for rid, r in recipes.items():
        cats.setdefault(r["category"], []).append(rid)
    lines = ["# >>> CATALOG SUMMARY (generated by tools/gen_registry.py)",
             "# " + "=" * 77, f"# CATALOG SUMMARY - {len(recipes)} recipes. describe('<id>') / python smollan.py show <id>",
             "# for slots, limits and an example call. Thumbnails: thumbnails/<id>.png", "# " + "=" * 77]
    for cat in sorted(cats, key=lambda c: order.index(c) if c in order else 99):
        lines.append(f"# [{cat}]")
        for rid in cats[cat]:
            r = recipes[rid]
            it = r.get("items")
            cnt = f" ({it['n']} items)" if it else ""
            lines.append(f"#   {rid:<32} {r['title']}{cnt}")
    summary = "\n".join(lines) + "\n# <<< CATALOG SUMMARY\n"
    if "# >>> CATALOG SUMMARY" in src:
        src = re.sub(r"# >>> CATALOG SUMMARY.*?# <<< CATALOG SUMMARY\n", lambda m: summary, src, flags=re.S)
    else:
        src = src.replace("from __future__ import annotations\n", summary + "\nfrom __future__ import annotations\n", 1)
    if "# >>> RECIPES" in src:
        src = re.sub(r"# >>> RECIPES.*?# <<< RECIPES\n", lambda m: block, src, flags=re.S)
    else:
        src = src.replace("\n\n# =============================================================================\n# 8. RECIPE LOOKUP",
                          "\n\n" + block + "\n\n# =============================================================================\n# 8. RECIPE LOOKUP", 1)
    open(path, "w", encoding="utf-8").write(src)
    print(f"wrote {len(recipes)} recipes into smollan.py")


if __name__ == "__main__":
    main()
