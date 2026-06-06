import xml.etree.ElementTree as ET

PATH = r"C:\Users\Office\Volley Game\decomp\swf.xml"
tree = ET.parse(PATH)
root = tree.getroot()

# Map characterId -> element for shapes and sprites
shapes = {}   # id -> (xmin,ymin,xmax,ymax) in twips
sprites = {}  # id -> element

def walk(el):
    for child in el:
        t = child.get("type")
        if t in ("DefineShapeTag","DefineShape2Tag","DefineShape3Tag","DefineShape4Tag"):
            sid = child.get("shapeId")
            sb = child.find("shapeBounds")
            if sid is not None and sb is not None:
                shapes[int(sid)] = (float(sb.get("Xmin")), float(sb.get("Ymin")),
                                    float(sb.get("Xmax")), float(sb.get("Ymax")))
        elif t in ("DefineSpriteTag",):
            sid = child.get("spriteId")
            if sid is not None:
                sprites[int(sid)] = child
        elif t in ("DefineMorphShapeTag","DefineMorphShape2Tag"):
            sid = child.get("characterId") or child.get("shapeId")
            sb = child.find("startBounds") or child.find("shapeBounds")
            if sid is not None and sb is not None:
                shapes[int(sid)] = (float(sb.get("Xmin")), float(sb.get("Ymin")),
                                    float(sb.get("Xmax")), float(sb.get("Ymax")))
        walk(child)

walk(root)

memo = {}
def bounds(cid, lvl=0):
    if cid in memo: return memo[cid]
    if lvl > 30: return None
    if cid in shapes:
        memo[cid] = shapes[cid]; return shapes[cid]
    if cid in sprites:
        sp = sprites[cid]
        sub = sp.find("subTags")
        bx0=by0=1e18; bx1=by1=-1e18; found=False
        depthChar = {}   # depth -> current characterId (track display list across frames incl. move tags)
        if sub is not None:
            for item in sub:
                t = item.get("type")
                if t == "RemoveObject2Tag" or t == "RemoveObjectTag":
                    depthChar.pop(item.get("depth"), None); continue
                if t not in ("PlaceObject2Tag","PlaceObject3Tag"): continue
                depth = item.get("depth")
                ccid = item.get("characterId")
                if ccid is not None: depthChar[depth] = int(ccid)
                cur = depthChar.get(depth)
                if cur is None: continue
                m = item.find("matrix")
                if m is None: continue          # move with no matrix change -> skip (no new extent)
                cb = bounds(cur, lvl+1)
                if cb is None: continue
                sx=float(m.get("scaleX") or 1.0); sy=float(m.get("scaleY") or 1.0)
                r0=float(m.get("rotateSkew0") or 0.0); r1=float(m.get("rotateSkew1") or 0.0)
                tx=float(m.get("translateX") or 0.0); ty=float(m.get("translateY") or 0.0)
                if not (m.get("hasScale")=="true"): sx=sy=1.0
                for X in (cb[0],cb[2]):
                    for Y in (cb[1],cb[3]):
                        px = sx*X + r1*Y + tx
                        py = r0*X + sy*Y + ty
                        bx0=min(bx0,px); by0=min(by0,py); bx1=max(bx1,px); by1=max(by1,py)
                        found=True
        res = (bx0,by0,bx1,by1) if found else None
        memo[cid]=res; return res
    return None

for cid,name in [(168,"keeper"),(91,"striker owen"),(152,"defender opp"),(143,"def man blue"),
                 (151,"def man red"),(122,"ball"),(124,"shadow"),(127,"bubble")]:
    b = bounds(cid)
    if b:
        xmin,ymin,xmax,ymax = b
        print(f"{name} (chid {cid}): bounds twips X[{xmin:.0f}..{xmax:.0f}] Y[{ymin:.0f}..{ymax:.0f}]  "
              f"=> px W={ (xmax-xmin)/20:.1f} H={(ymax-ymin)/20:.1f}  origin_in_png=({-xmin/20:.1f},{-ymin/20:.1f})")
    else:
        print(f"{name} (chid {cid}): no bounds")
