"""Generate assets/ui/trophy_*.png — Sega-style 16-bit trophy renders for the trophy room.

Chunky gold/silver metal with banded shading, hard highlights, dark outline —
matches the scoreboard/logo art direction. League trophy now; cup/euro variants
generated too (used as competitions land, CAREER_DESIGN E1/E4).

Run:  python3 artgen/gen_trophies.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 240, 320      # @2x (logical 120x160)

def build(kind, body, dark, lite, plinth=(60, 34, 16)):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W // 2
    if kind == "league":   # big-eared classic: wide bowl, tall handles, square plinth
        d.polygon([(cx-62, 44), (cx+62, 44), (cx+40, 150), (cx-40, 150)], fill=body)   # bowl
        d.rectangle([cx-66, 32, cx+66, 48], fill=body)                                  # rim
        for sgn in (-1, 1):                                                             # ears
            x0 = cx + sgn*62
            d.arc([x0-34+ (0 if sgn<0 else 0), 40, x0+34, 120], 0, 360, fill=body, width=14)
        d.rectangle([cx-12, 150, cx+12, 196], fill=body)                                # stem
        d.polygon([(cx-34, 196), (cx+34, 196), (cx+26, 184), (cx-26, 184)], fill=body)  # collar
    elif kind == "cup":    # slimmer cup with lid
        d.polygon([(cx-46, 64), (cx+46, 64), (cx+28, 160), (cx-28, 160)], fill=body)
        d.polygon([(cx-30, 40), (cx+30, 40), (cx+46, 64), (cx-46, 64)], fill=body)      # lid
        d.ellipse([cx-8, 24, cx+8, 42], fill=body)                                      # knob
        for sgn in (-1, 1):
            x0 = cx + sgn*46
            d.arc([x0-26, 66, x0+26, 130], 0, 360, fill=body, width=11)
        d.rectangle([cx-10, 160, cx+10, 200], fill=body)
    elif kind == "intl":   # world trophy: golden globe held by a column
        d.ellipse([cx-44, 40, cx+44, 128], fill=body)                                   # globe
        d.arc([cx-44, 40, cx+44, 128], 0, 360, fill=dark, width=3)
        d.arc([cx-20, 40, cx+20, 128], 0, 360, fill=dark, width=3)                      # meridians
        d.line([cx-44, 84, cx+44, 84], fill=dark, width=3)                              # equator
        d.polygon([(cx-26, 196), (cx+26, 196), (cx+10, 120), (cx-10, 120)], fill=body)  # column
    else:                  # "euro": tall jug with big handles
        d.polygon([(cx-40, 36), (cx+40, 36), (cx+30, 180), (cx-30, 180)], fill=body)
        d.rectangle([cx-46, 28, cx+46, 42], fill=body)
        for sgn in (-1, 1):
            x0 = cx + sgn*44
            d.arc([x0-30, 44, x0+30, 150], 0, 360, fill=body, width=12)
        d.rectangle([cx-11, 180, cx+11, 206], fill=body)
    # plinth (all)
    d.polygon([(cx-52, 232), (cx+52, 232), (cx+44, 206), (cx-44, 206)], fill=plinth)
    d.rectangle([cx-56, 232, cx+56, 252], fill=tuple(int(v*0.8) for v in plinth))
    d.rectangle([cx-40, 214, cx+40, 224], fill=(220, 214, 196))                         # name plate

    # ---- 16-bit metal shading: vertical bands + diagonal glint, then outline ----
    a = np.asarray(img).astype(np.float32)
    mask = a[:, :, 3] > 0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    body_m = mask & (np.abs(a[:, :, 0] - body[0]) < 30) & (np.abs(a[:, :, 2] - body[2]) < 30)
    band = np.sin((xx - cx) / W * np.pi)                       # bright centre, darker sides
    shade = 0.78 + 0.42 * np.clip(band, 0, 1)
    for c in range(3):
        a[:, :, c] = np.where(body_m, np.clip(a[:, :, c] * shade, 0, 255), a[:, :, c])
    glint = np.exp(-(((xx + yy*0.7) - (cx + 90)) / 26) ** 2)   # diagonal polish streak
    for c in range(3):
        a[:, :, c] = np.where(body_m, np.clip(a[:, :, c] + glint * np.array(lite)[c] * 0.55, 0, 255), a[:, :, c])
    out = Image.fromarray(a.astype(np.uint8))
    # dark outline: dilate alpha, draw under
    al = out.split()[3]
    dil = al.filter(ImageFilter.MaxFilter(5))
    ol = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ol.paste(Image.new("RGBA", (W, H), dark + (255,)), (0, 0), dil)
    ol.paste(out, (0, 0), out)
    return ol

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ui")
os.makedirs(dst, exist_ok=True)
for kind, body, dark, lite, fn in [
    ("league", (244, 196, 48), (60, 38, 4),  (255, 246, 200), "trophy_league.png"),
    ("cup",    (228, 230, 238), (40, 44, 54), (255, 255, 255), "trophy_cup.png"),
    ("euro",   (244, 196, 48), (60, 38, 4),  (255, 246, 200), "trophy_euro.png"),
    ("intl",   (244, 196, 48), (60, 38, 4),  (255, 246, 200), "trophy_intl.png"),
]:
    build(kind, body, dark, lite).save(os.path.join(dst, fn), optimize=True)
    print("wrote", fn)
