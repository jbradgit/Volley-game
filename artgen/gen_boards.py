"""Generate assets/ads/*.png + ads.json — the L1 perimeter hoarding boards.

Early-2000s static perimeter boards: flat solid colours, one chunky brand line,
optional small strap line (phone number / .co.uk — very of-the-era). All brands
are FICTIONAL; sold sponsor boards later replace these files via ads.json.

Board size: 396x102 px (= 3x the 132x34 logical slot, spec §3/L1).
Run:  python3 artgen/gen_boards.py
"""
import os, json
from PIL import Image, ImageDraw, ImageFont

BW, BH = 396, 102
FONTS = {
    "bold":   "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "italic": "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf",
    "serif":  "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
}
def F(kind, sz): return ImageFont.truetype(FONTS[kind], sz)

def fit(d, text, kind, max_w, start=58, min_sz=20):
    sz = start
    while sz > min_sz and d.textlength(text, font=F(kind, sz)) > max_w:
        sz -= 2
    return F(kind, sz)

def board(bg):
    im = Image.new("RGB", (BW, BH), bg)
    return im, ImageDraw.Draw(im)

def frame(im, d):
    """White rim + bottom ground-shadow edge, like real perimeter boards."""
    d.rectangle([0, 0, BW - 1, BH - 1], outline=(245, 245, 245), width=4)
    d.rectangle([4, BH - 10, BW - 5, BH - 5], fill=(0, 0, 0))
    sh = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(sh).rectangle([4, BH - 26, BW - 5, BH - 11], fill=40)
    im.paste(Image.new("RGB", (BW, BH), (0, 0, 0)), (0, 0), sh)

def centre(d, text, font, y, fill):
    d.text(((BW - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "ads")
os.makedirs(out_dir, exist_ok=True)
boards = []

def save(im, bid, weight):
    im.save(os.path.join(out_dir, bid + ".png"), optimize=True)
    boards.append({"id": bid, "img": bid + ".png", "weight": weight})
    print("wrote", bid + ".png")

# 1 — SCORDAGOL house board (black / neon green)
im, d = board((8, 9, 12))
f = fit(d, "SCORDAGOL", "bold", BW - 60)
centre(d, "SCORDAGOL", f, 16, (57, 255, 20))
centre(d, "VOLLEY YOUR WAY TO GREATNESS", F("bold", 17), 68, (200, 205, 210))
frame(im, d); save(im, "house_scordagol", 1)

# 2 — ADVERTISE HERE house board (blue / yellow)
im, d = board((0, 51, 153))
centre(d, "ADVERTISE HERE", fit(d, "ADVERTISE HERE", "bold", BW - 50), 18, (255, 226, 61))
centre(d, "YOUR BRAND, PITCHSIDE", F("bold", 18), 66, (235, 238, 245))
frame(im, d); save(im, "house_advertise", 1)

# 3 — KESTREL MOTORS (white / navy, red strap with phone number)
im, d = board((248, 248, 246))
centre(d, "KESTREL MOTORS", fit(d, "KESTREL MOTORS", "bold", BW - 44), 14, (16, 28, 80))
d.rectangle([60, 62, BW - 60, 66], fill=(200, 24, 30))
centre(d, "0800 555 444", F("bold", 20), 70, (200, 24, 30))
frame(im, d); save(im, "kestrel_motors", 2)

# 4 — VOLT COLA (red / white italic, yellow bolt)
im, d = board((206, 24, 30))
f = fit(d, "VOLT COLA", "italic", BW - 150)
tw = d.textlength("VOLT COLA", font=f)
d.text(((BW - tw) / 2 + 22, 26), "VOLT COLA", font=f, fill=(255, 255, 255))
d.polygon([(28, 20), (46, 20), (35, 46), (50, 46), (22, 84), (33, 54), (20, 54)],
          fill=(255, 214, 0))                                  # lightning bolt, clear of the text
frame(im, d); save(im, "volt_cola", 2)

# 5 — NETLINK 56k (white / orange + black: dial-up internet, peak 2002)
im, d = board((250, 250, 250))
f = F("bold", 46)
w1 = d.textlength("NET", font=f); w2 = d.textlength("LINK", font=f)
x0 = (BW - w1 - w2) / 2
d.text((x0, 12), "NET", font=f, fill=(20, 20, 24))
d.text((x0 + w1, 12), "LINK", font=f, fill=(238, 118, 0))
centre(d, "56k HOME INTERNET  ·  www.netlink.co.uk", F("bold", 17), 66, (90, 92, 98))
frame(im, d); save(im, "netlink", 2)

# 6 — PORTLY'S PIES (maroon / cream serif)
im, d = board((86, 22, 32))
centre(d, "PORTLY'S PIES", fit(d, "PORTLY'S PIES", "serif", BW - 56), 16, (240, 226, 198))
centre(d, "THE MATCHDAY CLASSIC", F("bold", 17), 68, (214, 180, 140))
frame(im, d); save(im, "portlys_pies", 2)

# 7 — MEGA SPORT sale (yellow / black italic + red)
im, d = board((255, 210, 0))
centre(d, "MEGA SPORT", fit(d, "MEGA SPORT", "italic", BW - 80), 14, (16, 16, 18))
centre(d, "SALE NOW ON", F("bold", 24), 64, (200, 24, 30))
frame(im, d); save(im, "mega_sport", 2)

with open(os.path.join(out_dir, "ads.json"), "w") as fjs:
    json.dump({"boards": boards}, fjs, indent=1)
print("wrote ads.json with", len(boards), "boards")
