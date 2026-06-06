"""Build a per-team defender kit PNG by compositing DefineSprite_143's named
sub-regions and flat-filling each with the team colour (Flash Color.setRGB).
Result is mapped onto the existing 151 footprint so the remake's verified
defender placements / hit-tests are unchanged."""
import sys, os
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import bounds as B   # reuse recursive bounds() + shapes/sprites maps

Z = 4
REG = os.path.join(os.path.dirname(__file__), 'regions')

# child char -> (instance, translateX, translateY) within sprite 143 (twips), depth order bottom->top
LAYERS = [
    (142, 'skin',    0,    0),
    (141, 'shirt',  -55, -317),
    (139, 'shorts', -34, -116),
    (137, 'socks',  -43,  785),
    (135, 'sleeves',-55, -700),
    (133, 'stripe1',-95, -731),
]
P143 = B.bounds(143)            # twips bounds of the man
M143X, M143Y = P143[0], P143[1] # Xmin,Ymin twips

import json as _json
PALETTE = {k: int(v.lstrip('#'), 16) for k, v in
           _json.load(open('assets/teams.json', encoding='utf-8'))['palette'].items()}

# team kit: (shirt, shorts, socks, sleeves, stripe1, shirt_type)
TEAMS = {
    'AstonVilla': ('claret','white','claret','skyblue','claret','sleeves'),
    'Chelsea':    ('blue','blue','white','blue','blue','plain'),
    'Liverpool':  ('red','red','red','red','red','plain'),
}

def load_region(char, name):
    if name == 'skin':
        return Image.open(os.path.join(REG, '142.png')).convert('RGBA')
    return Image.open(os.path.join(REG, 'DefineSprite_%d' % char, '1.png')).convert('RGBA')

def _hex(h): return ((h>>16)&255,(h>>8)&255,h&255)
def flat_fill(img, hexcol):
    a = np.asarray(img).copy()
    r,g,b = _hex(hexcol)
    mask = a[:,:,3] > 0
    a[mask,0]=r; a[mask,1]=g; a[mask,2]=b
    return Image.fromarray(a)

def striped_fill(img, base_hex, stripe_hex):
    a = np.asarray(img).copy()
    mask = a[:,:,3] > 0
    a[mask,0],a[mask,1],a[mask,2] = _hex(base_hex)
    xs = np.where(mask.any(axis=0))[0]
    if len(xs):
        x0 = xs.min(); bw = max(2, int((xs.max()-x0+1)/9))   # ~4-5 vertical stripes
        xc = np.arange(a.shape[1])[None,:]
        sm = mask & (((xc-x0)//bw) % 2 == 1)
        a[sm,0],a[sm,1],a[sm,2] = _hex(stripe_hex)
    return Image.fromarray(a)

def build(shirt,shorts,socks,sleeves,stripe1,st,pattern=None,stripe2=None):
    colmap = {'shirt':shirt,'shorts':shorts,'socks':socks,'sleeves':sleeves,'stripe1':stripe1}
    W = int(round((P143[2]-P143[0])/20*Z)); H = int(round((P143[3]-P143[1])/20*Z))
    canvas = Image.new('RGBA', (W+8, H+8), (0,0,0,0))
    for char,name,tx,ty in LAYERS:
        if name == 'stripe1' and shirt == stripe1:
            continue                          # stripe hidden when shirt==stripe colour
        cb = B.bounds(char)
        img = load_region(char, name)
        if name in colmap:
            if name=='shirt' and pattern=='stripes' and stripe2:
                img = striped_fill(img, PALETTE[shirt], PALETTE[stripe2])
            else:
                img = flat_fill(img, PALETTE[colmap[name]])
        ox = int(round((tx + cb[0] - M143X)/20*Z))
        oy = int(round((ty + cb[1] - M143Y)/20*Z))
        canvas.alpha_composite(img, (ox, oy))
    return canvas

def content_bbox(img):
    a = np.asarray(img); ys,xs = np.where(a[:,:,3] > 8)
    return (int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)

def map_to_151(man):
    """Resize the recoloured 143 man onto the 151 hi-res footprint (201x345)."""
    tgt = Image.open(os.path.join(os.path.dirname(__file__),'hires','DefineSprite_151','1.png')).convert('RGBA')
    TW,TH = tgt.size
    tb = content_bbox(tgt)
    mb = content_bbox(man)
    crop = man.crop(mb).resize((tb[2]-tb[0], tb[3]-tb[1]))
    out = Image.new('RGBA',(TW,TH),(0,0,0,0))
    out.alpha_composite(crop,(tb[0],tb[1]))
    return out

if __name__ == '__main__':
    for team in (sys.argv[1:] or ['AstonVilla','Chelsea']):
        shirt,shorts,socks,sleeves,stripe1,st = TEAMS[team]
        out = map_to_151(build(shirt,shorts,socks,sleeves,stripe1,st))
        out.save('assets/defender_%s.png'%team)
        print('wrote assets/defender_%s.png'%team, out.size)
