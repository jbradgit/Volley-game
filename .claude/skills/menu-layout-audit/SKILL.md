---
name: menu-layout-audit
description: >-
  Headless layout linter for SCORDAGOL's canvas menus/screens. Renders every teletext/menu
  screen in real Chrome, instruments the 2D context, and flags text that overflows its box,
  text that runs off-screen or hugs an edge, and bars that cover the decorative frame. Use
  after editing ANY drawMenu / drawMPMenu / drawHorse* / drawClassic* / drawHUD layout, or
  before a deploy, to catch "text doesn't fit / things are misaligned / spaced wrong" issues
  automatically instead of by eye.
---

# menu-layout-audit

SCORDAGOL's UI is hand-laid-out with `ctx.fillText` / `strokeRect` at absolute coordinates,
so it's easy to ship a screen where text spills its box, runs off the 924×520 frame, or a
title bar covers the decorative border. This skill catches those automatically.

## What it checks

Per screen (logical space is 924×520; the linter is transform-aware so celebration text drawn
via `ctx.translate` is measured at its real on-screen position):

- **OVERFLOW** — a `fillText` whose horizontal extent spills the `strokeRect` box it sits in
  (the "text doesn't fit in the box" bug). Boxes = stroked rects 40–924 wide, 18–64 tall.
- **OFFSCREEN** — text whose bounding box leaves `[0..924]×[0..520]`.
- **EDGE** — text within 6px of a left/right edge (cramped).
- **FRAMECOVER** — a tall (≥14px) full-width filled bar at the top crossing the 9/16px
  decorative frame (the "huge banner covering the frame" bug). Only on `framed: true` screens.

Thin CRT scanlines (`ttClear`, h≈1) and the background fill are ignored.

It also writes a PNG of every screen to `%TEMP%/volley_audit/` for eyeball confirmation —
**always Read a couple of those too**; the linter catches geometry, not ugliness.

## How to run

```bash
# 1. static server (the preview MCP server is unreliable here — run your own)
python -m http.server 5577 --bind 127.0.0.1   # in background, from the repo root

# 2. one-time: the browser driver (not committed; no bundled Chromium)
npm install puppeteer-core --no-save

# 3. audit
node .claude/skills/menu-layout-audit/audit.mjs
```

Exit code `0` = clean, `1` = issues found (each printed as `TYPE "text" coords`). It auto-detects
system Chrome/Edge; override with `CHROME=<path-to-exe>` and the URL with `AUDIT_URL=`.

It drives screens through the `?cap=1` `window.__dbg` harness (`renderStateSim`, `horseStart`,
`horsePlay`, `classicStart`, `classicPlay`). To add a screen, append to the `SCREENS` array with
its `state` (an `ST.*` key) and a `setup` string run in-page first. Set `framed:true` for screens
that draw the blue/magenta decorative border (main menu, multiplayer hub).

## When to use

- After any edit to `drawMenu`, `drawMPMenu`, `drawHorseSetup`, `drawHorseStandings`,
  `drawHorsePass`, `drawHorseEnd`, `drawClassic*`, `drawHUD`/`drawHorseHUD`, or the shared
  `ttBar`/`fitFill` helpers.
- As a gate before `/rebake-deploy` for any index.html-only menu/HUD change.

## Notes / limits

- Logical-space only; the in-match field HUD uses a `translate(OX)` field-centring transform —
  the linter handles uniform translate/scale but not the rotated confetti (which is decorative).
- Heuristic box-matching (text-centre inside a stroked rect). False negatives are possible for
  unusual layouts — the PNGs are the backstop. Tune `BOX_PAD` / `EDGE_MARGIN` at the top of
  `audit.mjs` if needed.
