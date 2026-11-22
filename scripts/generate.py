#!/usr/bin/env python3
"""Generative pixel-art set for the 'Hood Owls' NFT test collection.

Draws each owl on a 32x32 pixel grid, upscales to 512x512 with NEAREST.
Style reference: hero image (brown owl, big glowing amber eyes, green Robin
Hood hat with feather, mossy branch, dark teal starry night background).

Traits:
  body:        8 colors
  belly:       4 patterns
  eyes:        6 colors
  hat:         5 types (Robin Hood, Beanie, Cap, Wizard, None)
  hat_color:   4 colors (recorded as "None" when hat is None, so the
               uniqueness tuple matches what is actually visible)
  background:  8 night colors
  accessory:   4 values (Feather, Star, Mushroom, None)

Fixed seed 20261122 -> reproducible set. All 1000 trait tuples are
guaranteed unique; the script aborts loudly on a duplicate.
"""

import csv
import json
import os
import random
import sys
from collections import Counter

from PIL import Image

SEED = 20261122
OUT = os.path.expanduser("~/workspace/tools/test-wallet/hood-owls")
GRID = 32
SCALE = 16
SIZE = GRID * SCALE  # 512
N_TOKENS = 1000

BODY_COLORS = {
    "Cocoa": (107, 74, 47),
    "Chestnut": (139, 90, 43),
    "Slate": (90, 107, 124),
    "Plum": (124, 90, 139),
    "Forest": (74, 124, 89),
    "Sand": (201, 168, 106),
    "Ash": (138, 138, 138),
    "Rust": (166, 90, 58),
}

BELLY_PATTERNS = ["Plain", "Stripes", "Spots", "Scallop"]

EYE_COLORS = {
    "Amber": (255, 179, 71),
    "Emerald": (61, 220, 132),
    "Sapphire": (74, 144, 226),
    "Violet": (181, 101, 216),
    "Ruby": (231, 76, 60),
    "Teal": (46, 196, 182),
}

HAT_TYPES = ["Robin Hood", "Beanie", "Cap", "Wizard", "None"]

HAT_COLORS = {
    "Green": (62, 155, 79),
    "Crimson": (192, 57, 43),
    "Royal": (74, 95, 216),
    "Gold": (217, 164, 65),
}

BACKGROUNDS = {
    "Midnight Teal": (14, 46, 53),
    "Deep Navy": (16, 27, 58),
    "Forest Night": (15, 42, 26),
    "Plum Night": (36, 21, 51),
    "Charcoal": (28, 28, 34),
    "Ocean Deep": (10, 36, 56),
    "Moss Dark": (22, 36, 15),
    "Burgundy Night": (46, 18, 32),
}

ACCESSORIES = ["Feather", "Star", "Mushroom", "None"]

BRANCH = (107, 74, 47)
BRANCH_DARK = (74, 50, 32)
MOSS = (90, 143, 60)
ORANGE = (245, 166, 35)
BEAK = (255, 201, 60)
CREAM = (245, 230, 200)
SHINE = (255, 248, 231)
STAR_COLORS = [(255, 255, 255), (191, 227, 255), (255, 242, 176)]
MOON = (255, 242, 176)
FEATHER_RED = (231, 76, 60)
MUSHROOM_RED = (214, 69, 65)


def shade(rgb, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)


def blend(rgb, target, t):
    return tuple(int(c + (target[i] - c) * t) for i, c in enumerate(rgb))


class Canvas:
    """32x32 pixel buffer with clip-safe putpixel."""

    def __init__(self, bg):
        self.img = Image.new("RGB", (GRID, GRID), bg)

    def px(self, x, y, color):
        if 0 <= x < GRID and 0 <= y < GRID:
            self.img.putpixel((x, y), color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, color)

    def points(self, pts, color):
        for x, y in pts:
            self.px(x, y, color)


# Owl body silhouette (x, y) on the 32x32 grid. Head top y=9, feet y=24.
def body_pixels():
    pts = set()
    rows = {
        9: (11, 20),
        10: (12, 19),
        11: (11, 20),
        12: (10, 21),
        13: (10, 21),
        14: (10, 21),
        15: (10, 21),
        16: (10, 21),
        17: (10, 21),
        18: (10, 21),
        19: (10, 21),
        20: (11, 20),
        21: (11, 20),
        22: (12, 19),
        23: (12, 19),
        24: (12, 19),
    }
    for y, (x0, x1) in rows.items():
        for x in range(x0, x1 + 1):
            pts.add((x, y))
    # ear tufts (visible when no hat covers them)
    pts.update([(10, 10), (11, 9), (21, 10), (20, 9)])
    return pts


BODY = body_pixels()


def draw_owl(traits, rng):
    body_name, belly, eye_name, hat, hat_color, bg_name, accessory = traits
    body = BODY_COLORS[body_name]
    body_dark = shade(body, 0.62)
    face = blend(body, CREAM, 0.55)
    belly_c = blend(body, CREAM, 0.62)
    belly_dark = shade(belly_c, 0.72)
    eye = EYE_COLORS[eye_name]
    eye_glow = shade(eye, 0.45)
    eye_shine = blend(eye, (255, 255, 255), 0.45)
    bg = BACKGROUNDS[bg_name]
    outline = (22, 16, 12)

    cv = Canvas(bg)

    # --- sky: stars + a small moon (drawn first, owl covers them) ---
    for _ in range(rng.randint(10, 16)):
        cv.px(rng.randint(0, 31), rng.randint(0, 9), rng.choice(STAR_COLORS))
    cv.points([(27, 2), (28, 2), (27, 3), (28, 3)], MOON)
    cv.px(28, 2, shade(MOON, 0.75))

    # --- branch with moss ---
    cv.rect(2, 27, 29, 28, BRANCH)
    cv.rect(2, 28, 29, 28, BRANCH_DARK)
    for x in range(3, 29):
        if rng.random() < 0.35:
            cv.px(x, 26, MOSS)
            if rng.random() < 0.4:
                cv.px(x, 27, MOSS)

    # --- body outline (1px dilation) then body fill ---
    for x, y in BODY:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in BODY:
                cv.px(nx, ny, outline)
    cv.points(BODY, body)

    # --- wings (darker outer columns) ---
    for y in range(14, 20):
        cv.px(10, y, body_dark)
        cv.px(21, y, body_dark)

    # --- face patch (lighter area around the eyes) ---
    cv.rect(11, 13, 20, 17, face)

    # --- belly patch + pattern ---
    cv.rect(13, 19, 18, 23, belly_c)
    if belly == "Stripes":
        cv.rect(13, 20, 18, 20, belly_dark)
        cv.rect(13, 22, 18, 22, belly_dark)
    elif belly == "Spots":
        cv.points([(14, 20), (17, 20), (15, 22), (16, 21)], belly_dark)
    elif belly == "Scallop":
        cv.points([(13, 20), (15, 20), (17, 20), (14, 22), (16, 22), (18, 22)], belly_dark)

    # --- eyes: 3x3 blocks with glow halo, white-hot centre, shine ---
    for ex in (12, 17):
        # glow halo (orthogonal neighbours, only where face is)
        for hx, hy in (
            (ex - 1, 15), (ex + 3, 15), (ex + 1, 13), (ex + 1, 17),
        ):
            if cv.img.getpixel((hx, hy)) == face:
                cv.px(hx, hy, eye_glow)
        cv.rect(ex, 14, ex + 2, 16, eye)
        cv.px(ex + 1, 15, SHINE)
        cv.px(ex, 14, eye_shine)

    # --- beak ---
    cv.rect(15, 17, 16, 18, BEAK)
    cv.px(15, 18, ORANGE)

    # --- feet on the branch ---
    cv.points([(12, 25), (13, 25), (18, 25), (19, 25), (12, 26), (19, 26)], ORANGE)

    # --- hat ---
    if hat != "None":
        hc = HAT_COLORS[hat_color]
        hc_dark = shade(hc, 0.6)
        if hat == "Robin Hood":
            cv.rect(12, 7, 19, 8, hc)
            cv.points([(18, 6), (19, 6), (20, 5), (20, 6)], hc)
            cv.rect(11, 9, 20, 10, hc_dark)
        elif hat == "Beanie":
            cv.rect(12, 7, 19, 8, hc)
            cv.rect(11, 9, 20, 10, hc_dark)
            cv.points([(15, 5), (16, 5), (15, 6), (16, 6)], CREAM)
        elif hat == "Cap":
            cv.rect(11, 8, 20, 10, hc)
            cv.rect(21, 10, 25, 10, hc)
            cv.rect(22, 11, 24, 11, hc)
            cv.px(15, 7, hc_dark)
        elif hat == "Wizard":
            cv.rect(11, 9, 20, 10, hc)
            cv.rect(12, 8, 19, 8, hc)
            cv.rect(13, 7, 18, 7, hc)
            cv.rect(14, 6, 17, 6, hc)
            cv.rect(15, 5, 16, 5, hc)
            cv.points([(16, 3), (16, 4), (17, 4)], hc)
            cv.rect(11, 9, 20, 9, (217, 164, 65))
            cv.points([(14, 7), (16, 6)], MOON)

    # --- accessory ---
    if accessory == "Feather":
        # 4px diagonal feather anchored on the head/hat (bottom pixel
        # touches the dome or head top, so it never floats in the air)
        cv.points([(12, 8), (11, 7), (10, 6), (9, 5)], FEATHER_RED)
    elif accessory == "Star":
        cx, cy = 26, 6
        cv.points(
            [(cx, cy), (cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)],
            (255, 233, 138),
        )
        cv.px(cx, cy, SHINE)
    elif accessory == "Mushroom":
        cv.points([(5, 23), (6, 23), (7, 23), (5, 24), (6, 24), (7, 24)], MUSHROOM_RED)
        cv.points([(5, 23), (7, 23)], CREAM)
        cv.points([(6, 25), (6, 26)], CREAM)

    return cv.img.resize((SIZE, SIZE), Image.NEAREST)


def sample_traits(rng):
    body = rng.choice(list(BODY_COLORS))
    belly = rng.choice(BELLY_PATTERNS)
    eye = rng.choice(list(EYE_COLORS))
    hat = rng.choice(HAT_TYPES)
    hat_color = rng.choice(list(HAT_COLORS)) if hat != "None" else "None"
    bg = rng.choice(list(BACKGROUNDS))
    accessory = rng.choice(ACCESSORIES)
    return (body, belly, eye, hat, hat_color, bg, accessory)


def main():
    rng = random.Random(SEED)
    seen = set()
    records = []
    collisions = 0

    for token_id in range(1, N_TOKENS + 1):
        while True:
            traits = sample_traits(rng)
            if traits in seen:
                collisions += 1
                continue
            seen.add(traits)
            break
        img = draw_owl(traits, rng)
        img.save(os.path.join(OUT, f"{token_id:04d}.png"))

        body, belly, eye, hat, hat_color, bg, accessory = traits
        meta = {
            "name": f"Hood Owl #{token_id}",
            "description": "A night hunter of the Hood. One of 1,000 pixel owls keeping watch over Robinhood Chain.",
            "image": f"{token_id:04d}.png",
            "attributes": [
                {"trait_type": "Body Color", "value": body},
                {"trait_type": "Belly Pattern", "value": belly},
                {"trait_type": "Eye Color", "value": eye},
                {"trait_type": "Hat", "value": hat},
                {"trait_type": "Hat Color", "value": hat_color},
                {"trait_type": "Background", "value": bg},
                {"trait_type": "Accessory", "value": accessory},
            ],
        }
        with open(os.path.join(OUT, f"{token_id:04d}.json"), "w") as f:
            json.dump(meta, f, indent=2)
        records.append((token_id, *traits))

        if token_id % 250 == 0:
            print(f"... {token_id} done", flush=True)

    with open(os.path.join(OUT, "traits.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["token_id", "body", "belly", "eye", "hat", "hat_color", "background", "accessory"])
        w.writerows(records)

    # contact sheet: first 100 owls, 10x10 grid, each 64x64
    sheet = Image.new("RGB", (640, 640), (10, 10, 14))
    for i in range(100):
        im = Image.open(os.path.join(OUT, f"{i + 1:04d}.png")).resize((64, 64), Image.NEAREST)
        sheet.paste(im, ((i % 10) * 64, (i // 10) * 64))
    sheet.save(os.path.join(OUT, "contact-sheet.png"))

    print(f"seed: {SEED}")
    print(f"images: {N_TOKENS}")
    print(f"unique trait combos: {len(seen)}")
    print(f"collisions avoided during sampling: {collisions}")
    for idx, name in enumerate(
        ["body", "belly", "eye", "hat", "hat_color", "background", "accessory"]
    ):
        print(f"coverage {name}: {dict(Counter(r[idx + 1] for r in records))}")


if __name__ == "__main__":
    main()
