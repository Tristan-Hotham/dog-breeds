"""r/dataisbeautiful collage for 'Born here, loved there' (2400 x 3000 px). Run from the project folder: python3 reddit/collage.py"""
import json, os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Patch, FancyArrowPatch
from pyproj import Transformer
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); D = os.path.join(ROOT, "data")
F = "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/"
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + "FrauncesVar.ttf", weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
BG, FG, MUT, LAND = "#F6EFE2", "#241F1A", "#6E665B", "#E6DCCB"
R = json.load(open(os.path.join(D, "results.json"))); S = json.load(open(os.path.join(D, "site.json"))); W = json.load(open(os.path.join(D, "world.json")))
GEO = json.load(open(os.path.join(D, "countries_geo.json")))
OC = S["origin_colours"]; oc = lambda i: OC.get(i, OC["other"]); CN = S["cname"]
tr = Transformer.from_crs(4326, 8857, always_xy=True)
plt.rcParams["hatch.linewidth"] = 1.0; plt.rcParams["hatch.color"] = "#FFFFFF"

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
fig.text(.045, .968, "Born here, loved there", fontproperties=DISP, fontsize=54, color=FG, va="top")
fig.text(.045, .912, f"Where {R['meta']['n_study']} dog breeds come from, and each country's favourite breed today,\ncoloured by the country that breed was born in.", family=SER, fontsize=16.5, color=FG, va="top", linespacing=1.35)

# hero map
ax = fig.add_axes([.0, .505, 1.0, .35]); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-12.3e6, 15.8e6); ax.set_ylim(-5.4e6, 7.7e6)
for f in W["features"]:
    iso = f["properties"]["iso"]; r = S["pop"].get(iso)
    g = f["geometry"]; cs = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in cs:
        a = np.array(poly[0]); x, y = tr.transform(np.clip(a[:, 0], -179.9, 179.9), a[:, 1]); P = np.column_stack([x, y])
        if not r:
            ax.add_patch(MPoly(P, closed=True, fc=LAND, ec=BG, lw=.4))
        elif r["basis"] == "club":
            ax.add_patch(MPoly(P, closed=True, fc=oc(r["top_origin"]), ec=BG, lw=.7))
        else:
            ax.add_patch(MPoly(P, closed=True, fc=oc(r["top_origin"]) + "70", ec=oc(r["top_origin"]), lw=.4, hatch="////"))
# arcs from birthplace to the club countries where that breed is number one
def xy(iso):
    g = GEO[iso]; return tr.transform(g["lon"], g["lat"])
ORIGIN_PT = {"Golden Retriever": (57.27, -4.83), "Labrador Retriever": (52.5, -1.5), "French Bulldog": (48.85, 2.35), "Poodle": (47.0, 2.0), "German Shepherd": (51.0, 10.0)}
for breed, isos in R["number_ones"].items():
    o = [b for b in S["origins"].values() for x in b["breeds"] if x[0] == breed]
    la, lo = ORIGIN_PT.get(breed, (0, 0))
    x0, y0 = tr.transform(lo, la)
    col = None
    for iso in isos:
        for oi, c in S["pop"].items():
            if oi == iso: col = oc(c["top_origin"])
        x1, y1 = xy(iso)
        if abs(x1 - x0) < 3e5 and abs(y1 - y0) < 3e5: continue
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), connectionstyle="arc3,rad=-0.28", arrowstyle="-|>,head_length=7,head_width=3.5",
                                     color=FG, lw=1.3, alpha=.8, mutation_scale=1.6, zorder=6))
    ax.scatter([x0], [y0], s=60, c="white", edgecolors=FG, linewidths=1.6, zorder=7)
lab = [("French Bulldog\nborn in Paris,\nNo. 1 in the USA", "USA", (-1.6e6, -3.9e6)), ("Poodle (FCI: France)\nNo. 1 in Japan", "JPN", (-2.5e6, -3.9e6)),
       ("Golden Retriever\nborn in the Highlands,\nNo. 1 in France, Australia, Norway", "AUS", (-7.6e6, 1.1e6)),
       ("German Shepherd\nNo. 1 at home", "DEU", (1.9e6, -3.4e6))]
for t, iso, (dx, dy) in lab:
    x, y = xy(iso)
    ax.annotate(t, (x, y), (x + dx, y + dy), fontsize=10.5, family=MONO, color=FG, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=.3", fc=BG, ec="none", alpha=.9), arrowprops=dict(arrowstyle="-", color=FG, lw=.8), zorder=8)
# legend
used = {}
for r in S["pop"].values():
    k = r["top_origin"] if r["top_origin"] in OC else "other"; used[k] = used.get(k, 0) + 1
hs = [Patch(fc=oc(k), label=("bred in " + (CN[k].replace("the ", ""))) if k != "other" else "bred elsewhere") for k in sorted(used, key=lambda k: -used[k])]
hs += [Patch(fc="#B8B0A3", ec="#8D857A", hatch="////", label="Wikipedia stand-in, no open club figures")]
fig.legend(handles=hs, loc="upper left", bbox_to_anchor=(.045, .505), ncol=4, frameon=False, prop={"family": MONO, "size": 10.5}, handlelength=1.4, columnspacing=1.2, labelcolor=FG)

# big numbers
NUM = [(f"{R['origins']['top'][0]['n']}", "breeds born in Britain,\nmore than any other country"),
       (f"{R['clubs']['n_top_abroad']} of {R['meta']['n_clubs']}", "kennel clubs whose number one\nbreed was born abroad"),
       (f"{round(R['frenchie']['uk_drop'] * 100)}%", f"fall in UK French Bulldog\nregistrations, {R['frenchie']['uk_peak_year']} to 2025"),
       (f"{round(R['clubs']['home']['JPN'] * 100)}%", "of Japan Kennel Club\nregistrations are Japanese breeds")]
for i, (big, small) in enumerate(NUM):
    x = .045 + i * .24
    fig.text(x, .432, big, fontproperties=DISP, fontsize=40, color="#B5562B", va="top")
    fig.text(x, .381, small, family=SER, fontsize=12.5, color=FG, va="top", linespacing=1.25)

# small multiples row: UK birthplaces, top-ten squares, French Bulldog line
trb = Transformer.from_crs(4326, 27700, always_xy=True)
a1 = fig.add_axes([.03, .1, .27, .195]); a1.set_aspect("equal"); a1.axis("off")
cty = json.load(open("/home/claude/hist/how-roman-is-your-road/data/counties.geojson"))
for f in cty["features"]:
    g = shape(f["geometry"]).simplify(.01)
    for poly in getattr(g, "geoms", [g]):
        if poly.geom_type != "Polygon": continue
        a = np.array(poly.exterior.coords); x, y = trb.transform(a[:, 0], a[:, 1])
        a1.add_patch(MPoly(np.column_stack([x, y]), closed=True, fc=LAND, ec=BG, lw=.3))
P = S["uk"]["points"]
X, Y = trb.transform([p["lon"] for p in P], [p["lat"] for p in P])
a1.scatter(X, Y, s=26, c=OC["GBR"], edgecolors="white", linewidths=.8, zorder=5)
for p, x, y in zip(P, X, Y):
    if p["breed"] in ("Yorkshire Terrier", "Golden Retriever", "Bedlington Terrier", "Sussex Spaniel", "Pembroke Welsh Corgi", "Shetland Sheepdog", "Staffordshire Bull Terrier"):
        nm = p["breed"].replace(" Terrier", "").replace(" Retriever", "").replace(" Spaniel", "").replace(" Welsh Corgi", " Corgi").replace(" Sheepdog", "").replace(" Bull", " Bull T.")
        a1.text(x + 14000, y, nm, fontsize=9, family=MONO, color=FG, va="center")
a1.set_xlim(-30000, 760000); a1.set_ylim(0, 1220000)
fig.text(.04, .298, f"{R['uk']['n_points']} British breeds with a\nnamed birthplace", family=MONO, fontsize=11, color=FG, va="bottom", fontweight="medium")

a2 = fig.add_axes([.355, .11, .28, .175]); a2.axis("off")
rows = S["top10"][:6]
for i, r in enumerate(rows):
    for k, t in enumerate(r["t"]):
        a2.add_patch(plt.Rectangle((k, -i), .86, .8, fc=oc(t[1]), ec=FG if t[1] == r["iso"] else "none", lw=1.6))
    a2.text(-.3, -i + .4, CN[r["iso"]].replace("the ", "").replace("United States", "USA").replace("UK", "UK"), ha="right", va="center", fontsize=9.5, family=MONO, color=FG)
a2.set_xlim(-3.4, 10); a2.set_ylim(-len(rows) + .6, 1.0)
fig.text(.355, .298, "Each club's top ten, coloured\nby birthplace (outline = home)", family=MONO, fontsize=11, color=FG, va="bottom", fontweight="medium")

a3 = fig.add_axes([.71, .125, .25, .155]); a3.set_facecolor(BG)
T = S["uk"]["trend"]
for s in T["series"]:
    if s["n"] in ("French Bulldog", "Labrador Retriever"):
        fr = s["n"] == "French Bulldog"
        a3.plot(T["years"], [v / 1000 for v in s["v"]], color=oc(s["o"]), lw=3 if fr else 2, marker="o", ms=3)
        a3.text(2025.3, s["v"][-1] / 1000 + (3 if fr else 2), "French\nBulldog" if fr else "Labrador", fontsize=9.5, family=MONO, color=oc(s["o"]), va="center")
a3.set_xticks([2016, 2021, 2025]); a3.tick_params(labelsize=9, colors=MUT)
for sp in ("top", "right"): a3.spines[sp].set_visible(False)
a3.set_ylabel("thousand a year", fontsize=9, color=MUT, family=MONO); a3.set_xlim(2015.5, 2028.3)
fig.text(.70, .298, "UK registrations: the\nFrench Bulldog boom and bust", family=MONO, fontsize=11, color=FG, va="bottom", fontweight="medium")

fig.text(.045, .022, "Sources: Wikidata (CC0); FCI breeds nomenclature; registration figures of the Royal Kennel Club, AKC, VDH, Japan Kennel Club,\n"
         "Dogs Australia, SKK and NKK; CKC, SCC and Kennelliitto figures as reported in the press; Wikimedia pageviews (CC0); English Wikipedia\n"
         "(CC BY-SA 4.0); OS Open Names and ONS boundaries (OGL v3); Natural Earth. Registered pedigree dogs only; stand-in measures reading.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib · maps.tristanhotham.com/dog-breeds", family=MONO, fontsize=9.2, color=MUT, va="bottom", linespacing=1.45)
fig.savefig(os.path.join(HERE, "born_here_loved_there.png"), dpi=200, facecolor=BG)
print("saved")
