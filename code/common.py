"""Shared paths and helpers for the dog-breeds project."""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "/home/claude/hist/_data18/dog-breeds"          # raw bundles (read in place)
DATA = os.path.join(ROOT, "data")
TMP = "/tmp/claude-0/dogtmp"
NE50 = "/home/claude/hist/_data3/ne/geojson/ne_50m_admin_0_countries.geojson"
os.makedirs(DATA, exist_ok=True); os.makedirs(TMP, exist_ok=True)


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def jsave(obj, path, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    """Loose key for matching breed names across languages and spellings."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r"\(imp\)|\(.*?dog breed\)|\(dog\)|\(hund\)|\(chien\)|\(perro\)", "", s)
    s = s.replace("&", " and ")
    s = re.sub(r"[\W_]+", " ", s).strip()
    return s
