"""Build assets/teams.json for the 2025/26 Premier League (ratings from final position)."""
import json, re

# 2025/26 PL home kits + final positions (researched May 2026)
DATA = [
 ("Arsenal","red","white","white",1),
 ("Man City","skyblue","white","skyblue",2),
 ("Man Utd","red","white","black",3),
 ("Aston Villa","claret","white","skyblue",4),
 ("Liverpool","red","red","red",5),
 ("Bournemouth","red","black","black",6),
 ("Brighton","blue","blue","blue",7),
 ("Chelsea","blue","blue","white",8),
 ("Brentford","red","white","red",9),
 ("Sunderland","red","black","black",10),
 ("Newcastle","black","black","black",11),
 ("Everton","blue","white","blue",12),
 ("Fulham","white","black","white",13),
 ("Leeds","white","white","white",14),
 ("Crystal Palace","blue","red","blue",15),
 ("Nottm Forest","red","white","red",16),
 ("Spurs","white","navy","white",17),
 ("West Ham","claret","skyblue","claret",18),
 ("Burnley","claret","claret","skyblue",19),
 ("Wolves","gold","black","gold",20),
]
PALETTE = {"red":"#CC0000","white":"#FFFFFF","blue":"#003399","black":"#1A1A1A",
 "yellow":"#FFC633","grey":"#CCCCCC","green":"#006600","claret":"#7A0019",
 "skyblue":"#6CABDD","orange":"#FF9900","darkblue":"#1F2F77","navy":"#11203F",
 "gold":"#FDB913"}

def slug(n): return re.sub(r'[^A-Za-z0-9]','',n)
def rating(pos): return max(1, round(10 - (pos-1)*9/19))

STRIPED = {"Newcastle":"white","Brighton":"white","Sunderland":"white"}  # vertical-stripe shirts
teams=[]
for name,shirt,shorts,socks,pos in DATA:
    t={"slug":slug(name),"name":name,"rating":rating(pos),"type":"plain",
        "shirt":shirt,"shorts":shorts,"socks":socks,"socks_top":socks,"stripe":shirt,"sleeves":shirt,
        "position":pos}
    if name in STRIPED: t["pattern"]="stripes"; t["stripe2"]=STRIPED[name]
    teams.append(t)
json.dump({"palette":PALETTE,"teams":teams}, open("assets/teams.json","w"), indent=1)
print("wrote assets/teams.json:", len(teams), "teams")
for t in teams: print("  %-14s r%-2d %s/%s/%s"%(t["name"],t["rating"],t["shirt"],t["shorts"],t["socks"]))
