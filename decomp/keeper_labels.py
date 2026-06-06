import xml.etree.ElementTree as ET
t = ET.parse(r"C:\Users\Office\Volley Game\decomp\swf.xml"); root = t.getroot()
def find_sprite(el, sid):
    for c in el:
        if c.get("type")=="DefineSpriteTag" and c.get("spriteId")==str(sid): return c
        r=find_sprite(c,sid)
        if r is not None: return r
    return None
for sid,name in [(168,"keeper"),(180,"goalnet"),(119,"crink"),(175,"peep")]:
    sp=find_sprite(root,sid);
    if sp is None: print(name,"not found"); continue
    sub=sp.find("subTags"); frame=1; labels=[]
    for it in sub:
        ty=it.get("type")
        if ty=="FrameLabelTag": labels.append((frame, it.get("name")))
        elif ty=="ShowFrameTag": frame+=1
    print(f"--- {name} (chid {sid}) total frames={frame-1} ---")
    for f,n in labels: print(f"   frame {f}: {n}")
