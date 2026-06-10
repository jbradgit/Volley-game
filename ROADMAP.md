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
| 0.1 | Quick-win fixes from AUDIT.md: keeper-atlas error surfacing, `saveCareer` try/catch, dead-code deletion, stop loading `crowd.jpg`/`kit.jpg`, UTC daily seed, `serve.py` → 127.0.0.1, fix stale 14 Hz comment | Correctness + clears the decks | S each | ⬜ |
| 0.2 | **CI safety net**: GitHub Actions + Playwright loads `index.html?cap=1`, asserts zero console errors / no failed asset loads, runs `__dbg.sweep()` against committed golden outcomes, plays one seeded match to MATCHEND | Locks the physics before art swaps and refactors; the `__dbg` harness already exists (index.html:2198). *Started:* `ci/smoke.js` runs the game headlessly in Node (DOM stubs) and drives real shots + render frames — wire into GitHub Actions next | L | 🟨 |
| 0.3 | Delete stale duplicates & junk: `scordagol_web/` (stale fork of the game), 9 MB `Gemini_Generated_Image_*.png`, `game2.zip`, older Ruffle generation + `.js.map` files, `page_flashmuseum.html` | One canonical game; repo ~½ size | S | ⬜ |
| 0.4 | README.md: what SCORDAGOL is now, how to run (Windows + other OS), **the sacred/evolvable split** (physics & scoring are transcribed from the SWF — never change without re-verifying; rendering/UI/modes are fair game), deploy story. Mark HANDOVER.md as historical. | Docs currently contradict the code (AUDIT M-1) | M | ⬜ |

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

The keeper/striker/defender sprites, ball and all six SFX are ripped from the SWF and must be
replaced before publication. The engine makes this easier than it sounds: every sprite has a
documented registration origin and scale (HANDOVER §5), the keeper is atlas-driven
(`keeper_atlas.json` — any same-shaped atlas drops in), and defenders are recoloured live from
one region-tagged base image (index.html:88–136), so a *single* new defender base covers all 20 teams.

| # | Task | Notes | Effort | Status |
|---|---|---|---|---|
| B.1 | New ball + shadow | 41×41 logical, origin (19.6,34.1) — easiest first replacement; procedural 8-bit ball already exists in the menus (`_ball8`, index.html:1209) as a style anchor | S | ⬜ |
| B.2 | New striker sheet (idle + 5 kick frames × 6 kit variants per club) | Keep the existing per-club PNG naming (`striker_<slug>_k0..5`); consider reducing to one base + live recolour like the defender (engine pattern exists) | L–XL | ⬜ |
| B.3 | New defender region-map base | One image with tag colours per region (shirt/shorts/socks/sleeves/stripe) — the live recolour does the rest | M | ⬜ |
| B.4 | New keeper atlas (idle, dive L/R, 3 catch heights) | Match `keeper_atlas.json` schema; fewer frames than the original's 371 is fine — the code only uses 6 ranges (index.html:164) | L–XL | ⬜ |
| B.5 | Replace the 6 SFX (kick, post, whistle, goal, boos, ooh) | Licensed packs or recorded; keep the same filenames | S | ⬜ |
| B.6 | Style decision first: pick ONE art direction (the teletext/8-bit identity suggests chunky pixel-art sprites — also much easier to produce consistently than the current photo-traced look) | Decide before B.2–B.4 | — | ⬜ |

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
| 2.1 | Split `index.html` into ES modules (`physics.js`, `career.js`, `modes.js`, `render/`, `input.js`, `dbg.js`) — no bundler, no TS; HTTP serving is already mandatory so nothing is lost | The 2,310-line monolith is where regressions breed (AUDIT H-2); extraction order + state-object first step in AUDIT T-2.1 | XL (staged) | ⬜ |
| 2.2 | Unit tests for `career.js` (fixtures round-robin, `titleClinched`, odds bounds, offers) via `node --test` | Pure functions, free coverage | M | ⬜ |
| 2.3 | Portable asset scripts (kill `C:\Users\Office` paths) or retire them to the workshop repo | Currently single-machine (AUDIT M-5) | S | ⬜ |
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
| 3.6 | New-mode backlog (park until after launch): season cups, penalty shootout tiebreak for HORSE, weekly challenge archive, achievements | Ideas, not commitments | — | ⬜ |

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
| D1 | Art direction for sprites (gates Track B) | pixel-art (matches teletext identity, cheapest to produce) / clean vector / keep photo-traced look | ⬜ open |
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
