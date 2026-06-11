"""Generate the ORIGINAL sprite set — striker, defender, keeper, ball, shadow.

Completely clean-room art (no pixels from the source game) drawn from parametric
skeleton poses in the project's 16-bit style, but geometry-faithful to the engine:
registration origins, sprite boxes, kick-contact pose (foot through origin+15,
z 0..40) and keeper silhouette extents (the pixel hit-test!) all match the
documented values in docs/SPRITE_SPEC.md.

REGION TAGS (pure hues, brightness = shading) make every body recolourable live:
  shirt=red  sleeves=yellow  shorts=green  socks=blue  hair=magenta
  skin / boots / gloves / outline are final colours and pass through.

Outputs:
  assets/sprites/striker_k0..k5.png   131x191 logical @2x, origin (101.2,126.5)
  assets/sprites/defender.png          67x115 logical @2x, origin (33.4,57.5)
  assets/sprites/keeper_atlas.png + keeper_atlas.json  (frames 1, 50-99, 100-149, 323/328/354)
  assets/sprites/ball.png @3x (disc centre 20,20 of 41 box) + shadow.png

Run:  python3 artgen/gen_sprites.py
"""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sprites")
os.makedirs(OUT, exist_ok=True)
S = 2                                # render scale (2x logical)

# ---- palette: tags (recolourable) + finals ----
SHIRT  = ((255, 0, 0),   (172, 0, 0))
SLEEVE = ((255, 255, 0), (172, 172, 0))
SHORT  = ((0, 255, 0),   (0, 172, 0))
SOCK   = ((0, 0, 255),   (0, 0, 172))
HAIR   = ((255, 0, 255), (172, 0, 172))
SKIN   = ((236, 192, 152), (202, 158, 118))
BOOT   = ((48, 46, 54),  (32, 30, 38))
GLOVE  = ((242, 242, 246), (200, 200, 210))
OUTLN  = (16, 13, 20)

def canvas(w_log, h_log):
    im = Image.new("RGBA", (w_log * S, h_log * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)

def limb(d, p0, p1, w, col):
    """Capsule limb between logical points, w = logical thickness."""
    x0, y0 = p0[0] * S, p0[1] * S; x1, y1 = p1[0] * S, p1[1] * S; r = w * S / 2
    d.line([x0, y0, x1, y1], fill=col, width=int(w * S))
    for x, y in ((x0, y0), (x1, y1)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

def poly(d, pts, col):
    d.polygon([(x * S, y * S) for x, y in pts], fill=col)

def circle(d, c, r, col):
    x, y = c[0] * S, c[1] * S; r *= S
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)

def head(d, c, r, hair_style="cap", eye_dx=-0.35):
    circle(d, c, r, SKIN[0])
    # hair: tagged cap so it recolours per match
    x, y = c
    if hair_style == "cap":
        d.pieslice([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], 180, 360, fill=HAIR[0])
        d.rectangle([(x - r) * S, (y - r * 0.45) * S, (x + r) * S, (y - r * 0.15) * S], fill=HAIR[1])
    # face: simple dark eye on the facing side
    ex = x + eye_dx * r
    d.rectangle([ex * S - S, (y - r * 0.1) * S, ex * S + S, (y + 0.15 * r) * S], fill=(40, 30, 30))

def finish(im):
    """Dark outline under the figure (16-bit cel look)."""
    a = im.split()[3]
    dil = a.filter(ImageFilter.MaxFilter(5))
    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", im.size, OUTLN + (255,)), (0, 0), dil)
    base.paste(im, (0, 0), im)
    return base

# =========================================================================
# STRIKER — 131x191, origin (101.2,126.5); faces LEFT; kick foot swings
# through canvas x≈116, y≈95..122 (= field origin+15, z 0..40: the contact zone)
# =========================================================================
def leg(d, L, shade):
    """hip->knee->foot with shorts-coloured thigh, SKIN knee gap, sock, boot."""
    hip, knee, foot = L
    mid = lerp_pt2(hip, knee, 0.55)
    sockTop = lerp_pt2(knee, foot, 0.32)
    limb(d, hip, mid, 11, SHORT[shade])
    limb(d, mid, sockTop, 8, SKIN[shade])
    limb(d, sockTop, lerp_pt2(knee, foot, 0.88), 8, SOCK[shade])
    limb(d, lerp_pt2(knee, foot, 0.86), foot, 8, BOOT[shade])
def lerp_pt2(p, q, t): return (p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t)

def striker_pose(d, P):
    farL, nearL = P["legFar"], P["legNear"]     # [(hip),(knee),(foot)]
    farA, nearA = P["armFar"], P["armNear"]     # [(shoulder),(elbow),(hand)]
    hips, chest = P["hips"], P["chest"]
    # far limbs (shaded)
    limb(d, farA[0], farA[1], 8, SLEEVE[1]); limb(d, farA[1], farA[2], 7, SKIN[1])
    leg(d, farL, 1)
    # torso (shirt) + shade band
    w = P.get("torsoW", 22)
    poly(d, [(chest[0]-w*0.55, chest[1]), (chest[0]+w*0.55, chest[1]),
             (hips[0]+w*0.45, hips[1]), (hips[0]-w*0.45, hips[1])], SHIRT[0])
    poly(d, [(chest[0]+w*0.15, chest[1]), (chest[0]+w*0.55, chest[1]),
             (hips[0]+w*0.45, hips[1]), (hips[0]+w*0.10, hips[1])], SHIRT[1])
    # shorts block
    poly(d, [(hips[0]-w*0.5, hips[1]-2), (hips[0]+w*0.5, hips[1]-2),
             (hips[0]+w*0.55, hips[1]+12), (hips[0]-w*0.55, hips[1]+12)], SHORT[0])
    # near leg (lit)
    leg(d, nearL, 0)
    # near arm (lit)
    limb(d, nearA[0], nearA[1], 8, SLEEVE[0]); limb(d, nearA[1], nearA[2], 7, SKIN[0])
    head(d, P["head"], 14, eye_dx=-0.4)

STRIKER_POSES = {
 0: dict(head=(92,50), chest=(92,68), hips=(94,120),                       # idle, ready stance
        armFar=[(100,74),(108,96),(104,114)], armNear=[(84,74),(74,95),(70,112)],
        legFar=[(100,122),(104,150),(106,186)], legNear=[(88,122),(82,151),(78,186)]),
 1: dict(head=(88,52), chest=(90,70), hips=(94,121),                       # windup: kick leg back
        armFar=[(98,76),(112,90),(120,100)], armNear=[(82,76),(70,90),(62,100)],
        legFar=[(88,123),(80,150),(76,186)], legNear=[(100,123),(116,146),(126,166)]),
 2: dict(head=(90,52), chest=(92,70), hips=(94,120),                       # swing down
        armFar=[(100,76),(112,94),(118,108)], armNear=[(84,76),(70,92),(62,106)],
        legFar=[(88,122),(82,150),(78,186)], legNear=[(100,122),(110,156),(114,184)]),
 3: dict(head=(86,56), chest=(89,74), hips=(92,122),                       # STRIKE: foot at (117,108)
        armFar=[(97,80),(112,92),(122,98)], armNear=[(81,80),(66,90),(56,98)],
        legFar=[(86,124),(78,152),(72,186)], legNear=[(98,122),(110,110),(119,103)]),
 4: dict(head=(84,58), chest=(88,76), hips=(92,122),                       # follow-through high
        armFar=[(96,82),(112,90),(122,94)], armNear=[(80,82),(66,88),(56,94)],
        legFar=[(86,124),(78,152),(72,186)], legNear=[(98,120),(100,94),(90,78)]),
 5: dict(head=(88,52), chest=(91,70), hips=(93,120),                       # recover
        armFar=[(99,76),(108,96),(104,112)], armNear=[(83,76),(72,94),(68,110)],
        legFar=[(87,122),(81,150),(77,186)], legNear=[(99,122),(104,148),(102,170)]),
}
for k, P in STRIKER_POSES.items():
    im, d = canvas(131, 191)
    striker_pose(d, P)
    finish(im).save(os.path.join(OUT, f"striker_k{k}.png"), optimize=True)
print("striker k0..k5 written")

# =========================================================================
# DEFENDER — 67x115, origin (33.4,57.5); front-facing guard stance
# =========================================================================
im, d = canvas(67, 115)
limb(d, (22, 38), (12, 56), 6, SLEEVE[1]); limb(d, (12, 56), (10, 68), 5, SKIN[1])   # arms
limb(d, (45, 38), (55, 56), 6, SLEEVE[0]); limb(d, (55, 56), (57, 68), 5, SKIN[0])
poly(d, [(22, 33), (45, 33), (43, 66), (24, 66)], SHIRT[0])                          # torso
poly(d, [(37, 33), (45, 33), (43, 66), (37, 66)], SHIRT[1])
poly(d, [(23, 64), (44, 64), (45, 80), (22, 80)], SHORT[0])                          # shorts
poly(d, [(36, 64), (44, 64), (45, 80), (36, 80)], SHORT[1])
limb(d, (27, 80), (26, 96), 7, SKIN[0]); limb(d, (40, 80), (41, 96), 7, SKIN[1])     # knees
limb(d, (26, 96), (25, 108), 7, SOCK[0]); limb(d, (41, 96), (42, 108), 7, SOCK[1])   # socks
limb(d, (25, 110), (21, 112), 6, BOOT[0]); limb(d, (42, 110), (46, 112), 6, BOOT[1]) # boots
head(d, (33, 19), 10, eye_dx=0)
finish(im).save(os.path.join(OUT, "defender.png"), optimize=True)
print("defender written")

# =========================================================================
# KEEPER — unified space 596x263 (logical), feet anchor (300,197).
# Frames: 1 idle · 50-99 dive_left · 100-149 dive_right · 323/328/354 catches.
# Extents matched to the original's used frames (the save hit-test depends on them):
#   idle x267-334 y69-198 · full dive x≈5-178 y153-211 (mirrored right) · high catch top y≈54
# =========================================================================
def lerp(a, b, t): return a + (b - a) * t
def lerp_pt(p, q, t): return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))
def kf_interp(kfs, t):
    """kfs = [(t, pose_dict)] sorted; lerp every joint."""
    for i in range(len(kfs) - 1):
        t0, p0 = kfs[i]; t1, p1 = kfs[i + 1]
        if t0 <= t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return {k: [lerp_pt(a, b, f) for a, b in zip(p0[k], p1[k])] if isinstance(p0[k], list)
                    else lerp_pt(p0[k], p1[k], f) for k in p0}
    return kfs[-1][1]

def keeper_draw(d, P):
    armF, armN = P["armFar"], P["armNear"]
    legF, legN = P["legFar"], P["legNear"]
    hips, chest = P["hips"], P["chest"]
    limb(d, armF[0], armF[1], 7, SLEEVE[1]); limb(d, armF[1], armF[2], 6, SLEEVE[1])
    circle(d, armF[2], 4.5, GLOVE[1])
    limb(d, legF[0], legF[1], 8, SHORT[1]); limb(d, legF[1], legF[2], 6, SOCK[1])
    circle(d, legF[2], 3.5, BOOT[1])
    poly(d, [(chest[0]-10, chest[1]-8), (chest[0]+10, chest[1]-8),
             (hips[0]+9, hips[1]+4), (hips[0]-9, hips[1]+4)], SHIRT[0])
    poly(d, [(chest[0]+2, chest[1]-8), (chest[0]+10, chest[1]-8),
             (hips[0]+9, hips[1]+4), (hips[0]+2, hips[1]+4)], SHIRT[1])
    limb(d, legN[0], legN[1], 8, SHORT[0]); limb(d, legN[1], legN[2], 6, SOCK[0])
    circle(d, legN[2], 3.5, BOOT[0])
    limb(d, armN[0], armN[1], 7, SLEEVE[0]); limb(d, armN[1], armN[2], 6, SLEEVE[0])
    circle(d, armN[2], 4.5, GLOVE[0])
    head(d, P["head"], 9, eye_dx=0)

K_IDLE = dict(head=(300,80), chest=(300,104), hips=(300,134),
  armFar=[(310,98),(326,116),(330,134)], armNear=[(290,98),(274,116),(270,134)],
  legFar=[(306,136),(310,166),(312,194)], legNear=[(294,136),(290,166),(288,194)])
# dive-left keyframes (t 0..1 over frames 50..99)
K_DIVE = [
 (0.00, dict(head=(296,84), chest=(297,106), hips=(299,138),
   armFar=[(307,100),(320,118),(326,132)], armNear=[(287,100),(272,114),(264,126)],
   legFar=[(305,140),(308,168),(310,194)], legNear=[(293,140),(288,168),(286,194)])),
 (0.22, dict(head=(272,108), chest=(278,124), hips=(290,150),
   armFar=[(288,118),(272,120),(256,118)], armNear=[(268,118),(248,114),(232,108)],
   legFar=[(296,152),(306,172),(312,194)], legNear=[(284,152),(282,176),(284,196)])),
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
 323: dict(head=(300,116), chest=(300,138), hips=(300,160),                 # low: crouched, hands down
   armFar=[(310,132),(314,156),(308,174)], armNear=[(290,132),(286,156),(292,174)],
   legFar=[(306,162),(312,180),(310,194)], legNear=[(294,162),(288,180),(290,194)]),
 328: dict(head=(300,96), chest=(300,118), hips=(300,144),                  # mid: chest catch
   armFar=[(310,112),(320,122),(308,124)], armNear=[(290,112),(280,122),(292,124)],
   legFar=[(306,146),(310,170),(312,196)], legNear=[(294,146),(290,170),(288,196)]),
 354: dict(head=(300,84), chest=(300,108), hips=(300,136),                  # high: arms above the bar
   armFar=[(310,100),(318,78),(314,62)], armNear=[(290,100),(282,78),(286,62)],
   legFar=[(306,138),(310,166),(312,192)], legNear=[(294,138),(290,166),(288,192)]),
}

def render_keeper(pose, mirror=False):
    im, d = canvas(596, 263)
    keeper_draw(d, pose)
    im = finish(im)
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)   # 596-wide: mirrors around x=298... fix to 300:
        im = im.transform(im.size, Image.AFFINE, (1, 0, -4, 0, 1, 0))   # shift +4px(2x) so feet stay at 300
    return im

frames = {}
frames[1] = render_keeper(K_IDLE)
for i in range(50):
    pose = kf_interp(K_DIVE, i / 49)
    frames[50 + i] = render_keeper(pose)
    frames[100 + i] = render_keeper(pose, mirror=True)
for fn, pose in K_CATCH.items():
    frames[fn] = render_keeper(pose)

# trim + pack into one sheet
packed, rects = [], {}
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
for fn, im, bb, px, py in places:
    sheet.paste(im, (px, py))
    man[str(fn)] = dict(sheet=0, x=px, y=py, w=im.width, h=im.height,
                        ox=bb[0] / S, oy=bb[1] / S)      # ox/oy in unified LOGICAL units
sheet.save(os.path.join(OUT, "keeper_atlas.png"), optimize=True)
json.dump(dict(frames=man), open(os.path.join(OUT, "keeper_atlas.json"), "w"))
print("keeper atlas:", sheet.size, len(man), "frames")

# =========================================================================
# BALL (disc centre 20,20 of the 41 box, @3x) + SHADOW (28x11 ellipse)
# =========================================================================
B = 3
im = Image.new("RGBA", (41 * B, 41 * B), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
cx, cy, r = 20 * B + B/2, 20 * B + B/2, 19.5 * B
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(244, 244, 248))
TURN = 2 * math.pi / 5; A0 = -math.pi / 2
def pent(px, py, pr, rot):
    return [(px + math.cos(rot + i * TURN) * pr, py + math.sin(rot + i * TURN) * pr) for i in range(5)]
d.polygon(pent(cx, cy, r * 0.36, A0), fill=(24, 24, 28))
for i in range(5):
    a = A0 + i * TURN
    d.polygon(pent(cx + math.cos(a) * r * 0.78, cy + math.sin(a) * r * 0.78, r * 0.30, a + math.pi), fill=(24, 24, 28))
sh = Image.new("L", im.size, 0)                                        # bottom-right shade
ImageDraw.Draw(sh).ellipse([cx - r, cy - r, cx + r, cy + r], fill=70)
ImageDraw.Draw(sh).ellipse([cx - r - 6*B, cy - r - 6*B, cx + r - 2*B, cy + r - 2*B], fill=0)
im.paste(Image.new("RGBA", im.size, (10, 10, 16, 255)), (0, 0),
         Image.composite(sh, Image.new("L", im.size, 0), im.split()[3]))
dd = ImageDraw.Draw(im)
dd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(18, 18, 22), width=B)
im.save(os.path.join(OUT, "ball.png"), optimize=True)
sh = Image.new("RGBA", (28 * B, 11 * B), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse([0, 0, 28 * B - 1, 11 * B - 1], fill=(8, 12, 8, 255))
sh.save(os.path.join(OUT, "shadow.png"), optimize=True)
print("ball + shadow written")
