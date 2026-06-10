"""Compositor mock of the in-match frame using the NEW stadium layers.

Replicates index.html's draw order and coordinates exactly (L0 backdrop ->
L1 hoardings -> L2 procedural goal -> keeper/defenders/ball/striker) so layer
alignment can be validated without a browser. NOT a screenshot — the goal mesh
here is a PIL port of drawGoal() with the same constants.

Run:  python3 artgen/preview_mock.py   -> /tmp/mock_match.png, /tmp/mock_overlay.png
"""
import os, json
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = 2
VW, SH, OX = 924, 520, 187
LPOST, RPOST, BARH, GOAL_Y = 135, 430, 105, 163

img = Image.new("RGB", (VW * S, SH * S), (4, 6, 10))
d = ImageDraw.Draw(img, "RGBA")
fx = lambda x: (x + OX) * S
fy = lambda y: y * S

# L0 backdrop
bd = Image.open(os.path.join(ROOT, "assets/stadium/backdrop.png")).resize((VW * S, 400 * S))
img.paste(bd, (0, 0))

# L1 hoardings — same board order the game would pick (just take them in manifest order here)
ads = json.load(open(os.path.join(ROOT, "assets/boards/boards.json")))["boards"]
for i in range(7):
    b = ads[i % len(ads)]
    im = Image.open(os.path.join(ROOT, "assets/boards", b["img"])).resize((132 * S, 34 * S))
    img.paste(im, (i * 132 * S, 104 * S))

# L2 goal (PIL port of drawGoal(), rest state)
L, R, T, B = LPOST, RPOST, GOAL_Y - BARH, GOAL_Y
bl, br, bt, bb = L + 24, R - 24, T + 12, B - 3
MESH = (235, 238, 240, 82)
for x in range(bl, br + 1, 9):                                   # back panel mesh
    d.line([fx(x), fy(bt), fx(x), fy(bb)], fill=MESH, width=1)
for y in range(bt, bb + 1, 9):
    d.line([fx(bl), fy(y), fx(br), fy(y)], fill=MESH, width=1)
x = L
while x <= R:                                                     # roof panel
    k = (x - L) / (R - L)
    d.line([fx(x), fy(T), fx(bl + (br - bl) * k), fy(bt)], fill=MESH, width=1)
    x += 14
y = T
while y <= B:                                                     # side panels
    k = (y - T) / (B - T)
    d.line([fx(L), fy(y), fx(bl), fy(bt + (bb - bt) * k)], fill=MESH, width=1)
    d.line([fx(R), fy(y), fx(br), fy(bt + (bb - bt) * k)], fill=MESH, width=1)
    y += 14
d.rectangle([fx(bl), fy(bt), fx(br), fy(bb)], outline=(230, 232, 235, 128), width=2)
d.rectangle([fx(L - 3.5), fy(T - 3.5), fx(R + 3.5), fy(T + 3.5)], fill=(241, 243, 244))   # bar
d.rectangle([fx(L - 3.5), fy(T - 3.5), fx(L + 3.5), fy(B)], fill=(241, 243, 244))         # posts
d.rectangle([fx(R - 3.5), fy(T - 3.5), fx(R + 3.5), fy(B)], fill=(241, 243, 244))
d.rectangle([fx(L + 1.5), fy(T + 3.5), fx(L + 3.5), fy(B)], fill=(120, 128, 134, 128))
d.rectangle([fx(R + 1.5), fy(T + 3.5), fx(R + 3.5), fy(B)], fill=(120, 128, 134, 128))
d.rectangle([fx(L + 3.5), fy(T + 1.5), fx(R - 3.5), fy(T + 3.5)], fill=(120, 128, 134, 128))

def paste_sprite(path, x, y, w, h):
    sp = Image.open(os.path.join(ROOT, path)).convert("RGBA").resize((int(w * S), int(h * S)))
    img.paste(sp, (int(x * S), int(y * S)), sp)

# keeper (atlas frame 1) at feet anchor (263,163), scale 0.753/0.777
km = json.load(open(os.path.join(ROOT, "assets/keeper_atlas.json")))["frames"]["1"]
sheet = Image.open(os.path.join(ROOT, f"assets/keeper_atlas_{km['sheet']}.png")).convert("RGBA")
fr = sheet.crop((km["x"], km["y"], km["x"] + km["w"], km["y"] + km["h"]))
kw, kh = km["w"] / 2 * 0.7530, km["h"] / 2 * 0.7767
kx = 263 + OX + (km["ox"] - 300) * 0.7530
ky = 163 + (km["oy"] - 197) * 0.7767
fr = fr.resize((int(kw * S), int(kh * S)))
img.paste(fr, (int(kx * S), int(ky * S)), fr)

# defenders (pre-baked kit PNG stands in for the live recolour)
for ox_, oy_, sx_, sy_ in [(117.95, 210.25, 1.0, 1.0), (27.6, 163.35, .8982, .896), (471.15, 157.75, .8234, .8264)]:
    paste_sprite("assets/defender_AstonVilla.png", ox_ - 33.4 * sx_ + OX, oy_ - 57.5 * sy_, 67 * sx_, 115 * sy_)

# ball mid-flight at (300, 250, z=40) and striker at start (450,300)
ys = (10 + 90 * 250 / 325) * 0.8 / 100
paste_sprite("assets/ball.png", 300 - 19.6 * ys + OX, (250 - 40) - 34.1 * ys, 41 * ys, 41 * ys)
paste_sprite("assets/striker_Liverpool_k0.png", 450 - 101.2 + OX, 300 - 126.5, 131, 191)

img.save("/tmp/mock_match.png")
tpl = Image.open(os.path.join(ROOT, "docs/stadium_grid_template.png")).convert("RGB")
Image.blend(img.convert("RGB"), tpl, 0.35).save("/tmp/mock_overlay.png")
print("wrote /tmp/mock_match.png + /tmp/mock_overlay.png")
