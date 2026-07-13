# SCORDAGOL — Handover / State of Play

**Read this first.** Single source of truth for picking the project up on a new
device or a fresh session. Last updated: 2026-07-13.

---

## 0. CURRENT STATE (2026-07-10) — READ THIS FIRST (supersedes §3 below)

The 3D-sprite pipeline (old §3) is **long DONE and deployed**. **Live site:**
https://jbradgit.github.io/Volley-game/ (GitHub Pages serves `main`).

### ⇄ PICKING UP ON ANOTHER DEVICE (2026-07-10)
**Everything below (rounds 12–19b — the whole `claude/career-journey` line) is now MERGED TO `main`
and deployed.** `main` is the single current truth; there is no undeployed work in flight. On a
fresh/other machine just:
```
git fetch origin && git checkout main && git reset --hard origin/main
```
**⚠️ 2026-07-13 — the Git history was REWRITTEN (ROADMAP C.3 IP purge), so the `reset --hard` above
is now mandatory (an old clone can't fast-forward). Never merge a pre-2026-07-13 clone back in — it
would drag the removed Flash material back. Exactly what was removed and why:**
[`docs/IP_HISTORY_PURGE.md`](docs/IP_HISTORY_PURGE.md).

(If you have a stale local `claude/career-journey` branch on that device, it is behind — delete it
or reset it; do NOT merge it back in.) Then reinstall the ephemeral dev deps:
`pip install numpy pillow` (artgen) and `npm install puppeteer-core --no-save` (layout audit). Run
locally with `play.bat` → http://localhost:5578/index.html. Next tasks are in **§0 "Open / next"**
below (unchanged: C.3 history rewrite is the top Claude-doable item).

**Git state right now (2026-07-10, deploy session):**
- **Owner round 19 + 19b (DEPLOYED to `main`) — work-rate toggle REMOVED,
  condition→balls tightened, reputation gates role, career-home re-prioritised:** the round-17
  CONSERVE/NORMAL/ALL-OUT toggle (`CAR.workRate`, keys 1/2/3/W, the clickable CONDITION panel) is
  **gone** — condition now maps straight to balls via a continuous `energyFactor(e)` curve (≥75%
  ×1.0 … <18% ×0.25), no player choice in between. Drain is faster (`ENERGY_BASE_COST 42` flat,
  `RECOVER_BASE` 14→9, tuned against a throwaway sim so a starter needs a shake every 2-3 games).
  **Reputation now caps your role** (`roleFor(trust, rep)`: rep<15 blocks starter, rep<8 blocks
  sub) — a nobody with maxed trust still only gets a bench role, thresholds calibrated against
  rep's real growth rate so it binds briefly not permanently. **Debut cameo starts on ONE ball**
  (was flat 3), climbing to 3 once trust≥25. **Targets scale super-linearly** above 1 ball
  (`targetK(tb) = tb<=1 ? tb/10 : (tb/10)^0.8`). **Shakes renamed** SINGLE/DOUBLE SCOOP → 1/2
  SCOOP SHAKE. **Career home**: POSITION cell dropped (redundant with the table above), AGE/
  REPUTATION/board-goal demoted to a slim discreet line, STATUS bar now just FORM+CONDITION (was
  5 cramped cells); league table row height 25→22 to fit. Design: `docs/CAREER_DESIGN.md` §11g
  (§11e/§11f marked superseded where they describe the removed toggle). dbg: `setWorkRate`/
  `workRateSim` REMOVED; `lifeInfo()` gained `msgText`. CI 54/54 + smoke, layout audit clean (45
  screens, verified with real Puppeteer mouse-hover + screenshot tests, not just the linter).
  **Round 19b (visual pass, advisor-planned):** the career-home bottom is now **open teletext on
  black** (the `#0a1224` navy panels are gone from this screen — they clashed with the black table
  + blue header) on a strict SP=8 grid; the one framed box is NEXT MATCH with a **fieldset title**
  (neon frame now complete all round — the old blue title bar overpainted the top edge); the
  cryptic discreet line is now **four labelled two-tone fields** — `AGE: · REP: · BOARD: · TITLE
  ODDS:`. Design: `docs/CAREER_DESIGN.md` §11g "Round 19b". ⚠ the layout linter does NOT catch
  vertical spill inside a box — the section-bottom ≤496 budget (ticker clip 497) is guarded by a
  code comment only.
  **Not yet done by this round**: no full stochastic multi-season sim (validated via an isolated
  energy sim + a deterministic 40-match trace + the existing CI season-autoplay tests instead) —
  flagged as an acceptable risk, not a gap to silently ignore if a future session sees weird
  trust/rep/role behaviour over many real (non-forced) seasons.
- **Owner round 18 (COMMITTED on the branch) — player age + harder XI + decluttered home:**
  new careers start at **17** (`CAR.age`), age +1/season; `ageFatigue` multiplier on energy cost
  (≤20 .9 / prime 1.0 / 31-33 1.1 / 34-36 1.25 / 37+ 1.5); Vic warns at 34; **retirement at 38** →
  `ST.RETIRE` testimonial (honours board + accolade + Vic sign-off; CONTINUE CAREER on a retired
  save replays it). **Harder starting XI**: starter threshold 70→80, sub 30→35, trust gains cut,
  teenager (≤18) 25% slower, off-season drift +6→+4 — now ~23-30 matches to crack the XI (was ~10).
  **Decluttered career home**: the crammed footer → one consolidated 5-cell STATUS bar
  (POSITION/FORM/AGE/REPUTATION/CONDITION+work-rate) + a clean NEXT MATCH panel + a tidy £ SHOP /
  TROPHIES row + ticker. dbg: `retireSim`, journeyInfo gains `age`/`ageFatigue`/`retired`,
  setJourney gains `age`. Design `docs/CAREER_DESIGN.md` §11f. CI 54/54 + smoke, audit clean.
- **Owner round 17 (COMMITTED on the branch) — faithful NSS energy state-machine + work rate,
  £2 starting contract, deeper shop:** energy is now a **% state-machine** (a match burns the bar
  by WORK RATE: CONSERVE 22 / NORMAL 48 / ALL OUT 78, scaled by role; weak weekly recovery
  `RECOVER_BASE 14` × rest fraction; stacks = property +5/+15/+25/+35, trainer refund +10/+12/+15,
  shakes +50/+100). **Work rate** (`CAR.workRate`, click the CONDITION panel or keys 1/2/3/W)
  trades balls for energy (`roleTarget + (wr-2)*2`); tired legs cap the rate you can play.
  **Contract**: debut ~£2/game, **win bonus but NO goal bonus**, start money £10. **Shop depth**:
  4th lifestyle tier per category (rep up to +10), sponsor ladder now **6 rungs**. New: `ST.PAYDAY`
  drops the goal line; `effectiveWorkRate`/`maxWorkRate`/`matchEnergyCost`/`matchRecovery` in
  `applyJourney`. dbg: `setWorkRate`/`workRateSim`. Design: `docs/CAREER_DESIGN.md` §11e. Tuning:
  `scratchpad/smart_probe.js` (smart player holds ~60% energy; helpless one spirals to 0 in ~3).
- **E7 "The Journey" + E8 "The Life" + rounds 14-16** (now on `main` as part of this deploy).
  Full CI green, layout audit clean.
- **Owner round 16 (COMMITTED on the branch) — economy depth + energy realism + PAY DAY:**
  (1) **bank balance consistent + labelled** — `bankRight()` stamps `BANK £x` top-right on every
  career header (home top-bar is now `CAREER · SEASON N` centred, bank right); exceptions: S-MAIL
  client + contract paper (own identities). (2) **career-home hover explainers** (form / position /
  odds / reputation / condition / next-match / bank). (3) **energy = NSS rest-day model**
  (`restDaysFor` league 7d / cup 4d / Euro 3d / intl 5d × `ENERGY_REC_PER_DAY 3`; drain
  `4 + 3.6×role-target-balls`; helpless starter exhausted in ~5 games, congested weeks bite,
  subs stay fresh); tiredness harsher (**−2 under 60%, −4 under 40%**). (4) **trainers mirror NSS
  staff** — dearer = far longer contract (Beef £70/8g, Sven £220/24g, Proteina £520/60g). (5)
  **economy slowed** (wages −30%, goal bonus 5%-of-wage, sponsors weighted to WIN money, ad
  £12→£4, prize ~−45%, signing fee 6×→3×, lifestyle +45%). (6) **PAY DAY screen** (`ST.PAYDAY`)
  after each real match: itemised wage slip + Vic's cut + new balance + the energy toll/rest days
  (autoplay skips it). Design: `docs/CAREER_DESIGN.md` §11d. Tuning probe:
  `scratchpad/econ_probe.js` pattern (debut spender ends near-broke, miser hoards less).
  **E8 "The Life" (owner's NSS-economy brief, same branch, second commit):** `CAR.monies`
  economy (wages by club size/tier + win/goal bonuses; **Vic's cut 10% +1%/season** off all
  income, announced in his season brief); **NSS-style energy** (matches drain ~29, weak natural
  recovery — replenished by satirical **protein shakes** priced by star rating, a **trainer**
  hired per 10-game block: Beef/Sven/Dr. Proteina, 3 tiers with personalities + procedural
  placeholder portraits swappable via `assets/ui/trainer_<id>.png`, and better housing);
  **lifestyle shop** (clothes/motor/gadgets/the gaff) feeding `effRep()` which gates transfer
  offers AND **sponsor deals** (Tony's Meat Van → Galaxy Airways, per-goal/per-win for 20
  matches, need ≥1 item); **A WORD FROM OUR SPONSORS** fake rewarded ad (+12 M, once per
  matchday, unskippable 4s, Vic-cut-free); **comms queue** (`CAR.msgs`/`flushMsgs`): Vic
  delivers board expectations each season + mid-season on/off-track updates + promotion/benched
  news; trainers nag/say goodbye in their own voices. New screens: £ SHOP (key L / £ button on
  every career home incl. cup/Euro/tournament), THE GYM, FINANCES, ad break; pay-day line on the
  match-end burst; monies in the career header. Design: `docs/CAREER_DESIGN.md` §11.
  **Owner round 14 (third commit, same branch):** economy v2 — per-club **contracts**
  (wage/win/goal bonuses from club size + effRep), **signing-on fees** on transfers, rollover
  **raises**, **prize money** with the season review, and an itemised **season ledger** on the
  new FINANCES page. "The Life" renamed **£ SHOP**; **£** currency everywhere (`money()`);
  "NRG" wording purged (NSS terminology) → ENERGY. **Hover tooltips** on every shop/gym/finances
  element. **Vic tutorial** at career start (bench = "3 balls to prove your worth", energy,
  monies, shop, sponsors) and ALL agent speeches now read **one sentence per screen** (progress
  dots). Starting XI slower to crack (trust threshold 70, gains halved, start trust 20). All
  league AI **×1.1** ("10% harder all around"). Design: `docs/CAREER_DESIGN.md` §11b.
  **Owner round 15 (fourth commit, same branch) — polish/UX pass (ui-ux-pro-max skill):** UI kit
  (`SP=8` grid, `uiPanel`, 11 hand-drawn 16x16 pixel icons via `drawIcon`); **£ SHOP is now a HUB**
  of five full-screen departments (PROTEIN CORNER / THE GYM / LIFESTYLE 2x2 grid with tier pips /
  SPONSORS ladder with locked tiers / FINANCES) — no more cramming; **CONTRACT ceremony**
  (`ST.CONTRACT`, club-letterhead paper, terms, signatures, SPACE TO SIGN) at career start and on
  every transfer; discreet **SKIP ✕** on comms (drains the queue; ESC too); shakes = **SINGLE /
  DOUBLE SCOOP only**; **S-MAIL** rebrand + avatar/tag-chip inbox + the **dealer** (every email
  pool dealt without replacement — no two emails alike); **trophies regenerated** (gen_trophies.py:
  crowned league gold, silver lidded pot, big-eared Euro jug, golden globe; dual glints/rim
  light/bloom) + **gallery trophy room** (spotlights, glass shelves, reflections, engraved
  plaques) + **cup-week popup** (first visit per cup round / Euro stage: the trophy at stake +
  the tie). Audit now 34 screens (hub/departments/contract/full trophy room staged; overlays —
  tooltip + cup popup — eyeballed via snaps, not linted). CI 47/47 + smoke.
  What it is (owner brief: "career mode should feel like a journey", NSS-style):
  new **second tier `ENG2`** ("The Championship", 20 clubs, tier 2, no Europe) where every new
  career now STARTS; elite leagues/big clubs **LOCKED** on the select screens until earned
  (`vc_unlocks` in localStorage: reach a league to unlock starting there; win a top-flight title
  → FREE START anywhere); **reputation 0-100** (stars + tier on the career home) gating transfer
  offers, foreign-giant offers and international call-ups; **energy** (congested cup/Euro runs =
  fewer balls, SAME target); **coach trust / squad role** (new signings = 3-ball CAMEO → 6-ball
  SUPER SUB → starter, targets scaled fairly via the new `matchTargetBalls` split in
  `setTargets`); **board expectations** with a season-review verdict + rep swing. Old saves
  migrate as established starters (never a downgrade). Design details: `docs/CAREER_DESIGN.md`
  §10. New/changed tests: `ci/career.test.js` (+7 journey tests, losing-season test now expects
  NO call-up at low rep), `ci/leagues.test.js` (+ENG2). Audit gained journey screens
  (`leaguesel_locked/free`, `clubsel_locked/eng2`, `career_home_journey`, `agent_journey`).
- The 2026-06-30 session (logo, Slick Vic, HUD venue chips, fixes) **IS DEPLOYED** — owner played it
  via `play.bat` and approved; landed on `main` (`6bdd36b`) along with the workspace audit
  (`PROJECT_HEALTH_AUDIT.md`) and the port-5578 config fixes. Its branch is deleted.
- **2026-07-02 workshop purge (owner call): all original-Flash-game material is REMOVED from the
  working tree** — `original.swf`, `gamezip/`, `ruffle/`+`ruffle.html`, `decomp/` (exports, `swf.xml`,
  ripped bg/sprites/sounds, one-shot py tools), `ref_gameplay.png`, `ref_logo.png`. KEPT: the decompiled
  ActionScript mechanics reference, moved to **`docs/original_mechanics/`** (read its README — still
  third-party IP, engineering reference only); stadium geometry (already in `docs/`); the original-SFX
  provenance table (**`docs/AUDIO_SHORTLIST.md` §1b** — which sound goes where and does what).
  Everything deleted is still recoverable from Git history until the ROADMAP C.3 `git filter-repo`
  history rewrite — which is now THE remaining IP step (plus club names, fonts, the 6 SFX).

**What the 2026-06-30 session shipped (now on `main` as part of this deploy):**
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
1. ✅ **C.3 history rewrite — DONE 2026-07-13.** Public Git history rewritten with `git-filter-repo`
   to purge ALL original-Flash-game / workshop material (`original.swf`, `game2.zip`, `gamezip/`,
   `ruffle/` + `ruffle.html`, `decomp/`, `scordagol_web/`, `page_*.html`, `ref_gameplay.png`,
   `ref_logo.png`, the Gemini image). Full manifest + verification:
   [`docs/IP_HISTORY_PURGE.md`](docs/IP_HISTORY_PURGE.md). Tip content unchanged (tree `642c2fba…`),
   CI 54/54, pack 138→105 MiB. ⚠ Note the old "~137 MB → under 40" target was NOT met and is not
   reachable while `striker_base_v01.blend` (55 MB, provenance unconfirmed) + ~30 MB of legit
   3D-sprite history stay — both separate calls. `original.swf` was NOT in the doc's original list —
   it was hidden behind a duplicate-content blob and caught on cross-check; the enumeration lesson is
   in the manifest. `assets/*_Liverpool*.png` left in place (live assets → the separate **club-name
   rebrand** step). Every clone made before 2026-07-13 is stale: `git reset --hard origin/main`,
   never merge one back in.
2. **Audio (owner-gated) — shortlist is PREPPED in `docs/AUDIO_SHORTLIST.md`** (sources, links, licences,
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
`node ci/smoke.js && node --test ci/physics.test.js ci/career.test.js ci/horse.test.js ci/leagues.test.js ci/timing.test.js`.
Deploy = commit on a short-lived `claude/<topic>` branch → push → `git push origin <branch>:main` →
delete the branch (local + remote) once landed. Don't commit `node_modules/` or `tools/` (both
gitignored). Don't add new large binaries; `striker_base_v01.blend` (55 MB, tracked) is the 3D-pipeline
base model — its long-term home is an open call (PROJECT_HEALTH_AUDIT cleanup item 10).

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
| `CLAUDE.md` | Session bootstrap, auto-loaded by Claude Code on any device — points here. |
| **`HANDOVER.md`** (this) | Current state, workflow, the active task. Start here. |
| `AUDIT.md` | Original technical audit (health grade, findings) — context for the roadmap. |
| `ROADMAP.md` | Phased plan to publication (foundations → own-every-pixel → engineering → monetise → launch). Status ticks per task. |
| `docs/CAREER_DESIGN.md` | The career universe design + what shipped (E0–E5). |
| `docs/SPRITE_SPEC.md` | **The sprite/region-tag contract** the engine + all generators depend on. |
| `docs/STADIUM_ASSET_SPEC.md` | Layered-background geometry + the alignment grid. |
| `docs/ART_SOURCING.md` | The 3D-pipeline decision + **the Mixamo shopping list** (the active task). |
| `docs/AUDIO_SHORTLIST.md` | CC0/royalty-free SFX + menu-music shortlist for the audio swap (§0 next task). |
| `docs/SPRITE_FRAME_SELECTION.md` | The owner's recorded frame picks from the 3D-pipeline contact sheets. |
| `docs/original_mechanics/` | Decompiled ActionScript of the original game — THE mechanics reference for the sacred physics (read its README; third-party IP, reference only). |
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
