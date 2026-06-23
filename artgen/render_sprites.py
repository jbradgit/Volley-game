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
import sys, os, math, json, site
import numpy as np

# The bundled interpreter (e.g. Blender's) may not add the per-user site dir, where
# `pip install --user pillow` lands when the app's own site-packages isn't writable.
_usersite = site.getusersitepackages()
if _usersite and _usersite not in sys.path:
    sys.path.append(_usersite)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace_sprites import shade_of, uv_of                      # shared encoder maths

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "sprites")
SRC = os.path.join(ROOT, "artgen", "source3d")

# tag colours for the TAG pass (pure hues; engine contract)
TAGCOL = { "shirt": (1,0,0), "shorts": (0,1,0), "socks": (0,0,1), "sleeve": (1,1,0),
           "hair": (1,0,1), "skin": (0.93,0.75,0.58), "boot": (0.16,0.15,0.18),
           "glove": (0.95,0.95,0.97),
           "collar": (0,1,1), "cuff": (1,0.5,0), "sock_top": (0.5,0,1) }   # owner's 3 extra kit regions
TAGID = {k: i for i, k in enumerate(TAGCOL)}                   # id+1 in the id render

# owner's resolved polygon->region map (from striker_base_v01.blend material slots),
# transferred onto the same-topology FBX meshes so the sprite uses the EXACT regions.
_REGIONMAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kit_regions.json")
try:
    with open(_REGIONMAP_PATH) as _f: KIT_REGION_MAP = json.load(_f)
except Exception: KIT_REGION_MAP = {}

# owner's cylindrical sleeve unwrap (Kit_UV, per-loop, from the .blend) -> lengthwise sleeve stripes
_KITUV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kit_uv.json")
try:
    with open(_KITUV_PATH) as _f: KIT_UV_MAP = json.load(_f)
except Exception: KIT_UV_MAP = None
SLEEVE_U0, SLEEVE_UR = 0.1168, 0.87        # sleeve Kit_UV.x extent (pose-stable)

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

def _vertex_region(me_name, v, gnames, bone_names, keeper):
    """Per-vertex region. Garment meshes are whole-region; the shirt mesh splits
    shirt vs sleeve by the SUMMED arm-bone WEIGHT FRACTION (a smooth field -> the
    0.5 contour is a clean seam, not a jagged dominant-bone line)."""
    n = me_name.lower()
    if "short" in n:                  return "shorts"
    if "sock" in n:                   return "socks"
    if "shoe" in n or "boot" in n:    return "boot"
    if "hair" in n:                   return "hair"
    if "eyelash" in n or "brow" in n: return "skin"
    if "shirt" in n or "jersey" in n or "top" in n or "kit" in n:
        arm_w = tot = 0.0
        for g in v.groups:
            if g.group < len(gnames) and gnames[g.group] in bone_names:
                b = gnames[g.group].lower().split(":")[-1]; tot += g.weight
                if "forearm" in b or "hand" in b or b.endswith("arm"): arm_w += g.weight
        return "sleeve" if (tot > 0 and arm_w / tot > 0.5) else "shirt"
    # body / unknown mesh -> skin; keeper hands -> gloves (dominant bone)
    best, bw = None, 0.0
    for g in v.groups:
        if g.weight > bw and g.group < len(gnames) and gnames[g.group] in bone_names:
            bw, best = g.weight, gnames[g.group]
    b = (best or "").lower().split(":")[-1]
    if keeper and "hand" in b:        return "glove"
    return "skin"

def apply_kit_uv(meshes):
    """Transfer the owner's cylindrical Kit_UV (per-loop, same topology) onto the FBX shirt
    so the orco pass can emit it -> lengthwise sleeve stripes (orco-X gives rings, not stripes)."""
    if not KIT_UV_MAP: return
    for me_o in meshes:
        if me_o.name.split(".")[0] != "Ch38_Shirt": continue
        me = me_o.data
        if len(me.loops) != len(KIT_UV_MAP): continue
        uvl = me.uv_layers.get("Kit_UV") or me.uv_layers.new(name="Kit_UV")
        for li in range(len(me.loops)):
            uvl.data[li].uv = KIT_UV_MAP[li]

def assign_regions(bpy, arm, meshes, keeper=False):
    """Split every mesh's faces into flat TAG materials (mesh-name + smooth weight split)."""
    apply_kit_uv(meshes)                                        # ensure Kit_UV exists for the orco pass
    bone_names = set(b.name for b in arm.data.bones) if arm else set()
    mats = {}
    for region, col in TAGCOL.items():
        m = bpy.data.materials.new("tag_" + region)
        m.use_nodes = True
        nt = m.node_tree; nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*col, 1)
        o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs[0])
        mats[region] = m
    order = list(TAGCOL)
    for me in meshes:
        mesh = me.data
        mesh.materials.clear()
        for rg in order: mesh.materials.append(mats[rg])
        # OWNER'S RESOLVED REGIONS: if this mesh has a saved per-poly region map
        # (same topology), use it verbatim -> exact torso/sleeve/cuff/collar/socks/sock_top.
        base = me.name.split(".")[0]
        rmap = KIT_REGION_MAP.get(base)
        if rmap and len(rmap) == len(mesh.polygons):
            for pi, poly in enumerate(mesh.polygons):
                rg = rmap[pi]
                poly.material_index = order.index(rg) if rg in TAGCOL else order.index("skin")
            continue
        # fallback: bone-weight per-vertex region voting
        gnames = [g.name for g in me.vertex_groups]
        vreg = [_vertex_region(me.name, v, gnames, bone_names, keeper) for v in mesh.vertices]
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

def render(bpy, px_w, px_h, path, samples=16, denoise=False, hard=True):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = samples; sc.cycles.device = "CPU"
    sc.render.resolution_x = px_w; sc.render.resolution_y = px_h
    sc.render.film_transparent = True
    if hard:
        sc.cycles.pixel_filter_type = "BOX"; sc.cycles.filter_width = 0.01   # hard region edges (tag)
    else:
        sc.cycles.pixel_filter_type = "GAUSSIAN"; sc.cycles.filter_width = 1.5   # AA (beauty/lit)
    sc.cycles.use_denoising = denoise                                    # smooth shade -> clean cel bands
    if denoise:
        try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception: pass
        # clamp bright fireflies (the salt-and-pepper speckle at skin/garment seams) before denoise
        try:
            sc.cycles.sample_clamp_indirect = 1.5    # tighter: kill fireflies on dark skin
            sc.cycles.sample_clamp_direct = 3.0
            sc.cycles.blur_glossy = 2.0
        except Exception: pass
    # keep flat tag colours numerically pure (no Filmic/AgX tone-mapping)
    try: sc.view_settings.view_transform = "Standard"
    except Exception: pass
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def add_lights(bpy, cam=None, energy=4.6, ambient=0.95):
    """CAMERA-RELATIVE key light + BRIGHT neutral ambient fill (used for BOTH the beauty and the
    lit/shade pass). Owner: previous lighting was too low -> skin/ball read dark and grey.
    Idempotent: skips if a sun already exists."""
    from mathutils import Matrix
    if any(o.type == "LIGHT" for o in bpy.context.scene.objects):
        return
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = energy; sun.angle = math.radians(8)
    so = bpy.data.objects.new("sun", sun)
    if cam is not None:                              # key from the camera's upper-left
        m = cam.matrix_world.to_3x3() @ (Matrix.Rotation(math.radians(-26), 3, "X")
                                          @ Matrix.Rotation(math.radians(20), 3, "Y"))
        so.rotation_euler = m.to_euler()
    else:
        so.rotation_euler = (math.radians(55), 0, math.radians(-30))
    bpy.context.scene.collection.objects.link(so)
    amb = bpy.data.worlds.new("w"); amb.use_nodes = True
    bg = amb.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.92, 0.92, 0.95, 1)   # bright neutral fill lifts the shadow side (no dark/grey skin)
    bg.inputs[1].default_value = ambient
    bpy.context.scene.world = amb

def to_lit(bpy, meshes, cam=None):
    """Swap meshes to a white diffuse for the shade pass; ensure lights exist."""
    w = bpy.data.materials.new("lit"); w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs[0].default_value = (1,1,1,1)
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(df.outputs[0], o.inputs[0])
    for me in meshes:
        for i in range(len(me.data.materials)): me.data.materials[i] = w
    add_lights(bpy, cam)

# torso Generated-coord extent (pose-stable, from striker_base_v01.blend) -> planar pattern space
TORSO_X0, TORSO_XR, TORSO_Y0, TORSO_YR = 0.3575, 0.2879, 0.0, 0.9806

def to_orco(bpy, meshes):
    """Swap meshes to an EMISSION of the Generated (orco) coordinate -> a pose-stable
    PLANAR pattern coordinate (the same space kit_patterns.py uses). Rendered raw so
    stripes are parallel, not warped by the body silhouette like the screen-space UV."""
    m = bpy.data.materials.new("orco"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "Kit_UV"
    sepuv = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(uvn.outputs["UV"], sepuv.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], comb.inputs[0])             # R = Generated.X  (torso planar)
    nt.links.new(sep.outputs["Y"], comb.inputs[1])             # G = Generated.Y
    nt.links.new(sepuv.outputs["X"], comb.inputs[2])           # B = Kit_UV.x     (sleeve cylinder)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.0
    nt.links.new(comb.outputs[0], em.inputs[0])
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs[0])
    for me in meshes:
        for i in range(len(me.data.materials)): me.data.materials[i] = m

def render_orco(bpy, px_w, px_h, path):
    """Render the orco coord pass LINEAR (Raw view transform) so R=orcoX, G=orcoY are read back true."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = 1; sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = px_w, px_h
    sc.render.film_transparent = True
    sc.cycles.pixel_filter_type = "BOX"; sc.cycles.filter_width = 0.01
    sc.cycles.use_denoising = False
    try: sc.view_settings.view_transform = "Raw"
    except Exception:
        try: sc.view_settings.view_transform = "Standard"
        except Exception: pass
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def _smooth_labels(L, n):
    """3x3 majority filter on an integer label image — removes isolated speckle pixels
    so region boundaries become clean lines."""
    counts = np.zeros((n,) + L.shape, np.int16)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            s = np.roll(np.roll(L, dy, 0), dx, 1)
            for k in range(n):
                counts[k] += (s == k)
    return np.argmax(counts, axis=0).astype(np.uint8)

def encode(tag_png, lit_png, out_png, out_size, beauty_png=None, orco_png=None):
    """Tag+lit renders -> engine tag/UV format. When a BEAUTY render (original Mixamo
    materials) is supplied, the non-kit regions (skin/face/hair/boots/gloves) take the
    real detailed pixels; only the kit regions stay flat-tagged for recolouring.
    orco_png (linear Generated coords) gives the shirt PLANAR pattern UV -> parallel stripes."""
    from PIL import Image
    tag = np.asarray(Image.open(tag_png).convert("RGBA")).astype(np.int16)
    lit = np.asarray(Image.open(lit_png).convert("L")).astype(np.float32)
    orco = None
    if orco_png is not None:
        orco = np.asarray(Image.open(orco_png).convert("RGB")).astype(np.float32) / 255.0
    r, g, b, al = tag[...,0], tag[...,1], tag[...,2], tag[...,3]
    vis = al > 120
    out = np.zeros(tag.shape, np.uint8)
    # OUTPUT silhouette eroded 1px -> drops the fuzzy halo edge ring (hair light-fuzz from the
    # skin-tone backing / AA fringe). Region classification still uses the full `vis`.
    visE = vis & np.roll(vis,1,0) & np.roll(vis,-1,0) & np.roll(vis,1,1) & np.roll(vis,-1,1)
    out[...,3] = np.where(visE, 255, 0)
    # Label every visible pixel, then MAJORITY-FILTER the labels to kill the
    # salt-and-pepper speckle at garment/skin boundaries (z-fight + AA fringe).
    SKIN, NLAB = 7, 11    # +8 collar, 9 cuff, 10 sock_top (owner's extra solid kit regions)
    L = np.zeros(vis.shape, np.uint8); L[vis] = SKIN
    L[vis & (r>180) & (g<70) & (b<70)] = 1                       # shirt    red
    L[vis & (g>180) & (r<70) & (b<70)] = 2                       # shorts   green
    L[vis & (b>180) & (r<70) & (g<70)] = 3                       # socks    blue
    L[vis & (r>180) & (g>180) & (b<70)] = 4                      # sleeve   yellow
    L[vis & (r>180) & (b>180) & (g<70)] = 5                      # hair     magenta
    L[vis & (r>230) & (g>230) & (b>230)] = 6                     # glove ~neutral-white (NOT warm skin, whose sRGB blue is ~201)
    L[vis & (g>180) & (b>180) & (r<70)] = 8                      # collar   cyan
    L[vis & (r>180) & (g>70) & (g<215) & (b<70)] = 9             # cuff     orange (linear 0.5 -> sRGB 188, so <215 not <180)
    L[vis & (r>70) & (r<215) & (g<70) & (b>180)] = 10            # sock_top purple (linear 0.5 -> sRGB 188)
    L = _smooth_labels(L, NLAB); L[~vis] = 0
    masks = {"shirt": L==1, "shorts": L==2, "socks": L==3, "sleeve": L==4,
             "collar": L==8, "cuff": L==9, "sock_top": L==10}
    if beauty_png is None:
        masks["hair"] = L==5
    glove = L==6
    finals = vis & ~np.isin(L, (1, 2, 3, 4, 8, 9, 10))
    if beauty_png is not None:                                  # detail pass: real skin/face/hair/boots
        from PIL import ImageFilter
        bimg = Image.open(beauty_png).convert("RGBA")
        # composite over a skin-tone backing so mesh gaps / AA fringe read as skin not background
        back = Image.new("RGBA", bimg.size, (236, 188, 146, 255))
        bc = Image.alpha_composite(back, bimg).convert("RGB")
        # despeckle: real skin is saturated tan; the fireflies are NEUTRAL + BRIGHT clusters.
        # Target that signature and replace with a 7x7 median (pulls in surrounding dark skin),
        # plus a 3x3 pass for isolated outliers. Kills salt-and-pepper without softening real detail.
        b0 = np.asarray(bc).astype(np.int16)
        med3 = np.asarray(bc.filter(ImageFilter.MedianFilter(3))).astype(np.int16)
        med7 = np.asarray(bc.filter(ImageFilter.MedianFilter(7))).astype(np.int16)
        mx = b0.max(axis=2); mn = b0.min(axis=2)
        spec = ((mx - mn) < 30) & (mx > 160)                 # neutral + bright = specular firefly
        out3 = np.abs(b0 - med3).max(axis=2) > 38            # isolated outlier
        beauty = b0.copy()
        beauty = np.where(out3[..., None], med3, beauty)
        beauty = np.where(spec[..., None], med7, beauty)
        beauty = beauty.astype(np.uint8)
        detail = finals & ~glove                                # skin/hair/boots get real pixels
        for c in range(3):
            out[..., c] = np.where(detail, beauty[..., c], out[..., c])
        if glove.any():                                          # gloves: white with the lit shading
            lf = np.clip(0.55 + 0.55 * lit / 255.0, 0, 1.05)
            for c in range(3):
                out[..., c] = np.where(glove, np.clip(238 * lf, 0, 255), out[..., c])
    else:
        finals = finals & (L!=5)                                # hair is a recolour region here
        out[finals] = tag[finals].astype(np.uint8)              # skin/boot/glove pass through (flat)
        lf = np.clip(0.55 + 0.55 * lit / 255.0, 0, 1.05)
        for c in range(3):
            out[..., c] = np.where(finals, np.clip(out[..., c] * lf, 0, 255), out[..., c])
    for kind, m in masks.items():
        if not m.any(): continue
        sh = np.zeros(m.shape, np.uint8)
        sh[m] = shade_of(lit[m])
        if kind in ("shirt", "shorts", "socks", "sleeve"):     # patterned: carry UV
            if kind == "shirt" and orco is not None:            # PLANAR torso coord -> parallel stripes/hoops
                U = np.clip((orco[...,0] - TORSO_X0) / TORSO_XR, 0, 1)
                V = np.clip((orco[...,1] - TORSO_Y0) / TORSO_YR, 0, 1)
            elif kind == "sleeve" and orco is not None:         # cylindrical Kit_UV.x -> lengthwise stripes
                U = np.clip((orco[...,2] - SLEEVE_U0) / SLEEVE_UR, 0, 1)
                V = np.clip((orco[...,1] - TORSO_Y0) / TORSO_YR, 0, 1)
            else:
                U, V = uv_of(m)
            uu = (np.clip(U,0,1)*88).astype(np.uint8); vv = (np.clip(V,0,1)*88).astype(np.uint8)
            if kind in ("shirt","shorts","socks"):
                ch = {"shirt":(0,1,2), "shorts":(1,0,2), "socks":(2,0,1)}[kind]
                out[m, ch[0]] = sh[m]; out[m, ch[1]] = uu[m]; out[m, ch[2]] = vv[m]
            else:                                              # sleeve: RG=shade, B=u
                out[m,0] = out[m,1] = sh[m]; out[m,2] = uu[m]
        elif kind == "collar":                                 # solid: GB=shade, R=0
            out[m,1] = out[m,2] = sh[m]; out[m,0] = 0
        elif kind == "cuff":                                   # solid: RB=shade, G=0
            out[m,0] = out[m,2] = sh[m]; out[m,1] = 0
        elif kind == "sock_top":                               # solid: B=shade, R=110 marker, G=0
            out[m,2] = sh[m]; out[m,0] = 110; out[m,1] = 0
        else:                                                  # hair (procedural path only)
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

# ---------------- framing helpers ----------------
TMP = os.environ.get("TEMP", "/tmp")

def world_bbox(meshes):
    from mathutils import Vector
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for me in meshes:
        for c in me.bound_box:
            w = me.matrix_world @ Vector(c)
            mn = Vector((min(mn[i], w[i]) for i in range(3)))
            mx = Vector((max(mx[i], w[i]) for i in range(3)))
    return mn, mx

def make_ortho_cam(bpy, center, az_deg, el_deg, height):
    from mathutils import Vector
    center = Vector(center)
    sc = bpy.context.scene
    cam_d = bpy.data.cameras.new("c"); cam_d.type = "ORTHO"; cam_d.ortho_scale = height * 1.1
    cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    emp = bpy.data.objects.new("tgt", None); emp.location = center; sc.collection.objects.link(emp)
    trk = cam.constraints.new("TRACK_TO"); trk.target = emp
    trk.track_axis = "TRACK_NEGATIVE_Z"; trk.up_axis = "UP_Y"
    a = math.radians(az_deg); e = math.radians(el_deg); R = max(6.0, height * 3)
    cam.location = center + Vector((R*math.cos(e)*math.sin(a), -R*math.cos(e)*math.cos(a), R*math.sin(e)))
    bpy.context.view_layer.update()
    return cam, emp

def _flat_render(bpy, res, path):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.display.shading.light = "FLAT"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def _measure(path):
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGBA"))[..., 3] > 16
    ys, xs = np.where(a)
    if len(xs) == 0: return None
    return dict(x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()),
                W=a.shape[1], H=a.shape[0])

def fit_camera(bpy, cam, emp, res, frame, tgt):
    """Adjust ortho_scale + target (along camera right/up) so the silhouette hits
    tgt px {top, feet, cx}. Deterministic: 1 scale pass + 1 calibrated shift pass."""
    from mathutils import Vector
    bpy.context.scene.frame_set(frame)
    W, H = res
    tmp = os.path.join(TMP, "_fit.png")
    # pass 1: scale to height
    for _ in range(3):
        _flat_render(bpy, res, tmp); m = _measure(tmp)
        h_px = m["y1"] - m["y0"]; want = tgt["feet"] - tgt["top"]
        if abs(h_px - want) <= 3: break
        cam.data.ortho_scale *= h_px / want
        bpy.context.view_layer.update()
    # calibrate world-move -> px with the camera basis
    R3 = cam.matrix_world.to_3x3()
    right = (R3 @ Vector((1, 0, 0))).normalized()
    up = (R3 @ Vector((0, 1, 0))).normalized()
    _flat_render(bpy, res, tmp); m0 = _measure(tmp)
    cx0 = (m0["x0"] + m0["x1"]) / 2; cy0 = (m0["y0"] + m0["y1"]) / 2
    step = cam.data.ortho_scale * 0.05
    emp.location += right * step; bpy.context.view_layer.update()
    _flat_render(bpy, res, tmp); mR = _measure(tmp); emp.location -= right * step
    emp.location += up * step; bpy.context.view_layer.update()
    _flat_render(bpy, res, tmp); mU = _measure(tmp); emp.location -= up * step
    dcx_dr = (((mR["x0"]+mR["x1"])/2) - cx0) / step or 1e-6
    dcy_du = (((mU["y0"]+mU["y1"])/2) - cy0) / step or 1e-6
    tgt_cx = tgt["cx"]; tgt_cy = (tgt["top"] + tgt["feet"]) / 2
    emp.location += right * ((tgt_cx - cx0) / dcx_dr)
    emp.location += up * ((tgt_cy - cy0) / dcy_du)
    bpy.context.view_layer.update()

def _union_bbox(boxes):
    return (min(b["x0"] for b in boxes), min(b["y0"] for b in boxes),
            max(b["x1"] for b in boxes), max(b["y1"] for b in boxes))

def correct_for_union(bpy, cam, emp, res, union, inset=12):
    """Scale + recentre the camera so the given union bbox fits the canvas inset at
    the largest non-clipping size (one analytic pass, no extra renders)."""
    from mathutils import Vector
    W, H = res; ux0, uy0, ux1, uy1 = union
    uw = max(1, ux1 - ux0); uh = max(1, uy1 - uy0)
    s = min((W - 2*inset) / uw, (H - 2*inset) / uh)
    wpp = cam.data.ortho_scale / max(W, H)
    R3 = cam.matrix_world.to_3x3()
    right = (R3 @ Vector((1, 0, 0))).normalized(); up = (R3 @ Vector((0, 1, 0))).normalized()
    ucx = (ux0 + ux1) / 2; ucy = (uy0 + uy1) / 2
    emp.location += right * ((ucx - W/2) * wpp) + up * (-(ucy - H/2) * wpp)   # emp -> union centre
    cam.data.ortho_scale /= s
    bpy.context.view_layer.update()

def recenter_feet(bpy, cam, emp, res, feet_px):
    """Translate (no scale) so the silhouette's bottom-centre lands at feet_px — used to
    re-anchor catch clips whose root motion shifts the keeper off the idle camera."""
    from mathutils import Vector
    tmp = os.path.join(TMP, "_rc.png")
    _flat_render(bpy, res, tmp); m = _measure(tmp)
    if not m: return
    cx = (m["x0"] + m["x1"]) / 2; by = m["y1"]
    wpp = cam.data.ortho_scale / max(res)
    R3 = cam.matrix_world.to_3x3()
    right = (R3 @ Vector((1, 0, 0))).normalized(); up = (R3 @ Vector((0, 1, 0))).normalized()
    emp.location += right * ((cx - feet_px[0]) * wpp) + up * (-(by - feet_px[1]) * wpp)
    bpy.context.view_layer.update()

def cam_state(cam, emp):
    return dict(loc=tuple(cam.location), scale=cam.data.ortho_scale, tgt=tuple(emp.location))

def apply_cam_state(cam, emp, st):
    from mathutils import Vector
    cam.location = Vector(st["loc"]); cam.data.ortho_scale = st["scale"]
    emp.location = Vector(st["tgt"])

STRIKER_RES = (300, 382)                       # wider canvas; union auto-fit centres the whole volley arc
STRIKER_TGT = dict(top=12, feet=372, cx=150)   # initial idle fit; correct_for_union then fits all 6 frames
STRIKER_AZ, STRIKER_EL = 180, 12          # from directly behind (owner pick az180)

def _puff_garments(bpy, meshes, delta=0.007):
    """Push garment meshes out along their normals so they cleanly cover the body mesh
    instead of z-fighting with it (the salt-and-pepper speckle on socks/shorts/collar)."""
    import bmesh
    for me in meshes:
        n = me.name.lower()
        if not any(k in n for k in ("shirt", "shorts", "sock", "shoe", "jersey", "kit", "top")):
            continue
        bm = bmesh.new(); bm.from_mesh(me.data); bm.normal_update()
        for v in bm.verts:
            v.co += v.normal * delta
        bm.to_mesh(me.data); bm.free()

def _import_clean(bpy, path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    arm, meshes = import_model(bpy, path)
    _puff_garments(bpy, meshes)
    return arm, meshes

STRIKER_KICK = [9, 11, 13, 14, 16]        # GROUNDED k1..k5, contact (k3) on f14 (dropped airborne f18/f22)

def _render_tag_lit_set(bpy, meshes, cam, frames, tags, lits, res):
    """Render the TAG pass for every frame, then swap to lit and render the LIT pass."""
    for fr, tp in zip(frames, tags):
        bpy.context.scene.frame_set(fr); render(bpy, *res, tp, samples=1)
    to_lit(bpy, meshes, cam)
    for fr, lp in zip(frames, lits):
        bpy.context.scene.frame_set(fr); render(bpy, *res, lp, samples=64, denoise=True)

def cmd_striker(idle_fbx, shot_fbx):
    """k0 from the idle clip; k1..k5 from the shot clip, all through ONE camera that is
    auto-fitted to the union of all 6 poses so the volley arc never clips."""
    bpy = __import__("bpy")
    R = STRIKER_RES; tmp = os.path.join(TMP, "_sfit.png")
    idle_frame = None
    # --- shot clip: measure standing(frame1)+kick union with a ZOOMED-OUT cam (nothing
    #     clipping so extents are true), then auto-fit the camera to that union ---
    arm2, meshes2 = _import_clean(bpy, shot_fbx)
    assign_regions(bpy, arm2, meshes2)
    mn2, mx2 = world_bbox(meshes2); height = mx2.z - mn2.z
    cam2, emp2 = make_ortho_cam(bpy, (mn2 + mx2) / 2, STRIKER_AZ, STRIKER_EL, height)
    cam2.data.ortho_scale = height * 2.8; bpy.context.view_layer.update()
    stand = frame_range(arm2)[0]
    bbs = []
    for fr in [stand] + STRIKER_KICK:
        bpy.context.scene.frame_set(fr); _flat_render(bpy, R, tmp); bbs.append(_measure(tmp))
    correct_for_union(bpy, cam2, emp2, R, _union_bbox(bbs))
    st2 = cam_state(cam2, emp2)
    # render k1..k5 with the corrected camera
    tags = [os.path.join(TMP, f"k{i+1}_tag.png") for i in range(5)]
    lits = [os.path.join(TMP, f"k{i+1}_lit.png") for i in range(5)]
    _render_tag_lit_set(bpy, meshes2, cam2, STRIKER_KICK, tags, lits, R)
    for i in range(5):
        encode(tags[i], lits[i], os.path.join(OUT, f"striker_k{i+1}.png"), None)
    # render k0 with the SAME corrected camera (re-import: lit pass replaced shot materials)
    arm3, meshes3 = _import_clean(bpy, idle_fbx)
    idle_frame = frame_range(arm3)[0]
    assign_regions(bpy, arm3, meshes3)
    cam3, emp3 = make_ortho_cam(bpy, (0, 0, 0), STRIKER_AZ, STRIKER_EL, 1.8)
    apply_cam_state(cam3, emp3, st2)
    t0 = os.path.join(TMP, "k0_tag.png"); l0 = os.path.join(TMP, "k0_lit.png")
    _render_tag_lit_set(bpy, meshes3, cam3, [idle_frame], [t0], [l0], R)
    encode(t0, l0, os.path.join(OUT, "striker_k0.png"), None)
    for i in range(6):
        print(f"STRIKER k{i}:", _measure(os.path.join(OUT, f"striker_k{i}.png")))

STRIKER_KICK_CLIP = list(range(1, 16))     # owner pick: full volley wind-up->strike, Shot f1..f15
STRIKER_STRIKE_TICK = 12                    # contact = Shot f13 = index 12 in the kick list

def cmd_striker_sheet(idle_fbx, shot_fbx):
    """FULL-MOTION striker: idle + 20 dense kick frames packed L->R into one sheet
    (striker_sheet.png). One fixed union-fit camera so every frame shares an anchor;
    the engine plays frame=min(manKickT,N) so the strike syncs to the contact tick."""
    bpy = __import__("bpy")
    from PIL import Image
    R = STRIKER_RES; tmp = os.path.join(TMP, "_sfit.png")
    # union-fit camera over standing + all kick frames (zoomed out so extents are true)
    arm2, meshes2 = _import_clean(bpy, shot_fbx)
    mn2, mx2 = world_bbox(meshes2); height = mx2.z - mn2.z
    cam2, emp2 = make_ortho_cam(bpy, (mn2 + mx2) / 2, STRIKER_AZ, STRIKER_EL, height)
    cam2.data.ortho_scale = height * 2.8; bpy.context.view_layer.update()
    stand = frame_range(arm2)[0]
    bbs = []
    for fr in [stand] + STRIKER_KICK_CLIP:
        bpy.context.scene.frame_set(fr); _flat_render(bpy, R, tmp); bbs.append(_measure(tmp))
    correct_for_union(bpy, cam2, emp2, R, _union_bbox(bbs))
    st2 = cam_state(cam2, emp2)
    # render the 20 kick frames (with detail pass)
    kick_imgs = _render_clip_frames(bpy, arm2, meshes2, cam2, STRIKER_KICK_CLIP, "sh", 32,
                                    keeper=False, detail=True, res=R)
    # render the idle (frame 0) with the SAME camera (with detail pass)
    arm3, meshes3 = _import_clean(bpy, idle_fbx)
    idle_fr = frame_range(arm3)[0]
    cam3, emp3 = make_ortho_cam(bpy, (0, 0, 0), STRIKER_AZ, STRIKER_EL, 1.8)
    apply_cam_state(cam3, emp3, st2)
    idle_img = _render_clip_frames(bpy, arm3, meshes3, cam3, [idle_fr], "shidle", 32,
                                   keeper=False, detail=True, res=R)[0]
    # pack idle + kicks L->R
    frames = [idle_img] + kick_imgs
    sheet = Image.new("RGBA", (R[0] * len(frames), R[1]), (0, 0, 0, 0))
    for i, im in enumerate(frames): sheet.paste(im, (i * R[0], 0))
    sheet.save(os.path.join(OUT, "striker_sheet.png"), optimize=True)
    m = _measure(os.path.join(TMP, "sh_idle_enc.png"))
    print(f"STRIKER SHEET {len(frames)} frames @ {R[0]}x{R[1]}; idle bbox {m}; strike at frame {STRIKER_STRIKE_TICK}")

DEF_RES = (134, 230)
DEF_TGT = dict(top=4, feet=226, cx=67)
DEF_AZ, DEF_EL = 0, 8                       # front-on (owner: defenders face straight front)

DEF_VARIANTS = [5, 6, 7, 8]                   # Goalkeeper Miss frames -> 4 distinct defender poses (engine picks 3 of 4)

def cmd_defender_sheet(model_fbx):
    """Several front-facing defender poses packed into defender_sheet.png so the
    engine can give each defender a different stance (no clone army)."""
    bpy = __import__("bpy")
    from PIL import Image
    arm, meshes = _import_clean(bpy, model_fbx)
    mn, mx = world_bbox(meshes)
    cam, emp = make_ortho_cam(bpy, (mn + mx) / 2, DEF_AZ, DEF_EL, mx.z - mn.z)
    fit_camera(bpy, cam, emp, DEF_RES, DEF_VARIANTS[0], DEF_TGT)
    imgs = _render_clip_frames(bpy, arm, meshes, cam, DEF_VARIANTS, "defv", 24,
                               keeper=False, detail=True, res=DEF_RES)
    sheet = Image.new("RGBA", (DEF_RES[0] * len(imgs), DEF_RES[1]), (0, 0, 0, 0))
    for i, im in enumerate(imgs): sheet.paste(im, (i * DEF_RES[0], 0))
    sheet.save(os.path.join(OUT, "defender_sheet.png"), optimize=True)
    print(f"DEFENDER SHEET {len(imgs)} variants @ {DEF_RES[0]}x{DEF_RES[1]}")

def cmd_defender(model_fbx, frame=None):
    """One front-facing base (outfield kit, not keeper) -> defender.png, with the
    detail pass (real face/hair/skin) composited into the non-kit regions."""
    bpy = __import__("bpy")
    arm, meshes = _import_clean(bpy, model_fbx)
    f0, f1 = frame_range(arm)
    fr = int(frame) if frame else f0 + (f1 - f0) // 3
    mn, mx = world_bbox(meshes)
    cam, emp = make_ortho_cam(bpy, (mn + mx) / 2, DEF_AZ, DEF_EL, mx.z - mn.z)
    fit_camera(bpy, cam, emp, DEF_RES, fr, DEF_TGT)
    add_lights(bpy, cam)
    bp = os.path.join(TMP, "def_beauty.png")
    bpy.context.scene.frame_set(fr); render(bpy, *DEF_RES, bp, samples=40, denoise=True, hard=False)
    assign_regions(bpy, arm, meshes, keeper=False)
    t = os.path.join(TMP, "def_tag.png"); l = os.path.join(TMP, "def_lit.png")
    bpy.context.scene.frame_set(fr); render(bpy, *DEF_RES, t, samples=1, hard=True)
    to_lit(bpy, meshes, cam)
    bpy.context.scene.frame_set(fr); render(bpy, *DEF_RES, l, samples=24, denoise=True, hard=False)
    encode(t, l, os.path.join(OUT, "defender.png"), None, beauty_png=bp)
    print("DEFENDER frame", fr, _measure(os.path.join(OUT, "defender.png")))

# ---------------- ball (rotating Tango sphere, no logo) ----------------
def _tango_texture(path, W=1600, H=800, inner=16.5, outer=26.0, bw=7.5, bmax=33.0):
    """Equirectangular Tango map: WHITE-dominant ball with 12 black rings around the
    icosahedral pentagons + thin black bridges along the edges connecting adjacent
    rings (the interlocking Tango look). White pentagon + hexagon centres. No logo."""
    from PIL import Image
    phi = (1 + 5 ** 0.5) / 2
    raw = []
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            raw += [(0, s1, s2*phi), (s1, s2*phi, 0), (s2*phi, 0, s1)]   # 12 icosa verts
    V = np.array(raw, float); V /= np.linalg.norm(V, axis=1, keepdims=True)
    lon = np.linspace(0, 2*np.pi, W, endpoint=False)
    lat = np.linspace(0, np.pi, H)
    LO, LA = np.meshgrid(lon, lat)
    D = np.stack([np.sin(LA)*np.cos(LO), np.sin(LA)*np.sin(LO), np.cos(LA)], -1)
    dots = D @ V.T
    s = np.sort(dots, axis=-1)
    a1 = np.degrees(np.arccos(np.clip(s[..., -1], -1, 1)))             # nearest vertex
    a2 = np.degrees(np.arccos(np.clip(s[..., -2], -1, 1)))             # 2nd nearest
    ring = (a1 >= inner) & (a1 <= outer)                              # black ring around each pentagon
    bridge = ((a2 - a1) < bw) & (a1 > inner) & (a1 < bmax)            # thin connector along shared edges
    img = np.full((H, W, 3), 245, np.uint8)                            # off-white leather
    img[ring | bridge] = (20, 20, 24)
    Image.fromarray(img).save(path)

BALL_RES = (132, 132)
BALL_FRAMES = 24

def cmd_ball():
    bpy = __import__("bpy")
    from PIL import Image
    from mathutils import Vector, Matrix
    tex = os.path.join(TMP, "_tango_tex.png"); _tango_texture(tex)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=1.0)
    ball = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    mat = bpy.data.materials.new("ball"); mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    tnode = nt.nodes.new("ShaderNodeTexImage"); tnode.image = bpy.data.images.load(tex)
    tnode.interpolation = "Cubic"
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.55
    nt.links.new(tnode.outputs["Color"], bsdf.inputs["Base Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(bsdf.outputs[0], out.inputs[0])
    ball.data.materials.append(mat)
    cam_d = bpy.data.cameras.new("c"); cam_d.type = "ORTHO"; cam_d.ortho_scale = 2.18
    cam = bpy.data.objects.new("cam", cam_d); cam.location = (0, -6, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera = cam
    sun = bpy.data.lights.new("s", "SUN"); sun.energy = 3.6; sun.angle = math.radians(15)
    so = bpy.data.objects.new("s", sun); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
    bpy.context.scene.collection.objects.link(so)
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    bw = w.node_tree.nodes["Background"]; bw.inputs[0].default_value=(0.95,0.95,0.97,1); bw.inputs[1].default_value = 0.95   # brighter -> white ball, not grey
    bpy.context.scene.world = w
    axis = Vector((0.32, 0.0, 1.0)).normalized()
    ball.rotation_mode = "AXIS_ANGLE"
    sheet = Image.new("RGBA", (BALL_RES[0]*BALL_FRAMES, BALL_RES[1]), (0, 0, 0, 0))
    for i in range(BALL_FRAMES):
        ball.rotation_axis_angle = (2*math.pi*i/BALL_FRAMES, *axis)
        bpy.context.view_layer.update()
        p = os.path.join(TMP, f"ball_{i}.png")
        render(bpy, *BALL_RES, p, samples=24, denoise=True)
        sheet.paste(Image.open(p).convert("RGBA"), (i*BALL_RES[0], 0))
    sheet.save(os.path.join(OUT, "ball_sheet.png"), optimize=True)
    print(f"BALL SHEET {BALL_FRAMES} frames @ {BALL_RES[0]}x{BALL_RES[1]}")

# ---------------- keeper ----------------
# Render INTO the engine's unified 596x263 canvas at 2x (1192x526), feet anchor at
# unified (300,197) -> px (600,394). Each frame is then cropped+packed exactly like
# gen_sprites.py, so the manifest (ox/oy/w/h + frame numbers) and the binding save
# extents are reproduced and index.html needs no change.
KEEPER_RES = (1192, 526)
KEEPER_IDLE_TGT = dict(top=138, feet=394, cx=600)     # idle silhouette -> ~x267-334 y69-198
KEEPER_AZ, KEEPER_EL = 0, 6                            # keeper faces the camera (front)
KEEPER_DIVE_FRAMES = (7, 40)                           # Diving Save f7->f40 (f40 = full horizontal stretch; f57 was the prone collapse, reached short)

def _encode_open(tag, lit, tmpname, beauty=None, orco=None):
    p = os.path.join(TMP, tmpname)
    encode(tag, lit, p, None, beauty_png=beauty, orco_png=orco)
    from PIL import Image
    return Image.open(p).convert("RGBA").copy()

def _mirror_canvas(im):
    """Mirror a unified-canvas frame about the feet x=600 so the dive flips side."""
    from PIL import Image
    fl = im.transpose(Image.FLIP_LEFT_RIGHT)           # feet 600 -> 592
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.paste(fl, (8, 0))   # back to 600
    return out

def _pack_keeper(frames):
    from PIL import Image
    packed = []
    for fn, im in frames.items():
        bb = im.getbbox()
        if bb is None: continue
        packed.append((fn, im.crop(bb), bb))
    packed.sort(key=lambda x: -x[1].height)
    SHEET_W = 2048; x = y = rowh = 0; places = []
    for fn, im, bb in packed:
        if x + im.width > SHEET_W: x = 0; y += rowh + 2; rowh = 0
        places.append((fn, im, bb, x, y)); x += im.width + 2; rowh = max(rowh, im.height)
    sheet = Image.new("RGBA", (SHEET_W, y + rowh + 2), (0, 0, 0, 0)); man = {}
    for fn, im, bb, px_, py_ in places:
        sheet.paste(im, (px_, py_))
        man[str(fn)] = dict(sheet=0, x=px_, y=py_, w=im.width, h=im.height, ox=bb[0]/2.0, oy=bb[1]/2.0)
    sheet.save(os.path.join(OUT, "keeper_atlas.png"), optimize=True)
    json.dump(dict(frames=man), open(os.path.join(OUT, "keeper_atlas.json"), "w"))
    def ext(fr):
        m = man[str(fr)]; return (round(m["ox"]), round(m["ox"]+m["w"]/2), round(m["oy"]), round(m["oy"]+m["h"]/2))
    print("KEEPER atlas", sheet.size, len(man), "frames")
    print("  idle", ext(1), "target(267,334,69,198)")
    print("  dv99", ext(99), "target(5,178,153,211)")
    print("  dv50", ext(50), "  high354", ext(354), "target(263,330,53,196)")

def _render_clip_frames(bpy, arm, meshes, cam, clip_frames, prefix, lit_samples, keeper=True, detail=False, res=None):
    """Render a set of frames -> encoded PIL images. detail=True adds the beauty
    (real materials) pass for face/hair/skin; flat (detail=False) for fast motion."""
    res = res or KEEPER_RES
    n = len(clip_frames)
    beauties = [None] * n
    if detail:
        add_lights(bpy, cam)
        for i, fr in enumerate(clip_frames):
            bpy.context.scene.frame_set(fr); bp = os.path.join(TMP, f"{prefix}_{i}_b.png")
            render(bpy, *res, bp, samples=96, denoise=True, hard=False); beauties[i] = bp
    assign_regions(bpy, arm, meshes, keeper=keeper)
    tags = [os.path.join(TMP, f"{prefix}_{i}_t.png") for i in range(n)]
    for fr, tp in zip(clip_frames, tags):
        bpy.context.scene.frame_set(fr); render(bpy, *res, tp, samples=1, hard=True)
    to_orco(bpy, meshes)                                        # planar pattern-coord pass (parallel stripes)
    orcos = [os.path.join(TMP, f"{prefix}_{i}_o.png") for i in range(n)]
    for fr, op in zip(clip_frames, orcos):
        bpy.context.scene.frame_set(fr); render_orco(bpy, *res, op)
    to_lit(bpy, meshes, cam)
    lits = [os.path.join(TMP, f"{prefix}_{i}_l.png") for i in range(n)]
    for fr, lp in zip(clip_frames, lits):
        bpy.context.scene.frame_set(fr); render(bpy, *res, lp, samples=lit_samples, denoise=True, hard=False)
    return [_encode_open(tags[i], lits[i], f"{prefix}_{i}_e.png", beauties[i], orcos[i]) for i in range(n)]

# central catch poses: (filename in source3d, frame) -> low / mid / high
KEEPER_CATCH = {323: ("Goalkeeper Catch Low.fbx", 19),    # low  (ground gather) - owner pick
                328: ("Goalkeeper Catch.fbx", 13),         # mid  (chest gather) - owner pick
                354: ("Goalkeeper Catch High.fbx", 28)}    # high (overhead reach) - owner pick

def cmd_keeper(idle_fbx, dive_fbx, catch_fbx=None, ndive=None, lit_samples=None):
    bpy = __import__("bpy")
    ndive = int(ndive) if ndive else 14
    lit_samples = int(lit_samples) if lit_samples else 12
    srcd = os.path.dirname(idle_fbx)
    frames = {}
    # --- idle: fit + lock camera, detail pass ---
    arm, meshes = _import_clean(bpy, idle_fbx)
    idle_fr = frame_range(arm)[0] + 5             # owner pick: Catch f6 (clip starts at f1)
    mn, mx = world_bbox(meshes)
    cam, emp = make_ortho_cam(bpy, (mn + mx) / 2, KEEPER_AZ, KEEPER_EL, mx.z - mn.z)
    fit_camera(bpy, cam, emp, KEEPER_RES, idle_fr, KEEPER_IDLE_TGT)
    st = cam_state(cam, emp)
    frames[1] = _render_clip_frames(bpy, arm, meshes, cam, [idle_fr], "kidle", lit_samples, detail=True)[0]
    # --- dive (flat, fast motion) -> dive_left 50..99, mirror for dive_right 100..149 ---
    arm2, meshes2 = _import_clean(bpy, dive_fbx)
    mn2, mx2 = world_bbox(meshes2)
    cam2, emp2 = make_ortho_cam(bpy, (mn2 + mx2) / 2, KEEPER_AZ, KEEPER_EL, mx2.z - mn2.z)
    apply_cam_state(cam2, emp2, st)
    lo, hi = KEEPER_DIVE_FRAMES                         # owner pick: Diving Save f7..f57
    clip_frames = [int(round(lo + (hi - lo) * i / (ndive - 1))) for i in range(ndive)]
    dive_imgs = _render_clip_frames(bpy, arm2, meshes2, cam2, clip_frames, "kdive", lit_samples, detail=True)
    for j in range(50):
        idx = round(j / 49 * (ndive - 1))
        frames[50 + j] = dive_imgs[idx]                   # dive_left = screen-left (clip dives left)
        frames[100 + j] = _mirror_canvas(dive_imgs[idx]) # dive_right = mirror
    # --- central catches (low/mid/high) from their own clips, re-centred on the feet anchor ---
    for fn, (fname, cfr) in KEEPER_CATCH.items():
        arm_c, meshes_c = _import_clean(bpy, os.path.join(srcd, fname))
        mnc, mxc = world_bbox(meshes_c)
        cam_c, emp_c = make_ortho_cam(bpy, (mnc + mxc) / 2, KEEPER_AZ, KEEPER_EL, mxc.z - mnc.z)
        apply_cam_state(cam_c, emp_c, st)
        bpy.context.scene.frame_set(cfr)
        recenter_feet(bpy, cam_c, emp_c, KEEPER_RES, (600, 394))   # keeper feet -> unified (300,197)
        frames[fn] = _render_clip_frames(bpy, arm_c, meshes_c, cam_c, [cfr], f"kc{fn}", lit_samples, detail=True)[0]
    _pack_keeper(frames)

if __name__ == "__main__":
    # When launched via `blender -b -P render_sprites.py -- <args>`, the real args
    # follow the "--" separator; under plain python they follow argv[0].
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    cmd = argv[0] if argv else "test"
    if cmd == "probe": cmd_probe(argv[1])
    elif cmd == "test": cmd_test()
    elif cmd == "striker": cmd_striker(argv[1], argv[2])
    elif cmd == "strikersheet": cmd_striker_sheet(argv[1], argv[2])
    elif cmd == "defender": cmd_defender(argv[1], argv[2] if len(argv) > 2 else None)
    elif cmd == "defendersheet": cmd_defender_sheet(argv[1])
    elif cmd == "keeper": cmd_keeper(*argv[1:])
    elif cmd == "ball": cmd_ball()
    else: print("unknown command:", cmd)
