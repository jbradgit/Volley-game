# SCORDAGOL — Career Universe Design

*How the career grows from "one league, 38 volleys" into an immersive football life —
foreign leagues, cups, European nights, international tournaments, and a light
management layer — without ever diluting the core: **every fixture is still the
10-ball volley game.***

**Status:** E0 (calendar) + E1 (domestic cup) + E4 (Europe) + E5 (internationals) **shipped**. Owner decisions applied: cup/Europe/international matches are **5 balls with halved targets**; knockout ties are win-or-go-home (no draw band); the **World Tournament runs every 2 years, starting season 1**; the career home shows a **tailored view per competition** (league table / cup ladder / group table / flag-themed tournament hub). Remaining phases: E2 is partially in (nationality select shipped with E5), E3 (foreign leagues) and E6 (management economy) open. Builds on the engine as-is
(`index.html`): `CAR` save object, `TEAMS`/`teams.json`, `simRound`/`teamStrength`
league sim, transfer-offer inbox, seeded matches, the HORSE turn engine.

---

## 0. Design pillars

1. **The volley IS the game.** Every new competition is a new *reason* to play a
   10-ball match with different stakes, not a new minigame. Management elements are
   between-match decisions readable in under 30 seconds on a phone.
2. **Data-driven.** Leagues, nations, cups and tournaments are JSON; the engine
   already proves this pattern with `teams.json` (kits drive recolours, ratings
   drive targets). New content = new data files, minimal new code.
3. **Shippable slices.** Each phase below is independently releasable and saves
   stay compatible (see §7).
4. **Publication-aware.** Real foreign leagues/clubs multiply the IP problem
   (AUDIT C-1). All data files use a `name` field so everything can be
   fictionalised in one pass before launch (e.g. "La Liga" → "Liga Estelar";
   clubs follow the same slug-keyed pattern as today).

## 1. The world: leagues (`assets/world/leagues.json`)

Five leagues at launch, early-2000s flavour:

Difficulty ordering (owner decision): **England hardest, Spain second, then Italy /
Germany / France equal** — and the differences are slight, not dramatic.

| id | League (working name) | Teams | Difficulty | Character |
|---|---|---|---|---|
| ENG | Premier League | 20 | 1.00 (hardest) | the default start |
| ESP | Liga Estelar | 20 | 0.95 | two giants, technical |
| ITA | Serie Argento | 20 | 0.90 | low-scoring flavour |
| GER | Bundesturnier | 18 | 0.90 | high-scoring flavour |
| FRA | Ligue Royale | 18 | 0.90 | one dominant club |

Difficulty scales the AI strength curve only (the `winProb` constants); per-match
score targets are NOT changed by league. **League points realism (shipped):** the
sim is calibrated against recent real EPL tables — champions average ~87 pts
(range ~71–105), 4th ~71, 10th ~50, bottom ~22 — so running away with the title
now requires a genuinely great season, not just a decent one.

- Each league entry: `{ id, name, teams:[...same schema as teams.json...],
  targetMod, drawMod }` — the per-league personality is just two multipliers on
  `setTargets()` (index.html:451). Cheap, real variety.
- `CAR.leagueId` replaces the implicit "England". `standings()`, `simRound()`,
  fixtures — all already operate on a TEAMS array; they get the active league's
  array instead of the global.
- **Kit pipeline scales free:** defenders are recoloured live from one region map
  (index.html:88), so 96 new clubs = 96 JSON entries, zero new defender art.
  Striker kits need per-club PNGs today — Phase C includes making the striker use
  the same live-recolour path (one base + palette), which kills that asset cost
  forever.
- **Cross-league transfers:** the existing season-end inbox (`genOffers`) gains
  foreign offers once `CAR.reputation` (see §6) crosses thresholds. Accepting one
  moves `CAR.leagueId` — the headline moment of a career. Offer body text already
  templates club colours/finishes; add league flavour lines.

## 2. Domestic cup (per league)

- **Format:** 5 knockout rounds (R32 → final), drawn from the league's clubs +
  filler "lower-division" minnows (ratings 1–3, generated names) so early rounds
  feel like giant-killing territory.
- **Calendar:** cup rounds slot between league matchdays (after MD 6, 12, 19, 26,
  33). See §5 calendar model.
- **Draws happen in the inbox** — reuse the email screen: "CUP DRAW: you face
  Bridgewater Rovers (away)". Zero new UI.
- **No draws allowed:** if a cup match ends level vs the target (score between
  drawTarget and winTarget), it goes to a **shootout: 3 sudden-death balls** —
  reuses the seeded serve + HORSE turn machinery (`startMatch({balls:3})` exists
  today via the `balls` option).
- Win the final → trophy + prize money (§6) + a hoarding-board-style celebration
  screen.

## 3. European competition

- **Qualify** by league finish: 1st–4th → **Champions Trophy**; 5th–7th →
  **Continental Cup**. Shown on the season-end screen ("YOU'RE IN EUROPE!").
- **Format (kept tight):** group of 4 (6 matches, vs clubs drawn from the other
  four leagues) then SF + Final. 8 extra fixtures max — a season grows from 38 to
  ~45 playable matches; acceptable because any match is ~90 seconds.
- **Away nights feel different:** European away matches add a `targetMod` bump and
  (cosmetic) a variant backdrop — the layered stadium system (STADIUM_ASSET_SPEC)
  makes alternate backdrops a drop-in PNG; generate a "continental" variant
  (different roof/crowd palette, no English red sections).
- Group table reuses the league-table renderer with 4 rows.

## 4. National team

- **Nationality selection at career start** — new step in the NEW CAREER flow
  (after name, before club): pick from `assets/world/nations.json` (~16 nations,
  each with kit colours + rating, same palette system → live-recoloured kits
  work immediately). The flow already chains screens (`ST.NAME → ST.CLUBSEL`);
  add `ST.NATSEL` between them, reusing the club-select grid renderer.
- **Call-ups:** if your season form passes a threshold (rolling avg score vs
  targets — the data already exists in `CAR.form`/results), an inbox email calls
  you up. Caps + international goals tracked on a new CAREER → PROFILE panel.
- **Tournament every 4th summer** (between seasons, where the transfer inbox
  already lives): group of 4 + QF/SF/Final, max 6 matches, played back-to-back as
  a summer "festival" arc. Non-qualification or group exit = short summer; deep
  runs delay the next season start by nothing (it's all virtual time).
- **Friendly windows** (optional, Phase E.2): one mid-season international,
  low-stakes, keeps the shirt warm.

## 5. The enabler: a season **calendar** (do this first)

Today the season is `CAR.fixtures[idx]` — a flat league list. Everything above
needs one architectural change: at season start, generate
`CAR.calendar = [ {type:"league", opp, home}, {type:"cupdraw"}, {type:"cup", round, opp},
{type:"euro", stage, opp}, {type:"intl", ...}, ... ]`
and the career home shows "NEXT:" whatever the calendar says. `commitMatch()`
advances the pointer; `simRound()` still simulates the league only on league
matchdays. This is a contained refactor of `makeFixtures`/`startFixture`/
`commitMatch` and should land **with tests** (career.js extraction — ROADMAP
Phase 2 — pairs naturally with it).

## 6. The management layer: player-manager, not spreadsheet

Scope discipline: SCORDAGOL is not Football Manager. The fantasy is *"my career,
my club's rise"*. v1 ships three systems only:

1. **Reputation (0–100):** grows with results, trophies, caps. Gates: foreign
   offers, bigger clubs, captaincy flavour text. Replaces today's implicit
   "finish position → offers" rule with something that persists across seasons.
2. **Club budget & signings (the sporting-director hook):** prize money from
   league finish + cup runs fills a club budget. Between seasons you may sign
   **one squad player** from a shortlist of 3 (inbox flow again). A signing is a
   `teamStrength` modifier for YOUR club's *simulated* results (+0.03..+0.08) —
   it makes the league table feel ownable beyond your own matches, with zero
   change to volley physics. (The sim hook exists: `teamStrength()`,
   index.html:269.)
3. **Club upgrades (one track):** spend budget on the stadium — visually upgrades
   the backdrop variant (tier 1/2/3 art) and slightly raises home `winTarget`
   prize money. Pure cosmetics + economy, and it showcases the layered-backdrop
   system.

Explicitly **out** (for now): squads/lineups, tactics, staff, contracts/wages,
injuries, training minigames. Each would pull sessions past the 30-second
decision budget.

## 7. Save compatibility & data model

- `vc_career` gains `v:2` plus: `nation`, `leagueId`, `reputation`, `budget`,
  `caps`, `intlGoals`, `trophies:[]`, `calendar`, `calIdx`, `cup:{...}`,
  `euro:{...}`.
- A `migrateCareer(old)` shim maps v1 saves (default nation England, league ENG,
  reputation from titles/news length) — **never wipe a player's career.**
- New files: `assets/world/leagues.json`, `assets/world/nations.json`,
  `assets/world/cupnames.json` (minnow name generator parts).
- Every fetch follows the house rule: visible failure, never silent (the
  keeper-atlas lesson; no "ads" in paths).

## 8. Phasing (each row independently shippable)

| Phase | Contents | Effort | Depends on |
|---|---|---|---|
| **E0** | Calendar refactor + save v2 + migration + tests | L | career.js extraction (ROADMAP 2.1) recommended first |
| **E1** | Domestic cup (draws, minnows, shootout, trophy room) | L | E0 |
| **E2** | Nationality select + nations.json (no tournaments yet — it feeds profile/flavour) | M | — |
| **E3** | Foreign leagues + cross-league transfers + striker live-recolour | XL | E0; rebrand decision (D2) |
| **E4** | European competitions + continental backdrop variant | L | E0, E3 |
| **E5** | National team call-ups + summer tournament | L–XL | E2, E0 |
| **E6** | Reputation + budget + signings + stadium upgrades | L | E0; ideally after E1 so cup money exists |

Suggested order: **E0 → E1 → E2 → E3 → E4 → E5 → E6.** The cup first because it
delivers "more than just the league" with the least new data, and its shootout
mechanic is immediately reusable by E5.

## 9. Open questions (owner)

1. Season length feel: is ~45 matches/season (league+cup+Europe) right, or should
   league matchdays compress (e.g. play every other MD, sim the rest) once cups land?
2. Cup draws-as-emails vs a dedicated draw screen with animation?
3. Tournament cadence: every 4th season (realistic) or every 2nd (more content)?
4. Should signings ever affect *your* matches (e.g. better serves) or stay
   sim-only? (Recommend sim-only: protects the sacred physics.)
5. Fictional names: approve the working league names in §1 or supply your own.
