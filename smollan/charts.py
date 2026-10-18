"""Native, editable charts in Smollan colours (incl. an emulated waterfall)."""
from __future__ import annotations

from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Pt

from .brand import Brand
from .errors import SmollanError
from .shapes import _remove_shape


CHART_TYPES = {
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "stacked_column": XL_CHART_TYPE.COLUMN_STACKED,
    "stacked_100": XL_CHART_TYPE.COLUMN_STACKED_100,
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "stacked_bar": XL_CHART_TYPE.BAR_STACKED,
    "stacked_bar_100": XL_CHART_TYPE.BAR_STACKED_100,
    "line": XL_CHART_TYPE.LINE_MARKERS,
    "line_plain": XL_CHART_TYPE.LINE,
    "pie": XL_CHART_TYPE.PIE,
    "doughnut": XL_CHART_TYPE.DOUGHNUT,
    "area": XL_CHART_TYPE.AREA,
    "stacked_area": XL_CHART_TYPE.AREA_STACKED,
    "waterfall": XL_CHART_TYPE.COLUMN_STACKED,   # emulated with an invisible base series
}
_FAMILY = {  # python-pptx chart_type names -> our type names
    "COLUMN_CLUSTERED": "column", "COLUMN_STACKED_100": "stacked_100", "COLUMN_STACKED": "stacked_column",
    "BAR_CLUSTERED": "bar", "BAR_STACKED_100": "stacked_bar_100", "BAR_STACKED": "stacked_bar",
    "LINE_MARKERS_STACKED": "line", "LINE_MARKERS": "line", "LINE": "line_plain", "PIE": "pie",
    "DOUGHNUT": "doughnut", "AREA_STACKED": "stacked_area", "AREA": "area",
}


def _chart_family(chart):
    try:
        name = str(chart.chart_type).split(" ")[0].split(".")[-1]
    except Exception:
        return None
    return _FAMILY.get(name)


def _waterfall_data(values, totals):
    base, up, down, tot = [], [], [], []
    running = 0
    for i, v in enumerate(values):
        if i in totals:
            t = running if v is None else v
            running = t
            base.append(0); up.append(0); down.append(0); tot.append(t)
        elif v >= 0:
            base.append(running); up.append(v); down.append(0); tot.append(0)
            running += v
        else:
            running += v
            base.append(running); up.append(0); down.append(-v); tot.append(0)
    return [("Base", base), ("Increase", up), ("Decrease", down), ("Total", tot)]


def _chart_data(spec):
    cats = spec.get("categories")
    series = spec.get("series")
    if not cats or not series:
        raise SmollanError('chart needs "categories" and "series", e.g. '
                           '{"type": "column", "categories": ["Q1", "Q2"], "series": {"2026": [1, 2]}}')
    if isinstance(series, (list, tuple)):
        series = {spec.get("series_name", "Series 1"): series}
    data = CategoryChartData(number_format=spec.get("number_format", "General"))
    data.categories = cats
    if spec.get("type") == "waterfall":
        vals = list(series.values())[0]
        totals = set(spec.get("totals", [len(vals) - 1]))
        for name, vals2 in _waterfall_data(vals, totals):
            data.add_series(name, vals2)
        return data
    for name, vals in series.items():
        if len(vals) != len(cats):
            raise SmollanError(f"chart series {name!r} has {len(vals)} values for {len(cats)} categories")
        data.add_series(name, vals)
    return data


def style_chart(chart, spec):
    """Apply Smollan styling to a newly created chart."""
    ctype = spec.get("type", "column")
    chart.font.size = Pt(10)
    chart.font.name = Brand.BODY_FONT
    chart.font.color.rgb = Brand.CHARCOAL
    plot = chart.plots[0]
    multi = len(list(plot.series)) > 1 or ctype in ("pie", "doughnut")
    chart.has_legend = multi and ctype != "waterfall"
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    if ctype in ("pie", "doughnut"):
        for i, pt in enumerate(plot.series[0].points):
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = Brand.SERIES[i % len(Brand.SERIES)]
    else:
        colors = Brand.SERIES
        if ctype == "waterfall":
            colors = [None, Brand.GREEN, Brand.BRIGHT_CYAN, Brand.BLUE]
            plot.gap_width = 60
            plot.overlap = 100
        for i, s in enumerate(plot.series):
            col = colors[i % len(colors)]
            fmt = s.format
            if col is None:
                fmt.fill.background()
                fmt.line.fill.background()
                continue
            if ctype.startswith("line"):
                fmt.line.color.rgb = col
                fmt.line.width = Pt(2.25)
                s.smooth = False
            else:
                fmt.fill.solid()
                fmt.fill.fore_color.rgb = col
        try:
            va = chart.value_axis
            va.has_major_gridlines = True
            va.major_gridlines.format.line.color.rgb = Brand.PALE
            va.format.line.fill.background()
            chart.category_axis.format.line.color.rgb = Brand.GREY_BLUE
        except Exception:
            pass
    if ctype == "waterfall":
        fmt = spec.get("number_format", "#,##0")
        for i, s in enumerate(plot.series):
            if i == 0:
                continue                        # invisible base series: no labels
            dl = s.data_labels
            dl.show_value = True
            dl.font.size = Pt(9)
            dl.number_format = f"{fmt};-{fmt};;"  # hide zero labels
            dl.number_format_is_linked = False
            dl.font.color.rgb = Brand.WHITE if i == 3 else Brand.NEAR_BLACK
    elif spec.get("labels") or ctype in ("pie", "doughnut"):
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.font.size = Pt(9)
        dl.number_format = spec.get("number_format", "General")
        dl.number_format_is_linked = False
    if spec.get("title"):
        chart.has_title = True
        chart.chart_title.text_frame.text = spec["title"]
        f = chart.chart_title.text_frame.paragraphs[0].runs[0].font
        f.size, f.bold = Pt(12), True
    else:
        chart.has_title = False


def put_chart(slide, shape, spec):
    """Fill a chart slot. Re-uses the template chart (and its styling) when the type matches."""
    if not isinstance(spec, dict):
        raise SmollanError("chart slot expects a dict spec")
    data = _chart_data(spec)
    want = spec.get("type")
    existing = shape.chart if getattr(shape, "has_chart", False) and shape.has_chart else None
    if existing is not None and (want is None or want == _chart_family(existing)):
        existing.replace_data(data)
        if spec.get("title") and existing.has_title:
            existing.chart_title.text_frame.text = spec["title"]
        return shape
    xl = CHART_TYPES.get(want or "column")
    if xl is None:
        raise SmollanError(f"unknown chart type {want!r}; use one of {sorted(CHART_TYPES)}")
    if shape.is_placeholder and hasattr(shape, "insert_chart") and existing is None:
        frame = shape.insert_chart(xl, data)
    else:
        x, y, w, h = shape.left, shape.top, shape.width, shape.height
        _remove_shape(shape)
        frame = slide.shapes.add_chart(xl, x, y, w, h, data)
    style_chart(frame.chart, {**spec, "type": want or "column"})
    return frame
