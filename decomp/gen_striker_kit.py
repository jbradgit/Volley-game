"""Per-team striker kit across all 6 volley frames. The animated player sprite (91) is an
all-red 'RIISE 6' kit with no named regions, so segment it geometrically:
  body  = largest red component (filled -> covers name/number/crest)
  socks = the other big red components (below the body)
  arms/sleeves = the THIN protrusions removed by a morphological opening of the body
  torso core (opening result) is split into shirt (top) / shorts (bottom) by ONE consistent
  waist cut, so the shorts colour is identical across every frame.
This keeps shorts consistent (the old dual-path component/cut logic was the flicker source)
AND lets contrasting sleeves (Arsenal red/white, Fulham white/black, Spurs white/navy) work."""
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage

FRAMES = [1, 3, 5, 7, 9, 11]            # idle + kick frames -> k0..k5
SRC = 'decomp/hires/DefineSprite_91'
_PAL = json.load(open('assets/teams.json', encoding='utf-8'))['palette']
def rgb(name):
    h = _PAL[name].lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def kit_mask(a):
    R,G,B,A = a[:,:,0].astype(int),a[:,:,1].astype(int),a[:,:,2].astype(int),a[:,:,3]
    return (A>40)&(R>80)&(G<80)&(B<80)&((R-G)>45)&((R-B)>45)

def segment(a):
    """Return boolean masks (shirt, shorts, sleeves, socks) for the all-red kit."""
    m = kit_mask(a)
    lbl, n = ndimage.label(m)
    z = np.zeros(a.shape[:2], bool)
    if n == 0:
        return z, z, z, z
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n+1))
    ys, xs = np.where(a[:,:,3] > 40); fh = ys.max()-ys.min(); fw = xs.max()-xs.min()+1
    big = [i for i in range(1, n+1) if sizes[i-1] > 0.004*fh*fw]
    if not big:
        return z, z, z, z
    body_id = max(big, key=lambda i: sizes[i-1])
    body = ndimage.binary_fill_holes(lbl == body_id)
    socks_m = z.copy()
    for i in big:
        if i != body_id:
            socks_m |= ndimage.binary_fill_holes(lbl == i)
    # true torso width = median largest contiguous run over the upper 60% of the body
    by = np.where(body.any(axis=1))[0]; by0, by1 = by.min(), by.max()
    widths = []
    for yy in range(by0, by0 + int(0.6*(by1-by0)) + 1):
        row = np.where(body[yy])[0]
        if len(row) == 0:
            continue
        runs = np.split(row, np.where(np.diff(row) > 1)[0] + 1)
        widths.append(max(len(r) for r in runs))
    Wt = int(np.median(widths)) if widths else 60
    r = int(np.clip(round(0.30*Wt), 10, 40))
    st = np.ones((3, 3), bool)
    # opening (erode then dilate) keeps the thick torso+shorts, drops the thin arms
    core = ndimage.binary_erosion(body, st, iterations=r)
    core = ndimage.binary_dilation(core, st, iterations=r) & body
    if not core.any():
        core = body.copy()
    sleeves_m = body & ~core
    cy = np.where(core.any(axis=1))[0]
    rows = np.arange(a.shape[0])[:, None]
    c0, c1 = cy.min(), cy.max()
    waist = c1 - 0.30*(c1 - c0)                 # shorts = bottom ~30% of the torso core
    shirt_m  = core & (rows < waist)
    shorts_m = core & (rows >= waist)
    # any stray red bits -> socks if below the body, else shirt
    leftover = m & ~(shirt_m | shorts_m | sleeves_m | socks_m)
    socks_m |= leftover & (rows > by1)
    shirt_m |= leftover & (rows <= by1)
    return shirt_m, shorts_m, sleeves_m, socks_m

def recolour(frame_path, shirt, shorts, socks, sleeves=None, pattern=None, stripe2=None):
    if sleeves is None:
        sleeves = shirt
    im = Image.open(frame_path).convert('RGBA')
    a = np.asarray(im).copy()
    shirt_m, shorts_m, sleeves_m, socks_m = segment(a)
    sc, sh, sl, so = rgb(shirt), rgb(shorts), rgb(sleeves), rgb(socks)
    for mask, col in ((shirt_m, sc), (shorts_m, sh), (sleeves_m, sl), (socks_m, so)):
        a[mask, 0], a[mask, 1], a[mask, 2] = col
    if pattern == 'stripes' and stripe2:                 # vertical stripes across shirt (+arms if same base)
        s2 = rgb(stripe2)
        area = shirt_m | (sleeves_m if sleeves == shirt else np.zeros_like(shirt_m))
        xs2 = np.where(area.any(axis=0))[0]
        if len(xs2):
            x0 = xs2.min(); bw = max(4, int((xs2.max()-x0+1)/11))
            xc = np.arange(a.shape[1])[None, :]
            sm = area & (((xc-x0)//bw) % 2 == 1)
            a[sm, 0], a[sm, 1], a[sm, 2] = s2
    return Image.fromarray(a)

def _debug_frame(frame_path):
    """Colour each region distinctly to eyeball the segmentation."""
    im = Image.open(frame_path).convert('RGBA')
    a = np.asarray(im).copy()
    shirt_m, shorts_m, sleeves_m, socks_m = segment(a)
    for mask, col in ((shirt_m,(220,40,40)), (shorts_m,(40,200,40)),
                      (sleeves_m,(60,90,255)), (socks_m,(245,220,40))):
        a[mask,0],a[mask,1],a[mask,2]=col
    return Image.fromarray(a)

def montage(team, cols, debug=False):
    if debug:
        ims = [_debug_frame('%s/%d.png'%(SRC,f)) for f in FRAMES]
        name = 'decomp/_striker_%s_seg.jpg'%team
    else:
        ims = [recolour('%s/%d.png'%(SRC,f), *cols) for f in FRAMES]
        name = 'decomp/_striker_%s.jpg'%team
    H=300; pad=8; W=sum(int(i.size[0]*H/i.size[1]) for i in ims)+pad*(len(ims)+1)
    c=Image.new('RGBA',(W,H),(50,50,55,255)); x=pad
    for i in ims:
        w=int(i.size[0]*H/i.size[1]); c.alpha_composite(i.resize((w,H)),(x,0)); x+=w+pad
    c.convert('RGB').save(name); print('montage', name)

if __name__ == '__main__':
    import sys
    teams = json.load(open('assets/teams.json', encoding='utf-8'))['teams']
    by = {t['slug']:t for t in teams}
    args = sys.argv[1:]
    debug = '--seg' in args
    args = [x for x in args if x != '--seg']
    for slug in (args or ['Arsenal','Chelsea']):
        t = by[slug]
        montage(slug, (t['shirt'], t['shorts'], t['socks'], t.get('sleeves'), t.get('pattern'), t.get('stripe2')), debug)
