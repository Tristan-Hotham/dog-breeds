"""UK detail: Royal Kennel Club registrations 2016 to 2025 by breed (varieties added together), and where in Britain
the native breeds come from (hand-checked from English Wikipedia, with the sentence used kept as evidence).
Outputs: data/uk_trends.csv, data/uk_origins.csv
"""
import csv
from collections import defaultdict
from common import *

B = {r["qid"]: r for r in csv.DictReader(open(f"{DATA}/breeds.csv", encoding="utf-8")) if r["qid"]}
uk = jload(f"{DATA}/uk_registrations_2016_2025.json")
# map RKC names to breeds through the matched 2025 table (names_published lists every RKC name merged into a breed)
reg = [r for r in csv.DictReader(open(f"{DATA}/registrations.csv", encoding="utf-8")) if r["iso3"] == "GBR"]
name2q = {}
for r in reg:
    for n in r["names_published"].split("; "):
        name2q[n] = r["qid"]
ser = defaultdict(lambda: defaultdict(int))
for n, ys in uk.items():
    q = name2q.get(n)
    if not q:
        continue
    for y, c in ys.items():
        ser[q][int(y)] += c
years = list(range(2016, 2026))
tot = {y: sum(ser[q][y] for q in ser) for y in years}
rows = []
for q, ys in ser.items():
    rows.append(dict(qid=q, breed=B[q]["name"], origin_iso3=B[q]["origin_iso3"], **{str(y): ys.get(y, 0) for y in years}))
rows.sort(key=lambda r: -r["2025"])
with open(f"{DATA}/uk_trends.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["qid", "breed", "origin_iso3"] + [str(y) for y in years]); w.writeheader(); w.writerows(rows)
jsave({"totals": tot}, f"{TMP}/uk_totals.json")
print("UK totals", tot)
for r in rows[:12]:
    print(r["breed"], r["origin_iso3"], [r[str(y)] for y in years])

# ---- where in Britain: hand-checked from English Wikipedia (sentence kept as evidence; CC BY-SA 4.0) ----
from shapely.geometry import shape
from shapely.ops import unary_union
CTY = {f["properties"]["county"]: shape(f["geometry"]) for f in jload("/home/claude/hist/how-roman-is-your-road/data/counties.geojson")["features"]}
osn = {}
import csv as _csv
with open("/home/claude/hist/osnames_gb.tsv", encoding="utf-8") as f:
    for r in _csv.DictReader(f, delimiter="\t"):
        k = (r["name1"], r["local_type"])
        if k not in osn:
            osn[k] = (float(r["lat"]), float(r["lon"]))


def county(*names):
    g = unary_union([CTY[n] for n in names]).representative_point()
    return round(g.y, 4), round(g.x, 4), "county polygon: " + " + ".join(names) + " (ONS boundaries via how-roman-is-your-road)"


def place(name, lt):
    lat, lon = osn[(name, lt)]
    return round(lat, 4), round(lon, 4), f"OS Open Names: {name} ({lt})"


UKO = [
    ("Yorkshire Terrier", "Yorkshire", "England", county("North Yorkshire", "West Yorkshire", "South Yorkshire", "East Riding of Yorkshire"), "Wikipedia", "It originated in the nineteenth century in the English county of Yorkshire, after which it is named."),
    ("Airedale Terrier", "Airedale, West Riding of Yorkshire", "England", place("Airedale", "Valley"), "Wikipedia", "originated in the valley (dale) of the River Aire, in the West Riding of Yorkshire"),
    ("Bedlington Terrier", "Bedlington, Northumberland", "England", place("Bedlington", "Town"), "Wikipedia", "named after the mining town of Bedlington, Northumberland in North East England"),
    ("Border Collie", "Anglo-Scottish border", "England and Scotland", place("Carter Bar", "Hill Or Mountain"), "Wikipedia", "It originates in the region of the Anglo-Scottish border"),
    ("Border Terrier", "Anglo-Scottish border", "England and Scotland", place("Carter Bar", "Hill Or Mountain"), "Wikipedia", "It originates from the area of the Anglo-Scottish border"),
    ("Dandie Dinmont Terrier", "the Scottish Borders", "Scotland", county("Scottish Borders"), "Wikipedia", "The breed remained relatively unknown outside of the Borders until 1815"),
    ("Lakeland Terrier", "Lake District", "England", place("Keswick", "Town"), "Wikipedia", "takes its name from its place of origin, the Lake District in England"),
    ("Patterdale Terrier", "Patterdale, Lake District", "England", place("Patterdale", "Village"), "Wikipedia", "originally bred in Patterdale in the Lake District"),
    ("Pembroke Welsh Corgi", "Pembrokeshire", "Wales", (51.675, -4.9137, "OS Open Names: Penfro / Pembroke (Town)"), "Wikipedia", "a cattle herding dog breed that originated in Pembrokeshire, Wales"),
    ("Sussex Spaniel", "Sussex", "England", county("East Sussex", "West Sussex"), "Wikipedia", "a breed of dog native to Sussex, in southern England"),
    ("Norwich Terrier", "East Anglia (Norwich)", "England", place("Norwich", "City"), "Wikipedia infobox", "country = East Anglia, England"),
    ("West Country Harrier", "south-west England (Somerset)", "England", county("Somerset"), "Wikipedia", "sometimes called Somerset Harrier, is a breed of scent hound from the south west of England"),
    ("Welsh Terrier", "the mountains of north Wales", "Wales", county("Gwynedd"), "Wikipedia", "originally bred for hunting fox, rodents and badger; in the remote mountains of northern Wales"),
    ("Cairn Terrier", "Scottish Highlands", "Scotland", county("Highland"), "Wikipedia", "a terrier breed originating in the Scottish Highlands"),
    ("Shetland Sheepdog", "Shetland", "Scotland", place("Lerwick", "Town"), "Wikipedia", "a breed of herding dog that originated in the Shetland Islands of Scotland"),
    ("Golden Retriever", "Guisachan, Inverness-shire", "Scotland", place("Guisachan Forest", "Other Landcover"), "Wikipedia", "bred by Sir Dudley Marjoribanks at his Scottish estate Guisachan in the late nineteenth century"),
    ("Clumber Spaniel", "Clumber Park, Nottinghamshire", "England", place("Clumber Lake", "Inland Water"), "Wikipedia", "The name of the breed is taken from Clumber Park in Nottinghamshire where the breed was first developed."),
    ("Staffordshire Bull Terrier", "Staffordshire and north Birmingham", "England", county("Staffordshire"), "Wikipedia", "originated in the northern parts of Birmingham and in Staffordshire, for which it is named"),
    ("West Highland White Terrier", "Poltalloch, Argyll", "Scotland", county("Argyll and Bute"), "Wikipedia", "Edward Donald Malcolm, 16th Laird of Poltalloch, is credited with the creation of the modern breed from his Poltalloch Terrier"),
    ("Gordon Setter", "Gordon Castle, Moray", "Scotland", place("Fochabers", "Village"), "Wikipedia", "the setters at Gordon Castle during the Duke's time"),
]
byname = {b["name"]: q for q, b in B.items()}
t25 = {r["qid"]: r for r in rows}
out = []
for nm, plc, nation, (lat, lon, how), src, ev in UKO:
    q = byname.get(nm) or byname.get(nm.replace("Pembroke Welsh Corgi", "Pembroke Welsh Corgi"))
    assert q, nm
    out.append(dict(qid=q, breed=nm, place=plc, nation=nation, lat=lat, lon=lon, location_from=how,
                    evidence_source=f"English Wikipedia, {B[q]['enwiki'] or nm} ({src})", evidence=ev,
                    reg_2025=t25[q]["2025"] if q in t25 else "", reg_2016=t25[q]["2016"] if q in t25 else ""))
with open(f"{DATA}/uk_origins.csv", "w", newline="", encoding="utf-8") as f:
    w = _csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out), "UK breed birthplaces placed")
