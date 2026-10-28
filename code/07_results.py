"""Every number used in the page, paper, blog and collage (data/results.json) and the page data (data/site.json)."""
import csv
from collections import Counter, defaultdict
from common import *

B = list(csv.DictReader(open(f"{DATA}/breeds.csv", encoding="utf-8")))
BQ = {b["qid"]: b for b in B if b["qid"]}
S = [b for b in B if b["in_study"] == "1"]
geo = jload(f"{DATA}/countries_geo.json")
pop = list(csv.DictReader(open(f"{DATA}/country_popularity.csv", encoding="utf-8")))
t10 = list(csv.DictReader(open(f"{DATA}/club_top10.csv", encoding="utf-8")))
reg = list(csv.DictReader(open(f"{DATA}/registrations.csv", encoding="utf-8")))
ukt = list(csv.DictReader(open(f"{DATA}/uk_trends.csv", encoding="utf-8")))
uko = list(csv.DictReader(open(f"{DATA}/uk_origins.csv", encoding="utf-8")))
langtop = jload(f"{DATA}/lang_top.json")
pvl = list(csv.DictReader(open(f"{DATA}/pageviews_by_language.csv", encoding="utf-8")))
fci = jload(f"{RAW}/dogs_fci.json.gz")["breeds"]
wd = jload(f"{RAW}/dogs_wikidata_bundle.json.gz")

cname = {iso: g["name"] for iso, g in geo.items()}
cname.update({"GBR": "the UK", "USA": "the United States", "NLD": "the Netherlands", "CZE": "Czechia", "COD": "DR Congo", "XKX": "Kosovo",
              "PRI": "Puerto Rico", "GRL": "Greenland", "FRO": "Faroe Islands", "TWN": "Taiwan"})
cname_plain = {k: v.replace("the ", "", 1) if v.startswith("the ") else v for k, v in cname.items()}
CAP = lambda iso: cname_plain.get(iso, iso)

R = {}
# ---- origins ----
oc = Counter(b["origin_iso3"] for b in S)
top = [{"iso": i, "name": CAP(i), "n": n} for i, n in oc.most_common(12)]
top[0]["name"] = "Britain" if top[0]["iso"] == "GBR" else top[0]["name"]
eur = sum(n for i, n in oc.items() if geo.get(i, {}).get("continent") == "Europe")
both = [b for b in S if b["fci_num"] and b["wd_origin"]]
fci_iso = {}
for b in both:
    pass
dis = [b for b in S if b["fci_wd_disagree"] == "1"]
extra = [b for b in both if b["fci_wd_disagree"] == "0" and len(b["wd_origin"].split("|")) > 1]
R["origins"] = dict(top=top, n_countries=len(oc), europe_share=eur / len(S), n_compared=len(both), n_disagree=len(dis), n_extra=len(extra),
                    src_fci=sum(b["origin_source"].startswith("FCI") for b in S), src_wd=sum(b["origin_source"] == "Wikidata" for b in S),
                    src_wp=sum(b["origin_source"] == "Wikipedia infobox" for b in S), by_country={i: n for i, n in oc.items()})
R["meta"] = dict(n_wd=len(wd["breeds"]), n_fci=len(fci), n_study=len(S), n_fci_study=sum(1 for b in S if b["fci_num"]),
                 n_origin_countries=len(oc), retrieved="28 October 2026")

# ---- clubs ----
clubs = [r for r in pop if r["basis"] == "club"]
R["meta"]["n_clubs"] = len(clubs)
abroad = [r for r in clubs if r["top_origin"] != r["iso3"]]
home_top = [r for r in clubs if r["top_origin"] == r["iso3"]]
by_iso_t10 = defaultdict(list)
for r in t10:
    by_iso_t10[r["iso3"]].append(r)
n10 = sum(len(v) for v in by_iso_t10.values()); n10_abroad = sum(1 for v in by_iso_t10.values() for r in v if r["origin_iso3"] != r["iso3"])
CLUBNAME = {r["iso3"]: r["source"] for r in clubs}
R["clubs"] = dict(n_top_abroad=len(abroad), n_top_gbr=sum(r["top_origin"] == "GBR" for r in abroad),
                  home_top_list=" and ".join(f"{cname[r['iso3']]} ({r['top_breed']})" for r in home_top) or "none",
                  top10_abroad_share=n10_abroad / n10, n_top10=n10,
                  list="; ".join(f"{r['source']} ({CAP(r['iso3'])}, {r['year']})" for r in sorted(clubs, key=lambda r: CAP(r['iso3']))),
                  top={r["iso3"]: dict(breed=r["top_breed"], origin=r["top_origin"], count=r["top_count"], source=r["source"], year=r["year"]) for r in clubs},
                  home={r["iso3"]: float(r["home_share"]) for r in clubs if r["home_share"] != ""})
# home-grown chart: shares by origin for full-count clubs
home_rows = []
for iso in ("GBR", "DEU", "AUS", "JPN"):
    rs = [r for r in reg if r["iso3"] == iso and r["count"] != ""]
    tot = sum(int(r["count"]) for r in rs)
    c = Counter()
    for r in rs:
        c[r["origin_iso3"] or "other"] += int(r["count"])
    parts = [[iso, c.pop(iso, 0) / tot]]
    for o, n in c.most_common():
        if n / tot >= 0.04 and o != "other":
            parts.append([o, n / tot])
    parts.append(["other", 1 - sum(p[1] for p in parts)])
    home_rows.append(dict(iso=iso, parts=[[a, round(b, 4)] for a, b in parts], total=tot))
R["clubs"]["totals"] = {h["iso"]: h["total"] for h in home_rows}
R["clubs"]["home_parts"] = {h["iso"]: {p[0]: p[1] for p in h["parts"]} for h in home_rows}

# ---- French Bulldog and other stories ----
def regq(iso, name):
    for r in reg:
        if r["iso3"] == iso and r["breed"] == name:
            return r
ukser = {r["breed"]: {int(y): int(r[y]) for y in r if y.isdigit()} for r in ukt}
fb = ukser["French Bulldog"]; lab = ukser["Labrador Retriever"]
pk = max(fb, key=fb.get)
R["frenchie"] = dict(uk_peak=fb[pk], uk_peak_year=str(pk), uk_2025=fb[2025], uk_drop=1 - fb[2025] / fb[pk], uk_2018=fb[2018], lab_2018=lab[2018],
                     uk_rank_2025=int(regq("GBR", "French Bulldog")["rank"]), jkc_rank=int(regq("JPN", "French Bulldog")["rank"]),
                     jkc_count=int(regq("JPN", "French Bulldog")["count"]), akc_rank=1, akc_years_top="fourth",
                     vdh_2025=int(regq("DEU", "French Bulldog")["count"]))
R["frenchie"]["uk_2018_overtook"] = fb[2018] > lab[2018]
R["frenchie"]["rise"] = fb[pk] / fb[2016]; R["frenchie"]["fall"] = fb[pk] / fb[2025]
R["uk"] = dict(n_points=len(uko), totals={str(y): sum(ukser[b][y] for b in ukser) for y in range(2016, 2026)},
               lab_2025=lab[2025], lab_2021=lab[2021], cocker_2025=ukser["English Cocker Spaniel"][2025],
               dachs_2016=ukser["Dachshund"][2016], dachs_2025=ukser["Dachshund"][2025])
# breeds that are number one somewhere other than at home
ones = defaultdict(list)
for r in clubs:
    ones[r["top_breed"]].append(r["iso3"])
R["number_ones"] = {k: v for k, v in ones.items()}

# ---- proxy and its check against clubs ----
LANGCOUNTRY_CHECK = {"ja": "JPN", "sv": "SWE", "fi": "FIN", "no": "NOR", "de": "DEU", "fr": "FRA"}
checks = []
for l, iso in LANGCOUNTRY_CHECK.items():
    if l in langtop and iso in CLUBNAME:
        pt = BQ[langtop[l]["top"]]["name"]; ct = R["clubs"]["top"][iso]["breed"]
        club3 = [r["breed"] for r in t10 if r["iso3"] == iso][:3]
        checks.append(dict(lang=l, iso=iso, proxy=pt, club=ct, match=pt == ct, in_club_top3=pt in club3))
R["proxy"] = dict(n_langs=len(langtop), checks=checks, n_match=sum(c["match"] for c in checks), n_check=len(checks),
                  n_in_top3=sum(c["in_club_top3"] for c in checks),
                  n_single=sum(r["basis"] == "proxy_single" for r in pop), n_shared=sum(r["basis"] == "proxy_shared" for r in pop))
LANGNAME_ALL = {r["lang"]: r["language"] for r in pvl}
LN = {"ja": "Japanese", "sv": "Swedish", "fi": "Finnish", "no": "Norwegian", "de": "German", "fr": "French"}
bits = [f"{LN[c['lang']]} Wikipedia's most read breed is the {c['proxy']}, " + ("which is also the club's number one" if c["match"] else
        (f"which is in the club's top three (the club's number one is the {c['club']})" if c["in_club_top3"] else f"while the club's number one is the {c['club']}")) for c in checks]
R["proxy"]["check_text"] = f"In {R['proxy']['n_check']} countries with both, the stand-in names the club's own number one in {R['proxy']['n_match']} and a club top-three breed in {R['proxy']['n_in_top3']}. " + "; ".join(bits) + ". So read the striped countries as a rough guide to which breeds people are curious about, not a census."
R["meta"]["n_langs"] = len(langtop)
from collections import Counter as _C
LC5 = __import__("importlib").import_module("05_popularity") if False else None
lang_c = defaultdict(list)
for r in pop:
    if r["lang"]: lang_c[r["lang"]].append(r["iso3"])
topc = _C(BQ[t["top"]]["name"] for t in langtop.values())
R["proxy"]["top_counts"] = dict(topc.most_common())
R["proxy"]["cane_n"] = topc.get("Cane Corso", 0)
R["proxy"]["en_top"] = BQ[langtop["en"]["top"]]["name"]
R["proxy"]["en_top_views"] = langtop["en"]["views12"]
own = {"ja": "JPN", "fi": "FIN", "is": "ISL", "tr": "TUR", "he": "ISR", "ka": "GEO", "hy": "ARM", "hu": "HUN", "it": "ITA", "fr": "FRA", "de": "DEU",
       "sv": "SWE", "no": "NOR", "da": "DNK", "nl": "NLD", "pl": "POL", "cs": "CZE", "sk": "SVK", "ru": "RUS", "es": "ESP", "pt": "PRT", "zh": "CHN", "ko": "KOR"}
home_ed = sorted(l for l, iso in own.items() if l in langtop and BQ[langtop[l]["top"]]["origin_iso3"] == iso)
R["proxy"]["home_editions"] = home_ed
R["proxy"]["home_editions_text"] = ", ".join(f"{BQ[langtop[l]['top']]['name']} ({LANGNAME_ALL[l]})" for l in home_ed)
R["meta"]["n_countries_coloured"] = len(pop)

# ---- origin colours: the origins of number one breeds plus the big breeding countries ----
PAL = {"GBR": "#2F5D8C", "FRA": "#C8433A", "DEU": "#D9A21B", "USA": "#4F8A3A", "MEX": "#8E4FA8", "JPN": "#D9648F", "ITA": "#1F8F86",
       "CHN": "#8A5A2E", "RUS": "#5F6B7A", "AUS": "#E07B1F", "BEL": "#6E7F2E", "other": "#9A948A"}
site = {"origin_colours": PAL, "cname": {k: CAP(k) for k in cname}}
# origins per country
orig = defaultdict(lambda: {"breeds": []})
for b in sorted(S, key=lambda b: b["name"]):
    note = b["wd_origin_detail"].split("|")[0] if b["wd_origin_detail"] else ""
    flag = ""
    if b["fci_patronage"]:
        flag = "FCI patronage: " + b["fci_patronage"]
    if b["fci_development"]:
        flag = "developed in " + b["fci_development"]
    grp = f"FCI group {b['fci_group']}: {b['fci_group_name']}" if b["fci_group"] and b["fci_num"] else ""
    orig[b["origin_iso3"]]["breeds"].append([b["name"], b["qid"], 1 if b["fci_num"] else 0, grp, note, flag])
for iso, c in orig.items():
    rs = [r for r in reg if r["iso3"] == iso and r["origin_iso3"] == iso]
    if rs:
        c["reg"] = sorted(rs, key=lambda r: int(r["rank"]))[0]["breed"]
site["origins"] = orig
# popularity per country
site["pop"] = {}
for r in pop:
    d = dict(basis=r["basis"], source=r["source"], year=r["year"], top_breed=r["top_breed"], top_origin=r["top_origin"], lang=r["lang"],
             note=r["note"], home_share=float(r["home_share"]) if r["home_share"] else "")
    if r["basis"] == "club":
        d["top10"] = [[x["breed"], x["origin_iso3"], int(x["count"]) if x["count"] else ""] for x in by_iso_t10[r["iso3"]]]
    site["pop"][r["iso3"]] = d
from importlib import import_module
LC = import_module("05_popularity").LANG_COUNTRIES if False else None
lang_countries = defaultdict(list)
for r in pop:
    if r["lang"]:
        lang_countries[r["lang"]].append(r["iso3"])
LANGNAME = {r["lang"]: r["language"] for r in pvl}
site["langs"] = {}
for l, t in langtop.items():
    rows = [r for r in pvl if r["lang"] == l and r["views12"] != ""]
    rows.sort(key=lambda r: -int(r["views12"]))
    site["langs"][l] = dict(name=LANGNAME[l], countries=lang_countries.get(l, []),
                            top=[[r["breed"], r["origin_iso3"], int(r["views12"])] for r in rows[:5]])
site["top10"] = [{"iso": iso, "t": [[x["breed"], x["origin_iso3"], int(x["count"]) if x["count"] else ""] for x in by_iso_t10[iso]]}
                 for iso in sorted(by_iso_t10, key=lambda i: (-len(by_iso_t10[i]), CAP(i)))]
site["home"] = home_rows
# stories: breeds that top a club abroad
def best(name):
    rs = [r for r in reg if r["breed"] == name]
    return sorted(rs, key=lambda r: int(r["rank"]))
stories = []
for name, big, bigl, text in [
    ("Golden Retriever", "No. 1", "in " + ", ".join(CAP(i) for i in ones.get("Golden Retriever", [])),
     f"Bred at Guisachan in the Scottish Highlands; top of the French LOF (a little over {int(R['clubs']['top']['FRA']['count']):,} births, as reported) and of Dogs Australia ({int(R['clubs']['top']['AUS']['count']):,} registrations in 2025)."),
    ("Labrador Retriever", "No. 1", "in " + ", ".join(CAP(i) for i in ones.get("Labrador Retriever", [])),
     f"Developed in Britain from Newfoundland water dogs; the Royal Kennel Club still registered {R['uk']['lab_2025']:,} in 2025."),
    ("Poodle", "No. 1", "in Japan", f"Filed by the FCI under France; {int(regq('JPN', 'Poodle')['count']):,} registered with the Japan Kennel Club in 2025, most of them toy poodles."),
    ("Chihuahua", "No. 2", "in Japan", f"A Mexican breed; {int(regq('JPN', 'Chihuahua')['count']):,} JKC registrations in 2025."),
]:
    b = [x for x in S if x["name"] == name][0]
    stories.append(dict(breed=name, origin=b["origin_iso3"], from_=CAP(b["origin_iso3"]), big=big, bigl=bigl, text=text))
for s in stories:
    s["from"] = s.pop("from_")
site["stories"] = stories
R["stories"] = stories
# UK trend: breeds in the top five in any year
years = list(range(2016, 2026))
top5 = set()
for y in years:
    top5 |= {r["breed"] for r in sorted(ukt, key=lambda r: -int(r[str(y)]))[:5]}
for p in uko:
    p["lat"], p["lon"] = float(p["lat"]), float(p["lon"])
    p["reg_2025"] = int(p["reg_2025"]) if p["reg_2025"] else ""; p["reg_2016"] = int(p["reg_2016"]) if p["reg_2016"] else ""
site["uk"] = {"points": uko, "trend": {"years": years, "series": [{"n": r["breed"], "o": r["origin_iso3"], "v": [int(r[str(y)]) for y in years]} for r in ukt if r["breed"] in top5]}}
R["uk"]["top5_any_year"] = sorted(top5)
# disagreements table
site["disagree"] = [[b["name"], b["fci_country"], ("patronage " + b["fci_patronage"]) if b["fci_patronage"] else "", ", ".join(CAP(x) for x in b["wd_origin"].split("|"))] for b in sorted(dis, key=lambda b: b["name"])]
R["disagree"] = site["disagree"]
jsave(R, f"{DATA}/results.json", indent=1)
jsave(site, f"{DATA}/site.json")
print(json.dumps({k: R[k] for k in ("meta", "clubs", "frenchie", "proxy")}, indent=1, ensure_ascii=False)[:4000])
print(R["origins"]["top"][:6], R["origins"]["europe_share"], R["origins"]["n_disagree"], R["origins"]["n_extra"])
