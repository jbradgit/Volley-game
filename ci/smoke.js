// Headless smoke test: runs the game's <script> in Node with DOM stubs and drives the
// ?cap=1 __dbg harness through real physics shots + full render frames. Catches runtime
// ReferenceErrors / broken draw paths that a syntax check can't.
// (Pixel-dependent outcomes differ from a browser — the stub canvas has no pixels, so the
//  keeper never "saves" here; goals/posts/misses resolve exactly as in the real game.)
//
// Run:  node ci/smoke.js     (exit 0 = pass)
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");

// ---- minimal DOM/browser stubs ----
const ctxStub = () => new Proxy({}, {
  get(t, p) {
    if (p === "measureText") return () => ({ width: 10 });
    if (p === "getImageData") return (x, y, w, h) => ({ data: new Uint8ClampedArray((w || 1) * (h || 1) * 4) });
    if (p === "createImageData") return (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h });
    if (p === "createLinearGradient" || p === "createRadialGradient") return () => ({ addColorStop: () => {} });
    if (typeof p === "string") return () => {};
    return undefined;
  },
  set() { return true; }
});
const mkCanvas = () => ({
  width: 0, height: 0, style: {},
  getContext: () => ctxStub(),
  toDataURL: () => "data:image/png;base64,",
  addEventListener: () => {}, setPointerCapture: () => {},
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 924, height: 520 }),
});
class StubImage {
  constructor() { this.complete = false; this.naturalWidth = 0; }
  set src(v) { this._src = v; this.complete = true; this.naturalWidth = 100; this.naturalHeight = 100;
               if (this.onload) this.onload(); }
  get src() { return this._src; }
}
class StubAudio {
  constructor() { this.muted = false; this.volume = 1; this.currentTime = 0; }
  play() { return { then: (f) => { f && f(); return { catch: () => {} }; }, catch: () => {} }; }
  pause() {} cloneNode() { return new StubAudio(); }
}
const store = {};
const sandbox = {
  console, Math, JSON, Date, parseInt, parseFloat, isNaN, Number, String, Object, Array,
  Uint8ClampedArray, Promise, Error, RegExp,
  performance: { now: () => Date.now() },
  requestAnimationFrame: () => 0,
  setInterval: () => 0, setTimeout: () => 0, clearInterval: () => {},
  location: { search: "?cap=1" },
  localStorage: { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } },
  document: {
    getElementById: () => Object.assign(mkCanvas(), { value: "", focus: () => {}, blur: () => {} }),
    createElement: () => mkCanvas(),
    addEventListener: () => {},
    activeElement: null,
    fullscreenElement: null,
  },
  Image: StubImage, Audio: StubAudio,
  fetch: (url) => {                       // serve real repo files so teams/ads/atlas are genuine
    const f = path.join(ROOT, url.split("?")[0]);
    try {
      const txt = fs.readFileSync(f, "utf8");
      return Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(txt)) });
    } catch (e) { return Promise.reject(new Error("404 " + url)); }
  },
};
sandbox.window = sandbox;
sandbox.window.matchMedia = () => ({ matches: false });
sandbox.window.addEventListener = () => {};
sandbox.window.innerWidth = 1280; sandbox.window.innerHeight = 720;
sandbox.window.devicePixelRatio = 1;

// ---- load the game ----
const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
const vm = require("vm");
vm.createContext(sandbox);
vm.runInContext(js, sandbox, { filename: "index.html<script>" });

const fail = (m) => { console.error("FAIL:", m); process.exit(1); };
const dbg = sandbox.window.__dbg;
if (!dbg) fail("__dbg harness not exposed under ?cap=1");

(async () => {
  await new Promise(r => setTimeout(r, 0) || setImmediate(r));   // let fetch promises settle

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

  console.log("SMOKE PASS");
})().catch(e => fail(e.stack || e));
