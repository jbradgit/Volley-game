# Character Art Sourcing — Decision & Pipeline

*Problem: we need ORIGINAL, realistic-form, smoothly-animated football sprites with
clean recolourable regions. Hand-drawing procedurally hit its ceiling (v1/v2);
tracing the originals gave perfect form/motion but is derivative. This doc records
the researched options and the chosen path.*

## Options assessed (June 2026)

### A. Existing 2D sprite archives / packs
- [chasersgaming Football/Soccer pack](https://chasersgaming.itch.io/asset-pack-football-soccer) — **CC0**, ~£2,
  includes run/slide/kick/celebration. BUT: tiny retro top-down sprites — wrong
  perspective and ~10× too small for our 131×191 behind-the-striker view.
- [itch.io soccer-tagged assets](https://itch.io/game-assets/tag-soccer) /
  [football](https://itch.io/game-assets/tag-football) — same story across the board:
  football packs are top-down match-game sprites. **No pack found at our sprite size
  / camera angle.** Verdict: great for icons/extras, not for our cast.

### B. 3D pre-rendered sprites ← **CHOSEN**
The professional-era technique (pre-rendered sprite games) and a perfect fit:
- **Realistic form & smooth motion for free** — real rigged humans + real animation
  data; we can render 10–15 frames per action instead of the original's 6.
- **Regions for free** — assign flat TAG materials to body regions in 3D (by bone
  weights, works on any humanoid), render orthographically → frames come out
  pre-segmented; they feed straight into the existing encoder
  (`trace_sprites.py` machinery) and the engine's recolour/pattern system **unchanged**.
- **One style for everyone** — striker, defender, keeper from the same model +
  camera = the style unification we're missing.
- **FEASIBILITY PROVEN in-repo**: `pip install bpy` (Blender 5.0.1) works in the
  dev environment; a rigged glTF was imported, flat-shaded and rendered headless
  (Cycles CPU, ~1s/frame at 262×382). GitHub model downloads work.

**Animation/character sources (licence-verified):**
1. **Mixamo (Adobe)** — free, royalty-free for commercial games, no attribution;
   only restriction is redistributing raw assets standalone
   ([Adobe FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html),
   [licensing thread](https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/td-p/13234775)).
   Has FOOTBALL-SPECIFIC clips (soccer idle/pass/strike, goalkeeper saves).
   Needs a free account + interactive download → **the one human step** (see list below).
2. **Quaternius Universal Animation Library** — **CC0**, 120+ humanoid animations,
   retargetable ([site](https://quaternius.com/packs/universalanimationlibrary.html),
   [itch](https://quaternius.itch.io/universal-animation-library)). Direct download —
   usable without any account; generic kick rather than a true soccer strike.
   **Fallback if Mixamo step stalls.**

### C. New mechanical system (runtime skeletal animation)
Tween bones in-engine (Rayman-style). Infinitely smooth + trivially recolourable,
BUT the quality problem just moves to the part art, and it risks the sacred
kick-timing feel. Rejected as primary; note that the 3D pipeline gives us the same
smoothness benefit at render time with zero engine risk.

## The pipeline (artgen/render_sprites.py — to build next)

```
character.fbx + clips (Mixamo/CC0)          [user or CC0 fetch]
  └─ bpy: retarget clip → assign TAG materials by bone-weight region
       (head→hair/skin · spine→shirt · upper-arms→sleeve · forearms/hands→skin
        hips/upper-legs→shorts · calves→socks · feet→boots)
  └─ TWO passes per frame: flat tag pass + grayscale-lit pass (→ shade channel)
  └─ orthographic camera matched to game view (behind/high for striker,
       front for defender/keeper), framed to the exact sprite boxes in SPRITE_SPEC
  └─ existing encoder: tags + shade + per-part UV  →  assets/sprites/*
  └─ engine unchanged (one small tweak: more kick frames, same contact timing)
```

## The one human task — Mixamo shopping list

Create a free account at mixamo.com, pick ONE character (any athletic male,
e.g. "Brian"), then download these (format: **FBX Binary · With Skin · 30 fps ·
no keyframe reduction**) into `artgen/source3d/`:

| Search on Mixamo | For |
|---|---|
| Soccer Idle | striker idle (k0) |
| Soccer Pass *or* Strike / Penalty Kick (pick the best-looking side volley) | the kick (k1–k5+) |
| Goalkeeper Idle | keeper frame 1 |
| Goalkeeper Diving Save (a left or right dive) | dive_left/right (we mirror) |
| Goalkeeper Catch / overhead catch if available | the 3 catch poses |
| Standing Idle (alert/defensive) | defender |
| Victory (optional) | goal celebration (future) |

Commit them (they're embedded game inputs, not redistributed standalone — within
the licence) or hand them over any other way. Everything after that is automated.

## Status of current art
The traced striker/defender stay live as the best-playing placeholder; the
procedural keeper stays until the pipeline replaces all three in one style.
Both are superseded the moment the 3D renders land. Keeper save-extent targets in
SPRITE_SPEC §2 still bind the new renders.
