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
    """Mirror of index.html buildKit(): UV-channel tags, per-part patterns."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    vis = al >= 8
    tags = { 1: vis & (r>140) & (g<100) & (b<100),
             2: vis & (g>140) & (r<100) & (b<100),
             3: vis & (b>140) & (r<100) & (g<100),
             4: vis & (r>140) & (g>140) & (b<100) & (np.abs(r-g)<30),
             5: vis & (r>140) & (b>140) & (g<100) & (np.abs(r-b)<30) }
    K = { "c1": col(kit["c1"]), "c2": col(kit.get("c2", kit["c1"])), "sleeves": col(kit.get("sleeves", kit["c1"])),
          "shorts": col(kit.get("shorts", "white")), "socks": col(kit.get("socks", kit["c1"])) }
    p = kit.get("p", "solid")
    u = np.clip(g/88, 0, 0.999); v = np.clip(b/88, 0, 0.999)
    if   p == "stripes":  pat = (np.floor(u*7) % 2) == 1
    elif p == "hoops":    pat = (np.floor(v*9) % 2) == 1
    elif p == "halves":   pat = u > 0.5
    elif p == "quarters": pat = (u > 0.5) != (v > 0.5)
    elif p == "sash":     pat = np.abs(u + v - 1) < 0.18
    else:                 pat = np.zeros(u.shape, bool)
    out = a.copy()
    def put(m, c, shade):
        f = (shade/255*1.04)[..., None]
        out[m, :3] = np.minimum(255, (c * f)[m])
    put(tags[2], K["shorts"], g); put(tags[3], K["socks"], b)
    put(tags[4], K["sleeves"], (r+g)/2); put(tags[5], np.array(hair, np.float32), (r+b)/2)
    put(tags[1] & ~pat, K["c1"], r); put(tags[1] & pat, K["c2"], r)
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
