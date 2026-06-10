"""Generate docs/stadium_grid_template.png — the master alignment template for all
stadium background layers (backdrop / hoardings / goal).

Every line is derived from gameplay constants in index.html (LPOST/RPOST/BARH/
KEEPER_STAGE_Y/...) or measured from the current pitch art. Regenerate after any
spec change:  python3 docs/make_grid_template.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

S = 2                      # render scale (template is 2x logical, like the canvas backing store)
VW, SH = 924, 520          # logical view (index.html: VW=924, SH=520)
PLAY_H = 400               # stadium/backdrop covers y 0..400; scoreboard owns 400..520
SW, OX = 550, (924 - 550) // 2          # field width + centring offset (OX=187)

# ---- gameplay anchors (field space, from index.html) ----
LPOST, RPOST, BARH, POSTTOL = 135, 430, 105, 13      # :172
GOAL_Y = 163                                          # KEEPER_STAGE_Y :779 (post base / goal line)
BAR_TOP_Y = GOAL_Y - BARH                             # ball screen-y of the bar opening = 58
KEEPER_X = 263                                        # :173
MAN_Y, MAN_MIN_X, MAN_MAX_X = 300, 50, 500            # :174
SHADOW_MIN_Y = 130                                    # drawBall: shadow only when yball>=130 :763
DEFENDERS = [(117.95, 210.25, 1.0), (27.60, 163.35, 0.898), (471.15, 157.75, 0.823)]  # :550-553

# ---- art bands (measured from assets/pitch_hd.png, logical y) ----
CROWD_BOTTOM = 104        # crowd ends / hoarding band starts
HOARD_TOP, HOARD_BOT = 104, 138
GRASS_TOP = 143           # grass begins (hoarding->grass transition 138..143)

fx = lambda x: int((x + OX) * S)      # field-x -> template px
vx = lambda x: int(x * S)             # view-x  -> template px
fy = lambda y: int(y * S)

img = Image.new("RGB", (VW * S, SH * S), (10, 12, 16))
d = ImageDraw.Draw(img)

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

F10, F12, F15 = font(13), font(16), font(20)

# ---- zone fills ----
d.rectangle([0, 0, VW*S, fy(CROWD_BOTTOM)], fill=(38, 50, 72))                    # crowd
d.rectangle([0, fy(HOARD_TOP), VW*S, fy(HOARD_BOT)], fill=(96, 40, 110))          # hoardings
d.rectangle([0, fy(HOARD_BOT), VW*S, fy(GRASS_TOP)], fill=(46, 72, 40))           # transition
d.rectangle([0, fy(GRASS_TOP), VW*S, fy(PLAY_H)], fill=(34, 88, 44))              # grass
for yy in range(fy(PLAY_H), SH*S, 12):                                             # scoreboard hatch
    d.line([0, yy, VW*S, yy], fill=(28, 28, 34), width=4)
d.rectangle([0, fy(PLAY_H), VW*S, SH*S-1], outline=(70, 70, 80), width=2)

# ---- field bounds (550-wide physics space centred in the 924 view) ----
for x in (fx(0), fx(SW)):
    for yy in range(0, fy(PLAY_H), 18):
        d.line([x, yy, x, yy+9], fill=(255, 220, 60), width=3)
d.text((fx(0)+8, 8), "FIELD x=0 (view x=187)", font=F10, fill=(255, 220, 60))
d.text((fx(SW)-260, 8), "FIELD x=550 (view x=737)", font=F10, fill=(255, 220, 60))
d.text((30, fy(PLAY_H//2)), "side extension\n(widescreen only,\nno gameplay)", font=F10, fill=(200, 200, 210))
d.text((fx(SW)+30, fy(PLAY_H//2)), "side extension\n(widescreen only,\nno gameplay)", font=F10, fill=(200, 200, 210))

# ---- goal frame ----
gl, gr, gt, gb = fx(LPOST), fx(RPOST), fy(BAR_TOP_Y), fy(GOAL_Y)
# post tolerance bands (|xball-POST|<13 = woodwork zone)
for px_ in (LPOST, RPOST):
    d.rectangle([fx(px_-POSTTOL), gt, fx(px_+POSTTOL), gb], outline=(255, 120, 120), width=2)
d.rectangle([gl, gt, gr, gb], outline=(255, 60, 60), width=4)                      # goal mouth
d.line([0, gb, VW*S, gb], fill=(255, 60, 60), width=3)                             # goal line
d.line([gl, gt, gr, gt], fill=(255, 60, 60), width=4)                              # bar
d.text((gl+10, gt-34), f"BAR top: y={BAR_TOP_Y}  (goal needs ball z<{BARH})", font=F12, fill=(255, 90, 90))
d.text((vx(782), gb-32), f"GOAL LINE y={GOAL_Y}", font=F12, fill=(255, 90, 90))
d.text((gl-4, gb+8), f"L POST x={LPOST} (±{POSTTOL})", font=F10, fill=(255, 140, 140))
d.text((gr-150, gb+8), f"R POST x={RPOST} (±{POSTTOL})", font=F10, fill=(255, 140, 140))
d.text((fx((LPOST+RPOST)//2)-120, gt+10), "goal mouth 295 x 105 (logical)", font=F10, fill=(255, 170, 170))

# ---- hoarding band + slots ----
d.line([0, fy(HOARD_TOP), VW*S, fy(HOARD_TOP)], fill=(255, 90, 255), width=2)
d.line([0, fy(HOARD_BOT), VW*S, fy(HOARD_BOT)], fill=(255, 90, 255), width=2)
NSLOT, SLOT_W = 7, 132                       # 7 slots x 132 = 924 exactly
for i in range(NSLOT):
    x0 = vx(i*SLOT_W)
    d.rectangle([x0+2, fy(HOARD_TOP)+2, x0+SLOT_W*S-2, fy(HOARD_BOT)-2], outline=(255, 160, 255), width=2)
    d.text((x0+10, fy(HOARD_TOP)+6), f"AD {i+1}", font=F10, fill=(255, 200, 255))
d.text((vx(6)+4, fy(HOARD_TOP)-26), f"HOARDINGS y={HOARD_TOP}..{HOARD_BOT}  -  7 slots x 132x34 logical (396x102 @3x)",
       font=F12, fill=(255, 140, 255))

# ---- crowd / grass labels ----
d.text((vx(40), fy(36)), f"CROWD / STANDS  y=0..{CROWD_BOTTOM}", font=F15, fill=(170, 195, 235))
d.text((vx(380), fy(360)), f"GRASS  y={GRASS_TOP}..400", font=F15, fill=(150, 230, 160))
d.line([0, fy(GRASS_TOP), VW*S, fy(GRASS_TOP)], fill=(120, 230, 130), width=2)
d.text((vx(6), fy(GRASS_TOP)+4), f"grass starts y={GRASS_TOP}", font=F10, fill=(150, 230, 160))

# ---- sprite anchors ----
def cross(px_, py_, col, label, dy=8):
    d.line([px_-12, py_, px_+12, py_], fill=col, width=3)
    d.line([px_, py_-12, px_, py_+12], fill=col, width=3)
    d.text((px_+14, py_+dy), label, font=F10, fill=col)

cross(fx(KEEPER_X), fy(GOAL_Y), (80, 220, 255), f"KEEPER feet ({KEEPER_X},{GOAL_Y}) scale 0.75", dy=30)
for i, (dx_, dy_, sc) in enumerate(DEFENDERS):
    cross(fx(dx_), fy(dy_), (255, 200, 90), f"DEF{i+1} ({dx_:.0f},{dy_:.0f}) s{sc}", dy=4 if i else 14)
# striker line + range
d.line([fx(MAN_MIN_X), fy(MAN_Y), fx(MAN_MAX_X), fy(MAN_Y)], fill=(120, 255, 140), width=3)
for x_ in (MAN_MIN_X, MAN_MAX_X):
    d.line([fx(x_), fy(MAN_Y)-10, fx(x_), fy(MAN_Y)+10], fill=(120, 255, 140), width=3)
d.text((fx(210), fy(MAN_Y)+12), f"STRIKER line y={MAN_Y}, runs x={MAN_MIN_X}..{MAN_MAX_X}, scale 1.0", font=F12, fill=(120, 255, 140))
# shadow cutoff
for xx in range(0, VW*S, 24):
    d.line([xx, fy(SHADOW_MIN_Y), xx+10, fy(SHADOW_MIN_Y)], fill=(220, 220, 220), width=1)
d.text((vx(640), fy(SHADOW_MIN_Y)+44), f"ball shadow visible y>={SHADOW_MIN_Y} (dashed)", font=F10, fill=(220, 220, 220))

# ---- perspective ruler (right edge): sprite scale by stage y ----
d.text((vx(860), fy(150)), "scale@y", font=F10, fill=(200, 200, 210))
for y_, s_ in ((163, "0.75"), (210, "0.85"), (250, "0.92"), (300, "1.00")):
    d.line([vx(852), fy(y_), vx(864), fy(y_)], fill=(200, 200, 210), width=2)
    d.text((vx(868), fy(y_)-9), f"{s_}", font=F10, fill=(200, 200, 210))

# ---- header ----
d.text((vx(8), fy(PLAY_H)+18),
       "SCORDAGOL stadium template - 2x logical. View 924x400. Field=550 wide centred (OX=187). Backdrop: 924x400, NO goal/boards.",
       font=F12, fill=(235, 235, 240))
d.text((vx(8), fy(PLAY_H)+46),
       "Goal + hoardings are separate layers - see docs/STADIUM_ASSET_SPEC.md. Scoreboard zone y=400..520 is drawn by the game.",
       font=F12, fill=(150, 150, 160))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stadium_grid_template.png")
img.save(out)
print("wrote", out, img.size)
