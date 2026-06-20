# SCORDAGOL — Road to Publication

*Owner goal: publish (and monetise) the game. This roadmap sequences everything needed to get
there. Findings and severities referenced here are detailed in `AUDIT.md`. The stadium/asset
programme is specified in `docs/STADIUM_ASSET_SPEC.md` + `docs/stadium_grid_template.png`.*

**Status legend:** ⬜ not started · 🟨 in progress · ✅ done

---

## The one-paragraph strategy

Publication makes the audit's Critical finding (C-1) the spine of the plan: **every pixel, sound
and name in the shipped game must be ours.** Rather than treating that as a chore, the asset
replacement programme *is* the product upgrade you already want — the new layered stadium
(backdrop / ad hoardings / animated goal) replaces the ripped pitch art, deletes the baked-in
"zokker" watermark, unlocks the net animation that's been blocked since HANDOVER §3.4, and
creates the monetisation surface (sellable hoarding slots). Engineering work (CI safety net,
then modularisation) runs alongside so asset swaps and feature work can't silently break the
transcribed physics — the one thing that must never change.

---

## Phase 0 — Foundations *(do first; small, unblocks everything)*

| # | Task | Why | Effort | Status |
|---|---|---|---|---|
| 0.1 | Quick-win fixes from AUDIT.md: keeper-atlas error surfacing, `saveCareer` try/catch, dead-code deletion, stop loading `crowd.jpg`/`kit.jpg`, UTC daily seed, `serve.py` → 127.0.0.1, fix stale 14 Hz comment | Correctness + clears the decks | S each | 🟨 `serve.py`→127.0.0.1 done 2026-06-20; the rest are `index.html` edits, still pending |
| 0.2 | **CI safety net**: headless physics regression test in CI; later, an optional Playwright browser pass (real-browser console-error / failed-asset checks + screenshot approval) | Locks the physics before art swaps and refactors; the `__dbg` harness already exists (index.html:2901, gated on `?cap=1` at :2893). **✅ 2026-06-20:** `ci/smoke.js` runs the whole game headlessly in Node (DOM stubs) and **asserts golden outcomes** (shot resolution, goal score, 49/51-event winning seasons, cup/euro/intl trophies, kit build) — now **wired into GitHub Actions** (`.github/workflows/ci.yml`) on every push + PR → red on any physics change. Plus `node --test` golden suites sharing `ci/harness.js`: `ci/physics.test.js` (goal/miss geometry — net/bar/posts — + determinism) and `ci/career.test.js` (season/cup/Europe/World-Tournament + trophy invariants). *Remaining:* the Playwright browser pass. | L | 🟨 |
| 0.3 | Delete stale duplicates & junk. **✅ 2026-06-20:** `Gemini_Generated_Image_*.png`, `game2.zip` (SWF dup), `scordagol_web/` (pre-`buildKit()` fork w/ per-team baked PNGs), all `page_*.html` scrapes, Ruffle `.js.map` source maps. **Remaining:** the two Ruffle `.wasm` (~27 MB) turned out to be the baseline + SIMD ("extensions") variants of **one** 0.2.0 build — both required at runtime, *not* an old generation. Reclaiming them means dropping the Ruffle / `original.swf` reference player entirely (owner call — `original.swf` is the sacred-physics source, constraint #1). | One canonical game; smaller working tree | S | 🟨 |
| 0.4 | README.md: what SCORDAGOL is now, how to run (Windows + other OS), **the sacred/evolvable split** (physics & scoring are transcribed — never change without re-verifying; rendering/UI/modes are fair game), deploy story. Mark HANDOVER.md as historical. | Docs currently contradict the code (AUDIT M-1) | M | 🟨 **✅ 2026-06-20 `README.md` written** (IP-safe framing — no trademarked game/club named; corrects the stale line count; coexists with HANDOVER). *Open owner decision:* demote `HANDOVER.md` to historical, or keep it as the living dev doc the README links to. |

**Exit criteria:** CI green on main and red on any physics change; fresh clone < 40 MB; README exists.

---

## Phase 1 — Own every pixel (clean-room asset programme)

> Work through this in the order below — each step is independently shippable and the game keeps
> working throughout. **Track A is the stadium; it's first because it's the monetisation surface
> and the current art carries a third-party watermark.**

### Track A — Layered stadium *(spec: `docs/STADIUM_ASSET_SPEC.md`)*

The background becomes three independent layers — exactly the split you proposed:

1. **Backdrop** (one asset, 924×400 logical): stadium bowl + grass, **no goal, no boards**.
   Only two horizontal seams constrain it (crowd ends y≈104–138, grass starts y143) and both
   hide under the hoardings — this is what makes AI generation viable where previous attempts
   failed. Generate wide, then 3-slice-stretch to fit; never ask a model to hit the grid in one shot.
2. **Hoardings** (7 assets, 132×34 logical each + `ads.json` manifest): the ad band at y104..138.
   Flat rectangles — trivial to produce, and each slot is independently replaceable, which is the
   whole monetisation mechanism (see Phase 3).
3. **Goal + net** (one animatable layer at field x115..450, y40..170): posts at x135/430, bar at
   y58, line at y163. **Recommended: draw it procedurally in canvas** — pixel-exact by
   construction, the net bulge on goals comes free, zero IP risk. This finally delivers
   HANDOVER §3.4 (animated net), which was blocked only because the net is baked into the pitch.

| # | Task | Effort | Status |
|---|---|---|---|
| A.1 | Code: layer plumbing — `drawBackdrop`/`drawHoardings`/`drawGoal` replacing `drawStadiumSides`+`pitchBg`; ads manifest with visible fallback; goal bulge + woodwork shake triggers (spec §5) | M–L | ✅ |
| A.2 | Produce backdrop v1 — procedural early-2000s stadium (`artgen/gen_backdrop.py` → `assets/stadium/backdrop.png`), template-aligned | M | ✅ |
| A.3 | House + placeholder sponsor boards (`artgen/gen_boards.py` → `assets/ads/` ×7 + `ads.json`, all fictional brands) | S | ✅ |
| A.4 | Procedural goal + net bulge + woodwork shake (drawn inside the leftFooted mirror; `drawGoal()` in index.html) | M | ✅ |
| A.5 | Validate: compositor mock vs template ✅ (`artgen/preview_mock.py`); headless smoke ✅ (`ci/smoke.js`). **Remaining: owner plays it in a real browser + approves, then delete `pitch_hd.png`/`pitch.jpg`/`crowd.jpg`/`kit.jpg`** | S | 🟨 |

### Track B — Characters, ball, sounds

The keeper/striker/defender sprites + ball + 6 SFX are ripped from the SWF and must be
replaced before publication. **The recolour SYSTEM is done** (region-tag/UV contract +
`build_kit()` + home/away/patterns); what remains is a clean **art source** that's both
high-quality and 100% original. After procedural (too crude) and traced-from-original
(derivative) attempts, the decision is **3D pre-rendered sprites** — pipeline built &
tested (`artgen/render_sprites.py`), blocked on the Mixamo shopping list
(`docs/ART_SOURCING.md`, HANDOVER §3). The 3D renders feed the same tag system unchanged.

| # | Task | Notes | Effort | Status |
|---|---|---|---|---|
| B.0 | Recolour system (tag/UV contract, `build_kit`, home/away, patterns, clash) | Done + reused by every art source | L | ✅ |
| B.1 | Ball + shadow | `gen_sprites.py` pentagon ball, geometry matched | S | ✅ |
| B.2–B.4 | Striker / defender / keeper ART | **In flight — switching to 3D pipeline.** Live now: traced striker/defender (placeholder, derivative) + procedural keeper. Replace via `render_sprites.py` once Mixamo FBX land | XL | 🟨 |
| B.5 | Replace the 6 SFX (kick, post, whistle, goal, boos, ooh) | Licensed packs or recorded; keep the same filenames | S | ⬜ |
| B.6 | Art direction | **Decided: 3D pre-rendered, one style for all three characters** (`docs/ART_SOURCING.md`) | — | ✅ |

### Track C — Names, fonts, history

| # | Task | Notes | Effort | Status |
|---|---|---|---|---|
| C.1 | Rebrand the 20 clubs to fictional names/kits | `teams.json` is the single source — but slugs are also asset-filename keys (`striker_<slug>_*`), so rename JSON + files together. Kit colours can stay (colours aren't protectable; names/badges are) | M | ⬜ |
| C.2 | Self-host VT323 + Press Start 2P (OFL-licensed) in `assets/fonts/` | Removes the Google Fonts runtime dependency | S | ⬜ |
| C.3 | Split the workshop: move `decomp/`, all SWF copies, `gamezip/`, `ruffle/`+`ruffle.html`, `page_*.html`, ref images to a **private** archive repo; `git filter-repo` the public history so the copyrighted material never existed in it | Do **after** Tracks A/B no longer need decomp reference material. Single contributor = cheap to force-push now, expensive later | L | ⬜ |
| C.4 | Licence + credits screen (font licences, sound licences, "not affiliated with any real club/league") | App stores ask | S | ⬜ |

**Exit criteria:** the game contains zero ripped art/audio, zero real club names, no third-party
watermarks; public repo history is clean; CI screenshots approved.

---

## Phase 2 — Engineering for change

| # | Task | Why | Effort | Status |
|---|---|---|---|---|
| 2.1 | Split `index.html` into ES modules (`physics.js`, `career.js`, `modes.js`, `render/`, `input.js`, `dbg.js`) — no bundler, no TS; HTTP serving is already mandatory so nothing is lost | The ~3,000-line monolith is where regressions breed (AUDIT H-2); extraction order + state-object first step in AUDIT T-2.1 | XL (staged) | ⬜ |
| 2.2 | Unit tests for `career.js` (fixtures round-robin, `titleClinched`, odds bounds, offers) via `node --test` | Pure functions, free coverage | M | 🟨 **✅ 2026-06-20:** `ci/career.test.js` (8 tests) asserts career invariants through the `__dbg` harness — calendar size, 114-pt/1st all-win season, cup/Europe/World-Tournament structure (49/51/42-match seasons), trophy + caps accounting over 3 seasons, `titleClinched`, offers. Shares `ci/harness.js` with `smoke.js`; wired into CI. *Becomes true unit tests after the 2.1 split.* |
| 2.3 | Portable asset scripts (kill `C:\Users\Office` paths) or retire them to the workshop repo | **✅ verified 2026-06-20:** every `artgen/*.py` (and `play.bat`/`serve.py`) already derives paths from `__file__`/`%~dp0` — no hardcoded machine paths remain (AUDIT M-5 resolved). The only machine-specific bit is the *documented* desktop-Blender run command for the 3D pipeline (a command, not a path baked into code). | S | ✅ |
| 2.4 | Mobile battery pass: skip repaints on static teletext screens | Only if a real device shows drain; measure first | M | ⬜ |

---

## Phase 3 — Product & monetisation

| # | Task | Notes | Effort | Status |
|---|---|---|---|---|
| 3.1 | **Hoarding sales pipeline**: remote `ads.json` (bundled fallback), per-match seeded rotation, impression counter in localStorage → simple analytics ping later | In-canvas boards are *sponsorship* (static images you sell directly), not programmatic ad-network inventory — ad networks need DOM/iframe and would wreck the game feel. Price as "your logo in the game", like a real hoarding | M | ⬜ |
| 3.2 | Scoreboard "ADVERTISE HERE" panel → real sponsor slot (clickable on menu/result screens only, never mid-play) | The panel already exists (index.html:933) | S | ⬜ |
| 3.3 | Daily challenge, real version: UTC seed (Phase 0) + shared leaderboard | Needs a tiny backend (a single serverless KV endpoint is enough: POST score, GET top-N). Until then, keep the honest "THIS DEVICE" label | M–L | ⬜ |
| 3.4 | "Sponsored Daily" — daily challenge presented-by branding | Free once 3.1 + 3.3 exist | S | ⬜ |
| 3.5 | Remaining 1:1 polish from HANDOVER: idle/commentary animations (§3.6) — or formally drop and close | Decide; SCORDAGOL is its own game now | M | ⬜ |
| 3.6 | **Career universe expansion** — foreign leagues, domestic cups, European competitions, national team + nationality select, reputation/budget management layer. Full design: `docs/CAREER_DESIGN.md` (phases E0–E6; E0 calendar refactor first, pairs with task 2.1) | Owner-approved direction | L–XL per phase | 🟨 cups/Europe/intl shipped |

---

## Phase 4 — Launch

| # | Task | Notes | Effort | Status |
|---|---|---|---|---|
| 4.1 | Hosting + domain: any static host (GitHub Pages/Netlify/Cloudflare Pages) — the game is static files; add cache-busting via file hashes instead of the current `?v=` strings | CI deploys on tag | M | ⬜ |
| 4.2 | PWA wrapper: manifest + service worker (offline play, "Add to Home Screen") — fonts/assets all local after C.2 | The mobile UX work is already done; this is packaging | M | ⬜ |
| 4.3 | Distribution: itch.io / web portals first (zero gatekeeping), app stores later via wrapper (Capacitor) only if traction justifies it | Don't pay the app-store tax up front | M–XL | ⬜ |
| 4.4 | Pre-launch checklist: privacy note (localStorage only, no tracking — keep it that way as long as possible), credits/licences screen, 404-proof asset loading (every fetch has a visible failure path), performance check on a low-end Android | | M | ⬜ |

---

## Decision log (owner calls — record answers here)

| # | Decision | Options | Status |
|---|---|---|---|
| D1 | Art direction for sprites (gates Track B) | **RESOLVED: 3D pre-rendered sprites** (realistic form, smooth motion, one style, original). Pipeline built; needs Mixamo FBX — `docs/ART_SOURCING.md` | ✅ |
| D2 | Club rebrand approach | fully fictional names / parody names ("Manningham City") — fictional is safer | ⬜ open |
| D3 | Daily leaderboard backend | none for v1 / serverless KV / third-party (e.g. a games-portal API) | ⬜ open |
| D4 | Drop or finish HANDOVER §3.6 idle/commentary | | ⬜ open |
| D5 | Workshop repo timing — what still needs `decomp/` before the split (C.3)? | | ⬜ open |
| D6 | Trademark check on "SCORDAGOL" before spending on branding | | ⬜ open |

## Working rules (carry-over from the original project culture)

- **Never change `logicStep`/`savedCheck`/the constants block** without CI goldens proving
  outcomes are identical — the transcribed physics is the product's soul.
- Every new asset/`fetch` must have a **visible** failure path (the keeper-atlas lesson).
- Derive, don't eyeball: new layout/asset numbers go in `docs/` next to how they were derived
  (the grid template is the pattern).
- One canonical game: no copies of `index.html`; deploy artifacts are generated, not tracked.
