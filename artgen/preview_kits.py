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

def _stripe_mix(u, n, c1, c2, aa=0.06):
    x = np.clip(u, 0, 0.999) * n; fl = np.floor(x); fr = x - fl; band = (fl.astype(np.int64) & 1).astype(np.float32)
    d = np.minimum(fr, 1 - fr); k = (aa - d) / aa * 0.5
    t = np.where(d < aa, np.where(band > 0, 1 - k, k), band)
    return c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]

def build_kit(im, kit, hair=(60, 44, 34), skinMul=1.10):
    """Mirror of index.html buildKit() — SKIN-AS-REGION format: alpha 255=kit, 254=detail; kit pixel
    R=shade, G=u(0-255), B=(regionId<<5)|v5. Must run on the FULL-RES sprite (exact alpha/region)."""
    a = np.asarray(im.convert("RGBA")).astype(np.int32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    out = a.astype(np.float32)
    K = { "c1": col(kit["c1"]), "c2": col(kit.get("c2", kit["c1"])), "sleeves": col(kit.get("sleeves", kit["c1"])),
          "shorts": col(kit.get("shorts", "white")), "socks": col(kit.get("socks", kit["c1"])),
          "collar": col(kit.get("collar", kit["c1"])), "cuff": col(kit.get("cuff", kit["c1"])),
          "sockTop": col(kit.get("sockTop", kit.get("socks", kit["c1"]))) }
    sN = kit.get("stripeN", 7); slN = kit.get("sleeveN", 10)
    kit_px = al == 255; detail = (al >= 8) & (al < 255)
    region = b >> 5; u = g / 255.0; v = (b & 31) / 31.0; shade = r.astype(np.float32)
    skin = detail & (r > 90) & (r >= g) & (g >= b - 6) & ((r - b) > 10)
    for c in range(3): out[..., c] = np.where(skin, np.minimum(255, a[..., c] * skinMul), out[..., c])
    def patv(p, U, V, n):
        if p == "stripes":  return (np.floor(np.minimum(0.999, U) * n) % 2) == 1
        if p == "hoops":    return (np.floor(np.minimum(0.999, V) * 9) % 2) == 1
        if p == "halves":   return U > 0.5
        if p == "quarters": return (U > 0.5) != (V > 0.5)
        if p == "sash":     return np.abs(U + V - 1) < 0.18
        return np.zeros(U.shape, bool)
    def put(m, c, sh):
        if not m.any(): return
        f = (sh[m] / 255 * 1.04)[:, None]
        base = c if getattr(c, "ndim", 1) == 2 else c[None, :]
        out[m, :3] = np.minimum(255, base * f)
    m1 = kit_px & (region == 1)
    if kit.get("p") == "stripes": put(m1, _stripe_mix(u[m1], sN, K["c1"], K["c2"]), shade)
    else:
        pat = patv(kit.get("p", "solid"), u, v, sN); put(m1 & ~pat, K["c1"], shade); put(m1 & pat, K["c2"], shade)
    put(kit_px & (region == 2), K["shorts"], shade); put(kit_px & (region == 3), K["socks"], shade)
    m4 = kit_px & (region == 4)
    if kit.get("sleeveP") == "stripes": put(m4, _stripe_mix(u[m4], slN, K["sleeves"], K["c2"]), shade)
    elif kit.get("sleeveP"):
        pat = patv(kit["sleeveP"], u, v, slN); put(m4 & ~pat, K["sleeves"], shade); put(m4 & pat, K["c2"], shade)
    else: put(m4, K["sleeves"], shade)
    put(kit_px & (region == 5), K["collar"], shade); put(kit_px & (region == 6), K["cuff"], shade)
    put(kit_px & (region == 7), K["sockTop"], shade)
    return Image.fromarray(out.astype(np.uint8))

def kit_of(slug, away=False):
    return TJ[slug]["kits"]["a" if away else "h"]

if __name__ == "__main__":
    # Recolour at FULL RES (the format's alpha/region bits are exact only at native res), then
    # downscale for the showcase (mirrors the engine: buildKit full-res -> drawImage downscales).
    _ssheet = Image.open(os.path.join(ROOT, "assets/sprites/striker_sheet.png"))
    strik = _ssheet.crop((0, 0, 600, _ssheet.height))            # frame 0 = idle (600px frames)
    _dsheet = Image.open(os.path.join(ROOT, "assets/sprites/defender_sheet.png"))
    deff = _dsheet.crop((0, 0, 268, _dsheet.height))             # defender variant 0 (268px frames)
    man = json.load(open(os.path.join(ROOT, "assets/sprites/keeper_atlas.json")))["frames"]["1"]
    ksheet = Image.open(os.path.join(ROOT, "assets/sprites/keeper_atlas.png"))
    keep = ksheet.crop((man["x"], man["y"], man["x"] + man["w"], man["y"] + man["h"]))

    HAIRS = [(40, 40, 42), (150, 95, 45), (225, 195, 120), (196, 96, 0)]
    show_strikers = ["Liverpool", "Arsenal", "Newcastle", "AstonVilla", "Brazil", "Argentina"]
    show_defs = [("Celtic", 0), ("Juventus", 0), ("Monaco", 0), ("CrystalPalace", 0),
                 ("Barcelona", 0), ("Liverpool", 1), ("Germany", 1), ("Wolves", 0), ("PSG", 0), ("Sunderland", 0)]
    def _disp(im, h):  # recolour output -> display height h
        return im.resize((round(im.width * h / im.height), h), Image.BILINEAR)
    sheet = Image.new("RGB", (2150, 430), (16, 84, 34))
    x = 8
    for i, slug in enumerate(show_strikers):
        im = _disp(build_kit(strik, kit_of(slug), HAIRS[i % 4]), 200)
        sheet.paste(im, (x, 14), im); x += im.width - 40
    x += 60
    for i, (slug, away) in enumerate(show_defs):
        im = _disp(build_kit(deff, kit_of(slug, away), HAIRS[(i + 1) % 4]), 150)
        sheet.paste(im, (x, 200), im); x += im.width + 6
    gk = _disp(build_kit(keep, {"p": "solid", "c1": "#ffe23d", "shorts": "#15171d", "socks": "#ffe23d"}, (34, 28, 24)), 150)
    sheet.paste(gk, (x + 10, 410 - gk.height), gk); x += gk.width + 30
    import tempfile
    _outp = os.path.join(tempfile.gettempdir(), "kits_sheet.png")
    sheet.crop((0, 0, min(2150, x + 20), 430)).save(_outp)
    print("wrote", _outp)
