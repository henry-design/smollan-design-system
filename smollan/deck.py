"""Deck - the main API: add recipe slides, save with closing slide and preflight."""
from __future__ import annotations

import os
import re

from pptx import Presentation
from pptx.oxml.ns import qn

from ._opc import (PartCopier, _add_slide_part, _dedupe_partnames, _remove_slide, _renumber_shape_ids,
                   _strip_unused_rels)
from .brand import Brand
from .catalog import resolve
from .charts import put_chart
from .config import MASTER_PATH
from .errors import SmollanError
from .orgchart import draw_org_chart
from .recipes import RECIPES
from .shapes import (_find_shape, _iter_shapes, _purge_alternate_content, _remove_shape, put_logo,
                     put_photo, put_video)
from .tables import put_gantt, put_table
from .text import set_text
from .validation import validate


class Deck:
    """Build a Smollan deck.

    Deck(title=..., presenter=..., date=..., subtitle=..., client=..., logo=...,
         cover="cover.dark_blue", closing="closing", auto_cover=True, auto_closing=True)
      .add(recipe_id, **slots)   -> adds one slide (see describe(recipe_id) for slots)
      .save(path)                -> adds the closing slide, removes unused layouts, runs preflight
    """

    def __init__(self, title: str | None = None, presenter: str | None = None, date: str | None = None,
                 subtitle: str | None = None, client: str | None = None, cover: str = "cover.dark_blue",
                 closing: str = "closing", auto_cover: bool = True, auto_closing: bool = True,
                 logo: str | None = None, master: str = MASTER_PATH):
        if not os.path.exists(master):
            raise SmollanError(f"{master} not found - run tools/build_master.py first")
        self.prs = Presentation(master)
        self._templates = {s._element.cSld.get("name"): s for s in self.prs.slides}
        self._n_templates = len(self.prs.slides)
        self._copier = PartCopier(self.prs.part.package)
        self.client = client
        self.logo = logo            # client logo: used on every slide that has a 'logo' slot
        self.closing = closing
        self.auto_closing = auto_closing
        self.recipes_used: list[str] = []
        self.log: list[str] = []
        self._saved = False
        if auto_cover:
            self.add_cover(cover, title=title, subtitle=subtitle, presenter=presenter, date=date)

    # -- covers / closing ----------------------------------------------------
    def add_cover(self, recipe="cover.dark_blue", title=None, subtitle=None, presenter=None, date=None, **extra):
        rid = resolve(recipe)
        slots = RECIPES[rid]["slots"]
        offered = {"heading": title, "subheading": subtitle, "presenter": presenter, "date": date, **extra}
        return self.add(rid, **{k: v for k, v in offered.items() if k in slots and v is not None})

    # -- core ------------------------------------------------------------------
    def add(self, recipe: str, **content):
        """Add one slide from a recipe. Raises SmollanError (with a fix) if content breaks a rule."""
        if self._saved:
            raise SmollanError("deck already saved - create a new Deck")
        rid = resolve(recipe)
        r = RECIPES[rid]
        if self.logo and "logo" in r["slots"] and "logo" not in content:
            content["logo"] = self.logo
        errors = validate(rid, content)
        if errors:
            raise SmollanError("; ".join(errors))
        tmpl = self._templates[r["src"]]
        self._copier.memo = {}
        part = self._copier.copy(tmpl.part, redirect={id(tmpl.slide_layout.part): tmpl.slide_layout.part})
        _add_slide_part(self.prs, part)
        slide = self.prs.slides[-1]
        try:
            slide._element.cSld.set("name", rid)
            n_slide = len(self.prs.slides) - self._n_templates
            filled, empty_photos = set(), []
            for name, spec in r["slots"].items():
                val = content.get(name)
                if val is not None and val != "":
                    self._fill(slide, spec, spec["ref"], val, rid)
                    filled.add(spec["ref"])
                elif spec["kind"] == "photo":
                    empty_photos.append(spec["ref"])
                elif spec.get("keep"):
                    if spec.get("default"):          # Smollan's standard wording
                        self._fill(slide, spec, spec["ref"], spec["default"], rid)
                    filled.add(spec["ref"])
            it = r.get("items")
            items = content.get("items") or []
            drop_refs = set()
            if it:
                keep_defaults = not items and it.get("keep_default")
                for f, spec in it["fields"].items():
                    for i, ref in enumerate(spec["refs"]):
                        if ref is None:
                            continue
                        val = items[i].get(f) if i < len(items) else None
                        if val is not None and val != "":
                            self._fill(slide, spec, ref, val, rid)
                            filled.add(ref)
                        elif spec["kind"] == "photo":
                            empty_photos.append(ref)
                        elif keep_defaults:
                            filled.add(ref)
                        elif i >= len(items):
                            drop_refs.add(ref)
            for ref in self._all_refs(r) - filled:
                if ref in empty_photos and ref not in drop_refs:
                    self._reset_photo(slide, ref)
                    self.log.append(f"slide {n_slide} ({rid}): photo slot {ref} left empty")
                    continue
                self._clear(slide, ref)
            for ref in drop_refs | set(r.get("remove", [])):
                self._clear(slide, ref)
            if self.client:
                _replace_client(slide, self.client)
            _renumber_shape_ids(slide._element.cSld.spTree)
            _strip_unused_rels(slide.part, slide._element)
        except Exception:
            _remove_slide(self.prs, slide)      # never leave a half-built slide in the deck
            raise
        self.recipes_used.append(rid)
        return slide

    @staticmethod
    def _all_refs(r):
        refs = {s["ref"] for s in r["slots"].values()}
        if r.get("items"):
            for s in r["items"]["fields"].values():
                refs |= {x for x in s["refs"] if x}
        return refs

    def _clear(self, slide, ref):
        if ref.startswith("ph:"):
            _purge_alternate_content(slide, int(ref[3:]))
        if ref.startswith("cell:"):
            cell = _find_shape(slide, ref)
            if cell is not None:
                set_text(cell, "")
            return
        kind, _, rest = ref.partition(":")
        for sh in list(_iter_shapes(slide.shapes)):
            if (kind == "ph" and sh.is_placeholder and sh.placeholder_format.idx == int(rest)) or \
                    (kind == "id" and sh.shape_id == int(rest)):
                _remove_shape(sh)
                return

    def _reset_photo(self, slide, ref):
        """Turn a template photo into an empty picture placeholder."""
        sh = _find_shape(slide, ref)
        if sh is None:
            return None
        if sh.is_placeholder and sh._element.tag == qn("p:pic"):
            _remove_shape(sh)
            sh = _find_shape(slide, ref)       # re-cloned (empty) from the layout
        elif not sh.is_placeholder and sh.shape_type == 13:
            pass
        return sh

    def _fill(self, slide, spec, ref, value, rid):
        kind = spec["kind"]
        if kind == "photo":
            sh = self._reset_photo(slide, ref)
            if sh is None:
                raise SmollanError(f"{rid}: photo slot {ref} not found")
            put_photo(slide, sh, value)
            return
        target = _find_shape(slide, ref)
        if target is None:
            raise SmollanError(f"{rid}: slot {ref} not found on template (rebuild the master?)")
        if kind == "text":
            set_text(target, value)
        elif kind == "chart":
            put_chart(slide, target, value)
        elif kind == "table":
            opts = spec.get("table", {})
            put_table(target, value, opts.get("header_rows", 1), opts.get("footer_rows", 0), opts.get("fixed", False))
        elif kind == "gantt":
            put_gantt(target, value)
        elif kind == "org":
            x, y, w, h = target.left, target.top, target.width, target.height
            _remove_shape(target)
            draw_org_chart(slide, x, y, w, h, value)
        elif kind == "logo":
            put_logo(slide, target, value)
        elif kind == "video":
            put_video(slide, target, value)
        else:
            raise SmollanError(f"unknown slot kind {kind}")

    # -- output ----------------------------------------------------------------
    def save(self, path: str, preflight: bool = True) -> list[str]:
        if self._saved:
            raise SmollanError("deck already saved")
        last_cat = RECIPES[self.recipes_used[-1]]["category"] if self.recipes_used else None
        if self.auto_closing and last_cat not in ("closing", "thankyou"):
            self.add(self.closing)
        for s in list(self.prs.slides)[:self._n_templates]:
            _remove_slide(self.prs, s)
        used = {id(s.slide_layout.part) for s in self.prs.slides}
        layouts = self.prs.slide_masters[0].slide_layouts
        for lay in list(layouts):
            if id(lay.part) not in used:
                layouts.remove(lay)
        _dedupe_partnames(self.prs.part.package)
        self.prs.save(path)
        self._saved = True
        issues = preflight_check(self.prs) + self.log if preflight else []
        if preflight:
            print(f"saved {path}: {len(self.prs.slides)} slides; preflight: "
                  f"{'clean' if not issues else str(len(issues)) + ' issue(s)'}")
            for i in issues:
                print("  -", i)
        return issues


def _replace_client(slide, client):
    """Swap '[Client]' / '[CLIENT]' / '[Client X]' tokens for the client name, keeping formatting."""
    rx = re.compile(r"\[client(?: x)?\]", re.I)
    for sh in _iter_shapes(slide.shapes):
        frames = []
        if sh.has_text_frame:
            frames.append(sh.text_frame)
        if getattr(sh, "has_table", False) and sh.has_table:
            frames += [c.text_frame for row in sh.table.rows for c in row.cells]
        for tf in frames:
            for t in tf._txBody.iter(qn("a:t")):
                if t.text and rx.search(t.text):
                    t.text = rx.sub(lambda m: client.upper() if m.group(0).isupper() else client, t.text)


def preflight_check(prs) -> list[str]:
    """Find template text left behind, mojibake and empty placeholders."""
    pat = re.compile("|".join(Brand.LEFTOVER_PATTERNS), re.I)
    issues = []
    for n, s in enumerate(prs.slides, 1):
        rid = s._element.cSld.get("name") or "?"
        for sh in _iter_shapes(s.shapes):
            texts = []
            if sh.has_text_frame:
                texts.append(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                texts += [c.text for row in sh.table.rows for c in row.cells]
            for t in texts:
                m = pat.search(t or "")
                if m:
                    issues.append(f"slide {n} ({rid}): leftover template text {t.strip()[:60]!r}")
    return issues
