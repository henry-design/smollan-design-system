"""Fill styled template tables: resize rows/columns by cloning, ticks, gantt."""
from __future__ import annotations

import copy

from lxml import etree
from pptx.oxml.ns import qn
from pptx.util import Inches

from .errors import SmollanError
from .text import _txbody, set_text


TICKS = ["", "✓", "✔", "", "●", "", ""]
CROSSES = ["", "✗", "✕", "×", ""]
_FILL_TAGS = ("noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill")


def _table_symbol(tbl, col, pool):
    """Find a symbol cell (tick / dot / cross) in a column; return a copy of its <a:r>."""
    for search_col in [col] + list(range(len(tbl.columns))):
        for row in tbl.rows:
            if search_col >= len(row.cells):
                continue
            cell = row.cells[search_col]
            t = cell.text.strip()
            if t and t in pool:
                r = cell._tc.find(".//" + qn("a:r"))
                if r is not None:
                    return copy.deepcopy(r)
    return None


def _has_merge(rows):
    for r in rows:
        for tc in r._tr.findall(qn("a:tc")):
            if tc.get("gridSpan") or tc.get("rowSpan") or tc.get("hMerge") or tc.get("vMerge"):
                return True
    return False


def _set_cell(cell, value, tick_run=None, cross_run=None):
    is_tick = value is True or (isinstance(value, str) and value.strip().lower() in ("tick", "yes", "✓"))
    is_cross = value is False or (isinstance(value, str) and value.strip().lower() in ("cross", "no", "✗"))
    if not (is_tick or is_cross):
        return set_text(cell, "" if value is None else (value if isinstance(value, list) else str(value)))
    run = tick_run if is_tick else cross_run
    if run is None:
        return set_text(cell, "✓" if is_tick else "")
    txbody = _txbody(cell)
    ps = txbody.findall(qn("a:p"))
    keep_ppr = ps[0].find(qn("a:pPr")) if ps else None
    for p in ps:
        txbody.remove(p)
    p = etree.SubElement(txbody, qn("a:p"))
    if keep_ppr is not None:
        p.append(copy.deepcopy(keep_ppr))
    p.append(copy.deepcopy(run))


def _set_tc_fill(cell, fill_el):
    """Set a table cell's fill (fill_el = <a:solidFill> etc., or None for no fill)."""
    tcpr = cell._tc.get_or_add_tcPr()
    for child in list(tcpr):
        if etree.QName(child).localname in _FILL_TAGS:
            tcpr.remove(child)
    new = copy.deepcopy(fill_el) if fill_el is not None else etree.Element(qn("a:noFill"))
    lns = [c for c in tcpr if etree.QName(c).localname.startswith("ln")]
    if lns:
        lns[-1].addnext(new)
    else:
        tcpr.insert(0, new)


def put_table(shape, spec, header_rows=1, footer_rows=0, fixed=False):
    """Fill a table slot.

    spec = {"header": [[...]] | [...], "rows": [[...], ...], "footer": [[...]]}
           or a plain list of rows (the first `header_rows` rows are the header).
    Cell values: str | list[str] (paragraphs) | True (tick/dot) | False (cross) | None.
    The table keeps its overall size; rows/columns are added by cloning template ones,
    so zebra striping, coloured row labels and symbols carry over.
    """
    if isinstance(spec, (list, tuple)):
        spec = {"header": list(spec[:header_rows]), "rows": list(spec[header_rows:])}
    header = spec.get("header") or []
    if header and not isinstance(header[0], (list, tuple)):
        header = [header]
    body = [list(r) for r in spec.get("rows", [])]
    footer = spec.get("footer") or []
    if footer and not isinstance(footer[0], (list, tuple)):
        footer = [footer]
    tbl = shape.table
    R, C = len(tbl.rows), len(tbl.columns)
    all_rows = header + body + footer
    if not all_rows:
        raise SmollanError("table needs at least one row")
    newC = max(len(r) for r in all_rows)
    tick_runs = [_table_symbol(tbl, c, TICKS) for c in range(C)]
    cross_runs = [_table_symbol(tbl, c, CROSSES) for c in range(C)]
    H, F = min(header_rows, R), min(footer_rows, max(R - header_rows, 0))
    if header and len(header) != H:
        raise SmollanError(f"this table preset has {H} header row(s); you passed {len(header)}")
    if footer and len(footer) != F:
        raise SmollanError(f"this table preset has {F} footer row(s); you passed {len(footer)}")
    n_body_tmpl = R - H - F
    if fixed and (newC != C or len(body) != n_body_tmpl):
        raise SmollanError(f"this table preset has a fixed structure: {n_body_tmpl} body rows x {C} columns "
                           f"(+{H} header, {F} footer rows). Pass exactly that, or use a 'tables.clean*' recipe.")
    # ---- columns
    if newC != C:
        if _has_merge(list(tbl.rows)):
            raise SmollanError(f"this table preset has merged cells, so its {C} columns are fixed. Pass {C} "
                               f"values per row, or use 'tables.clean' for free-form tables.")
        grid = tbl._tbl.tblGrid
        total_w = sum(int(g.get("w")) for g in grid.findall(qn("a:gridCol")))
        while len(grid.findall(qn("a:gridCol"))) < newC:
            grid.append(copy.deepcopy(grid.findall(qn("a:gridCol"))[-1]))
            for tr in tbl._tbl.findall(qn("a:tr")):
                tr.append(copy.deepcopy(tr.findall(qn("a:tc"))[-1]))
        while len(grid.findall(qn("a:gridCol"))) > newC:
            grid.remove(grid.findall(qn("a:gridCol"))[-1])
            for tr in tbl._tbl.findall(qn("a:tr")):
                tr.remove(tr.findall(qn("a:tc"))[-1])
        cols = grid.findall(qn("a:gridCol"))
        old = [int(g.get("w")) for g in cols]
        scale = total_w / sum(old)
        for g, w in zip(cols, old):
            g.set("w", str(int(w * scale)))
        tick_runs = (tick_runs + [tick_runs[-1]] * newC)[:newC]
        cross_runs = (cross_runs + [cross_runs[-1]] * newC)[:newC]
    # ---- body rows
    tr_els = tbl._tbl.findall(qn("a:tr"))
    body_els = tr_els[H:len(tr_els) - F]
    if len(body) != len(body_els):
        if body_els and _has_merge(list(tbl.rows)[H:R - F]):
            raise SmollanError(f"this table preset has merged body cells, so it holds exactly "
                               f"{len(body_els)} body rows.")
        tmpl_body = [copy.deepcopy(e) for e in (body_els or tr_els[-1:])]
        total_h = sum(int(e.get("h")) for e in body_els) or int(tr_els[-1].get("h"))
        anchor = tr_els[H - 1] if H else None
        for e in body_els:
            tbl._tbl.remove(e)
        new_h = max(int(total_h / max(len(body), 1)), int(Inches(0.22)))
        insert_after = anchor
        for i in range(len(body)):
            e = copy.deepcopy(tmpl_body[i % len(tmpl_body)])
            e.set("h", str(min(new_h, int(e.get("h")))))
            if insert_after is None:
                tbl._tbl.tblGrid.addnext(e)
            else:
                insert_after.addnext(e)
            insert_after = e
    # ---- write values
    rows = list(tbl.rows)
    data_rows = (header if header else [None] * H) + body + (footer if footer else [None] * F)
    for ri, row in enumerate(rows):
        if ri >= len(data_rows) or data_rows[ri] is None:
            continue
        vals = data_rows[ri]
        for ci, cell in enumerate(row.cells):
            if cell.is_spanned:
                continue
            v = vals[ci] if ci < len(vals) else ""
            _set_cell(cell, v, tick_runs[min(ci, len(tick_runs) - 1)], cross_runs[min(ci, len(cross_runs) - 1)])
    return shape


def put_gantt(shape, spec):
    """Gantt preset. spec = {"periods": ["1", "2", ...], "tasks": [{"label": "...", "start": 1, "end": 3}],
    "corner": "WEEK"}. start/end are 1-based period numbers (inclusive)."""
    periods, tasks = spec["periods"], spec["tasks"]
    tbl = shape.table

    def cell_fill(cell):
        return cell._tc.find(qn("a:tcPr") + "/" + qn("a:solidFill"))

    # The background is the most common cell fill; bar colours are the fills that differ from it.
    body = [c for row in list(tbl.rows)[1:] for c in list(row.cells)[1:]]
    keys = [etree.tostring(f) if (f := cell_fill(c)) is not None else b"" for c in body]
    background_key = max(set(keys), key=keys.count) if keys else b""
    background = next((copy.deepcopy(cell_fill(c)) for c, k in zip(body, keys) if k == background_key and k), None)
    bars = []
    for row in list(tbl.rows)[1:]:
        for cell in list(row.cells)[1:]:
            f = cell_fill(cell)
            if f is not None and etree.tostring(f) != background_key:
                bars.append(copy.deepcopy(f))
                break
    put_table(shape, {"header": [[spec.get("corner", "WEEK")] + list(periods)],
                      "rows": [[t["label"]] + [""] * len(periods) for t in tasks]})
    for ti, (t, row) in enumerate(zip(tasks, list(tbl.rows)[1:])):
        bar = bars[ti % len(bars)] if bars else None
        for pi, cell in enumerate(list(row.cells)[1:], start=1):
            in_task = bar is not None and t["start"] <= pi <= t["end"]
            _set_tc_fill(cell, bar if in_task else background)
    return shape
