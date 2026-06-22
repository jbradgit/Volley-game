"""Procedural football-kit pattern generator for the 3D striker shirt.

Builds per-region materials for `Ch38_Shirt` and assigns them to its slots.
Region = material slot:  0 torso, 1 sleeve, 2 cuff, 3 collar.

Projection per region (chosen so patterns stay welded to the fabric when the
rig is posed/animated):
  * torso  -> Generated (orco) coords  : planar, pose-stable
  * sleeve -> the `Kit_UV` map          : the unwrapped arm cylinder
Collar and cuff are always solid.

Patterns
  torso  : solid | vstripes | hoops | quarters | halfhalf
  sleeve : solid | vstripes | hoops | sidecolor
Sleeve `hoops` are auto width-matched and shoulder-aligned to the torso hoops.
`halfhalf` torso + `sidecolor` sleeve gives the opposing-sleeve scheme
(left torso c1 / right torso c2  ->  left sleeve c2 / right sleeve c1).

Usage (inside Blender):
    import kit_patterns
    kit_patterns.apply_kit(bpy.data.objects["Ch38_Shirt"],
                           torso="vstripes", sleeve="vstripes",
                           c1=(0.72,0.07,0.09), c2=(0.09,0.13,0.46))
"""
import bpy
from mathutils import Vector

UV_NAME = "Kit_UV"
SHOULDER_Y = 146.5          # local height of the shoulder line (alignment ref)


# --------------------------------------------------------------------------- #
#  geometry constants (computed from the mesh each call -- cheap)
# --------------------------------------------------------------------------- #
def _constants(shirt):
    me = shirt.data
    vs = me.vertices
    xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]
    bminx, bsx = min(xs), max(xs) - min(xs)
    bminy, bsy = min(ys), max(ys) - min(ys)
    gx = lambda x: (x - bminx) / bsx
    gy = lambda y: (y - bminy) / bsy

    tvi = {i for p in me.polygons if p.material_index == 0 for i in p.vertices}
    tgx = [gx(vs[i].co.x) for i in tvi]; tgy = [gy(vs[i].co.y) for i in tvi]
    ty  = [vs[i].co.y for i in tvi]

    # arm axis from the armature if present, else principal X
    p0 = Vector((19.198, 142.593, -2.832)); p1 = Vector((68.093, 142.297, -3.659))
    arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'
                and any("LeftArm" in b.name for b in o.data.bones)), None)
    if arm:
        gb = lambda n: next((b for b in arm.data.bones if b.name.endswith(n)), None)
        ba, bh = gb("LeftArm"), gb("LeftHand")
        if ba and bh:
            p0, p1 = ba.head_local.copy(), bh.head_local.copy()
    a = (p1 - p0).normalized()

    # measure ONE arm only (p0/axis are the left arm) so the ring width matches the torso
    svi = {i for p in me.polygons if p.material_index in (1, 2) and p.center.x > 0 for i in p.vertices}
    tarr = [(vs[i].co - p0).dot(a) for i in svi]
    tr = (max(tarr) - min(tarr)) or 1.0

    kitd = me.uv_layers[UV_NAME].data
    uL = []; vL = []; uR = []; vR = []
    for p in me.polygons:
        if p.material_index in (1, 2):
            side = p.center.x > 0
            for li in p.loop_indices:
                uv = kitd[li].uv
                (uL if side else uR).append(uv.x)
                (vL if side else vR).append(uv.y)

    return dict(
        TGXc=(min(tgx) + max(tgx)) / 2, TGXr=max(tgx) - min(tgx),
        TGYc=(min(tgy) + max(tgy)) / 2, TGYr=max(tgy) - min(tgy),
        Theight=max(ty) - min(ty), GYsh=gy(SHOULDER_Y), SGXc=gx(0.0),
        uext=((max(uL) - min(uL)) + (max(uR) - min(uR))) / 2, uoff=min(min(uL), min(uR)),
        vext=((max(vL) - min(vL)) + (max(vR) - min(vR))) / 2, voff=min(min(vL), min(vR)),
        tr=tr,
    )


# --------------------------------------------------------------------------- #
#  node helpers
# --------------------------------------------------------------------------- #
def _M(nt, op, a, b=None, bv=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    nt.links.new(a, n.inputs[0])
    if b is not None:  nt.links.new(b, n.inputs[1])
    if bv is not None: n.inputs[1].default_value = bv
    return n.outputs[0]

def _ramp(nt, fac, A, B):
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = 'CONSTANT'
    e = rp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*A, 1)
    e[1].position = 0.5; e[1].color = (*B, 1)
    nt.links.new(fac, rp.inputs[0]); return rp.outputs[0]

def _band(nt, c, period, off):
    # alternating 0/1 stripes of width `period`, symmetric about `off`
    return _M(nt, 'ABSOLUTE', _M(nt, 'MODULO',
              _M(nt, 'ROUND', _M(nt, 'DIVIDE', _M(nt, 'SUBTRACT', c, bv=off), bv=period)), bv=2.0))

def _base(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Roughness"].default_value = 0.62
    nt.links.new(b.outputs[0], o.inputs["Surface"])
    m["kit_region"] = name
    return m, nt, b

def _orco(nt):
    s = nt.nodes.new("ShaderNodeSeparateXYZ"); t = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(t.outputs["Generated"], s.inputs[0]); return s

def _kituv(nt):
    s = nt.nodes.new("ShaderNodeSeparateXYZ"); u = nt.nodes.new("ShaderNodeUVMap")
    u.uv_map = UV_NAME; nt.links.new(u.outputs["UV"], s.inputs[0]); return s


# --------------------------------------------------------------------------- #
#  region material builders
# --------------------------------------------------------------------------- #
def _torso(name, pat, c1, c2, count, k):
    m, nt, b = _base(name)
    if pat == 'solid':
        b.inputs["Base Color"].default_value = (*c1, 1); return m
    s = _orco(nt)
    if pat == 'vstripes':
        col = _ramp(nt, _band(nt, s.outputs["X"], k['TGXr'] / count, k['TGXc']), c1, c2)
    elif pat == 'hoops':
        col = _ramp(nt, _band(nt, s.outputs["Y"], k['TGYr'] / count, k['GYsh']), c1, c2)
    elif pat == 'halfhalf':
        col = _ramp(nt, _M(nt, 'GREATER_THAN', s.outputs["X"], bv=k['TGXc']), c2, c1)
    elif pat == 'quarters':
        fx = _M(nt, 'GREATER_THAN', s.outputs["X"], bv=k['TGXc'])
        fy = _M(nt, 'GREATER_THAN', s.outputs["Y"], bv=k['TGYc'])
        col = _ramp(nt, _M(nt, 'MODULO', _M(nt, 'ADD', fx, fy), bv=2.0), c1, c2)
    else:
        raise ValueError("torso pattern: " + pat)
    nt.links.new(col, b.inputs["Base Color"]); return m

def _sleeve(name, pat, c1, c2, count, torso_count, k):
    m, nt, b = _base(name)
    if pat == 'solid':
        b.inputs["Base Color"].default_value = (*c1, 1); return m
    if pat == 'sidecolor':                       # solid per arm (opposing scheme)
        s = _orco(nt)
        col = _ramp(nt, _M(nt, 'GREATER_THAN', s.outputs["X"], bv=k['SGXc']), c1, c2)
        nt.links.new(col, b.inputs["Base Color"]); return m
    s = _kituv(nt)
    if pat == 'vstripes':                        # lengthwise (constant-U)
        col = _ramp(nt, _band(nt, s.outputs["X"], k['uext'] / count, k['uoff']), c1, c2)
    elif pat == 'hoops':                         # rings (constant-V), width-matched to torso
        hv = (k['Theight'] / torso_count) * k['vext'] / k['tr']
        col = _ramp(nt, _band(nt, s.outputs["Y"], hv, k['voff']), c1, c2)
    else:
        raise ValueError("sleeve pattern: " + pat)
    nt.links.new(col, b.inputs["Base Color"]); return m

def _solidify(slot_mat, rgb):
    slot_mat.use_nodes = True
    bsdf = slot_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1)


# --------------------------------------------------------------------------- #
#  public entry point
# --------------------------------------------------------------------------- #
def apply_kit(shirt, torso="solid", sleeve="solid",
              c1=(0.72, 0.07, 0.09), c2=(0.09, 0.13, 0.46),
              torso_count=8, sleeve_count=10, collar=None, cuff=None):
    """Assign procedural kit materials to `shirt` (the Ch38_Shirt object)."""
    k = _constants(shirt)
    me = shirt.data
    me.materials[0] = _torso("KIT_Torso", torso, c1, c2, torso_count, k)
    me.materials[1] = _sleeve("KIT_Sleeve", sleeve, c1, c2, sleeve_count, torso_count, k)
    if collar is not None and len(me.materials) > 3:
        _solidify(me.materials[3], collar)
    if cuff is not None and len(me.materials) > 2:
        _solidify(me.materials[2], cuff)
    return shirt
