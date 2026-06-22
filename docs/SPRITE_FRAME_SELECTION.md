# Sprite Frame Selection — owner's manual picks

The 3D pipeline renders a *labelled contact sheet* of every clip (each frame shot
from that character's in-game camera). The owner reads off the frame numbers to
keep per action; those numbers become the constants in `artgen/render_sprites.py`,
then the real bake runs. **This file is the record of those picks** so nothing is
re-guessed. Contact sheets live in `artgen/_contact/` (scratch, not shipped).

Cameras: striker az190/el12 (over-shoulder) · defender az0/el8 (front) · keeper az0 (front).

## Striker
| Action | Source clip | Frames | Contact | Notes |
|---|---|---|---|---|
| Volley / kick | `Striker Shot.fbx` (40f) | **f01–f15** | **f13** | full kick sequence; grounded (drops the airborne f16+ leap) |
| Idle / stand | `Striker Idle.fbx` | **f01** | — | neutral centred stand |

## Defender
Pose borrowed from a **goalkeeper** clip (more natural defensive stance) but rendered
as an outfield player (`keeper=False` regions — normal sleeves, no gloves). Front cam az0/el8.
GK Idle rejected (too static); the **Miss** clip's upright arms-at-sides set reads as outfield.
| Action | Source clip | Frames | Notes |
|---|---|---|---|
| Stance variants | `Goalkeeper Miss.fbx` | **f05, f06, f07, f08** | 4-pose pool. **ENGINE:** 3 defenders/match, assign 3 *distinct* from the pool at random — never two defenders the same pose. |

## Keeper
GK Idle rejected for the idle too; the **Catch** clip's coiled set is a better keeper-ready.
Engine only uses 6 states (`KEEPER_ANIMS`): idle, dive_left[50-99], dive_right[100-149],
low_catch[323], mid_catch[328], high_catch[354]. **Body Block & Sidestep are NOT used** —
ignore them (and the broken Sidestep FBX doesn't matter).
| Engine state (atlas frames) | Source clip | Frames | Notes |
|---|---|---|---|
| idle [1] | `Goalkeeper Catch.fbx` | **f06** | coiled athletic keeper-ready |
| dive_left [50–99] | `Goalkeeper Diving Save.fbx` | **f07–f57** → resample to 50 | full-extension must hit SPRITE_SPEC §2 save extents |
| dive_right [100–149] | **H-mirror of dive_left** | (auto) | symmetric reach both sides |
| low_catch [323] | `Goalkeeper Catch Low.fbx` | **f19** | low gather, hands near ground |
| mid_catch [328] | `Goalkeeper Catch.fbx` | **f13** | hands at chest |
| high_catch [354] | `Goalkeeper Catch High.fbx` | **f28** | full overhead reach |

**Held ball (caught):** already engine-native — on a central catch the ball freezes "in his
hands" (index.html `held`), pose picked by height. The 3 height-matched poses above make it
sit right; fine-tune the ball's resting offset per pose visually after the bake.
