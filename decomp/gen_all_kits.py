"""Generate per-team defender + animated striker kits for all clubs in assets/teams.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import gen_kit, gen_striker_kit

STRIKER_FRAMES = [1, 3, 5, 7, 9, 11]   # -> striker_<slug>_k0..k5

def main():
    data = json.load(open('assets/teams.json', encoding='utf-8'))
    only = set(sys.argv[1:])
    for t in data['teams']:
        if only and t['slug'] not in only:
            continue
        slug = t['slug']
        pat, s2 = t.get('pattern'), t.get('stripe2')
        # defender (plain man, per-region flat fill, mapped to 151 footprint)
        man = gen_kit.build(t['shirt'], t['shorts'], t['socks'], t['sleeves'], t['stripe'], t['type'], pat, s2)
        gen_kit.map_to_151(man).save('assets/defender_%s.png' % slug)
        # striker (recoloured volley frames) — now with contrasting sleeves
        for idx, fr in enumerate(STRIKER_FRAMES):
            im = gen_striker_kit.recolour('decomp/hires/DefineSprite_91/%d.png' % fr,
                                          t['shirt'], t['shorts'], t['socks'], t.get('sleeves'), pat, s2)
            im.save('assets/striker_%s_k%d.png' % (slug, idx))
        print('kits: %-12s defender + 6 striker frames' % slug)

if __name__ == '__main__':
    main()
