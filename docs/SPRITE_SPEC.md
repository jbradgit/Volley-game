# Sprite System — Geometry & Region-Tag Contract

*This file is the contract the engine and generators depend on — honour it whatever
the art source.*

**Current pipeline (the future, built + tested): `artgen/render_sprites.py`** renders
a rigged 3D human + real animation clips to these tagged sprites. It is the chosen
permanent path (replaces both placeholders below in one consistent style, 100%
original). It needs Mixamo FBX input — see `docs/ART_SOURCING.md` and HANDOVER §3.

**Live placeholders until the 3D renders land:**
- STRIKER + DEFENDER: `artgen/trace_sprites.py` — traced from the original Villa
  frames (silhouettes/animation match the original; kick-timing read is sacred).
  **Derivative of the source game's art — not publishable; superseded by the 3D pipeline.**
- KEEPER + BALL: `artgen/gen_sprites.py` — procedural, clean-room, save-extent verified.

Kit data: `artgen/gen_kits.py` · visual check: `artgen/preview_kits.py`.*

## 1. Region tags (how recolouring works)

Base sprites carry tags in the colour channels; the dominant channel(s) name the
region, the dominant value is the **cel-shade band** (lit 255 / mid 204 / dark 158),
and the spare channels carry **per-part UV coordinates** (×88): u = across the part
from its centre line, v = along it. `tagOf()`/`buildKit()` in index.html decode this;
`out = kitColour × (shade/255 × 1.04)` so the 3-tone shading survives any kit.

| Tag | Channels | Becomes |
|---|---|---|
| shirt | R=shade, G=u·88, B=v·88 | kit `c1`, `c2` by pattern |
| shorts | G=shade, R=u·88, B=v·88 | kit `shorts` |
| socks | B=shade, R=u·88, G=v·88 | kit `socks` |
| sleeves | R=G=shade, B=u·88 | kit `sleeves` (defaults `c1`) |
| hair | R=B=shade | random per-match hair colour |
| skin / boots / gloves / eyes / outline | final colours | pass through |

**Patterns** are evaluated in PART-LOCAL UV space, so stripes run parallel to the
part and mirror symmetrically from its centre: `stripes` = 7 even bands of u ·
`hoops` = 9 bands of v · `halves` (u) · `quarters` (u⊕v) · `sash` (|u+v−1|<0.18).
Painter's order is fixed in the generator: far arm → far leg → near thigh →
shorts → shirt (over shorts waist, dark hem line) → near calf/sock/boot →
near arm (over torso) → neck/head/hair. Same-colour kits stay separated by the
forced-dark hem and cuff strips.

**Kit spec** (in `teams.json` / `world.json`, palette colour names):
`kits: { h:{p,c1,c2?,sleeves?,shorts,socks}, a:{...} }` — legacy top-level fields
remain the home kit for HUD theming. **Clash rule:** the home side wears home; the
visitor switches to away when shirt-colour distance < 95 (`loadKits`).
Keeper wears the first of yellow/green/orange/grey that clashes with neither side.

## 2. Geometry (must hold for every regenerated sprite)

| Sprite | Box (logical) | Origin | Notes |
|---|---|---|---|
| striker k0..k5 | 131×191 @2x | (101.2, 126.5) | faces left; feet on canvas bottom |
| — kick contact | — | — | frame **k3** is the strike: foot through canvas (≈117, 103–122) = field origin+15, ball z 0..40. Anim: idle=k0; kick seq k1..k5, `idx=floor((manKickT−1)/2)` |
| defender | 67×115 @2x | (33.4, 57.5) | front-facing; one base covers every team |
| keeper atlas | unified 596×263 logical, feet (300,197) | manifest `ox,oy` logical; `w,h` @2x | frames: 1 idle · 50–99 dive_left · 100–149 dive_right (mirror) · 323/328/354 catches |
| — extents | idle x267–334 y69–198 · full dive x≈5–180 (mirrored 418–590) y≈153–211 · high catch top y≈54 | | **the save pixel hit-test reads these silhouettes** — keep within a few px of these targets (verified in gen_sprites output) |
| ball | 41×41 @3x | (19.6, 34.1) | disc centred (20,20), fills the box |
| shadow | 28×11 @3x | (13.0, 0.0) | full-box ellipse, drawn at α 0.25 |

## 3. Pipeline summary

`gen_sprites.py` (skeleton poses → tagged PNGs + keeper atlas/manifest)
→ `assets/sprites/*` → loaded once in `sources` → **`loadKits()`** builds per-match
canvases (`SPRITES.striker[6] / .defender / .keeper`) via `buildKit()` →
`drawStriker/drawDefenders/drawKeeperTo` draw them at the geometry above.
No per-club image files, no network fetches at kit time, and nations/minnows/euro
clubs all render through the same path. The retired ripped art under `assets/`
(striker_*, defender_*, keeper_atlas_*, ball/shadow/pitch) can be deleted once the
new look is approved (ROADMAP A.5/B).
