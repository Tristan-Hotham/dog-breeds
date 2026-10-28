"""World outlines (Natural Earth 1:50m, simplified) keyed by ISO3, plus country centroids and a
small list of big cities for map labels (GeoNames, via the sun-and-rain project's cleaned file).
Outputs: data/world.json, data/countries_geo.json, data/cities.json
"""
from shapely.geometry import shape, mapping
from common import *

ne = jload(NE50)
feats, geo = [], {}
for f in ne["features"]:
    p = f["properties"]
    iso = p.get("ISO_A3")
    if not iso or iso == "-99":
        iso = p.get("ADM0_A3")
    if iso in ("ATA",):
        continue
    if p.get("ADM0_A3") == "KOS":
        iso = "XKX"
    g = shape(f["geometry"])
    gs = g.simplify(0.08, preserve_topology=True)
    if gs.is_empty:
        continue
    m = mapping(gs)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 2), round(c[1], 2)]
    feats.append({"type": "Feature", "properties": {"iso": iso, "name": p.get("NAME_EN") or p.get("NAME")},
                  "geometry": {"type": m["type"], "coordinates": rnd(m["coordinates"])}})
    rp = g.representative_point()
    # use the label point Natural Earth provides when present (better for countries with far territories)
    lx, ly = p.get("LABEL_X"), p.get("LABEL_Y")
    geo[iso] = {"name": p.get("NAME_EN") or p.get("NAME"), "lon": round(lx if lx is not None else rp.x, 3),
                "lat": round(ly if ly is not None else rp.y, 3), "continent": p.get("CONTINENT"),
                "pop": p.get("POP_EST"), "region": p.get("REGION_UN"), "subregion": p.get("SUBREGION")}
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")
jsave(geo, f"{DATA}/countries_geo.json", indent=0)

c = jload("/home/claude/hist/sun-and-rain/data/cities_page.json")
cols = c["cols"]
ix = {k: i for i, k in enumerate(cols)}
rows = sorted(c["rows"], key=lambda r: -(r[ix["pop"]] or 0))[:900]
cities = [{"name": r[ix["name"]], "lat": round(r[ix["lat"]], 3), "lon": round(r[ix["lon"]], 3), "pop": r[ix["pop"]]} for r in rows]
jsave(cities, f"{DATA}/cities.json")
print(len(feats), "countries;", len(cities), "cities;", os.path.getsize(f"{DATA}/world.json") // 1024, "KB world")
