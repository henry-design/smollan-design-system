"""Brand tokens: colours, fonts, geometry, preflight patterns."""
from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.util import Inches


class Brand:
    """Smollan brand tokens. Use these instead of hard-coded values."""

    # -- colours (theme1.xml of the Core Template) ---------------------------
    DARK_BLUE = RGBColor(0x00, 0x28, 0x4E)   # primary brand, covers, headings
    BLUE = RGBColor(0x00, 0x50, 0x83)        # primary accent, table headers
    CYAN_BLUE = RGBColor(0x00, 0x79, 0xC0)   # accent 1, 2nd chart series
    BRIGHT_CYAN = RGBColor(0x00, 0xBB, 0xF0) # links, tertiary accent
    MID_BLUE = RGBColor(0x54, 0x9A, 0xD3)    # soft callouts, 4th series
    CHARCOAL = RGBColor(0x37, 0x46, 0x5B)    # third cover tone, body emphasis
    NEAR_BLACK = RGBColor(0x0E, 0x1D, 0x29)  # dark backgrounds
    GREEN = RGBColor(0x16, 0xB7, 0x95)       # FOCAL colour - one per slide
    LIME = RGBColor(0x8A, 0xC5, 0x46)        # positive deltas, callouts
    PALE = RGBColor(0xEF, 0xF2, 0xF6)        # section backgrounds, zebra rows
    GREY_BLUE = RGBColor(0xB4, 0xC3, 0xCE)   # dividers, low emphasis
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)

    # Order used for chart series / repeated items (matches the packs' charts).
    SERIES = [BLUE, GREEN, CYAN_BLUE, BRIGHT_CYAN, CHARCOAL, LIME, MID_BLUE, DARK_BLUE]

    HEADING_FONT = "Montserrat"
    BODY_FONT = "Calibri"

    SLIDE_W = Inches(13.333)
    SLIDE_H = Inches(7.5)
    MARGIN = Inches(0.64)        # the packs' left/right content margin
    CONTENT_TOP = Inches(1.55)   # below a one-line heading + sub-heading
    CONTENT_BOTTOM = Inches(6.95)  # above the footer strip

    # Text the preflight check treats as "template text left behind".
    LEFTOVER_PATTERNS = [
        r"\[client", r"click to (edit|add|insert)", r"insert (your|intro|desc)",
        r"your (slide )?heading", r"heading goes here", r"sub-heading (goes )?here",
        r"\bxx\b", r"xxxx", r"lorem", r"�", r"edit tables in master",
        r"type bullet", r"add your", r"text goes here", r"name surname",
        r"title or designation",
    ]
