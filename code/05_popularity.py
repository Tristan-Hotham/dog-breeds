"""Popularity now: kennel club registrations where published, Wikipedia pageviews as a labelled proxy elsewhere.

Pageviews: for 201 breeds (the 200 with the most Wikipedia language editions plus the Pomeranian), daily user views
over the 60 days to 28 October 2026 in 42 language editions (MediaWiki PageViewInfo, with continuation), and monthly
views October 2025 to September 2026 for each edition's four most viewed breeds (Wikimedia REST API). The 12-month figure decides each
edition's top breed; the 60-day figure picks the candidates.
Outputs: data/pageviews_by_language.csv, data/country_popularity.csv, data/club_top10.csv
"""
import csv
from collections import defaultdict
from common import *

B = {r["qid"]: r for r in csv.DictReader(open(f"{DATA}/breeds.csv", encoding="utf-8")) if r["qid"]}
geo = jload(f"{DATA}/countries_geo.json")
pv = jload(f"{RAW}/dogs_pageviews_v2.json.gz")
P60, P12 = pv["pv60"], pv["pv12"]

LANGNAME = {"en": "English", "de": "German", "fr": "French", "es": "Spanish", "it": "Italian", "pt": "Portuguese", "nl": "Dutch",
            "pl": "Polish", "ru": "Russian", "uk": "Ukrainian", "ja": "Japanese", "zh": "Chinese", "ko": "Korean", "sv": "Swedish",
            "fi": "Finnish", "da": "Danish", "no": "Norwegian (Bokmål)", "cs": "Czech", "sk": "Slovak", "hu": "Hungarian",
            "ro": "Romanian", "bg": "Bulgarian", "el": "Greek", "tr": "Turkish", "he": "Hebrew", "ar": "Arabic", "fa": "Persian",
            "hr": "Croatian", "sr": "Serbian", "sl": "Slovene", "et": "Estonian", "lv": "Latvian", "lt": "Lithuanian",
            "is": "Icelandic", "th": "Thai", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay", "ka": "Georgian",
            "hy": "Armenian", "hi": "Hindi", "af": "Afrikaans"}
# Countries each edition stands for. "single": the language is the main language of essentially one country.
# "shared": an edition read across several countries; its top breed is shown for each, flagged as shared.
LANG_COUNTRIES = {
    "ja": ("single", ["JPN"]), "ko": ("single", ["KOR"]), "pl": ("single", ["POL"]), "cs": ("single", ["CZE"]),
    "sk": ("single", ["SVK"]), "hu": ("single", ["HUN"]), "it": ("single", ["ITA", "SMR"]), "sv": ("single", ["SWE"]),
    "fi": ("single", ["FIN"]), "da": ("single", ["DNK"]), "no": ("single", ["NOR"]), "is": ("single", ["ISL"]),
    "et": ("single", ["EST"]), "lv": ("single", ["LVA"]), "lt": ("single", ["LTU"]), "sl": ("single", ["SVN"]),
    "hr": ("single", ["HRV"]), "bg": ("single", ["BGR"]), "el": ("single", ["GRC", "CYP"]), "tr": ("single", ["TUR"]),
    "he": ("single", ["ISR"]), "ka": ("single", ["GEO"]), "hy": ("single", ["ARM"]), "th": ("single", ["THA"]),
    "vi": ("single", ["VNM"]), "id": ("single", ["IDN"]), "uk": ("single", ["UKR"]), "fa": ("single", ["IRN"]),
    "ro": ("single", ["ROU", "MDA"]), "ms": ("single", ["MYS", "BRN"]), "nl": ("single", ["NLD"]), "hi": ("single", ["IND"]),
    "sr": ("shared", ["SRB", "MNE", "BIH"]), "de": ("shared", ["DEU", "AUT", "CHE", "LIE", "LUX"]),
    "fr": ("shared", ["FRA", "BEL", "MCO"]), "es": ("shared", ["ESP", "MEX", "COL", "ARG", "PER", "VEN", "CHL", "ECU", "GTM", "CUB",
                                                         "BOL", "DOM", "HND", "PRY", "SLV", "NIC", "CRI", "PAN", "URY", "PRI"]),
    "pt": ("shared", ["BRA", "PRT", "AGO", "MOZ"]), "ru": ("shared", ["RUS", "BLR", "KAZ", "KGZ"]),
    "ar": ("shared", ["EGY", "SAU", "DZA", "MAR", "IRQ", "SYR", "JOR", "TUN", "LBY", "YEM", "ARE", "OMN", "KWT", "QAT", "BHR", "LBN", "PSE", "SDN"]),
    "zh": ("shared", ["CHN", "TWN"]), "en": ("shared", ["IRL", "NZL"]), "af": ("shared", []),
}

# 1. per-language ranking
langrows, lang_top = [], {}
by = defaultdict(list)
for k, v in P60.items():
    if not v:
        continue
    q, l = k.split("|")
    if q not in B and q != "Q39579":
        continue
    by[l].append((q, v[0]))
for l, lst in by.items():
    lst.sort(key=lambda x: -x[1])
    tot = sum(x[1] for x in lst)
    m12 = {}
    for q, _ in lst[:4]:
        s = P12.get(f"{q}|{l}")
        if s:
            m12[q] = sum(x[1] for x in s)
    top12 = max(m12, key=m12.get) if m12 else lst[0][0]
    for i, (q, n) in enumerate(lst, 1):
        langrows.append(dict(lang=l, language=LANGNAME[l], rank60=i, qid=q, breed=B[q]["name"], origin_iso3=B[q]["origin_iso3"],
                             views60=n, share60=round(n / tot, 4), views12=m12.get(q, "")))
    srt12 = sorted(m12.items(), key=lambda x: -x[1])
    lang_top[l] = dict(top=top12, top60=lst[0][0], total60=tot, views12=m12.get(top12), n=len(lst),
                       second=srt12[1][0] if len(srt12) > 1 else None, margin12=(srt12[0][1] / srt12[1][1]) if len(srt12) > 1 else None,
                       top3_12=[q for q, _ in srt12[:3]])
with open(f"{DATA}/pageviews_by_language.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(langrows[0].keys())); w.writeheader(); w.writerows(langrows)

# 2. kennel clubs
reg = list(csv.DictReader(open(f"{DATA}/registrations.csv", encoding="utf-8")))
clubs = defaultdict(list)
for r in reg:
    clubs[r["iso3"]].append(r)
CLUBNOTE = {"DEU": "puppies bred in VDH member clubs", "FRA": "LOF registrations, top three as reported", "CAN": "rank only, top four",
            "NOR": "top three as listed", "FIN": "2024 figures", "USA": "rank only", "SWE": "top 20 published"}
rows, club_top10 = [], []
for iso, rs in clubs.items():
    rs.sort(key=lambda r: int(r["rank"]))
    top = rs[0]
    counted = [r for r in rs if r["count"] != ""]
    total = sum(int(r["count"]) for r in counted)
    home = sum(int(r["count"]) for r in counted if r["origin_iso3"] == iso)
    t10 = rs[:10]
    for r in t10:
        club_top10.append(dict(iso3=iso, rank=r["rank"], breed=r["breed"], qid=r["qid"], origin_iso3=r["origin_iso3"], count=r["count"], club=r["club"], year=r["year"]))
    rows.append(dict(iso3=iso, country=geo.get(iso, {}).get("name", iso), basis="club", source=top["club"], year=top["year"],
                     top_qid=top["qid"], top_breed=top["breed"], top_origin=top["origin_iso3"], top_count=top["count"],
                     top_share=round(int(top["count"]) / total, 4) if top["count"] and total and len(counted) > 30 else "",
                     home_share=round(home / total, 4) if total and len(counted) > 30 else "",
                     top10_abroad=sum(r["origin_iso3"] != iso for r in t10), top10_n=len(t10), lang="", note=CLUBNOTE.get(iso, "")))
have = {r["iso3"] for r in rows}
# 3. proxy for the rest
for l, (kind, isos) in LANG_COUNTRIES.items():
    if l not in lang_top:
        continue
    t = lang_top[l]
    for iso in isos:
        if iso in have or iso not in geo:
            continue
        rows.append(dict(iso3=iso, country=geo[iso]["name"], basis="proxy_" + kind, source=f"{LANGNAME[l]} Wikipedia pageviews",
                         year="2025 to 2026", top_qid=t["top"], top_breed=B[t["top"]]["name"], top_origin=B[t["top"]]["origin_iso3"],
                         top_count=t["views12"] or "", top_share="", home_share="", top10_abroad="", top10_n="", lang=l,
                         note="12 months to September 2026"))
with open(f"{DATA}/country_popularity.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(f"{DATA}/club_top10.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(club_top10[0].keys())); w.writeheader(); w.writerows(club_top10)
jsave(lang_top, f"{DATA}/lang_top.json", indent=0)
print(len(rows), "countries:", sum(r["basis"] == "club" for r in rows), "club,", sum(r["basis"] == "proxy_single" for r in rows), "single-language proxy,",
      sum(r["basis"] == "proxy_shared" for r in rows), "shared-language proxy")
for l, t in sorted(lang_top.items()):
    print(l, B[t["top"]]["name"], B[t["top"]]["origin_iso3"], t["views12"], "| 60d top:", B[t["top60"]]["name"], "margin", t["margin12"] and round(t["margin12"], 2))
