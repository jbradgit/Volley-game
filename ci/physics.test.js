// Physics golden tests (node --test). The shot physics + scoring are transcribed from the
// original game and are SACRED (HANDOVER constraint #1 / ROADMAP working rules): they must
// not change without re-verifying outcomes. These lock the goal/miss resolution geometry —
// the net, the bar and both posts — plus determinism, through the ?cap=1 __dbg harness.
//
// forceShot(x0, dbx, z) sets a deterministic flight (no RNG, no defenders) and steps it to
// the goal line; window.__rs records the resolution (finalx, z, innet, bar, lp, rp).
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadGame } = require("./harness");

// Resolve a forced shot to its result. Returns { score, rs:{finalx,z,innet,bar,lp,rp,hk} }.
async function forced(x0, dbx, z){
  const { dbg, window } = await loadGame();
  dbg.serve(20, 37);            // reset the physics clock (forceShot alone inherits a stale t)
  dbg.forceShot(x0, dbx, z);
  let v; for (let i = 0; i < 200 && (v = dbg.step(1)).state === "flight"; i++);
  if (!v || v.state !== "result") throw new Error("shot did not resolve: " + JSON.stringify(v));
  return { score: dbg.vars().score, rs: window.__rs };
}

test("realShot is deterministic for identical inputs", async () => {
  const { dbg: a } = await loadGame();
  const { dbg: b } = await loadGame();
  // kt=28 connects under KICK_FRAMES=6 (the original; owner reverted the brief KICK_FRAMES=5 trial).
  const ra = a.realShot(300, 28, 20, 37, true);
  const rb = b.realShot(300, 28, 20, 37, true);
  assert.equal(JSON.stringify(rb), JSON.stringify(ra), "same inputs must yield identical physics");
  assert.equal(ra.connected, true, "the swept timing connects");
});

test("forceShot is deterministic", async () => {
  const a = await forced(282, 0, 30);
  const b = await forced(282, 0, 30);
  assert.equal(JSON.stringify(a), JSON.stringify(b));
});

test("a central, below-the-bar shot is a goal worth 4000", async () => {
  const r = await forced(282, 0, 30);
  assert.equal(r.rs.innet, true, "ball crosses the line into the net");
  assert.equal(r.rs.bar, false, "did not hit the bar");
  assert.equal(r.rs.lp, false, "did not hit the left post");
  assert.equal(r.rs.rp, false, "did not hit the right post");
  assert.equal(r.score, 4000, "a clean goal scores 4000");
});

test("a shot over the bar is not a goal", async () => {
  const over = await forced(282, 0, 80);
  const goal = await forced(282, 0, 30);
  assert.equal(over.rs.innet, false, "a high shot misses the net");
  assert.equal(over.score, 0, "no points for missing");
  assert.ok(over.rs.z > goal.rs.z, "the over-the-bar shot resolves higher than a goal");
});

test("shots wide of either post are not goals", async () => {
  const goal  = await forced(282, 0, 30);
  const right = await forced(470, 0, 30);
  const left  = await forced(120, 0, 30);
  assert.equal(right.rs.innet, false, "wide-right misses");
  assert.equal(right.score, 0);
  assert.equal(left.rs.innet, false, "wide-left misses");
  assert.equal(left.score, 0);
  assert.ok(right.rs.finalx > goal.rs.finalx, "wide-right resolves right of a central goal");
  assert.ok(left.rs.finalx  < goal.rs.finalx, "wide-left resolves left of a central goal");
});

test("a shot that strikes a post is kept out (woodwork)", async () => {
  const left = await forced(135, 0, 30);
  assert.equal(left.rs.lp, true, "left post struck");
  assert.equal(left.rs.rp, false);
  assert.equal(left.rs.innet, false, "woodwork keeps it out of the net");
  assert.equal(left.score, 150, "hitting the post scores the woodwork bonus, not a goal");

  const right = await forced(430, 0, 30);
  assert.equal(right.rs.rp, true, "right post struck");
  assert.equal(right.rs.lp, false);
  assert.equal(right.rs.innet, false);
  assert.equal(right.score, 150);
});

test("a shot that strikes the bar is kept out", async () => {
  const bar = await forced(282, 0, 40);
  assert.equal(bar.rs.bar, true, "crossbar struck");
  assert.equal(bar.rs.innet, false, "no goal off the bar");
  assert.equal(bar.score, 150, "woodwork, not a goal");
});

test("the timing sweep finds connecting shots carrying trajectory data", async () => {
  const { dbg } = await loadGame();
  const sw = dbg.sweep(300, 20, 37, true);
  assert.ok(sw.length >= 1, "at least one kick timing connects");
  for (const s of sw){
    assert.equal(typeof s.kt, "number", "kick-tick is recorded");
    assert.equal(typeof s.fx, "number", "final x is computed");
    assert.equal(typeof s.z,  "number", "resolution height is computed");
  }
});
