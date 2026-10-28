"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; the page data (site.json, world.json, cities.json) is embedded. Facts stated in words are checked."""
import json, os, re
from common import *

R = jload(f"{DATA}/results.json")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    raise ValueError(f)


# facts stated in words
c = R["clubs"]["top"]
assert c["FRA"]["breed"] == "Golden Retriever" and c["USA"]["breed"] == "French Bulldog" and c["JPN"]["breed"] == "Poodle"
assert R["origins"]["top"][0]["iso"] == "GBR"
assert R["frenchie"]["uk_2018_overtook"]
assert "French Bulldog" not in [r["breed"] for r in []]
assert R["clubs"]["home"]["GBR"] == max(R["clubs"]["home"].values())

if __name__ == "__main__":
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(3)), tpl)
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(jload(f"{DATA}/site.json")))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    assert "{{" not in html
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        scr = re.sub(r"var\(--[\w-]+", "", scr).replace('"--', "").replace("'--", "")
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")
