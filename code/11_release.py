"""Blog post and meta (release/blog), Zenodo files and meta (release/zenodo)."""
import re, shutil, zipfile, json as _json
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "f1": return f"{v:.1f}"
    raise ValueError(f)


# checks of facts stated in words in the blog
assert sorted(R["number_ones"]["Golden Retriever"]) == ["AUS", "FRA", "NOR"]
assert sorted(R["number_ones"]["Labrador Retriever"]) == ["CAN", "FIN", "GBR", "SWE"]
assert R["proxy"]["n_match"] == 0 and {"ja", "fi", "tr"} <= set(R["proxy"]["home_editions"])
assert R["frenchie"]["jkc_rank"] == 7 and R["frenchie"]["uk_2018_overtook"]
jp = [x for x in jload(f"{DATA}/site.json")["top10"] if x["iso"] == "JPN"][0]
assert not any(t[1] == "JPN" for t in jp["t"])

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(3)), post)
for img in re.findall(r"\{\{IMG\|([^|]+)\|", post):
    assert os.path.exists(f"{REL}/blog/{img}"), img
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
assert "\u2014" not in vis and "\u2013" not in vis and "--" not in vis
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Born here, loved there: where dog breeds come from, and where they are loved",
        "slug": "dog-breeds",
        "excerpt": f"I mapped {R['meta']['n_study']} dog breeds to their countries of origin and set them against kennel club registrations. In {R['clubs']['n_top_abroad']} of {R['meta']['n_clubs']} countries the favourite dog was born somewhere else.",
        "seo_description": f"Where {R['meta']['n_study']} dog breeds come from and where they are loved now: Britain bred the most, and France bred America's favourite dog.",
        "tags": ["dogs", "dog breeds", "kennel clubs", "maps", "data visualisation", "Wikidata", "French Bulldog", "data"],
        "header_alt": f"Title card reading 'Born here, loved there' in blue and rust on cream, beside a world map coloured by the birthplace of each country's favourite dog breed: British blue across Canada, Australia and northern Europe, French red over the United States, German gold over Germany, hatched colours where a Wikipedia stand-in is used. Text: where {R['meta']['n_study']} dog breeds come from and where they are loved now; {R['clubs']['n_top_abroad']} of {R['meta']['n_clubs']} kennel clubs have a number one breed born in another country."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
NAME = "Hotham_Born_Here_Loved_There"
shutil.copy(f"{REL}/{NAME}.pdf", f"{Z}/{NAME}.pdf")
for f in ("breeds.csv", "registrations.csv", "country_popularity.csv", "uk_origins.csv", "uk_trends.csv", "pageviews_by_language.csv", "results.json"):
    shutil.copy(f"{DATA}/{f}", f"{Z}/{f}")
zp = f"{Z}/dog-breeds_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith((".pyc",)) or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"dog-breeds/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"dog-breeds/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\emph{", "").replace("}", "").replace("\\&", "&")
zmeta = {"title": "Born Here, Loved There: Where Dog Breeds Come From and Where They Are Loved. Breed origins from Wikidata and the FCI set against kennel club registrations in " + str(R["meta"]["n_clubs"]) + " countries",
         "description_html": f"<p>{ab}</p><p>Interactive version: https://maps.tristanhotham.com/dog-breeds/. Data and code: https://github.com/Tristan-Hotham/dog-breeds. Blog post: to follow.</p>",
         "keywords": ["dog breeds", "kennel clubs", "breed registrations", "Wikidata", "FCI", "Wikipedia pageviews", "cultural diffusion", "French Bulldog", "maps", "popularity"],
         "licence": "cc-by-sa-4.0",
         "related": [{"identifier": "https://github.com/Tristan-Hotham/dog-breeds", "relation": "issupplementedby", "resource_type": "software"},
                     {"identifier": "https://maps.tristanhotham.com/dog-breeds/", "relation": "issupplementedby", "resource_type": "other"},
                     {"identifier": "https://www.wikidata.org/", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.fci.be/en/nomenclature/", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.royalkennelclub.com/about-us/resources/breed-registration-statistics/", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.akc.org/expert-advice/news/most-popular-dog-breeds-2025/", "relation": "isderivedfrom", "resource_type": "other"},
                     {"identifier": "https://www.vdh.de/presse/welpenstatistik/", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.jkc.or.jp/registr-statistics/2025/", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.dogsaustralia.org.au/media/10430/rego-stats-list_2018-2025.pdf", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://wikimedia.org/api/rest_v1/", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.naturalearthdata.com/", "relation": "isderivedfrom", "resource_type": "dataset"}]}
for k in ("title",):
    assert "--" not in zmeta[k]
jsave(zmeta, f"{Z}/meta.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s
print("blog words", words, "; zenodo files", sorted(os.listdir(Z)))
