"""Trace the ORIGINAL striker/defender frames into the region-tag sprite format.

Source: assets/striker_AstonVilla_k0..k5.png + assets/defender_AstonVilla.png —
chosen because the Villa kit has four distinct colours (claret shirt, white
shorts, sky sleeves/socks), giving pixel-accurate region segmentation.

Output keeps the original silhouette and shading EXACTLY (the kick-timing read),
re-encoded per docs/SPRITE_SPEC.md:
  shirt R=shade G=u*88 B=v*88 · shorts G=shade R=u B=v · socks B=shade R=u G=v
  sleeves R=G=shade B=u · hair R=B=shade · everything else passes through as-is.
Shade is CONTINUOUS (150..255 from the source pixel's tone), so the original's
modelling/folds survive any recolour. u is row-normalised per connected part, so
stripes follow the torso and mirror from its centre.

Run:  python3 artgen/trace_sprites.py     (writes assets/sprites/striker_k*.png + defender.png)
"""
import os
import numpy as np
from PIL import Image
from collections import deque

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "sprites")

def components(mask):
    """4-connected component labels (BFS; images are small)."""
    lab = np.zeros(mask.shape, np.int32); cur = 0
    for sy, sx in zip(*np.nonzero(mask & (lab == 0))):
        if lab[sy, sx]: continue
        cur += 1
        q = deque([(sy, sx)]); lab[sy, sx] = cur
        while q:
            y, x = q.popleft()
            for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] \
                   and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur; q.append((ny, nx))
    return lab, cur

def shade_of(vals):
    """Continuous shade anchored on the garment's BASE tone (median -> bright), so a
    recoloured kit renders at full colour with the original folds as darker accents."""
    med = float(np.median(vals))
    hi = float(np.percentile(vals, 97)); lo = float(np.percentile(vals, 3))
    up = np.clip((vals - med) / max(1.0, hi - med), 0, 1)
    dn = np.clip((med - vals) / max(1.0, med - lo), 0, 1)
    return np.clip(238 + up * 17 - dn * 80, 150, 255).astype(np.uint8)

def uv_of(mask):
    """u: row-normalised across the part (stripes follow + mirror); v: bbox-normalised."""
    ys, xs = np.nonzero(mask)
    U = np.zeros(mask.shape, np.float32); V = np.zeros(mask.shape, np.float32)
    y0, y1 = ys.min(), ys.max()
    V[ys, xs] = (ys - y0) / max(1, y1 - y0)
    for ry in np.unique(ys):
        rx = xs[ys == ry]
        lo, hi = rx.min(), rx.max()
        U[ry, rx] = (rx - lo) / max(1, hi - lo)
    return U, V

def trace(src_path, logical_wh):
    im = Image.open(src_path).convert("RGBA")
    a = np.asarray(im).astype(np.int16)
    r, g, b, al = a[...,0], a[...,1], a[...,2], a[...,3]
    vis = al > 40
    out = np.asarray(im).copy()                       # finals (skin/boots/outline/AA) pass through
    out[..., 3] = np.where(vis, 255, 0)

    skin   = vis & (r > 200) & (g > 140) & (g < 240) & (b > 70) & (b < 215) & (r > g) & (g > b)
    hair   = vis & (r >= 120) & (r <= 235) & (g >= 40) & (g <= 150) & (b < 58) & (r - g >= 48) & (g - b > 34)
    claret = vis & (r > 65) & (r < 190) & (g < 70) & (b < 75) & (r - g > 40) & ~hair
    sky    = vis & (b > 120) & (b > r + 20) & (g > r + 20) & ~skin
    white  = vis & (np.minimum(np.minimum(r, g), b) >= 200) & ~skin

    H = a.shape[0]
    # split white into shorts (big, mid-body) vs collar/cuffs (small/high -> sleeves tag)
    wl, wn = components(white)
    shorts = np.zeros_like(white); trimW = np.zeros_like(white)
    for c in range(1, wn + 1):
        m = wl == c
        if m.sum() < 12: trimW |= m; continue
        cy = np.nonzero(m)[0].mean()
        (shorts if (m.sum() > 400 and 0.30*H < cy < 0.80*H) else trimW).__ior__(m)
    # split sky into sleeves (upper / adjacent to shirt) vs socks (lower)
    sl, sn = components(sky)
    sleeve = trimW.copy(); socks = np.zeros_like(sky)
    for c in range(1, sn + 1):
        m = sl == c
        cy = np.nonzero(m)[0].mean()
        (socks if cy > 0.62 * H else sleeve).__ior__(m)

    # ---- encode regions ----
    def put(mask, kind, dom):
        if not mask.any(): return
        sh = np.zeros(mask.shape, np.uint8)
        sh[mask] = shade_of(dom[mask].astype(np.float32))
        if kind in ("shirt", "shorts", "socks"):
            U, V = uv_of(mask)
            uu = (np.clip(U, 0, 1) * 88).astype(np.uint8); vv = (np.clip(V, 0, 1) * 88).astype(np.uint8)
            ch = {"shirt": (0,1,2), "shorts": (1,0,2), "socks": (2,0,1)}[kind]
            out[mask, ch[0]] = sh[mask]; out[mask, ch[1]] = uu[mask]; out[mask, ch[2]] = vv[mask]
        elif kind == "sleeve":
            U, _ = uv_of(mask)
            out[mask, 0] = out[mask, 1] = sh[mask]
            out[mask, 2] = (np.clip(U, 0, 1) * 88).astype(np.uint8)[mask]
        else:                                          # hair
            out[mask, 0] = out[mask, 2] = sh[mask]; out[mask, 1] = 0
    put(claret, "shirt", r)
    put(shorts, "shorts", (r + g + b) / 3)
    put(socks,  "socks",  b)
    put(sleeve, "sleeve", np.where(white, (r+g+b)/3, b))   # collar/cuffs share the sleeve slot
    put(hair,   "hair",   r)

    res = Image.fromarray(out).resize((logical_wh[0]*2, logical_wh[1]*2), Image.NEAREST)
    return res

if __name__ == "__main__":
    for k in range(6):
        trace(os.path.join(ROOT, f"assets/striker_AstonVilla_k{k}.png"), (131, 191)) \
            .save(os.path.join(OUT, f"striker_k{k}.png"), optimize=True)
    print("striker k0..k5 traced")
    trace(os.path.join(ROOT, "assets/defender_AstonVilla.png"), (67, 115)) \
        .save(os.path.join(OUT, "defender.png"), optimize=True)
    print("defender traced")
