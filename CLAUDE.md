# SCORDAGOL — session bootstrap

**Read [`HANDOVER.md`](HANDOVER.md) §0 before doing anything — it is the single source of
truth for current state and the next tasks.** ("Keep going" = its Open/next priority list.)

## Non-negotiables
- **Sacred physics:** `logicStep()`, `savedCheck()` and the constants block in `index.html` are
  transcribed from the original game. NEVER change them without the CI goldens proving outcomes identical.
- **Full CI gate before ANY push** (subsets spam the owner with CI emails):
  `node ci/smoke.js && node --test ci/physics.test.js ci/career.test.js ci/horse.test.js ci/leagues.test.js`
  — must print `SMOKE PASS` and 28/28 pass.
- **`main` deploys automatically** (GitHub Pages = the live game). Work on a short-lived
  `claude/<topic>` branch; land with `git push origin <branch>:main`; delete the branch after.
  Visual changes need the owner's eyeball before landing on `main`.
- **Never** wipe the `vc_career` localStorage save (migrate it), put `pixel`/`ad`/`advert`/`track`
  in an asset filename (adblockers), or add a `fetch`/asset load without a visible failure path.

## Working here
- The whole game is `index.html` (vanilla JS + Canvas). Dev server: `python serve.py` →
  http://localhost:5578/index.html (threaded no-cache — keep it threaded). `?cap=1` exposes the
  `__dbg` test harness. Windows: `play.bat` / `stop.bat`.
- After any menu/HUD/`draw*` edit, run the `menu-layout-audit` skill (`.claude/skills/`).
- Fresh machine: `pip install numpy pillow` (artgen), `npm install puppeteer-core --no-save`
  (layout audit). CI needs only Node built-ins.
- The owner is non-technical: plain English, lead the process, give him copy-paste-free steps.
- Owner reports "lag/stutter"? Check the machine's display refresh rate FIRST (HANDOVER §0 gotcha —
  a 4K monitor at 30Hz caused a phantom "regression" once).

Docs map: `HANDOVER.md` (state) → `ROADMAP.md` (plan/decisions) → `docs/*` (binding specs) →
`PROJECT_HEALTH_AUDIT.md` (2026-07-01 audit) → `AUDIT.md` (historical, do not treat as current).
