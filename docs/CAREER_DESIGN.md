# SCORDAGOL — Career Universe Design

*How the career grows from "one league, 38 volleys" into an immersive football life —
foreign leagues, cups, European nights, international tournaments, and a light
management layer — without ever diluting the core: **every fixture is still the
10-ball volley game.***

**Status:** E0 (calendar) + E1 (domestic cup) + E4 (Europe) + E5 (internationals) + E3 (foreign leagues) + **E7 (the Journey — see §10)** + **E8 (the Life — see §11)** **shipped**. Owner decisions applied: cup/Europe/international matches are **5 balls with halved targets**; knockout ties are win-or-go-home (no draw band); the **World Tournament runs every 2 years, starting season 1** (E7: once your reputation earns a call-up); the career home shows a **tailored view per competition** (league table / cup ladder / group table / flag-themed tournament hub). Remaining phases: E2 is partially in (nationality select shipped with E5), E6 (management economy) open. Builds on the engine as-is
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

## 10. E7 — "The Journey" (SHIPPED 2026-07-02)

Owner brief: *"career mode should feel like a journey"* — NSS-style progression instead of
starting at the best club in the world. Five systems, all between-match state on `CAR`;
the sacred volley physics are untouched (the systems only decide **how many balls** you
get and **which clubs write to you**).

1. **Humble beginnings — the second tier.** New league `ENG2` ("The Championship",
   `tier:2` in `leagues.json`): 20 clubs rated 1–5, no European qualification. New careers
   start there; the five elite leagues appear on league select as **LOCKED** rows (the
   "journey map"). Reaching a league in any career unlocks *starting* there
   (`vc_unlocks.leagues`); winning any **top-flight title** unlocks **FREE START** (any
   club, any league — the old behaviour, now a reward). Career club-select only offers
   modest clubs (rating ≤ 4) in tier-1 leagues until free start is earned.
2. **Reputation 0–100** (`CAR.rep`, starts 5). Earned per result weighted by opponent
   rating (cup/Euro/intl nights ×1.3, second-tier ×0.7), plus trophies (+6 cup, +10 league,
   +12 Europe, +15 world) and the board verdict; positive gains taper (`×(1−rep/130)`) so
   LEGEND takes seasons. Gates: **transfer offers** (`repNeed()` — giants need ~68),
   **cross-league offers** (tier-1, rep ≥ 45, top-8 finish → the E3 headline move),
   **international call-ups** (rep ≥ 25 — a losing nobody stays home). Shown as stars +
   tier (UNKNOWN → PROSPECT → RISING STAR → BIG NAME → SUPERSTAR → LEGEND) on the
   career-home REPUTATION panel.
3. **Energy 0–100** (`CAR.energy`). Matches cost legs; a league week's rest more than
   recovers it, midweek cup/Euro slots barely do — so **congested runs** (the treble
   chase) are what tire you: `<60` costs one ball, `<40` two, **with the target
   unchanged** (owner's rule: *"less balls to hit your target"*). Fresh every new season;
   floor of 70 going into a World Tournament. CONDITION panel + countdown strap
   ("TIRED LEGS: 9 BALLS, FULL TARGET").
4. **Coach trust / squad role** (`CAR.trust`). New signings start low (25 + rep/2):
   `<30` = **3-ball CAMEO**, `<60` = **6-ball SUPER SUB** — both with the target scaled to
   the balls (the `matchTargetBalls` split in `setTargets`), so it's a fair cameo.
   Appearances/wins build trust ("took his chance" bonus for subs hitting the win
   target); a losing streak as a starter erodes it. Role shown in the NEXT MATCH bar,
   the countdown strap, and news lines on promotion/benching.
5. **Board expectations** (`CAR.objective`, set every season from the club's rating rank):
   WIN THE LEAGUE / TOP 4 / TOP 7 / TOP HALF / BEAT THE DROP. Season review shows the
   verdict (DELIGHTED/SATISFIED/DISAPPOINTED/FURIOUS) with the rep swing; the career-home
   POSITION cell is coloured against the goal.

Offer ladder (`genOffers`): same-league clubs above you (rep-gated) + tier-2 → ENG step-up
offers when you shine + foreign giants for big names + an ENG2 **lifeline** after a
bottom-three top-flight season. Offers carry `leagueId`; accepting one calls
`nextSeason(slug, leagueId)`.

Saves: pre-journey careers migrate in `loadCareer()` as **established starters** (rep ≥ 35
from titles/trophies/caps, trust 70, energy 100 — never a downgrade); existing titles
count toward free start. `vc_unlocks` lives OUTSIDE `vc_career` so it survives new careers.

Deferred E7 ideas (owner's "unlockables" theme, cosmetic-only): unlockable ball skins /
boot colours / celebrations tied to milestones; a PROFILE/milestones panel; sacking +
forced transfer-listing after a FURIOUS season.

## 11. E8 — "The Life" (SHIPPED 2026-07-02, same session as E7 round 2)

Owner brief: replicate the NSS (New Star Soccer) bux economy — energy you replenish with
consumables, money from wages/sponsors/ads, lifestyle that feeds reputation, a hired
trainer, an agent who takes his cut — with the satire dialled up (protein-shake culture).
Research notes: NSS NRG prices scale with star rating; staff are hired per match-block and
boost post-match recovery; sponsors refuse players with no lifestyle items; wages start tiny.

1. **Monies** (`CAR.monies`). Wage per appearance (tier-2: `10+rating*3`, tier-1:
   `40+rating*10`) + 60% win bonus + per-goal bonus + sponsor payouts, paid at `endMatch`
   (`matchEarnings`, shown on the VICTORY/LOSS burst). **Vic's cut** = `10% + 1%/season`
   (cap 25) off ALL income — he announces the rise in his season brief. Kept deliberately
   tight early (a Championship kid nets ~25/match) so choices matter.
2. **Protein shakes** (the satire): HALF SCOOP +25 / DOUBLE SCOOP +55 / MASS GAINER 5000
   (full), priced `mult × your stars` (NSS NRG rule). Energy now drains ~29 per 10-ball
   match with only weak natural recovery (14 + housing + trainer) — the E7 tired-legs
   ball-cut is unchanged, but shakes/trainer/housing are how you manage it. Reset to 100
   each season; benched players stay fresh (cameos cost little).
3. **Trainer**: hired by the 10-game block on THE GYM screen; three tiers with
   personalities and agent-style comms (hire speech, a nag when you dip under 40 energy,
   a goodbye when the block runs out): Barry 'Beef' Binns (80 M, +8/match), Sven
   Nutriblast (240 M, +13), Dr. Proteina (550 M, +18). Portraits are procedural
   PLACEHOLDERS with a PNG-first hook (`assets/ui/trainer_<id>.png`) for the owner's art.
4. **Lifestyle shop** (THE LIFE screen): CLOTHES / MOTOR / GADGETS / THE GAFF, 3-4 tiers
   each, buy upward only. Items add a lifestyle bonus to **effective rep**
   (`effRep = rep + lifeBonus`, used by transfer-offer gating and sponsors); housing also
   boosts recovery (NSS properties rule).
5. **Sponsors**: one active deal, gated on effRep AND owning ≥1 lifestyle item (no
   clobber, no sponsors): TONY'S MEAT VAN (10) → CRISPY NUGGZ (30) → SCORBOOST PRO-TEIN
   (50) → GALAXY AIRWAYS (70); pay per goal/win for 20 matches, Vic taxed.
6. **A WORD FROM OUR SPONSORS**: a fake rewarded ad — one of the ground's own hoarding
   boards full-screen for 4 unskippable seconds → +12 M, once per matchday, Vic-cut-free
   ("Vic doesn't know about this income"). Future hook for a real rewarded-ad network.
7. **Comms queue** (`CAR.msgs` → `flushMsgs` on returning to the career home): Vic
   delivers the board expectation + his cut every season start, on/off-track updates at
   1/3 and 0.7 of the season, and promotion/benching news (the E7 trust beats); trainers
   talk in their own voices with their own portraits.

Saves migrate with savings (`100 + 150/season`); `vc_career` gains `monies/earned/items/
trainer/sponsor/msgs/adSeen`. UI: £ THE LIFE button on every career home (key L), monies
in the header, THE LIFE + THE GYM + ad-break screens, pay-day line on the match-end burst.

### 11b. Owner round 14 (same session)

- **Economy v2:** per-club **contracts** (`CAR.contract`: wage / win bonus / goal bonus,
  negotiated from club size + effective rep); transfers bring a **signing-on fee** (6x wage)
  and a new contract; a grown rep earns a **raise** at the rollover (Vic announces both).
  **Prize money** at the season review (league finish + cup run + Europe, tier-scaled).
  **`CAR.ledger`** books every pound in/out per season, shown on the new **FINANCES** page
  (contract terms, Vic's %, sponsor terms, itemised income/outgoings, net).
- **"The Life" renamed £ SHOP**; currency symbol is **£** everywhere (`money()` formatter);
  all "NRG" wording (NSS terminology) replaced with **ENERGY**.
- **Hover help:** every shop/gym/finances element registers a tooltip (`tipRegions` +
  `drawTooltip`) explaining what it is and how it works (desktop hover; touch users get the
  same from the tutorial).
- **Vic's tutorial** at career start (comms queue): the bench ("3 balls off the bench to
  prove your worth"), energy/shakes, monies + his cut, the shop/trainer, sponsors.
- **One sentence at a time:** the agent screen paginates every speech into sentences
  (typewriter per sentence, progress dots, action key advances).
- **Slower road to the XI:** starter threshold 60→70, trust gains roughly halved, career
  start trust 27→20, off-season drift +10→+6 (a decent run now takes ~10 matches to crack
  the eleven; a poor one 20+).
- **Difficulty:** all league AI strength ×1.1 (owner: "10% harder all around").

### 11c. Owner round 15 (same session) — polish/UX pass

- **UI kit** (per the ui-ux-pro-max audit): 8px spacing grid + 24px margins, `uiPanel`
  card component, hand-drawn 16x16 pixel icons (shake/dumbbell/shirt/car/house/gamepad/
  megaphone/ledger/coin/trophy/bolt), one accent colour per role.
- **£ SHOP = a hub of five departments**, each a full screen: PROTEIN CORNER (condition
  bar with threshold ticks + the two scoops), THE GYM, LIFESTYLE (2x2 category grid,
  tier pips, upgrade-only buttons), SPONSORS (the deal + the full ladder with lock
  reasons), FINANCES. Hover tooltips throughout.
- **Contract ceremony** (`ST.CONTRACT`): club-letterhead document with the negotiated
  terms and Vic's commission, signed at career start and after every transfer.
- **Comms**: discreet corner SKIP ✕ (drops the whole queue; ESC does the same).
- **Shakes**: SINGLE SCOOP +25 / DOUBLE SCOOP +55 only (owner).
- **S-MAIL** (was Smail): avatar initials + tag chips (DOMESTIC / THE BIG TIME / league
  name / THE HARD ROAD) in the inbox; the offer generator deals every pool (senders,
  subjects, hooks, flattery, closes, foreign PS lines) without replacement, so **no two
  emails in an inbox are ever the same**; pools enlarged.
- **Trophies**: regenerated real-inspired silverware (crowned league gold, silver lidded
  pot, big-eared European jug, golden globe on a swirl) with dual glints, rim light,
  specular pips and baked bloom; **gallery trophy room** (spotlight cones, glass shelves,
  radial glow, reflections, engraved season plaques); **cup-week popup** shows the trophy
  at stake + the tie, once per cup round / Euro stage (`cup.seenR` / `euro.seenK`).


### 11d. Owner round 16 (economy depth + energy realism + pay day)

- **Bank balance consistent + labelled.** `bankRight()` returns `"BANK £x"`, stamped
  top-right on every career-management header (home, cup, Europe, tournament hub, shop
  hub + all departments, gym, finances, trophy room, season review). The home top-bar now
  reads `CAREER · SEASON N` centred with the bank on the right. Deliberate exceptions: the
  S-MAIL client (own email identity) and the contract paper (own letterhead).
- **Career-home hover explainers** on the FORM / POSITION / TITLE-ODDS footer, the
  REPUTATION and CONDITION panels, the NEXT MATCH panel and the bank readout.
- **Energy → NSS rest-day model.** A match drains by *workload* (`ENERGY_DRAIN_BASE 4 +
  3.6 × role target balls` → starter ≈ 40, sub ≈ 26, cameo ≈ 15) and you recover by
  *resting between fixtures* (`restDaysFor`: league 7d, cup 4d, Europe 3d, intl 5d ×
  `ENERGY_REC_PER_DAY 3`, plus trainer + property). So a helpless starter is exhausted in
  ~5 games, congested cup/Euro weeks bite hardest, and subs/cameos naturally stay fresher.
  Thresholds harsher (owner): **under 60% = −2 balls, under 40% = −4 balls** (same target).
- **Trainers mirror NSS staff.** Dearer = far longer contract (the value is fewer
  renewals): Beef £70/8 games/+7, Sven £220/24/+11, Dr Proteina £520/60/+16.
- **Economy slowed (NSS grind).** Wages −30% (`tier2 5+r×2`, `tier1 24+r×6`), goal bonus
  tiny (`5% of wage`, min 1) and sponsors weighted onto WIN money (per-goal shrunk) so a
  10-ball haul can't explode; rewarded ad £12→£4; prize money ~−45%; signing fee 6×→3×
  wage; lifestyle costs +~45% (aspirational). Probe: a debut spender ends a season near
  broke after real investment; a do-nothing miser hoards less and plays exhausted.
- **PAY DAY screen** (`ST.PAYDAY`) after the result burst: an itemised wage slip
  (appearance fee, win bonus, goals × bonus, sponsor, gross, Vic's cut, in-the-bank, new
  balance) plus the match's energy toll and rest days. Real play only; autoplay skips it.

### 11e. Owner round 17 (faithful NSS energy state-machine + work rate; £2 start; shop depth)

- **Energy is now a % state-machine, lifted from New Star Soccer.** A match burns a chunk of
  the 100% bar by **WORK RATE** (a 3-heart toggle): CONSERVE 22% / NORMAL 48% / ALL OUT 78%,
  scaled by role minutes (`ROLE_ENERGY` cameo 0.4 / sub 0.6 / starter 1.0). Natural weekly
  recovery is deliberately weak (`RECOVER_BASE 14`, scaled by `restFracFor`: league 1.0, cup
  0.55, Europe 0.45, intl 0.7) so you spiral into the subs without buying recovery. Stacks:
  **property** weekly % (`THE GAFF` +5/+15/+25/+35, NSS values), **trainer** post-match refund
  (+10/+12/+15), **shakes** on-the-spot (SINGLE +50 / DOUBLE +100). A helpless starter is
  spent in ~3 games; a smart one (CONSERVE when tired + a cheap trainer) holds ~60%+.
- **Work rate** (`CAR.workRate`, click the CONDITION panel or keys 1/2/3/W on the home) trades
  balls for energy: `balls = roleTarget + (wr-2)*2` (ALL OUT +2 chances, CONSERVE -2). Tired
  legs **cap** the rate you can play (≥60% for ALL OUT, ≥28% for NORMAL, else CONSERVE);
  under 12% costs a further -2. Replaces the old flat energy-ball-cut.
- **Contract**: a debut unknown starts on **~£2 a game** with a **win bonus but NO goal bonus**
  (owner: a 10-ball game scores too many goals for per-goal pay). Start money cut to **£10**.
- **Shop/reputation depth**: lifestyle gains a 4th tier per category (Couture House / Hypercar /
  Superyacht, rep up to +10) and the sponsor ladder grows to **six rungs** (Tony's Meat Van →
  Scordacoin Crypto, gated on effective rep). Bigger lifestyle rep = a stronger reputation
  lever feeding offers + sponsors.
- Deferred (noted for a later round): NSS age/degradation fatigue multiplier (we don't track
  age); training/relationship energy sinks (no such gameplay yet) — the work-rate toggle is the
  creative substitute the owner asked for.
