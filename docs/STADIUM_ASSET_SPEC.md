# Stadium Background — Layered Asset Specification

*Companion: `docs/stadium_grid_template.png` (regenerate with `python3 docs/make_grid_template.py`).*
*All numbers are derived from gameplay constants in `index.html` or measured from the current art — do not re-derive.*

## 0. Why this is safe to change (read first)

The background is **100% cosmetic**. The only pixel-sensitive system in the game is the keeper
save test (`savedCheck()`, index.html:567), and it samples a **separate offscreen canvas** that
contains only the keeper sprite (`drawKeeperTo(offCtx)`). Nothing ever reads background pixels.

So the constraint is purely *visual*: the art must **look** like it lives where the invisible
physics happens — posts where `LPOST`/`RPOST` are, goal line where the keeper's feet are, board
band where the ball flies. Get the lines below right and gameplay cannot break.

## 1. Coordinate system

| Term | Definition |
|---|---|
| **Field space** | The original SWF's 550-wide stage. All physics lives here. `x: 0..550`, `y: 0..400` visible pitch. |
| **View space** | The widescreen canvas, `924 × 520` logical. The field is centred: `view_x = field_x + 187` (`OX`, index.html:47). |
| **Scoreboard zone** | `y 400..520` — drawn by the game (`drawHUD`). **Never part of any background asset.** |
| Export scale | Author/export at **2× or 3× logical** (the canvas backing store is 2–4×, index.html:58). The game draws at logical size; the browser downscales → crisp. |

> The goal is **not centred in the view**: goal centre is field x = 282.5 → view x = **469.5**,
> while the view centre is 462. Place the backdrop's vanishing point at view x ≈ 469, not 462.

## 2. The hard lines (master geometry table)

All values **logical px**. (For view x of a field x, add 187.)

| Anchor | Field coords | Source |
|---|---|---|
| Left post centre | x = **135** (woodwork zone ±13) | `LPOST`, index.html:172 |
| Right post centre | x = **430** (±13) | `RPOST` |
| Crossbar (opening top) | y = **58** (= goal line 163 − BARH 105) | `BARH`, :172 |
| Goal line / post base | y = **163** | `KEEPER_STAGE_Y`, :779 |
| Goal mouth | **295 × 105** (x 135..430, y 58..163) | derived |
| Keeper feet anchor | (**263, 163**), sprite scale 0.753/0.777 | :173, :777 |
| Defender 1 | (117.95, 210.25) scale 1.0 | :551 |
| Defender 2 | (27.60, 163.35) scale 0.898 | :552 |
| Defender 3 | (471.15, 157.75) scale 0.823 | :553 |
| Striker | runs y = **300**, x 50..500, scale 1.0 | :174 |
| Ball shadow visible | y ≥ **130** | :763 |
| Crowd band | y **0..104** | measured from `pitch_hd.png` |
| **Hoarding band** | y **104..138** (34 tall) | measured |
| Grass starts | y **143** (138..143 = transition/board base) | measured |
| Pitch bottom | y **400** | `pitchBg`, :1829 |

**Perspective cheat-sheet** (so painted elements scale consistently with sprites):
scale ≈ 0.75 at y163 → 0.85 at y210 → 0.92 at y250 → 1.00 at y300.
(Ball law: `yscale = 10 + 90·y/325`, :650.)

## 3. The three layers

Draw order (back → front):
**L0 backdrop → L1 hoardings → L2 goal+net → [existing sprites: keeper → defenders → ball → striker] → HUD.**

### L0 — Stadium backdrop (one asset)

| Property | Value |
|---|---|
| File | `assets/stadium/backdrop.png` |
| Logical size | **924 × 400** (export 1848×800 @2× or 2772×1200 @3×) |
| Drawn at | view (0,0), before the `translate(OX)` — replaces both `drawStadiumSides()` (:1814) and the pitch part of `pitchBg()` (:1828) |

Content rules:
- **Crowd/stands fill y 0..104.** Any stadium bowl design; keep crowd colours neutral/mixed (a per-team-tintable crowd is a possible later enhancement — don't bake club colours in).
- **y 104..143 needs only a plausible dark base** — the hoarding layer covers it. This band is your error margin: if a generated image's crowd ends anywhere in 104..138, the boards hide the seam. **This is what makes AI generation tractable.**
- **Grass y 143..400.** Mow stripes/texture fine. Current art's grass tone ≈ RGB(120,150,63) up top, darker toward the bottom, if you want continuity.
- **NO goal, NO ad boards, NO players, no readable text** baked in. Ever. That's the whole point of layering.
- Vanishing point at view x ≈ 469 (see §1 note).
- Side thirds (view x 0..187 and 737..924) appear only on widescreen — design them as continuation (stand curvature, dugouts, etc.), nothing important in them (phones in odd aspect ratios may crop edges slightly).

### L1 — Advertising hoardings (7 separate assets + manifest)

| Property | Value |
|---|---|
| Band | view-space, y **104..138**, full 924 width |
| Slots | **7 slots × 132 × 34 logical** (7 × 132 = 924 exactly) |
| Board asset size | **396 × 102 px** (@3×) PNG, opaque |
| Files | `assets/boards/<id>.png` + `assets/boards/boards.json` manifest |

Manifest sketch:

```json
{ "boards": [
    { "id": "house_scordagol",  "img": "house_scordagol.png",  "weight": 1 },
    { "id": "house_advertise",  "img": "house_advertise.png",  "weight": 1 },
    { "id": "sponsor_acme",     "img": "sponsor_acme.png",     "weight": 3 }
] }
```

Runtime behaviour (when implemented):
- **URL rule: never use "ads"/"advert" in paths or filenames** — desktop ad-blockers (EasyList) block such URLs, which hides every board. This is why the folder is `assets/boards/`.
- Per match, pick 7 boards (weighted, seeded by the match RNG so daily-challenge players see identical boards).
- **Failure must be visible-safe** (lesson from the keeper-atlas bug): if the manifest or an
  image fails to load (see URL rule above), draw a flat club-coloured board with "SCORDAGOL" text — never an empty band.
- Boards are *impressions only* — no tap/click handling in-match (a mis-tap would move the striker). Clickable sponsorship belongs on menu screens / the scoreboard "ADVERTISE HERE" panel.
- Later: fetch a remote `ads.json` (with the bundled one as fallback) so sold boards update without redeploying the game. Needs CORS-enabled hosting; cache with a date key.

Design rules for board images: high contrast, one short message, min text height ~14 logical px
(boards render ~132 px wide ≈ 1/7 of screen width); 4 px safe margin all round.

### L2 — Goal frame + net (one animatable asset)

This layer simultaneously delivers HANDOVER §3.4 (animated net — currently impossible because
the net is baked into the pitch) and removes the baked-in third-party watermark
(the current `pitch_hd.png` net has a "zokker — Free Online Games!" logo baked into it — a
publication blocker on its own).

| Property | Value |
|---|---|
| Asset box (field space) | x **115..450**, y **40..170** → **335 × 130 logical** (posts at asset-local x 20 and 315; bar at local y 18; goal line at local y 123) |
| States | `rest`, `bulge` (3–5 frames, triggered on goal: where `flash=0.6` is set, index.html:687), optional `crink` shake on woodwork |
| Net | semi-transparent (α ≈ 0.3–0.4) so hoardings/crowd read through the mesh |

**Recommended implementation: procedural (canvas-drawn), not a PNG.**
Posts/bar are rectangles at exact coordinates; the net is a drawn mesh (verticals, horizontals,
slight sag); the bulge displaces mesh points around the ball's entry x for 3–4 frames. Benefits:
pixel-exact by construction, crisp at every devicePixelRatio, animates for free, zero IP risk,
and it kills the alignment problem entirely. A static PNG sheet (rest + bulge frames at the box
above) is the fallback if the hand-drawn look is preferred.
Reference for proportions: the original goal sprite (DefineSprite_180) was placed at scale
0.614/0.493, translate (284.65, 106.9) — HANDOVER §3.4.

**Mirroring gotcha:** when `leftFooted` is true the *sprites* mirror around the goal centre
(GCX = 282.5, index.html:1850) but the background layers must NOT mirror. A bulge positioned from
`xball` must be drawn inside the mirrored transform (or have its x manually reflected) or it will
bulge on the wrong side for left-footed matches.

## 4. Production workflow (how to actually get assets that fit)

Past attempts failed by asking one generation to satisfy all constraints at once. Don't. The
layer split means **only two horizontal seams** (crowd-bottom ~104, grass-top 143) constrain the
big generated image, and both are hidden under the hoarding band.

1. **Backdrop:** generate wide stadium art at 1848×800 (or larger, same aspect 2.31:1) with a
   prompt like *"empty football stadium from pitch level, packed stands across the top third,
   empty green pitch lower two-thirds, no goal, no advertising boards, no text, flat even
   lighting"*. Then **fit, don't regenerate**: in any editor (or a 10-line PIL script), 3-slice
   the image vertically (crowd / seam / grass) and stretch each band so the crowd ends in
   y 104..138 and grass starts at 143. The hoardings cover the join.
2. **Hoardings:** flat 396×102 rectangles — any design tool, no AI needed. Make the two house
   boards first ("SCORDAGOL", "ADVERTISE HERE — yourname@…").
3. **Goal:** procedural per §3/L2 (or hand-draw over the template at 50% opacity in
   Photoshop/Krita — never freehand without it).
4. **Validate in-game:** drop files in, load `index.html?cap=1`, grab `canvas.toDataURL()` (the
   documented headless flow), overlay `stadium_grid_template.png` at 50% opacity. Checklist:
   - [ ] post verticals within ±2 px of the red lines (x135/x430)
   - [ ] post bases sit on the goal line (y163); bar at y58
   - [ ] hoarding band fully covers y 104..138, no backdrop seam visible
   - [ ] grass texture starts by y143; keeper's feet stand on the line, not in front/behind
   - [ ] no goal/boards/text baked into the backdrop
   - [ ] one full match played: goal bulge on the correct side, including a left-footed match

## 5. Code integration (summary — implement as one PR)

- `sources` (index.html:74): replace `pitch` with `backdrop`; **delete the unused `crowd`/`kit` entries** (already dead).
- Replace `drawStadiumSides()` + `pitchBg()` with `drawBackdrop()` (view space) and add
  `drawHoardings()` (view space) + `drawGoal()` (field space, drawn before the keeper, exactly
  where the baked goal sits today — keeper stays in front of the net, as in the original).
- Add `boards.json` fetch **with a visible fallback** (see L1).
- Trigger `goalAnim` next to `flash=0.6` (:687); woodwork shake next to `sfx.post()` (:659–665).
- Keep old assets until the visual diff is approved, then delete `pitch_hd.png`/`pitch.jpg`/`crowd.jpg`/`kit.jpg`.
- Acceptance: physics CI goldens unchanged (rendering only); screenshot diff approved on desktop + one phone aspect.
