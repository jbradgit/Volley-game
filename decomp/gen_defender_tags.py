"""Build ONE region-tag map of the defender (the SWF's named sub-shapes painted with
unique tag colours), at the same 151 footprint as the baked defender_<team>.png files.
The game loads this once and recolours each region live per opponent in the browser —
exactly the original game's Color.setRGB-per-sub-clip method, but in canvas."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import gen_kit as G
from PIL import Image
import numpy as np

# Only the recolourable sub-clips get a tag colour (the original Color.setRGB targets).
# 'skin' (sprite 142) is the fixed BASE: skin + hair + boots + black line-work -> kept as-is.
TAGS = {
    'shirt':   0xFF0000,
    'shorts':  0x00FF00,
    'socks':   0x0000FF,
    'sleeves': 0xFFFF00,
    'stripe1': 0x00FFFF,
}

def build_tags():
    W = int(round((G.P143[2] - G.P143[0]) / 20 * G.Z))
    H = int(round((G.P143[3] - G.P143[1]) / 20 * G.Z))
    canvas = Image.new('RGBA', (W + 8, H + 8), (0, 0, 0, 0))
    for char, name, tx, ty in G.LAYERS:       # bottom -> top, same depth order as gen_kit
        img = G.load_region(char, name)
        if name in TAGS:                      # recolourable region -> flat tag colour, HARD edge
            img = G.flat_fill(img, TAGS[name])
            a = np.asarray(img).copy()        # binarise alpha so there are NO blended edge pixels
            a[:, :, 3] = np.where(a[:, :, 3] > 127, 255, 0).astype('uint8')
            img = Image.fromarray(a)
        # else 'skin' base: composite the real skin/hair/boots/outline pixels untouched
        cb = G.B.bounds(char)
        ox = int(round((tx + cb[0] - G.M143X) / 20 * G.Z))
        oy = int(round((ty + cb[1] - G.M143Y) / 20 * G.Z))
        canvas.alpha_composite(img, (ox, oy))
    return canvas

def map_to_151_nearest(man):
    tgt = Image.open(os.path.join(os.path.dirname(__file__), 'hires', 'DefineSprite_151', '1.png')).convert('RGBA')
    TW, TH = tgt.size
    tb = G.content_bbox(tgt); mb = G.content_bbox(man)
    crop = man.crop(mb).resize((tb[2] - tb[0], tb[3] - tb[1]), Image.NEAREST)  # NEAREST keeps tags crisp
    out = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    out.alpha_composite(crop, (tb[0], tb[1]))
    return out

if __name__ == '__main__':
    out = map_to_151_nearest(build_tags())
    out.save('assets/defender_regionmap.png')
    print('wrote assets/defender_regionmap.png', out.size)
