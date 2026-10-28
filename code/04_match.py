"""Match kennel club breed names (as published, in five languages) to the breed table.

Aliases: Wikidata English label, English Wikipedia title, FCI names (official and English), and Wikipedia
article titles in German, Swedish, Japanese, Finnish, Norwegian and French (Wikidata sitelinks), plus a short list
of hand matches for club naming conventions (for example "Retriever (Labrador)"). Varieties that a club lists
separately (for example the three Dachshund sizes or the Poodle sizes) are added together under one breed.
Output: data/registrations.csv (one row per country and breed) and data/registrations_unmatched.csv
"""
import csv, re
from collections import defaultdict
from common import *

wd = jload(f"{RAW}/dogs_wikidata_bundle.json.gz")
B = {r["qid"]: r for r in csv.DictReader(open(f"{DATA}/breeds.csv", encoding="utf-8")) if r["qid"]}
alias = {}


def add(name, q):
    k = norm(name)
    if k and k not in alias:
        alias[k] = q


for q, r in B.items():
    for n in (r["name"], r["enwiki"], r["fci_name"]):
        add(n, q)
for q, d in wd["det"].items():
    if q not in B:
        continue
    for l in ("en", "de", "sv", "ja", "fi", "no", "fr", "nn", "da"):
        if l in d["sl"]:
            add(re.sub(r"\s*\(.*?\)\s*$", "", d["sl"][l]), q)
            add(d["sl"][l], q)
by_label = {norm(r["name"]): q for q, r in B.items()}


def Q(label):
    return by_label[norm(label)]


MANUAL = {
    # Royal Kennel Club conventions
    "Retriever (Labrador)": "Labrador Retriever", "Retriever (Golden)": "Golden Retriever", "Spaniel (Cocker)": "English Cocker Spaniel",
    "Spaniel (English Springer)": "English Springer Spaniel", "Spaniel (Cavalier King Charles)": "Cavalier King Charles Spaniel",
    "Retriever (Flat Coated)": "Flat-Coated Retriever", "Retriever (Chesapeake Bay)": "Chesapeake Bay Retriever",
    "Retriever (Curly Coated)": "Curly-Coated Retriever", "Retriever (Nova Scotia Duck Tolling)": "Nova Scotia Duck Tolling Retriever",
    "Spaniel (American Cocker)": "American Cocker Spaniel", "Spaniel (Welsh Springer)": "Welsh Springer Spaniel",
    "Spaniel (Clumber)": "Clumber Spaniel", "Spaniel (Field)": "Field Spaniel", "Spaniel (Irish Water)": "Irish Water Spaniel",
    "Spaniel (Sussex)": "Sussex Spaniel", "Spaniel (King Charles)": "King Charles Spaniel", "Spaniel (Japanese Chin)": "Japanese Chin",
    "Hungarian Vizsla": "Vizsla", "Italian Spinone": "Spinone Italiano", "German Shepherd Dog": "German Shepherd",
    "Dachshund (Miniature Smooth Haired)": "Dachshund", "Dachshund (Miniature Long Haired)": "Dachshund",
    "Dachshund (Miniature Wire Haired)": "Dachshund", "Dachshund (Smooth Haired)": "Dachshund", "Dachshund (Long Haired)": "Dachshund",
    "Dachshund (Wire Haired)": "Dachshund", "Poodle (Toy)": "Poodle", "Poodle (Miniature)": "Poodle", "Poodle (Standard)": "Poodle",
    "Chihuahua (Long Coat)": "Chihuahua", "Chihuahua (Smooth Coat)": "Chihuahua", "Chihuahua (Long)": "Chihuahua",
    "Chihuahua (Smooth)": "Chihuahua", "Schnauzer": "Standard Schnauzer", "Miniature Schnauzer": "Miniature Schnauzer",
    "Bull Terrier (Miniature)": "Miniature Bull Terrier", "Pointer": "English Pointer", "English Pointer": "English Pointer",
    "Newfoundland": "Newfoundland dog", "Pyrenean Mountain Dog": "Pyrenean Mountain Dog", "Bulldog": "Bulldog",
    "Collie (Rough)": "Rough Collie", "Collie (Smooth)": "Smooth Collie", "Collie": "Rough Collie", "Japanese Shiba Inu": "Shiba Inu",
    "Japanese Akita Inu": "Akita", "Akita": "American Akita", "Shar-Pei": "Shar Pei", "Chinese Shar-Pei": "Shar Pei",
    "Welsh Corgi (Pembroke)": "Pembroke Welsh Corgi", "Welsh Corgi (Cardigan)": "Cardigan Welsh Corgi",
    "Pembroke Welsh Corgi": "Pembroke Welsh Corgi", "Cardigan Welsh Corgi": "Cardigan Welsh Corgi",
    "Bichon Frise": "Bichon Frise", "Bichon Frisé": "Bichon Frise", "Dogue de Bordeaux": "Dogue de Bordeaux",
    "German Spitz (Klein)": "German Spitz", "German Spitz (Mittel)": "German Spitz", "Pomeranian": "Pomeranian",
    "Xoloitzcuintle (Mexican Hairless) (Intermediate) (Imp)": "Xoloitzcuintle", "Xoloitzcuintle (Mexican Hairless) (Miniature) (Imp)": "Xoloitzcuintle",
    "Xoloitzcuintle (Mexican Hairless) (Standard) (Imp)": "Xoloitzcuintle", "Kooikerhondje": "Kooikerhondje",
    "Jack Russell Terrier": "Jack Russell Terrier", "Parson Russell Terrier": "Parson Russell Terrier", "Russell Terrier": "Jack Russell Terrier",
    "Doberman Pinscher": "Dobermann", "Dobermann": "Dobermann", "Great Dane": "Great Dane", "Great Pyrenees": "Pyrenean Mountain Dog",
    "Belgian Malinois": "Malinois dog", "Belgian Shepherd Dog (Malinois)": "Malinois dog", "Belgian Sheepdog": "Groenendael",
    "Belgian Tervuren": "Tervuren", "Belgian Laekenois": "Laekenois", "Mastiff": "English Mastiff", "Bullmastiff": "Bullmastiff",
    "English Cocker Spaniel": "English Cocker Spaniel", "Brittany": "Brittany",
    "German Wirehaired Pointer": "German Wirehaired Pointer", "Giant Schnauzer": "Giant Schnauzer", "Standard Schnauzer": "Standard Schnauzer",
    "Wirehaired Pointing Griffon": "Wirehaired Pointing Griffon", "Brussels Griffon": "Griffon Bruxellois", "Griffon Bruxellois": "Griffon Bruxellois",
    "Neapolitan Mastiff": "Neapolitan Mastiff", "Silky Terrier": "Australian Silky Terrier", "Australian Silky Terrier": "Australian Silky Terrier",
    "Wire Fox Terrier": "Wire Fox Terrier", "Smooth Fox Terrier": "Smooth Fox Terrier", "Fox Terrier (Wire)": "Wire Fox Terrier",
    "Fox Terrier (Smooth)": "Smooth Fox Terrier", "Nederlandse Kooikerhondje": "Kooikerhondje", "Löwchen": "Löwchen",
    "Petit Basset Griffon Vendéen": "Petit Basset Griffon Vendéen", "Grand Basset Griffon Vendeen": "Grand Basset Griffon Vendéen",
    "Cirneco dell'Etna": "Cirneco dell'Etna", "Danish-Swedish Farmdog": "Danish-Swedish Farmdog", "Dansk-svensk gårdshund": "Danish-Swedish Farmdog",
    "Black Russian Terrier": "Black Russian Terrier", "Russian Toy": "Russian Toy", "Bergamasco Sheepdog": "Bergamasco Shepherd",
    "Polish Lowland Sheepdog": "Polish Lowland Sheepdog", "Pyrenean Shepherd": "Pyrenean Shepherd", "Miniature American Shepherd": "Miniature American Shepherd",
    "Miniature american shepherd": "Miniature American Shepherd", "Australian Shepherd": "Australian Shepherd",
    "American Staffordshire Terrier": "American Staffordshire Terrier", "Staffordshire Bull Terrier": "Staffordshire Bull Terrier",
    # Sweden (SKK press release)
    "Tysk schäferhund": "German Shepherd", "Cocker spaniel": "English Cocker Spaniel", "Staffordshire bullterrier": "Staffordshire Bull Terrier",
    "Bichon havanais": "Havanese", "Finsk lapphund": "Finnish Lapphund", "Pudel, dvärg": "Poodle", "Pudel, mellan": "Poodle",
    "Jack russel terrier": "Jack Russell Terrier", "Engelsk springer spaniel": "English Springer Spaniel",
    "Tax, normalstor strävhårig": "Dachshund", "Flatcoated retriever": "Flat-Coated Retriever", "Jämthund": "Jämthund",
    "Drever": "Drever", "Shetland sheepdog": "Shetland Sheepdog", "Border collie": "Border Collie",
    # France, Finland, Norway
    "Berger australien": "Australian Shepherd", "Staffordshire bull terrier": "Staffordshire Bull Terrier", "Golden retriever": "Golden Retriever",
    "Labradorinnoutaja": "Labrador Retriever", "Kultainennoutaja": "Golden Retriever", "Suomenlapinkoira": "Finnish Lapphund",
    "Labrador retriever": "Labrador Retriever", "Poodle": "Poodle", "German Shepherd": "German Shepherd",
    # Germany (VDH names, some machine-translated in the saved page)
    "Deutscher Schäferhund": "German Shepherd", "Teckel": "Dachshund", "Deutsch Drahthaar": "German Wirehaired Pointer",
    "Deutsch Kurzhaar": "German Shorthaired Pointer", "Deutsch Langhaar": "German Longhaired Pointer", "Pudel": "Poodle",
    "Kleiner Münsterländer": "Small Münsterländer", "Großer Münsterländer Vorstehhund": "Large Münsterländer", "Mops": "Pug",
    "Dalmatiner": "Dalmatian dog", "Zwergschnauzer": "Miniature Schnauzer", "Riesenschnauzer": "Giant Schnauzer", "Schnauzer": "Standard Schnauzer",
    "Hovawart": "Hovawart", "Berner Sennenhund": "Bernese Mountain Dog", "Bernese Mountain Dog": "Bernese Mountain Dog",
    "Deutsche Dogge": "Great Dane", "Havaneser": "Havanese", "Malteser": "Maltese dog", "Malinois": "Malinois dog",
    "Französische Bulldogge": "French Bulldog", "Sheltie (Shetland Sheepdog)": "Shetland Sheepdog", "Collie (Langhaar)": "Rough Collie",
    "Collie (Kurzhaar)": "Smooth Collie", "Bobtail (Old English Sheepdog)": "Old English Sheepdog", "Neufundländer": "Newfoundland dog",
    "Bernhardiner": "St. Bernard", "Zwergspitz": "Pomeranian", "Kleinspitz": "German Spitz", "Mittelspitz": "German Spitz", "Großspitz": "German Spitz",
    "Wolfsspitz": "Keeshond", "Irish Red Setter": "Irish Setter", "Magyar Vizsla": "Vizsla", "Deutscher Jagdterrier": "Jagdterrier",
    "Deutscher Wachtelhund": "German Spaniel", "Kontinentaler Zwergspaniel": "Papillon", "Fox Terrier (Drahthaar)": "Wire Fox Terrier",
    "Fox Terrier (Glatthaar)": "Smooth Fox Terrier", "Welsh Corgi (Pembroke) ": "Pembroke Welsh Corgi", "Chihuahua": "Chihuahua",
    "Bordeauxdogge": "Dogue de Bordeaux", "Cane Corso Italiano": "Cane Corso", "Weißer Schweizer Schäferhund": "Berger Blanc Suisse",
    "Tibet Terrier": "Tibetan Terrier", "Großer Schweizer Sennenhund": "Greater Swiss Mountain Dog", "Barsoi": "Borzoi",
    "Afghanischer Windhund": "Afghan Hound", "Italienisches Windspiel": "Italian Greyhound", "Zwergpinscher": "Miniature Pinscher",
    "Deutscher Pinscher": "German Pinscher", "Continental Bulldog": "Continental Bulldog", "Landseer": "Landseer (dog)",
    "Mittelasiatischer Schäferhund": "Central Asian Shepherd Dog", "Kaukasischer Schäferhund": "Caucasian Shepherd Dog",
    "Bichon à poil frisé": "Bichon Frise", "Bayerischer Gebirgsschweißhund": "Bavarian Mountain Hound", "Shiba": "Shiba Inu",
    "Sheltie": "Shetland Sheepdog", "Labrador Retriever": "Labrador Retriever", "Golden Retriever": "Golden Retriever",
    # Japan (JKC)
    "プードル": "Poodle", "チワワ": "Chihuahua", "ダックスフンド": "Dachshund", "ポメラニアン": "Pomeranian", "ミニチュア・シュナウザー": "Miniature Schnauzer",
    "マルチーズ": "Maltese dog", "フレンチ・ブルドッグ": "French Bulldog", "ヨークシャー・テリア": "Yorkshire Terrier", "ビション・フリーゼ": "Bichon Frise",
    "シー・ズー": "Shih Tzu", "ゴールデン・レトリーバー": "Golden Retriever", "パグ": "Pug", "ウェルシュ・コーギー・ペンブローク": "Pembroke Welsh Corgi",
    "ボーダー・コリー": "Border Collie", "ペキニーズ": "Pekingese", "柴": "Shiba Inu", "キャバリア・キング・チャールズ・スパニエル": "Cavalier King Charles Spaniel",
    "パピヨン": "Papillon", "ラブラドール・レトリーバー": "Labrador Retriever", "イタリアン・グレーハウンド": "Italian Greyhound",
    "ジャック・ラッセル・テリア": "Jack Russell Terrier", "ミニチュア・ピンシャー": "Miniature Pinscher", "シベリアン・ハスキー": "Siberian Husky",
    "シェットランド・シープドッグ": "Shetland Sheepdog",
    "German Shepherd Dog (LSC)": "German Shepherd", "British Bulldog": "Bulldog", "Hungarian Wirehaired Vizsla": "Wirehaired Vizsla",
    "秋田": "Akita", "Minature American Shepherd": "Miniature American Shepherd", "Nova Scotia Duck Tolling Ret.": "Nova Scotia Duck Tolling Retriever",
    "Basset Griffon Vendeen (Petit)": "Petit Basset Griffon Vendéen", "Basset Griffon Vendeen (Grand)": "Grand Basset Griffon Vendéen",
    "Appenzeller Mountain Dog": "Appenzeller Sennenhund", "アイリッシュ・セター": "Irish Setter", "甲斐": "Kai Ken", "四国": "Shikoku Ken",
    "北海道": "Hokkaido", "Holländischer Schäferhund (Kurzhaar)": "Dutch Shepherd", "Holländischer Schäferhund (Langhaar)": "Dutch Shepherd",
    "Holländischer Schäferhund (Rauhhaar)": "Dutch Shepherd", "Maremma Sheepdog": "Abruzzo-Maremma Sheepdog",
    "Korthals Griffon (Imp)": "Wirehaired Pointing Griffon", "Portugese Water Dog": "Portuguese Water Dog",
    "Anatolian Shepherd Dog": "Anatolian Shepherd", "Russian Black Terrier": "Black Russian Terrier",
    "Belgian Shepherd Dog (Tervueren)": "Tervuren", "Belgian Shepherd Dog (Groenendael)": "Groenendael", "Belgian Shepherd Dog (Laekenois)": "Laekenois",
    "Hungarian Pumi": "Pumi", "Hungarian Mudi (Imp)": "Mudi", "Great Swiss Mountain Dog": "Greater Swiss Mountain Dog",
    "Wirehaired Slovakian Pointer": "Slovakian Wirehaired Pointer", "Dachshund Rabbit (Long)": "Dachshund", "Dachshund Rabbit (Smooth)": "Dachshund",
    "Dachshund Rabbit (Wire)": "Dachshund", "Zwergspitz": "Pomeranian", "ポメラニアン": "Pomeranian", "Pomeranian": "Pomeranian",
    "Russisch Bolonka Zwetna": "Russian Tsvetnaya Bolonka", "Pyrenäen-Berghund": "Pyrenean Mountain Dog",
}
unmatched = []
agg = defaultdict(lambda: {"count": 0, "names": [], "rank": None})
meta = {}
for r in csv.DictReader(open(f"{DATA}/registrations_raw.csv", encoding="utf-8")):
    nm = r["name"].strip()
    q = None
    if nm == "Cocker Spaniel":  # AKC's Cocker Spaniel is the American breed; elsewhere the name means the English breed
        nm = "American Cocker Spaniel" if r["iso3"] == "USA" else "English Cocker Spaniel"
    if nm in MANUAL:
        try:
            q = Q(MANUAL[nm])
        except KeyError:
            q = alias.get(norm(MANUAL[nm]))
            if not q:
                print("manual target missing:", MANUAL[nm])
    if not q:
        q = alias.get(norm(nm)) or alias.get(norm(re.sub(r"\(.*?\)", "", nm)))
    if not q:
        unmatched.append(r)
        continue
    a = agg[(r["iso3"], q)]
    a["names"].append(nm)
    if r["count"] != "":
        a["count"] += int(float(r["count"])); a["has"] = True
    if r["rank"] != "":
        a["rank"] = int(r["rank"]) if a["rank"] is None else min(a["rank"], int(r["rank"]))
    meta[r["iso3"]] = (r["club"], r["year"], r["source"])

out = []
for (iso, q), a in agg.items():
    out.append(dict(iso3=iso, club=meta[iso][0], year=meta[iso][1], qid=q, breed=B[q]["name"], names_published="; ".join(a["names"]),
                    count=a["count"] if a.get("has") else "", rank_published=a["rank"] or "", origin_iso3=B[q]["origin_iso3"], source=meta[iso][2]))
# rank within country after adding varieties together: by count where counts exist, else by published rank
res = []
for iso in sorted({o["iso3"] for o in out}):
    rs = [o for o in out if o["iso3"] == iso]
    if all(o["count"] != "" for o in rs) and iso not in ("NOR", "CAN", "USA"):
        rs.sort(key=lambda o: -o["count"])
    else:
        rs.sort(key=lambda o: o["rank_published"] or 999)
    for i, o in enumerate(rs, 1):
        o["rank"] = i
    res += rs
with open(f"{DATA}/registrations.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
with open(f"{DATA}/registrations_unmatched.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["iso3", "name", "count", "rank"]); w.writeheader()
    for r in unmatched:
        w.writerow({k: r[k] for k in w.fieldnames})
tot = defaultdict(int); unm = defaultdict(int)
for r in csv.DictReader(open(f"{DATA}/registrations_raw.csv", encoding="utf-8")):
    if r["count"]:
        tot[r["iso3"]] += int(float(r["count"]))
for r in unmatched:
    if r["count"]:
        unm[r["iso3"]] += int(float(r["count"]))
for iso in tot:
    print(iso, "unmatched share of count", round(unm[iso] / tot[iso], 4), "rows", sum(1 for r in unmatched if r["iso3"] == iso))
print("top unmatched:", sorted([(int(float(r["count"] or 0)), r["iso3"], r["name"]) for r in unmatched], reverse=True)[:40])
