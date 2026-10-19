"""
Stress test for pie and doughnut charts (template charts and newly created ones).

    python tools/test_pie_doughnut.py [out.pptx]

Each slide's heading says what it tests. Render with tools/render.ps1 and check that:
every slice has a distinct Smollan colour, labels are readable, legends list every category,
titles are right, and nothing is clipped.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from smollan import Deck, SmollanError  # noqa: E402

CATS = ["Modern trade", "Traditional", "Wholesale", "E-commerce", "Pharmacy", "Forecourt", "Liquor", "Other"]
VALS = [34, 22, 15, 11, 8, 5, 3, 2]


def pie(n, **extra):
    return {"categories": CATS[:n], "series": {"Share": VALS[:n]}, **extra}


CASES = [
    # (recipe, heading, slots)
    ("graphs.2_intro", "TEMPLATE PIES: 4 VS 4 SLICES", dict(chart=pie(4), chart_2=pie(4))),
    ("graphs.2_intro", "TEMPLATE PIES: 3 VS 6 SLICES", dict(chart=pie(3), chart_2=pie(6))),
    ("graphs.2_intro", "TEMPLATE PIES: 8 SLICES + TITLES", dict(chart=pie(8, title="Channel mix 2025"),
                                                              chart_2=pie(8, title="Channel mix 2026"))),
    ("graphs.2_intro", "TEMPLATE PIES: 2 SLICES, ZERO VALUE", dict(chart={"categories": ["Yes", "No", "Unsure"],
                                                                         "series": {"Answer": [70, 30, 0]}},
                                                                  chart_2=pie(2))),
    ("graphs.text_left", "TEMPLATE DOUGHNUT: 2 SLICES", dict(chart=pie(2))),
    ("graphs.text_left", "TEMPLATE DOUGHNUT: 7 SLICES", dict(chart=pie(7))),
    ("graphs.text_left", "TEMPLATE DOUGHNUT: 2 SERIES (RINGS)", dict(chart={"categories": CATS[:4],
                                                                           "series": {"2025": VALS[:4], "2026": [30, 25, 20, 25]}})),
    ("graphs.2_desc", "TEMPLATE DOUGHNUT IN CARD: 5 SLICES", dict(items=[
        {"chart": {"categories": ["Q1", "Q2", "Q3", "Q4"], "series": {"Sales": [4, 5, 6, 7]}}, "heading": "AREA", "text": "Left card"},
        {"chart": pie(5), "heading": "CHANNEL MIX", "text": "Five slices in the doughnut card"}])),
    ("stats.2_doughnut", "STATS DOUGHNUT 70 / 30", dict(chart={"categories": ["Modern", "Traditional"], "series": {"Split": [70, 30]}},
                                                         chart_value_1="70%", chart_value_2="30%",
                                                         items=[{"value": "70%", "text": "Modern trade"}, {"value": "30%", "text": "Traditional"}])),
    ("stats.2_doughnut", "STATS DOUGHNUT 3 SLICES", dict(chart={"categories": ["A", "B", "C"], "series": {"Split": [55, 25, 20]}},
                                                          chart_value_1="55%", chart_value_2="45%",
                                                          items=[{"value": "55%", "text": "A"}, {"value": "45%", "text": "B + C"}])),
    ("graphs.1", "NEW PIE ON A COLUMN TEMPLATE: 5 SLICES", dict(chart=pie(5, type="pie"))),
    ("graphs.1_sub", "NEW DOUGHNUT, PERCENT FORMAT", dict(subheading="VALUES 0-1 SHOWN AS %",
                                                         chart={"type": "doughnut", "categories": CATS[:4],
                                                                "series": {"Share": [0.45, 0.30, 0.15, 0.10]},
                                                                "number_format": "0%", "title": "Share of sales"})),
    ("graphs.1_sub", "NEW PIE, 8 SLICES, LONG LABELS", dict(subheading="LEGEND + LABEL CHECK",
                                                            chart={"type": "pie", "categories": [c + " channel total" for c in CATS],
                                                                   "series": {"Share": VALS}})),
    ("graphs.text_left", "TEMPLATE DOUGHNUT RETYPED TO PIE", dict(chart=pie(4, type="pie"))),
    ("graphs.text_left", "TEMPLATE DOUGHNUT, PERCENT LABELS", dict(chart=pie(6, labels="percent"))),
    ("graphs.1", "NEW PIE, PERCENT LABELS, 2 SLICES", dict(chart={"type": "pie", "categories": ["Yes", "No"],
                                                                "series": {"Answer": [62, 38]}, "labels": "percent"})),
]

# Content that must be refused (and must not leave a half-built slide behind).
BAD = [
    ("graphs.2_intro", dict(chart=pie(4), chart_2={"categories": [f"C{i}" for i in range(9)],
                                                   "series": {"S": list(range(1, 10))}}), "max 8 slices"),
    ("graphs.2_intro", dict(chart={"categories": ["A", "B"], "series": {"x": [1, 2], "y": [3, 4]}}), "one series"),
    ("graphs.text_left", dict(chart={"categories": ["A", "B"], "series": {"x": [5, -2]}}), "cannot be negative"),
    ("graphs.1", dict(chart={"type": "doughnut", "categories": ["A", "B"], "series": {"x": [0, 0]}}), "all zero"),
]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "examples", "test_pie_doughnut.pptx")
    d = Deck(title="PIE AND DOUGHNUT TEST", auto_closing=False)
    for rid, heading, slots in CASES:
        d.add(rid, heading=heading, **slots)
    for rid, slots, expect in BAD:
        before = len(d.prs.slides)
        try:
            d.add(rid, heading="SHOULD FAIL", **slots)
            raise SystemExit(f"FAIL: {rid} accepted bad data ({expect})")
        except SmollanError as e:
            assert expect in str(e), (expect, str(e))
            assert len(d.prs.slides) == before, "half-built slide left behind"
            print(f"refused as expected: {e}")
    d.save(out)


if __name__ == "__main__":
    main()
