"""Opt-in stock photo library bundled with the package."""
from __future__ import annotations

import json
import os

from .config import PHOTO_DIR
from .errors import SmollanError


class _Assets:
    """assets.photo('name') -> path;  assets.photos('retail') -> [(name, description)]"""

    def _index(self):
        p = os.path.join(PHOTO_DIR, "index.json")
        if not os.path.exists(p):
            return {}
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def photo(self, name: str) -> str:
        idx = self._index()
        if name not in idx:
            raise SmollanError(f"no photo {name!r}; see assets.photos()")
        return os.path.join(PHOTO_DIR, idx[name]["file"])

    def photos(self, tag: str | None = None, show: bool = True):
        out = [(k, v["description"]) for k, v in self._index().items()
               if tag is None or tag.lower() in (v["description"] + " " + " ".join(v.get("tags", []))).lower()]
        if show:
            for k, d in out:
                print(f"{k:<28} {d}")
        return out


assets = _Assets()
