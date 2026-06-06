"""Align a generated stadium image so its goal matches the game's locked coords,
output a 3x (1650x1200) background for the 550x400 playfield."""
import sys
from PIL import Image, ImageDraw

SRC = 'Gemini_Generated_Image_ivxfmlivxfmlivxf.png'
# measured goal in the SOURCE image (full-res px): left post, right post, crossbar y, goal-line y
L, R, BAR, LINE = 618, 1792, 575, 873
# target goal in LOGICAL 550x400 space
TL, TR, TBAR, TLINE = 135, 430, 48, 163
SCALE = 3
OW, OH = 550*SCALE, 400*SCALE

def build(verify=False, l=L, r=R, bar=BAR, line=LINE):
    im = Image.open(SRC).convert('RGB')
    W, H = im.size
    # pad bottom with stretched grass so the vertical stretch doesn't sample past the image
    pad = Image.new('RGB', (W, H+400))
    pad.paste(im, (0, 0))
    grass = im.crop((0, H-160, W, H)).resize((W, 560))
    pad.paste(grass, (0, H-160))
    sx = (TR-TL)/(r-l)            # logical-px per source-px
    sy = (TLINE-TBAR)/(line-bar)
    # affine maps OUTPUT (3x logical) coords -> SOURCE px: src = a*out + c
    a = (1.0/sx)/SCALE
    c = l - (1.0/sx)*TL
    e = (1.0/sy)/SCALE
    f = bar - (1.0/sy)*TBAR
    out = pad.transform((OW, OH), Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.BICUBIC)
    if verify:
        d = ImageDraw.Draw(out)
        for gx in (TL, TR, 263):
            d.line([(gx*SCALE,0),(gx*SCALE,OH)], fill=(0,255,0), width=2)
        for gy in (TBAR, TLINE):
            d.line([(0,gy*SCALE),(OW,gy*SCALE)], fill=(255,0,255), width=2)
    return out

if __name__ == '__main__':
    verify = '--verify' in sys.argv
    out = build(verify=verify)
    name = 'decomp/_bg_verify.jpg' if verify else 'assets/pitch_hd.png'
    if verify: out.convert('RGB').resize((550,400)).save(name)
    else: out.save(name)
    print('wrote', name, out.size)
