#!/usr/bin/env python3
"""Check a manuscript's citations against its reference list, and the list against the record.

Usage:
    python3 ref_check.py main.tex [more.tex ...] --bib refs.bib [more.bib ...]
    python3 ref_check.py main.tex --bib refs.bib --online --mailto you@institute.edu
    python3 ref_check.py main.tex --bib refs.bib --ledger refcheck.md
    python3 ref_check.py main.tex --online          (list typed as \\bibitem entries, no .bib)

Offline, always:
  - every \\cite key has an entry, every entry is cited, no key is defined twice;
  - no [CITE: ...] placeholder is left in the text;
  - each entry has the fields its type needs, a well-formed DOI or arXiv number, and
    characters and capitals that survive BibTeX;
  - the same DOI or the same title under two keys;
  - citations naming more than --group works at one point, and works cited only in such groups;
  - the spread of publication years and the authors who appear most often
    (with --authors "Family, G." ...: the share of the manuscript authors' own work).

With --online (needs access to doi.org, api.crossref.org and export.arxiv.org):
  - each DOI is resolved: a DOI that does not exist, or belongs to a different work, is an error;
  - title, authors, journal, volume, first page or article number and year are compared
    with the record;
  - retractions, expressions of concern and corrections attached to the record are reported;
  - each arXiv number is looked up, and a published version is reported when arXiv lists one;
  - entries without an identifier are searched in Crossref by title and first author.

A list typed as \\bibitem entries is checked too: the record is found by the DOI or arXiv
number in the typed text, or by a Crossref search of the text, and the record's first author,
volume, first page and year are looked for in what was typed.

--ledger FILE writes a Markdown file with one row per reference and one row per citation
with the sentence it sits in, for the manual check that each reference supports its sentence.
An existing file is kept unless --force is given. The address given with --mailto is sent
to Crossref, which answers identified callers at a higher rate.

A flag is a lead, not a verdict. "Not found" means that this script found no record: books,
theses, reports and old, very recent or non-English works are often missing from the indexes,
and the indexes contain errors of their own. The script cannot tell whether a reference
supports the sentence that cites it.

Does not follow \\input or \\include: pass every .tex file. Standard library only.
Exit status is 1 if any error is reported, otherwise 0.
"""
import argparse
import bisect
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date

DOI_BASE = os.environ.get("REFCHECK_DOI_BASE", "https://doi.org")
CROSSREF_BASE = os.environ.get("REFCHECK_CROSSREF_BASE", "https://api.crossref.org")
ARXIV_BASE = os.environ.get("REFCHECK_ARXIV_BASE", "https://export.arxiv.org/api/query")
CSL = "application/vnd.citationstyles.csl+json"

CITE_CMD = (r"(?:[Cc]ite(?:[tp]|alt|alp|author|year|yearpar|num|n|online|talias|palias|title|date|url)?"
            r"|nocite|onlinecite|(?:[Pp]aren|[Tt]ext|[Aa]uto|[Ss]mart|[Ss]uper|[Ff]oot|[Ff]ull|[Ff]ootfull)cite(?:text)?)")
CITE_RE = re.compile(r"\\(" + CITE_CMD + r")\*?(?![A-Za-z])\s*((?:\[[^\]]*\]\s*)*)\{([^{}]*)\}")
CITES_ONLY_RE = re.compile(r"(?:\\" + CITE_CMD + r"\*?(?:\[[^\]]*\])*\{[^{}]*\})*")
PLACEHOLDER_RE = re.compile(r"\[CITE:[^\]]*\]")
BIBITEM_RE = re.compile(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^{}]+)\}")
ENTRY_RE = re.compile(r"@\s*([A-Za-z]+)\s*([{(])")
RUNAWAY_RE = re.compile(r"\n[ \t]*@[A-Za-z]+\s*[{(]")
FIELD_RE = re.compile(r"\s*,?\s*([A-Za-z][\w\-:.+]*)\s*=\s*")
BARE_RE = re.compile(r"[^\s,#{}\"]+")
HASH_RE = re.compile(r"\s*#\s*")
AND_RE = re.compile(r"\s+and\s+", re.I)
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DOI_FIND_RE = re.compile(r"10\.\d{4,9}/[^\s{}\\\"<>]+")
ARXIV_ID = r"(?:\d{4}\.\d{4,5}|[a-z][a-z\-]*(?:\.[A-Z]{2})?/\d{7})"
ARXIV_RE = re.compile(rf"^{ARXIV_ID}(?:v\d+)?$")
ARXIV_FIND_RE = re.compile(rf"arXiv:\s*({ARXIV_ID})(?:v\d+)?", re.I)
ACCENT_RE = re.compile(r"""\\(?:["'`^~=.]\s*\{?\s*\\?([A-Za-z])\s*\}?"""
                       r"""|[uvHcdbkrt](?:\s*\{\s*\\?([A-Za-z])\s*\}|\s+([A-Za-z])|\s*\\([ij])(?![A-Za-z])))""")
LETTER_RE = re.compile(r"\\(ss|ae|AE|oe|OE|aa|AA|o|O|l|L|i|j)(?![A-Za-z])")
LETTERS = {"ss": "ss", "ae": "ae", "AE": "AE", "oe": "oe", "OE": "OE", "aa": "a", "AA": "A"}
ABBR_RE = re.compile(r"\b(?:Figs?|Eqs?|Refs?|Secs?|Tabs?|et al|e\.g|i\.e|cf|vs|ca|approx|Dr|Prof|Nos?|Vol|[A-Z])\.")
BOUND_RE = re.compile(r"[.!?](?=\s|~|\\[A-Za-z]*cite|$)|\n[ \t]*\n"
                      r"|\\(?:(?:sub)*section|paragraph)\*?\s*\{[^{}]*\}|\\(?:begin|end)\s*\{[^{}]*\}"
                      r"|\\(?:item|caption)\b")
STOP = set("of the and in on for a an de der die la le et".split())
MONTHS = {m: m for m in "jan feb mar apr may jun jul aug sep oct nov dec".split()}
REQUIRED = {
    "article": ["author", "title", "journal", "year"],
    "book": ["title", "publisher", "year"],
    "inbook": ["title", "publisher", "year"],
    "incollection": ["author", "title", "booktitle", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "conference": ["author", "title", "booktitle", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
    "thesis": ["author", "title", "school", "year"],
    "techreport": ["author", "title", "institution", "year"],
    "report": ["author", "title", "institution", "year"],
    "unpublished": ["author", "title", "note"],
    "misc": ["title"], "online": ["title"], "software": ["title"], "dataset": ["title"],
}
ALIAS = {"journal": ("journal", "journaltitle"), "year": ("year", "date"),
         "school": ("school", "institution"), "institution": ("institution", "school")}
RETRACT = {"retraction", "withdrawal", "removal", "partial_retraction"}
CONCERN = {"expression_of_concern"}
MARK_RE = re.compile(r"\s*(?:retracted(?: article)?|retraction(?: note)?|withdrawn|removed)\b\s*:?\s*", re.I)
UA = "complete-paper-ref-check/1.0"


# ---------- text helpers ----------

def detex(s):
    """LaTeX or registry markup to plain text, for comparison only."""
    s = re.sub(r"<[^>]{1,200}>", "", s)
    s = ACCENT_RE.sub(lambda m: next(g for g in m.groups() if g), s)
    s = LETTER_RE.sub(lambda m: LETTERS.get(m.group(1), m.group(1)), s)
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)
    s = s.replace("~", " ").replace("\\&", "&")
    return re.sub(r"[{}$\\^_]", "", s)


def fold(s):
    """Lower-case ASCII letters and digits separated by single spaces."""
    s = unicodedata.normalize("NFKD", detex(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    for a, b in (("ß", "ss"), ("ø", "o"), ("ł", "l"), ("æ", "ae"), ("œ", "oe"), ("đ", "d"), ("ı", "i")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def squash(s):
    return fold(s).replace(" ", "")


def ratio(a, b):
    a, b = squash(a), squash(b)
    if len(a) < 4 or len(b) < 4:
        return None
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def same_name(a, b):
    return bool(a and b) and (a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.8)


def first(x):
    return (x[0] if x else "") if isinstance(x, list) else (x or "")


def short(s, n=90):
    s = " ".join(detex(str(s)).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def match_close(text, i, opener="{"):
    """Index of the bracket that closes the one opened just before position i."""
    depth = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            if depth == 0 and opener == "{":
                return i
            depth -= 1
        elif c == ")" and opener == "(" and depth == 0:
            return i
        i += 1
    return len(text)


# ---------- reading .bib and .tex ----------

def parse_fields(body, strings, undefined=None):
    out, i, n = [], 0, len(body)
    while True:
        m = FIELD_RE.match(body, i)
        if not m:
            break
        name, i, parts = m.group(1).lower(), m.end(), []
        while i < n:
            if body[i] == "{":
                j = match_close(body, i + 1)
                parts.append(body[i + 1:j])
                i = j + 1
            elif body[i] == '"':
                j, depth = i + 1, 0
                while j < n and not (body[j] == '"' and depth == 0):
                    depth += (body[j] == "{") - (body[j] == "}")
                    j += 1
                parts.append(body[i + 1:j])
                i = j + 1
            else:
                m2 = BARE_RE.match(body, i)
                if not m2:
                    break
                word = m2.group(0)
                if undefined is not None and not word.isdigit() and word.lower() not in strings:
                    undefined.append(f"{word} in {name}")
                parts.append(strings.get(word.lower(), word))
                i = m2.end()
            m3 = HASH_RE.match(body, i)
            if not m3:
                break
            i = m3.end()
        out.append((name, " ".join("".join(parts).split())))
    return out


def parse_bib(text, fname):
    entries, strings, pos = [], dict(MONTHS), 0
    while True:
        m = ENTRY_RE.search(text, pos)
        if not m:
            break
        kind = m.group(1).lower()
        end = match_close(text, m.end(), m.group(2))
        runaway = RUNAWAY_RE.search(text, m.end(), end)     # the entry swallowed the next one: it is not closed
        if runaway:
            end = runaway.start()
        body, pos = text[m.end():end], end + 1
        if kind in ("comment", "preamble"):
            continue
        if kind == "string":
            strings.update(parse_fields(body, strings))
            continue
        key, _, rest = body.partition(",")
        undefined = []
        entries.append({"key": key.strip(), "type": kind, "fields": dict(parse_fields(rest, strings, undefined)),
                        "where": f"{fname}:{text.count(chr(10), 0, m.start()) + 1}", "broken": bool(runaway),
                        "undefined": undefined})
    return entries


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def read_tex(paths):
    """Citations, placeholders and \\bibitem entries of the .tex files."""
    cites, placeholders, bibitems, nocite_all = [], [], [], False
    for path in paths:
        text = strip_comments(open(path, encoding="utf-8", errors="replace").read())
        masked = ABBR_RE.sub(lambda m: m.group(0).replace(".", "\x00"), text)
        bounds = [0] + [m.end() for m in BOUND_RE.finditer(masked)] + [len(text)]

        def line(off):
            return text.count("\n", 0, off) + 1

        def tidy(a, b):
            s = CITE_RE.sub(lambda m: "[" + ",".join(k.strip() for k in m.group(3).split(",")) + "]", text[a:b])
            return " ".join(s.split())

        for m in CITE_RE.finditer(text):
            keys = [k.strip() for k in m.group(3).split(",") if k.strip()]
            if "nocite" in m.group(1).lower():
                nocite_all = nocite_all or "*" in keys
                cites.append({"keys": [k for k in keys if k != "*"], "where": f"{path}:{line(m.start())}",
                              "sentence": "", "nocite": True})
                continue
            i = bisect.bisect_right(bounds, m.start()) - 1
            left = bounds[i]
            if i > 0 and text[left - 1] in ".!?" and CITES_ONLY_RE.fullmatch(text[left:m.start()]):
                left, right = bounds[i - 1], CITES_ONLY_RE.match(text, m.end()).end()   # cited after the full stop
            else:
                lead = CITES_ONLY_RE.match(text, left)          # citations that close the sentence before
                if left and text[left - 1] in ".!?" and lead.end() <= m.start():
                    left = lead.end()
                right = bounds[min(bisect.bisect_left(bounds, m.end()), len(bounds) - 1)]
            sent = tidy(left, max(right, m.end()))
            if len(sent) > 300:
                mark = "[" + ",".join(keys) + "]"
                at = max(sent.find(mark), 0)
                sent = ("…" if at > 220 else "") + sent[max(at - 220, 0): at + len(mark) + 60] + "…"
            cites.append({"keys": keys, "where": f"{path}:{line(m.start())}", "sentence": sent, "nocite": False})
        for m in PLACEHOLDER_RE.finditer(text):
            placeholders.append((f"{path}:{line(m.start())}", m.group(0)))
        items = list(BIBITEM_RE.finditer(text))
        for n, m in enumerate(items):
            stop = items[n + 1].start() if n + 1 < len(items) else text.find("\\end{thebibliography}", m.end())
            raw = text[m.end(): stop if stop != -1 else len(text)]
            bibitems.append({"key": m.group(1).strip(), "where": f"{path}:{line(m.start())}",
                             "text": " ".join(raw.split())})
    return cites, placeholders, bibitems, nocite_all


# ---------- names ----------

def split_names(field):
    out, depth, start, i = [], 0, 0, 0
    while i < len(field):
        depth += (field[i] == "{") - (field[i] == "}")
        m = AND_RE.match(field, i) if depth == 0 else None
        if m:
            out.append(field[start:i])
            i = start = m.end()
        else:
            i += 1
    out.append(field[start:])
    return [x.strip() for x in out if x.strip()]


def name_parts(name):
    """(family, given, display): family and given folded, family cut to its last word so that
    particles do not matter; display is the family name as typed."""
    n = name.strip()
    if n.lower() == "others":
        return None
    if n.startswith("{") and match_close(n, 1) == len(n) - 1:        # {Some Collaboration}
        return fold(n), "", " ".join(detex(n).split())
    if "," in n:
        fam, giv = n.split(",")[0], n.split(",")[-1]
    else:
        words = n.split()
        fam, giv = (words[-1], " ".join(words[:-1])) if words else ("", "")
    f = fold(fam).split()
    return (f[-1] if f else ""), fold(giv), " ".join(detex(fam).split())


def record_authors(rec):
    """Authors of a registry record as (family, given, display); empty entries are dropped."""
    out = []
    for a in rec.get("author") or []:
        if a.get("family"):
            f = fold(a["family"]).split()
            out.append((f[-1] if f else "", fold(a.get("given") or ""), a["family"]))
        elif a.get("name") or a.get("literal"):
            whole = a.get("name") or a.get("literal")
            out.append((fold(whole), "", whole))
    return [a for a in out if a[0]]


def label(parts):
    """'Family G', built from the folded name so that one person gets one label."""
    return (parts[0].title() + " " + parts[1][:1].upper()).strip()


# ---------- network ----------

def http_get(url, accept, tries=3):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as f:
                return f.status, f.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt + 1 < tries:
                time.sleep(3 * (attempt + 1))
                continue
            return e.code, ""
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt + 1 < tries:
                time.sleep(2 * (attempt + 1))
                continue
            return 0, str(e)


def doi_record(doi):
    """('ok', record) | ('exists', None) | ('missing', None) | ('error', reason)."""
    quoted = urllib.parse.quote(doi, safe="/()._-:;")
    status, body = http_get(f"{DOI_BASE}/{quoted}", CSL)
    if status == 200:
        try:
            rec = json.loads(body)
            if isinstance(rec, dict) and rec.get("title") is not None:
                return "ok", rec
        except ValueError:
            pass
    if status in (0, 429) or status >= 500:
        return "error", f"no answer from the DOI resolver ({status or body})"
    status2, body2 = http_get(f"{DOI_BASE}/api/handles/{quoted}", "application/json")
    try:
        code = json.loads(body2).get("responseCode") if body2 else None
    except ValueError:
        code = None
    if status2 == 200 and code == 1:
        return "exists", None
    if status2 == 404 or code == 100:
        return "missing", None
    return "error", f"DOI resolver answered {status}/{status2}"


def arxiv_records(ids):
    """{id: record}; an id that arXiv does not know is absent; a failed call sets it to None."""
    out, ns = {}, {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    ids = sorted(set(ids))
    for n in range(0, len(ids), 20):
        chunk = ids[n:n + 20]
        if n:
            time.sleep(3)
        q = urllib.parse.urlencode({"id_list": ",".join(chunk), "max_results": len(chunk)})
        status, body = http_get(f"{ARXIV_BASE}?{q}", "application/atom+xml")
        try:
            root = ET.fromstring(body) if status == 200 else None
        except ET.ParseError:
            root = None
        if root is None:
            out.update({i: None for i in chunk})
            continue
        for e in root.findall("a:entry", ns):
            m = re.search(r"abs/(.+?)(?:v\d+)?$", e.findtext("a:id", "", ns))
            if not m:
                continue
            out[m.group(1)] = {
                "title": " ".join(e.findtext("a:title", "", ns).split()),
                "authors": [x.findtext("a:name", "", ns) for x in e.findall("a:author", ns)],
                "year": e.findtext("a:published", "", ns)[:4],
                "doi": e.findtext("x:doi", "", ns), "journal_ref": e.findtext("x:journal_ref", "", ns)}
    return out


def crossref_search(query, mailto):
    p = {"query.bibliographic": query[:400], "rows": 3,
         "select": "DOI,title,author,container-title,issued,volume,page,type"}
    if mailto:
        p["mailto"] = mailto
    status, body = http_get(f"{CROSSREF_BASE}/works?{urllib.parse.urlencode(p)}", "application/json")
    try:
        return json.loads(body)["message"]["items"] if status == 200 else None
    except (ValueError, KeyError):
        return None


# ---------- comparison with the record ----------

def record_years(rec):
    years = set()
    for k in ("issued", "published", "published-print", "published-online"):
        try:
            years.add(int(rec[k]["date-parts"][0][0]))
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    return years


def journal_match(bib_journal, names):
    def abbrev(x, y):                       # "natl" for "national", "phys" for "physical"
        it = iter(y)
        return x[:1] == y[:1] and all(c in it for c in x)
    b = [w for w in fold(bib_journal).split() if w not in STOP]
    for name in names:
        r = [w for w in fold(name).split() if w not in STOP]
        if not r:
            continue
        if "".join(b) == "".join(r) or (len(b) == 1 and b[0] == "".join(w[0] for w in r)):
            return True
        if len(b) == len(r) and all(abbrev(x, y) or abbrev(y, x) for x, y in zip(b, r)):
            return True
    return False


def compare_authors(names, rec_auth):
    """names: name_parts() results, None for 'others'. Returns (worst level, messages, compared)."""
    bib = [p for p in names if p and p[0]]
    if not bib or not rec_auth:
        return None, [], False
    fams = [r[0] for r in rec_auth]
    found = [any(same_name(b[0], f) for f in fams) for b in bib]
    swapped = [not ok and any(b[0] in r[1].split() for r in rec_auth) for b, ok in zip(bib, found)]
    hits = sum(f or s for f, s in zip(found, swapped))
    msgs, level = [], None
    shown = ", ".join(r[2] for r in rec_auth[:4]) + (" …" if len(rec_auth) > 4 else "")
    if hits == 0 or (len(bib) >= 3 and hits / len(bib) < 0.6):
        level = "E"
        msgs.append(f"author list differs from the record: {hits} of {len(bib)} names found (record: {shown})")
    elif not same_name(bib[0][0], fams[0]) and not swapped[0]:
        level = "W"
        msgs.append(f"first author differs: entry '{bib[0][2]}', record '{rec_auth[0][2]}'")
    if any(swapped):
        level = level or "N"
        msgs.append("family and given name may be swapped: " + ", ".join(b[2] for b, sw in zip(bib, swapped) if sw))
    if None not in names and len(bib) != len(rec_auth) and level != "E":
        level = level or "N"
        msgs.append(f"entry lists {len(bib)} author(s), record lists {len(rec_auth)}")
    return level, msgs, True


def record_updates(rec, doi):
    """Messages for retractions, concerns and corrections attached to a Crossref record."""
    out, seen = [], set()
    title = first(rec.get("title"))
    if MARK_RE.match(detex(title)):
        out.append(("E", f"record title is marked: '{short(title, 60)}'"))
    for field in ("updated-by", "update-to"):
        for u in rec.get(field) or []:
            kind, other = (u.get("type") or "").lower(), (u.get("DOI") or "").lower()
            about_self = field == "updated-by" or other == doi.lower()
            if (kind, other, about_self) in seen:
                continue
            seen.add((kind, other, about_self))
            try:
                when = "-".join(f"{x:02d}" for x in u["updated"]["date-parts"][0])
            except (KeyError, IndexError, TypeError, ValueError):
                when = "date not given"
            src = u.get("source") or "source not given"
            if not about_self:
                if kind in RETRACT | CONCERN:
                    out.append(("W", f"this record is a {kind.replace('_', ' ')} notice for {other}: "
                                     "cite the notice only when the notice is what the sentence is about"))
            elif kind in RETRACT:
                out.append(("E", f"RETRACTED ({kind}, {when}, notice {other}, source: {src})"))
            elif kind in CONCERN:
                out.append(("W", f"expression of concern ({when}, {other}, source: {src})"))
            else:
                out.append(("N", f"{kind.replace('_', ' ') or 'update'} exists ({when}, {other}): "
                                 "cite it if the corrected content is used"))
    if any(m.startswith("RETRACTED") for _, m in out):
        out = [x for x in out if x[0] == "E"]
    for r in (rec.get("relation") or {}).get("is-preprint-of") or []:
        out.append(("N", f"a published version exists: {r.get('id')}"))
    return out


def compare_with_record(e, rec, doi):
    """(identity findings, update findings), each a list of (level, message)."""
    f, out = e["fields"], []
    rec_title, sim = first(rec.get("title")), None
    bare_title = MARK_RE.sub("", detex(rec_title), count=1) if MARK_RE.match(detex(rec_title)) else rec_title
    if f.get("title") and rec_title:
        sim = ratio(f["title"], bare_title)
    rec_auth = record_authors(rec)
    a_level, a_msgs, compared = compare_authors([name_parts(n) for n in split_names(f.get("author", ""))], rec_auth)
    updates = record_updates(rec, doi)
    if sim is not None and sim < 0.9:
        a, b = squash(f["title"]), squash(bare_title)
        if min(len(a), len(b)) >= 15 and (a in b or b in a):
            out.append(("N", f"title is a shorter or longer form of the record's: '{short(rec_title)}'"))
        elif sim < 0.6 and (a_level in ("E", "W") or not compared):
            who = ", ".join(r[2] for r in rec_auth[:3]) or "no authors in the record"
            return [("E", f"identifier belongs to a different work: '{short(rec_title)}' ({who})")], updates
        elif sim < 0.6:
            out.append(("W", f"title differs strongly from the record while the authors agree "
                             f"(translation, comment, erratum?): '{short(rec_title)}'"))
        else:
            out.append(("W", f"title differs from the record: '{short(rec_title)}'"))
    out += [(a_level if n == 0 else "N", m) for n, m in enumerate(a_msgs)]
    names = [first(rec.get(k)) for k in ("container-title", "container-title-short", "short-container-title")]
    journal = f.get("journal") or f.get("journaltitle")
    if journal and any(names) and not journal_match(journal, [n for n in names if n]):
        out.append(("N", f"journal differs, or is abbreviated in a way this script cannot match: "
                         f"entry '{short(journal, 50)}', record '{short(next(n for n in names if n), 50)}'"))
    if f.get("volume") and rec.get("volume") and f["volume"].strip() != str(rec["volume"]).strip():
        out.append(("W", f"volume differs: entry {f['volume']}, record {rec['volume']}"))
    mine = {re.split(r"[-–—]", f[k])[0].strip().lower() for k in ("pages", "eid", "article-number", "articleno") if f.get(k)}
    theirs = {str(x).split("-")[0].strip().lower() for x in (rec.get("page"), rec.get("article-number")) if x}
    if mine and theirs and not mine & theirs:
        out.append(("W", f"first page or article number differs: entry {', '.join(sorted(mine))}, "
                         f"record {', '.join(sorted(theirs))}"))
    elif theirs and not mine:
        out.append(("W", f"no page or article number in the entry: the record gives {', '.join(sorted(theirs))}"))
    year = re.search(r"\d{4}", f.get("year") or f.get("date") or "")
    years = record_years(rec)
    if year and years and int(year.group()) not in years:
        gap = min(abs(int(year.group()) - y) for y in years)
        out.append(("N" if gap <= 1 else "W", f"year differs: entry {year.group()}, record "
                    f"{', '.join(map(str, sorted(years)))} (a record may carry the online or deposit date)"))
    return out, updates


# ---------- checks ----------

def clean_doi(raw):
    d = raw.strip()
    bare = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", d, flags=re.I)
    return bare, bare != d


def entry_arxiv(f):
    if f.get("eprint") and (f.get("archiveprefix", "arxiv").lower() == "arxiv" or ARXIV_RE.match(f["eprint"])):
        return re.sub(r"^arxiv:\s*", "", f["eprint"].strip(), flags=re.I)
    for k in ("journal", "note", "howpublished", "url", "number"):
        m = ARXIV_FIND_RE.search(f.get(k, "")) or re.search(rf"arxiv\.org/abs/({ARXIV_ID})", f.get(k, ""))
        if m:
            return m.group(1)
    return None


def title_capitals(raw):
    """Words whose capitals a sentence-case bibliography style would lower."""
    depth, plain = 0, []
    for c in raw:
        depth += (c == "{") - (c == "}")
        plain.append(c if depth == 0 and c not in "{}" else " ")
    words = "".join(plain).split()
    if len(words) < 2:
        return None
    risky = [w for w in words if re.search(r"(?<=[^-–/])[A-Z]", w.strip("$(")) or (re.search(r"[$\d]", w) and re.search(r"[A-Z]", w))]
    capped = [w for n, w in enumerate(words) if n and w[:1].isupper() and not words[n - 1].endswith(":")]
    if len(words) > 3 and len(capped) > 0.5 * (len(words) - 1):
        return ("title is in title case: a sentence-case style will lower every word; brace what must stay capital"
                + (f" (for example {', '.join(dict.fromkeys(risky))[:60]})" if risky else ""))
    flagged = list(dict.fromkeys(risky + capped))
    if flagged:
        return "capitals not protected by braces (a sentence-case style will lower them): " + ", ".join(flagged[:5])
    return None


def check_entry(e, this_year):
    """Offline checks on one .bib entry: list of (level, message)."""
    f, out, kind = e["fields"], [], e["type"]
    for word in e.get("undefined", []):
        out.append(("W", f"undefined abbreviation {word}: BibTeX will drop it (write it in braces, or define it with @string)"))
    for need in REQUIRED.get(kind, ["title"]):
        if not any(f.get(k) for k in ALIAS.get(need, (need,))):
            out.append(("W", f"@{kind} without {need}"))
    if kind in ("book", "inbook") and not (f.get("author") or f.get("editor")):
        out.append(("W", f"@{kind} without author or editor"))
    doi_raw, arx = f.get("doi", ""), entry_arxiv(f)
    if doi_raw:
        doi, had_prefix = clean_doi(doi_raw)
        if had_prefix:
            out.append(("W", "doi field holds a URL or a 'doi:' prefix: store the bare DOI (10.xxxx/...)"))
        if not DOI_RE.match(doi):
            out.append(("W", f"DOI is not well formed: '{doi}'"))
    if f.get("eprint") and arx and not ARXIV_RE.match(arx):
        out.append(("W", f"arXiv number is not well formed: '{arx}'"))
    if kind == "article":
        if not (f.get("pages") or f.get("eid") or f.get("article-number") or f.get("articleno")) and not doi_raw and not arx:
            out.append(("W", "no page, article number or identifier: a reader cannot locate the work"))
        elif not doi_raw and not arx:
            out.append(("N", "no DOI: identity cannot be checked automatically"))
        elif not (f.get("pages") or f.get("eid") or f.get("article-number") or f.get("articleno")) and f.get("volume"):
            out.append(("N", "no page or article number (registry exports often omit article numbers)"))
        if f.get("journal") and ARXIV_FIND_RE.search(f["journal"]) and not f.get("eprint"):
            out.append(("N", "preprint stored as a journal: use the eprint and archivePrefix fields"))
    if kind == "misc" and f.get("journal"):
        out.append(("W", "@misc with a journal field: should this be @article?"))
    author = f.get("author", "")
    if re.search(r"\bet\.?\s+al\b", author, re.I):
        out.append(("W", "'et al.' typed in the author field is read as a name: list the authors"))
    if author and not AND_RE.search(author) and author.count(",") >= 3 and not author.startswith("{"):
        out.append(("W", "authors seem to be separated by commas: BibTeX needs 'and' between names"))
    if re.search(r"\band\s+others\s*$", author, re.I):
        out.append(("N", "author list ends with 'and others': give all authors and let the style shorten the list"))
    if re.search(r"[^\x00-\x7f]", author):
        out.append(("N", "non-ASCII letters in author: classic BibTeX can mangle initials; use LaTeX accents or Biber"))
    year = f.get("year") or f.get("date") or ""
    y = re.search(r"\d{4}", year)
    if year and not y:
        out.append(("W", f"year is not a four-digit number: '{year}'"))
    elif y and int(y.group()) > this_year + 1:
        out.append(("W", f"year lies in the future: {y.group()}"))
    for k in ("title", "journal", "booktitle", "publisher", "author", "editor"):
        v = f.get(k, "")
        bad = sorted(set(re.findall(r"(?<!\\)[&%#]", v)))
        if bad:
            out.append(("W", f"unescaped {' '.join(bad)} in {k}"))
        if re.search(r"(?<!\\)[_^]", re.sub(r"\$[^$]*\$|\\\(.*?\\\)", "", v)):
            out.append(("W", f"_ or ^ outside math in {k}"))
    if re.search(r"\d\s*[–—]\s*\d", f.get("pages", "")):
        out.append(("N", "pages use a Unicode dash: write the range with two hyphens (--)"))
    raw = f.get("title", "")
    if raw.startswith("{") and match_close(raw, 1) == len(raw) - 1:
        out.append(("N", "whole title is braced: the style cannot set its case; brace only what must stay capital"))
    elif raw and kind in ("article", "inproceedings", "incollection", "misc", "unpublished"):
        msg = title_capitals(raw)
        if msg:
            out.append(("N", msg))
    return out


def grade(ident, updates):
    """Ledger word for one compared reference."""
    worst = "MISMATCH" if any(l == "E" for l, _ in ident) else "differs" if any(l == "W" for l, _ in ident) else "yes"
    return worst + (", RETRACTED" if any(l == "E" for l, _ in updates) else "")


def check_online(entries, bibitems, args, add):
    """Compare entries with their records. Returns {key: (exists, matches, seen at)} for the ledger."""
    status, pause = {}, (0.15 if args.mailto else 0.25)
    arx_of = [entry_arxiv(e["fields"]) for e in entries]
    arx = arxiv_records([re.sub(r"v\d+$", "", a) for e, a in zip(entries, arx_of)
                         if a and ARXIV_RE.match(a) and not e["fields"].get("doi")])
    for n, (e, aid) in enumerate(zip(entries, arx_of), 1):
        f, key, loc = e["fields"], e["key"], e["where"]
        print(f"\r  checking {n}/{len(entries)}", end="", file=sys.stderr, flush=True)
        if f.get("doi"):
            doi, _ = clean_doi(f["doi"])
            time.sleep(pause)
            state, rec = doi_record(doi)
            if state == "missing":
                add("E", loc, key, f"DOI does not exist: {doi}")
                status[key] = ("not found", "—", "")
            elif state == "error":
                add("W", loc, key, f"could not be checked: {rec}")
                status[key] = ("unchecked", "—", "")
            elif state == "exists":
                add("N", loc, key, f"DOI exists, but its registry gives no metadata: compare by hand ({doi})")
                status[key] = ("yes", "unchecked", "doi.org")
            else:
                ident, updates = compare_with_record(e, rec, doi)
                for level, msg in ident + updates:
                    add(level, loc, key, msg)
                status[key] = ("yes", grade(ident, updates), "doi.org")
        elif aid and ARXIV_RE.match(aid):
            aid = re.sub(r"v\d+$", "", aid)
            if aid not in arx:
                add("E", loc, key, f"arXiv number does not exist: {aid}")
                status[key] = ("not found", "—", "")
            elif arx[aid] is None:
                add("W", loc, key, "could not be checked: no answer from arXiv")
                status[key] = ("unchecked", "—", "")
            else:
                r = arx[aid]
                rec = {"title": r["title"], "author": [{"family": a.split()[-1], "given": " ".join(a.split()[:-1])}
                                                         for a in r["authors"] if a.split()]}
                ident, _ = compare_with_record({"fields": {"title": f.get("title", ""), "author": f.get("author", "")}}, rec, "")
                if (r["doi"] or r["journal_ref"]) and not f.get("journal"):
                    ident.append(("N", "arXiv lists a published version: " + " ".join(
                        x for x in (r["journal_ref"], r["doi"] and "doi " + r["doi"]) if x)))
                for level, msg in ident:
                    add(level, loc, key, msg)
                status[key] = ("yes", grade(ident, []), "arXiv")
        elif e["type"] in ("article", "inproceedings", "conference", "incollection") and f.get("title"):
            names = [name_parts(x) for x in split_names(f.get("author", ""))]
            lead = next((p[0] for p in names if p), "")
            time.sleep(0.4 if args.mailto else 1.1)
            items = crossref_search(" ".join(detex(x) for x in (f["title"], lead, f.get("journal", ""), f.get("year", ""))),
                                    args.mailto)
            if items is None:
                add("W", loc, key, "could not be checked: no answer from Crossref")
                status[key] = ("unchecked", "—", "")
                continue
            best = max(items, key=lambda it: ratio(f["title"], first(it.get("title"))) or 0, default=None)
            sim = ratio(f["title"], first(best.get("title"))) if best else None
            if best and sim and sim >= 0.9 and (not lead or any(same_name(lead, r[0]) for r in record_authors(best))):
                add("N", loc, key, f"no identifier in the entry; Crossref has a matching record: add doi = {{{best.get('DOI')}}}")
                time.sleep(pause)
                state, rec = doi_record(best.get("DOI") or "")
                ident, updates = compare_with_record(e, rec, best["DOI"]) if state == "ok" else ([], [])
                for level, msg in ident + updates:
                    add(level, loc, key, msg)
                status[key] = ("yes", grade(ident, updates) if state == "ok" else "unchecked", "Crossref search")
            else:
                near = f" (nearest: '{short(first(best.get('title')), 60)}')" if best else ""
                add("W", loc, key, "no identifier, and no matching record in Crossref" + near
                    + ": find the work by hand before it is cited")
                status[key] = ("not found", "—", "")
        else:
            add("N", loc, key, f"@{e['type']} without DOI or arXiv number: verify by hand "
                               "(publisher, library catalogue, repository)")
            status[key] = ("unchecked", "—", "")
    for n, b in enumerate(bibitems, 1):
        print(f"\r  checking typed item {n}/{len(bibitems)}   ", end="", file=sys.stderr, flush=True)
        status[b["key"]] = check_bibitem(b, args, pause, add)
    print("", file=sys.stderr)
    return status


def check_bibitem(b, args, pause, add):
    """A hand-typed reference: does the content of the record occur in the typed text?"""
    text, loc, key = b["text"], b["where"], b["key"]
    m = DOI_FIND_RE.search(text)
    a = ARXIV_FIND_RE.search(text) or re.search(rf"arxiv\.org/abs/({ARXIV_ID})", text)
    rec = doi = None
    if m:
        doi = m.group(0).rstrip(".,;)")
        time.sleep(pause)
        state, rec = doi_record(doi)
        if state == "missing":
            add("E", loc, key, f"DOI does not exist: {doi}")
            return "not found", "—", ""
        if state != "ok":
            add("W" if state == "error" else "N", loc, key, f"record could not be read for {doi}: compare by hand")
            return ("unchecked", "—", "") if state == "error" else ("yes", "unchecked", "doi.org")
    elif a:
        time.sleep(3)
        got = arxiv_records([a.group(1)])
        if a.group(1) not in got:
            add("E", loc, key, f"arXiv number does not exist: {a.group(1)}")
            return "not found", "—", ""
        if got[a.group(1)] is None:
            add("W", loc, key, "could not be checked: no answer from arXiv")
            return "unchecked", "—", ""
        r = got[a.group(1)]
        rec = {"title": r["title"], "author": [{"family": x.split()[-1]} for x in r["authors"] if x.split()]}
    else:
        time.sleep(0.4 if args.mailto else 1.1)
        items = crossref_search(detex(text), args.mailto)
        if items is None:
            add("W", loc, key, "could not be checked: no answer from Crossref")
            return "unchecked", "—", ""
        rec = items[0] if items else None
    if not rec:
        add("W", loc, key, "no record found in Crossref: find the work by hand before it is cited")
        return "not found", "—", ""
    auth = record_authors(rec)
    want = {"first author": auth[0][2] if auth else "", "volume": str(rec.get("volume") or ""),
            "page": str(rec.get("page") or rec.get("article-number") or "").split("-")[0],
            "year": " ".join(map(str, sorted(record_years(rec))))}
    words = fold(text).split()
    absent = [k for k, v in want.items() if v and not any(x in words for x in fold(v).split())]
    present = sum(1 for v in want.values() if v) - len(absent)
    if doi or a:
        updates = record_updates(rec, doi or "")
        for level, msg in updates:
            add(level, loc, key, msg)
        tail = ", RETRACTED" if any(l == "E" for l, _ in updates) else ""
        seen = "doi.org" if doi else "arXiv"
        if "first author" in absent and ("year" in absent or present <= 1):
            add("E", loc, key, f"identifier belongs to a different work: '{short(first(rec.get('title')))}'")
            return "yes", "MISMATCH" + tail, seen
        if absent:
            add("W", loc, key, "the record's " + ", ".join(f"{k} ({want[k]})" for k in absent)
                + " not found in the typed reference")
            return "yes", "differs" + tail, seen
        return "yes", "yes" + tail, seen
    if present >= 3 and not absent:
        add("N", loc, key, f"Crossref has a matching record: {rec.get('DOI')}")
        time.sleep(pause)
        state, full = doi_record(rec.get("DOI") or "")
        updates = record_updates(full, rec["DOI"]) if state == "ok" else []
        for level, msg in updates:
            add(level, loc, key, msg)
        return "yes", "yes" + (", RETRACTED" if any(l == "E" for l, _ in updates) else ""), "Crossref search"
    add("W", loc, key, f"no confident match in Crossref (nearest: '{short(first(rec.get('title')), 60)}'): "
                       "find the work by hand before it is cited")
    return "not found", "—", ""


def write_ledger(path, entries, bibitems, cites, status, online, found):
    def cell(x):
        return str(x).replace("|", "\\|")

    def notes(key):
        return cell(short("; ".join(m for l, _, k, m in found if k == key and l in "EW"), 200))
    rows = ["# Reference check", "",
            f"Written by ref_check.py on {date.today().isoformat()}; comparison with the record: "
            f"{'run' if online else 'not run'}.",
            "The script's columns state what it found, not that a reference is right. The rest is filled by hand.",
            "", "## References", "",
            "| Key | Identifier | Exists | Matches record | Seen at | Notes |", "|---|---|---|---|---|---|"]
    for e in entries:
        f = e["fields"]
        ident = clean_doi(f["doi"])[0] if f.get("doi") else ("arXiv:" + entry_arxiv(f) if entry_arxiv(f) else "none")
        ex, ok, seen = status.get(e["key"], ("unchecked", "—", ""))
        rows.append(f"| {cell(e['key'])} | {cell(ident)} | {ex} | {ok} | {seen} | {notes(e['key'])} |")
    for b in bibitems:
        ex, ok, seen = status.get(b["key"], ("unchecked", "—", ""))
        rows.append(f"| {cell(b['key'])} | typed entry | {ex} | {ok} | {seen} | {notes(b['key'])} |")
    rows += ["", "## Citations", "",
             "Function: credit, support, source, method, contrast or background. Read: full, abstract or title. "
             "Supports: yes, partly, no or unchecked.", "",
             "| # | Where | Key | Sentence | Function | Read | Supports | Action |", "|---|---|---|---|---|---|---|---|"]
    n = 0
    for c in cites:
        for k in ([] if c["nocite"] else c["keys"]):
            n += 1
            rows.append(f"| {n} | {cell(c['where'])} | {cell(k)} | {cell(c['sentence'])} |  |  |  |  |")
    rows += ["", "## Coverage", "", "| Line of work | Cited | Missing or thin | Proposal |", "|---|---|---|---|",
             "", "## Open items", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Check citations and the reference list of a LaTeX manuscript.")
    ap.add_argument("tex", nargs="+", help=".tex files (\\input is not followed)")
    ap.add_argument("--bib", nargs="*", default=[], help=".bib files")
    ap.add_argument("--online", action="store_true", help="compare with doi.org, Crossref and arXiv")
    ap.add_argument("--mailto", help="contact address sent to Crossref (higher rate limits)")
    ap.add_argument("--group", type=int, default=4, help="flag citations naming more than this many works (default 4)")
    ap.add_argument("--authors", nargs="*", default=[], help='manuscript authors as "Family, G." for the self-citation share')
    ap.add_argument("--ledger", help="write a Markdown ledger of references and citations to this file")
    ap.add_argument("--force", action="store_true", help="overwrite an existing ledger")
    args = ap.parse_args()

    global UA
    if args.mailto:
        UA = f"complete-paper-ref-check/1.0 (mailto:{args.mailto})"
    found = []                                     # (level, where, key, message)

    def add(level, where, key, msg):
        found.append((level, where, key, msg))

    missing = [p for p in args.tex + args.bib if not os.path.isfile(p)]
    if missing:
        sys.exit("ref_check: no such file: " + ", ".join(missing))
    cites, placeholders, bibitems, nocite_all = read_tex(args.tex)
    entries = []
    for path in args.bib:
        entries += parse_bib(open(path, encoding="utf-8", errors="replace").read(), path)
    if entries and bibitems:                       # a pasted .bbl next to its .bib: the .bib is the source
        typed = {b["key"] for b in bibitems} - {e["key"] for e in entries}
        bibitems = [b for b in bibitems if b["key"] in typed]

    defined = Counter([e["key"] for e in entries] + [b["key"] for b in bibitems])
    lower = defaultdict(set)
    for k in defined:
        lower[k.lower()].add(k)
    where = {e["key"]: e["where"] for e in entries}
    where.update({b["key"]: b["where"] for b in bibitems})
    for k, n in defined.items():
        if n > 1:
            add("E", where[k], k, f"key defined {n} times")
    for variants in lower.values():
        if len(variants) > 1:
            add("W", where[sorted(variants)[0]], sorted(variants)[0], "keys differ only in case: " + ", ".join(sorted(variants)))
    cited, first_seen = Counter(), {}
    for c in cites:
        for k in c["keys"]:
            cited[k] += 1
            first_seen.setdefault(k, c["where"])
    for k in cited:
        if k not in defined:
            hint = f" (differs only in case from {sorted(lower[k.lower()])[0]})" if k.lower() in lower else ""
            add("E", first_seen[k], k, f"cited {cited[k]} time(s), but no such entry{hint}")
    for k in defined:
        if k not in cited:
            add("N", where[k], k, "never cited" + (" (printed anyway by \\nocite{*})" if nocite_all else ""))
    for loc, text in placeholders:
        add("E", loc, "-", f"placeholder left in the text: {text}")
    if not entries and not bibitems:
        add("W", args.tex[0], "-", "no reference list found: pass the .bib file with --bib")

    this_year = date.today().year
    by_doi, by_title = defaultdict(list), defaultdict(list)
    for e in entries:
        if e["broken"]:
            add("E", e["where"], e["key"], "entry is not closed: its braces or quotes do not balance")
        for level, msg in check_entry(e, this_year):
            add(level, e["where"], e["key"], msg)
        if e["fields"].get("doi"):
            by_doi[clean_doi(e["fields"]["doi"])[0].lower()].append(e)
        if len(squash(e["fields"].get("title", ""))) >= 12:
            lead = next((p[0] for p in map(name_parts, split_names(e["fields"].get("author", ""))) if p), "")
            by_title[(squash(e["fields"]["title"]), lead)].append(e)
    for doi, group in by_doi.items():
        if len(group) > 1:
            add("W", group[0]["where"], group[0]["key"], f"same DOI under several keys: {', '.join(g['key'] for g in group)}")
    for group in by_title.values():
        dois = {clean_doi(g["fields"].get("doi", ""))[0].lower() for g in group}
        if len(group) > 1 and (len(dois) > 1 or "" in dois):
            add("W", group[0]["where"], group[0]["key"], "same title and first author under several keys (a duplicate, "
                f"or the preprint and the published version of one work): {', '.join(g['key'] for g in group)}")

    big = [c for c in cites if not c["nocite"] and len(c["keys"]) > args.group]
    for c in big:
        add("N", c["where"], "-", f"{len(c['keys'])} works cited at one point: say what they share, or split them by what each supports")
    alone = {k for c in cites if not c["nocite"] and len(c["keys"]) <= args.group for k in c["keys"]}
    only_grouped = sorted(k for k in cited if k in defined and k not in alone
                          and any(k in c["keys"] for c in big))

    status = {}
    if args.online:
        status = check_online(entries, bibitems, args, add)

    names = {"E": "ERRORS", "W": "WARNINGS", "N": "NOTES"}
    print(f"ref_check: {len(args.tex)} .tex file(s), {len(args.bib)} .bib file(s), {len(entries)} entries, "
          f"{len(bibitems)} typed item(s), {sum(1 for c in cites if not c['nocite'])} citation command(s)")
    for level in "EWN":
        rows = [x for x in found if x[0] == level]
        if rows:
            print(f"\n{names[level]} ({len(rows)})")
            for _, loc, key, msg in rows:
                print(f"  {loc}  {key}: {msg}")

    used = [e for e in entries if e["key"] in cited] or entries
    print("\nSUMMARY")
    print(f"  keys cited {len(cited)} | entries {len(defined)} | cited without entry "
          f"{sum(1 for k in cited if k not in defined)} | entries never cited {sum(1 for k in defined if k not in cited)}")
    if args.online:
        tally = Counter((v[0], v[1]) for v in status.values())
        print("  record check (exists / matches): "
              + (", ".join(f"{n} {ex} / {ok}" for (ex, ok), n in sorted(tally.items())) or "nothing to check"))
    else:
        print("  record check: not run (add --online)")
    years = sorted(int(m.group()) for e in used for m in [re.search(r"\d{4}", e["fields"].get("year") or e["fields"].get("date") or "")] if m)
    if years:
        recent = sum(1 for y in years if y >= this_year - 3)
        print(f"  years: median {years[len(years) // 2]}, newest {years[-1]}, {recent} of {len(years)} from {this_year - 3} or later")
    people = Counter()
    for e in used:
        for p in {label(p) for p in map(name_parts, split_names(e["fields"].get("author", ""))) if p and p[0]}:
            people[p] += 1
    top = [(p, n) for p, n in people.most_common(5) if n >= 3]
    if top:
        print("  most frequent authors (namesakes are merged): " + ", ".join(f"{p} {n}/{len(used)}" for p, n in top))
    if args.authors:
        own = [name_parts(a) for a in args.authors]
        mine = [e for e in used if any(same_name(o[0], p[0]) and (not o[1] or not p[1] or o[1][:1] == p[1][:1])
                                       for o in own if o for p in map(name_parts, split_names(e["fields"].get("author", ""))) if p)]
        if used:
            print(f"  own work: {len(mine)} of {len(used)} references ({100 * len(mine) / len(used):.0f}%)")
    print(f"  citations naming more than {args.group} works: {len(big)}"
          + (f"; cited only inside such groups ({len(only_grouped)}): {', '.join(only_grouped[:15])}"
             + (" …" if len(only_grouped) > 15 else "") if only_grouped else ""))

    if args.ledger:
        if os.path.exists(args.ledger) and not args.force:
            print(f"\nledger not written: {args.ledger} exists (use --force to overwrite it)")
        else:
            write_ledger(args.ledger, entries, bibitems, cites, status, args.online, found)
            print(f"\nledger written: {args.ledger}")
    errors = sum(1 for x in found if x[0] == "E")
    print(f"\n{errors} error(s), {sum(1 for x in found if x[0] == 'W')} warning(s), {sum(1 for x in found if x[0] == 'N')} note(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
