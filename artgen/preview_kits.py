"""Render a kit showcase by mirroring index.html's buildKit() recolour exactly.

Validates the tag/pattern contract: if this sheet looks right, the in-game
renderer produces the same result (same classification, same pattern maths).

Run:  python3 artgen/preview_kits.py   -> /tmp/kits_sheet.png
"""
import os, json
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PAL = json.load(open(os.path.join(ROOT, "assets/teams.json")))["palette"]
TJ = {t["slug"]: t for t in json.load(open(os.path.join(ROOT, "assets/teams.json")))["teams"]}
WJ = json.load(open(os.path.join(ROOT, "assets/world/world.json")))
for g in ("euro", "nations", "minnows"):
    for t in WJ[g]: TJ[t["slug"]] = t

def hexrgb(h): n = int(h[1:], 16); return np.array([(n >> 16) & 255, (n >> 8) & 255, n & 255], np.float32)
def col(name): return hexrgb(PAL.get(name, name if str(name).startswith("#") else "#cccccc"))

def build_kit(im, kit, hair=(60, 44, 34)):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    mx = np.maximum(np.maximum(r, g), b) + 1e-6
    nr, ng, nb = r / mx, g / mx, b / mx
    vis = (al >= 8) & (mx >= 70)
    tags = { 1: vis & (nr > .85) & (ng < .35) & (nb < .35), 2: vis & (ng > .85) & (nr < .35) & (nb < .35),
             3: vis & (nb > .85) & (nr < .35) & (ng < .35), 4: vis & (nr > .85) & (ng > .85) & (nb < .35),
             5: vis & (nr > .85) & (nb > .85) & (ng < .35) }
    K = { "c1": col(kit["c1"]), "c2": col(kit.get("c2", kit["c1"])), "sleeves": col(kit.get("sleeves", kit["c1"])),
          "shorts": col(kit.get("shorts", "white")), "socks": col(kit.get("socks", kit["c1"])) }
    ys, xs = np.nonzero(tags[1])
    bb = (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else (0, 1, 0, 1)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    p = kit.get("p", "solid")
    if   p == "stripes":  pat = (((xx - bb[0]) // 14) % 2) == 1
    elif p == "hoops":    pat = (((yy - bb[2]) // 16) % 2) == 1
    elif p == "halves":   pat = xx > (bb[0] + bb[1]) / 2
    elif p == "quarters": pat = (xx < (bb[0] + bb[1]) / 2) != (yy < (bb[2] + bb[3]) / 2)
    elif p == "sash":     pat = np.abs((xx - bb[0]) - (yy - bb[2]) * 0.55 - (bb[1] - bb[0]) * 0.30) < 13
    else:                 pat = np.zeros(xx.shape, bool)
    sh = (0.62 + 0.40 * mx / 255)[..., None]
    out = a.copy()
    for tg, c in ((2, K["shorts"]), (3, K["socks"]), (4, K["sleeves"]), (5, np.array(hair, np.float32))):
        m = tags[tg]; out[m, :3] = np.minimum(255, c * sh[m])
    m1 = tags[1] & ~pat; out[m1, :3] = np.minimum(255, K["c1"] * sh[m1])
    m2 = tags[1] & pat;  out[m2, :3] = np.minimum(255, K["c2"] * sh[m2])
    return Image.fromarray(out.astype(np.uint8))

def kit_of(slug, away=False):
    return TJ[slug]["kits"]["a" if away else "h"]

if __name__ == "__main__":
    strik = Image.open(os.path.join(ROOT, "assets/sprites/striker_k0.png"))
    deff = Image.open(os.path.join(ROOT, "assets/sprites/defender.png"))
    man = json.load(open(os.path.join(ROOT, "assets/sprites/keeper_atlas.json")))["frames"]["1"]
    ksheet = Image.open(os.path.join(ROOT, "assets/sprites/keeper_atlas.png"))
    keep = ksheet.crop((man["x"], man["y"], man["x"] + man["w"], man["y"] + man["h"]))

    HAIRS = [(40, 40, 42), (150, 95, 45), (225, 195, 120), (196, 96, 0)]
    show_strikers = ["Liverpool", "Arsenal", "Newcastle", "AstonVilla", "Brazil", "Argentina"]
    show_defs = [("Celtic", 0), ("Juventus", 0), ("Monaco", 0), ("CrystalPalace", 0),
                 ("Barcelona", 0), ("Liverpool", 1), ("Germany", 1), ("Wolves", 0), ("PSG", 0), ("Sunderland", 0)]
    sheet = Image.new("RGB", (2150, 430), (16, 84, 34))
    x = 8
    for i, slug in enumerate(show_strikers):
        im = build_kit(strik, kit_of(slug), HAIRS[i % 4])
        sheet.paste(im, (x, 14), im); x += im.width - 80
    x += 90
    for i, (slug, away) in enumerate(show_defs):
        im = build_kit(deff, kit_of(slug, away), HAIRS[(i + 1) % 4])
        sheet.paste(im, (x, 180), im); x += im.width + 10
    gk = build_kit(keep, {"p": "solid", "c1": "#ffe23d", "shorts": "#15171d", "socks": "#ffe23d"}, (34, 28, 24))
    sheet.paste(gk, (x + 10, 410 - gk.height), gk); x += gk.width + 30
    sheet.crop((0, 0, min(2150, x + 20), 430)).save("/tmp/kits_sheet.png")
    print("wrote /tmp/kits_sheet.png")
