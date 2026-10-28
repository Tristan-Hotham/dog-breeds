"""Static figures: header.png (1200 x 630), blog figures (release/blog/b_*.png, 1520 px wide) and paper figures
(release/paper/f_*.png). Maps are drawn from Natural Earth outlines (data/world.json) in the Equal Earth projection."""
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Patch
from matplotlib.collections import PatchCollection
import numpy as np
from pyproj import Transformer
from common import *

F = "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/"
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf"]:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + "FrauncesVar.ttf", weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 13, "axes.edgecolor": "#6C665C", "axes.labelcolor": "#22201C",
                     "xtick.color": "#6C665C", "ytick.color": "#6C665C", "svg.fonttype": "none"})
BG, FG, MUT, LAND, RULE = "#F8F4EC", "#22201C", "#6C665C", "#E9E2D4", "#E0D7C7"
R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json"); W = jload(f"{DATA}/world.json")
OC = SITE["origin_colours"]; oc = lambda i: OC.get(i, OC["other"])
CN = SITE["cname"]
REL = os.path.join(ROOT, "release"); os.makedirs(f"{REL}/blog", exist_ok=True); os.makedirs(f"{REL}/paper", exist_ok=True)
tr = Transformer.from_crs(4326, 8857, always_xy=True)


def polys(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        ring = np.array(poly[0])
        x, y = tr.transform(np.clip(ring[:, 0], -179.9, 179.9), ring[:, 1])
        yield np.column_stack([x, y])


SHAPES = [(f["properties"]["iso"], list(polys(f["geometry"]))) for f in W["features"]]
OBREAKS = [1, 3, 6, 11, 21, 41]; ORAMP = ["#F1E3CC", "#E8C79B", "#DCA06A", "#C97646", "#A9502E", "#7A3420"]


def ocolour(n):
    k = -1
    for i, b in enumerate(OBREAKS):
        if n >= b: k = i
    return ORAMP[k] if k >= 0 else None


def world_axes(ax, extent=(-12.5e6, 15.5e6, -6.2e6, 8.4e6)):
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3]); ax.set_aspect("equal"); ax.axis("off")


def draw_origins(ax, lw=.35):
    by = R["origins"]["by_country"]
    for iso, ps in SHAPES:
        c = ocolour(by.get(iso, 0)) or LAND
        for p in ps:
            ax.add_patch(MPoly(p, closed=True, fc=c, ec="#FFFFFF", lw=lw))


def draw_loved(ax, lw=.35):
    for iso, ps in SHAPES:
        r = SITE["pop"].get(iso)
        for p in ps:
            if not r:
                ax.add_patch(MPoly(p, closed=True, fc=LAND, ec="#FFFFFF", lw=lw))
            elif r["basis"] == "club":
                ax.add_patch(MPoly(p, closed=True, fc=oc(r["top_origin"]), ec="#FFFFFF", lw=lw * 1.6))
            else:
                ax.add_patch(MPoly(p, closed=True, fc=oc(r["top_origin"]) + "66", ec=oc(r["top_origin"]), lw=lw, hatch="////"))


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)


plt.rcParams["hatch.linewidth"] = 0.8
plt.rcParams["hatch.color"] = "#FFFFFF"

# ---------- blog / paper: origins map ----------
for out, w in ((f"{REL}/blog/b_origins_map.png", 7.6), (f"{REL}/paper/f_origins_map.png", 7.6)):
    fig = plt.figure(figsize=(w, 4.4), facecolor=BG if "blog" in out else "white"); ax = fig.add_axes([0, .08, 1, .92]); world_axes(ax); draw_origins(ax)
    hs = [Patch(fc=ORAMP[i], ec="none", label=f"{b} to {OBREAKS[i + 1] - 1}" if i < len(OBREAKS) - 1 else f"{b} or more") for i, b in enumerate(OBREAKS)]
    fig.legend(handles=hs, loc="lower center", ncol=6, frameon=False, fontsize=9, title="breeds of origin per country", title_fontsize=9, bbox_to_anchor=(.5, -.01))
    for iso, dx, dy in (("GBR", -2.6e6, 1.4e6), ("FRA", -4.6e6, 0.1e6), ("USA", -1.5e6, -2.6e6), ("ESP", -3.4e6, -2.1e6), ("DEU", 1.2e6, 1.4e6)):
        g = jload(f"{DATA}/countries_geo.json")[iso]; x, y = tr.transform(g["lon"], g["lat"])
        ax.annotate(f"{CN[iso]} {R['origins']['by_country'][iso]}", (x, y), (x + dx, y + dy), fontsize=9, color=FG, fontweight="medium",
                    arrowprops=dict(arrowstyle="-", color=FG, lw=.6))
    save(fig, out)

# ---------- loved map ----------
for out in (f"{REL}/blog/b_loved_map.png", f"{REL}/paper/f_loved_map.png"):
    fig = plt.figure(figsize=(7.6, 4.6), facecolor=BG if "blog" in out else "white"); ax = fig.add_axes([0, .12, 1, .88]); world_axes(ax); draw_loved(ax)
    used = {}
    for r in SITE["pop"].values():
        k = r["top_origin"] if r["top_origin"] in OC else "other"; used[k] = used.get(k, 0) + 1
    hs = [Patch(fc=oc(k), ec="none", label=("breed from " + CN[k]) if k != "other" else "other origins") for k in sorted(used, key=lambda k: -used[k])]
    hs.append(Patch(fc="#BBBBBB", ec="#888888", hatch="////", label="Wikipedia stand-in"))
    fig.legend(handles=hs, loc="lower center", ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(.5, -.005))
    save(fig, out)

# ---------- top ten squares ----------
for out in (f"{REL}/blog/b_top10.png", f"{REL}/paper/f_top10.png"):
    rows = SITE["top10"]
    fig = plt.figure(figsize=(7.6, 0.42 * len(rows) + 1.0), facecolor=BG if "blog" in out else "white"); ax = fig.add_axes([.2, .14, .78, .8])
    for i, r in enumerate(rows):
        for k, t in enumerate(r["t"]):
            home = t[1] == r["iso"]
            ax.add_patch(plt.Rectangle((k, -i), .9, .82, fc=oc(t[1]), ec=FG if home else "none", lw=2 if home else 0))
            ab = "".join(w[0] for w in t[0].replace("-", " ").split())[:3]
            ax.text(k + .45, -i + .41, ab, ha="center", va="center", fontsize=7.5, color="white")
        ax.text(-.25, -i + .41, CN[r["iso"]], ha="right", va="center", fontsize=10, color=FG)
    for k in range(10): ax.text(k + .45, 1.05, str(k + 1), ha="center", fontsize=9, color=MUT)
    ax.set_xlim(0, 10); ax.set_ylim(-len(rows) + .7, 1.35); ax.axis("off")
    ks = []
    for r in rows:
        for t in r["t"]:
            k = t[1] if t[1] in OC else "other"
            if k not in ks: ks.append(k)
    hs = [Patch(fc=oc(k), label=CN[k] if k != "other" else "other") for k in ks] + [Patch(fc="none", ec=FG, lw=2, label="home-grown")]
    fig.legend(handles=hs, loc="lower center", ncol=6, frameon=False, fontsize=8.5, bbox_to_anchor=(.55, -.01))
    save(fig, out)

# ---------- UK trend ----------
T = SITE["uk"]["trend"]
for out in (f"{REL}/blog/b_uk_trend.png", f"{REL}/paper/f_uk_trend.png"):
    fig, ax = plt.subplots(figsize=(7.6, 4.2), facecolor=BG if "blog" in out else "white"); ax.set_facecolor(fig.get_facecolor())
    ls = ["-", "--", "-.", ":", (0, (5, 1)), (0, (1, 1)), (0, (3, 1, 1, 1))]
    ends = []
    for j, s in enumerate(sorted(T["series"], key=lambda s: -s["v"][-1])):
        fr = s["n"] == "French Bulldog"
        ax.plot(T["years"], s["v"], color=oc(s["o"]), lw=3.2 if fr else 1.8, ls="-" if fr else ls[j % len(ls)], marker="o", ms=3.5 if fr else 2.5)
        y = s["v"][-1]
        while any(abs(y - e) < 2300 for e in ends): y -= 2300
        ends.append(y); ax.text(2025.25, y, s["n"], va="center", fontsize=9, color=oc(s["o"]), fontweight="medium")
    ax.set_xlim(2016, 2028.6); ax.set_xticks(T["years"]); ax.tick_params(labelsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{int(v / 1000)}k" if v else "0"))
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=RULE, lw=.8); ax.set_ylabel("Royal Kennel Club registrations", fontsize=9)
    fig.tight_layout(); save(fig, out)

# ---------- home-grown shares ----------
for out in (f"{REL}/blog/b_home.png", f"{REL}/paper/f_home.png"):
    rows = SITE["home"]
    fig, ax = plt.subplots(figsize=(7.6, 2.9), facecolor=BG if "blog" in out else "white"); ax.set_facecolor(fig.get_facecolor())
    for i, r in enumerate(rows):
        x = 0
        for o, v in r["parts"]:
            c = "#CFC4B1" if o == "other" else oc(o)
            ax.barh(-i, v, left=x, color=c, edgecolor=FG if o == r["iso"] else "white", lw=2 if o == r["iso"] else .8, height=.62, hatch="" )
            if v > .065: ax.text(x + .008, -i, (o if o != "other" else "other") + f" {round(v * 100)}%", va="center", fontsize=8.5, color="white" if o != "other" else FG)
            x += v
        ax.text(-.01, -i, CN[r["iso"]], ha="right", va="center", fontsize=10)
    ax.set_xlim(0, 1); ax.axis("off"); fig.tight_layout(); save(fig, out)

# ---------- UK birthplaces ----------
from shapely.geometry import shape
trb = Transformer.from_crs(4326, 27700, always_xy=True)
cty = jload("/home/claude/hist/how-roman-is-your-road/data/counties.geojson")
for out in (f"{REL}/blog/b_uk_map.png", f"{REL}/paper/f_uk_map.png"):
    fig = plt.figure(figsize=(6.2, 7.6), facecolor=BG if "blog" in out else "white"); ax = fig.add_axes([0, 0, 1, 1])
    for f in cty["features"]:
        g = shape(f["geometry"]).simplify(0.003)
        gs = getattr(g, "geoms", [g])
        for poly in gs:
            if poly.geom_type != "Polygon": continue
            a = np.array(poly.exterior.coords); x, y = trb.transform(a[:, 0], a[:, 1])
            ax.add_patch(MPoly(np.column_stack([x, y]), closed=True, fc=LAND, ec="#FFFFFF", lw=.6))
    pts = sorted(SITE["uk"]["points"], key=lambda p: -p["lat"])
    placed = [(x - 7000, y - 7000, x + 7000, y + 7000) for x, y in (trb.transform(p["lon"], p["lat"]) for p in pts)]
    for p in pts:
        x, y = trb.transform(p["lon"], p["lat"])
        ax.scatter([x], [y], s=46, c="white", edgecolors=FG, linewidths=1.6, zorder=5)
        for dx, dy, ha in ((10000, 0, "left"), (-10000, 0, "right"), (10000, -17000, "left"), (-10000, -17000, "right"), (10000, 17000, "left"), (-10000, 17000, "right"), (10000, -34000, "left"), (-10000, 34000, "right")):
            w = len(p["breed"]) * 9300 + 4000
            bx = (x + dx if ha == "left" else x + dx - w, y + dy - 7500, x + dx + w if ha == "left" else x + dx, y + dy + 7500)
            if any(bx[0] < o[2] and bx[2] > o[0] and bx[1] < o[3] and bx[3] > o[1] for o in placed):
                continue
            placed.append(bx); ax.text(x + dx, y + dy, p["breed"], ha=ha, va="center", fontsize=8.6, color=FG); break
    ax.set_xlim(-60000, 720000); ax.set_ylim(0, 1230000); ax.set_aspect("equal"); ax.axis("off")
    save(fig, out)

# ---------- header 1200 x 630 ----------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([.36, .02, .66, .96]); world_axes(ax, (-12.5e6, 15.5e6, -6.0e6, 8.4e6)); draw_loved(ax, lw=.3)
fig.text(.04, .86, "Born here,", fontproperties=DISP, fontsize=50, color=OC["GBR"], va="top")
fig.text(.04, .70, "loved there", fontproperties=DISP, fontsize=50, color="#B5562B", va="top")
fig.text(.04, .50, f"Where {R['meta']['n_study']} dog breeds come from,\nand where they are loved now.", family=SER, fontsize=17, color=FG, va="top", linespacing=1.3)
fig.text(.04, .30, f"{R['clubs']['n_top_abroad']} of {R['meta']['n_clubs']} kennel clubs: number one\nbreed born in another country", family=MONO, fontsize=12.5, color=FG, va="top", linespacing=1.3)
fig.text(.04, .07, "maps.tristanhotham.com/dog-breeds", family=MONO, fontsize=12, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)
print("figures done")
