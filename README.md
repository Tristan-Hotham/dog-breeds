# Born here, loved there

Where the world's dog breeds come from, and where they are loved now. 573 breeds mapped to a present-day country of origin (FCI nomenclature, Wikidata, English Wikipedia), set against the latest open registration figures of 10 national kennel clubs, with Wikipedia reading in 42 languages as a labelled stand-in elsewhere.

Interactive page: https://maps.tristanhotham.com/dog-breeds/
Paper: https://doi.org/10.5281/zenodo.23748254
Blog post: https://blog.tristanhotham.com/2026/10/28/dog-breeds/

## Headline results

- Britain is the country of origin of 72 of the 573 breeds, more than any other; then France 57, the United States 51, Spain 39 and Germany 38. Europe accounts for 69% of the breeds.
- For 8 of 10 kennel clubs the number one breed was born in another country; 6 of those are British breeds. Only Germany (German Shepherd) and the UK (Labrador Retriever) put a home-grown breed first.
- Across the clubs' top tens, 79% of places go to breeds from another country.
- Home-grown breeds are 61% of Royal Kennel Club registrations in 2025, 44% of VDH puppies, 3% in Australia and 2% in Japan.
- The French Bulldog, a French breed, is the AKC's number one and the Japan Kennel Club's number 7 (9,578 in 2025). In Britain it overtook the Labrador in 2018 (36,785 against 36,526), peaked at 54,074 in 2021 and fell to 7,750 in 2025 (86% down).
- 20 British breeds can be placed at a named county, valley, town or estate from their English Wikipedia articles.
- The Wikipedia stand-in names the club's own number one in 0 of 6 test countries and a club top-three breed in 1: read it as curiosity, not ownership. The Cane Corso is the most read breed in 12 of 42 language editions.

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
| `data/uk_origins.csv` | 20 British breed birthplaces with the English Wikipedia sentence used and how the marker was placed. |
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
