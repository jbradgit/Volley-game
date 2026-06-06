"""Background = the ORIGINAL pitch.jpg upscaled, with the goal/net/posts/crossbar left
completely untouched (so they stay perfectly aligned). The old 'mousebreaker' board is
covered by purple 'WIMP STUDIO' hoardings painted ONLY on the sides, outside the posts.
The goal mouth (net) is never modified, which fixes the post/net misalignment."""
from PIL import Image, ImageDraw, ImageFont

S = 2
base = Image.open('assets/pitch.jpg').convert('RGB').resize((550*S, 400*S), Image.LANCZOS)
d = ImageDraw.Draw(base)

y0, y1 = 104*S, 140*S                 # band covering the old advertising board
bh = y1 - y0
postL, postR = 133*S, 432*S           # boards stop just outside the posts; goal mouth stays original
PURPLE = (104, 24, 152)
boards = [(0, postL), (postR, base.width)]

# NB: the goal mouth (postL..postR) is left 100% original -> net/posts/crossbar stay aligned.
# side hoardings (flat purple with a lit top edge + shadowed bottom edge)
for bx0, bx1 in boards:
    d.rectangle([bx0, y0, bx1, y1], fill=PURPLE)
    d.rectangle([bx0, y0, bx1, y0+2*S], fill=(150, 70, 200))
    d.rectangle([bx0, y1-2*S, bx1, y1], fill=(64, 12, 96))

# 'WIMP STUDIO' on two stacked lines so it fills the board — identical size BOTH sides, big + extra-bold
LINES = ['WIMP', 'STUDIO']
FONT_PATH = r'C:\Windows\Fonts\arialbi.ttf'      # Arial Bold Italic
def make_label(px):
    font = ImageFont.truetype(FONT_PATH, px)
    sw = max(1, px // 9)                           # heavy stroke -> "twice as bold" (faux-heavy)
    lh = px * 1.02
    wmax = max(font.getlength(l) for l in LINES)
    tmp = Image.new('RGBA', (int(wmax) + 2*px, int(lh*len(LINES)) + 4*sw), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    for i, l in enumerate(LINES):
        w = font.getlength(l)
        td.text(((tmp.width - w)/2, px*0.2 + i*lh), l, font=font, fill=(255, 255, 255, 255),
                stroke_width=sw, stroke_fill=(255, 255, 255, 255))
    return tmp.crop(tmp.getbbox())

min_bw = min(bx1 - bx0 for bx0, bx1 in boards) - 12*S
best = make_label(8*S)
for px in range(8*S, 64*S):
    lab = make_label(px)
    if lab.height <= bh - 3*S and lab.width <= min_bw:
        best = lab
    else:
        break
lab = best
for bx0, bx1 in boards:
    base.paste(lab, (bx0 + (bx1 - bx0 - lab.width)//2, y0 + (bh - lab.height)//2), lab)

base.save('assets/pitch_hd.png')
print('wrote assets/pitch_hd.png', base.size, 'label', lab.size)
