# SCORDAGOL — Handover / State of Play

**Read this first.** Single source of truth for picking the project up on a new
device or a fresh session. Last updated: 2026-06-26.

---

## 0. CURRENT STATE (2026-06-26) — READ THIS FIRST (supersedes §3 below)

The 3D-sprite pipeline (old §3) is **long DONE and deployed**. Since then many rounds of
art/career/multiplayer/UI work shipped. **Live site:** https://jbradgit.github.io/Volley-game/
(GitHub Pages serves `main`).

**Git state right now:**
- Work branch: **`claude/3d-character-sprites`** (pushed to origin).
- `main` (= live Pages) is at **`5df880b`**.
- The branch is **1 commit ahead** at **`8062200`** — a big multiplayer/menu/HUD/font batch
  that is **CI-green + layout-audit-clean but NOT yet deployed to `main`**, because it includes
  a **new SCORDAGOL logo + headline font (v1, owner hasn't visually signed off)**.
- **To deploy it:** review the new logo/font in a browser; if good →
  `git push origin claude/3d-character-sprites:main` (fast-forward; Pages republishes in ~1–2 min).
  If the logo/font needs changes, iterate on the branch first.

**What's in `8062200` (this session):**
- **In-match HUDs reworked** (neutral dark blue, no team names/opponent score):
  HORSE shows the current player's letter tiles + the setter's name with "SET ✓";
  CLASSIC shows the current player + live score (left) and the points leader + score (right).
  Both via `drawHorseHUD()` / `drawClassicHUD()` branched at the top of `drawHUD()`.
- **Standard headers:** every sub-screen uses `ttHeader(centre, right)` =
  **SCORDAGOL (left) · status (centre) · mode (right)**, vertically centred.
- **New headline font** `drawHeadline()` (fine-pixel italic VT323 + rainbow speed-streak,
  Sport-76 inspired) **replaces Press Start 2P everywhere** — new logo, MULTIPLAYER title,
  mode card titles, START, player/champion names. `pxFont` is retired (`pxText`/`ttFont` =
  VT323 stay; they're the "fine pixel" font the owner is fine with).
- **`centredText()`** is the single source of truth for centring text in a box (uses real glyph
  metrics; `align` arg for vertical-only centring of left-aligned rows). Use it — don't hand-nudge
  baselines (alignment was a recurring complaint; this is the fix).
- **Home menu** footer/spacing fixed so 4 options + best score fit without overlap.

**Verification — the preview MCP server is UNRELIABLE here (dies). Use the audit skill:**
- **`menu-layout-audit` skill** (committed, `.claude/skills/menu-layout-audit/`): headless Chrome
  linter that instruments the canvas and flags text overflow / off-screen / edge / over-centre /
  text-overlap / frame-cover across all 19 menu+career screens. Run after ANY `draw*` menu/HUD edit:
  `python -m http.server 5577` (background) then `node .claude/skills/menu-layout-audit/audit.mjs`
  (needs `npm install puppeteer-core --no-save` + system Chrome; writes PNGs to `%TEMP%/volley_audit`
  to Read). `audit.mjs` also shows the full puppeteer+`?cap=1`+`window.__dbg` pattern for ad-hoc
  screenshots (the in-match HUDs aren't auto-audited — drive a real match like the skill does).

**Open / next (priority):**
1. **Owner review of the new logo + headline font** (v1) → then deploy to `main`. Reference was a
   "Sport 76" rainbow-italic font; current impl is VT323 + skew + rainbow streak.
2. **Commercial-readiness Q (owner asked):** with placeholder SFX sourced, the remaining
   launch blockers are IP — **real club/league/competition names** (trademark) and **any
   source-game-derived assets/sounds**. The 3D-rendered characters, generated stadium/crowd/ball,
   and the transcribed-but-clean-room physics are OK; fonts (VT323/Press-Start) are SIL-OFL
   (self-host for prod — see the `<link>` comment in `index.html`). See ROADMAP Track C.
3. **Per-player team SELECT in HORSE** (deferred) — owner wants players to pick teams in HORSE setup.
4. Foreign-league per-team kits (ESP/ITA/GER/FRA still use compact derive-field kits).
5. PWA real-phone test (install / offline).

**CI is the FULL suite — run ALL before pushing** (a subset once spammed the owner CI emails):
`node ci/smoke.js && node --test ci/physics.test.js ci/career.test.js ci/horse.test.js ci/leagues.test.js`.
Deploy = commit on the branch → push branch → `git push origin claude/3d-character-sprites:main`.
Don't commit `node_modules/`, the scratch `tools/`, or `striker_base_v01.blend` (pre-existing, not ours).

---

## 1. What this is

**SCORDAGOL** — an HTML5 Canvas football **volley** game. You get balls crossed in,
time a volley, beat the keeper. Began as a 1:1 remake of a 2007 Flash game and has
since grown into its own original game with a full career universe.

- **The whole game is `index.html`** (one file, ~3,000 lines, vanilla JS + Canvas 2D).
  No framework, no build step. Served over http (never `file://` — that taints the
  canvas and breaks the keeper save test).
- **Assets** in `assets/`. **Art generators** (Python) in `artgen/`. **Docs** in `docs/`.
- **Owner goal:** publish + monetise. So **every shipped pixel/sound/name must be ours**
  (no copyright from the original game). That single constraint drives most decisions.

---

## 2. How to run, test, and deploy

### Run locally
- Windows: double-click **`play.bat`** → serves on `http://localhost:5577/index.html`.
- Any OS: `python3 serve.py` (or `python3 -m http.server 5577`) then open that URL.

### Fresh-container setup (the dev environment is ephemeral — reinstall each session)
```
pip install numpy pillow      # all artgen/*.py scripts
pip install bpy               # 3D sprite pipeline only (Blender 5.0.1 as a module, ~minutes)
# node is preinstalled; used by ci/smoke.js
```

### Test (always run before pushing)
```
node ci/smoke.js              # headless: physics shots, a goal, 2 full career seasons,
                              # all screens render, kit build. Must print "SMOKE PASS".
```
`ci/smoke.js` loads `index.html` in Node with DOM stubs and drives the `?cap=1`
debug harness (`window.__dbg`). It is the safety net — if it fails, do not push.

### Deploy (how changes go live)
Work happens on a short-lived **feature branch** (`claude/<topic>`), is tested
locally, then fast-forwarded onto `main`. **`main` is the only branch GitHub Pages
serves — landing on `main` *is* the deploy.** Don't hardcode a branch name here; it
goes stale (a previous one did). Pattern:
```
node ci/smoke.js                         # must print SMOKE PASS first
git add -A && git commit -m "..."
git checkout main && git merge --ff-only <feature-branch>
git push origin main                     # Pages republishes in ~1–2 min
git checkout <feature-branch>            # carry on — or delete the branch if done
```
Feature branches now live **locally only** (the old remote `claude/*` branches were
deleted in the 2026-06-20 tidy-up); push them to origin only if you need a PR or
backup. The owner tests by **hard refresh** (`Ctrl+F5` / `Cmd+Shift+R`, or add
`?new=N` to the URL on mobile). **Never push to `main` without the smoke test
passing.** If another session has pushed to `main` meanwhile, `git fetch origin main`
and merge it in first.

---

## 3. THE ACTIVE TASK — character sprites (why this handover exists)

**Status: pipeline built & tested; waiting on the owner's one manual step.**

### The story so far (don't repeat these dead ends)
1. **Procedural figures v1/v2** (`artgen/gen_sprites.py`) — too crude/stiff ("stick
   figures"). Rejected for striker/defender.
2. **Traced from the original frames** (`artgen/trace_sprites.py`) — perfect
   silhouettes/animation/timing, but **derivative of the source game's art** → not
   publishable long-term. This is the **current live placeholder** for striker + defender.
3. **Procedural keeper** (`gen_sprites.py`) — clean-room and save-extent-correct, but a
   **style clash** with the traced outfield players.

### The chosen solution (decided + proven): 3D pre-rendered sprites
Render a rigged 3D human playing real motion-capture animations, orthographically, to
2D frames — the classic pre-rendered-sprite technique. This gives realistic form +
smooth motion + one consistent style for all three characters + 100% original art.

- **Pipeline is written and tested end-to-end:** `artgen/render_sprites.py`.
  Verified in-environment: `bpy` installs, a rigged glTF imports, region materials
  assigned by bone weights, two-pass render (flat **tag** pass + **lit** pass),
  encoded into the engine's tag/UV format, and the result **round-trips through the
  existing `build_kit()` recolour unchanged** (tested with solid + striped kits).
- **It reuses everything already built:** the region-tag contract (`docs/SPRITE_SPEC.md`),
  the `shade_of`/`uv_of` encoder maths (`trace_sprites.py`), and the in-engine
  `buildKit()` recolour + pattern system. **No `index.html` changes needed** to adopt it
  (one optional tweak later: more kick frames at the same contact timing).

### ⏭️ THE NEXT ACTION (owner does this, then a session runs the pipeline)
1. Owner: free Mixamo account → download ~6 FBX clips (exact shopping list in
   **`docs/ART_SOURCING.md`**: Soccer Idle, a Strike/Penalty Kick, Goalkeeper Idle +
   Diving Save + Catch, Standing Idle) into **`artgen/source3d/`**.
   Format: FBX Binary · With Skin · 30 fps · no keyframe reduction.
2. Session: `pip install bpy numpy pillow`, then:
   ```
   python3 artgen/render_sprites.py probe artgen/source3d/<character>.fbx   # check bone/clip names
   python3 artgen/render_sprites.py test                                    # sanity (needs a rigged glb)
   # then the striker/defender/keeper subcommands (stubs present; finish them against the
   # real rig — bone_region() mapping + camera framing per docs/SPRITE_SPEC.md §2 geometry)
   ```
3. Output overwrites `assets/sprites/striker_k*.png`, `defender.png`, `keeper_atlas.*`.
   Validate: `python3 artgen/preview_kits.py` (kit showcase), `node ci/smoke.js`, then deploy.
   **Keeper save-extent targets in `docs/SPRITE_SPEC.md` §2 are binding** — the save
   test reads the keeper's silhouette; new renders must hit those extents (±few px).

**Fallback if Mixamo stalls:** Quaternius Universal Animation Library (CC0, no account)
— see `docs/ART_SOURCING.md`. Generic kick, but unblocks solo.

---

## 4. What's DONE and live

| Area | State |
|---|---|
| **Stadium** | Layered: generated backdrop (`gen_backdrop.py`), 7 ad hoardings (`gen_boards.py`, `assets/boards/` — NB never "ads" in paths, adblockers), procedural animated goal+net (bulge on goal, shake on woodwork). `docs/STADIUM_ASSET_SPEC.md`. |
| **HUD** | Sega-style 5×7 pixel scoreboard digits, classic-football ball counter, team-coloured chassis. |
| **Logo** | Green-metallic streaked `SCORDAGOL` (`assets/ui/logo.png`, `gen_logo.py`). |
| **Career universe** | Season **calendar** engine; **domestic cup** (5 KO rounds, minnows→giants); **Europe** (Champions Trophy / Continental Cup, group→SF→final); **internationals** (nationality select at career start, World Tournament every 2 yrs from season 1, flag-themed hub). All cup/Euro/intl matches = **5 balls, halved targets, no-draw KO**. Career home view is **competition-aware**. `docs/CAREER_DESIGN.md`. |
| **Trophy room** | Sega-style renders (`gen_trophies.py`): league/cup/euro/world, labelled. Press T / button on career home. |
| **League sim** | Recalibrated vs real EPL (champions ~87 pts). |
| **Season review + Smail inbox** | Restyled; transfer offers from named senders via a football-cliché generator. |
| **Kit system** | `buildKit()` recolours tagged bases into any kit: home/away in `teams.json`/`world.json`, patterns (stripes/hoops/halves/quarters/sash), auto away-kit on clash, keeper non-clash colour. `docs/SPRITE_SPEC.md`. |
| **CI safety net** | `ci/smoke.js` (started; wire to GitHub Actions is still TODO — ROADMAP 0.2). |

---

## 5. Hard constraints (break these and you break the game)

1. **Physics & scoring are transcribed from the original SWF — sacred.** `logicStep()`,
   `savedCheck()`, and the constants block in `index.html`. Never change without
   re-verifying outcomes via `ci/smoke.js`. Everything above `render()` is fair game.
2. **Region-tag contract** (`docs/SPRITE_SPEC.md` §1): the engine decodes tag channels
   + per-part UVs. Any new sprite source must honour it. Keep `build_kit()` in
   `index.html` and `artgen/preview_kits.py` in sync.
3. **Keeper save extents** (`docs/SPRITE_SPEC.md` §2) — the save is a pixel hit-test on
   the rendered keeper silhouette.
4. **No "ads"/"advert" in any URL or filename** (desktop adblockers hide them).
5. **Every `fetch`/asset load needs a VISIBLE failure path**, never silent (the
   keeper-atlas bug lesson — AUDIT H-1).
6. **Never wipe a save** (`vc_career`); migrate it (see `loadCareer()`).
7. **Publication/IP:** real club names + the traced sprites are the remaining blockers.
   Decisions deferred to ROADMAP Track C / C.3 (workshop split). Don't ship as-is.

---

## 6. Document map

| Doc | Covers |
|---|---|
| **`HANDOVER.md`** (this) | Current state, workflow, the active task. Start here. |
| `AUDIT.md` | Original technical audit (health grade, findings) — context for the roadmap. |
| `ROADMAP.md` | Phased plan to publication (foundations → own-every-pixel → engineering → monetise → launch). Status ticks per task. |
| `docs/CAREER_DESIGN.md` | The career universe design + what shipped (E0–E5). |
| `docs/SPRITE_SPEC.md` | **The sprite/region-tag contract** the engine + all generators depend on. |
| `docs/STADIUM_ASSET_SPEC.md` | Layered-background geometry + the alignment grid. |
| `docs/ART_SOURCING.md` | The 3D-pipeline decision + **the Mixamo shopping list** (the active task). |

## 7. artgen/ script index
- `render_sprites.py` — **3D → tagged sprites pipeline** (the future; tested).
- `trace_sprites.py` — current striker/defender (traced placeholder).
- `gen_sprites.py` — current keeper + ball + shadow (procedural).
- `gen_kits.py` — injects home/away kit data into `teams.json`/`world.json`.
- `preview_kits.py` — mirrors `build_kit()` for offline visual validation.
- `gen_backdrop.py` · `gen_boards.py` · `gen_trophies.py` · `gen_logo.py` — stadium/UI art.
- `preview_mock.py` — composites an in-match frame vs the stadium grid template.

---

*Historical note: an older handover describing the strict 1:1 Flash-reproduction phase
was replaced by this document on 2026-06-15. The transcribed physics from that phase
remains the sacred core (constraint #1).*
