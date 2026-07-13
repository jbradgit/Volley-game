# IP history purge — ROADMAP C.3 (2026-07-13)

On **2026-07-13** this repository's Git **history** was rewritten with
`git-filter-repo` (v2.47.0) to permanently remove the original 2007 Flash game and
all decompiled / "workshop" material used as reference during the early 1:1 remake.

The **working tree** was already cleaned on 2026-07-02 (the "workshop purge"). That
left the material live in every *historical* commit — still downloadable from the
public repo. This step removed it from history too, so it is no longer retrievable.

> **⚠️ Every commit hash changed.** Old `main` tip was `3384444`; the rewrite replaced
> the whole history. **Any other clone (office box, original dev box) is now stale.**
> On those machines: **re-clone, or `git fetch origin && git reset --hard origin/main`.**
> **Do NOT merge an old clone back in** — that would drag the removed material back.

## What was removed (from ALL history)

**Directories (removed in full):**
| Path | What it was |
|------|-------------|
| `decomp/` | Decompiled SWF export — images, sprites, sounds, `swf.xml`, build scripts |
| `ruffle/` | Bundled Ruffle Flash player (`.wasm` / `.js`) |
| `gamezip/` | Packaged original game, incl. `LiverpoolFCVolleyChallengeV32PC.swf` |
| `scordagol_web/` | An early full web export (per-club traced kit art for the whole league) |

**Single files (removed):**
- `original.swf` — the original 2007 Flash game itself
- `game2.zip` — a zip of the original game
- `ruffle.html` — Ruffle player host page
- `ref_gameplay.png`, `ref_logo.png` — reference screenshots of the original
- `Gemini_Generated_Image_ivxfmlivxfmlivxf.png`
- `page_flashmuseum.html`, `page_flashstorage.html`, `page_mygamesworld.html` — saved host pages

## What was deliberately KEPT (and why)

- **`docs/original_mechanics/`** — the decompiled ActionScript **mechanics reference**.
  Owner-approved keep (2026-07-02): text-only game logic, no art or binaries.
- **`assets/*_Liverpool*.png`** + **`editor/striker_Liverpool_k0_regions.json`** — these are
  **live, current game assets**, so they were left untouched (removing them would change the
  deployed game). Retiring a real club name/art is the **separate "club-name rebrand" IP step**
  — it needs new fictional names, regenerated art, and code changes, then a later history sweep.
- **`striker_base_v01.blend`** (55 MB) — the 3D-pipeline base model; provenance unconfirmed.
  Its removal is a separate owner decision (see `PROJECT_HEALTH_AUDIT.md`).

## Verification performed before the force-push

- **Deployed content byte-identical:** the file tree at the tip commit was *unchanged* by the
  rewrite (tree object `642c2fba84d6eb52de189b8f25ee41fc861de836` — identical before and after),
  so the live game did not change at all.
- **No Flash IP remains:** an exhaustive per-commit scan (every path in every commit tree) found
  zero `.swf` / `.fla` / `.zip` / `.wasm` and no `ruffle` / `decomp` / `gamezip` / `scordagol_web`
  path in any commit. Distinct paths across history dropped 1846 → 417.
- **CI green:** `SMOKE PASS` + 54/54 tests on the rewritten repo.
- **Size:** pack 138.10 MiB → ~105 MiB. (Not "< 40 MB" — the 55 MB `.blend` plus ~30 MB of
  legitimate 3D-sprite iteration history remain; both are separate, out-of-scope decisions.)

A mirror backup of the pre-rewrite history was taken first (kept off-repo, locally).

## Still open on the IP track (unchanged by this step)

Club-name rebrand (real names/art → original), self-host the SIL-OFL fonts, replace the 6
SWF-decompiled SFX (`docs/AUDIO_SHORTLIST.md`), and — if the owner decides — drop the 55 MB
`.blend`. See `ROADMAP.md` Track C.
