"""Generate assets/ui/logo_gold.png — the SCORDAGOL logo, Joe Montana Football style.

A faithful recreation of the Sega title treatment: tall condensed SERIF letters,
gold chrome vertical gradient, chiselled bevel (bright top-left facets, dark
bottom-right), black outline, dark-bronze 3D extrude. Rendered at high res with
supersampling, shipped as a transparent PNG the game scales down (always crisp,
identical on every device/browser font stack).

Run:  python3 artgen/gen_logo.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TXT = "SCORDAGOL"
F = 220                    # glyph size at working res (final asset is half this)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# ---- 1. condensed-tall serif mask (Montana letters are narrow and tall) ----
font = ImageFont.truetype(SERIF, F)
tmp = Image.new("L", (1, 1)); td = ImageDraw.Draw(tmp)
bb = td.textbbox((0, 0), TXT, font=font)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
m0 = Image.new("L", (tw + 8, th + 8), 0)
ImageDraw.Draw(m0).text((4 - bb[0], 4 - bb[1]), TXT, font=font, fill=255)
m0 = m0.resize((int(m0.width * 0.80), int(m0.height * 1.14)), Image.LANCZOS)   # condense + heighten

PAD = 26
W, H = m0.width + PAD * 2, m0.height + PAD * 2
mask = Image.new("L", (W, H), 0); mask.paste(m0, (PAD, PAD))
M = (np.asarray(mask, dtype=np.float32) / 255.0 > 0.5).astype(np.float32)

def shift(a, dy, dx):
    out = np.zeros_like(a)
    ys = slice(max(0, dy), H + min(0, dy)); xs = slice(max(0, dx), W + min(0, dx))
    yd = slice(max(0, -dy), H + min(0, -dy)); xd = slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = a[yd, xd]
    return out

# ---- 2. layers ----
rgb = np.zeros((H, W, 3), dtype=np.float32)
alpha = np.zeros((H, W), dtype=np.float32)

OUT_W, EXTRUDE = 4, 9
dil = np.asarray(mask.filter(ImageFilter.MaxFilter(OUT_W * 2 + 1)), np.float32) / 255.0
ext_col = np.array([34, 16, 4]); out_col = np.array([12, 6, 2])
for s in range(EXTRUDE, 0, -1):                       # dark-bronze 3D extrude, down-right
    e = shift(dil, s, s)
    rgb[e > 0.5] = ext_col + (s / EXTRUDE) * np.array([26, 12, 4])
    alpha[e > 0.5] = 1
rgb[dil > 0.5] = out_col; alpha[dil > 0.5] = 1        # black outline

# gold chrome face: vertical gradient across the glyph height
ys, xs = np.nonzero(M); gy0, gy1 = ys.min(), ys.max()
g = (np.arange(H, dtype=np.float32) - gy0) / max(1, gy1 - gy0)
g = np.clip(g, 0, 1)
stops = [(0.00, (255, 252, 232)), (0.13, (255, 233, 128)), (0.32, (244, 197, 56)),
         (0.46, (200, 138, 24)),  (0.52, (255, 246, 200)), (0.60, (224, 160, 32)),
         (0.80, (160, 100, 16)),  (1.00, (96, 56, 8))]
grad = np.zeros((H, 3), dtype=np.float32)
for i in range(len(stops) - 1):
    (p0, c0), (p1, c1) = stops[i], stops[i + 1]
    sel = (g >= p0) & (g <= p1)
    t = (g[sel] - p0) / max(1e-6, p1 - p0)
    grad[sel] = np.outer(1 - t, c0) + np.outer(t, c1)
face = grad[:, None, :].repeat(W, axis=1)

# chiselled bevel: edge band facing up-left glints, facing down-right darkens
BEV = 7
er = np.asarray(mask.filter(ImageFilter.MinFilter(BEV * 2 + 1)), np.float32) / 255.0
edge = (M > 0.5) & (er < 0.5)
lit = edge & (shift(M, BEV, BEV) < 0.5)               # up-left facet
drk = edge & (shift(M, -BEV, -BEV) < 0.5)             # down-right facet
face[lit] = face[lit] * 0.25 + np.array([255, 250, 224]) * 0.75
face[drk] = face[drk] * 0.35 + np.array([110, 62, 10]) * 0.65

rgb[M > 0.5] = face[M > 0.5]; alpha[M > 0.5] = 1

# ---- 3. compose + downsample for smooth edges ----
img = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
out = Image.fromarray(img, "RGBA").resize((W // 2, H // 2), Image.LANCZOS)
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ui")
os.makedirs(dst, exist_ok=True)
path = os.path.join(dst, "logo_gold.png")
out.save(path, optimize=True)
print("wrote", os.path.normpath(path), out.size)
