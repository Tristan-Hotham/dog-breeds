"""Parse the kennel club registration tables into one long table (names as published).

Inputs (read in place from RAW): dogs_rkc_pdfs.json.gz (Royal Kennel Club 10-yearly PDFs),
dogs_ankc.json.gz (Dogs Australia PDF), dogs_vdh.json.gz (VDH Welpenstatistik table),
dogs_jkc2025.json.gz (JKC 2025 table), akc_2025.txt (AKC 2025 full ranking, rank only),
rankings_manual.json (Sweden, France, Canada, Norway, Finland: transcribed from press releases).
Output: data/registrations_raw.csv
"""
import base64, csv, re, subprocess, os
from common import *

rows = []  # iso3, club, year, name_published, count, rank_published, source


def pdftext(b64, name):
    p = os.path.join(TMP, name)
    open(p, "wb").write(base64.b64decode(b64))
    t = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
    os.remove(p)
    return t


num = re.compile(r"^\d{1,3}(?:,\d{3})*$|^\d+$")

# UK: Royal Kennel Club, comparative tables 2016 to 2025
rkc = jload(f"{RAW}/dogs_rkc_pdfs.json.gz")
uk_years = {}
for path, b64 in rkc["pdfs_b64"].items():
    if "10-yearly" not in path or not b64:
        continue
    group = path.split("stats-")[-1].replace(".pdf", "")
    for line in pdftext(b64, "rkc.pdf").splitlines():
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) < 2 or parts[0].upper() == parts[0] or parts[0].startswith("TOTAL"):
            continue
        vals = [p for p in parts[1:] if num.match(p.replace(" ", ""))]
        if not vals:
            continue
        nums = [int(v.replace(",", "")) for v in vals]
        name = parts[0]
        yrs = list(range(2025 - len(nums) + 1, 2026))
        for y, n in zip(yrs, nums):
            uk_years.setdefault(name, {})[y] = n
        rows.append(dict(iso3="GBR", club="Royal Kennel Club", year=2025, name=name, count=nums[-1], rank="",
                         group=group, source="https://www.royalkennelclub.com/about-us/resources/breed-registration-statistics/"))
jsave(uk_years, f"{DATA}/uk_registrations_2016_2025.json")

# Australia: Dogs Australia national registration analysis 2018 to 2025
ankc = jload(f"{RAW}/dogs_ankc.json.gz")
for line in pdftext(ankc["pdf_b64"], "ankc.pdf").splitlines():
    m = re.match(r"^(\S.*?)\s{2,}((?:\d+\s+){7}\d+)\s*$", line.strip())
    if not m or m.group(1).upper().startswith(("TOTAL", "GRAND")):
        continue
    nums = [int(x) for x in m.group(2).split()]
    rows.append(dict(iso3="AUS", club="Dogs Australia (ANKC)", year=2025, name=m.group(1).strip(), count=nums[-1], rank="",
                     group="", source=ankc["source"]))

# Germany: VDH puppy statistics (member clubs), 2025 column
vdh = jload(f"{RAW}/dogs_vdh.json.gz")
for r in vdh["rows"][1:]:
    if len(r) < 2 or r[0] in ("Gesamt", "Alle Rassen", "Total", "All breeds"):
        continue
    try:
        n = int(r[1].replace(".", "").replace(",", ""))
    except ValueError:
        continue
    rows.append(dict(iso3="DEU", club="VDH", year=2025, name=r[0], count=n, rank="", group="", source=vdh["source"]))

# Japan: JKC 2025
jkc = jload(f"{RAW}/dogs_jkc2025.json.gz")
for r in jkc["rows"]:
    if len(r) < 3 or not r[0].strip().isdigit():
        continue
    name = re.sub(r"[（(].*?[)）]", "", r[1]).strip()
    rows.append(dict(iso3="JPN", club="Japan Kennel Club (JKC)", year=2025, name=name, count=int(r[2].replace(",", "")),
                     rank=int(r[0]), group="", source=jkc["source"]))

# USA: AKC 2025 ranking (no counts published)
for line in open(f"{RAW}/akc_2025.txt", encoding="utf-8"):
    k, name = line.strip().split(" ", 1)
    rows.append(dict(iso3="USA", club="American Kennel Club (AKC)", year=2025, name=name, count="", rank=int(k), group="",
                     source="https://www.akc.org/expert-advice/news/most-popular-dog-breeds-2025/"))

# Manual transcriptions from press releases
man = jload(f"{RAW}/rankings_manual.json")
for iso, d in man.items():
    if iso.startswith("_"):
        continue
    for i, t in enumerate(d["top"], 1):
        rows.append(dict(iso3=iso, club=d["club"], year=d["year"], name=t[0], count=t[1] if t[1] is not None else "",
                         rank=i, group="", source=d["source"]))

# rank by count where counts exist and no published rank
from collections import defaultdict
by = defaultdict(list)
for r in rows:
    by[r["iso3"]].append(r)
for iso, rs in by.items():
    if all(r["count"] != "" for r in rs) and all(r["rank"] == "" for r in rs):
        for i, r in enumerate(sorted(rs, key=lambda r: -r["count"]), 1):
            r["rank"] = i

with open(f"{DATA}/registrations_raw.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["iso3", "club", "year", "name", "count", "rank", "group", "source"])
    w.writeheader(); w.writerows(rows)
for iso, rs in by.items():
    top = sorted(rs, key=lambda r: (r["rank"] if r["rank"] != "" else 9999))[:3]
    print(iso, len(rs), [(t["name"], t["count"]) for t in top])
