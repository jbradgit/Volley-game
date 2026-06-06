# Volley Challenge — Handover

A from-scratch HTML5 Canvas remake of the 2007 Flash game **LFC Volley Challenge** (Mousebreaker).
Goal: an **exact, 1:1 reproduction** of the original, reconstructed entirely from the decompiled SWF —
**no guessing, no shortcuts**. We can differentiate *after* it matches the original perfectly.

---

## 1. How to run / test
- Run **`play.bat`** (double-click) → starts a local server and opens `http://localhost:5577/index.html`.
- Or: `py -m http.server 5577` in the project folder, then open that URL.
- **Do NOT** open `index.html` as a `file://` page — it taints the canvas and breaks the keeper's pixel-based save test. Always serve over `http://localhost`.
- Reference: `http://localhost:5577/ruffle.html` runs the **actual original SWF** via Ruffle (for visual comparison only — its menus can't be driven by script).
- Controls: **←/→** move player, **Space** volley / start / restart.

---

## 2. Current state — what's DONE and verified exact
The **gameplay logic is exact** (transcribed from decompiled ActionScript). Don't change it unless re-verifying against the source:
- Physics: serve arc, bounce (halves score), kick contact (`dbx = man._x+15-xball`, `dby = z`, connects only if `z<40 && |dbx|<30`), flight (`z += dby/13`, rising curl), in-net.
- Scoring (÷bounced): contact +100, woodwork +150, save +300, goal +4000. **Goals are free shots.** 10 balls/match.
- Keeper save = real **pixel hit-test** of the rendered keeper sprite at the original's 8 sample points.
- Defender deflections: one bbox hit-test per defender at its depth threshold (opp1 yball<240 `dbx-=10+rnd8`; opp2 yball<200 `dbx-=20+rnd8`; opp3 yball<200 `dbx+=10+rnd8`).
- Win/draw targets, FULL TIME → WIN/DRAW/DEFEAT, best score persistence.
- **Exact placements/scales/origins** for striker, defenders, ball, shadow, keeper (computed from `swf.xml`, see §5).
- Real ripped art: `pitch.jpg` background, keeper sprite (+2 dive frames), striker idle + 5 kick frames, solid claret defender, real ball + shadow.
- On-screen terminology matches the original ("Balls:", "Score:", "Your target to win/draw this game is X", "MOVE MAN", "SHOOT").

---

## 3. ISSUES (user feedback)
**Status (session 2, 2026-05-22 — all DONE items verified in-browser):**
- ✅ **3.1 Low resolution** — DONE. Sprites re-exported high-res (ball/shadow/striker 3×, keeper 2×, defenders 4×) and drawn at LOGICAL sizes so the browser downscales → crisp. Verified.
- ✅ **3.2 Keeper full animation** — DONE. Packed into `assets/keeper_atlas_{0,1}.png` + `keeper_atlas.json`; idle / dive_left / dive_right / low|mid|high catch wired to the exact dive/catch decision. Verified with a live high-catch save.
- ✅ **3.3 Per-team kits** — DONE. `decomp/gen_kit.py` composites DefineSprite_143 regions, flat-fills per team (palette + add_new_team data), maps to the 151 footprint (placements unchanged). `assets/defender_<Team>.png`, loaded by opponent name. Villa + Chelsea generated & verified.
- ✅ **3.5 Ball size** — DONE. In-play `/ball` uses `yscale*0.8` (was full yscale → ~25% too big); in-net ball + shadow keep full yscale.
- ⬜ **3.4 Net animation** — REMAINING. See updated notes below (incl. authentic-background find).
- ⬜ **3.6 Idle/commentary** — REMAINING.
- ⬜ **3.7 Frame rate** — still open (28 Hz currently).

Each issue below lists the **exact data already extracted** so there is zero guesswork.

### 3.1 Low resolution / soft — biggest visual gap [DONE]
The original is **vector** (crisp at any zoom). Our sprites are raster PNGs at native ~550px res, upscaled → soft.
**Fix:** re-export every sprite/shape at high resolution (e.g. 3–4×) via FFDec's zoom option, *or* export as SVG and render vector. Then draw at the correct logical size. The canvas backing is already 2× (`SCALE=2`); make assets match or exceed it.
FFDec image export supports a zoom factor — re-export keeper, striker (all frames), defender man, ball, shadow, and ideally re-render `pitch.jpg`/net at higher res.

### 3.2 Keeper — not responsive, not enough variation (USE THE FULL ANIMATION SET) [DONE]
We only used 3 frames of one dive. **DefineSprite_168 has 371 frames with 10 labelled animations** (all frames already exported to `decomp/assets/sprites/DefineSprite_168/`):
| label | frames | label | frames |
|---|---|---|---|
| (idle) | 1–49 | dive_up_right | 277–301 |
| dive_left | 50–99 | dive_up_left | 302–322 |
| dive_right | 100–149 | low_catch | 323–327 |
| dive_up | 150–180 | mid_catch | 328–353 |
| dive_right_low | 181–232 | high_catch | 354–371 |
| dive_left_low | 233–276 | | |
The original code selects them: on a dive `keeps.gotoandplay("dive_left"/"dive_right")`; on a central catch (`no_dive`) `keeps.gotoandstop("low_catch"/"mid_catch"/"high_catch")` by height (`z<30` low, `z<60` mid, else high). Wire each animation to the existing dive/catch decision and **play the full frame range** for fluidity.

### 3.3 Defender kits — plain, recoloured per team [DONE]
The original uses a **plain man sprite with named colourable sub-clips** (`shirt, shorts, socks, sleeves, trim(=socks_top), stripe1`) recoloured per opponent (`frame_5/DoAction_2.as`).
**Colour → hex palette (`opp_convert_col_to_hex`):**
`red=0xCC0000  white=0xFFFFFF  blue=0x003399  black=0x000000  yellow=0xFFC633  grey=0xCCCCCC  green=0x006600  claret=0x840000  skyblue=0x66CCCC  orange=0xFF9900  darkblue=0x1F2F77`
**Per-team kit data** is in `frame_126/DoAction.as` `add_new_team(rating, shirt_type, name, colour, shorts, socks, socks_top, stripe, sleeves, collar, song)` — e.g. Chelsea = blue shirt/shorts/sleeves, **white socks** (matches the user's screenshot); Aston Villa = claret + skyblue sleeves + white shorts.
**Fix:** export the man's colourable sub-shapes separately (find their chids inside the man sprite 151/143) and tint+composite per region, or recolour by region. Striker (Liverpool) stays its own kit; only the 3 opponents recolour.

### 3.4 Net animation on goal [REMAINING]
The net is baked into the static `pitch.jpg`. The original animates it: **goalnet = DefineSprite_180** = the WHOLE goal (posts + crossbar + net), 9 frames, "goal" bulge ~frames 5–9 (its internal net mesh at depth 1 is shifted; `_level0.goalnet.gotoandplay("goal")` on score). **crink = DefineSprite_119** (20 frames) plays on woodwork.
**Exact placement (main timeline, depth 28):** scaleX **0.61432**, scaleY **0.49258**, translate **(284.65, 106.9) px** to 180's registration origin (get the origin via `bounds.py`).
**Blocker:** 180 is the whole goal and `pitch.jpg`/`201.jpg` already have the goal+net baked, so a clean overlay needs a **goal-less background**. Options: (a) re-export the gameplay frame with `-removeCharacter 180` to get a goal-less bg, then overlay 180; (b) overlay 180 aligned over the baked net so frame 1 matches at rest and only the bulge shows (risk: doubling if misaligned).
**Authentic-background find (do alongside):** real bg = `decomp/assets/images/200.jpg` (vivid RED Anfield crowd, 550×248, top) + `201.jpg` (goal + grass, 550×400). Current `pitch.jpg` is a grayer/softer rip missing the red crowd — swapping to 200+201 closes the look gap vs `ref_gameplay.png`.

### 3.5 Ball too big — verify size [DONE]
Ball = DefineSprite_122, 41×41 native, drawn at `yscale%` (`10+90*yball/325`). Its bounds were oddly tall (Y[-683..137]) so the 41×41 canvas may include padding / the visible disc may be smaller. **Measure the actual ball disc (non-transparent extent) and compare to the original** (user says ours is too big); correct the rendered diameter.

### 3.6 Stiffness / idle animation [REMAINING]
Original has idle variation: `opponent.man.head.gotoandplay("blink"/"lookleft"/"lookright")` and commentary **peep = DefineSprite_175** (whistle f2, time_up f10, goal f41, boos f83, near_miss f116). Add idle head/commentary animation and use full frame sequences; consider smoothing the render.

### 3.7 Frame rate (open question)
Decompiled main loop is **2 frames** (`mainloop`=physics frame, next frame loops back) → 14 Hz logic, with clip `enterFrame` at 28 Hz. Currently set to **28 Hz** (user found 14 Hz too slow). Couldn't measure the original directly (Ruffle won't take synthetic menu clicks). It's one constant in `swfFrame()`. Decide once the visuals are polished.

---

## 4. Inventory (where everything is)
- `index.html` — the game (single file, vanilla Canvas).
- `assets/` — art in use. **High-res now:** ball.png, shadow.png, striker.png + striker_k0–4.png (3×); keeper_atlas_0/1.png + keeper_atlas.json (2× packed full-anim); defender_<Team>.png (per-team kits). pitch.jpg/crowd.jpg/kit.jpg still the old rip. (Old keeper*.png + defender.png are now unused.)
- `decomp/gen_kit.py` — regenerates `assets/defender_<Team>.png` from DefineSprite_143 regions (run `py decomp/gen_kit.py AstonVilla Chelsea ...`). `decomp/regions/` + `decomp/hires/` are its source exports. `decomp/decode_cap.py` — decode a preview_eval dataURL capture to an image.
- `original.swf` — the real game (CWS, AVM1/AS2, 28 fps, 550×520).
- `tools/` — portable JRE + JPEXS FFDec. Run: `tools\jre\jdk-17.0.19+10-jre\bin\java.exe -jar tools\ffdec\ffdec.jar <args>`.
- `decomp/scripts/` — all decompiled ActionScript (gameplay = frame_5/6/8/9/10/11/34; teams/fixtures = frame_126; kit recolour = frame_5/DoAction_2.as).
- `decomp/swf.xml` — full SWF as XML (every shape bound + PlaceObject matrix). `decomp/swfdump.txt` — tag list.
- `decomp/assets/sprites/` & `images/` — **every** exported sprite frame & bitmap.
- `decomp/bounds.py` — computes any sprite's exact bounds/origin from swf.xml. `decomp/keeper_labels.py` — frame-label extractor.
- `ruffle/` + `ruffle.html` — original running in Ruffle (reference). `play.bat` — launcher. `.claude/launch.json` — preview server.
- Memory: `.claude/projects/C--Users-Office-Volley-Game/memory/` — `reference_decompiled-mechanics.md` is the source-of-truth spec (physics, scoring, geometry, sprite IDs, exact origins, frame labels).

---

## 5. Exact reference values (from the SWF — do not re-derive)
- Stage 550×520. lpost=135, rpost=430, barh=105, posttolerance=13, goal line y≈163. keeps._x=263. man start (450,300), range x 50–500.
- **Origins** (registration in the export PNG): ball (19.6,34.1)/41×41; shadow (13.0,0.0)/28×11; striker owen-91 (101.2,126.5)/131×191; defender man-151 (33.4,57.5)/67×115; keeper anchored by feet (PNG 300,197 → stage 263,163), scale 0.753×/0.777×.
- **Defender placements:** opp1 (117.95,210.25) s1.0 ; opp2 (27.6,163.35) s0.898/0.896 ; opp3 (471.15,157.75) s0.823/0.826.
- Sprite IDs: keeper 168, striker players 51(cisse)/67(gerrard)/79(baros)/91(owen), defender wrapper 152 (inner man 143=striped, 151=solid), ball 122, shadow 124, goalnet 180, crink 119, peep 175, bubble 127.

---

## 6. Ground rules
**DO:** derive every value from the SWF data (`swf.xml`, `decomp/scripts/`, exported frames, `bounds.py`); re-export assets at high res for crispness; use the full keeper animation set; recolour kits per team from the palette+team data; animate the net.
**DON'T:** eyeball/guess; use Ruffle screenshots to reverse-engineer placement (use the data); take shortcuts; or change the verified gameplay logic/physics/scoring.

---

## 7. Copy-paste prompt for the new session
> Continue the **Volley Challenge** remake in `C:\Users\Office\Volley Game`. Read `HANDOVER.md` and the memory file `reference_decompiled-mechanics.md` first. Session 2 finished issues 3.1 (high-res sprites), 3.2 (full keeper animation), 3.3 (per-team kits), 3.5 (ball size) — all verified in-browser. **Do not change physics/scoring**; objective is an **exact 1:1 visual reproduction** — **no guessing, no shortcuts** (derive from `decomp/swf.xml`, decompiled scripts, `decomp/bounds.py`). Remaining: (A) **authentic background** — swap `pitch.jpg` for the real `decomp/assets/images/200.jpg` (red Anfield crowd) + `201.jpg` (goal+grass); high value, low risk. (B) **animated net on goal** (§3.4) — needs a goal-less bg (re-export gameplay frame with `-removeCharacter 180`, or align overlay over baked net); goalnet=DefineSprite_180 at scale 0.61432/0.49258 translate (284.65,106.9), bulge frames ~5–9; crink=119 on woodwork. (C) **idle/commentary** (§3.6) — head blink/look, peep=DefineSprite_175. (D) framerate 14 vs 28 Hz (§3.7). Test via `play.bat` (http, never file://); for headless capture load `index.html?cap=1` and grab `canvas.toDataURL` via preview_eval (preview_screenshot times out on the rAF loop). Don't use Ruffle screenshots for placement.
