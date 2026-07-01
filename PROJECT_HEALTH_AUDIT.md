# PROJECT HEALTH AUDIT — SCORDAGOL / Volley-game

*Audit date: 2026-07-01 · Auditor: Claude Code (repository audit, read-only) · Commit audited: `b98ae86` on `claude/3d-character-sprites`*

**No files were modified, moved, or deleted during this audit.** One command with side effects was run: `git fetch --prune` (updates remote-tracking refs only — required for accurate divergence data). All other commands were read-only or the project's own headless tests.

---

# Executive summary

## Status: 🟠 AMBER — workable but needs attention

The **code and Git state are healthy** (would be Green on their own): the working tree is clean, all branches are linear and pushed, the full CI suite passes locally (SMOKE PASS + 28/28 golden tests), `git fsck` is clean, and there are no stashes, worktrees, conflicts, or unmerged remote work. What pulls the grade to Amber is **legal/IP exposure in a public repo** (critical relative to the stated goal of publishing and monetising) and a cluster of **stale documentation/config** that actively contradicts the current setup.

## Five most important findings

1. **[CONFIRMED — Critical for the publication goal] The public GitHub repo and live GitHub Pages site distribute copyrighted third-party material.** Two byte-identical copies of the original *Liverpool FC Volley Challenge* SWF (`original.swf` and `gamezip/content/.../LiverpoolFCVolleyChallengeV32PC.swf`, MD5 `D118A032...` both), a 1,238-file decompilation (`decomp/`, incl. 13.6 MB `swf.xml`), 6 SWF-ripped sound effects (`assets/snd/`), and real Premier League club names/kits are all tracked and publicly served. This is *known and planned for* (ROADMAP Track C.3: private workshop repo + `git filter-repo`), but it is not done, and every day it stays public increases history-rewrite cost and exposure.

2. **[CONFIRMED — High] Local `main` is 4 commits behind `origin/main`, and the deployed site is 2 commits behind the reviewed work branch.** Not dangerous (local `main` is a strict ancestor — a fast-forward fixes it), but anyone building from local `main` builds a stale game, and the finished, CI-green 2026-06-30 session work (`claude/3d-character-sprites`) is awaiting the owner's visual sign-off before deploy. This matches HANDOVER §0 exactly — the docs and reality agree.

3. **[CONFIRMED — Medium] Three configs still point at the retired dev port 5577:** `README.md` (says the game serves on 5577), `stop.bat` (kills only 5577 — **it can no longer stop the current server**, which runs on 5578), and `.claude/launch.json` (starts `python -m http.server 5577`, which also bypasses the no-cache threaded `serve.py` — the exact stale-content trap HANDOVER §0 spent hours debugging). `serve.py` and `play.bat` correctly use 5578.

4. **[CONFIRMED — Medium] The repo is ~137 MB packed with large binaries tracked directly:** `striker_base_v01.blend` 55.6 MB, two Ruffle `.wasm` 25.8 MB combined, `decomp/swf.xml` 13.6 MB, `decomp/bg/202.png` 4.6 MB. No Git LFS, no `.gitattributes`. HANDOVER says "don't commit `striker_base_v01.blend`" yet it is already tracked ("pre-existing") — ambiguous instruction, see Conflicting information. Most of this is resolved for free by the same C.3 history rewrite as finding 1.

5. **[CONFIRMED — Medium] A documented single point of failure exists for one asset source:** `assets/ui/New Vic.png` (the Slick Vic portrait trace source, 1.18 MB) is gitignored and exists **only on the original dev box** (HANDOVER §0 item 6). If that machine is lost, the source is gone (the shipped traced PNG survives). No other unbacked-up work was found — every commit is pushed, and the only untracked files are scratch tooling.

---

# Project map

| Item | Value |
|---|---|
| Repository root | `C:\Users\Volley Game\Volley Game` (nested inside `C:\Users\Volley Game`, which contains nothing else) |
| Remote | `origin` → `https://github.com/jbradgit/Volley-game.git` (public) |
| Default remote branch | `main` (confirmed via `origin/HEAD` and GitHub API) |
| Deployment | GitHub Pages serves `main` → https://jbradgit.github.io/Volley-game/ — **pushing to `main` IS the deploy** |
| Current branch | `claude/3d-character-sprites` @ `b98ae86` (2026-06-30), in sync with its origin counterpart |
| Local branches | `main` @ `ad6d8c3` (2026-06-25, stale), `claude/3d-character-sprites` @ `b98ae86` |
| Remote branches | `origin/main` @ `4f8f98a` (2026-06-26), `origin/claude/3d-character-sprites` @ `b98ae86` |
| Worktrees | 1 (the main checkout only) |
| Stashes | none |
| Uncommitted changes | none (clean tree) |
| Untracked files | `tools/` only — `_snap.mjs`, `_snap_classic.mjs`, `_snap_hud.mjs`, `_shots/` (10 screenshots, 2026-06-26). Rest of `tools/` (JRE, ffdec, zips) is gitignored |
| Open PRs / issues | 0 / 0 (4 historical PRs, all merged; last 2026-06-10; checked via public GitHub API — `gh` CLI is not authenticated on this machine) |
| Language / stack | Single-file vanilla JS + Canvas 2D game (`index.html`, ~250 KB). No framework, no build step, no `package.json` |
| Art pipeline | Python 3 (`artgen/*.py`, needs numpy+pillow; 3D pipeline needs `bpy`) |
| Tests / CI | Node built-ins only: `ci/smoke.js` + 4 `node --test` golden suites, wired to GitHub Actions (`.github/workflows/ci.yml`) on every push/PR |
| Dev server | `serve.py` (threaded, no-cache, localhost:**5578**), launched by `play.bat` |
| PWA | `manifest.webmanifest` + `sw.js` (network-first SW, cache `scordagol-v3`) |
| Claude tooling | `.claude/skills/menu-layout-audit/` (headless layout linter), `.claude/skills/rebake-deploy/`, `.claude/launch.json` (stale — see findings), `settings.local.json` (harmless permission allowlist). **No CLAUDE.md exists** |
| Key folders | `assets/` (runtime art/audio, 196 tracked), `artgen/` (art generators), `ci/` (tests), `docs/` (specs), `decomp/` + `ruffle/` + `gamezip/` + `original.swf` (reference workshop — IP-sensitive), `editor/` (browser dev tools), `tools/` (local scratch, untracked/ignored) |

**Adjacent-folder sweep:** `C:\Users` contains only `Admin`, `Public`, and `Volley Game`. There are **no sibling copies, clones, backups, or prototypes** of this project on the accessible workspace, and only one Git worktree. The "multiple local copies" risk is **not present** (the historical `scordagol_web/` fork was deleted in the 2026-06-20 tidy-up per ROADMAP 0.3).

---

# Git and GitHub status

## Topology (fully linear — no divergence anywhere)

```
ad6d8c3 (local main, 2026-06-25)
   └── … 4 commits … 4f8f98a (origin/main = LIVE SITE, 2026-06-26)
                        └── d618771 ── b98ae86 (HEAD = claude/3d-character-sprites = origin/…, 2026-06-30)
```

- Local `main` **is a strict ancestor** of `origin/main` (verified with `git merge-base --is-ancestor`) → a plain fast-forward fixes it; nothing can be lost.
- HEAD contains `origin/main` entirely → deploying is a fast-forward push, exactly as HANDOVER prescribes.
- **No commits exist locally that aren't on GitHub.** No remote commits are missing locally (after `git fetch --prune`).
- No detached HEAD, no merge/rebase/cherry-pick in progress, no conflict markers in tracked files, `git fsck` clean.

## Branch table

| Branch | Tip / date | Status vs upstream | Purpose (evidence) | Category | Recommendation |
|---|---|---|---|---|---|
| `claude/3d-character-sprites` (current) | `b98ae86` 2026-06-30 | In sync with origin; **2 ahead of origin/main** | 2026-06-30 session: Slick Vic agent screen, sporty logo, HUD venue chips, rainbow-kit fix, dev-server hardening, audio shortlist doc (commit messages + HANDOVER §0 agree). Name is historical — the 3D-sprite work it's named for shipped long ago | **2 — Ready to merge** (CI green + layout-audit clean per HANDOVER; awaiting owner's visual sign-off, which HANDOVER explicitly requires) | Owner eyeballs live, then `git push origin claude/3d-character-sprites:main` |
| `main` (local) | `ad6d8c3` 2026-06-25 | **4 behind** origin/main, 0 ahead | Stale local pointer to the deploy branch | **4 — Superseded pointer** (not lost work) | `git checkout main && git merge --ff-only origin/main` — zero risk |
| `origin/main` | `4f8f98a` 2026-06-26 | — (default, live) | The deployed game | **1 — Active and required** | Keep; it is the product |
| `origin/claude/3d-character-sprites` | `b98ae86` | = local | Remote backup of the work branch | **1 now → 5 after deploy** | Delete after its commits land on `main` (subject to approval) |

There are no other branches, local or remote (the old remote `claude/*` branches were deleted in the 2026-06-20 tidy-up — HANDOVER §2 records this). **No overlapping, conflicting, purposeless, or at-risk branches exist.** Branch hygiene is genuinely good.

## Work-loss check

| Item | At risk? |
|---|---|
| Committed work | No — every local commit is on GitHub |
| Uncommitted tracked changes | None exist |
| Untracked files | Only `tools/_snap*.mjs` + `tools/_shots/` (scratch snapshot scripts + screenshots from 2026-06-26). HANDOVER explicitly says don't commit `tools/` scratch. Low value; likely superseded by the tracked `.claude/skills/menu-layout-audit/audit.mjs` |
| `assets/ui/New Vic.png` | **Yes (off-repo by design)** — exists only on the original dev box; gitignored intentionally. Single-copy risk documented in HANDOVER §0.6 but no backup exists |

---

# Workspace duplication review

| Suspect | Evidence | Verdict | Canonical | Risk | Recommended action |
|---|---|---|---|---|---|
| `original.swf` (root) vs `gamezip/content/…/LiverpoolFCVolleyChallengeV32PC.swf` | **MD5 identical** (`D118A032AF2A9AB54E3A458D8510A44A`); both tracked | **Confirmed duplicate** — and both are copyrighted third-party material | Neither should ultimately remain public; `original.swf` is the one docs treat as the "sacred physics source" | High (IP) / Low (ambiguity — code only references `original.swf` via `ruffle.html`) | Fold into ROADMAP C.3 (private archive + history rewrite). If deferring C.3, drop `gamezip/` as the redundant copy — *after approval* |
| `striker_base_v01.blend` (tracked, 55.6 MB) vs `striker_base_v01.blend1` (local, 58 MB, ignored) | `.blend1` is Blender's auto-save backup; correctly gitignored (`*.blend1`) | **Intentional** — `.blend1` is a generated artefact | The `.blend` | Low (duplication) / Medium (55.6 MB tracked without LFS) | No action on `.blend1`. Decide the `.blend`'s future in C.3 (LFS, or move to the private workshop repo) |
| Two Ruffle `.wasm` (13.2 + 12.4 MB) | ROADMAP 0.3 investigated: baseline + SIMD variants of **one** 0.2.0 build, both required by the reference player | **Intentional variation** — not stale generations | Both (while `ruffle.html` is kept) | Low | Removed automatically if C.3 retires the Ruffle reference player |
| `tools/_snap*.mjs` (untracked) vs `.claude/skills/menu-layout-audit/audit.mjs` (tracked) | Same domain (headless Chrome screenshots of menus); the skill is newer, documented, and referenced by HANDOVER as *the* verification tool | **Likely superseded scratch** (unconfirmed — did not diff behaviour) | `audit.mjs` | Low | Either delete `tools/_snap*` + `_shots/` or add `tools/` wholesale to `.gitignore` — after approval |
| `docs/make_grid_template.py` + `stadium_grid_template.png` | Generator + its output, both tracked | **Required generated artefact** (the template is the documented derivation record — matches ROADMAP "derive, don't eyeball" rule) | Both | None | Keep |
| `artgen/_*` (previews, logs, ~60 items) | All matched by the `artgen/_*` gitignore rule | **Intentional local scratch** | — | None | Keep local; already ignored |
| Copies of the whole project | `C:\Users` contains no other project folders; one worktree; `scordagol_web/` fork deleted 2026-06-20 | **No duplicates exist** | This repo | None | — |

No files matching `*copy*`, `*old*`, `*backup*`, `*final*`, `*v2*` etc. exist in the tracked tree (the 2026-06-20 cleanup was effective).

---

# Conflicting information review

| # | Conflict | Files | More authoritative | Why | Safest resolution | Owner decision needed? |
|---|---|---|---|---|---|---|
| 1 | Dev port **5577 vs 5578** | `README.md` (5577) vs `serve.py`/`play.bat` (5578) + HANDOVER §0 (documents the move) | Code + HANDOVER | `serve.py:10` literally sets `PORT = 5578` with the reason in a comment | Update README's three port references | No |
| 2 | `stop.bat` kills port **5577** only — cannot stop the current 5578 server; header still says "Volley Challenge" | `stop.bat` vs `serve.py`/`play.bat` | Code | Functional breakage, not just docs | Update `stop.bat` to 5578 | No |
| 3 | `.claude/launch.json` starts `python -m http.server 5577` — stale port **and** bypasses the threaded no-cache server, re-creating the exact stale-content/starved-socket trap HANDOVER §0 warns about | `.claude/launch.json` vs `serve.py` | `serve.py` | HANDOVER: "KEEP IT THREADED" | Point launch.json at `python serve.py`, port 5578 | No |
| 4 | HANDOVER says "**Don't commit** … `striker_base_v01.blend` (pre-existing, not ours)" yet the file **is tracked** (55.6 MB); `.gitignore` comment says "the .blend itself is tracked as pipeline source" | `HANDOVER.md:87` vs `.gitignore:19` vs Git index | Ambiguous — the instruction reads as "don't re-commit changes to it", but "not ours" muddies whether it's even original IP | `.gitignore` (matches reality) | Clarify in HANDOVER; decide its long-term home (LFS / private repo) in C.3 | **Yes** — is the blend original work, and should it stay in the public repo? |
| 5 | ROADMAP A.3 says boards live in `assets/ads/`; they actually live in `assets/boards/` (renamed because ad-blockers hide "ads" paths — HANDOVER constraint #4) | `ROADMAP.md:63` vs filesystem + HANDOVER §4 | HANDOVER + filesystem | The rename rationale is a hard constraint | One-word ROADMAP fix | No |
| 6 | HANDOVER §6 document map omits `docs/AUDIO_SHORTLIST.md` (the declared NEXT task's key doc, referenced only in §0) and `docs/SPRITE_FRAME_SELECTION.md` | `HANDOVER.md` §6 | §0 (newer) | §0 explicitly supersedes older sections | Add both rows to the doc map | No |
| 7 | `index.html:2577` comment cites `assets/ui/vic_pixel.png` — the file was renamed `slick_vic.png` (the loading code at :2581 is correct) | Comment vs code | Code | Runtime verified: all 20 asset references in `index.html` resolve; this is the only stale mention and it's comment-only | Fix the comment when next editing that region | No |
| 8 | `AUDIT.md` describes a 2,310-line file, no README, no CI — all now false | `AUDIT.md` vs present state | Present state | AUDIT.md **self-declares** it is a point-in-time record ("do not read this document as current state") | None needed — correctly labelled historical | No |
| 9 | README repo-map row says HANDOVER is where "full details" live; ROADMAP 0.4 leaves open whether to demote HANDOVER to historical | `README.md` vs `ROADMAP.md` D-item in 0.4 | Current practice (HANDOVER is actively maintained, updated 2026-06-30) | Every session updates it; it self-describes as "single source of truth" | Record the decision: HANDOVER **is** the living dev doc | Already de-facto decided; confirm in ROADMAP 0.4 |

**Documentation authority chain (as practised and mostly as written):** `HANDOVER.md §0` (current state, supersedes its own older sections) → `README.md` (public-facing how-to) → `ROADMAP.md` (plan + decision log) → `AUDIT.md` (frozen historical record) → `docs/*` (binding technical specs).

---

# Build and validation results

All run 2026-07-01 on the working tree at `b98ae86`. **Everything passes.**

| Check | Command | Result |
|---|---|---|
| Smoke test (full game headless: physics, goal, 2 career seasons, renders, kit build) | `node ci/smoke.js` | ✅ **SMOKE PASS**, exit 0 |
| Golden regression suites (physics, career, HORSE, leagues) | `node --test ci/physics.test.js ci/career.test.js ci/horse.test.js ci/leagues.test.js` | ✅ **28/28 pass**, 0 fail, ~11.5 s |
| Git object integrity | `git fsck --no-dangling` | ✅ Clean |
| Repo size | `git count-objects -vH` | ⚠️ 137.75 MiB packed (finding 4) |
| Asset references | Regex-extracted all `assets/…` paths from `index.html` (20 unique) and stat-checked each | ✅ All exist (only stale mention is a comment) |
| Secrets scan | Pattern grep (api key / secret / token / password / bearer) across tracked source | ✅ No hits |
| GitHub state | Public API (`gh` unauthenticated) | ✅ 0 open PRs, 0 open issues; CI runs on push/PR |
| Dependency integrity | N/A — no `package.json`/lockfile exists by design; CI uses Node built-ins only; `node_modules/` (puppeteer-core, ignored) is a documented per-session `--no-save` install | ✅ Consistent with docs |

Not run: `.claude/skills/menu-layout-audit/audit.mjs` (needs a live server + system Chrome; HANDOVER records this branch already passed it on 2026-06-30) and the `artgen` Python pipeline (generators, not validators; would write files).

---

# Risks

| # | Risk | Severity | Confidence |
|---|---|---|---|
| R1 | **IP/legal exposure**: public repo + live site distribute the original SWF (×2), full decompilation, ripped SFX, real PL club names — while the stated goal is monetisation. History rewrite (C.3) gets more expensive with every commit | **Critical** (relative to the publication goal; no *technical* breakage) | Confirmed |
| R2 | `assets/ui/New Vic.png` single copy on one machine, no backup | **High** | Confirmed (documented in HANDOVER; the file's absence here verified) |
| R3 | Undeployed reviewed work: live site lags the CI-green branch by 2 commits; the longer it waits, the higher the chance a new session forks from the wrong base | **Medium** | Confirmed |
| R4 | 137 MB repo, 55.6 MB blend + 25.8 MB wasm tracked without LFS; slow clones (ephemeral dev containers re-clone every session per HANDOVER §2) | **Medium** | Confirmed |
| R5 | Stale port configs (`stop.bat` non-functional, `launch.json` re-creates a debugged failure mode, README misleads) | **Medium** | Confirmed |
| R6 | Local `main` 4 behind — a session that builds/deploys from local `main` without fetching ships stale code | **Medium** | Confirmed |
| R7 | No `.gitattributes` with `core.autocrlf=true` and mixed Windows/Linux-container development — line-ending churn risk on any new machine with different config | **Low** | Confirmed config; churn is hypothetical |
| R8 | Untracked `tools/_snap*.mjs` scratch overlaps the tracked layout-audit skill — a future session might "fix" the wrong tool | **Low** | Likely (behavioural overlap not diffed) |
| R9 | Doc-map omissions and stale comments (conflicts 6, 7) cause minor session-startup confusion | **Low** | Confirmed |
| R10 | No CLAUDE.md — session guidance lives in HANDOVER.md, which works but relies on sessions knowing to read it (README does say "start here") | **Low** | Confirmed |

---

# Recommended cleanup plan

**Nothing below has been done. All items await your approval.**

### 1. Safe actions — no product behaviour change, no history risk
1. Fast-forward local `main`: `git checkout main && git merge --ff-only origin/main && git checkout claude/3d-character-sprites` (R6).
2. Fix the three port-5577 stragglers: `README.md`, `stop.bat`, `.claude/launch.json` (→ `python serve.py`, 5578) (R5).
3. HANDOVER §6 doc map: add `AUDIO_SHORTLIST.md` and `SPRITE_FRAME_SELECTION.md`; ROADMAP A.3: `assets/ads/` → `assets/boards/` (R9).
4. Add a `.gitattributes` (e.g. `* text=auto` + explicit binary entries for png/jpg/mp3/swf/wasm/blend) (R7).
5. Back up `New Vic.png` from the original dev box to any second location (cloud drive / a private repo) (R2). *Needs the owner — the file isn't on this machine.*

### 2. Actions requiring review
6. Deploy the work branch: owner eyeballs https://jbradgit.github.io/Volley-game/ vs the branch locally (logo, Slick Vic, HUD venue chips, agent flow — HANDOVER's own checklist), then `git push origin claude/3d-character-sprites:main` (R3).
7. Resolve the `tools/_snap*` overlap: confirm the layout-audit skill covers what the snap scripts did, then delete them or ignore `tools/` wholesale (R8).
8. Fix the `vic_pixel.png` comment at `index.html:2577` next time that region is edited (bundle with other work — don't burn a deploy on a comment).

### 3. Actions requiring a product decision
9. **Schedule ROADMAP C.3** (the workshop split + `git filter-repo` history rewrite). Decide: what still needs `decomp/` as reference (ROADMAP D5)? Does `original.swf` stay in the private repo only? This simultaneously resolves R1 and most of R4. Single-contributor repos are cheap to rewrite **now**; painful later.
10. Decide `striker_base_v01.blend`'s status (conflict 4): original work or not? Keep public (LFS), or move to the private workshop repo in C.3?
11. Club rebrand timing (ROADMAP D2) — real PL names are part of R1.

### 4. Do not do until a backup/branch exists
- The C.3 history rewrite itself (`git filter-repo` + force-push): take a full mirror clone (`git clone --mirror`) to offline storage **first**, and only run it after Tracks A/B no longer need `decomp/`.
- Any deletion of `decomp/`, `ruffle/`, `gamezip/`, or `original.swf` from the working tree — `original.swf` is the sacred-physics reference (HANDOVER constraint #1).

---

# Proposed branch strategy

The current de-facto model is sound for a solo project with Pages-deploys-main. Formalise it as:

- **`main`** — deployable, protected by convention: nothing lands without `node ci/smoke.js` + the 4 golden suites passing (CI enforces this on push anyway). Landing on `main` = deploy.
- **One short-lived feature branch at a time**: `claude/<topic>` for AI-session work, `feat/<topic>` / `fix/<topic>` if the owner works directly. Rebase/branch **from freshly fetched `origin/main`**, keep linear, land via `--ff-only` merge or `push branch:main`, then **delete the branch (local + remote) immediately after landing** — the current branch's stale name ("3d-character-sprites" carrying audio-shortlist work) shows why long-lived session branches drift from their names.
- **Experiments**: `exp/<topic>`, never pushed to `main`, deleted or promoted within days.
- **Releases**: when publication nears, tag `main` (`v0.x`) at each deploy so any live regression can be bisected; Pages keeps serving `main` tip.
- **Rule carried over from ROADMAP**: no long-running parallel feature branches — the game is one 3,000-line file; two concurrent branches editing `index.html` will conflict on nearly every change.

---

# Source-of-truth rules

| Domain | Canonical source | Notes |
|---|---|---|
| Current state / how to work | **`HANDOVER.md` §0** | Self-declared and de-facto SoT; supersedes its own older sections and all other docs on current state |
| Product plan + open decisions | `ROADMAP.md` (incl. its Decision log) | |
| Game rules / physics | **The code**: `logicStep()`, `savedCheck()`, constants block in `index.html` — protected by `ci/` goldens | "Sacred" (HANDOVER constraint #1). `original.swf` is the historical reference, not an editable source |
| Sprite/recolour contract | `docs/SPRITE_SPEC.md` | Binding on engine + all generators |
| Stadium geometry | `docs/STADIUM_ASSET_SPEC.md` + `docs/stadium_grid_template.png` | |
| Career design | `docs/CAREER_DESIGN.md` | |
| Art sourcing / 3D pipeline | `docs/ART_SOURCING.md`; pipeline source `artgen/render_sprites.py`; model source `striker_base_v01.blend` | |
| Visual assets (shipped) | `assets/**` — **generated** by `artgen/*.py`; generators are the source, PNGs are artefacts (except traced placeholders and `slick_vic.png`, whose trace source `New Vic.png` is off-repo — see R2) | |
| Teams/kits data | `assets/teams.json` + `assets/world/world.json` (written by `artgen/gen_kits.py`) | Slugs double as asset filename keys — rename together (ROADMAP C.1) |
| Build/deploy process | `HANDOVER.md` §2 + `.github/workflows/ci.yml` | No build step exists; deploy = push to `main` |
| Dependencies | None declared, by design; `pip install numpy pillow [bpy]` + `npm install puppeteer-core --no-save` per HANDOVER §2 | |
| Dev server config | `serve.py` (port, threading, no-cache) | Everything else (README, stop.bat, launch.json) must follow it |
| AI-session instructions | `HANDOVER.md` (+ `.claude/skills/*`) | No CLAUDE.md; consider a one-liner CLAUDE.md pointing at HANDOVER.md so tooling auto-loads it |
| Historical record | `AUDIT.md` (frozen), superseded HANDOVER sections | Never treat as current |

---

# Next 10 actions

1. ☐ Owner: eyeball the work branch (locally via `play.bat`, checklist in HANDOVER §0) → approve deploy.
2. ☐ Deploy: `git push origin claude/3d-character-sprites:main`; verify Pages refresh; then delete the `claude/3d-character-sprites` branch (remote + local) per the branch strategy.
3. ☐ Fast-forward local `main` (safe action 1).
4. ☐ Fix the three port-5577 configs + doc-map/ROADMAP one-liners (safe actions 2–3) in one small commit.
5. ☐ Owner: back up `New Vic.png` off the original dev box (R2).
6. ☐ Add `.gitattributes` (safe action 4).
7. ☐ Answer ROADMAP D5 (what still needs `decomp/`?) — this gates C.3.
8. ☐ Decide `striker_base_v01.blend` provenance/home (cleanup item 10).
9. ☐ Take a `--mirror` backup clone, then execute C.3: private workshop repo + `git filter-repo` on the public history (removes SWFs, `decomp/`, `ruffle/`, `gamezip/`; shrinks clone to well under 40 MB — ROADMAP Phase 0 exit criterion).
10. ☐ Proceed with the documented next feature task: audio replacement (`docs/AUDIO_SHORTLIST.md` — owner auditions, session swaps the 6 SFX + menu track), which also clears part of R1.

---

# Evidence appendix

- **Repo/remote**: `git remote -v` → `origin https://github.com/jbradgit/Volley-game.git`; `origin/HEAD → origin/main`; GitHub API: `"default_branch": "main"`, `"private": false`, `"open_issues_count": 0`, `"pushed_at": "2026-06-30T07:19:55Z"`, `"size": 136965` (KB).
- **Branches** (`git branch -vv --all`, post-fetch): `claude/3d-character-sprites b98ae86 [origin/… ]` (in sync); `main ad6d8c3 [origin/main: behind 4]`. `git merge-base --is-ancestor main origin/main` → true. `origin/main..HEAD` = `d618771`, `b98ae86` (both 2026-06-30). `main..origin/main` = `5df880b`, `8062200`, `133b1cc`, `4f8f98a` (all 2026-06-26).
- **Worktrees/stash**: `git worktree list` → 1 entry; `git stash list` → empty.
- **Integrity/size**: `git fsck --no-dangling` → no output; `git count-objects -vH` → `size-pack: 137.75 MiB`, `garbage: 0`.
- **Tracked large files** (>1 MB, live sizes): `striker_base_v01.blend` 55.6 MB; `decomp/swf.xml` 13.6 MB; `ruffle/*.wasm` 13.2 + 12.4 MB; `decomp/bg/202.png` 4.6 MB; `assets/sprites/striker_sheet.png` 1.3 MB; `assets/stadium/backdrop.png` 1.2 MB; `assets/sprites/keeper_atlas.png` 1.2 MB.
- **Tracked-file counts by top-level path**: decomp 1238 · assets 196 · artgen 16 · ruffle 9 · docs 8 · editor 6 · ci 6 · .claude 5 · gamezip 2 · root files 16.
- **SWF duplicate**: `Get-FileHash -Algorithm MD5` → `original.swf` = `gamezip/content/www.extremegamezone.com/games/LiverpoolFCVolleyChallengeV32PC.swf` = `D118A032AF2A9AB54E3A458D8510A44A` (503,998 bytes each).
- **Untracked** (`git status --porcelain --ignored`): `?? tools/` (untracked members: `_snap.mjs` 5.8 KB, `_snap_classic.mjs`, `_snap_hud.mjs`, `_shots/` ×10 PNGs, all dated 2026-06-26); ignored: `tools/jre|ffdec|*.zip`, `artgen/_*` (~60 items), `artgen/__pycache__`, `node_modules/`, `striker_base_v01.blend1`.
- **Ports**: `serve.py:10` `PORT = 5578`; `play.bat:12,14` `:5578`; `stop.bat:5` `:5577`; `README.md:22,27,29` `5577`; `.claude/launch.json` `["‑m","http.server","5577"]`.
- **Validation**: `node ci/smoke.js` → `SMOKE PASS`, exit 0 (menu render, forced shot, goal score 4000, 30-frame render, timing sweep, 49- and 51-match seasons, kit build). `node --test` (4 suites) → `tests 28 · pass 28 · fail 0`, 11,484 ms.
- **Asset refs**: 20 unique `assets/…` paths extracted from `index.html`; all exist on disk. Sole stale mention: comment `index.html:2577` (`vic_pixel.png`); loader at `:2581` uses `slick_vic.png?v=5`.
- **PRs** (GitHub public API): 4 total, all merged/closed; newest PR #4 "Fix secondary-colour pick, table column order, bigger result animations", merged 2026-06-10. `gh` CLI installed (v2.95.0) but **not authenticated** on this machine.
- **Secrets**: case-insensitive grep for `api[_-]?key|secret|token|password|Bearer` `[:=]` across tracked html/js/py/json/md/bat → 0 hits.
- **Line endings**: `git config core.autocrlf` → `true`; no `.gitattributes` present.
- **TODO markers**: 0 TODO/FIXME/HACK/XXX in `index.html`.
- **Adjacent folders**: `C:\Users` → `Admin`, `Public`, `Volley Game` only; `C:\Users\Volley Game` contains only the repo folder.
- **Commands with side effects run during audit**: `git fetch --prune` (remote-tracking refs only). Report file `PROJECT_HEALTH_AUDIT.md` created (did not previously exist; verified against root listing).

---

# Addendum (2026-07-01/02) — owner-reported in-match stutter: investigated, root cause found

**Report:** owner tested `play.bat` (this branch) and saw lag in matches — "stuttering striker and ball".

**Method:** instrumented frame-time probes (rAF gap recorder + PerformanceObserver long-task capture) driving a real career match via the `?cap=1` `__dbg` harness in headless *and* headed (real-GPU) Chrome on the same machine, run against **both** this branch's `index.html` and the deployed `origin/main` version served from the same working tree.

**Results (both versions, within noise of each other):**
- Menu idle and live match play: zero frames over 60 ms, zero long tasks — no code-side stutter exists in either version.
- One reproducible ~195–235 ms main-thread stall exactly at match entry in **both** versions — the `loadKits()`/`buildKit()` kit bake. Pre-existing, minor, not the reported symptom.
- **Root cause of the perceived stutter: the machine's display.** The 4K LG monitor is running at **3840×2160 @ 29 Hz** over HDMI (`Win32_VideoController CurrentRefreshRate = 29`; connection type HDMI). At ~30 Hz refresh, the 28 Hz game (and everything else on screen) visibly judders — the 28-vs-30 beat makes sprites double-step about twice a second. The monitor's EDID advertises support for **3840×2160 @ 60 Hz** (`WmiMonitorListedSupportedSourceModes`), so the limit is the HDMI link (4K@30 cable/port), not the monitor.

**Conclusion:** not a regression; the work branch is performance-identical to live. Deploy remains gated only on the owner's visual sign-off. Remedies (owner action): connect via DisplayPort or an HDMI 2.0-capable port/cable for 4K@60, or set Windows display to 1920×1080 @ 60 Hz. Optional future code hardening (not required): extend the ball's render interpolation to striker/defender/keeper, and move the ~220 ms kit bake off the match-entry frame (pre-bake during the preceding screen).

**Session changes applied after the audit (owner approved "follow your lead"):** port-5577 stragglers fixed (`stop.bat` → 5578 + SCORDAGOL name, `README.md` → 5578, `.claude/launch.json` → `serve.py`/5578), stale `vic_pixel.png` comment fixed (`index.html:2577`), HANDOVER doc-map rows + display-gotcha added, ROADMAP A.3 path corrected to `assets/boards/` + `boards.json`, `.gitattributes` added. No game logic touched; full CI suite run before commit.
