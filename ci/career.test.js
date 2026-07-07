// Career-engine regression tests (node --test). Complements ci/smoke.js: where smoke.js
// plays one golden season, this asserts the underlying career RULES hold across seasons —
// fixtures/calendar size, league points math, title qualification, cup/Europe/international
// structure, trophy accounting and transfer offers. All driven through the ?cap=1 __dbg
// harness, so it needs no changes to index.html (and will become true unit tests once the
// engine is split out per ROADMAP 2.1).
//
// These assert invariants that hold for ANY random seed: a forced all-win season always
// yields 114 pts and 1st place (rivals can reach at most 108), KO ties resolve by the
// player's forced result, and competition sizes are fixed.
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadGame } = require("./harness");

// Autoplay a whole season via __dbg, tallying matches by competition.
// win=true forces every player match to a win; other clubs are simulated (RNG).
function playSeason(dbg, win){
  const counts = { L:0, C:0, E:0, I:0 };
  let guard = 240, r;
  while (guard-- > 0){
    r = dbg.playNext(win);
    if (r.ev) counts[r.ev]++;                 // r.ev is 'L' | 'C' | 'E'
    else if (r.trn && !r.exited) counts.I++;  // an international (World Tournament) match
    dbg.tick();                               // render the resulting home view (must not throw)
    if (r.done || r.exited || r.state === "seasonend") break;
  }
  counts.total = counts.L + counts.C + counts.E + counts.I;
  return counts;
}
const tally = (arr, v) => arr.filter(x => x === v).length;

test("new career: season-1 calendar is 38 league + 5 cup, no Europe", async () => {
  const { dbg } = await loadGame();
  const { cal } = dbg.newCareerSim("England");
  assert.equal(cal, 43, "season 1 has 43 calendar slots (38L + 5C)");

  const info = dbg.careerInfo();
  assert.equal(info.season, 1);
  assert.equal(info.pts, 0);
  assert.equal(info.caps, 0);
  assert.equal(info.trophies.length, 0, "no trophies at the start");
  assert.equal(info.cup.round, 0);
  assert.equal(info.cup.out, false);
  assert.equal(info.cup.won, false);
  assert.ok(info.pos >= 1 && info.pos <= 20, "a valid league position");
});

test("nationality choice does not change the club calendar", async () => {
  for (const nation of ["England", "Brazil", "Italy", "Spain"]) {
    const { dbg } = await loadGame();
    const { cal } = dbg.newCareerSim(nation);
    assert.equal(cal, 43, `cal should be 43 regardless of nation (${nation})`);
  }
});

test("winning season 1: 38L + 5C + 6I = 49 matches, 114 pts, champions, treble", async () => {
  const { dbg, errors } = await loadGame();
  dbg.newCareerSim("Brazil");
  const c = playSeason(dbg, true);
  assert.equal(c.L, 38, "38 league matches");
  assert.equal(c.C, 5,  "5 cup rounds when every tie is won");
  assert.equal(c.E, 0,  "no European campaign in season 1");
  assert.equal(c.I, 6,  "World Tournament = 3 group + QF + SF + F");
  assert.equal(c.total, 49);

  const info = dbg.careerInfo();
  assert.equal(info.season, 1);
  assert.equal(info.pts, 114, "win all 38 league games -> 114 pts");
  assert.equal(info.pos, 1, "champions (a rival can reach at most 108)");
  assert.equal(info.caps, 6, "6 World Tournament caps");
  assert.equal(info.cup.won, true);
  assert.equal(info.cup.out, false);
  assert.ok(info.trophies.includes("cup"),  "cup won");
  assert.ok(info.trophies.includes("intl"), "World Tournament won");
  assert.ok(!info.trophies.includes("league"), "league title is only recorded at the rollover");
  assert.equal(info.nextEuro, "CT", "champions qualify for the Champions Trophy");
  assert.equal(errors.length, 0, "no console errors during a full season: " + errors.join(" | "));
});

test("season 2 is a European year: 38L + 5C + 8E = 51 matches, no internationals", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("Brazil");
  playSeason(dbg, true);                       // win season 1 -> qualify for Europe

  const roll = dbg.nextSeasonSim();
  assert.equal(roll.season, 2);
  assert.equal(roll.euro, true, "European campaign present in season 2");
  assert.equal(roll.cal, 51, "38 league + 5 cup + 8 Europe");
  assert.ok(dbg.careerInfo().trophies.includes("league"), "S1 league title counted at the rollover");

  const c = playSeason(dbg, true);
  assert.equal(c.L, 38);
  assert.equal(c.C, 5);
  assert.equal(c.E, 8, "6 group + SF + F");
  assert.equal(c.I, 0, "no World Tournament in an even season");
  assert.equal(c.total, 51);

  const info = dbg.careerInfo();
  assert.equal(info.season, 2);
  assert.equal(info.pts, 114);
  assert.equal(info.pos, 1);
  assert.equal(info.caps, 6, "caps unchanged in a non-tournament year");
  assert.ok(info.trophies.includes("euro"), "European trophy won");
});

test("losing season 1: 0 pts, cup KO after one tie, NO international call-up (E7: rep too low)", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("Brazil");
  const c = playSeason(dbg, false);
  assert.equal(c.L, 38, "all league games are still played (no KO)");
  assert.equal(c.C, 1,  "knocked out of the cup after the first tie");
  assert.equal(c.E, 0);
  assert.equal(c.I, 0,  "a nobody with a losing season doesn't get a call-up");
  assert.equal(c.total, 39);

  const info = dbg.careerInfo();
  assert.equal(info.pts, 0, "lose all 38 -> 0 pts");
  assert.equal(info.cup.out, true);
  assert.equal(info.cup.won, false);
  assert.equal(info.caps, 0);
  assert.ok(!info.trophies.includes("cup"));
  assert.ok(!info.trophies.includes("intl"));
  assert.ok(!info.trophies.includes("euro"));
  assert.ok(info.nextEuro == null, "no European qualification");
  assert.ok(dbg.journeyInfo().rep < 25, "a season of defeats leaves you unknown");
});

test("titleClinched() is true on a mathematically-decided table", async () => {
  const { dbg } = await loadGame();
  assert.equal(dbg.clinchTitle().clinched, true);
});

test("a champion season generates transfer offers", async () => {
  const { dbg } = await loadGame();
  const se = dbg.fakeSeasonEnd(1);
  assert.equal(se.state, "seasonend");
  assert.equal(se.pos, 1, "fakeSeasonEnd(1) forces a title");
  assert.ok(se.offers.length > 0, "a champion attracts transfer offers");
});

test("three winning seasons: correct trophy haul, caps and season cadence", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("Brazil");
  for (let s = 1; s <= 3; s++){
    playSeason(dbg, true);
    if (s < 3) dbg.nextSeasonSim();
  }
  const info = dbg.careerInfo();
  assert.equal(info.season, 3);
  const t = info.trophies;
  assert.equal(tally(t, "cup"), 3,    "a cup in each of seasons 1-3");
  assert.equal(tally(t, "league"), 2, "league titles recorded at the S1->S2 and S2->S3 rollovers");
  assert.equal(tally(t, "euro"), 2,   "Europe in seasons 2 and 3");
  assert.equal(tally(t, "intl"), 2,   "World Tournament in odd seasons 1 and 3");
  assert.equal(info.caps, 12,         "6 caps in each of seasons 1 and 3");
});

// ================= E7 "The Journey": lower-league start, reputation, energy, squad role =================

test("journey: a new career starts as an unknown 3-ball cameo in the second tier", async () => {
  const { dbg } = await loadGame();
  const r = dbg.newCareerSim("England", "ENG2", "Millwall");
  assert.equal(r.leagueId, "ENG2");
  assert.equal(r.teams, 20, "the Championship has 20 clubs");
  assert.equal(r.cal, 43, "38 league matchdays + 5 cup rounds, no Europe");

  const j = dbg.journeyInfo();
  assert.equal(j.tier, 2);
  assert.equal(j.rep, 5, "an unknown");
  assert.equal(j.role, "cameo", "the coach doesn't trust a trialist yet");
  assert.ok(j.objective && j.objective.pos >= 1, "the board sets a season objective");

  const plan = dbg.matchPlanSim();
  assert.equal(plan.balls, 3, "a cameo gets 3 balls");
  assert.equal(plan.targetBalls, 3, "with the target scaled to match (a fair cameo)");
});

test("journey: wins earn the coach's trust — cameo -> super sub -> starter", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  const roles = [];
  for (let i = 0; i < 10; i++){ roles.push(dbg.journeyInfo().role); dbg.playNext(true); }
  assert.equal(roles[0], "cameo");
  assert.ok(roles.includes("sub"), "passes through the super-sub role: " + roles.join(","));
  assert.equal(dbg.journeyInfo().role, "starter", "a winning run earns a starting spot");
  dbg.setJourney({ energy: 100 });   // isolate the ROLE quota from tired legs (E8: matches drain energy)
  assert.equal(dbg.matchPlanSim().balls, 10, "a fresh starter gets the full 10 balls");
});

test("journey (round 17): work rate trades balls for energy; tiredness forces you down", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setJourney({ trust: 100, energy: 100 });   // a fresh starter (target 10 balls)
  dbg.setWorkRate(3); let plan = dbg.matchPlanSim();
  assert.equal(plan.targetBalls, 10, "the target still assumes the role's 10 balls");
  assert.equal(plan.balls, 12, "ALL OUT gives +2 balls");
  dbg.setWorkRate(2); assert.equal(dbg.matchPlanSim().balls, 10, "NORMAL = the target");
  dbg.setWorkRate(1); assert.equal(dbg.matchPlanSim().balls, 8, "CONSERVE = -2 balls");
  // tiredness caps the work rate you can actually play
  dbg.setJourney({ energy: 40 }); dbg.setWorkRate(3);
  assert.equal(dbg.matchPlanSim().balls, 10, "under 60% you can't go ALL OUT (forced NORMAL)");
  dbg.setJourney({ energy: 20 }); dbg.setWorkRate(3);
  assert.equal(dbg.matchPlanSim().balls, 8, "under 28% you're forced to CONSERVE");
  dbg.setJourney({ energy: 8 });
  assert.equal(dbg.matchPlanSim().balls, 6, "running on fumes (<12%) costs a further two");
});

test("journey: winning the second tier brings top-flight offers but NO European spot", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  playSeason(dbg, true);
  const info = dbg.careerInfo();
  assert.equal(info.pos, 1, "champions of the second tier");
  assert.ok(info.nextEuro == null, "no Europe from the second tier");
  const offers = dbg.offersSim();
  assert.ok(offers.some(o => o.leagueId === "ENG"), "a Championship winner draws Premier League interest: " + JSON.stringify(offers));
});

test("journey: reputation gates the elite — and a top-flight title unlocks free start", async () => {
  const { dbg } = await loadGame();
  // an unknown champion: the title itself bumps rep (~+16), but the gates still hold him to small clubs
  dbg.fakeSeasonEnd(1, 0);
  let offers = dbg.offersSim();
  assert.ok(offers.length > 0, "a champion still gets offers");
  assert.ok(offers.every(o => o.rating <= 4), "a low-rep champion only tempts modest clubs: " + JSON.stringify(offers));
  assert.ok(!offers.some(o => o.leagueId !== "ENG"), "no foreign interest at low rep");

  // a superstar champion gets the giants and the continent
  const { dbg: dbg2 } = await loadGame();
  dbg2.fakeSeasonEnd(1, 90);
  offers = dbg2.offersSim();
  assert.ok(offers.some(o => o.rating >= 9), "giants court a superstar");
  assert.ok(offers.some(o => o.leagueId !== "ENG"), "foreign leagues come calling: " + JSON.stringify(offers));
  assert.equal(dbg2.journeyInfo().unlocks.freestart, true, "a top-flight title unlocks free start");
});

test("journey: accepting a foreign offer moves the career abroad with trust to re-earn", async () => {
  const { dbg } = await loadGame();
  dbg.fakeSeasonEnd(1, 90);
  const r = dbg.nextSeasonSim("RealMadrid", "ESP");
  assert.equal(r.leagueId, "ESP", "career moved to La Liga");
  assert.equal(r.slug, "RealMadrid");
  assert.ok(r.trust >= 15 && r.trust <= 75, "a new gaffer's trust must be re-earned (got " + r.trust + ")");
  // and the new season plays through without error
  const c = playSeason(dbg, true);
  assert.ok(c.L >= 38, "a full La Liga season plays out");
});

test("energy (round 17): a higher work rate burns more of the bar", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setJourney({ trust: 100, energy: 100 });
  dbg.setWorkRate(1); dbg.playNext(true);
  const conserve = -dbg.lifeInfo().lastEnergy.delta;
  dbg.setJourney({ energy: 100 }); dbg.setWorkRate(2); dbg.playNext(true);
  const normal = -dbg.lifeInfo().lastEnergy.delta;
  assert.ok(normal > conserve, `NORMAL (${normal}) burns more than CONSERVE (${conserve})`);
  assert.ok(normal >= 25, `a normal match takes a real chunk of the bar (${normal}%) - NSS-fast`);
});

test("contract (round 17): a debut unknown starts on about GBP 2 a game, win bonus only", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  const c = dbg.lifeInfo().contract;
  assert.ok(c.wage <= 4, "a nobody earns a pittance to start: GBP " + c.wage);
  assert.ok(c.winB >= 2, "but there's a win bonus");
  assert.equal(c.goalB, 0, "and no goal bonus");
  assert.equal(dbg.lifeInfo().monies, 10, "and starts near-broke");
});

// ================= E8 "The Life": Monies, protein shakes, the trainer, lifestyle, sponsors =================

test("life: a new career is skint, wages land minus Vic's cut, and the cut rises each season", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  let l = dbg.lifeInfo();
  assert.equal(l.monies, 10, "an unknown kid starts near-broke");
  assert.equal(l.vicCut, 10, "Vic opens at 10%");
  assert.ok(l.msgs.includes("vic"), "Vic's season brief (board expectation + his cut) is queued");

  dbg.setJourney({ trust: 100 });    // a full 10-ball match so the energy cost is visible
  dbg.playNext(true);
  l = dbg.lifeInfo();
  assert.ok(l.monies > 10, "an appearance pays wages");
  assert.ok(l.lastEarn && l.lastEarn.gross > 0);
  assert.equal(l.lastEarn.cut, Math.round(l.lastEarn.gross * 0.10), "Vic skims exactly his 10%");
  assert.equal(l.lastEarn.net, l.lastEarn.gross - l.lastEarn.cut);
  assert.ok(l.energy < 100, "a match costs legs (NSS model)");

  // roll to season 2: the cut goes up
  let guard = 240, r;
  while (guard-- > 0){ r = dbg.playNext(true); if (r.done || r.exited || r.state === "seasonend") break; }
  dbg.nextSeasonSim();
  assert.equal(dbg.lifeInfo().vicCut, 11, "Vic's cut rises every season");
  assert.equal(dbg.lifeInfo().energy, 100, "fresh legs every new season");
});

test("life: protein shakes restore energy for monies, priced by your stars", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setMonies(500);
  dbg.setJourney({ energy: 40 });
  const price = dbg.shakePriceSim(0);
  assert.equal(price, 16, "SINGLE SCOOP at 1 star = 16 monies");
  assert.equal(dbg.buyShakeSim(0), true);
  let l = dbg.lifeInfo();
  assert.equal(l.energy, 90, "single scoop = +50 energy (NSS standard can)");
  assert.equal(l.monies, 500 - price);
  dbg.setJourney({ energy: 100 });
  assert.equal(dbg.buyShakeSim(0), false, "no shake-hoarding at full energy");
});

test("life: a trainer is hired by the block, tops up recovery, and says goodbye when it expires", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setMonies(500);
  assert.equal(dbg.hireTrainerSim("beef"), true);
  let l = dbg.lifeInfo();
  assert.equal(l.monies, 445, "Beef costs 55 for the block");
  assert.deepEqual({ id: l.trainer.id, games: l.trainer.games, rec: l.trainer.rec }, { id: "beef", games: 8, rec: 10 });
  for (let i = 0; i < 8; i++) dbg.playNext(true);
  l = dbg.lifeInfo();
  assert.equal(l.trainer, null, "the 8-game block is used up");
  // the goodbye is either still queued or already up on screen (the comms flush runs per match)
  assert.ok(l.msgs.includes("beef") || l.agentWho === "beef", "Beef says goodbye when the block expires");
});

test("life v3 (round 16): dearer trainers last far more games (NSS staff model)", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setMonies(2000);
  const lens = {};
  for (const id of ["beef", "sven", "proteina"]) {
    dbg.hireTrainerSim(id);
    lens[id] = dbg.lifeInfo().trainer.games;
  }
  assert.ok(lens.beef < lens.sven && lens.sven < lens.proteina,
    "contract length climbs with price: " + JSON.stringify(lens));
  assert.ok(lens.proteina >= 40, "the elite trainer lasts most of a season (" + lens.proteina + ")");
});

test("life v3 (round 16): a full match drains a starter's legs; rest is recorded", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setJourney({ trust: 100, energy: 100 });   // force a full-quota starter, fresh legs
  dbg.playNext(true);
  const en = dbg.lifeInfo().lastEnergy;
  assert.ok(en, "the match records an energy change");
  assert.ok(en.delta < 0, "a full match nets a drain even after a week's rest: " + JSON.stringify(en));
  assert.ok(en.rest >= 1, "rest days are recorded for the fixture");
  assert.ok(dbg.lifeInfo().energy < 100, "legs are lighter than before the match");
});

test("life v3 (round 16): the pay-day breakdown itemises the wage slip", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setJourney({ trust: 100, energy: 100 });
  dbg.playNext(true);   // a win with 2 goals (autoplay standard)
  const e = dbg.lifeInfo().lastEarn;
  assert.ok(e.wage > 0, "an appearance fee");
  assert.equal(e.gross, e.wage + e.win + e.goalPay + e.spons, "gross = the itemised lines");
  assert.equal(e.net, e.gross - e.cut, "net = gross minus Vic's cut");
});

test("life: no clobber, no sponsors — lifestyle raises effective rep and unlocks deals", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  dbg.setJourney({ rep: 30 });
  assert.equal(dbg.signSponsorSim(), false, "sponsors want a player WITH a lifestyle");
  dbg.setMonies(500);
  assert.equal(dbg.buyItemSim("trackie"), true);
  let l = dbg.lifeInfo();
  assert.equal(l.lifeBonus, 1);
  assert.equal(l.effRep, 31, "effective rep = earned rep + lifestyle");
  assert.equal(dbg.signSponsorSim(), true);
  l = dbg.lifeInfo();
  assert.equal(l.sponsor.name, "CRISPY NUGGZ", "effRep 31 reaches the tier-2 deal");
  assert.equal(l.sponsor.left, 20);
  dbg.playNext(true);
  assert.equal(dbg.lifeInfo().sponsor.left, 19, "each match burns a sponsor appearance");
});

test("life: the sponsored ad pays once per matchday, tax-free (Vic doesn't know)", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  const m0 = dbg.lifeInfo().monies;
  assert.equal(dbg.watchAdSim(), true);
  assert.equal(dbg.lifeInfo().monies, m0 + 4, "+4, no cut taken");
  assert.equal(dbg.watchAdSim(), false, "one word from the sponsors per matchday");
  dbg.playNext(true);
  assert.equal(dbg.watchAdSim(), true, "a new matchday brings a new ad");
});

// ================= E8.2 (owner round 14): contracts, prize money, ledger, tutorial, slower XI =================

test("life v2: a contract sets the pay; every pound lands in the season ledger", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  const c = dbg.lifeInfo().contract;
  assert.ok(c && c.wage >= 2 && c.winB > 0, "a contract is negotiated at signing: " + JSON.stringify(c));
  assert.equal(c.goalB, 0, "owner round 17: a win bonus, but NO goal bonus");
  dbg.playNext(true);   // a win (the autoplay standard)
  const l = dbg.lifeInfo();
  assert.equal(l.lastEarn.gross, c.wage + c.winB, "gross = wage + win bonus (no goal money)");
  assert.equal(l.ledger.wages, c.wage, "the ledger books the wage");
  assert.equal(l.ledger.bonus, c.winB, "and the win bonus");
  assert.equal(l.ledger.vic, l.lastEarn.cut, "and Vic's slice");
});

test("life v2: a transfer brings a signing-on fee and a renegotiated contract", async () => {
  const { dbg } = await loadGame();
  dbg.fakeSeasonEnd(1, 90);
  const before = dbg.lifeInfo().monies;
  dbg.nextSeasonSim("RealMadrid", "ESP");
  const l = dbg.lifeInfo();
  assert.ok(l.ledger.signing > 0, "a signing-on fee is banked");
  assert.ok(l.monies > before, "the fee lands (after Vic)");
  assert.ok(l.contract.wage > 30, "Real Madrid pay superstar wages: " + l.contract.wage);
  assert.ok(l.msgs.includes("vic") || l.agentWho === "vic", "Vic announces the deal");
});

test("life v2: the season's prize money lands with the review", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  let guard = 240, r;
  while (guard-- > 0){ r = dbg.playNext(true); if (r.done || r.exited || r.state === "seasonend") break; }
  const l = dbg.lifeInfo();
  assert.ok(l.prize && l.prize.gross > 0, "champions bank prize money: " + JSON.stringify(l.prize));
  assert.equal(l.ledger.prize, l.prize.gross, "and it's in the books");
});

test("vic v2: speeches read out one sentence at a time", async () => {
  const { dbg } = await loadGame();
  const r = dbg.agentSim("intro");
  assert.ok(r.pages >= 4, "the long intro paginates into sentences (got " + r.pages + " pages)");
  assert.ok(r.len < 200, "each page is a sentence, not the whole wall of text");
});

test("journey v2: the tutorial queues at career start and the XI takes longer to crack", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("England", "ENG2", "Millwall");
  const msgs = dbg.lifeInfo().msgs;
  assert.ok(msgs.filter(w => w === "vic").length >= 6, "Vic's tutorial + season brief are queued (" + msgs.length + " msgs)");
  // 5 straight wins used to be enough for the XI; not any more
  for (let i = 0; i < 5; i++) dbg.playNext(true);
  assert.notEqual(dbg.journeyInfo().role, "starter", "five good games no longer walk into the starting eleven");
});

test("life: a pre-Life save migrates with some savings put by", async () => {
  const { dbg, sandbox } = await loadGame();
  dbg.newCareerSim("England", "ENG", "Liverpool");
  const save = JSON.parse(sandbox.localStorage.getItem("vc_career"));
  delete save.monies; delete save.items; delete save.trainer; delete save.sponsor; delete save.msgs; delete save.earned;
  save.season = 3;
  sandbox.localStorage.setItem("vc_career", JSON.stringify(save));
  dbg.loadCareerSim();
  const l = dbg.lifeInfo();
  assert.equal(l.monies, 400, "season-3 pro migrates with 100 + 2x150 savings");
  assert.equal(l.vicCut, 12, "Vic's cut tracks the season even for migrated saves");
});

test("journey: a pre-journey save migrates to an established starter (never a downgrade)", async () => {
  const { dbg, sandbox } = await loadGame();
  dbg.newCareerSim("England", "ENG", "Liverpool");
  const save = JSON.parse(sandbox.localStorage.getItem("vc_career"));
  delete save.rep; delete save.energy; delete save.trust; delete save.objective; delete save.verdict;
  save.titles = 1; save.trophies = [{ t: "league", s: 1, club: "Liverpool" }];
  sandbox.localStorage.setItem("vc_career", JSON.stringify(save));
  const m = dbg.loadCareerSim();
  assert.ok(m.rep >= 35, "an existing career is never an unknown (rep " + m.rep + ")");
  assert.equal(m.trust, 70, "an existing career keeps its starting spot");
  assert.equal(m.energy, 100);
  assert.equal(dbg.journeyInfo().unlocks.freestart, true, "existing titles count toward free start");
});
