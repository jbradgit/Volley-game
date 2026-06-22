// HORSE multiplayer regression tests (node --test). Drives the rewritten state machine
// through the __dbg hooks (horseStart / horsePlay(scored) / horseState) — no real shots, so
// the rules are tested in isolation. The mechanic: the leader takes a delivery; if they SCORE,
// every other active player must score the SAME delivery or take the next letter of the word
// (independently). Leader keeps the initiative until they miss. Spell the word = out; last in wins.
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadGame } = require("./harness");

test("a missed setting shot passes leadership and assigns no letters", async () => {
  const { dbg } = await loadGame();
  let s = dbg.horseStart(["A", "B"], "HORSE");
  assert.equal(s.players.length, 2);
  assert.equal(s.phase, "lead");
  assert.equal(s.leader, 0);
  assert.equal(s.current, 0);

  s = dbg.horsePlay(false);                  // leader A misses their own challenge
  assert.equal(s.phase, "lead", "no challenge was set");
  assert.equal(s.leader, 1, "leadership passes to B");
  assert.equal(s.current, 1);
  assert.equal(s.players[0].letters, 0, "you never get a letter for missing your own setting shot");
  assert.equal(s.players[1].letters, 0);
});

test("a follower who fails to match the leader's goal takes a letter", async () => {
  const { dbg } = await loadGame();
  dbg.horseStart(["A", "B"], "HORSE");
  let s = dbg.horsePlay(true);               // leader A scores -> challenge set
  assert.equal(s.phase, "follow");
  assert.equal(s.current, 1, "B must respond");
  assert.equal(s.leader, 0);

  s = dbg.horsePlay(false);                  // B fails to match
  assert.equal(s.players[1].letters, 1, "B takes a letter");
  assert.equal(s.players[0].letters, 0, "the leader is unaffected");
  assert.equal(s.phase, "lead", "back to the leader for a fresh challenge");
  assert.equal(s.leader, 0, "A keeps the initiative after setting a challenge");
  assert.equal(s.current, 0);
});

test("matching the leader's goal costs no letter", async () => {
  const { dbg } = await loadGame();
  dbg.horseStart(["A", "B"], "HORSE");
  dbg.horsePlay(true);                        // A scores
  const s = dbg.horsePlay(true);             // B matches
  assert.equal(s.players[1].letters, 0, "no letter for matching");
  assert.equal(s.phase, "lead");
  assert.equal(s.leader, 0);
});

test("spell the word and you're out; the last player standing wins", async () => {
  const { dbg } = await loadGame();
  dbg.horseStart(["A", "B"], "HORSE");        // 5-letter word
  let s;
  for (let i = 0; i < 5; i++){
    s = dbg.horsePlay(true);                  // A (leader) scores
    s = dbg.horsePlay(false);                 // B fails to match -> a letter
  }
  assert.equal(s.players[1].letters, 5, "B has spelled HORSE");
  assert.equal(s.players[1].out, true, "B is eliminated");
  assert.equal(s.winner, 0, "A wins");
  assert.equal(s.state, "horseend");
});

test("letters are tracked independently across three players", async () => {
  const { dbg } = await loadGame();
  let s = dbg.horseStart(["A", "B", "C"], "HORSE");
  assert.equal(s.players.length, 3);

  s = dbg.horsePlay(true);                     // A scores -> B and C must respond
  assert.equal(s.phase, "follow");
  assert.equal(s.current, 1, "B responds first");

  s = dbg.horsePlay(false);                    // B misses -> B gets a letter
  assert.equal(s.players[1].letters, 1);
  assert.equal(s.current, 2, "C responds next");

  s = dbg.horsePlay(true);                     // C matches -> no letter
  assert.equal(s.players[2].letters, 0, "C is unaffected by B's miss (independent)");
  assert.equal(s.players[1].letters, 1);
  assert.equal(s.phase, "lead");
  assert.equal(s.leader, 0, "A keeps leading");
});

test("the word sets the number of lives (shorter word = quicker game)", async () => {
  const { dbg } = await loadGame();
  dbg.horseStart(["A", "B"], "GO");           // 2 letters
  dbg.horsePlay(true); let s = dbg.horsePlay(false);
  assert.equal(s.players[1].letters, 1);
  dbg.horsePlay(true); s = dbg.horsePlay(false);
  assert.equal(s.state, "horseend", "two misses spells GO");
  assert.equal(s.winner, 0);
});
