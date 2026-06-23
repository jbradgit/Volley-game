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
  const r = dbg.newCareerSim("Spain", "ESP");
  assert.equal(r.leagueId, "ESP", "career not in ESP");
  assert.equal(r.teams, 10, "ESP should have 10 clubs");
  const std = dbg.standings ? dbg.standings() : null;
  // the player's club must be one of the league's clubs (not an English one)
  const espSlugs = ["RealMadrid", "Barcelona", "Valencia", "Deportivo", "Sevilla", "Villarreal", "AthBilbao", "RealSociedad", "Betis", "CeltaVigo"];
  assert.ok(espSlugs.includes(r.slug), "career slug not a La Liga club: " + r.slug);
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
