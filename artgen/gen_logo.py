"""Generate assets/ui/logo.png — the SCORDAGOL logo.

The ORIGINAL letterform (chunky heavy italic sans, plain O's — no footballs) with a
GREEN METALLIC finish: vertical green chrome gradient, chiselled bevel, and bright
diagonal polish streaks across the face. Dark-green outline + 3D extrude.
Rendered hi-res with supersampling, shipped as a transparent PNG.

Run:  python3 artgen/gen_logo.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TXT = "SCORDAGOL"
F = 200
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
STROKE = max(2, F // 26)         # fatten Bold toward an Arial-Black weight
SKEW = 0.22                      # the original logo's italic lean

# ---- 1. heavy italic sans mask ----
font = ImageFont.truetype(SANS, F)
tmp = Image.new("L", (1, 1)); td = ImageDraw.Draw(tmp)
bb = td.textbbox((0, 0), TXT, font=font, stroke_width=STROKE)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
m0 = Image.new("L", (tw + 12, th + 12), 0)
ImageDraw.Draw(m0).text((6 - bb[0], 6 - bb[1]), TXT, font=font, fill=255, stroke_width=STROKE, stroke_fill=255)
# italic shear (lean right, like the original)
sh_w = int(m0.width + SKEW * m0.height)
m0 = m0.transform((sh_w, m0.height), Image.AFFINE, (1, SKEW, -SKEW * m0.height, 0, 1, 0), resample=Image.BILINEAR)

PAD = 24
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

OUT_W, EXTRUDE = 4, 8
dil = np.asarray(mask.filter(ImageFilter.MaxFilter(OUT_W * 2 + 1)), np.float32) / 255.0
ext_col = np.array([5, 42, 20]); out_col = np.array([2, 20, 10])
for s in range(EXTRUDE, 0, -1):                       # dark-green 3D extrude, down-right
    e = shift(dil, s, s)
    rgb[e > 0.5] = ext_col + (s / EXTRUDE) * np.array([6, 18, 10])
    alpha[e > 0.5] = 1
rgb[dil > 0.5] = out_col; alpha[dil > 0.5] = 1        # dark outline

# green chrome: vertical gradient...
ys_, xs_ = np.nonzero(M); gy0, gy1 = ys_.min(), ys_.max()
g = np.clip((np.arange(H, dtype=np.float32) - gy0) / max(1, gy1 - gy0), 0, 1)
stops = [(0.00, (236, 255, 232)), (0.16, (150, 255, 140)), (0.36, (52, 224, 96)),
         (0.48, (20, 150, 60)),   (0.54, (196, 255, 200)), (0.62, (40, 190, 80)),
         (0.82, (16, 120, 48)),   (1.00, (6, 70, 28))]
grad = np.zeros((H, 3), dtype=np.float32)
for i in range(len(stops) - 1):
    (p0, c0), (p1, c1) = stops[i], stops[i + 1]
    sel = (g >= p0) & (g <= p1)
    t = (g[sel] - p0) / max(1e-6, p1 - p0)
    grad[sel] = np.outer(1 - t, c0) + np.outer(t, c1)
face = grad[:, None, :].repeat(W, axis=1)

# ...with DIAGONAL polish streaks (bright sweeps + a couple of dark ones between)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
diag = (xx + yy * 0.9) / (W + H * 0.9)               # 0..1 along the 45-ish degree axis
streak = np.ones((H, W), dtype=np.float32)
for c, amp, wd in [(0.16, 0.42, 0.030), (0.40, 0.30, 0.022), (0.66, 0.46, 0.034), (0.88, 0.26, 0.020)]:
    streak += amp * np.exp(-((diag - c) / wd) ** 2)   # bright glints
for c, amp, wd in [(0.28, 0.16, 0.030), (0.54, 0.14, 0.026), (0.78, 0.14, 0.028)]:
    streak -= amp * np.exp(-((diag - c) / wd) ** 2)   # dark counter-streaks
face = np.clip(face * streak[:, :, None], 0, 255)

# chiselled bevel: up-left facets glint, down-right facets darken
BEV = 6
er = np.asarray(mask.filter(ImageFilter.MinFilter(BEV * 2 + 1)), np.float32) / 255.0
edge = (M > 0.5) & (er < 0.5)
lit = edge & (shift(M, BEV, BEV) < 0.5)
drk = edge & (shift(M, -BEV, -BEV) < 0.5)
face[lit] = face[lit] * 0.25 + np.array([232, 255, 228]) * 0.75
face[drk] = face[drk] * 0.35 + np.array([8, 74, 30]) * 0.65

rgb[M > 0.5] = face[M > 0.5]; alpha[M > 0.5] = 1

# ---- 3. compose + downsample ----
img = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
out = Image.fromarray(img, "RGBA").resize((W // 2, H // 2), Image.LANCZOS)
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ui")
os.makedirs(dst, exist_ok=True)
path = os.path.join(dst, "logo.png")
out.save(path, optimize=True)
print("wrote", os.path.normpath(path), out.size)
