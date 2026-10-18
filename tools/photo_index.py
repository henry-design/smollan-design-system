"""
Rename the extracted raw photos to descriptive names and write assets/photos/index.json.

    python tools/photo_index.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smollan import PHOTO_DIR  # noqa: E402

PHOTOS = {  # raw file -> (name, description, tags)
    "raw_01.jpg": ("woman_laptop_sofa", "Smiling woman in a teal dress working on a laptop on a sofa", "people digital ecommerce home"),
    "raw_02.jpg": ("beauty_makeup_consultant", "Beauty consultant applying make-up to a customer in store", "people beauty cosmetics instore promoter"),
    "raw_03.jpg": ("two_shoppers_phone", "Two women shopping in a grocery aisle, one checking her phone", "people shoppers grocery retail"),
    "raw_04.jpg": ("merchandiser_snacks_aisle", "Smollan merchandiser in a branded polo arranging a snacks display", "merchandiser field execution smollan retail"),
    "raw_05.jpg": ("man_stocking_jars_shelf", "Man stocking jars and spreads on a supermarket shelf", "shelf retail availability merchandising"),
    "raw_06.jpg": ("couple_fresh_produce", "Couple choosing fresh produce (lettuce) in a store", "people shoppers fresh produce"),
    "raw_07.jpg": ("man_glasses_shelf_check", "Man in glasses checking products on a brightly lit shelf", "shelf audit merchandising retail"),
    "raw_08.jpg": ("woman_phone_sofa", "Woman with braids smiling at her phone on a sofa", "people digital mobile home"),
    "raw_09.jpg": ("woman_pharmacy_shelf", "Woman choosing a product in a pharmacy / health-and-beauty aisle", "pharmacy health beauty shopper"),
    "raw_17.jpg": ("canned_goods_shelf", "Full shelves of canned goods (no people)", "shelf retail availability products"),
    "raw_18.png": ("merchandiser_mono", "Black-and-white photo of a merchandiser restocking a shelf", "merchandiser field execution mono"),
    "raw_19.jpg": ("office_team_walk", "Three colleagues walking and talking in a Smollan office corridor", "people office team corporate"),
    "raw_20.jpg": ("woman_cosmetics_aisle", "Woman with a phone in a cosmetics aisle (square crop)", "people beauty shopper mobile"),
    "raw_21.jpg": ("meeting_sofa_tablet", "Two colleagues in a meeting on a blue sofa with a tablet", "people office meeting corporate"),
    "raw_22.jpg": ("beauty_makeup_consultant_wide", "Beauty consultant applying make-up (wider crop)", "people beauty cosmetics instore"),
    "raw_23.jpg": ("woman_laptop_closeup", "Woman with braids using a laptop (close-up)", "people digital ecommerce"),
    "raw_24.jpg": ("two_women_product_choice", "Two women comparing a personal-care product in store", "people shoppers beauty"),
    "raw_25.jpg": ("woman_office_hijab", "Smiling woman in a hijab sitting in an office", "people office corporate team"),
    "raw_26.jpg": ("merchandiser_detergent_aisle", "Merchandiser arranging detergent packs on a shelf", "merchandiser field execution home care"),
    "raw_27.jpg": ("merchandiser_woman_shelf", "Smollan merchandiser (woman) placing products on a shelf", "merchandiser field execution smollan"),
    "raw_28.jpg": ("man_glasses_shelf_wide", "Man in glasses at a shelf (wider crop)", "shelf audit merchandising"),
}


def main():
    index = {}
    for f in sorted(os.listdir(PHOTO_DIR)):
        if not f.startswith("raw_"):
            continue
        src = os.path.join(PHOTO_DIR, f)
        if f not in PHOTOS:
            os.remove(src)            # diagram graphics, not photos
            continue
        name, desc, tags = PHOTOS[f]
        ext = os.path.splitext(f)[1]
        os.replace(src, os.path.join(PHOTO_DIR, name + ext))
        index[name] = {"file": name + ext, "description": desc, "tags": tags.split()}
    with open(os.path.join(PHOTO_DIR, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1)
    print(f"indexed {len(index)} photos")


if __name__ == "__main__":
    main()
