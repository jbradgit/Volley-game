"""Generate the KEEPER atlas + BALL + SHADOW (striker/defender: see trace_sprites.py).

ISS-era volumetric figures: tapered limbs, shaped torso, 3-tone cel shading,
strict painter's order (far arm > far leg > near thigh > shorts > shirt over
shorts > near calf > near arm over torso > head). 100% clean-room.

REGION TAGS now carry PER-PART UV COORDINATES in the spare channels so kit
patterns run parallel to each part, evenly spaced and centre-symmetric:
  shirt   R=shade  G=u*88  B=v*88     (u across the part 0..1, v along it)
  shorts  G=shade  R=u*88  B=v*88
  socks   B=shade  R=u*88  G=v*88
  sleeves R=G=shade        B=u*88
  hair    R=B=shade        G=0
Shade levels (cel bands): lit 255 / mid 204 / dark 158. Skin/boots/gloves are
final colours with the same banding. Engine contract: docs/SPRITE_SPEC.md.

Run:  python3 artgen/gen_sprites.py
"""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sprites")
os.makedirs(OUT, exist_ok=True)
S = 2
LIT, MID, DRK = 255, 204, 158
SKIN  = (238, 190, 148)
BOOT  = (50, 48, 56)
GLOVE = (240, 240, 246)
OUTLN = (16, 13, 20)
SHADEF = {0: 1.0, 1: 0.80, 2: 0.62}          # cel band factors for final-colour parts

class Fig:
    def __init__(self, w_log, h_log):
        self.W, self.H = w_log * S, h_log * S
        self.px = np.zeros((self.H, self.W, 4), np.uint8)

    def _mask(self, pts):
        m = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in pts], fill=255)
        return np.asarray(m) > 0

    def _capsule_pts(self, p0, w0, p1, w1):
        ax, ay = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(ax, ay) or 1
        nx, ny = -ay / L, ax / L
        pts = []
        for t in range(7):                                    # end cap at p1
            a = math.atan2(ny, nx) - math.pi * t / 6
            pts.append((p1[0] + math.cos(a) * w1 / 2, p1[1] + math.sin(a) * w1 / 2))
        for t in range(7):                                    # cap at p0
            a = math.atan2(-ny, -nx) - math.pi * t / 6
            pts.append((p0[0] + math.cos(a) * w0 / 2, p0[1] + math.sin(a) * w0 / 2))
        return pts

    def _write(self, mask, region, u, v, far=0):
        """Write a part: tag channels (with uv) or final colour, cel-banded by u."""
        band = np.full(u.shape, 1, np.uint8)                  # mid
        band[u < 0.32] = 0                                    # lit (light from left)
        band[u > 0.74] = 2                                    # dark
        band = np.minimum(2, band + far)
        shade = np.choose(band, [LIT, MID, DRK]).astype(np.uint8)
        uu = np.clip(u * 88, 0, 88).astype(np.uint8)
        vv = np.clip(v * 88, 0, 88).astype(np.uint8)
        out = np.zeros((*u.shape, 4), np.uint8); out[..., 3] = 255
        if   region == "shirt":  out[..., 0], out[..., 1], out[..., 2] = shade, uu, vv
        elif region == "shorts": out[..., 1], out[..., 0], out[..., 2] = shade, uu, vv
        elif region == "socks":  out[..., 2], out[..., 0], out[..., 1] = shade, uu, vv
        elif region == "sleeve": out[..., 0] = out[..., 1] = shade; out[..., 2] = uu
        elif region == "hair":   out[..., 0] = out[..., 2] = shade
        else:                                                  # final colour
            col = {"skin": SKIN, "boot": BOOT, "glove": GLOVE, "eye": (30,26,30)}[region]
            for c in range(3):
                out[..., c] = np.choose(band, [min(255,int(col[c]*1.0)),
                                               int(col[c]*0.82), int(col[c]*0.64)])
        self.px[mask] = out[mask]

    def limb(self, p0, w0, p1, w1, region, far=0):
        """Tapered capsule. u = across (0 left edge), v = along p0->p1."""
        mask = self._mask(self._capsule_pts(p0, w0, p1, w1))
        ys, xs = np.nonzero(mask)
        if not len(xs): return
        ax, ay = p1[0] - p0[0], p1[1] - p0[1]
        L2 = ax * ax + ay * ay or 1
        pxl, pyl = xs / S - p0[0], ys / S - p0[1]
        v = np.clip((pxl * ax + pyl * ay) / L2, 0, 1)
        w = w0 + (w1 - w0) * v
        perp = (pxl * (-ay) + pyl * ax) / math.sqrt(L2)
        u = np.clip(perp / np.maximum(w, 0.1) + 0.5, 0, 1)
        U = np.zeros(mask.shape); V = np.zeros(mask.shape)
        U[ys, xs] = u; V[ys, xs] = v
        self._write(mask, region, U, V, far)

    def quad(self, pts, region, far=0, vspan=None):
        """Convex quad (TL,TR,BR,BL-ish): u across each row, v top->bottom."""
        mask = self._mask(pts)
        ys, xs = np.nonzero(mask)
        if not len(xs): return
        y0, y1 = ys.min(), ys.max()
        v = (ys - y0) / max(1, y1 - y0)
        # per-row horizontal span -> u centred per row
        U = np.zeros(mask.shape); V = np.zeros(mask.shape)
        for ry in np.unique(ys):
            sel = ys == ry
            rx = xs[sel]
            lo, hi = rx.min(), rx.max()
            U[ry, rx] = (rx - lo) / max(1, hi - lo)
        V[ys, xs] = v
        if vspan: V[ys, xs] = vspan[0] + v * (vspan[1] - vspan[0])
        self._write(mask, region, U, V, far)

    def disc(self, c, r, region, far=0):
        pts = [(c[0] + math.cos(a) * r, c[1] + math.sin(a) * r)
               for a in np.linspace(0, 2 * math.pi, 24)]
        mask = self._mask(pts)
        ys, xs = np.nonzero(mask)
        if not len(xs): return
        U = np.zeros(mask.shape); V = np.zeros(mask.shape)
        U[ys, xs] = np.clip((xs / S - (c[0] - r)) / (2 * r), 0, 1)
        V[ys, xs] = np.clip((ys / S - (c[1] - r)) / (2 * r), 0, 1)
        self._write(mask, region, U, V, far)

    def image(self):
        im = Image.fromarray(self.px)
        a = im.split()[3].filter(ImageFilter.MaxFilter(5))
        base = Image.new("RGBA", im.size, (0, 0, 0, 0))
        base.paste(Image.new("RGBA", im.size, OUTLN + (255,)), (0, 0), a)
        base.paste(im, (0, 0), im)
        return base

# ---------- shared body builder (painter's order enforced here) ----------
def hair_cap(f, c, r):
    """Rounded cap of hair over the top ~60%% of the head (tagged, recolours)."""
    hx, hy = c
    pts = [(hx + math.cos(a)*r*1.04, hy + math.sin(a)*r*1.04)
           for a in np.linspace(math.pi, 2*math.pi, 14)]      # top arc
    pts = [(hx - r*1.0, hy + r*0.10)] + pts + [(hx + r*1.0, hy + r*0.10)]
    mask = f._mask(pts)
    ys, xs = np.nonzero(mask)
    if not len(xs): return
    U = np.zeros(mask.shape); V = np.zeros(mask.shape)
    U[ys, xs] = np.clip((xs/2 - (hx - r))/(2*r), 0, 1)
    f._write(mask, "hair", U, V)

def draw_player(f, P, head_r=13, widths=None):
    """P: head,chest,hips + armFar/armNear [sh,el,hand] + legFar/legNear [hip,knee,foot]."""
    W = widths or dict(torso=(30, 22), thigh=(13, 9.5), calf=(9.5, 6.5),
                       uarm=(9, 7.5), farm=(7.5, 6), shorts_drop=14)
    def arm(A, far):
        f.limb(A[0], W["uarm"][0], A[1], W["uarm"][1], "sleeve", far)
        f.limb(A[1], W["farm"][0], A[2], W["farm"][1], "skin", far)
        f.disc(A[2], 3.4, "skin", far)
    def leg_lower(Lg, far):
        knee, foot = Lg[1], Lg[2]
        sockTop = (knee[0] + (foot[0]-knee[0])*0.30, knee[1] + (foot[1]-knee[1])*0.30)
        bootTop = (knee[0] + (foot[0]-knee[0])*0.82, knee[1] + (foot[1]-knee[1])*0.82)
        f.limb(knee, W["calf"][0], sockTop, W["calf"][0]*0.95, "skin", far)
        f.limb(sockTop, W["calf"][0], bootTop, W["calf"][1], "socks", far)
        f.limb(bootTop, W["calf"][1]+1.5, foot, W["calf"][1]+1.5, "boot", far)
    def thigh(Lg, far):
        f.limb(Lg[0], W["thigh"][0], Lg[1], W["thigh"][1], "skin", far)
    # 1 far arm  2 far leg  3 near thigh
    arm(P["armFar"], 1)
    thigh(P["legFar"], 1); leg_lower(P["legFar"], 1)
    thigh(P["legNear"], 0)
    # 4 shorts (one piece over both thigh tops)
    hips = P["hips"]
    hw = W["torso"][1]
    f.quad([(hips[0]-hw*0.62, hips[1]-4), (hips[0]+hw*0.62, hips[1]-4),
            (hips[0]+hw*0.70, hips[1]+W["shorts_drop"]), (hips[0]-hw*0.70, hips[1]+W["shorts_drop"])],
           "shorts")
    # shorts cuff: forced-dark strip so same-colour kits still read as two garments
    f.quad([(hips[0]-hw*0.70, hips[1]+W["shorts_drop"]-2.5), (hips[0]+hw*0.70, hips[1]+W["shorts_drop"]-2.5),
            (hips[0]+hw*0.70, hips[1]+W["shorts_drop"]), (hips[0]-hw*0.70, hips[1]+W["shorts_drop"])], "shorts", far=2)
    # 5 shirt OVER the shorts waist; shoulders wider than waist + dark hem line
    chest, sw, ww = P["chest"], W["torso"][0], W["torso"][1]
    f.quad([(chest[0]-sw/2, chest[1]-6), (chest[0]+sw/2, chest[1]-6),
            (hips[0]+ww/2, hips[1]+3), (hips[0]-ww/2, hips[1]+3)], "shirt")
    f.quad([(hips[0]-ww/2, hips[1]+0.5), (hips[0]+ww/2, hips[1]+0.5),
            (hips[0]+ww/2, hips[1]+3), (hips[0]-ww/2, hips[1]+3)], "shirt", far=2)
    # 6 near calf/sock/boot over the shorts hem
    leg_lower(P["legNear"], 0)
    # 7 near arm over the torso
    arm(P["armNear"], 0)
    # 8 neck + head + hair cap + eye
    f.limb((P["head"][0], P["head"][1]+head_r*0.6), 7,
           (chest[0], chest[1]-4), 8, "skin")
    f.disc(P["head"], head_r, "skin")
    hair_cap(f, P["head"], head_r)
    hx, hy = P["head"]
    if P.get("front"):
        f.disc((hx-head_r*0.38, hy+head_r*0.10), 1.3, "eye")
        f.disc((hx+head_r*0.38, hy+head_r*0.10), 1.3, "eye")
    else:
        f.disc((hx-head_r*0.42, hy+head_r*0.12), 1.4, "eye")

# =========================================================================
# STRIKER + DEFENDER are now produced by artgen/trace_sprites.py (traced from the
# original frames for silhouette/animation fidelity). This file keeps the
# procedural KEEPER (approved look + verified save extents) and BALL/SHADOW.
# =========================================================================

# =========================================================================
# KEEPER — unified 596x263, feet (300,197). Slightly slimmer body (owner call)
# but dive/idle/catch EXTENTS preserved so the save pixel-test is unchanged.
# =========================================================================
def lerp_pt(p, q, t): return (p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t)
def kf_interp(kfs, t):
    for i in range(len(kfs)-1):
        t0, p0 = kfs[i]; t1, p1 = kfs[i+1]
        if t0 <= t <= t1:
            ff = 0 if t1 == t0 else (t-t0)/(t1-t0)
            return {k: [lerp_pt(a,b,ff) for a,b in zip(p0[k],p1[k])] if isinstance(p0[k],list)
                    else lerp_pt(p0[k],p1[k],ff) for k in p0}
    return kfs[-1][1]

def draw_keeper(f, P):
    KW = dict(torso=(21,16), thigh=(9,7), calf=(7,5), uarm=(7,6), farm=(6,5), shorts_drop=10)
    def arm(A, far):
        f.limb(A[0], KW["uarm"][0], A[1], KW["uarm"][1], "sleeve", far)
        f.limb(A[1], KW["farm"][0], A[2], KW["farm"][1], "sleeve", far)   # long sleeves
        f.disc(A[2], 4.6, "glove", far)
    def leg(Lg, far):
        f.limb(Lg[0], KW["thigh"][0], Lg[1], KW["thigh"][1], "shorts", far)   # keeper: long shorts look
        f.limb(Lg[1], KW["calf"][0], lerp_pt(Lg[1], Lg[2], 0.85), KW["calf"][1], "socks", far)
        f.limb(lerp_pt(Lg[1], Lg[2], 0.8), KW["calf"][1]+1.2, Lg[2], KW["calf"][1]+1.2, "boot", far)
    arm(P["armFar"], 1); leg(P["legFar"], 1)
    hips, chest = P["hips"], P["chest"]
    f.quad([(chest[0]-KW["torso"][0]/2, chest[1]-5), (chest[0]+KW["torso"][0]/2, chest[1]-5),
            (hips[0]+KW["torso"][1]/2, hips[1]+5), (hips[0]-KW["torso"][1]/2, hips[1]+5)], "shirt")
    leg(P["legNear"], 0); arm(P["armNear"], 0)
    f.limb((P["head"][0], P["head"][1]+5), 6, (chest[0], chest[1]-3), 7, "skin")
    f.disc(P["head"], 8.5, "skin")
    hair_cap(f, P["head"], 8.5)
    hx, hy = P["head"]
    f.disc((hx-3, hy+1.2), 1.1, "eye"); f.disc((hx+3, hy+1.2), 1.1, "eye")

K_IDLE = dict(head=(300,80), chest=(300,104), hips=(300,134),
  armFar=[(309,98),(325,116),(330,134)], armNear=[(291,98),(275,116),(270,134)],
  legFar=[(306,138),(310,166),(312,193)], legNear=[(294,138),(290,166),(288,193)])
K_DIVE = [
 (0.00, dict(head=(296,84), chest=(297,106), hips=(299,138),
   armFar=[(306,100),(320,118),(326,132)], armNear=[(288,100),(272,114),(264,126)],
   legFar=[(305,140),(308,168),(310,193)], legNear=[(293,140),(288,168),(286,193)])),
 (0.22, dict(head=(272,108), chest=(278,124), hips=(290,150),
   armFar=[(288,118),(272,120),(256,118)], armNear=[(268,118),(248,114),(232,108)],
   legFar=[(296,152),(306,172),(312,193)], legNear=[(284,152),(282,176),(284,195)])),
 (0.55, dict(head=(170,138), chest=(190,146), hips=(222,156),
   armFar=[(180,140),(158,138),(140,134)], armNear=[(174,148),(150,148),(130,146)],
   legFar=[(228,158),(254,162),(280,168)], legNear=[(224,164),(252,172),(278,182)])),
 (0.85, dict(head=(58,182), chest=(82,184), hips=(118,188),
   armFar=[(72,176),(48,172),(28,168)], armNear=[(70,188),(44,188),(22,186)],
   legFar=[(126,186),(152,186),(176,184)], legNear=[(122,194),(150,196),(176,198)])),
 (1.00, dict(head=(56,188), chest=(80,190), hips=(116,192),
   armFar=[(70,180),(44,176),(22,172)], armNear=[(68,194),(42,194),(18,192)],
   legFar=[(124,190),(152,190),(176,188)], legNear=[(120,198),(150,200),(176,202)])),
]
K_CATCH = {
 323: dict(head=(300,116), chest=(300,138), hips=(300,160),
   armFar=[(309,132),(314,156),(308,174)], armNear=[(291,132),(286,156),(292,174)],
   legFar=[(306,162),(312,180),(310,193)], legNear=[(294,162),(288,180),(290,193)]),
 328: dict(head=(300,96), chest=(300,118), hips=(300,144),
   armFar=[(309,112),(320,122),(308,124)], armNear=[(291,112),(280,122),(292,124)],
   legFar=[(306,146),(310,170),(312,194)], legNear=[(294,146),(290,170),(288,194)]),
 354: dict(head=(300,84), chest=(300,108), hips=(300,136),
   armFar=[(309,100),(317,78),(314,62)], armNear=[(291,100),(283,78),(286,62)],
   legFar=[(306,138),(310,166),(312,192)], legNear=[(294,138),(290,166),(288,192)]),
}
def render_keeper(pose, mirror=False):
    f = Fig(596, 263)
    draw_keeper(f, pose)
    im = f.image()
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.transform(im.size, Image.AFFINE, (1, 0, -4, 0, 1, 0))
    return im

frames = {1: render_keeper(K_IDLE)}
for i in range(50):
    pose = kf_interp(K_DIVE, i / 49)
    frames[50 + i] = render_keeper(pose)
    frames[100 + i] = render_keeper(pose, mirror=True)
for fn, pose in K_CATCH.items():
    frames[fn] = render_keeper(pose)

packed = []
for fn, im in frames.items():
    bb = im.getbbox()
    packed.append((fn, im.crop(bb), bb))
packed.sort(key=lambda x: -x[1].height)
SHEET_W = 2048; x = y = rowh = 0; places = []
for fn, im, bb in packed:
    if x + im.width > SHEET_W: x = 0; y += rowh + 2; rowh = 0
    places.append((fn, im, bb, x, y)); x += im.width + 2; rowh = max(rowh, im.height)
sheet = Image.new("RGBA", (SHEET_W, y + rowh + 2), (0, 0, 0, 0))
man = {}
for fn, im, bb, px_, py_ in places:
    sheet.paste(im, (px_, py_))
    man[str(fn)] = dict(sheet=0, x=px_, y=py_, w=im.width, h=im.height, ox=bb[0]/S, oy=bb[1]/S)
sheet.save(os.path.join(OUT, "keeper_atlas.png"), optimize=True)
json.dump(dict(frames=man), open(os.path.join(OUT, "keeper_atlas.json"), "w"))
def ext(fr):
    fr2 = man[str(fr)]; return (round(fr2["ox"]), round(fr2["ox"]+fr2["w"]/2), round(fr2["oy"]), round(fr2["oy"]+fr2["h"]/2))
print("keeper atlas:", sheet.size, len(man), "frames")
print("  idle", ext(1), "target(267,334,69,198) · dv99", ext(99), "target(5,178,153,211) · high", ext(354), "target(263,330,53,196)")

# =========================================================================
# BALL + SHADOW (unchanged geometry)
# =========================================================================
B = 3
im = Image.new("RGBA", (41*B, 41*B), (0,0,0,0)); d = ImageDraw.Draw(im)
cx, cy, r = 20*B + B/2, 20*B + B/2, 19.5*B
d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(244,244,248))
TURN = 2*math.pi/5; A0 = -math.pi/2
def pent(px_, py_, pr, rot):
    return [(px_+math.cos(rot+i*TURN)*pr, py_+math.sin(rot+i*TURN)*pr) for i in range(5)]
d.polygon(pent(cx, cy, r*0.36, A0), fill=(24,24,28))
for i in range(5):
    a = A0 + i*TURN
    d.polygon(pent(cx+math.cos(a)*r*0.78, cy+math.sin(a)*r*0.78, r*0.30, a+math.pi), fill=(24,24,28))
sh = Image.new("L", im.size, 0)
ImageDraw.Draw(sh).ellipse([cx-r, cy-r, cx+r, cy+r], fill=70)
ImageDraw.Draw(sh).ellipse([cx-r-6*B, cy-r-6*B, cx+r-2*B, cy+r-2*B], fill=0)
im.paste(Image.new("RGBA", im.size, (10,10,16,255)), (0,0),
         Image.composite(sh, Image.new("L", im.size, 0), im.split()[3]))
ImageDraw.Draw(im).ellipse([cx-r, cy-r, cx+r, cy+r], outline=(18,18,22), width=B)
im.save(os.path.join(OUT, "ball.png"), optimize=True)
sh = Image.new("RGBA", (28*B, 11*B), (0,0,0,0))
ImageDraw.Draw(sh).ellipse([0,0,28*B-1,11*B-1], fill=(8,12,8,255))
sh.save(os.path.join(OUT, "shadow.png"), optimize=True)
print("ball + shadow written")
