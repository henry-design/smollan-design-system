"""
Extract the stock photos used in the Smollan packs into assets/photos/.

    python tools/extract_photos.py      -> assets/photos/raw_XX.<ext> + tools/_photo_sheet.png

Only real photographs are kept (>= 600 px on the long side, >= 60 KB); logos, icons
and SVGs are skipped. Name and describe them afterwards in assets/photos/index.json
(tools/photo_index.py writes it).
"""
import hashlib
import io
import os
import sys

from PIL import Image, ImageDraw
from pptx import Presentation

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smollan import MASTER_PATH, PHOTO_DIR  # noqa: E402


def main():
    prs = Presentation(MASTER_PATH)
    os.makedirs(PHOTO_DIR, exist_ok=True)
    seen, kept = set(), []
    for part in prs.part.package.iter_parts():
        name = str(part.partname)
        if not name.startswith("/ppt/media/") or not name.endswith((".jpg", ".jpeg", ".png")):
            continue
        blob = part.blob
        sha = hashlib.sha1(blob).hexdigest()
        if sha in seen or len(blob) < 60_000:
            continue
        seen.add(sha)
        try:
            im = Image.open(io.BytesIO(blob))
        except Exception:
            continue
        if max(im.size) < 600:
            continue
        ext = ".png" if name.endswith(".png") else ".jpg"
        out = os.path.join(PHOTO_DIR, f"raw_{len(kept) + 1:02d}{ext}")
        with open(out, "wb") as f:
            f.write(blob)
        kept.append((out, im.size))
    # contact sheet for naming
    W, H, cols = 300, 200, 5
    rows = (len(kept) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * (H + 18)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (path, size) in enumerate(kept):
        im = Image.open(path).convert("RGB")
        im.thumbnail((W - 6, H - 6))
        x, y = (i % cols) * W, (i // cols) * (H + 18)
        sheet.paste(im, (x + 3, y + 18))
        d.text((x + 4, y + 3), f"{os.path.basename(path)} {size[0]}x{size[1]}", fill="black")
    sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_photo_sheet.png"))
    print(f"kept {len(kept)} photos")


if __name__ == "__main__":
    main()
