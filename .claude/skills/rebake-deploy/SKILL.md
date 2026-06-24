---
name: rebake-deploy
description: Re-bake the 3D character sprites (Blender 5.1), bump cache tags, run the FULL CI gate, and deploy SCORDAGOL to GitHub Pages. Use whenever sprite art (striker/defender/keeper) or kit/encode logic changes and needs to go live, or for a normal index.html-only deploy.
---

# Re-bake & deploy runbook (SCORDAGOL)

A repeatable pipeline for the most common loop in this project: change art/encode → re-bake →
verify → deploy. Follow the steps in order; the gotchas are hard-won.

## 0. Preconditions
- Blender 5.1: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`
- FBX sources in `artgen/source3d/` (gitignored, ~520MB). System python has numpy+Pillow.
- Work on branch `claude/3d-character-sprites`. `main` is what GitHub Pages serves.

## 1. Re-bake (only the characters that changed)
Run from the repo root. Each takes a few minutes (keeper longest). Run in the background.
```
BL="/c/Program Files/Blender Foundation/Blender 5.1/blender.exe"
"$BL" -b -P artgen/render_sprites.py -- strikersheet "artgen/source3d/Striker Idle.fbx" "artgen/source3d/Striker Shot.fbx"
"$BL" -b -P artgen/render_sprites.py -- defendersheet "artgen/source3d/Goalkeeper Miss.fbx"
"$BL" -b -P artgen/render_sprites.py -- keeper "artgen/source3d/Goalkeeper Catch.fbx" "artgen/source3d/Goalkeeper Diving Save.fbx"
# ball (rarely): -- ball
```
- **Keeper save extents are BINDING** (docs/SPRITE_SPEC.md §2). The keeper bake prints idle/dv99/
  dv50/high354 vs targets — they must stay within a few px (dv99 reach x1 ≈ 178). The save is a
  pixel hit-test on the keeper alpha silhouette.
- Geometry/camera don't change with lighting/shading tweaks, so positions/extents stay stable.

## 2. Verify the look OFFLINE (the live preview server is unreliable on this device — it dies)
Recolour with the faithful buildKit ports and READ the PNGs (don't trust the browser preview):
```
python artgen/_kit_showcase.py     # all 20 Prem kits on the striker -> artgen/_artstyle/kit_showcase.png
python artgen/preview_kits.py      # committed validator (mixed strikers/defenders/keeper)
```
These mirror index.html `buildKit()` EXACTLY (skin-as-region format: alpha 255=kit/254=detail;
kit pixel R=shade, G=u, B=(regionId<<5)|v5). If they look right, the engine will match.

## 3. Bump the cache tags in index.html (ALWAYS, after any re-bake)
Four spots — bump the `?v=mNN` for each re-baked asset:
- `katlas:"assets/sprites/keeper_atlas.png?v=mNN"`
- `strikersheet:"assets/sprites/striker_sheet.png?v=mNN"`
- `defbase:"assets/sprites/defender_sheet.png?v=mNN"`
- `fetch("assets/sprites/keeper_atlas.json?v=mNN")`

## 4. Run the FULL CI gate (NOT just smoke) — this is exactly what .github/workflows/ci.yml runs
```
node ci/smoke.js                                                              # must print SMOKE PASS
node --test ci/physics.test.js ci/career.test.js ci/horse.test.js ci/leagues.test.js   # all must pass
```
**Do not push until BOTH are green.** Running only a subset (e.g. smoke+leagues) once let
`physics.test.js` go red on every push and spammed the owner CI-failure emails. If a physics
constant changed (KICK_FRAMES, anything in logicStep/savedCheck), expect physics.test.js golden
values/timings to need updating — fix them, re-run, then push.

## 5. Commit & deploy (no local branch-switch; never commit striker_base_v01.blend)
```
git add index.html artgen/render_sprites.py assets/sprites/*.png   # + any test/json you changed
# DO NOT `git add striker_base_v01.blend` — it carries unrelated local WIP. Leave it unstaged.
git commit -m "..."                                  # end with the Co-Authored-By line
git fetch origin
git push origin claude/3d-character-sprites          # feature branch
git push origin claude/3d-character-sprites:main     # fast-forward main = the deploy
git branch -f main origin/main
```

## 6. Verify live (Pages rebuilds ~1-3 min; the repo is PUBLIC so the API needs no auth)
```
U=https://jbradgit.github.io/Volley-game
curl -s "$U/index.html" | grep -c "v=mNN"            # new tags present on the live HTML
curl -s "https://api.github.com/repos/jbradgit/Volley-game/actions/runs?per_page=3"   # CI conclusion=success
```
The owner plays at that URL (web + installable PWA). Hard-refresh / `?new=N` on mobile.

## Notes
- Sprite tag contract: keep REGION_ID (render_sprites.py) and KREGION (index.html) in sync, and
  keep `artgen/preview_kits.py` mirroring `buildKit()`.
- `gh` is NOT installed here; use git over https (creds cached) and the GitHub REST API via curl.
