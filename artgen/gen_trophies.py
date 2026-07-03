"""Generate assets/ui/trophy_*.png — 16-bit trophy renders for the trophy room.

Round 15 (owner): SHINIER, and silhouettes that read like the real silverware each one
is based on — league = crowned lid + scroll handles on a wide-shouldered body,
cup = the classic lidded pot with curved handles, euro = the tall big-eared jug (silver),
intl = the golden globe lifted on a swirling stem. Polished metal: banded shading,
dual diagonal glints, top-light falloff, rim light, specular pips, soft baked bloom.

Run:  python artgen/gen_trophies.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 240, 320      # @2x (logical 120x160)
SS = 2               # supersample factor for smooth curves


def _ellipse(d, cx, cy, rx, ry, fill):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)


def build(kind, body, dark, lite, plinth=(52, 30, 14)):
    w, h = W * SS, H * SS
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w // 2
    S = SS  # original coords are for 240x320

    if kind == "league":   # crowned lid, wide shoulders, scroll handles (league champions)
        d.polygon([(cx - 60*S, 70*S), (cx + 60*S, 70*S), (cx + 44*S, 128*S),
                   (cx + 20*S, 158*S), (cx - 20*S, 158*S), (cx - 44*S, 128*S)], fill=body)
        _ellipse(d, cx, 70*S, 62*S, 12*S, body)                       # shoulder curve
        d.rectangle([cx - 64*S, 58*S, cx + 64*S, 70*S], fill=body)    # rim collar
        d.polygon([(cx - 40*S, 58*S), (cx + 40*S, 58*S), (cx + 26*S, 36*S), (cx - 26*S, 36*S)], fill=body)
        for i in (-2, -1, 0, 1, 2):                                    # crown points
            px = cx + i * 13 * S
            d.polygon([(px - 6*S, 38*S), (px + 6*S, 38*S), (px, 22*S)], fill=body)
            _ellipse(d, px, 22*S, 3*S, 3*S, lite)
        for sgn in (-1, 1):                                            # scroll handles
            x0 = cx + sgn * 66 * S
            d.arc([x0 - 26*S, 66*S, x0 + 26*S, 130*S], 0, 360, fill=body, width=11*S)
            _ellipse(d, x0 + sgn*10*S, 128*S, 9*S, 9*S, body)
        d.rectangle([cx - 13*S, 158*S, cx + 13*S, 198*S], fill=body)   # stem
        _ellipse(d, cx, 198*S, 30*S, 8*S, body)                        # foot bell
    elif kind == "cup":    # the classic lidded pot (silver)
        _ellipse(d, cx, 108*S, 48*S, 52*S, body)                       # rounded belly
        d.polygon([(cx - 42*S, 120*S), (cx + 42*S, 120*S), (cx + 16*S, 166*S), (cx - 16*S, 166*S)], fill=body)
        d.polygon([(cx - 34*S, 62*S), (cx + 34*S, 62*S), (cx + 48*S, 76*S), (cx - 48*S, 76*S)], fill=body)
        _ellipse(d, cx, 50*S, 9*S, 12*S, body)                         # lid dome
        _ellipse(d, cx, 40*S, 5*S, 5*S, body)                          # knob
        for sgn in (-1, 1):                                            # curvy handles
            x0 = cx + sgn * 52 * S
            d.arc([x0 - 30*S, 58*S, x0 + 30*S, 132*S], 0, 360, fill=body, width=10*S)
            _ellipse(d, x0 + sgn*4*S, 62*S, 7*S, 7*S, body)
        d.rectangle([cx - 11*S, 166*S, cx + 11*S, 200*S], fill=body)
        _ellipse(d, cx, 200*S, 26*S, 7*S, body)
    elif kind == "intl":   # the golden globe on a swirling stem
        _ellipse(d, cx, 82*S, 46*S, 46*S, body)                        # globe
        d.arc([cx - 46*S, 36*S, cx + 46*S, 128*S], 0, 360, fill=dark, width=2*S)
        d.arc([cx - 22*S, 36*S, cx + 22*S, 128*S], 0, 360, fill=dark, width=2*S)
        d.line([cx - 46*S, 82*S, cx + 46*S, 82*S], fill=dark, width=2*S)
        d.arc([cx - 46*S, 56*S, cx + 46*S, 108*S], 200, 340, fill=dark, width=2*S)
        for sgn in (-1, 1):                                            # swirling arms cradle the globe
            d.arc([cx + (sgn*34 - 34)*S, 108*S, cx + (sgn*34 + 34)*S, 196*S],
                  90 if sgn > 0 else 270, 270 if sgn > 0 else 90, fill=body, width=13*S)
        d.polygon([(cx - 20*S, 196*S), (cx + 20*S, 196*S), (cx + 12*S, 150*S), (cx - 12*S, 150*S)], fill=body)
    else:                  # "euro": the tall big-eared jug (silver)
        d.polygon([(cx - 38*S, 44*S), (cx + 38*S, 44*S), (cx + 32*S, 150*S),
                   (cx + 16*S, 178*S), (cx - 16*S, 178*S), (cx - 32*S, 150*S)], fill=body)
        d.rectangle([cx - 46*S, 32*S, cx + 46*S, 46*S], fill=body)     # wide rim
        _ellipse(d, cx, 32*S, 46*S, 7*S, body)
        for sgn in (-1, 1):                                            # the BIG ears
            x0 = cx + sgn * 54 * S
            d.arc([x0 - 34*S, 40*S, x0 + 34*S, 156*S], 0, 360, fill=body, width=12*S)
        d.rectangle([cx - 12*S, 178*S, cx + 12*S, 204*S], fill=body)
        _ellipse(d, cx, 204*S, 28*S, 7*S, body)

    # plinth (all): bevelled dark base with a gold name plate
    d.polygon([(cx - 54*S, 232*S), (cx + 54*S, 232*S), (cx + 44*S, 206*S), (cx - 44*S, 206*S)], fill=plinth)
    d.rectangle([cx - 58*S, 232*S, cx + 58*S, 254*S], fill=tuple(int(v*0.8) for v in plinth))
    d.rectangle([cx - 58*S, 250*S, cx + 58*S, 254*S], fill=tuple(int(v*0.55) for v in plinth))
    d.rectangle([cx - 38*S, 214*S, cx + 38*S, 226*S], fill=(238, 210, 130))
    d.rectangle([cx - 38*S, 223*S, cx + 38*S, 226*S], fill=(180, 148, 70))

    img = img.resize((W, H), Image.LANCZOS)

    # ---- polished metal: bands + DUAL glints + top light + rim light + specular pips ----
    a = np.asarray(img).astype(np.float32)
    mask = a[:, :, 3] > 40
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx2 = W / 2
    body_m = mask & (np.abs(a[:, :, 0] - body[0]) < 40) & (np.abs(a[:, :, 2] - body[2]) < 40)
    band = np.sin((xx - cx2) / W * np.pi)                     # bright centre, darker sides
    shade = 0.72 + 0.5 * np.clip(band, 0, 1)
    vert = 1.0 - 0.18 * np.clip((yy - 40) / 200, 0, 1)        # light falls from above
    for c in range(3):
        a[:, :, c] = np.where(body_m, np.clip(a[:, :, c] * shade * vert, 0, 255), a[:, :, c])
    for gx, gw, gs in ((cx2 + 78, 20, 0.85), (cx2 - 62, 10, 0.5)):     # two polish streaks
        glint = np.exp(-(((xx + yy * 0.7) - gx - 60) / gw) ** 2)
        for c in range(3):
            a[:, :, c] = np.where(body_m, np.clip(a[:, :, c] + glint * np.array(lite)[c] * gs, 0, 255), a[:, :, c])
    edge = body_m & ~np.roll(body_m, 3, axis=0)               # rim light on top edges
    for c in range(3):
        a[:, :, c] = np.where(edge, np.clip(a[:, :, c] * 0.4 + np.array(lite)[c] * 0.9, 0, 255), a[:, :, c])
    out = Image.fromarray(a.astype(np.uint8))
    dd = ImageDraw.Draw(out)                                  # hard specular sparkles
    for (px, py, pr) in ((cx2 + 24, 74, 3), (cx2 - 18, 100, 2), (cx2 + 10, 52, 2)):
        dd.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 255, 250, 255))
    # dark outline under + soft bloom halo baked in
    al = out.split()[3]
    dil = al.filter(ImageFilter.MaxFilter(5))
    halo = al.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.35))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), tuple(list(lite) + [0]))
    glow.putalpha(halo)
    base.alpha_composite(glow)
    ol = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ol.paste(Image.new("RGBA", (W, H), dark + (255,)), (0, 0), dil)
    base.alpha_composite(ol)
    base.alpha_composite(out)
    return base


dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ui")
os.makedirs(dst, exist_ok=True)
for kind, body, dark, lite, fn in [
    ("league", (250, 200, 52),  (58, 36, 4),  (255, 248, 208), "trophy_league.png"),
    ("cup",    (226, 230, 240), (38, 42, 52), (255, 255, 255), "trophy_cup.png"),
    ("euro",   (214, 220, 234), (38, 42, 52), (255, 255, 255), "trophy_euro.png"),
    ("intl",   (252, 192, 44),  (58, 36, 4),  (255, 244, 196), "trophy_intl.png"),
]:
    build(kind, body, dark, lite).save(os.path.join(dst, fn), optimize=True)
    print("wrote", fn)
