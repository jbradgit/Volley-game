// Headless smoke test: runs the game's <script> in Node with DOM stubs and drives the
// ?cap=1 __dbg harness through real physics shots + full render frames. Catches runtime
// ReferenceErrors / broken draw paths that a syntax check can't.
// (Pixel-dependent outcomes differ from a browser — the stub canvas has no pixels, so the
//  keeper never "saves" here; goals/posts/misses resolve exactly as in the real game.)
//
// Run:  node ci/smoke.js     (exit 0 = pass)
// Deeper career-invariant coverage lives in ci/career.test.js (node --test).
"use strict";
const { loadGame } = require("./harness");

(async () => {
  const { dbg } = await loadGame();
  const fail = (m) => { console.error("FAIL:", m); process.exit(1); };
  if (!dbg) fail("__dbg harness not exposed under ?cap=1");

  // 0. render the title screen (exercises ttClear/drawMenu/_buildLogo/_ball8)
  dbg.tick(); dbg.tick();
  console.log("menu render ok");

  // 1. the timing sweep finds connecting shots, and a full shot resolves to a result
  const sw0 = dbg.sweep(300, 20, 37, true);
  if (!sw0.length) fail("sweep found no connecting kick timings");
  const shot = dbg.realShot(300, sw0[0].kt, 20, 37, true);
  if (!shot.connected) fail("realShot did not connect at swept timing: " + JSON.stringify(shot));
  if (!shot.result) fail("shot produced no result text");
  console.log("shot:", JSON.stringify(shot));

  // 2. a straight goal triggers scoring + the net-bulge path
  dbg.serve(20, 37);          // resets the physics clock (forceShot alone inherits stale t)
  dbg.forceShot(282, 0, 30);  // central, below the bar at resolution -> clean goal
  let v;
  for (let i = 0; i < 200 && (v = dbg.step(1)).state === "flight"; i++);
  if (!v || v.state !== "result") fail("forced goal did not reach RESULT: " + JSON.stringify(v));
  const vars = dbg.vars();
  if (vars.score < 4000) fail("goal did not score 4000+: " + vars.score);
  console.log("goal ok, score:", vars.score);

  // 3. full render frames (exercises drawBackdrop/drawHoardings/drawGoal incl. bulge decay)
  for (let i = 0; i < 30; i++) dbg.tick();
  console.log("render x30 ok");

  // 4. timing sweep returns connected shots
  const sw = dbg.sweep(300, 20, 37, true);
  if (!sw.length) fail("sweep found no connecting kick timings");
  console.log("sweep:", sw.length, "connecting timings, first:", JSON.stringify(sw[0]));

  // 5. season end -> Smail offers carry the new sender fields; screen renders
  const se = dbg.fakeSeasonEnd(1);
  if (se.state !== "seasonend") fail("fakeSeasonEnd did not reach SEASONEND: " + JSON.stringify(se));
  if (!se.offers.length) fail("champion season generated no transfer offers");
  dbg.tick(); dbg.tick();
  console.log("season end ok, offers:", se.offers.join(", "));

  // 6. full career autoplay: 38 league + 5 cup + 6 World Tournament matches, all won
  dbg.newCareerSim("Brazil");
  let played = 0, guard = 120, r6;
  while (guard-- > 0){
    r6 = dbg.playNext(true);
    if (r6.ev || (r6.trn && !r6.exited)) played++;          // count matches, incl. the season's last
    dbg.tick();                                              // render whichever home view comes next (league/cup/euro/hub)
    if (r6.done || r6.exited || r6.state === "seasonend") break;
  }
  const info = dbg.careerInfo();
  if (played !== 49) fail("expected 49 events in a winning season 1 (38L+5C+6I), played " + played);
  if (info.trophies.indexOf("cup") < 0)  fail("cup not won: " + JSON.stringify(info));
  if (info.trophies.indexOf("intl") < 0) fail("world tournament not won: " + JSON.stringify(info));
  if (info.caps !== 6) fail("expected 6 caps, got " + info.caps);
  if (info.nextEuro !== "CT") fail("champions should qualify for CT, got " + info.nextEuro);
  console.log("season 1 autoplay ok:", played, "matches, trophies:", info.trophies.join("+"), "pts:", info.pts);

  // 7. season 2 carries a European campaign; win everything -> 51 events (38L+5C+8E)
  const s2 = dbg.nextSeasonSim();
  if (!s2.euro) fail("no European campaign in season 2 despite qualification");
  let played2 = 0; guard = 130;
  while (guard-- > 0){
    const r = dbg.playNext(true);
    if (r.ev || (r.trn && !r.exited)) played2++;
    dbg.tick();
    if (r.done || r.exited || r.state === "seasonend") break;
  }
  const info2 = dbg.careerInfo();
  if (played2 !== 51) fail("expected 51 events in winning season 2 (38L+5C+8E), played " + played2);
  if (info2.trophies.indexOf("euro") < 0) fail("euro not won: " + JSON.stringify(info2));
  console.log("season 2 autoplay ok:", played2, "matches, euro stage:", info2.euro);

  // 8. the universal kit renderer builds all per-match sprites without error
  const kt = dbg.buildKitsTest();
  if (!kt.ready || !kt.striker || !kt.def || !kt.gk) fail("kit build failed: " + JSON.stringify(kt));
  console.log("kit build ok:", JSON.stringify(kt));

  console.log("SMOKE PASS");
})().catch(e => { console.error("FAIL:", e.stack || e); process.exit(1); });
