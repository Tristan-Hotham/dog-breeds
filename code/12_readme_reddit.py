"""README.md and reddit/post.md, with every number from data/results.json. Run before 11_release.py."""
from common import *

R = jload(f"{DATA}/results.json")
assert R['proxy']['n_match'] == 0
o = R["origins"]["top"]; c = R["clubs"]; fb = R["frenchie"]; m = R["meta"]; p = R["proxy"]
pct = lambda x: f"{round(x * 100)}%"
README = f"""# Born here, loved there

Where the world's dog breeds come from, and where they are loved now. {m['n_study']} breeds mapped to a present-day country of origin (FCI nomenclature, Wikidata, English Wikipedia), set against the latest open registration figures of {m['n_clubs']} national kennel clubs, with Wikipedia reading in {m['n_langs']} languages as a labelled stand-in elsewhere.

Interactive page: https://maps.tristanhotham.com/dog-breeds/
Paper: https://doi.org/10.5281/zenodo.23748254
Blog post: https://blog.tristanhotham.com/2026/10/28/dog-breeds/

## Headline results

- Britain is the country of origin of {o[0]['n']} of the {m['n_study']} breeds, more than any other; then France {o[1]['n']}, the United States {o[2]['n']}, Spain {o[3]['n']} and Germany {o[4]['n']}. Europe accounts for {pct(R['origins']['europe_share'])} of the breeds.
- For {c['n_top_abroad']} of {m['n_clubs']} kennel clubs the number one breed was born in another country; {c['n_top_gbr']} of those are British breeds. Only {c['home_top_list']} put a home-grown breed first.
- Across the clubs' top tens, {pct(c['top10_abroad_share'])} of places go to breeds from another country.
- Home-grown breeds are {pct(c['home']['GBR'])} of Royal Kennel Club registrations in 2025, {pct(c['home']['DEU'])} of VDH puppies, {pct(c['home']['AUS'])} in Australia and {pct(c['home']['JPN'])} in Japan.
- The French Bulldog, a French breed, is the AKC's number one and the Japan Kennel Club's number {fb['jkc_rank']} ({fb['jkc_count']:,} in 2025). In Britain it overtook the Labrador in 2018 ({fb['uk_2018']:,} against {fb['lab_2018']:,}), peaked at {fb['uk_peak']:,} in {fb['uk_peak_year']} and fell to {fb['uk_2025']:,} in 2025 ({pct(fb['uk_drop'])} down).
- {R['uk']['n_points']} British breeds can be placed at a named county, valley, town or estate from their English Wikipedia articles.
- The Wikipedia stand-in names the club's own number one in {p['n_match']} of {p['n_check']} test countries and a club top-three breed in {p['n_in_top3']}: read it as curiosity, not ownership. The Cane Corso is the most read breed in {p['cane_n']} of {m['n_langs']} language editions.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/08_build_site.py`; data embedded). |
| `header.png` | Social card, 1200 x 630. |
| `data/breeds.csv` | Every Wikidata dog breed with FCI number, group, country of origin, patronage and development; Wikidata and Wikipedia origins; the origin used and its source; flags for disagreement, extinct and excluded; `in_study`. |
| `data/origin_disagreements.csv` | Breeds where the FCI and Wikidata share no country of origin. |
| `data/registrations_raw.csv` | Kennel club figures as published (names in the club's language). |
| `data/registrations.csv` | The same matched to breeds, varieties added together, ranked within each country. |
| `data/registrations_unmatched.csv` | Club names that could not be matched (under 0.2% of any club's counts). |
| `data/uk_registrations_2016_2025.json`, `data/uk_trends.csv` | Royal Kennel Club registrations 2016 to 2025 by RKC name and by breed. |
| `data/uk_origins.csv` | {R['uk']['n_points']} British breed birthplaces with the English Wikipedia sentence used and how the marker was placed. |
| `data/pageviews_by_language.csv`, `data/lang_top.json` | Wikipedia pageviews of breed articles by language (60 days and 12 months). |
| `data/country_popularity.csv`, `data/club_top10.csv` | Each country's top breed and source (club or stand-in); each club's top ten. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/site.json`, `data/world.json`, `data/cities.json`, `data/countries_geo.json` | Page data; simplified Natural Earth outlines; GeoNames city labels. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source, blog figures and post, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## How to rerun

Needs Python 3 with shapely, pyproj, matplotlib and Pillow, `pdftotext`, and xelatex for the paper. Raw inputs (read in place from `/home/claude/hist/_data18/dog-breeds/`, set in `code/common.py`) were fetched in a browser on 28 October 2026: the Wikidata and English Wikipedia bundle, the FCI nomenclature pages, the kennel club tables and PDFs, and the Wikipedia pageviews.

```
python3 code/01_registrations.py   # parse club tables and PDFs
python3 code/02_geo.py             # world outlines, centroids, city labels
python3 code/03_breeds.py          # breed table: Wikidata + FCI + Wikipedia origins
python3 code/04_match.py           # match club names to breeds
python3 code/05_popularity.py      # pageviews, each country's favourite
python3 code/06_uk.py              # UK trends and birthplaces
python3 code/07_results.py         # results.json and site.json
python3 code/08_build_site.py      # index.html
python3 code/09_figures.py         # header, blog and paper figures
python3 code/10_paper.py           # paper PDF
python3 code/12_readme_reddit.py   # README and Reddit text
python3 code/11_release.py         # blog post, Zenodo files
python3 reddit/collage.py          # collage
```

## Sources and licences

- Wikidata (CC0), via QLever and the Wikidata API; English Wikipedia breed articles (CC BY-SA 4.0).
- FCI breeds nomenclature, Fédération Cynologique Internationale, https://www.fci.be/en/nomenclature/ (factual fields, with credit).
- Royal Kennel Club breed registration statistics; American Kennel Club most popular breeds of 2025; VDH Welpenstatistik; Japan Kennel Club registrations by breed 2025; Dogs Australia national registration analysis 2018 to 2025; Svenska Kennelklubben and Norsk Kennel Klub press releases; Canadian Kennel Club top ten as reported by The Canadian Press; Société Centrale Canine figures as reported by Breizh-Info; Suomen Kennelliitto 2024 figures as reported by Verkkouutiset. Numbers used as facts with credit; no text reproduced.
- Wikimedia pageviews (CC0).
- Natural Earth (public domain); OS Open Names and ONS boundaries (Open Government Licence v3.0); GeoNames (CC BY 4.0) for city labels. Base map tiles on the page © Esri.

Text, figures and derived data: CC BY-SA 4.0. Code: MIT (see LICENSE).

## Citation

Hotham, T. (2026) Born here, loved there: where dog breeds come from and where they are loved. https://doi.org/10.5281/zenodo.23748254

Dr Tristan Hotham, Independent researcher, ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(README)

title = (f"[OC] Born here, loved there: where {m['n_study']} dog breeds come from, and each country's favourite breed coloured by its birthplace. "
         f"In {c['n_top_abroad']} of {m['n_clubs']} countries with open kennel club figures, the number one breed was born abroad")
body = (f"I mapped {m['n_study']} dog breeds to their country of origin (FCI breed register, Wikidata, Wikipedia) and set them against the latest kennel club registrations. "
        f"Britain is the birthplace of the most breeds ({o[0]['n']}). The Golden Retriever, bred on a Highland estate, is number one in France and Australia; "
        f"the French Bulldog is number one in the United States, while British registrations of it fell {pct(fb['uk_drop'])} from {fb['uk_peak_year']} to 2025. "
        f"Only {pct(c['home']['JPN'])} of Japan Kennel Club registrations are Japanese breeds. "
        f"Caveat: clubs count registered pedigree dogs only, and the hatched countries use Wikipedia reading as a stand-in, which never matched the club's favourite in {p['n_check']} tests. "
        f"Interactive map: https://maps.tristanhotham.com/dog-breeds/")
src = ("Source: Wikidata dog breed items (CC0); FCI breeds nomenclature (fci.be); registration figures of the Royal Kennel Club (2016 to 2025), American Kennel Club (2025 ranking), "
       "VDH Welpenstatistik, Japan Kennel Club (2025), Dogs Australia (2018 to 2025), Svenska Kennelklubben and Norsk Kennel Klub (press releases, 2025); Canadian Kennel Club, "
       "Société Centrale Canine and Suomen Kennelliitto figures as reported in the press; Wikimedia pageviews (CC0); English Wikipedia (CC BY-SA 4.0); OS Open Names and ONS "
       "boundaries (OGL v3.0); Natural Earth (public domain).\n\nTools: Python (shapely, pyproj, matplotlib); Leaflet for the interactive map.\n\n"
       "Interactive version: https://maps.tristanhotham.com/dog-breeds/\nPaper: https://doi.org/10.5281/zenodo.23748254\nBlog post: https://blog.tristanhotham.com/2026/10/28/dog-breeds/")
assert len(title) < 300
post = f"## Title\n\n{title}\n\n## Body\n\n{body}\n\n## Source comment\n\n{src}\n"
import re
for txt in (post, README):
    assert "\u2014" not in txt and "\u2013" not in txt and not re.search(r"(?<![!<(\w-])--(?![>\w-])", txt)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print(len(title), len(body.split()), "words body")
