"""Generate assets/stadium/backdrop.png — the L0 stadium backdrop layer.

Early-2000s English top-flight look at 16-bit (Mega Drive) detail level:
cantilever roof + white fascia + floodlight banks, two packed row-aligned crowd
tiers with colour sections and banners, perimeter wall, and a striped pitch with
proper (stylised) markings — six-yard box, penalty area, spot and arc — drawn in
the game's perspective. NO goal, NO advertising boards, NO text (separate layers,
see docs/STADIUM_ASSET_SPEC.md).

Run:  python3 artgen/gen_backdrop.py        (writes assets/stadium/backdrop.png)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 2                          # export at 2x logical
VW, PLAY_H = 924, 400
W, H = VW * S, PLAY_H * S
OX = 187                       # field x -> view x
GOAL_CX = (135 + 430) / 2 + OX # vanishing axis x ≈ 469.5 view (spec §1)
PERSP = 0.00243                # lateral spread per px of depth: matches keeper 0.75@y163 -> striker 1.0@y300

# band geometry (logical y, spec §2)
ROOF_B, TIER2_B, DIV_B, TIER1_B, WALL_B, DARK_B = 16, 56, 63, 99, 104, 143
GRASS_TOP, GOAL_LINE_Y = 143, 163

rng = np.random.default_rng(20060513)
img = np.zeros((H, W, 3), dtype=np.float32)
yl = lambda v: int(v * S)

# ---------- roof: steel underside, ribs, floodlight banks, white fascia ----------
for y in range(0, yl(ROOF_B)):
    t = y / max(1, yl(ROOF_B))
    img[y, :] = np.array([28, 31, 38]) + t * np.array([16, 16, 18])
for ry in range(3, yl(ROOF_B) - 5, 6):
    img[ry, :] *= 0.80
xx = np.arange(W)
for gx in (W * 0.18, W * 0.82):                       # floodlight banks: glow + lamp grid
    glow = np.exp(-((xx - gx) ** 2) / (2 * (W * 0.05) ** 2)) * 30
    img[0:yl(ROOF_B) - 4, :] += glow[None, :, None]
    for r in range(2):
        for c in range(8):
            lx, ly_ = int(gx - 28 + c * 8), 6 + r * 8
            img[ly_:ly_ + 4, lx:lx + 4] = np.array([255, 250, 220])
img[yl(ROOF_B) - 5: yl(ROOF_B), :] = np.array([228, 230, 233])       # fascia board
for sx_ in range(0, W, 60 * S):                                       # fascia support stubs
    img[yl(ROOF_B) - 9: yl(ROOF_B) - 5, sx_: sx_ + 2 * S] = np.array([180, 183, 188])

# ---------- crowd: row-aligned 16-bit heads with colour sections ----------
PAL = np.array([
    [38, 42, 58], [30, 30, 36], [72, 74, 82], [92, 90, 98],       # 0-3 coats
    [168, 42, 46], [186, 54, 54],                                  # 4-5 red shirts/scarves
    [48, 66, 138], [70, 92, 170],                                  # 6-7 blue
    [208, 208, 214], [235, 235, 240],                              # 8-9 white
    [198, 160, 126], [180, 140, 110],                              # 10-11 faces
    [52, 40, 32], [112, 92, 66], [228, 204, 130],                  # 12-14 hair
], dtype=np.float32)
BASE_W = np.array([2.6, 2.6, 2.0, 1.4, 1.2, 1.0, 1.0, 0.8, 1.0, 0.7, 2.6, 1.6, 1.5, 0.9, 0.4])

def sections(seed_n=6):
    """Random crowd colour sections (home red end, away blue block, white...)"""
    out, x = [], 0
    while x < W:
        wseg = int(rng.uniform(90, 220) * S)
        bias = rng.choice([4, 4, 6, 8, -1], p=[0.30, 0.15, 0.20, 0.15, 0.20])  # -1 = no bias
        out.append((x, min(W, x + wseg), bias))
        x += wseg
    return out

def section_of(secs, x):
    for x0, x1, b in secs:
        if x0 <= x < x1: return b
    return -1

def crowd(y0, y1, head, dark):
    r0, r1 = yl(y0), yl(y1)
    img[r0:r1, :] = np.array([24, 25, 31])
    secs = sections()
    row_h = head + 1
    for ry in range(r0, r1 - head, row_h):                # terraced rows of heads
        rl = 0.84 + 0.32 * rng.random()                   # per-row lighting
        x = int(rng.integers(0, head))
        while x < W - head:
            bias = section_of(secs, x)
            if bias >= 0 and rng.random() < 0.5:
                ci = bias + int(rng.integers(0, 2))
            else:
                ci = int(rng.choice(len(PAL), p=BASE_W / BASE_W.sum()))
            c = PAL[ci] * rl * rng.uniform(0.82, 1.12) * (0.78 if dark else 1.0)
            img[ry + 1: ry + head, x: x + head] = c                       # body/shirt block
            hc = PAL[10 + int(rng.integers(0, 2))] * rl * (0.78 if dark else 1.0)
            img[ry: ry + max(1, head // 2), x + 1: x + head - 1] = hc      # head above
            x += head + int(rng.integers(0, 2))
        img[ry + row_h - 1: ry + row_h, :] *= 0.72                         # row shadow line

crowd(ROOF_B, TIER2_B, 3 * S // 2 + 1, dark=True)         # upper tier, smaller heads
img[yl(TIER2_B):yl(DIV_B), :] = np.array([60, 64, 72])    # balcony divider
img[yl(TIER2_B):yl(TIER2_B) + S, :] = np.array([100, 105, 112])
crowd(DIV_B, TIER1_B, 2 * S, dark=False)                  # lower tier, bigger heads
# stairwell aisles
for ax in np.linspace(W * 0.08, W * 0.92, 7):
    a0, a1 = int(ax - 3 * S), int(ax + 3 * S)
    img[yl(ROOF_B):yl(TIER2_B), a0:a1] = np.array([46, 48, 54])
    img[yl(DIV_B):yl(TIER1_B), a0:a1] = np.array([52, 54, 60])

# ---------- perimeter wall + dark base under the boards ----------
img[yl(TIER1_B):yl(WALL_B), :] = np.array([90, 94, 102])
img[yl(TIER1_B):yl(TIER1_B) + S, :] = np.array([132, 136, 142])
for y in range(yl(WALL_B), yl(DARK_B)):
    t = (y - yl(WALL_B)) / max(1, yl(DARK_B) - yl(WALL_B))
    img[y, :] = np.array([24, 30, 26]) + t * np.array([14, 22, 12])

# ---------- pitch: fewer, thicker mow stripes with 16-bit dither seams ----------
LIGHT = np.array([100, 152, 68], dtype=np.float32)
DARKG = np.array([82, 130, 55], dtype=np.float32)
bounds, y, hgt = [GRASS_TOP], float(GRASS_TOP), 17.0
while y < PLAY_H:
    y += hgt; hgt *= 1.28; bounds.append(min(PLAY_H, y))
gr0 = yl(GRASS_TOP)
for i in range(len(bounds) - 1):
    g = LIGHT if i % 2 == 0 else DARKG
    r0, r1 = yl(bounds[i]), yl(bounds[i + 1])
    depth = (np.arange(r0, r1) / H)[:, None, None]
    img[r0:r1, :] = g[None, None, :] * (1.05 - depth * 0.16)
xg = np.arange(W)[None, :]
for b in bounds[1:-1]:                                     # checkerboard dither seam (MD classic)
    rb = yl(b)
    above = img[rb - 3].copy(); below = img[min(H - 1, rb + 3)].copy()
    for off in (-1, 0):
        row = rb + off
        mask = ((xg[0] + row) % 2 == 0)
        img[row, mask] = below[mask]; img[row, ~mask] = above[~mask]
img[gr0:, :] += rng.normal(0, 2.2, (H - gr0, W, 1))        # light blade noise
for i, yy_ in enumerate(range(gr0, yl(150))):              # hoarding shadow on the grass top
    img[yy_, :] *= 0.78 + 0.22 * (i / max(1, yl(150) - gr0))
# worn goalmouth (kept subtle, under the markings)
ys_ = np.arange(gr0, yl(190))[:, None]
wear = np.exp(-(((xg - GOAL_CX * S) / (125 * S)) ** 2 + ((ys_ - 167 * S) / (11 * S)) ** 2)) * 0.32
sand = np.array([126, 116, 74], dtype=np.float32)
img[gr0:yl(190), :] = img[gr0:yl(190), :] * (1 - wear[:, :, None]) + sand * wear[:, :, None]

# ---------- pitch markings (drawn with the game's perspective) ----------
out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(out, "RGBA")
LINE = (240, 244, 236, 225)
def PX(lat, yy): return (GOAL_CX + lat * (1 + PERSP * (yy - GOAL_LINE_Y))) * S
def PY(yy): return yy * S
def pline(p0, p1, w_=4):
    d.line([p0, p1], fill=LINE, width=w_)
# goal line — full width (runs to the corners off-view)
d.line([(0, PY(GOAL_LINE_Y)), (W, PY(GOAL_LINE_Y))], fill=LINE, width=5)
# six-yard box: half-width 200, depth to y196 (stylised: the game's goal is arcade-huge)
SIXW, SIXY = 200, 196
pline((PX(-SIXW, GOAL_LINE_Y), PY(GOAL_LINE_Y)), (PX(-SIXW, SIXY), PY(SIXY)))
pline((PX(+SIXW, GOAL_LINE_Y), PY(GOAL_LINE_Y)), (PX(+SIXW, SIXY), PY(SIXY)))
pline((PX(-SIXW, SIXY), PY(SIXY)), (PX(+SIXW, SIXY), PY(SIXY)))
# penalty area: half-width 290, depth to y242
PENW, PENY = 290, 242
pline((PX(-PENW, GOAL_LINE_Y), PY(GOAL_LINE_Y)), (PX(-PENW, PENY), PY(PENY)), 5)
pline((PX(+PENW, GOAL_LINE_Y), PY(GOAL_LINE_Y)), (PX(+PENW, PENY), PY(PENY)), 5)
pline((PX(-PENW, PENY), PY(PENY)), (PX(+PENW, PENY), PY(PENY)), 5)
# penalty spot + D (arc outside the area)
SPOTY = 258
d.ellipse([PX(0, SPOTY) - 3 * S, PY(SPOTY) - 1.6 * S, PX(0, SPOTY) + 3 * S, PY(SPOTY) + 1.6 * S], fill=LINE)
# the D: drawn as segments of a half-ellipse so both ends land exactly ON the area line
import math
ARC_HW, ARC_BOT = 118, 288
prev = None
for i in range(0, 37):
    t = math.pi * i / 36
    lat = ARC_HW * math.cos(t)
    yy = PENY + (ARC_BOT - PENY) * math.sin(t)
    pt = (PX(lat, yy), PY(yy))
    if prev: d.line([prev, pt], fill=LINE, width=5)
    prev = pt

# ---------- finish ----------
crowd_zone = out.crop((0, 0, W, yl(WALL_B))).filter(ImageFilter.GaussianBlur(0.5))
out.paste(crowd_zone, (0, 0))
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "stadium")
os.makedirs(dst, exist_ok=True)
path = os.path.join(dst, "backdrop.png")
out.save(path, optimize=True)
print("wrote", os.path.normpath(path), out.size)
