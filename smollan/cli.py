"""Command-line interface, JSON deck builder and font installer."""
from __future__ import annotations

import json
import os
import re
import sys

from . import __version__
from .catalog import catalog, find, show
from .config import FONT_DIR, HERE
from .deck import Deck
from .errors import SmollanError
from .photos import assets
from .recipes import RECIPES


def build_from_spec(spec: dict | str, out: str | None = None, base_dir: str | None = None) -> list[str]:
    """Build a deck from a JSON-style spec (for agents that do not write Python).

    spec = {"deck": {"title": ..., "presenter": ..., "date": ..., "client": ..., "cover": ..., ...},
            "slides": [{"recipe": "stats.3", "heading": "...", "items": [...]}, ...],
            "output": "deck.pptx"}
    Photo values may be "asset:<photo name>" (library photo) or a path relative to base_dir.
    """
    if isinstance(spec, str):
        base_dir = base_dir or os.path.dirname(os.path.abspath(spec))
        with open(spec, encoding="utf-8") as f:
            spec = json.load(f)
    base_dir = base_dir or os.getcwd()

    def resolve_paths(v):
        if isinstance(v, str) and v.startswith("asset:"):
            return assets.photo(v[6:])
        if isinstance(v, str) and v.lower().endswith((".jpg", ".jpeg", ".png", ".mp4", ".gif", ".bmp"))                 and not os.path.isabs(v):
            return os.path.join(base_dir, v)
        if isinstance(v, dict):
            return {k: resolve_paths(x) for k, x in v.items()}
        if isinstance(v, list):
            return [resolve_paths(x) for x in v]
        return v

    deck = Deck(**resolve_paths(spec.get("deck", {})))
    for i, slide in enumerate(spec.get("slides", []), 1):
        slide = dict(slide)
        rid = slide.pop("recipe", None)
        if not rid:
            raise SmollanError(f"slides[{i - 1}] has no 'recipe'")
        try:
            deck.add(rid, **resolve_paths(slide))
        except SmollanError as e:
            raise SmollanError(f"slides[{i - 1}] ({rid}): {e}") from None
    out = out or spec.get("output") or "deck.pptx"
    if not os.path.isabs(out):
        out = os.path.join(base_dir, out)
    return deck.save(out)


def install_fonts() -> list[str]:
    """Install the bundled Montserrat fonts for the current user (Windows, macOS, Linux)."""
    import shutil
    fonts = sorted(f for f in os.listdir(FONT_DIR) if f.lower().endswith(".ttf"))
    if sys.platform.startswith("win"):
        dest = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
    elif sys.platform == "darwin":
        dest = os.path.expanduser("~/Library/Fonts")
    else:
        dest = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(dest, exist_ok=True)
    done = []
    for f in fonts:
        target = os.path.join(dest, f)
        shutil.copyfile(os.path.join(FONT_DIR, f), target)
        done.append(target)
        if sys.platform.startswith("win"):
            import winreg
            style = re.sub(r"([a-z])([A-Z])", r"\1 \2", f[len("Montserrat-"):-4])
            name = "Montserrat (TrueType)" if style == "Regular" else f"Montserrat {style} (TrueType)"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts",
                                0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, target)
    if sys.platform.startswith("linux") and shutil.which("fc-cache"):
        os.system("fc-cache -f >/dev/null 2>&1")
    return done


_CLI_HELP = """smollan - Smollan PowerPoint design system

usage: smollan <command> [args]

  list [category]          list recipe ids (optionally one category)
  show <id>                full spec of a recipe: slots, limits, items, example call
  find <words...>          rank recipes for a plain-English need
  build <spec.json> [out]  build a deck from a JSON spec (see AGENTS.md)
  photos [tag]             list the bundled stock photos
  install-fonts            install Montserrat for the current user
  catalog [dir]            write CATALOG.md + catalog.json
  path                     print the installed package folder (master, assets)
  version                  print the version

Python: from smollan import Deck, find, describe   (read AGENTS.md)"""


def main(argv=None):
    """Console entry point (`smollan ...` / `python -m smollan ...`)."""
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(_CLI_HELP)
        return 0
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "list":
            cat = rest[0] if rest else None
            for rid, r in RECIPES.items():
                if cat is None or r["category"] == cat:
                    print(f"{rid:<30} {r['title']}")
        elif cmd == "show":
            show(rest[0])
        elif cmd == "find":
            find(" ".join(rest))
        elif cmd == "build":
            issues = build_from_spec(rest[0], rest[1] if len(rest) > 1 else None)
            return 1 if issues else 0
        elif cmd == "photos":
            assets.photos(rest[0] if rest else None)
        elif cmd == "install-fonts":
            for p in install_fonts():
                print("installed", p)
        elif cmd == "catalog":
            catalog(out_dir=rest[0] if rest else None)
            print("wrote CATALOG.md and catalog.json")
        elif cmd == "path":
            print(HERE)
        elif cmd == "version":
            print(__version__)
        else:
            print(f"unknown command {cmd!r}\n\n{_CLI_HELP}")
            return 2
    except SmollanError as e:
        print(f"SmollanError: {e}", file=sys.stderr)
        return 1
    return 0
