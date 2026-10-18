"""Text filling that keeps the template's own fonts, sizes, colours and bullets."""
from __future__ import annotations

import copy
import re

from lxml import etree
from pptx.oxml.ns import qn


def _txbody(obj):
    if hasattr(obj, "_tc"):                      # table cell
        return obj._tc.get_or_add_txBody()
    return obj.text_frame._txBody


def _as_rpr(el):
    if el is None:
        return None
    rpr = etree.Element(qn("a:rPr"))
    for k, v in el.attrib.items():
        rpr.set(k, v)
    for c in el:
        rpr.append(copy.deepcopy(c))
    return rpr


def _para_models(txbody):
    models = []
    for p in txbody.findall(qn("a:p")):
        pPr = p.find(qn("a:pPr"))
        r = p.find(qn("a:r"))
        rpr = r.find(qn("a:rPr")) if r is not None else None
        if rpr is None:
            rpr = _as_rpr(p.find(qn("a:endParaRPr")))
        has_text = r is not None and bool("".join(t.text or "" for t in p.iter(qn("a:t"))).strip())
        models.append((pPr, rpr, has_text))
    with_text = [m for m in models if m[2]]
    return [(m[0], m[1]) for m in (with_text or models)] or [(None, None)]


def _normalize_paragraphs(value) -> list[tuple[int, str]]:
    """str -> one paragraph; list -> one paragraph per item ('- ' prefix = level 1)."""
    if value is None:
        return []
    items = value if isinstance(value, (list, tuple)) else [value]
    out = []
    for it in items:
        it = str(it)
        lvl = 0
        while it.startswith("- "):
            lvl += 1
            it = it[2:]
        out.append((lvl, it))
    return out


def _segments(text):
    """Split a paragraph into runs: '**bold**' segments and '\\n' line breaks."""
    out = []
    for li, line in enumerate(text.split("\n")):
        if li:
            out.append(("", False, True))
        for part in re.split(r"(\*\*.+?\*\*)", line):
            if not part:
                continue
            if part.startswith("**") and part.endswith("**"):
                out.append((part[2:-2], True, False))
            else:
                out.append((part, False, False))
    return out or [("", False, False)]


def set_text(target, value):
    """Replace the text of a shape / placeholder / table cell, keeping template formatting.

    value: str (use '\\n' for a line break, '**bold**' for emphasis) or list[str]
    for several paragraphs/bullets ('- ' prefix indents one level).
    """
    txbody = _txbody(target)
    models = _para_models(txbody)
    by_level = {}
    for pPr, rpr in models:
        lvl = int(pPr.get("lvl", "0")) if pPr is not None else 0
        by_level.setdefault(lvl, (pPr, rpr))
    for p in txbody.findall(qn("a:p")):
        txbody.remove(p)
    paras = _normalize_paragraphs(value) or [(0, "")]
    for i, (lvl, text) in enumerate(paras):
        pPr, rpr = by_level.get(lvl) or models[min(i, len(models) - 1)]
        p = etree.SubElement(txbody, qn("a:p"))
        if pPr is not None:
            np_ = copy.deepcopy(pPr)
            if lvl:
                np_.set("lvl", str(lvl))
            p.append(np_)
        elif lvl:
            etree.SubElement(p, qn("a:pPr")).set("lvl", str(lvl))
        for seg, bold, is_break in _segments(text):
            if is_break:
                br = etree.SubElement(p, qn("a:br"))
                if rpr is not None:
                    br.append(copy.deepcopy(rpr))
                continue
            r = etree.SubElement(p, qn("a:r"))
            rp = copy.deepcopy(rpr) if rpr is not None else etree.Element(qn("a:rPr"))
            rp.set("lang", rp.get("lang", "en-GB"))
            if bold:
                rp.set("b", "1")
            r.append(rp)
            etree.SubElement(r, qn("a:t")).text = seg


def _plain(value) -> list[str]:
    return [t for _, t in _normalize_paragraphs(value)]
