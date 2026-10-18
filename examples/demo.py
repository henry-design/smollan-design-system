"""
Worked example: a realistic Smollan client review deck, built the way an agent should.

    python examples/demo.py            -> examples/demo_client_review.pptx

1. Decide the story (sections + one message per slide).
2. For each message pick a recipe: find("..."), then describe("<id>") for its slots.
3. deck.add("<id>", **slots) - SmollanError tells you exactly what to change.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from smollan import Deck, SmollanError, assets  # noqa: E402

deck = Deck(title="Q3 BUSINESS REVIEW\nACME FOODS", presenter="Jane Doe, Client Lead", date="OCTOBER 2026",
            client="Acme Foods", cover="cover.dark_blue")

deck.add("title.one_line_sub", heading="AGENDA", subheading="What we will cover today",
         body=["Q3 performance highlights", "How we delivered: our execution model",
               "Your team", "What we will measure in Q4", "Next steps"])

deck.add("divider.dark_blue", heading="Q3 PERFORMANCE", section="SECTION 01")

deck.add("stats.3", heading="Q3 RESULTS AT A GLANCE", subheading="Across 1,240 stores in modern and traditional trade",
         items=[{"label": "AVAILABILITY", "value": "96%", "text": "On-shelf availability, up 4 points on Q2.",
                 "note": "Source: Smollan store audits, Jul-Sep"},
                {"label": "SHARE OF SHELF", "value": "31%", "text": "Share of shelf in core categories.",
                 "note": "Target 30%"},
                {"label": "COMPLIANCE", "value": "92%", "text": "Planogram compliance across key accounts.",
                 "note": "Up from 85% in Q1"}])

deck.add("graphs.1_sub", heading="SELL-OUT GROWTH BY MONTH", subheading="VALUE SALES, R MILLION",
         chart={"categories": ["Jul", "Aug", "Sep"], "series": {"2025": [41.2, 43.0, 44.1], "2026": [45.8, 48.3, 50.6]}})

deck.add("tables.clean", heading="PERFORMANCE BY KEY ACCOUNT", intro="Q3 actuals vs. target",
         table={"header": ["ACCOUNT", "OSA", "SHARE OF SHELF", "COMPLIANCE", "PROMO EXECUTION"],
                "rows": [["Retailer A", "97%", "33%", "94%", True],
                         ["Retailer B", "95%", "30%", "91%", True],
                         ["Retailer C", "94%", "29%", "90%", False],
                         ["Retailer D", "96%", "32%", "93%", True]]})

deck.add("divider.dark_blue", heading="HOW WE DELIVERED", section="SECTION 02")

deck.add("process.5", heading="OUR EXECUTION MODEL", subheading="FROM INSIGHT TO SHELF",
         intro="A weekly rhythm that turns store data into action within 48 hours.",
         items=[{"heading": "PLAN", "bullets": ["Route plans", "Store priorities"], "detail": "Every Monday"},
                {"heading": "EXECUTE", "bullets": ["Merchandising", "Promo set-up"], "detail": "Daily"},
                {"heading": "MEASURE", "bullets": ["Photo audits", "OSA checks"], "detail": "Each visit"},
                {"heading": "ANALYSE", "bullets": ["Dashboards", "Exception alerts"], "detail": "Within 24h"},
                {"heading": "ACT", "bullets": ["Fix gaps", "Share wins"], "detail": "Within 48h"}])

deck.add("stats.1_photo", heading="ONE NUMBER THAT MATTERS", subheading="Out-of-stocks resolved within 48 hours",
         value="89%", label="RESOLVED IN 48H", text="Exception alerts route straight to the field team on the day.",
         note="Q3 2026, all regions", photo=assets.photo("merchandiser_snacks_aisle"))

deck.add("org.tree", heading="YOUR ACME FOODS TEAM",
         tree={"name": "Jane Doe", "role": "Client Lead", "children": [
             {"name": "Sipho Dlamini", "role": "Field Manager - Inland",
              "children": [{"name": "Ann Lee", "role": "Team Leader"}, {"name": "Raj Patel", "role": "Team Leader"}]},
             {"name": "Maria Silva", "role": "Field Manager - Coastal",
              "children": [{"name": "Tom Berg", "role": "Team Leader"}, {"name": "Lea Roux", "role": "Team Leader"}]},
             {"name": "Ken Otieno", "role": "Insights Lead", "children": [{"name": "Ola Ade", "role": "Analyst"}]}]})

deck.add("kpis.5", heading="Q4 KPIs", intro="Co-created with [Client], reviewed monthly.",
         items=[{"label": "OSA", "text": "On-shelf availability at or above 96% in all key accounts"},
                {"label": "SHARE OF SHELF", "text": "Maintain 31%+ share of shelf in core categories"},
                {"label": "COMPLIANCE", "text": "Planogram compliance of 93% or higher"},
                {"label": "PROMO", "text": "100% of promotions live on day one"},
                {"label": "RESPONSE", "text": "Out-of-stocks resolved within 48 hours"}])

deck.add("why.pillars", subheading="WINNING AT THE POINT OF PURCHASE")   # default Smollan pillars kept

# Guard-rails in action: 9 steps is more than any process slide holds.
try:
    deck.add("process.8", items=[{"heading": f"STEP {i}"} for i in range(1, 10)])
except SmollanError as e:
    print("Expected guard-rail:", str(e)[:140], "...")

deck.add("thankyou.c", subheading="NEXT STEPS",
         message="Thank you for a strong quarter together. We look forward to an even better Q4.",
         body=["Agree Q4 KPI targets by 31 October", "Monthly performance reviews", "Q4 review in January"])

deck.save(os.path.join(HERE, "demo_client_review.pptx"))
