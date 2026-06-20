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

test("losing season 1: 0 pts, cup KO after one tie, group-stage international exit", async () => {
  const { dbg } = await loadGame();
  dbg.newCareerSim("Brazil");
  const c = playSeason(dbg, false);
  assert.equal(c.L, 38, "all league games are still played (no KO)");
  assert.equal(c.C, 1,  "knocked out of the cup after the first tie");
  assert.equal(c.E, 0);
  assert.equal(c.I, 3,  "World Tournament: 3 group games, then eliminated");
  assert.equal(c.total, 42);

  const info = dbg.careerInfo();
  assert.equal(info.pts, 0, "lose all 38 -> 0 pts");
  assert.equal(info.cup.out, true);
  assert.equal(info.cup.won, false);
  assert.equal(info.caps, 3);
  assert.ok(!info.trophies.includes("cup"));
  assert.ok(!info.trophies.includes("intl"));
  assert.ok(!info.trophies.includes("euro"));
  assert.ok(info.nextEuro == null, "no European qualification");
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
