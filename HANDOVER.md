# SCORDAGOL — Handover / State of Play

**Read this first.** Single source of truth for picking the project up on a new
device or a fresh session. Last updated: 2026-06-30.

---

## 0. CURRENT STATE (2026-06-30) — READ THIS FIRST (supersedes §3 below)

The 3D-sprite pipeline (old §3) is **long DONE and deployed**. **Live site:**
https://jbradgit.github.io/Volley-game/ (GitHub Pages serves `main`).

**Git state right now:**
- Work branch **`claude/3d-character-sprites`** is **AHEAD of `main`** with the 2026-06-30 session
  below — **CI-green + layout-audit-clean, but NOT yet deployed to `main`/live.** Owner should eyeball it
  (logo, Slick Vic, HUD venue chips, agent flow) then deploy: `git push origin claude/3d-character-sprites:main`.

**What the 2026-06-30 session shipped (this branch, UNDEPLOYED):**
- **Homescreen logo redesigned** — bold chunky italic 3D-extruded "Lardiland"-style wordmark
  (`drawSportyLogo()`, Press Start 2P + red→gold gradient). HOMESCREEN ONLY.
- **`drawHeadline()` REVERTED to standardised teletext** (upright VT323, solid colour — NO rainbow/italic;
  this supersedes the old §0 "new headline font everywhere" claim). Everywhere except the homescreen logo
  is plain teletext now. `careerBar()` makes the 3 career-screen headers plain blue bars
  (SCORDAGOL · mode · status), replacing the old green logo box.
- **AgentCommunicationScreen — "Slick Vic"** (new `ST.AGENT` state + `drawAgentScreen()`): pure-black
  teletext page, 1px-framed pixel-art portrait (`assets/ui/slick_vic.png`, traced from `New Vic.png`),
  typewriter dialogue (`AGENT_TYPING_SPEED`), action key skips/advances. East-End wheeler-dealer voice
  (`VIC_LINES`). `showAgent(text, onComplete)` is the reusable core; `__dbg.agentSim(which)` for the audit.
  Wired into career start: name → **Vic (asks your nation)** → nationality → **Vic (pick your league)**
  → league → club. Season-end shows Vic's call-up check (`hasNationalCallUp()` = NEXT season is an
  odd/World-Tournament year) → then the transfer offers.
- **In-match HUD venue display:** the top fixture strip now shows **HOME team ALWAYS left, AWAY ALWAYS
  right** (neutral grey HOME/AWAY chips via `venueChip()`), driven by `OPPONENT.home`
  (`=== fx.home === "player at home"`). The arcade scoreboard BELOW is INDEPENDENT — keeps YOUR score
  left / target right regardless of venue.
- **TAB key** = jump to next field/option on menu/select screens + HORSE setup (web-form style; not advertised).
- **Em dashes removed from ALL user-facing text** (Vic, transfer emails, menus, HUD, prompts) — owner dislikes them.
- **"Only keeper / rainbow kit" bug FIXED:** `loadKits()` now waits for the sprite-base images
  (`spriteBasesReady()`, ~6s cap) before baking kits — starting a match before the 1.3MB striker sheet
  finished baked NULL sprites (keeper fell back to its raw rainbow tag-atlas, others vanished). Also:
  timestep clamp 0.25→0.12 (kills the physics-burst "jitter" after a load stall) + a "LOADING…" state.

**Deployed baseline (commit `8062200`, on `main`):** in-match HORSE/CLASSIC HUD modes
(`drawHorseHUD`/`drawClassicHUD`), `centredText()` as the single source of truth for box-centred text,
home-menu spacing. (The headline-font part of that commit is now superseded — see above.)

**⚠ LOCAL-DEV GOTCHAS found this session (these caused hours of "it's still showing the old version"):**
- **`serve.py` is now THREADED** (`ThreadingHTTPServer`). The old single-threaded `TCPServer` stalled asset
  requests forever (Chrome idle/preconnect sockets starved the one thread) — that hung the Vic portrait in
  "loading…". KEEP IT THREADED.
- **Local server moved to PORT 5578** (was 5577) so a fresh origin escapes any stuck old service worker.
  `play.bat` starts the server FIRST, then opens the browser after a 2s delay (no "refused to connect" race).
- **`index.html` unregisters the SW + clears caches on localhost** (registers it only in production), so
  local dev always serves fresh.
- **NEVER put `pixel`/`ad`/`advert`/`track` in an asset filename** — ad/privacy blockers silently block them.
  The portrait is `slick_vic.png` (was `vic_pixel.png` → blocked → procedural fallback showed instead).
- **"Laggy / stuttering striker and ball" on the office box = THE DISPLAY, not the code.** 2026-07-01
  perf probe (headless + headed, real match driven via `__dbg`): frame times on this branch and `main`
  are IDENTICAL and clean (the only stall anywhere is a one-off ~220ms kit-bake at match entry — both
  versions). The 4K monitor was running at **29Hz over HDMI** (4K@30 cable/port limit); at 30Hz the 28Hz
  game visibly judders. The monitor supports 4K@60 — fix is DisplayPort/HDMI-2.0, or set 1920×1080@60.
  Before chasing any "lag" report, check `Win32_VideoController CurrentRefreshRate` first.

**Verification — use the `menu-layout-audit` skill** (`.claude/skills/menu-layout-audit/`): headless-Chrome
linter (text overflow / off-screen / edge / overlap / frame-cover) across all menu/career/agent screens.
Run after ANY `draw*` menu/HUD edit: `python serve.py` (NOW PORT 5578, background) then
`node .claude/skills/menu-layout-audit/audit.mjs` (needs `npm install puppeteer-core --no-save` + system
Chrome; PNGs to `%TEMP%/volley_audit`). The in-match HUD isn't auto-audited — drive a real match
(`__dbg.newCareerSim` → Space → Space) and screenshot the canvas.

**Open / next (priority):**
1. **Owner: eyeball this branch live, then deploy to `main`.**
2. **Audio (NEXT TASK) — shortlist is PREPPED in `docs/AUDIO_SHORTLIST.md`** (sources, links, licences,
   wiring notes). Owner auditions + picks, then a session does: (a) **replace the 6 SWF-decompiled SFX**
   in `assets/snd/` (whistle/goal/boos/ooh/kick/post — an IP blocker) with CC0/Pixabay ones + bump the
   `?v=hr5` cache tag; (b) add a looping **jazzy-chiptune menu track**. The audio system
   (`SND` / `sfx.*` / `play()` / `audio()` unlock / `muted`) is at `index.html` ~302–326 and is clean —
   SFX swap needs NO code (same filenames). Owner offered: generate an original loop if sourcing stalls.
3. **Pause-menu kick controls (owner asked):** a KICK-TIMING slider (±1 frame steps, default 0 = NO change
   to the sacred contact timing) PLUS a wind-up-speed control — like the existing DRAG SPEED / RELEASE GLIDE rows.
4. **App / store:** already an installable PWA (use that for app-feel testing). A Capacitor store wrap is
   ~1 day and best done LAST, once IP/audio/content are settled — NOT an engine blocker.
5. IP/launch blockers unchanged: real club/league names (trademark), traced striker/defender art (the 3D
   pipeline replaces it, pending the owner's Mixamo step), self-host fonts (SIL-OFL). See ROADMAP Track C.
6. **`assets/ui/New Vic.png`** (1.18MB) is the Vic-trace SOURCE — kept LOCAL ONLY (gitignored, NOT in the
   repo; it bloats the push + would ship to Pages). It lives on the original dev box; re-add it there to
   re-trace (script pattern: load → downsample ~400px with `imageSmoothingEnabled` + light posterize →
   `slick_vic.png`). Also still open: per-player team select in HORSE; foreign per-team kits; PWA real-phone test.

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
| `docs/AUDIO_SHORTLIST.md` | CC0/royalty-free SFX + menu-music shortlist for the audio swap (§0 next task). |
| `docs/SPRITE_FRAME_SELECTION.md` | The owner's recorded frame picks from the 3D-pipeline contact sheets. |
| `PROJECT_HEALTH_AUDIT.md` | 2026-07-01 full workspace/Git/GitHub health audit + cleanup plan (point-in-time). |

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
