// Foreign-league career tests (node --test). Verifies E3: leagues.json loads, a foreign-league
// career uses that league's clubs, and a full season autoplays without error.
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadGame } = require("./harness");

test("leagues.json loads 5 elite leagues with clubs", async () => {
  const { dbg } = await loadGame();
  const lgs = dbg.leaguesSim();
  const ids = lgs.map(l => l.id);
  for (const id of ["ENG", "ESP", "ITA", "GER", "FRA"]) assert.ok(ids.includes(id), "missing league " + id);
  for (const l of lgs) assert.ok(l.teams >= 8, l.id + " has too few clubs: " + l.teams);
});

test("a Spanish-league career uses Spanish clubs and a Spanish slug", async () => {
  const { dbg } = await loadGame();
  const r = dbg.newCareerSim("Spain", "ESP", "RealMadrid");
  assert.equal(r.leagueId, "ESP", "career not in ESP");
  assert.equal(r.teams, 20, "La Liga should have its full 20 clubs");
  assert.equal(r.slug, "RealMadrid", "career slug should be the chosen La Liga club, got " + r.slug);
});

test("all foreign leagues have full real-life sizes", async () => {
  const { dbg } = await loadGame();
  const sizes = {}; for (const l of dbg.leaguesSim()) sizes[l.id] = l.teams;
  assert.equal(sizes.ESP, 20, "La Liga"); assert.equal(sizes.ITA, 20, "Serie A");
  assert.equal(sizes.GER, 18, "Bundesliga"); assert.equal(sizes.FRA, 20, "Ligue 1");
  assert.equal(sizes.ENG, 20, "Premier League");
});

test("the league-select screen renders without error", async () => {
  const { dbg, errors } = await loadGame();
  dbg.renderStateSim("LEAGUESEL");
  assert.equal(errors.length, 0, "errors rendering league select: " + errors.join(" | "));
});

test("a foreign-league season autoplays to completion without error", async () => {
  const { dbg, errors } = await loadGame();
  dbg.newCareerSim("Italy", "ITA");
  let played = 0, guard = 200, r;
  while (guard-- > 0) {
    r = dbg.playNext(true);
    if (r.ev || (r.trn && !r.exited)) played++;
    dbg.tick();
    if (r.done || r.exited || r.state === "seasonend") break;
  }
  assert.ok(played >= 18, "Italian season should have >=18 league matches, played " + played);
  assert.equal(errors.length, 0, "console errors during foreign-league season: " + errors.join(" | "));
});

test("a foreign-league European campaign never draws the player against themselves", async () => {
  const { dbg, errors } = await loadGame();
  dbg.newCareerSim("Spain", "ESP", "RealMadrid");   // rating 10 -> Champions Trophy when champions
  let guard = 220, r;
  while (guard-- > 0) { r = dbg.playNext(true); dbg.tick(); if (r.done || r.exited || r.state === "seasonend") break; }
  const s2 = dbg.nextSeasonSim();
  assert.ok(s2.euro, "no European campaign in season 2 after winning La Liga");
  const e = dbg.euroSim();
  assert.ok(e, "euro not initialised");
  assert.ok(!e.group.includes("RealMadrid"), "player drawn into their own Euro group: " + JSON.stringify(e.group));
  guard = 240;
  while (guard-- > 0) { r = dbg.playNext(true); dbg.tick(); if (r.done || r.exited || r.state === "seasonend") break; }
  const e2 = dbg.euroSim();
  if (e2) assert.ok(e2.sfOpp !== "RealMadrid" && e2.fOpp !== "RealMadrid", "player drawn vs self in Euro KO");
  assert.equal(errors.length, 0, "errors in foreign-league Euro season: " + errors.join(" | "));
});
