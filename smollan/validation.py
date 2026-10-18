"""Check content against a recipe's rules before anything is built."""
from __future__ import annotations

from .catalog import alternatives
from .recipes import RECIPES
from .text import _plain


def _est_lines(value, cpl):
    if not cpl:
        return 0
    total = 0
    for para in _plain(value):
        for seg in para.replace("**", "").split("\n"):
            total += max(1, -(-len(seg) // cpl))
    return total


def _check_text(rid, where, spec, value, errors):
    if spec["kind"] != "text" or value is None:
        return
    if not isinstance(value, (str, list, tuple)):
        errors.append(f"{where}: expected text (str or list of str), got {type(value).__name__}")
        return
    limit = spec.get("max_lines") or spec.get("cap")
    cpl = spec.get("cpl")
    if not limit or not cpl:
        return
    est = _est_lines(value, int(cpl * 1.1))
    if est > limit:
        errors.append(f"{where}: ~{est} lines but this slot holds {limit} (about {limit * cpl} characters). "
                      f"Shorten the copy - do not shrink the font.")


def validate(rid: str, content: dict) -> list[str]:
    r = RECIPES[rid]
    errors = []
    allowed = set(r["slots"]) | ({"items"} if r.get("items") else set())
    for k in content:
        if k not in allowed:
            errors.append(f"unknown slot {k!r} for {rid}; valid slots: {sorted(allowed)}")
    for name, spec in r["slots"].items():
        if spec.get("required") and content.get(name) in (None, "", []):
            errors.append(f"{rid}.{name} is required")
        _check_text(rid, f"{rid}.{name}", spec, content.get(name), errors)
    it = r.get("items")
    items = content.get("items")
    if it:
        if items is None and it.get("keep_default"):
            items = None
        elif items is None:
            items = []
    if it and items is not None:
        if not isinstance(items, (list, tuple)) or not all(isinstance(i, dict) for i in items):
            errors.append(f"{rid}.items must be a list of dicts with keys {list(it['fields'])}")
        elif not items:
            cnt = it["n"] if it["min"] == it["n"] else f"{it['min']}-{it['n']}"
            errors.append(f"{rid} needs items=[...] with {cnt} dicts using the fields {list(it['fields'])} "
                          f"- see describe('{rid}')")
        elif not (it["min"] <= len(items) <= it["n"]):
            cnt = it["n"] if it["min"] == it["n"] else f"{it['min']}-{it['n']}"
            alts = alternatives(rid, len(items))
            singles = [oid for oid, o in RECIPES.items() if o["category"] == r["category"] and not o.get("items")]
            if alts:
                hint = f" Recipes in '{r['category']}' that take {len(items)}: {alts}"
            elif len(items) == 1 and singles:
                hint = f" For a single block use a recipe with named slots instead: {singles}"
            else:
                hint = f" No '{r['category']}' recipe takes {len(items)} - split the content over two slides."
            errors.append(f"{rid} holds {cnt} items; you passed {len(items)}.{hint}")
        else:
            for i, item in enumerate(items):
                for k in item:
                    if k not in it["fields"]:
                        errors.append(f"{rid}.items[{i}]: unknown field {k!r}; fields: {list(it['fields'])}")
                for f, spec in it["fields"].items():
                    _check_text(rid, f"{rid}.items[{i}].{f}", spec, item.get(f), errors)
    if r.get("special") == "process" and items and len(items) > 8:
        errors.append("process slides hold max 8 steps - split across two slides or use infographic.cycle")
    return errors
