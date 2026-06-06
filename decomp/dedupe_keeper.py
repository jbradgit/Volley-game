"""Deduplicate the keeper atlas: 104 timeline frames -> only the UNIQUE bitmaps.
Many dive frames are byte-identical (the held full-stretch pose repeats ~30x per side),
so we keep one copy of each unique image and remap every frame number to it. Same visuals,
much smaller download. Frame metadata (ox,oy,w,h) is preserved so the game is unchanged."""
import json, hashlib, os
from PIL import Image

A = "assets"
d = json.load(open(os.path.join(A, "keeper_atlas.json")))
F = d["frames"]
sheets = [Image.open(os.path.join(A, "keeper_atlas_%d.png" % i)).convert("RGBA") for i in range(d.get("sheets", 2))]

# hash every frame's bitmap; group identical
uniq = {}            # hash -> {"img":Image, "w":int, "h":int}
frame_hash = {}      # frame-number -> hash
for k, m in F.items():
    im = sheets[m["sheet"]].crop((m["x"], m["y"], m["x"] + m["w"], m["y"] + m["h"]))
    h = hashlib.md5(im.tobytes()).hexdigest()
    frame_hash[k] = h
    if h not in uniq:
        uniq[h] = {"img": im, "w": m["w"], "h": m["h"]}

# shelf-pack the unique bitmaps (tallest first) into a single sheet, width 2048
PAD, W = 2, 2048
order = sorted(uniq.items(), key=lambda t: -t[1]["h"])
pos = {}                       # hash -> (x, y)
x = y = PAD; rowH = 0; usedW = 0
for h, info in order:
    w, hh = info["w"], info["h"]
    if x + w + PAD > W:
        x = PAD; y += rowH + PAD; rowH = 0
    pos[h] = (x, y)
    x += w + PAD; rowH = max(rowH, hh); usedW = max(usedW, x)
sheetH = y + rowH + PAD
assert sheetH <= 2048, "unique frames don't fit one sheet (%dpx)" % sheetH

sheet = Image.new("RGBA", (usedW, sheetH), (0, 0, 0, 0))
for h, (px, py) in pos.items():
    sheet.paste(uniq[h]["img"], (px, py))
sheet.save(os.path.join(A, "keeper_atlas_0.png"))
# the game still loads a second sheet; keep a 1x1 placeholder so it doesn't 404
Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(os.path.join(A, "keeper_atlas_1.png"))

# remap every frame number to its unique rect (metadata preserved)
newF = {}
for k, m in F.items():
    px, py = pos[frame_hash[k]]
    newF[k] = {"sheet": 0, "x": px, "y": py, "w": m["w"], "h": m["h"], "ox": m["ox"], "oy": m["oy"]}
json.dump({"sheets": 1, "frames": newF, "anims": d["anims"]}, open(os.path.join(A, "keeper_atlas.json"), "w"))

before = os.path.getsize(os.path.join("decomp", "keeper_backup", "keeper_atlas_0.png")) + \
         os.path.getsize(os.path.join("decomp", "keeper_backup", "keeper_atlas_1.png"))
after = os.path.getsize(os.path.join(A, "keeper_atlas_0.png")) + os.path.getsize(os.path.join(A, "keeper_atlas_1.png"))
print("frames: %d  ->  unique: %d" % (len(F), len(uniq)))
print("atlas sheet: %dx%d" % (usedW, sheetH))
print("PNG bytes: %d  ->  %d  (%.0f%% smaller)" % (before, after, 100*(1-after/before)))
