"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex."""
import csv, re, shutil, subprocess
from common import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Born_Here_Loved_There"
CN = SITE["cname"]
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pct": return f"{v * 100:.0f}\\%"
    if f == "pct1": return f"{v * 100:.1f}\\%"
    if f == "f1": return f"{v:.1f}"
    return tex(str(v))


B = [b for b in csv.DictReader(open(f"{DATA}/breeds.csv", encoding="utf-8")) if b["in_study"] == "1"]
rows = ""
for o in R["origins"]["top"][:10]:
    bs = sorted([b for b in B if b["origin_iso3"] == o["iso"]], key=lambda b: -int(b["sitelinks"] or 0))[:4]
    rows += f"{tex(CN[o['iso']])} & {o['n']} & {tex(', '.join(b['name'] for b in bs))}\\\\\n"
TO = ("\\begin{table}[tbp]\\centering\\small\\caption{The ten leading countries of origin, with the four breeds of each that have the most "
      "Wikipedia language editions.}\\label{tab:origins}\\begin{tabular}{lrp{9.6cm}}\\toprule Country & Breeds & Examples\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
pop = {r["iso3"]: r for r in csv.DictReader(open(f"{DATA}/country_popularity.csv", encoding="utf-8")) if r["basis"] == "club"}
MEAS = {"GBR": "registrations", "AUS": "registrations", "JPN": "registrations", "DEU": "puppies bred", "USA": "rank only", "SWE": "registrations, top 20",
        "FRA": "LOF births, top 3", "CAN": "rank, top 10", "NOR": "top 3", "FIN": "registrations, top 3"}
rows = ""
for iso in sorted(pop, key=lambda i: CN[i]):
    r = pop[iso]
    hs = f"{float(r['home_share']) * 100:.0f}\\%" if r["home_share"] else "n/a"
    rows += f"{tex(CN[iso])} & {tex(r['source'].replace(' (', ' ').replace(')', ''))} & {r['year']} & {MEAS[iso]} & {tex(r['top_breed'])} & {tex(CN[r['top_origin']])} & {hs}\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Kennel club figures used, each club's number one breed and its country of origin, and the share "
      "of all counted registrations that belong to home-grown breeds (clubs that count every breed).}\\label{tab:clubs}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{1.8cm}>{\\raggedright\\arraybackslash}p{3.4cm}l>{\\raggedright\\arraybackslash}p{2.1cm}>{\\raggedright\\arraybackslash}p{3.0cm}>{\\raggedright\\arraybackslash}p{1.5cm}r}\\toprule Country & Club & Year & Measure & Number one & Bred in & Home\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
LN = {"ja": "Japanese", "sv": "Swedish", "fi": "Finnish", "no": "Norwegian", "de": "German", "fr": "French"}
rows = "".join(f"{tex(CN[c['iso']])} & {LN[c['lang']]} & {tex(c['proxy'])} & {tex(c['club'])} & {'yes' if c['match'] else ('top three' if c['in_club_top3'] else 'no')}\\\\\n" for c in R["proxy"]["checks"])
TP = ("\\begin{table}[tbp]\\centering\\small\\caption{The Wikipedia proxy tested against kennel club figures: most read breed article (12 months to September 2026) "
      "and the club's number one.}\\label{tab:proxy}\\begin{tabular}{llllc}\\toprule Country & Wikipedia & Most read & Club number one & Agrees\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(3) or "raw"), t)
t = t.replace("{{TABLE_ORIGINS}}", TO).replace("{{TABLE_CLUBS}}", TC).replace("{{TABLE_PROXY}}", TP)
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower()][:10])
for ext in (".aux", ".log", ".out"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
shutil.copy(os.path.join(OUT, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words; dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
