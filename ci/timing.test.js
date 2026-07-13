// VOLLEY TIMING tests (node --test) — NON-golden. These guard the player-facing volley-timing
// calibration (pause menu: EARLIER / STANDARD / LATER), which shifts the input->contact interval
// by +/-1 tick. STANDARD (0) MUST equal the sacred KICK_FRAMES so the physics goldens are
// untouched; seeded matches (daily / HORSE / classic) must ignore the setting so shared
// leaderboards stay fair. See docs/CAREER_DESIGN or HANDOVER for the design note.
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadGame } = require("./harness");

test("effective kick frames: STANDARD == sacred 5, EARLIER 4, LATER 6", async () => {
  const { dbg } = await loadGame();
  assert.equal(dbg.kickFrames(), 5, "default (STANDARD) is the sacred KICK_FRAMES");
  dbg.setVolleyTiming(-1); assert.equal(dbg.kickFrames(), 4, "EARLIER pulls contact one tick sooner");
  dbg.setVolleyTiming(1);  assert.equal(dbg.kickFrames(), 6, "LATER pushes contact one tick later");
});

test("the setting clamps to -1..+1", async () => {
  const { dbg } = await loadGame();
  assert.equal(dbg.setVolleyTiming(5), 1, "over-max clamps to LATER");
  assert.equal(dbg.setVolleyTiming(-9), -1, "under-min clamps to EARLIER");
});

test("a seeded match locks VOLLEY TIMING to STANDARD", async () => {
  const { dbg } = await loadGame();
  dbg.setVolleyTiming(-1);
  dbg.setSeeded(true);
  assert.equal(dbg.kickFrames(), 5, "seeded (daily/HORSE/classic) ignores the setting");
  dbg.setSeeded(false);
  assert.equal(dbg.kickFrames(), 4, "unseeded honours it again");
});

// Integration: the shift genuinely moves the contact tick, and the effect is exactly +/-1 tick.
// Contact lands at (kt + effectiveKickFrames), so triggering the kick one tick earlier while timing
// is LATER (+1) — or one tick later while EARLIER (-1) — lands on the SAME contact tick, hence the
// same contact point. realShot(300,29,20,37,true) is the known-connecting golden shot at STANDARD.
test("the timing shift moves contact by exactly one tick (compensation invariant)", async () => {
  const { dbg } = await loadGame();
  const base = dbg.realShot(300, 29, 20, 37, true);          // STANDARD, kt=29 -> contact @ tick 34
  assert.equal(base.connected, true, "baseline shot connects");

  dbg.setVolleyTiming(1);
  const later = dbg.realShot(300, 28, 20, 37, true);          // LATER(+1), kt=28 -> contact @ tick 34
  dbg.setVolleyTiming(-1);
  const earlier = dbg.realShot(300, 30, 20, 37, true);        // EARLIER(-1), kt=30 -> contact @ tick 34
  dbg.setVolleyTiming(0);

  assert.equal(later.connected, true, "compensated LATER shot connects");
  assert.equal(earlier.connected, true, "compensated EARLIER shot connects");
  assert.equal(later.contactX, base.contactX, "LATER +1 with the kick one tick earlier meets the ball at the same point");
  assert.equal(earlier.contactX, base.contactX, "EARLIER -1 with the kick one tick later meets the ball at the same point");
});

test("seeded lock holds through a real shot", async () => {
  const { dbg } = await loadGame();
  const base = dbg.realShot(300, 29, 20, 37, true);          // STANDARD
  dbg.setSeeded(true);
  dbg.setVolleyTiming(-1);                                    // would shift contact if honoured
  const locked = dbg.realShot(300, 29, 20, 37, true);
  assert.equal(locked.contactX, base.contactX, "a seeded match plays the standard timing regardless of the setting");
});
