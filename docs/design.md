# Smollan Design System - design record (2026-10-18)

## Goal
A single script that acts as the master Smollan template: every slide design, style and asset from
the 16 PPT packs is available in code, so an agent that has decided what to present can pick the
matching slide and produce an on-brand, editable deck. Every option needs a summary and a detailed
description so agents can choose well.

## Decisions (agreed with the user)
| Topic | Decision |
|---|---|
| Fidelity | **Hybrid**: one merged `smollan_master.pptx` (all layouts + one template slide per recipe) + a code registry that fills it. Pixel-identical to the packs. |
| Language / interface | Python, `python-pptx`, **Python API** (`Deck().add(id, **slots)`) |
| Scope | All reusable layouts (Core + packs 1-14), Growth Teams tables merged into `tables.*`, bespoke org charts, example content as presets, opt-in photo library |
| Org charts | SmartArt can't be generated, so charts are **drawn from tree data**; bespoke charts are filled box by box |
| Fixed layout content | **Made editable**: tables, charts and wording baked into layouts are moved onto the template slides |
| Charts | Native, editable charts; template chart styling is reused when the type matches |
| Catalog | Docstrings + `CATALOG.md` + thumbnails + `catalog.json` |
| Rule breaks | **Error + suggestion** (`SmollanError`) |
| Missing photos | Empty picture slot, reported (library is opt-in via `assets.photo`) |
| Extras | Preflight check on save; auto cover + closing |
| Packaging | Single `smollan.py` with sidecar master/assets; friendly ids + original layout names as aliases |

## Architecture
- `tools/build_master.py`: merges all layouts into the Core master (the masters are identical across packs),
  de-duplicating by content. It copies each example slide as a named template slide, moves layout-baked
  content onto the slides, and strips designer sticky notes into usage notes.
- `tools/analyze_slots.py`: infers slots: role from the prompt text, limits from box geometry and the
  "no longer than N lines" instructions, and repeated blocks grouped into items in reading order.
- `tools/curation.py`: the hand-written ids, titles, summaries, use/avoid guidance and slot overrides.
- `tools/gen_registry.py`: merges the two and writes the `RECIPES` block and the summary index into `smollan.py`.
- `smollan.py`: when you add a slide, it copies the template slide (with its own charts and images),
  fills each slot while keeping the template formatting, removes unused slots, and swaps in the
  `[Client]` name. On save it removes the template slides and unused layouts, then runs the preflight check.

## Verification
`tools/selftest.py` builds all 190 recipes with sample content: 0 failures, preflight clean. The deck
opens in PowerPoint 2024 without repair and every slide was rendered and checked by eye. The worked
example in `examples/demo.py` builds cleanly and triggers the 9-step guard-rail as intended.
