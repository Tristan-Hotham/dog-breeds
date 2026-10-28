"""Breed table: Wikidata dog breeds joined to the FCI nomenclature and English Wikipedia infoboxes.

Origin used on the map, in order of preference:
  1. FCI country of origin (breeds the FCI recognises), the international stud-book standard;
  2. Wikidata country of origin (P495) mapped to a present-day country;
  3. English Wikipedia infobox "country" field (first country named).
Every breed keeps all three where they exist, and a flag where FCI and Wikidata disagree.
Output: data/breeds.csv, data/breeds.json (page), data/origin_disagreements.csv
"""
import csv, re
from collections import Counter, defaultdict
from common import *

wd = jload(f"{RAW}/dogs_wikidata_bundle.json.gz")
fci = jload(f"{RAW}/dogs_fci.json.gz")["breeds"]
ib2p = f"{RAW}/dogs_enwiki_infobox.json.gz"
ib2 = jload(ib2p)["pages"] if os.path.exists(ib2p) else {}
geo = jload(f"{DATA}/countries_geo.json")
E = wd["ents"]

# historical or sub-national origins in Wikidata mapped to a present-day country (region kept as a note)
HIST = {"Q21": "GBR", "Q22": "GBR", "Q25": "GBR", "Q38272": "GBR", "Q435405": "GBR", "Q17252": "CHN", "Q29520": "CHN",
        "Q43287": "DEU", "Q11772": "GRC", "Q11266977": "GRC", "Q1747689": "ITA", "Q4951156": "ITA", "Q8828": "ESP",
        "Q52631": "ESP", "Q52636": "ESP", "Q5813": "ESP", "Q327": "FRA", "Q797": "USA", "Q5428": "RUS", "Q6605": "RUS",
        "Q22502": "TWN", "Q217169": "ZWE", "Q22890": "IRL", "Q3348614": "BGD", "Q15180": "RUS", "Q33946": "CZE",
        "Q1183": "PRI", "Q1246": "XKX", "Q4628": "FRO", "Q223": "GRL"}
SUBNAT = {"Q21": "England", "Q22": "Scotland", "Q25": "Wales", "Q17252": "Tibet", "Q8828": "Mallorca", "Q52631": "Ibiza",
          "Q52636": "Menorca", "Q5813": "Canary Islands", "Q327": "Brittany", "Q797": "Alaska", "Q5428": "Siberia",
          "Q6605": "Sakha", "Q4951156": "Sicily", "Q22502": "Taiwan", "Q15180": "Soviet Union", "Q33946": "Czechoslovakia",
          "Q43287": "German Empire", "Q11772": "Ancient Greece", "Q11266977": "Epirus", "Q1747689": "Ancient Rome"}


def wd_iso(q):
    if q in HIST:
        return HIST[q]
    e = E.get(q) or {}
    iso = e.get("iso3")
    if iso == "SUN":
        return "RUS"
    if iso == "CSK":
        return "CZE"
    return iso


FCI_ISO = {"GREAT BRITAIN": "GBR", "ENGLAND": "GBR", "FRANCE": "FRA", "GERMANY": "DEU", "ITALY": "ITA", "SPAIN": "ESP",
           "JAPAN": "JPN", "UNITED STATES OF AMERICA": "USA", "RUSSIAN FEDERATION": "RUS", "SWITZERLAND": "CHE",
           "PORTUGAL": "PRT", "HUNGARY": "HUN", "THE NETHERLANDS": "NLD", "SWEDEN": "SWE", "IRELAND": "IRL", "BELGIUM": "BEL",
           "NORWAY": "NOR", "AUSTRIA": "AUT", "AUSTRALIA": "AUS", "POLAND": "POL", "CROATIA": "HRV", "FINLAND": "FIN",
           "BRAZIL": "BRA", "CZECH REPUBLIC": "CZE", "CHINA": "CHN", "TIBET (CHINA)": "CHN", "ROMANIA": "ROU", "SLOVAKIA": "SVK",
           "MOROCCO": "MAR", "DENMARK": "DNK", "CANADA": "CAN", "MEXICO": "MEX", "SERBIA": "SRB", "THAILAND": "THA",
           "AFGHANISTAN": "AFG", "INDONESIA": "IDN", "MALI": "MLI", "CENTRAL AFRICA": "COD", "CUBA": "CUB",
           "BOSNIA AND HERZEGOVINA": "BIH", "ISRAEL": "ISR", "CZECHOSLOVAKIA": "CZE", "URUGUAY": "URY", "MADAGASCAR": "MDG",
           "MONTENEGRO": "MNE", "ARGENTINA": "ARG", "ESTONIA": "EST", "GREENLAND": "GRL", "GREECE": "GRC", "ICELAND": "ISL",
           "NORTH MACEDONIA": "MKD", "TURKEY": "TUR", "KAZAKHSTAN": "KAZ", "KOREA (REPUBLIC OF)": "KOR", "SLOVENIA": "SVN",
           "COLOMBIA": "COL", "BULGARIA": "BGR", "UKRAINE": "UKR", "LITHUANIA": "LTU", "PERU": "PER", "SOUTH AFRICA": "ZAF",
           "LATVIA": "LVA", "GEORGIA": "GEO", "ALBANIA": "ALB", "CHILE": "CHL", "ALGERIA": "DZA", "TUNISIA": "TUN",
           "WESTERN MEDITERRANEAN BASIN": None, "CENTRAL MEDITERRANEAN BASIN": None, "MIDDLE EAST": None, "NORTHERN RUSSIA": "RUS", "SIBERIA": "RUS", "FCI": None, "TAIWAN": "TWN", "IRAN": "IRN", "MALTA": "MLT"}


def parse_fci(b):
    raw = b["country"]
    pat = None
    m = re.match(r"(.*?) Country of patronage of the breed (.*)", raw)
    if m:
        raw, pat = m.group(1), m.group(2)
    dev = None
    m = re.search(r"Country of development of the breed (.*)", b["status"] or "")
    if m:
        dev = m.group(1).strip()
    status = "provisional" if "provisional" in (b["status"] or "") else "definitive"
    origins = [s.strip() for s in raw.split(",")]
    isos = [FCI_ISO.get(s.upper()) for s in origins]
    for s, i in zip(origins, isos):
        if i is None and s.upper() not in ("WESTERN MEDITERRANEAN BASIN", "CENTRAL MEDITERRANEAN BASIN", "MIDDLE EAST"):
            print("FCI country not mapped:", s)
    eng = b["page"].rsplit("-", 1)[0].replace("-", " ").title()
    return dict(fci_num=b["num"], fci_name=b["name"].title(), fci_name_en=eng, fci_group=int(b["group"]), fci_group_name=b["groupName"],
                fci_section=b["section"], fci_status=status, fci_country=raw.title(), fci_iso=[i for i in isos if i],
                fci_patronage=(pat or "").title(), fci_development=(dev or "").title(), fci_accept=b["accept"])


F = {b["num"]: parse_fci(b) for b in fci}
FBYNAME = {}
for n, f in F.items():
    for k in (f["fci_name_en"], f["fci_name"]):
        FBYNAME.setdefault(norm(k), n)
FMANUAL = {"German Shepherd": 166, "Afghan Hound": 228, "Akita Inu": 255, "Bichon Frise": 215, "Airedale Terrier": 7,
           "Scottish Terrier": 73, "Schipperke": 83, "Saluki": 269, "Samoyed": 212, "Alaskan Malamute": 243,
           "Affenpinscher": 186, "Sealyham Terrier": 74, "Kintamani": 362, "Ariege Pointer": 177, "Campeiro Bulldog": 374,
           "Bohemian Shepherd": 364, "Yugoslavian Shepherd Dog": 41, "Macedonian Karaman": 378, "Schapendoes": 313,
           "Russo-European Laika": 304, "Saarloos Wolfdog": 311, "Shiba Inu": 257, "Shikoku Ken": 319, "Slovak Cuvac": 142,
           "Småland Hound": 129, "Smaland Hound": 129, "Styrian Coarse-haired Hound": 62, "Finnish Lapphund": 189,
           "Schweizerischer Niederlaufhund": 60}
used_fci = set()

# English Wikipedia infobox fields
def ibfield(box, key):
    m = re.search(r"\|[ \t]*" + key + r"[ \t]*=[ \t]*(.*)", box or "")
    if not m:
        return ""
    v = m.group(1)
    v = re.sub(r"\{\{(?:r|ref|efn|sfn|refn)\|[^{}]*\}\}", "", v, flags=re.I)
    v = re.sub(r"<ref[^>]*/>|<ref.*?</ref>|<ref.*", "", v)
    v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", v)
    v = re.sub(r"\{\{(?:flagcountry|flag|flagu|flagicon)\|([^|}]*)[^}]*\}\}", r"\1", v, flags=re.I)
    v = re.sub(r"\{\{[^{}]*\}\}", "", v)
    v = re.sub(r"<br\s*/?>", "; ", v)
    v = re.sub(r"<[^>]+>", "", v).strip(" ;,")
    return v


enib = {}
for t, v in wd["enwiki"]["ib"].items():
    enib[t] = {"box": v["box"], "lead": v.get("lead", "")}
for t, v in ib2.items():  # second, wider fetch (all pages using the infobox template), takes precedence
    enib[t] = {"box": v["box"], "lead": v.get("lead") or enib.get(t, {}).get("lead", ""), "qid": v.get("qid")}
norm_red = wd["enwiki"]["norm"]

COUNTRY_WORDS = {g["name"]: iso for iso, g in geo.items() if g.get("name")}
COUNTRY_WORDS.update({"United Kingdom": "GBR", "England": "GBR", "Scotland": "GBR", "Wales": "GBR", "Great Britain": "GBR",
                      "UK": "GBR", "Britain": "GBR", "United States": "USA", "USA": "USA", "Tibet": "CHN", "China": "CHN",
                      "Russia": "RUS", "Soviet Union": "RUS", "Czech Republic": "CZE", "Czechia": "CZE", "Ireland": "IRL",
                      "Republic of Ireland": "IRL", "Germany": "DEU", "Holland": "NLD", "Netherlands": "NLD", "South Korea": "KOR",
                      "Korea": "KOR", "Japan": "JPN", "Taiwan": "TWN", "Bosnia and Herzegovina": "BIH", "Serbia": "SRB",
                      "Congo": "COD", "Democratic Republic of the Congo": "COD", "Ivory Coast": "CIV", "Turkey": "TUR",
                      "Türkiye": "TUR", "Iran": "IRN", "Mexico": "MEX", "Brazil": "BRA", "North Macedonia": "MKD"})


def first_country(txt):
    best = None
    for w, iso in COUNTRY_WORDS.items():
        m = re.search(r"\b" + re.escape(w) + r"\b", txt)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), iso)
    return best[1] if best else None


breeds = []
EXCL = {"Q13406463", "Q4167410", "Q17362920", "Q1301464", "Q22990839", "Q3329412", "Q1146306"}  # list, disambig, duplicate, crossbreed, jackal-dog, ...
for b in wd["breeds"]:
    q = b["b"]
    cls = set(filter(None, b["classes"].split("|")))
    d = wd["det"].get(q, {})
    title = ""
    if b["enwiki"]:
        title = b["enwiki"].strip("<>").split("/wiki/")[-1]
        from urllib.parse import unquote
        title = unquote(title).replace("_", " ")
        title = norm_red.get(title, title)
    ib = enib.get(title, {})
    if not ib:
        for t, v in ib2.items():
            if v.get("qid") == q:
                ib, title = enib[t], t
                break
    box = ib.get("box", "")
    fnums = [int(x) for x in b["fci"].split("|") if x.strip().isdigit()]
    fn = fnums[0] if fnums and fnums[0] in F else None
    if fn is None:
        for k in (b["label"], title):
            if k and norm(k) in FBYNAME:
                fn = FBYNAME[norm(k)]; break
    if fn is None:
        for k in (b["label"], title):
            if k in FMANUAL or norm(k) in {norm(x) for x in FMANUAL}:
                fn = FMANUAL.get(k) or {norm(x): v for x, v in FMANUAL.items()}[norm(k)]; break
    if fn in used_fci:
        fn = None
    f = F.get(fn) if fn else None
    if fn:
        used_fci.add(fn)
    wdc = [x for x in b["countries"].split("|") if x]
    wd_isos = sorted({wd_iso(x) for x in wdc if wd_iso(x)})
    sub = [SUBNAT[x] for x in wdc if x in SUBNAT]
    ib_country = ibfield(box, "country") or ibfield(box, "origin")
    ib_iso = first_country(ib_country) if ib_country else None
    extinct = "Q237350" in cls or bool(ibfield(box, "extinct"))
    cross = bool(cls & {"Q1301464", "Q3329412", "Q1146306"}) or "crossbreed" in (d.get("desc") or "").lower()
    excluded = (bool(cls & EXCL) or cross) and not f or (b["label"] or "").startswith("List of")
    if f and f["fci_iso"]:
        origin, src = f["fci_iso"][0], "FCI"
    elif wd_isos:
        origin, src = (wd_isos[0] if len(wd_isos) == 1 else sorted(wd_isos, key=lambda i: -sum(wd_iso(x) == i for x in wdc))[0]), "Wikidata"
    elif ib_iso:
        origin, src = ib_iso, "Wikipedia infobox"
    else:
        origin, src = None, ""
    # mass and height from Wikidata where recorded (kg, cm)
    def qty(prop, unit_ok):
        vals = []
        for s in d.get(prop, []):
            v = s.get("v") or {}
            if not isinstance(v, dict) or "amount" not in v:
                continue
            u = v.get("unit", "").rsplit("/", 1)[-1]
            a = float(v["amount"])
            if u in unit_ok:
                vals.append(a * unit_ok[u])
        return round(sum(vals) / len(vals), 1) if vals else None
    mass = qty("P2067", {"Q11570": 1, "Q100995": 0.4536})
    height = qty("P2048", {"Q174728": 1, "Q11573": 100, "Q218593": 2.54})
    disagree = bool(f and f["fci_iso"] and wd_isos and not set(f["fci_iso"]) & set(wd_isos))
    nm = b["label"] or (f["fci_name_en"] if f else title)
    if nm and nm == nm.lower():
        nm = re.sub(r"\s*\(.*?\)$", "", title) if title and title.lower().startswith(nm[:4]) else nm[0].upper() + nm[1:]
    breeds.append(dict(qid=q, name=nm, enwiki=title, sitelinks=int(b["sitelinks"] or 0),
                       fci_num=f["fci_num"] if f else "", fci_name=f["fci_name"] if f else "", fci_group=f["fci_group"] if f else "",
                       fci_group_name=f["fci_group_name"] if f else "", fci_status=f["fci_status"] if f else "",
                       fci_country=f["fci_country"] if f else "", fci_patronage=f["fci_patronage"] if f else "",
                       fci_development=f["fci_development"] if f else "", wd_origin="|".join(wd_isos),
                       wd_origin_detail="|".join(sub), enwiki_country=ib_country, enwiki_iso=ib_iso or "",
                       origin_iso3=origin or "", origin_source=src, fci_wd_disagree=int(disagree), akc_id=b["akc"],
                       extinct=int(extinct), excluded=int(excluded), mass_kg=mass if mass is not None else "",
                       height_cm=height if height is not None else "", image=b["image"].strip("<>").split("FilePath/")[-1] if b["image"] else ""))

# Breeds Wikidata types as a variety rather than a breed, but kennel clubs register separately
EXTRA = [dict(qid="Q39579", name="Pomeranian", enwiki="Pomeranian dog", origin="DEU",
              note="FCI recognises the Pomeranian as a size of the German Spitz (no. 97, Germany); Wikidata types it as a dog variety")]
for e in EXTRA:
    breeds.append(dict(qid=e["qid"], name=e["name"], enwiki=e["enwiki"], sitelinks=0, fci_num="", fci_name="", fci_group=5,
                       fci_group_name="Spitz and primitive types", fci_status="", fci_country="Germany (as German Spitz)",
                       fci_patronage="", fci_development="", wd_origin="", wd_origin_detail="", enwiki_country="", enwiki_iso="",
                       origin_iso3=e["origin"], origin_source="FCI (German Spitz)", fci_wd_disagree=0, akc_id="pomeranian", extinct=0,
                       excluded=0, mass_kg="", height_cm="", image=""))

# FCI breeds that did not match a Wikidata item by FCI number
have = {x["fci_num"] for x in breeds if x["fci_num"] != ""}
missing = [n for n in F if n not in have]
print("FCI numbers not on any Wikidata breed:", len(missing), [F[n]["fci_name_en"] for n in missing][:40])
for n in missing:
    f = F[n]
    breeds.append(dict(qid="", name=f["fci_name_en"], enwiki="", sitelinks=0, fci_num=n, fci_name=f["fci_name"], fci_group=f["fci_group"],
                       fci_group_name=f["fci_group_name"], fci_status=f["fci_status"], fci_country=f["fci_country"],
                       fci_patronage=f["fci_patronage"], fci_development=f["fci_development"], wd_origin="", wd_origin_detail="",
                       enwiki_country="", enwiki_iso="", origin_iso3=f["fci_iso"][0] if f["fci_iso"] else "", origin_source="FCI",
                       fci_wd_disagree=0, akc_id="", extinct=0, excluded=0, mass_kg="", height_cm="", image=""))

# study set: recognised by the FCI, or with an English Wikipedia article; not crossbreeds, lists or extinct
for x in breeds:
    x["in_study"] = int(not x["excluded"] and not x["extinct"] and bool(x["origin_iso3"]) and (x["fci_num"] != "" or x["enwiki"] != ""))

for x in breeds:
    for k, v in x.items():
        if isinstance(v, str):
            x[k] = v.replace("\u2013", "-").replace("\u2014", "-")
cols = list(breeds[0].keys())
with open(f"{DATA}/breeds.csv", "w", newline="", encoding="utf-8") as fo:
    w = csv.DictWriter(fo, fieldnames=cols); w.writeheader(); w.writerows(sorted(breeds, key=lambda x: x["name"]))
dis = [x for x in breeds if x["fci_wd_disagree"]]
with open(f"{DATA}/origin_disagreements.csv", "w", newline="", encoding="utf-8") as fo:
    w = csv.DictWriter(fo, fieldnames=["qid", "name", "fci_num", "fci_country", "fci_patronage", "fci_development", "wd_origin", "wd_origin_detail", "enwiki_country"])
    w.writeheader(); [w.writerow({k: x[k] for k in w.fieldnames}) for x in sorted(dis, key=lambda x: x["name"])]
S = [x for x in breeds if x["in_study"]]
c = Counter(x["origin_iso3"] for x in S)
print(len(breeds), "rows;", len(S), "in study;", Counter(x["origin_source"] for x in S), "; disagreements", len(dis))
print(c.most_common(15))
