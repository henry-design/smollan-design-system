"""Package paths (data ships inside the installed package)."""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))            # installed package folder (holds the data)
MASTER_PATH = os.path.join(HERE, "smollan_master.pptx")
PHOTO_DIR = os.path.join(HERE, "assets", "photos")
FONT_DIR = os.path.join(HERE, "assets", "fonts")
_PARENT = os.path.dirname(HERE)
REPO_ROOT = _PARENT if os.path.isdir(os.path.join(_PARENT, "tools")) else None   # source checkout only
