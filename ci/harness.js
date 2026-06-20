// Shared test harness: load the whole game (index.html's <script>) into a fresh Node VM
// context with minimal DOM/browser stubs, drive it through the ?cap=1 __dbg harness.
// Used by ci/smoke.js and ci/*.test.js. Each loadGame() call is fully isolated — its own
// sandbox, localStorage and career state — so tests can't bleed into each other.
//
// (Pixel-dependent outcomes differ from a real browser — the stub canvas has no pixels, so
//  the keeper never "saves" here; goals/posts/misses resolve exactly as in the real game.)
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
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

function makeSandbox() {
  const store = {};
  const errors = [], warns = [];
  // forward to the real console (so smoke.js output is preserved) but also capture for assertions
  const cons = Object.assign(Object.create(console), {
    error: (...a) => { errors.push(a.map(String).join(" ")); console.error(...a); },
    warn:  (...a) => { warns.push(a.map(String).join(" ")); console.warn(...a); },
  });
  const sandbox = {
    console: cons, Math, JSON, Date, parseInt, parseFloat, isNaN, Number, String, Object, Array,
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
    fetch: (url) => {                       // serve real repo files so teams/ads/atlas/world are genuine
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
  return { sandbox, errors, warns };
}

// Load a fresh game instance. Returns { dbg, window, sandbox, errors, warns }.
// `errors`/`warns` accumulate anything the game logs to console.error/warn after this point.
async function loadGame() {
  const { sandbox, errors, warns } = makeSandbox();
  const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
  const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
  vm.createContext(sandbox);
  vm.runInContext(js, sandbox, { filename: "index.html<script>" });
  await new Promise(r => setImmediate(r));   // let fetch (.then) settle so WORLD/teams/ads are loaded
  const dbg = sandbox.window.__dbg;
  if (!dbg) throw new Error("__dbg harness not exposed (ensure location.search is ?cap=1)");
  return { dbg, window: sandbox.window, sandbox, errors, warns };
}

module.exports = { loadGame };
