// menu-layout-audit — headless layout linter for SCORDAGOL's canvas screens.
//
// Renders each teletext/menu screen via the ?cap=1 __dbg harness with the 2D context
// instrumented to record every text/box/bar draw (transform-corrected to logical 924×520
// space), then flags the layout failures that keep recurring by eye:
//   • OVERFLOW   — text wider than the box it sits in (text doesn't fit / spills the border)
//   • OFFSCREEN  — text whose bounding box leaves the 924×520 frame
//   • EDGE       — text within EDGE_MARGIN px of an edge (cramped)
//   • FRAMECOVER — a tall full-width filled bar crossing the decorative frame (menu/hub only)
// It also writes a PNG of every screen to <tmp>/volley_audit for eyeball confirmation.
//
// Run:  node .claude/skills/menu-layout-audit/audit.mjs
//   needs a static server on :5577 (e.g. `python -m http.server 5577`) and puppeteer-core
//   + a Chrome/Edge. Override the browser with  CHROME=<path>  if auto-detect misses.
import puppeteer from 'puppeteer-core';
import fs from 'fs'; import path from 'path'; import os from 'os';

const VW = 924, SH = 520, EDGE_MARGIN = 6, BOX_PAD = 4;
const URL = process.env.AUDIT_URL || 'http://127.0.0.1:5578/?cap=1';
const OUT = path.join(os.tmpdir(), 'volley_audit');
fs.mkdirSync(OUT, { recursive: true });

const CHROME = process.env.CHROME || [
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
].find(p => fs.existsSync(p));
if (!CHROME) { console.error('No Chrome/Edge found — set CHROME=<path to chrome.exe>'); process.exit(2); }

// Screens to audit. `setup` runs in-page before the (instrumented) render; `state` is the
// ST.* render target. `framed` enables the FRAMECOVER check (decorative-border screens).
const SCREENS = [
  // worst-case home menu: a career save (4 options incl. CONTINUE CAREER) + a best score (full footer)
  { name: 'menu',            state: 'MENU',        framed: true, setup: "__dbg.newCareerSim('Brazil','ENG','Liverpool');__dbg.setBest(34700)" },
  { name: 'mpmenu',          state: 'MPMENU',      framed: true },
  { name: 'horsesetup_2p',   state: 'HORSESETUP',  setup: "__dbg.horseStart(['ALICE','BOB'],'HORSE')" },
  { name: 'horsesetup_6p',   state: 'HORSESETUP',  setup: "__dbg.horseStart(['ALICE','BOB','CARLA','DAN','EVE','FRANK'],'PIG')" },
  { name: 'classicsetup_6p', state: 'HORSESETUP',  setup: "__dbg.classicStart(['ALICE','BOB','CARLA','DAN','EVE','FRANK'])" },
  { name: 'horsepass_6p',    state: 'HORSEPASS',   setup: "__dbg.horseStart(['ALICE','BOB','CARLA','DAN','EVE','FRANK'],'HORSE');__dbg.horsePlay(true)" },
  { name: 'horseend',        state: 'HORSEEND',    setup: "__dbg.horseStart(['ALICE','BOB'],'PI');__dbg.horsePlay(true);__dbg.horsePlay(false);__dbg.horsePlay(true);__dbg.horsePlay(false)" },
  { name: 'classicpass',     state: 'CLASSICPASS', setup: "__dbg.classicStart(['ALICE','BOB','CARLA'])" },
  { name: 'classicend',      state: 'CLASSICEND',  setup: "__dbg.classicStart(['ALICE','BOB','CARLA']);__dbg.classicPlay(42000);__dbg.classicPlay(31000);__dbg.classicPlay(55000)" },
  // career + other screens
  { name: 'career_home',     state: 'TABLE',       setup: "__dbg.newCareerSim('Brazil','ENG','Liverpool')" },
  { name: 'name',            state: 'NAME' },
  { name: 'natsel',          state: 'NATSEL' },
  { name: 'clubsel',         state: 'CLUBSEL',     setup: "__dbg.newCareerSim('Brazil','ENG','Liverpool')" },
  { name: 'seasonend',       state: 'SEASONEND',   setup: "__dbg.fakeSeasonEnd(1)" },
  { name: 'inbox',           state: 'INBOX',       setup: "__dbg.fakeSeasonEnd(1)" },
  { name: 'trophy',          state: 'TROPHY',      setup: "__dbg.newCareerSim('Brazil','ENG','Liverpool')" },
  { name: 'dailyboard',      state: 'DAILYBOARD' },
  { name: 'over',            state: 'OVER' },
  // Slick Vic agent screen — the long intro is the worst case for text wrap/overflow on the right column
  { name: 'agent_intro',     state: 'AGENT',       setup: "__dbg.agentSim('intro')" },
  { name: 'agent_team',      state: 'AGENT',       setup: "__dbg.agentSim('team')" },
  { name: 'agent_callup',    state: 'AGENT',       setup: "__dbg.agentSim('callup_no')" },
];

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
  args: ['--no-sandbox', '--force-device-scale-factor=1'], defaultViewport: { width: 1000, height: 640 } });
const page = await browser.newPage();
page.on('console', m => { if (m.type() === 'error') console.log('PAGE ERR:', m.text()); });

// instrument the 2D context BEFORE any game code runs (records draws + their transform)
await page.evaluateOnNewDocument(() => {
  const C = CanvasRenderingContext2D.prototype, ops = [];
  window.__ops = ops; window.__rec = false;
  const px = f => { const m = /([0-9.]+)px/.exec(f || ''); return m ? +m[1] : 12; };
  const tf = ctx => { const m = ctx.getTransform(); return { a: m.a, b: m.b, c: m.c, d: m.d, e: m.e, f: m.f }; };
  for (const fn of ['fillText', 'strokeText']) {
    const orig = C[fn];
    C[fn] = function (t, x, y) {
      if (window.__rec && t !== '' && t != null) { const tm = this.measureText(String(t));
        ops.push({ kind: 'text', t: String(t), x, y, w: tm.width, fs: px(this.font),
          asc: tm.actualBoundingBoxAscent, desc: tm.actualBoundingBoxDescent,
          align: this.textAlign, base: this.textBaseline, m: tf(this) }); }
      return orig.apply(this, arguments);
    };
  }
  for (const fn of ['fillRect', 'strokeRect']) {
    const orig = C[fn];
    C[fn] = function (x, y, w, h) {
      if (window.__rec) ops.push({ kind: fn === 'fillRect' ? 'fill' : 'stroke', x, y, w, h, m: tf(this) });
      return orig.apply(this, arguments);
    };
  }
});

await page.goto(URL, { waitUntil: 'networkidle2' });
await page.waitForFunction(() => { try { return window.__dbg && document.querySelector('canvas').width > 100 && window.__dbg.leaguesSim().length; } catch (e) { return false; } }, { timeout: 15000 });
await new Promise(r => setTimeout(r, 800));
const SCALE = await page.evaluate(() => document.querySelector('canvas').width / 924);   // backing-store -> logical

// transform-correct to logical 924×520 space (handles the celebration translate/scale)
const L = (o) => ({ x: (o.m.a * o.x + o.m.e) / SCALE, y: (o.m.d * o.y + o.m.f) / SCALE, sx: o.m.a / SCALE, sy: o.m.d / SCALE });
function textBox(o) {
  const g = L(o), w = o.w * g.sx;
  let x0 = g.x; if (o.align === 'center') x0 = g.x - w / 2; else if (o.align === 'right' || o.align === 'end') x0 = g.x - w;
  let y0, y1;
  if (typeof o.asc === 'number' && !isNaN(o.asc)) { y0 = g.y - o.asc * g.sy; y1 = g.y + o.desc * g.sy; }  // real glyph bounds (relative to the active baseline)
  else { const fs = o.fs * g.sy; if (o.base === 'middle') { y0 = g.y - fs / 2; y1 = g.y + fs / 2; } else if (o.base === 'top') { y0 = g.y; y1 = g.y + fs; } else { y0 = g.y - fs * 0.78; y1 = g.y + fs * 0.22; } }
  return { x0, x1: x0 + w, y0, y1 };
}
const rectLogical = (o) => { const g = L(o); return { x: g.x, y: g.y, w: o.w * g.sx, h: o.h * g.sy }; };

let total = 0;
for (const s of SCREENS) {
  if (s.setup) await page.evaluate(s.setup).catch(e => console.log('setup err', s.name, e.message));
  const ops = await page.evaluate((st) => {
    window.__ops.length = 0; window.__rec = true;
    window.__dbg.renderStateSim(st);
    window.__rec = false;
    return window.__ops.slice();
  }, s.state);
  const url = await page.evaluate((st) => {
    window.__dbg.renderStateSim(st);
    const c = document.querySelector('canvas'), o = document.createElement('canvas');
    o.width = 924; o.height = 520; o.getContext('2d').drawImage(c, 0, 0, 924, 520);
    return o.toDataURL('image/png');
  }, s.state);
  fs.writeFileSync(path.join(OUT, s.name + '.png'), Buffer.from(url.split(',')[1], 'base64'));

  const texts = ops.filter(o => o.kind === 'text').map(o => ({ t: o.t, box: textBox(o) }));
  const boxes = ops.filter(o => o.kind === 'stroke').map(rectLogical).filter(b => b.w > 40 && b.h >= 18 && b.h <= 64);
  const findings = [];
  const r0 = n => n.toFixed(0);

  for (const t of texts) {
    const b = t.box;
    if (b.x0 < -0.5 || b.x1 > VW + 0.5 || b.y0 < -0.5 || b.y1 > SH + 0.5)
      findings.push(`OFFSCREEN  "${t.t}"  x[${r0(b.x0)}..${r0(b.x1)}] y[${r0(b.y0)}..${r0(b.y1)}]`);
    else if (b.x0 < EDGE_MARGIN || b.x1 > VW - EDGE_MARGIN)
      findings.push(`EDGE       "${t.t}"  x[${r0(b.x0)}..${r0(b.x1)}] (within ${EDGE_MARGIN}px of a side)`);
    const cy = (b.y0 + b.y1) / 2, cx = (b.x0 + b.x1) / 2;   // assign to its containing box
    t.bx = boxes.find(bx => cy > bx.y && cy < bx.y + bx.h && cx > bx.x && cx < bx.x + bx.w);
    if (t.bx && (b.x0 < t.bx.x + BOX_PAD - 0.5 || b.x1 > t.bx.x + t.bx.w - BOX_PAD + 0.5))
      findings.push(`OVERFLOW   "${t.t}"  text x[${r0(b.x0)}..${r0(b.x1)}] exceeds box x[${r0(t.bx.x)}..${r0(t.bx.x + t.bx.w)}]`);
  }
  // VCENTER only for SINGLE-line boxes (a lone value that should be centred); multi-line panels
  // (header+value, email rows) legitimately stack text, so skip them — the PNG is the backstop.
  for (const bx of boxes) {
    const inside = texts.filter(t => t.bx === bx);
    if (inside.length !== 1) continue;
    const b = inside[0].box, off = (b.y0 + b.y1) / 2 - (bx.y + bx.h / 2);
    if (Math.abs(off) > 2.5)
      findings.push(`VCENTER    "${inside[0].t}"  ${off > 0 ? 'low' : 'high'} by ${Math.abs(off).toFixed(1)}px in box y[${r0(bx.y)}..${r0(bx.y + bx.h)}]`);
  }
  // text-vs-text overlap (e.g. the footer controls hint colliding with a menu option)
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
    if (texts[i].t === texts[j].t) continue;            // identical strings = intentional shadow/outline layering
    const a = texts[i].box, b = texts[j].box;
    const ox = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), oy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
    if (ox > 3 && oy > 3) findings.push(`OVERLAP    "${texts[i].t}" x "${texts[j].t}"  (${ox.toFixed(0)}x${oy.toFixed(0)}px)`);
  }
  if (s.framed) {
    for (const o of ops.filter(o => o.kind === 'fill')) {            // tall full-width bar over the 9/16px frame
      const r = rectLogical(o);
      if (r.w >= VW * 0.85 && r.x <= 20 && r.y < 90 && r.h >= 14 && r.h < 80)
        findings.push(`FRAMECOVER fill bar x${r0(r.x)} w${r0(r.w)} y${r0(r.y)} h${r0(r.h)} crosses the decorative frame`);
    }
    for (const t of texts) {                                         // text intruding the decorative frame border
      const b = t.box;
      if (b.y1 > SH - 20 || b.y0 < 22 || b.x0 < 18 || b.x1 > VW - 18)
        findings.push(`FRAMEIN    "${t.t}" intrudes the frame  y[${r0(b.y0)}..${r0(b.y1)}] x[${r0(b.x0)}..${r0(b.x1)}]`);
    }
  }

  total += findings.length;
  console.log(`\n[${findings.length ? '✗ ' + findings.length : '✓ clean'}] ${s.name}  (${texts.length} texts, ${boxes.length} boxes)`);
  for (const f of findings) console.log('   ', f);
}

console.log(`\n${total === 0 ? '✓ LAYOUT CLEAN' : '✗ ' + total + ' layout issue(s)'} — PNGs in ${OUT}`);
await browser.close();
process.exit(total === 0 ? 0 : 1);
