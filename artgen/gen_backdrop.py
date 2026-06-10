"""Generate assets/stadium/backdrop.png — the L0 stadium backdrop layer.

Early-2000s English top-flight look: cantilever roof with white fascia, two packed
tiers behind the goal, perimeter wall, striped pitch with a worn goalmouth.
NO goal, NO advertising boards, NO text — those are separate layers (see
docs/STADIUM_ASSET_SPEC.md). All band geometry comes from the spec table.

Run:  python3 artgen/gen_backdrop.py        (writes assets/stadium/backdrop.png)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 2                          # export at 2x logical (matches current art convention)
VW, PLAY_H = 924, 400          # backdrop covers the full view width, y 0..400
W, H = VW * S, PLAY_H * S
OX = 187                       # field x -> view x offset
GOAL_CX = (135 + 430) / 2 + OX # vanishing point x ≈ 469.5 view (spec §1 note)

# band geometry (logical y, from STADIUM_ASSET_SPEC.md §2)
ROOF_B   = 16     # roof underside 0..16, white fascia at its base
TIER2_B  = 56     # upper tier crowd 16..56
DIV_B    = 63     # tier divider band 56..63
TIER1_B  = 99     # lower tier crowd 63..99
WALL_B   = 104    # perimeter wall top 99..104
DARK_B   = 143    # hoarding zone base 104..143 (covered by the boards layer)
GRASS_B  = 400

rng = np.random.default_rng(20060513)   # fixed seed -> reproducible asset

img = np.zeros((H, W, 3), dtype=np.float32)

def yl(v): return int(v * S)            # logical y -> px row

# ---------- roof ----------
# dark steel underside with a subtle horizontal rib texture, lighter toward the fascia
for y in range(0, yl(ROOF_B)):
    t = y / max(1, yl(ROOF_B))
    base = np.array([30, 33, 39]) + t * np.array([14, 14, 16])
    img[y, :] = base
for ry in range(3, yl(ROOF_B) - 4, 7):                       # roof ribs
    img[ry, :] *= 0.82
# white fascia board along the roof edge (classic 90s/00s stand signature)
img[yl(ROOF_B) - 5 * S // 2: yl(ROOF_B), :] = np.array([225, 227, 230])
# faint floodlight glow bleeding under the roof
xx = np.arange(W)
for gx in (W * 0.18, W * 0.82):
    glow = np.exp(-((xx - gx) ** 2) / (2 * (W * 0.06) ** 2)) * 26
    img[0:yl(ROOF_B) - 4, :] += glow[None, :, None]

# ---------- crowd tiers (pointillist heads/shirts) ----------
def crowd(y0, y1, dot_min, dot_max, dark):
    """Fill logical band y0..y1 with a packed-crowd dot field."""
    r0, r1 = yl(y0), yl(y1)
    # dim concrete base behind the bodies
    img[r0:r1, :] = np.array([26, 27, 33]) * (0.9 if dark else 1.1)
    area = (r1 - r0) * W
    n = int(area / (dot_min * dot_min * 1.65))
    ys = rng.integers(r0, r1, n)
    xs = rng.integers(0, W, n)
    # palette: winter jackets (navy/black/grey), club shirts (red/blue/white), skin, hair
    pal = np.array([
        [38, 42, 58], [30, 30, 36], [70, 72, 80], [90, 88, 96],      # coats
        [150, 40, 44], [160, 50, 50], [44, 60, 120], [200, 200, 205],# shirts/scarves
        [196, 158, 124], [180, 140, 110],                            # faces
        [50, 38, 30], [110, 90, 64],                                 # hair
    ], dtype=np.float32)
    wts = np.array([3, 3, 2.4, 1.6, 1.3, 1.1, 1.2, 1.1, 2.6, 1.6, 1.4, 0.8])
    wts = wts / wts.sum()
    cols = pal[rng.choice(len(pal), n, p=wts)]
    cols *= rng.uniform(0.78, 1.15, (n, 1))                          # per-dot lighting variance
    if dark:
        cols *= 0.8                                                  # upper tier sits in roof shadow
    sizes = rng.integers(dot_min, dot_max + 1, n)
    for x, y, c, sz in zip(xs, ys, cols, sizes):
        img[y:min(r1, y + sz), x:min(W, x + sz)] = c
    # row shading: each terrace row slightly darker at its base (depth read)
    for ry in range(r0, r1, 5 * S):
        img[ry:ry + S, :] *= 0.88

crowd(ROOF_B, TIER2_B, 2, 3, dark=True)     # upper tier: smaller, dimmer heads
# tier divider: concrete balcony edge
img[yl(TIER2_B):yl(DIV_B), :] = np.array([58, 62, 70])
img[yl(TIER2_B):yl(TIER2_B) + S, :] = np.array([95, 100, 108])
crowd(DIV_B, TIER1_B, 3, 5, dark=False)     # lower tier: bigger, brighter
# stairwell aisles cutting both tiers (regular gaps you see behind every goal)
for ax in np.linspace(W * 0.08, W * 0.92, 7):
    a0, a1 = int(ax - 3 * S), int(ax + 3 * S)
    img[yl(ROOF_B):yl(TIER2_B), a0:a1] = np.array([44, 46, 52])
    img[yl(DIV_B):yl(TIER1_B), a0:a1] = np.array([50, 52, 58])

# ---------- perimeter wall + dark base under the hoardings ----------
img[yl(TIER1_B):yl(WALL_B), :] = np.array([88, 92, 100])             # wall cap
img[yl(TIER1_B):yl(TIER1_B) + S, :] = np.array([130, 134, 140])
# 104..143: mostly hidden behind the boards layer; keep a plausible dark walkway
for y in range(yl(WALL_B), yl(DARK_B)):
    t = (y - yl(WALL_B)) / max(1, yl(DARK_B) - yl(WALL_B))
    img[y, :] = np.array([24, 30, 26]) + t * np.array([14, 22, 12])

# ---------- pitch ----------
LIGHT = np.array([96, 144, 70], dtype=np.float32)    # mown-stripe greens
DARKG = np.array([80, 126, 58], dtype=np.float32)
# stripe boundaries: equal world depth -> heights grow toward the viewer
bounds, y, hgt = [143], 143.0, 7.0
while y < 400:
    y += hgt; hgt *= 1.22; bounds.append(min(400, y))
for i in range(len(bounds) - 1):
    g = LIGHT if i % 2 == 0 else DARKG
    r0, r1 = yl(bounds[i]), yl(bounds[i + 1])
    rows = np.arange(r0, r1)
    depth = rows / H                                   # nearer grass slightly richer/darker
    shade = (1.04 - depth * 0.18)[:, None, None]
    img[r0:r1, :] = g[None, None, :] * shade
# blade noise
gr0 = yl(143)
noise = rng.normal(0, 4.5, (H - gr0, W, 1))
img[gr0:, :] += noise
# hoarding shadow falling onto the grass top
for i, y in enumerate(range(gr0, yl(150))):
    img[y, :] *= 0.78 + 0.22 * (i / max(1, yl(150) - gr0))
# goal line (full width — runs to the corners off-view)
img[yl(162.5):yl(164), :] = img[yl(162.5):yl(164), :] * 0.25 + np.array([235, 240, 232]) * 0.75
# worn goalmouth: subtle sandy patch where the keeper works, centred on the goal
yy = np.arange(gr0, yl(190))[:, None]
xg = np.arange(W)[None, :]
wear = np.exp(-(((xg - GOAL_CX * S) / (130 * S)) ** 2 + ((yy - 167 * S) / (12 * S)) ** 2))
wear = np.clip(wear, 0, 1) * 0.45
sand = np.array([128, 118, 76], dtype=np.float32)
img[gr0:yl(190), :] = img[gr0:yl(190), :] * (1 - wear[:, :, None]) + sand * wear[:, :, None]

# ---------- finish ----------
out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
# soften the crowd dots a whisker so they read as people, not noise
crowd_zone = out.crop((0, 0, W, yl(WALL_B))).filter(ImageFilter.GaussianBlur(0.6))
out.paste(crowd_zone, (0, 0))

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "stadium")
os.makedirs(dst, exist_ok=True)
path = os.path.join(dst, "backdrop.png")
out.save(path, optimize=True)
print("wrote", os.path.normpath(path), out.size)
