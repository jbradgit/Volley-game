"""Inject real-life-inspired HOME + AWAY kit specs into teams.json and world.json.

Kit spec (palette colour names): { p, c1, c2, sleeves, shorts, socks }
  p = solid | stripes | hoops | halves | quarters | sash   (c2 = pattern second colour)
Legacy top-level fields (shirt/shorts/...) are kept = home kit, so HUD theming,
ticker colours and kit swatches keep working untouched.

Run:  python3 artgen/gen_kits.py
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def K(p, c1, shorts, socks, c2=None, sleeves=None):
    k = {"p": p, "c1": c1, "shorts": shorts, "socks": socks}
    if c2: k["c2"] = c2
    if sleeves: k["sleeves"] = sleeves
    return k

KITS = {  # slug: (home, away) — early-2000s real-life inspired
 "Arsenal":       (K("solid","red","white","red",sleeves="white"),      K("solid","yellow","darkblue","yellow")),
 "AstonVilla":    (K("solid","claret","white","skyblue",sleeves="skyblue"), K("solid","white","claret","white")),
 "Bournemouth":   (K("stripes","red","black","black","black"),         K("solid","white","white","white")),
 "Brentford":     (K("stripes","red","black","red","white"),           K("solid","yellow","black","yellow")),
 "Brighton":      (K("stripes","blue","white","white","white"),        K("solid","yellow","blue","yellow")),
 "Burnley":       (K("solid","claret","white","claret",sleeves="skyblue"), K("solid","yellow","claret","yellow")),
 "Chelsea":       (K("solid","blue","blue","white"),                   K("solid","yellow","yellow","yellow")),
 "CrystalPalace": (K("stripes","red","blue","blue","blue"),            K("solid","white","white","white")),
 "Everton":       (K("solid","blue","white","white"),                  K("solid","yellow","grey","yellow")),
 "Fulham":        (K("solid","white","black","white"),                 K("solid","red","black","red")),
 "Leeds":         (K("solid","white","white","white"),                 K("solid","yellow","blue","yellow")),
 "Liverpool":     (K("solid","red","red","red"),                       K("solid","gold","black","gold")),
 "ManCity":       (K("solid","skyblue","white","navy"),                K("solid","black","black","black")),
 "ManUtd":        (K("solid","red","white","black"),                   K("solid","white","black","white")),
 "Newcastle":     (K("stripes","black","black","black","white"),       K("solid","gold","navy","gold")),
 "NottmForest":   (K("solid","red","white","red"),                     K("solid","white","white","white")),
 "Spurs":         (K("solid","white","navy","white"),                  K("solid","navy","navy","navy")),
 "Sunderland":    (K("stripes","red","black","red","white"),           K("solid","navy","navy","navy")),
 "WestHam":       (K("solid","claret","white","claret",sleeves="skyblue"), K("solid","skyblue","skyblue","skyblue")),
 "Wolves":        (K("solid","gold","black","gold"),                   K("solid","black","black","black")),
 # europe
 "RealMadrid":    (K("solid","white","white","white"),                 K("solid","navy","navy","navy")),
 "Barcelona":     (K("stripes","blue","darkblue","darkblue","claret"), K("solid","yellow","yellow","yellow")),
 "Valencia":      (K("solid","white","black","white"),                 K("solid","orange","orange","orange")),
 "Deportivo":     (K("stripes","blue","navy","blue","white"),          K("solid","red","red","red")),
 "Juventus":      (K("stripes","white","white","black","black"),       K("solid","navy","navy","navy")),
 "ACMilan":       (K("stripes","red","white","black","black"),         K("solid","white","white","white")),
 "InterMilan":    (K("stripes","blue","black","black","black"),        K("solid","white","white","white")),
 "Roma":          (K("solid","claret","white","claret",sleeves="orange"), K("solid","white","white","white")),
 "BayernMunich":  (K("solid","red","red","red"),                       K("solid","white","navy","white")),
 "Dortmund":      (K("solid","yellow","black","yellow"),               K("solid","black","black","black")),
 "Leverkusen":    (K("solid","red","black","red"),                     K("solid","white","white","white")),
 "Lyon":          (K("solid","white","white","white",sleeves="blue"),  K("solid","navy","navy","navy")),
 "Monaco":        (K("halves","red","white","white","white"),          K("solid","white","red","white")),
 "Marseille":     (K("solid","white","white","white",sleeves="skyblue"), K("solid","skyblue","white","skyblue")),
 "Porto":         (K("stripes","blue","blue","white","white"),         K("solid","white","white","white")),
 "Ajax":          (K("stripes","white","white","white","red"),         K("solid","navy","navy","navy")),
 "Celtic":        (K("hoops","green","white","white","white"),         K("solid","yellow","green","yellow")),
 "PSG":           (K("stripes","darkblue","darkblue","darkblue","red"), K("solid","white","white","white")),
 # nations
 "Brazil":        (K("solid","yellow","blue","white"),                 K("solid","blue","white","blue")),
 "France":        (K("solid","darkblue","white","red"),                K("solid","white","white","white")),
 "Argentina":     (K("stripes","skyblue","black","white","white"),     K("solid","darkblue","black","darkblue")),
 "Italy":         (K("solid","blue","white","blue"),                   K("solid","white","white","white")),
 "Germany":       (K("solid","white","black","white"),                 K("solid","green","black","green")),
 "England":       (K("solid","white","navy","white"),                  K("solid","red","white","red")),
 "Spain":         (K("solid","red","navy","red"),                      K("solid","white","white","white")),
 "Portugal":      (K("solid","claret","green","claret"),               K("solid","white","white","white")),
 "Netherlands":   (K("solid","orange","white","orange"),               K("solid","darkblue","darkblue","darkblue")),
 "CzechRep":      (K("solid","red","white","blue"),                    K("solid","white","white","white")),
 "Sweden":        (K("solid","yellow","blue","yellow"),                K("solid","blue","yellow","blue")),
 "Denmark":       (K("solid","red","white","red"),                     K("solid","white","red","white")),
 "Ireland":       (K("solid","green","white","green"),                 K("solid","white","green","white")),
 "USA":           (K("solid","white","blue","white"),                  K("solid","darkblue","darkblue","darkblue")),
 "Scotland":      (K("solid","darkblue","white","darkblue"),           K("solid","yellow","darkblue","yellow")),
 "Japan":         (K("solid","blue","white","blue"),                   K("solid","white","blue","white")),
}

def derive(t):
    """Teams without a curated entry (minnows): home from legacy fields, plain away."""
    p = "stripes" if t.get("pattern") == "stripes" else "solid"
    h = K(p, t["shirt"], t.get("shorts","white"), t.get("socks", t["shirt"]),
          c2=t.get("stripe2"), sleeves=(t.get("sleeves") if t.get("sleeves") != t["shirt"] else None))
    a = K("solid", "white" if t["shirt"] != "white" else "red", "black", "white")
    return h, a

def apply(team):
    h, a = KITS.get(team["slug"]) or derive(team)
    team["kits"] = {"h": h, "a": a}

tj = json.load(open(os.path.join(ROOT, "assets/teams.json")))
for t in tj["teams"]: apply(t)
json.dump(tj, open(os.path.join(ROOT, "assets/teams.json"), "w"), indent=1)
wj = json.load(open(os.path.join(ROOT, "assets/world/world.json")))
for grp in ("euro", "nations", "minnows"):
    for t in wj[grp]: apply(t)
json.dump(wj, open(os.path.join(ROOT, "assets/world/world.json"), "w"), indent=1)
print("kits injected:", len(tj["teams"]), "league +", sum(len(wj[g]) for g in ("euro","nations","minnows")), "world")
