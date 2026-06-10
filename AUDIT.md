# SCORDAGOL / Volley-game — Technical Audit
*Audit date: 2026-06-10 · Commit audited: `3c1e5e4` · Scope: full repo, depth-focused on `index.html` (the entire game)*

---

## Executive Summary

**Overall health: C.** The game itself is in genuinely good shape — the gameplay core is carefully transcribed from the decompiled original, the touch UX has had real iteration, and the code comments are unusually good at recording *why*. What drags the grade down is everything around the game: the repository publicly ships the original copyrighted SWF, its full decompilation, and ripped assets under a "© 2026 WIMP STUDIO · ALL RIGHTS RESERVED" banner; there is no README, no tests, no CI, and the only documentation (HANDOVER.md) describes a project goal the code abandoned several weeks of commits ago; and the whole game lives in one 2,310-line HTML file whose commit history already shows regression/revert cycles.

**Top 3 risks:** (1) IP/legal exposure if this is published or monetised — original SWF, decompiled scripts, ripped art, and real Premier League club names are all tracked in the repo; (2) zero automated safety net — the excellent `?cap=1` debug harness exists but is never run, and history shows regressions slipping through (`29a4a98` "Revert controls to pre-regression state"); (3) a silent fetch failure (`keeper_atlas.json`) that makes the keeper invisible *and* disables saves entirely, with no on-screen error.

**Top 3 opportunities:** (1) the `__dbg.sweep()`/`realShot()` harness is 80% of a deterministic integration-test suite — wiring it to CI is cheap and high-leverage; (2) pruning ~30 MB of binaries, stale duplicates (`scordagol_web/`), and scraped pages would make the repo legible and ~5× smaller; (3) a one-page README replacing the stale HANDOVER would let anyone (including future Claude sessions) work on this without re-deriving what's true.

---

## Repo Map

**Purpose:** "SCORDAGOL" — an HTML5 Canvas remake of the 2007 Flash game *LFC Volley Challenge* (Mousebreaker). It began as an exact 1:1 reproduction (per HANDOVER.md) and has since evolved into its own arcade game: a 20-team career mode with a simulated league, transfer offers, a seeded daily challenge, and a 2-player pass-the-phone "HORSE" mode, with a teletext/Ceefax visual identity. Touch/mobile is a first-class target.

**Stack:** Vanilla JavaScript + Canvas 2D in a single `index.html`. No package manifest, no lockfile, no build step, no framework, no CI. Dev server is stdlib Python (`serve.py`) launched by `play.bat` (Windows). Asset pipeline is ad-hoc Python 3 + PIL scripts in `decomp/`.

**Maturity:** Polished hobby project with apparent distribution ambitions — the menu claims `SCORDAGOL ™ © 2026 WIMP STUDIO · ALL RIGHTS RESERVED` (index.html:1380), the scoreboard has an "ADVERTISE HERE / YOUR MESSAGE IN LIGHTS" panel (index.html:933–934), and a comment plans a "production/app build" (index.html:13–14).

**Key directories:**

| Path | What it is |
|---|---|
| `index.html` | **The entire game** — 2,310 lines: physics, career sim, 3 game modes, renderer, input, audio, debug harness |
| `assets/` | Runtime art + audio (163 files): per-team striker kits, keeper atlas, pitch, SFX, `teams.json` (20 clubs + palette) |
| `decomp/` | Reverse-engineering workshop: decompiled ActionScript (~150 `.as` files), `swf.xml` (14 MB), exported sprites, Python regeneration scripts |
| `scordagol_web/` | **Stale duplicate** deployment snapshot — its `index.html` (89 KB) is an old fork of the live one (140 KB), with a full copy of `assets/` |
| `ruffle/` | Ruffle Flash emulator dist (two wasm generations + source maps, ~28 MB) used by `ruffle.html` to run the original SWF as visual reference |
| `editor/` | Browser-based dev tools (region editor, recolour preview, asset checklist dashboard) |
| `gamezip/`, `original.swf`, `game2.zip` | Three copies of the original copyrighted SWF |
| `page_*.html` | Scraped third-party web pages (one is 212 KB) kept as reference |
| `HANDOVER.md` | The only documentation — a session-handover note frozen at the "exact 1:1 remake" phase |

**Control flow (index.html):** `requestAnimationFrame` loop → fixed-timestep accumulator at 28 Hz (`tick`, :2186–2194) → `swfFrame()` (:601) advances animations + calls `logicStep()` (:641) which is a direct transcription of the SWF's frame_9 (ball physics, goal/save/woodwork resolution) and frame_10 (kick contact, defender deflections, keeper AI). A string-keyed state machine `ST` (:219–224) drives 16 screens; `render()` (:1834) repaints everything each frame. State is ~60 module-level mutable variables (:402–426). Persistence is `localStorage` (career save, best score, settings).

**Surprises found during mapping:** the live game and a stale fork of it coexist (`index.html` vs `scordagol_web/index.html`); a 9 MB AI-generated PNG sits unused at the repo root; and the in-file comments contradict each other about whether game logic runs at 14 Hz or 28 Hz (see A-6).

---

## Audit Report

Findings are labelled **[fact]** (verifiable at the cited line) or **[judgment]** (my assessment).

### Critical

**C-1 · IP/legal exposure across the whole repository — the single biggest issue.**
**[fact]** The repo tracks: the original copyrighted game three times (`original.swf`, `game2.zip`, `gamezip/content/www.extremegamezone.com/games/LiverpoolFCVolleyChallengeV32PC.swf`); its full decompilation (`decomp/scripts/`, `decomp/swf.xml`); art ripped from it (`assets/keeper_atlas_*.png`, `assets/pitch_hd.png`, striker/defender sprites per HANDOVER.md §2 "Real ripped art"); scraped third-party pages (`page_flashmuseum.html`, 212 KB); real Premier League club names and kit colours (`assets/teams.json`); and the original's sound effects ("the ORIGINAL SWF sound effects (decompiled to assets/snd)", index.html:192). Meanwhile the game asserts ownership: `SCORDAGOL ™ © 2026 WIMP STUDIO · ALL RIGHTS RESERVED` (index.html:1380) and carries an ad-sales placeholder (index.html:933–934).
**[judgment]** For a private learning project this is tolerable; for anything published or monetised it is a takedown/legal risk on multiple axes at once (Mousebreaker/publisher rights in the SWF and art, Premier League/club name & badge-adjacent rights, scraped content). Transcribed *gameplay constants* are the defensible part; shipped *binaries, art, audio, and club names* are not. This needs a deliberate decision before any other investment makes sense. **Severity: Critical** (calibrated to the apparent distribution intent; downgrade to Low if the project stays private).

### High

**H-1 · Silent keeper-atlas failure disables saves entirely.**
**[fact]** `fetch("assets/keeper_atlas.json?v=dd").then(...).catch(()=>{})` (index.html:161). If this fetch fails, `KMAN` stays `null`, `drawKeeperTo()` returns immediately (:785), so the keeper is never drawn — and because `savedCheck()` is a *pixel* hit-test against the rendered keeper (:567–578), `hitkeeper` is always 0: every shot on target becomes a goal, silently. The team did this right for `teams.json` (`rosterStatus` surfaced on the menu, :152–158 and :1366–1370) but not for the atlas, and a failed asset is a known deployment mode here (the menu warning literally says "CHECK DEPLOYMENT").
**[judgment]** This is the empty-catch pattern (`catch(e){}` at :64, :203, :207, :1952–1953, :2146…) biting in the one place where failure changes game outcomes rather than degrading cosmetics. **Severity: High** (correctness, silent, plausible trigger).

**H-2 · One 2,310-line god file; all state in ~60 shared mutable variables.**
**[fact]** Physics, career simulation, Monte-Carlo title odds, three game modes, 16 screens of rendering, input (keyboard/mouse/touch/hidden-input soft keyboard), audio, and the dev harness all live in one IIFE in `index.html`. Cross-cutting mutable state is declared at :402–426 (`xball, yball, z, dbx, …, dragging, tableScrollY, …`). Hit-test geometry must be manually kept in sync with draw geometry (e.g. `menuHit` :2086 mirrors `drawMenu` :1340; `clubHit` :2092 mirrors `drawClubSelect` :1408 — the shared-constant pattern at :1338/:1407 exists precisely because these drifted before).
**[fact]** The commit log records the consequences: `29a4a98` "Revert controls to pre-regression state", `f36b733` "Fix club select root cause", `e229fe9`/`53febe9` repeated fixes to the same club-select bug.
**[judgment]** The no-build, single-file approach is a legitimate choice for shipping simplicity, but at 2,310 lines with three game modes it is past the point where every change risks an unrelated screen. ES modules would preserve "no build step" while restoring boundaries. **Severity: High** (maintainability; it is where most future cost accrues).

**H-3 · No automated tests, no CI — despite a ready-made deterministic harness.**
**[fact]** There are zero test files and no CI config anywhere in the repo. Yet `index.html` ships a deterministic verification rig behind `?cap=1`: `__dbg.serve()`, `realShot()` (runs one full physics shot and returns the outcome, :2276–2290), `sweep()` (sweeps all kick timings, :2292–2304), `keeperExtent()`, plus seeded RNG (`mulberry32`, :186) making whole matches reproducible.
**[judgment]** This is 80% of an integration-test suite that nobody runs. Given H-2 and the documented regressions, automating it is the highest-leverage engineering change available. **Severity: High** (testing).

**H-4 · Repository bloat, duplication, and a stale parallel build.**
**[fact]** 1,611 tracked files, 34 MB packed / 85 MB working tree. Largest offenders: `decomp/swf.xml` 14 MB; two generations of Ruffle wasm + their source maps (~28 MB total — `ruffle/bae0d5b…wasm` 13.9 MB, `ecc5e23…wasm` 13 MB, two `.js.map` files); `Gemini_Generated_Image_ivxfmlivxfmlivxf.png` 9 MB, referenced nowhere; the original SWF tracked three times (~1.5 MB); and `scordagol_web/` — a complete stale copy of the game whose `index.html` differs from the live one (89,633 vs 140,233 bytes), with duplicated `assets/` including pre-baked per-team defender PNGs the live code no longer needs (it recolours live via `buildDefenderLive`, index.html:109–136, falling back to the PNGs at :148).
**[judgment]** Beyond clone cost, the real damage is ambiguity: two games, two asset sets, no statement of which is canonical. **Severity: High** for DevEx.

### Medium

**M-1 · Documentation is stale and contradicts the code; no README.**
**[fact]** HANDOVER.md is the only doc. It states the goal is an "exact, 1:1 reproduction… We can differentiate *after* it matches" (HANDOVER.md:3–5) and "Don't change the verified gameplay logic" — but the code is now SCORDAGOL with career/daily/HORSE modes, a 924-px widescreen view, and momentum touch controls. It instructs running from `C:\Users\Office\Volley Game` (:114), references a `tools/` directory (:89) and a `.claude/projects/...` memory file (:95) that are not in the repo.
**[fact]** In-code contradiction: index.html:168–170 says "ball physics / scoring / keeper run at 14 Hz. We mirror that split exactly", while :636 says "game logic runs every frame (28 Hz) — full-rate" and `logicStep()` is indeed called from every 28 Hz `swfFrame()`. HANDOVER §3.7 confirms 28 Hz was a deliberate user-driven change — the older comment was never updated.
**[judgment]** A newcomer cannot tell which behaviours are sacred ("exact SWF") and which are deliberate divergences. **Severity: Medium.**

**M-2 · Dead code and wasted asset loads.**
**[fact]** All verified unreachable/unused: `drawTitle()` (:1278–1316) — `ST.TITLE` (:221) is never entered and the function is never called; `handleTableMenu()`/`tableMenuBtns` (:416, :1965–1968) — never invoked/populated; `keeperX` (:404) — written at :542/:2264, never read (the keeper actually uses `keeperPose.x`); the table swipe-scroll machinery — `tableScrollY` is computed (:1838, :2106–2110, :2153) but `drawTable()` never reads it (leftover from the reverted scrolling table, commit `2b9c627`); the `pendingMode==="quick"` branch (:1412) — nothing sets `"quick"`; and `IMG.crowd` + `IMG.kit` are downloaded at startup (:74–76) but never drawn.
**Severity: Medium** (≈100 lines of trap-laden code + two wasted network requests on every load).

**M-3 · `saveCareer()` can throw and abort the post-match state transition.**
**[fact]** `localStorage.setItem` is uncaught in `saveCareer()` (:240), unlike `loadCareer()` which is wrapped (:239). `commitMatch()` calls `saveCareer()` *before* setting the next state (:531–532). In Safari private browsing (older versions) or with a full quota, `setItem` throws → `commitMatch` aborts → the game soft-locks on the match-end screen.
**Severity: Medium** (low probability, bad failure mode, one-line fix).

**M-4 · "Daily challenge" is neither global nor timezone-stable.**
**[fact]** The seed is the *local* date (`dailyKey()`, :1683–1684), so players in different timezones play different "today"s; the leaderboard is `localStorage` only (honestly labelled "THIS DEVICE", :1744).
**[judgment]** Works as built for one device; under-delivers the implied product promise ("same club + opponent for everyone, today", :1689). UTC-keying is a one-line fix; a shared leaderboard is a product decision (see Open Questions). **Severity: Medium** (product), not a bug.

**M-5 · Asset pipeline runs only on the original author's PC.**
**[fact]** `decomp/bounds.py:3` and `decomp/keeper_labels.py:2` hardcode `C:\Users\Office\Volley Game\…`; `decomp/build_authbg.py:26` hardcodes `C:\Windows\Fonts\arialbi.ttf`. (`gen_kit.py` does it right with `os.path.dirname(__file__)`.) Remaining HANDOVER tasks (§3.4 net animation, §3.6 idle/commentary) depend on these scripts.
**Severity: Medium** for DevEx — blocks anyone else finishing the planned asset work.

### Low

**L-1 · Runtime dependency on Google Fonts** (index.html:15–17). Offline/app builds fall back to monospace; the code's own comment already says "self-host these for the production/app build" (:13–14). **Low** — known, planned.

**L-2 · Dev server binds all interfaces.** `socketserver.TCPServer(('', PORT)…)` (serve.py:14) listens on 0.0.0.0, exposing the project directory read-only to the LAN while playing. Bind `127.0.0.1`. **Low.**

**L-3 · Render-loop inefficiencies.** Full-canvas repaint at display refresh even on static menus; per-frame font auto-fit `while(measureText…)` loops (:851, :897–901, :1496, :1548); ~170 scanline `fillRect`s per frame (`ttClear` :1136–1138); `getImageData` canvases without `willReadFrequently` (:564, offscreen hit-test). **[judgment]** No observed frame problem on desktop; mostly a mobile battery tax. **Low** — don't optimise until something is measurably slow.

**L-4 · Security posture otherwise healthy** — one sentence: no secrets, no `innerHTML`/`eval`, no injection surface (all text is canvas-rendered), storage is `localStorage` only, the two text inputs are sanitised (`sanitizeField`, :1951).

### Strengths (preserve these)

- **Decompilation-grounded correctness.** Physics and scoring are transcribed, not guessed, and the comments cite their SWF source frames (e.g. ":672 frame_10 line 50", `defenders` placements from PlaceObject matrices, :548–554). HANDOVER §5 records exact reference values "do not re-derive".
- **The `__dbg` harness** (:2198–2306) — `realShot`/`sweep`/`keeperExtent` are real deterministic instruments, not printf debugging.
- **Seeded-RNG architecture** — swappable `RAND` + `mulberry32` + pre-rolled `serveQueue` (:184–189, :460–466) gives fair daily/HORSE play cleanly.
- **Failure surfacing done right once** — `rosterStatus` on the menu (:1366–1370) is exactly the pattern H-1 needs copied.
- **Smart live kit recolouring** — `buildDefenderLive` region-tag map (:88–136) replaced 20 pre-baked PNGs with one tagged base image.
- **Why-comments.** e.g. the `stopPropagation` rationale (:2073), drag anchor semantics (:2147–2150), the ODDS model design note (:259–268). Rare and valuable — keep the culture.
- **Touch UX rigour** — pointer capture, relative-drag anchoring, momentum with smoothed velocity, hidden-input soft-keyboard summoning, separate touch/desktop affordances on every screen.

---

## Improvement Strategy

### Theme 1 — Decide the legal posture, then separate "workshop" from "product" *(addresses C-1, H-4)*
**Target state:** the repo (or at minimum the deployable artifact) contains only assets you have the right to ship. The reverse-engineering workshop (`decomp/`, SWFs, Ruffle, scraped pages) lives in a separate private archive repo or is deleted once its remaining value (net animation, idle anims per HANDOVER §3.4/3.6) is extracted. `scordagol_web/` is deleted; one canonical game.
**Principle:** a repository is a statement of what the project *is*. Right now it states "decompiled commercial game with my name on it."
**Trade-off:** if the owner's intent is strictly private/educational, downgrade this to "prune for size/clarity only" — don't spend effort laundering history for a private repo.

### Theme 2 — Automate the safety net you already built *(addresses H-3, enables everything else)*
**Target state:** CI (GitHub Actions) serves the repo, loads `index.html?cap=1` headlessly (Playwright), and asserts: page loads with zero console errors; all fetched assets 200; `__dbg.sweep(450,20,37,true)` returns a known-good outcome table; one scripted seeded match reaches `MATCHEND` with the expected score; `__dbg.fakeSeasonEnd()`/`clinchTitle()` screens render.
**Principle:** lock in current behaviour *before* restructuring (Theme 3). The physics is the crown jewel and is already deterministic — assert it.
**Done means:** CI red on any physics outcome change or load-time console error.

### Theme 3 — Break the monolith along its natural seams, without adding a build step *(addresses H-2, M-2)*
**Target state:** `index.html` becomes a thin shell loading ES modules: `physics.js` (the sacred transcribed core — `logicStep`, `savedCheck`, constants), `career.js` (table/odds/offers sim — pure functions over `CAR`, trivially unit-testable), `modes.js` (daily/HORSE), `render/*.js`, `input.js`, `dbg.js`. Dead code from M-2 deleted in the process.
**Principle:** module boundaries should match change boundaries — history shows touch-input and menu-rendering change weekly while physics must never change; they shouldn't share scope.
**Trade-off:** keep zero build tooling (no bundler, no TS). ES modules require HTTP serving — already a hard requirement (HANDOVER §1: `file://` breaks the canvas hit-test), so nothing is lost.
**What I'm explicitly NOT recommending:** TypeScript, a framework, a bundler, or server infrastructure. Wrong weight class for this project's maturity, and the no-build property is genuinely valuable here.

### Theme 4 — Make the docs tell the truth *(addresses M-1, M-5)*
**Target state:** a README that states what SCORDAGOL is *now*, how to run it (Windows + non-Windows), the sacred-vs-evolvable split ("physics/scoring are transcribed from the SWF — never change without re-verifying; everything above `render()` is fair game"), and the 14 Hz→28 Hz decision. HANDOVER.md gets a banner ("historical — superseded by README") or is rewritten. The stale 14 Hz comment at index.html:168–170 is corrected.
**Principle:** docs that contradict code are worse than no docs — they actively misdirect (including AI agents working from HANDOVER's "do not change" instructions against the current design).

### Measurable "done" signals
- CI exists and fails on: console errors at load, missing assets, any changed `sweep()` physics outcome.
- Fresh clone < 10 MB; zero duplicate copies of the game; `git ls-files | wc -l` < 400.
- Zero unreachable functions (drawTitle, handleTableMenu, quick-play branch, etc. removed).
- Keeper-atlas failure produces an on-screen error (same pattern as `rosterStatus`).
- README exists; HANDOVER marked historical; no doc statement contradicts code.
- A written owner decision on IP posture exists (even if the decision is "stays private, ship nothing").

---

## Task Plan

### Quick wins (do immediately — all S, high impact)

| ID | Task | Why |
|---|---|---|
| QW-1 | Surface keeper-atlas load failure on-screen (copy the `rosterStatus` pattern) + retry once | Fixes H-1, the only silent gameplay-corrupting failure |
| QW-2 | Wrap `saveCareer()` setItem in try/catch with a visible "SAVE FAILED" notice | Fixes M-3 soft-lock |
| QW-3 | Delete dead code: `drawTitle`+`ST.TITLE`, `handleTableMenu`/`tableMenuBtns`, `keeperX`, table-scroll vestiges, `"quick"` branch; stop loading `crowd.jpg`/`kit.jpg` | Fixes M-2; ~100 lines + 2 requests |
| QW-4 | Delete unreferenced bloat: 9 MB Gemini PNG, `game2.zip`, older Ruffle generation + both `.js.map` files, `page_flashmuseum.html` | Halves repo size with zero risk |
| QW-5 | `serve.py`: bind `127.0.0.1`; key `dailyKey()` to UTC | Fixes L-2 + the cheap half of M-4 |
| QW-6 | Fix the stale 14 Hz comment block (index.html:168–170) | Removes the worst doc/code contradiction |

### Milestone 0 — Safety net *(before any restructuring)*

**T-0.1 · Headless CI smoke + physics regression suite** — **Effort: L · Risk: none (additive) · Depends: nothing**
GitHub Actions workflow: python http.server + Playwright loads `index.html?cap=1`; asserts zero console errors and all asset requests 200; runs `__dbg.sweep()` at 2–3 fixed `(manX, vel, ang)` tuples and diffs against committed golden JSON; scripts one seeded 10-ball match to `MATCHEND` and asserts the final score. *Acceptance:* CI green on `main`; deliberately changing a physics constant turns it red.
**Implementation sketch:** (1) `npm`-less is impossible for Playwright — add a minimal `package.json` confined to `ci/` so the game itself stays build-free. (2) In the test, use `page.evaluate(() => __dbg.sweep(450,20,37,true))`; note `?cap=1` already drives ticks from `setInterval` (index.html:2199) so headless rAF throttling is solved by the existing design. (3) Golden files: commit `ci/golden/sweep_450_20_37.json`; compare with exact equality — the sim is deterministic when `noDef=true` and the keeper roll (`rnd(10)<8`, :722) is the one nondeterminism left, so either seed `RAND` first via a new `__dbg.seed(n)` (3-line addition) or assert only the defender-free fields. (4) Gotcha: fonts fetch from Google in CI — assert "no failed *local* requests" or stub the font hosts.

**T-0.2 · Golden-screenshot sanity (optional)** — **Effort: M · Risk: none · Depends: T-0.1**
Capture menu / table / in-match canvases via `toDataURL` (the documented `?cap=1` flow) and diff at a loose threshold to catch blank-screen regressions. *Acceptance:* a deliberately broken asset path fails CI.

### Milestone 1 — Critical & correctness fixes

**T-1.1 · IP decision + repo separation** — **Effort: M (decision) + L (execution) · Risk: low technically; the decision itself is the point · Depends: owner input (see Open Questions)**
Owner decides: private-forever vs publish-clean. If publish-clean: move `decomp/`, all SWF copies, `gamezip/`, `ruffle/`+`ruffle.html`, `page_*.html`, ref images to a private `volley-workshop` repo; replace ripped art/SFX and real club names in the shipping build (fictional club names are a find/replace in `teams.json` — the engine is already fully data-driven, a strength); rewrite git history (`git filter-repo`) so the SWF/decomp never existed in the public repo. *Acceptance:* `git log --all -- original.swf` empty on the public repo; game plays identically with replacement data.
**Implementation sketch:** (1) Create the private archive first, push full current history to it — nothing is lost. (2) In the public repo run `git filter-repo --invert-paths --path original.swf --path game2.zip --path gamezip --path decomp --path page_flashmuseum.html …` (coordinate force-push; only one contributor, so cheap now — it gets expensive later). (3) Club names: `teams.json` slugs are also asset filename keys (`striker_<slug>_k0.png`, index.html:144) — rename JSON slugs and asset files together; one sed + one `git mv` loop. (4) Gotcha: HANDOVER's remaining tasks (net animation §3.4) need `decomp/` — finish extracting those two assets *before* the split, or do the work from the archive repo.

**T-1.2 · Ship QW-1 and QW-2** (if not already done) — **Effort: S · Risk: minimal · Depends: T-0.1 ideally first**

**T-1.3 · Delete `scordagol_web/`** and document the actual deploy story (what produced it? a script? by hand?) in the README; if a deploy snapshot is needed, generate it, don't track it (`.gitignore` already anticipates `scordagol_web.zip`). — **Effort: S · Risk: low — verify nothing serves from it first · Depends: nothing**

### Milestone 2 — High-leverage restructuring

**T-2.1 · Split `index.html` into ES modules** — **Effort: XL → break down as below · Risk: medium (mitigated by M0) · Depends: T-0.1 hard requirement**
Order of extraction, each its own PR with CI green between: (a) `dbg.js` (pure additive move, proves the import wiring); (b) `physics.js` — `logicStep`, `savedCheck`, `newServe`, the constants block :167–190, exporting a state object instead of 40 loose `let`s; (c) `career.js` — `makeFixtures`, `simRound`, `computeTitleOdds`, `standings`, offers (pure, unit-testable with plain `node --test`); (d) `modes.js`, `input.js`, `render/` last (they churn most). *Acceptance:* CI unchanged-green at every step; `index.html` < 300 lines; `career.js` has node unit tests for `titleClinched`, `computeTitleOdds` bounds, fixture double-round-robin invariants.
**Implementation sketch:** (1) The IIFE's shared-variable web is the hazard; introduce a single `const G = {…}` game-state object first *inside* the monolith (mechanical rename, CI verifies), then extraction becomes cut-and-paste. (2) Keep the `__dbg` API surface byte-identical so T-0.1 goldens keep working. (3) Gotcha: `savedCheck` needs `drawKeeperTo` — renderer and physics touch at exactly this one function; pass it in as a dependency rather than importing render into physics (it's also the reason `file://` is banned — keep that comment).

**T-2.2 · README + HANDOVER triage** — **Effort: M · Risk: none · Depends: T-1.1 decision (affects run instructions)**
README: what it is, play controls, run on Windows (`play.bat`) and elsewhere (`python3 serve.py`), the sacred/evolvable code split, the 28 Hz decision, deploy story, asset-pipeline pointer. Mark HANDOVER historical. *Acceptance:* a newcomer can run the game and knows what not to touch, with zero contradictions.

**T-2.3 · Portable asset scripts** — **Effort: S · Risk: none · Depends: T-1.1 (scripts may move to workshop repo)**
Replace the three hardcoded `C:\` paths with `__file__`-relative paths (pattern already in `gen_kit.py`); document required inputs. *Acceptance:* `bounds.py` runs on Linux/macOS against the repo checkout.

### Milestone 3 — Quality & polish

| ID | Task | Effort | Risk | Depends |
|---|---|---|---|---|
| T-3.1 | Self-host VT323 + Press Start 2P (woff2 in `assets/fonts/`) | S | low | — |
| T-3.2 | `willReadFrequently:true` on the two read-back canvases (:564, defmap) | S | none | — |
| T-3.3 | Skip repaint on static teletext screens (dirty-flag: redraw only while `ttSub` reveal is active, ticker scrolls, or cursor blinks) — battery win on mobile | M | low-med (visual regressions; lean on T-0.2) | T-0.2 |
| T-3.4 | Finish HANDOVER §3.4 net animation + §3.6 idle/commentary (the two remaining 1:1 gaps) — or formally drop them now that the game has its own identity | L | med | T-2.3, owner intent |
| T-3.5 | Decide daily-challenge ambition: keep device-local (rename to "TODAY'S BEST ON THIS DEVICE" everywhere) or add a serverless leaderboard | S–XL | — | owner intent |
| T-3.6 | Unit tests for `career.js` edge cases (clinch math :322–328, odds floor :304–310, offers slicing :385–398) | M | none | T-2.1c |

---

## Open Questions (need a human)

1. **Distribution intent (gates C-1/T-1.1, the whole Milestone 1):** Is SCORDAGOL meant to be published/monetised (the ™/©/ad-board suggests yes)? If yes — are you prepared to replace ripped art/SFX and real club names, and does the "exact 1:1 reproduction" goal in HANDOVER still stand, or is SCORDAGOL now officially its own game? These pull in opposite directions and the repo currently does both.
2. **Is the `decomp/` workshop still active?** The two remaining HANDOVER tasks (net animation, idle/commentary) are the only things that need it. Finish them first, or archive now?
3. **Daily challenge ambition:** is a real cross-device leaderboard wanted (implies a backend or a serverless KV store), or should the UI stop implying global competition?
4. **Target platforms for "the production/app build"** (index.html:13): web-only, PWA, or app-store wrapper? Affects font self-hosting, fullscreen handling, and whether the 85 MB asset folder needs a packing pass.
5. **Performance target:** is there a real device where the game currently struggles? I found no evidence of frame problems; T-3.3 is speculative until someone names a device/battery complaint.

---

*Lighter-review areas: `editor/*.html` (dev-only tools, skimmed), `decomp/` Python beyond the path issues (one-shot generators), Ruffle vendor code (not reviewed — vendored dist). The core game (`index.html`) was read in full.*
