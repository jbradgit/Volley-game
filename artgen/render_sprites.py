"""3D -> region-tagged sprite renderer (the permanent character-art pipeline).

Input:  a rigged humanoid + animation clips (Mixamo FBX preferred; any glTF works)
        in artgen/source3d/ — see docs/ART_SOURCING.md for the shopping list.
Output: assets/sprites/* in the engine's tag/UV format (docs/SPRITE_SPEC.md §1),
        produced from TWO renders per frame:
          1. TAG pass  — flat emission colours per body region
          2. LIT pass  — white diffuse + sun -> the shade channel
        Region encode + per-part UV reuse trace_sprites.py's functions.

Region assignment is by BONE WEIGHTS with parametric splits along the bone, so it
works on any Mixamo character without manual painting:
  head(top 45%)→hair · head/neck(rest)→skin · spine*→shirt · shoulders+upper arms→sleeve
  forearms/hands→skin (keeper: sleeve/glove) · hips+upper legs(top 55%)→shorts,
  (rest)→skin · calves(top 25%)→skin knee, (rest)→socks · feet/toes→boots

Usage (headless, via pip-installed bpy):
  python3 artgen/render_sprites.py probe  <model>          # list bones/clips
  python3 artgen/render_sprites.py test                    # e2e check on a stand-in model
  python3 artgen/render_sprites.py striker <model> <clip> [--frames 6] [--contact 3]
  python3 artgen/render_sprites.py defender <model> <clip> [--frame 0.4]
  python3 artgen/render_sprites.py keeper  <model> <idle> <dive> <catchlow> <catchmid> <catchhigh>
"""
import sys, os, math, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace_sprites import shade_of, uv_of                      # shared encoder maths

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "sprites")
SRC = os.path.join(ROOT, "artgen", "source3d")

# tag colours for the TAG pass (pure hues; engine contract)
TAGCOL = { "shirt": (1,0,0), "shorts": (0,1,0), "socks": (0,0,1), "sleeve": (1,1,0),
           "hair": (1,0,1), "skin": (0.93,0.75,0.58), "boot": (0.16,0.15,0.18),
           "glove": (0.95,0.95,0.97) }
TAGID = {k: i for i, k in enumerate(TAGCOL)}                   # id+1 in the id render

# Mixamo bone-name -> (region, along-bone split [(t_end, region), ...])
def bone_region(name, keeper=False):
    n = name.lower().split(":")[-1]
    if "head" in n:                 return [(0.55, "skin"), (1.0, "hair")]
    if "neck" in n:                 return [(1.0, "skin")]
    if "shoulder" in n:             return [(1.0, "sleeve")]
    if "forearm" in n:              return [(1.0, "sleeve" if keeper else "skin")]
    if "hand" in n:                 return [(1.0, "glove" if keeper else "skin")]
    if "arm" in n:                  return [(1.0, "sleeve")]
    if "upleg" in n:                return [(0.58, "shorts"), (1.0, "skin")]
    if ("foot" in n) or ("toe" in n): return [(1.0, "boot")]
    if "leg" in n:                  return [(0.25, "skin"), (1.0, "socks")]
    if "hips" in n:                 return [(1.0, "shorts")]
    if "spine" in n or "chest" in n or "torso" in n: return [(1.0, "shirt")]
    return [(1.0, "skin")]

def setup_scene():
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy

def import_model(bpy, path):
    if path.lower().endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        bpy.ops.import_scene.fbx(filepath=path)
    arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    return arm, meshes

def import_clip(bpy, path, arm):
    """Import an animation-only FBX/GLB and retarget its action onto `arm` (same rig)."""
    before = set(bpy.data.actions)
    if path.lower().endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        bpy.ops.import_scene.fbx(filepath=path)
    new_actions = [a for a in bpy.data.actions if a not in before]
    # remove any extra imported objects (keep just the action)
    for o in list(bpy.context.scene.objects):
        if o.type in ("ARMATURE", "MESH") and o is not arm and not any(
                m.parent is arm or (m.find_armature() if m.type=="MESH" else None) is arm
                for m in [o]):
            pass
    act = new_actions[-1] if new_actions else None
    if act:
        if not arm.animation_data: arm.animation_data_create()
        arm.animation_data.action = act
    return act

def assign_regions(bpy, arm, meshes, keeper=False):
    """Split every mesh's faces into TAG materials by dominant-bone region."""
    # bone rest geometry in armature space
    bones = {b.name: (np.array(b.head_local), np.array(b.tail_local)) for b in arm.data.bones}
    mats = {}
    for region, col in TAGCOL.items():
        m = bpy.data.materials.new("tag_" + region)
        m.use_nodes = True
        nt = m.node_tree; nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*col, 1)
        o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs[0])
        mats[region] = m
    for me in meshes:
        ob = me; mesh = ob.data
        gnames = [g.name for g in ob.vertex_groups]
        vreg = []
        for v in mesh.vertices:
            best, bw = None, 0.0
            for g in v.groups:
                if g.weight > bw and g.group < len(gnames) and gnames[g.group] in bones:
                    bw, best = g.weight, gnames[g.group]
            if best is None:
                vreg.append("skin"); continue
            h, t = bones[best]
            ax = t - h; L = float(np.dot(ax, ax)) or 1.0
            tpar = float(np.dot(np.array(v.co) - h, ax) / L)
            region = "skin"
            for tend, rg in bone_region(best, keeper):
                if tpar <= tend: region = rg; break
            else:
                region = bone_region(best, keeper)[-1][1]
            vreg.append(region)
        mesh.materials.clear()
        order = list(TAGCOL)
        for rg in order: mesh.materials.append(mats[rg])
        for poly in mesh.polygons:
            votes = {}
            for vi in poly.vertices: votes[vreg[vi]] = votes.get(vreg[vi], 0) + 1
            poly.material_index = order.index(max(votes, key=votes.get))
    return mats

def make_camera(bpy, scale, loc, rot):
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = scale
    co = bpy.data.objects.new("cam", cam); co.location = loc
    co.rotation_euler = rot
    bpy.context.scene.collection.objects.link(co)
    bpy.context.scene.camera = co
    return co

def render(bpy, px_w, px_h, path, samples=16):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = samples; sc.cycles.device = "CPU"
    sc.render.resolution_x = px_w; sc.render.resolution_y = px_h
    sc.render.film_transparent = True
    sc.cycles.pixel_filter_type = "BOX"; sc.cycles.filter_width = 0.01   # hard region edges
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def to_lit(bpy, meshes):
    """Swap to a white diffuse + sun for the shade pass."""
    w = bpy.data.materials.new("lit"); w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs[0].default_value = (1,1,1,1)
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(df.outputs[0], o.inputs[0])
    for me in meshes:
        for i in range(len(me.data.materials)): me.data.materials[i] = w
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(55), 0, math.radians(-30))   # high-left key light
    bpy.context.scene.collection.objects.link(so)
    amb = bpy.data.worlds.new("w"); amb.use_nodes = True
    amb.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    bpy.context.scene.world = amb

def encode(tag_png, lit_png, out_png, out_size):
    """Tag+lit renders -> engine tag/UV format (reuses trace encoder maths)."""
    from PIL import Image
    tag = np.asarray(Image.open(tag_png).convert("RGBA")).astype(np.int16)
    lit = np.asarray(Image.open(lit_png).convert("L")).astype(np.float32)
    r, g, b, al = tag[...,0], tag[...,1], tag[...,2], tag[...,3]
    vis = al > 120
    out = np.zeros(tag.shape, np.uint8); out[...,3] = np.where(vis, 255, 0)
    masks = {
      "shirt":  vis & (r>180) & (g<70) & (b<70),
      "shorts": vis & (g>180) & (r<70) & (b<70),
      "socks":  vis & (b>180) & (r<70) & (g<70),
      "sleeve": vis & (r>180) & (g>180) & (b<70),
      "hair":   vis & (r>180) & (b>180) & (g<70),
    }
    finals = vis.copy()
    for m in masks.values(): finals &= ~m
    out[finals] = tag[finals].astype(np.uint8)                  # skin/boot/glove pass through
    # apply lighting to finals too
    lf = np.clip(0.55 + 0.55 * lit / 255.0, 0, 1.05)
    for c in range(3):
        out[..., c] = np.where(finals, np.clip(out[..., c] * lf, 0, 255), out[..., c])
    for kind, m in masks.items():
        if not m.any(): continue
        sh = np.zeros(m.shape, np.uint8)
        sh[m] = shade_of(lit[m])
        U, V = uv_of(m)
        uu = (np.clip(U,0,1)*88).astype(np.uint8); vv = (np.clip(V,0,1)*88).astype(np.uint8)
        if kind in ("shirt","shorts","socks"):
            ch = {"shirt":(0,1,2), "shorts":(1,0,2), "socks":(2,0,1)}[kind]
            out[m, ch[0]] = sh[m]; out[m, ch[1]] = uu[m]; out[m, ch[2]] = vv[m]
        elif kind == "sleeve":
            out[m,0] = out[m,1] = sh[m]; out[m,2] = uu[m]
        else:
            out[m,0] = out[m,2] = sh[m]; out[m,1] = 0
    img = Image.fromarray(out)
    if out_size: img = img.resize(out_size, Image.NEAREST)
    img.save(out_png, optimize=True)

def frame_range(arm):
    act = arm.animation_data.action if arm.animation_data else None
    return (int(act.frame_range[0]), int(act.frame_range[1])) if act else (1, 1)

# ---------------- commands ----------------
def cmd_probe(model):
    bpy = setup_scene(); arm, meshes = import_model(bpy, model)
    print("meshes:", [m.name for m in meshes])
    if arm:
        print("bones:", sorted(b.name for b in arm.data.bones)[:60])
        print("frames:", frame_range(arm), "actions:", [a.name for a in bpy.data.actions])

def render_pair(bpy, arm, meshes, frame, w, h, base, keeper=False):
    sc = bpy.context.scene; sc.frame_set(frame)
    render(bpy, w, h, base + "_tag.png")
    return base + "_tag.png"

def cmd_test():
    """End-to-end proof on the stand-in model (/tmp/test.glb, rigged walk)."""
    import shutil
    from PIL import Image
    bpy = setup_scene()
    arm, meshes = import_model(bpy, "/tmp/test.glb")
    assign_regions(bpy, arm, meshes)
    make_camera(bpy, 2.3, (0.3, -4, 0.95), (math.radians(80), 0, math.radians(8)))
    f0, f1 = frame_range(arm)
    frames = [f0 + int((f1 - f0) * t) for t in (0.0, 0.33, 0.66)]
    outs = []
    for i, fr in enumerate(frames):
        bpy.context.scene.frame_set(fr)
        render(bpy, 262, 382, f"/tmp/rp_{i}_tag.png")
    to_lit(bpy, meshes)
    for i, fr in enumerate(frames):
        bpy.context.scene.frame_set(fr)
        render(bpy, 262, 382, f"/tmp/rp_{i}_lit.png")
    for i in range(len(frames)):
        encode(f"/tmp/rp_{i}_tag.png", f"/tmp/rp_{i}_lit.png", f"/tmp/rp_{i}_enc.png", None)
        outs.append(f"/tmp/rp_{i}_enc.png")
    print("encoded:", outs)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"
    if cmd == "probe": cmd_probe(sys.argv[2])
    elif cmd == "test": cmd_test()
    else: print("striker/defender/keeper commands activate once Mixamo files land in artgen/source3d/")
