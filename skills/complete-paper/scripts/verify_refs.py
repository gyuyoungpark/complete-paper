#!/usr/bin/env python3
r"""
verify_refs.py: check that references exist and that their metadata match
(complete-paper skill).

Standard library only, Python 3.8 or later. Needs network access.

Input: a .bib file, a .tex file with \bibitem entries, or a .bbl file.
DOIs are looked up on Crossref, arXiv identifiers on arXiv. Fields compared:
first author's family name, year, and title (BibTeX) or volume and page
(\bibitem text, where titles are often omitted).

Status
  verified   the identifier resolves and the compared fields match
  mismatch   the identifier resolves but a field differs (details listed)
  not-found  the identifier does not resolve
  no-id      no DOI or arXiv identifier; with --search, a Crossref candidate
             is suggested, which must be checked by hand
  error      network or parsing problem

A verified record shows that the reference exists and is described
correctly. It does not show that the reference supports the sentence citing
it; read the work for that.

Exit status: 1 if any mismatch or not-found, otherwise 0.

Examples
  python verify_refs.py refs.bib
  python verify_refs.py main.tex --md > paper-state/references-check-raw.md
  python verify_refs.py refs.bib --search --mailto you@example.org
"""

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "complete-paper-verify-refs/0.1"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s{}\"<>,;]+")
ARXIV_RE = re.compile(r"(?:arxiv[:\s/]*(?:abs/)?|eprint\s*=\s*[{\"]?)"
                      r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", re.I)


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def match_close(text, i, open_ch="{", close_ch="}"):
    depth, k = 0, i
    while k < len(text):
        c = text[k]
        if c == "\\":
            k += 2
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return len(text)


def parse_fields(body):
    fields, i, n = {}, 0, len(body)
    name_re = re.compile(r"\s*,?\s*([A-Za-z][\w\-:]*)\s*=\s*")
    while i < n:
        m = name_re.match(body, i)
        if not m:
            break
        name = m.group(1).lower()
        i = m.end()
        if i >= n:
            break
        if body[i] == "{":
            j = match_close(body, i)
            value = body[i + 1:j - 1]
        elif body[i] == '"':
            j = i + 1
            depth = 0
            while j < n and not (body[j] == '"' and depth == 0 and body[j - 1] != "\\"):
                depth += {"{": 1, "}": -1}.get(body[j], 0)
                j += 1
            value = body[i + 1:j]
            j += 1
        else:
            m2 = re.match(r"[^,]*", body[i:])
            value = m2.group().strip()
            j = i + m2.end()
        fields[name] = " ".join(value.split())
        i = j
    return fields


def parse_bib(text):
    entries, pos = [], 0
    head = re.compile(r"@\s*(\w+)\s*([{(])")
    while True:
        m = head.search(text, pos)
        if not m:
            break
        kind = m.group(1).lower()
        open_ch = m.group(2)
        close_ch = "}" if open_ch == "{" else ")"
        end = match_close(text, m.end() - 1, open_ch, close_ch)
        pos = end
        if kind in ("comment", "string", "preamble"):
            continue
        inner = text[m.end():end - 1]
        key, _, body = inner.partition(",")
        fields = parse_fields(body)
        raw = text[m.start():end]
        entries.append({"key": key.strip(), "kind": kind, "fields": fields, "raw": raw})
    return entries


def parse_bibitems(text):
    entries = []
    rx = re.compile(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
    ms = list(rx.finditer(text))
    for idx, m in enumerate(ms):
        end = ms[idx + 1].start() if idx + 1 < len(ms) else len(text)
        stop = text.find("\\end{thebibliography}", m.end(), end)
        if stop >= 0:
            end = stop
        entries.append({"key": m.group(1).strip(), "kind": "bibitem", "fields": {},
                        "raw": text[m.end():end]})
    return entries


def find_ids(entry):
    f, raw = entry["fields"], entry["raw"]
    doi = None
    for src in (f.get("doi", ""), f.get("url", ""), raw):
        m = DOI_RE.search(src)
        if m:
            doi = m.group().rstrip(".)]")
            break
    arxiv = None
    if f.get("eprint") and ("arxiv" in f.get("archiveprefix", "arxiv").lower()):
        m = re.match(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})", f["eprint"].strip(), re.I)
        if m:
            arxiv = m.group(1)
    if not arxiv:
        m = ARXIV_RE.search(raw)
        if m:
            arxiv = m.group(1)
    return doi, arxiv


# --------------------------------------------------------------------------
# Normalization
# --------------------------------------------------------------------------

def norm(s):
    s = re.sub(r"\\[a-zA-Z]+\s*|\\[^a-zA-Z]", "", s or "")
    s = s.replace("{", "").replace("}", "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def first_family(author_field):
    if not author_field:
        return ""
    first = re.split(r"\s+and\s+", author_field)[0].strip()
    if "," in first:
        fam = first.split(",")[0]
    else:
        parts = first.split()
        fam = parts[-1] if parts else ""
    return norm(fam)


def title_similarity(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


# --------------------------------------------------------------------------
# Lookups
# --------------------------------------------------------------------------

def http_get(url, mailto=None, timeout=20):
    ua = USER_AGENT + (" (mailto:%s)" % mailto if mailto else "")
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def crossref_work(doi, mailto):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    msg = json.loads(http_get(url, mailto))["message"]
    year = None
    for k in ("issued", "published-print", "published-online", "created"):
        parts = (msg.get(k) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    authors = msg.get("author") or []
    return {
        "title": (msg.get("title") or [""])[0],
        "family": norm(authors[0].get("family", authors[0].get("name", ""))) if authors else "",
        "families": [norm(a.get("family", a.get("name", ""))) for a in authors],
        "year": year,
        "journal": (msg.get("container-title") or [""])[0],
        "volume": msg.get("volume") or "",
        "page": (msg.get("page") or msg.get("article-number") or "").split("-")[0],
        "article_number": msg.get("article-number") or "",
        "type": msg.get("type", ""),
    }


def arxiv_record(arxiv_id, mailto):
    try:
        xml = http_get("https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv_id), mailto)
        ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
        root = ET.fromstring(xml)
        e = root.find("a:entry", ns)
        if e is not None and e.find("a:title", ns) is not None:
            title = " ".join((e.find("a:title", ns).text or "").split())
            if title and title.lower() != "error":
                authors = [norm((a.find("a:name", ns).text or "").split()[-1]) for a in e.findall("a:author", ns)]
                pub = (e.find("a:published", ns).text or "")[:4]
                doi_el = e.find("x:doi", ns)
                return {"title": title, "family": authors[0] if authors else "", "families": authors,
                        "year": int(pub) if pub.isdigit() else None,
                        "published_doi": doi_el.text if doi_el is not None else ""}
    except (urllib.error.URLError, ET.ParseError, ValueError, OSError):
        pass
    html = http_get("https://arxiv.org/abs/" + urllib.parse.quote(arxiv_id), mailto)
    m = re.search(r'<meta name="citation_title" content="([^"]*)"', html)
    if not m:
        raise LookupError("not found")
    authors = re.findall(r'<meta name="citation_author" content="([^"]*)"', html)
    d = re.search(r'<meta name="citation_date" content="(\d{4})', html)
    doi = re.search(r'<meta name="citation_doi" content="([^"]*)"', html)
    return {"title": m.group(1), "family": norm(authors[0].split(",")[0]) if authors else "",
            "families": [norm(a.split(",")[0]) for a in authors],
            "year": int(d.group(1)) if d else None, "published_doi": doi.group(1) if doi else ""}


def crossref_search(entry, mailto):
    f = entry["fields"]
    q = " ".join(x for x in (f.get("title", ""), f.get("author", "").split(" and ")[0],
                             f.get("journal", ""), f.get("year", "")) if x)
    if not q.strip():
        q = re.sub(r"\\[a-zA-Z]+|[{}]", " ", entry["raw"])[:250]
    url = "https://api.crossref.org/works?rows=1&query.bibliographic=" + urllib.parse.quote(q)
    items = json.loads(http_get(url, mailto))["message"].get("items") or []
    if not items:
        return None
    it = items[0]
    return {"doi": it.get("DOI", ""), "title": (it.get("title") or [""])[0], "score": it.get("score")}


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

def compare(entry, rec):
    problems, notes = [], []
    f = entry["fields"]
    # identifiers and links contain volume and page numbers; drop them before matching
    raw = re.sub(r"https?://\S+|doi:\s*\S+|" + DOI_RE.pattern + r"|" + ARXIV_RE.pattern, " ",
                 entry["raw"], flags=re.I)
    raw_norm = norm(raw)
    if f:
        fam = first_family(f.get("author", ""))
        if fam and rec.get("family") and fam != rec["family"]:
            if fam in rec.get("families", []):
                problems.append("first author is '%s' here but '%s' in the record ('%s' is a later author)"
                                % (fam, rec["family"], fam))
            else:
                problems.append("first author '%s' vs record '%s'" % (fam, rec["family"]))
        y = re.search(r"\d{4}", f.get("year", "") or f.get("date", ""))
        if y and rec.get("year"):
            dy = abs(int(y.group()) - int(rec["year"]))
            if dy > 1:
                problems.append("year %s vs record %s" % (y.group(), rec["year"]))
            elif dy == 1:
                notes.append("year %s vs record %s (online/print dates may differ)" % (y.group(), rec["year"]))
        if f.get("title") and rec.get("title"):
            sim = title_similarity(f["title"], rec["title"])
            if sim < 0.85:
                problems.append("title differs (similarity %.2f): record title '%s'" % (sim, rec["title"][:90]))
        if f.get("volume") and rec.get("volume") and norm(f["volume"]) != norm(rec["volume"]):
            problems.append("volume %s vs record %s" % (f["volume"], rec["volume"]))
        pages = (f.get("pages") or f.get("eid") or "").split("-")[0].strip()
        if pages and rec.get("page") and norm(pages) != norm(rec["page"]) \
                and norm(pages) != norm(rec.get("article_number", "")):
            problems.append("page %s vs record %s" % (pages, rec["page"]))
    else:
        if rec.get("family") and rec["family"] not in raw_norm:
            problems.append("record's first author '%s' not found in the entry" % rec["family"])
        if rec.get("year") and str(rec["year"]) not in raw:
            near = [str(int(rec["year"]) + d) for d in (-1, 1)]
            if any(n in raw for n in near):
                notes.append("year differs by one from the record (%s)" % rec["year"])
            else:
                problems.append("record's year %s not found in the entry" % rec["year"])
        if rec.get("volume") and not re.search(r"(?<!\d)%s(?!\d)" % re.escape(str(rec["volume"])), raw):
            problems.append("record's volume %s not found in the entry" % rec["volume"])
        page = rec.get("page") or rec.get("article_number")
        if page and norm(page) not in raw_norm:
            problems.append("record's page or article number %s not found in the entry" % page)
    return problems, notes


def verify(entry, args):
    doi, arxiv = find_ids(entry)
    result = {"key": entry["key"], "doi": doi or "", "arxiv": arxiv or "", "status": "", "details": []}
    try:
        if doi:
            try:
                rec = crossref_work(doi, args.mailto)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    result["status"] = "not-found"
                    result["details"].append("DOI %s is not registered with Crossref (check it at "
                                             "https://doi.org/%s; DataCite DOIs are not covered)" % (doi, doi))
                    return result
                raise
        elif arxiv:
            try:
                rec = arxiv_record(arxiv, args.mailto)
            except (LookupError, urllib.error.HTTPError):
                result["status"] = "not-found"
                result["details"].append("arXiv identifier %s does not resolve" % arxiv)
                return result
            if rec.get("published_doi"):
                result["details"].append("a published version exists: DOI %s; cite it if the venue prefers"
                                         % rec["published_doi"])
        else:
            result["status"] = "no-id"
            if args.search:
                cand = crossref_search(entry, args.mailto)
                if cand:
                    result["details"].append("candidate (verify by hand): DOI %s, '%s'"
                                             % (cand["doi"], cand["title"][:90]))
            else:
                result["details"].append("no DOI or arXiv identifier; find the record and add one, "
                                         "or run with --search")
            return result
        problems, notes = compare(entry, rec)
        result["status"] = "mismatch" if problems else "verified"
        result["details"] = problems + notes + result["details"]
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        result["status"] = "error"
        result["details"].append("lookup failed: %s" % e)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help=".bib, .tex (with \\bibitem) or .bbl file")
    ap.add_argument("--search", action="store_true",
                    help="for entries without an identifier, ask Crossref for a candidate match")
    ap.add_argument("--mailto", help="contact address for Crossref's polite pool (optional; your choice)")
    ap.add_argument("--keys", help="comma-separated keys to check (default: all)")
    ap.add_argument("--delay", type=float, default=0.2, help="seconds between requests (default 0.2)")
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="print JSON")
    fmt.add_argument("--md", action="store_true", help="print a Markdown table")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    with open(args.file, encoding="utf-8", errors="replace") as f:
        text = f.read()
    text = re.sub(r"(?<!\\)%.*", "", text) if not args.file.endswith(".bib") else text
    entries = parse_bib(text) if args.file.endswith(".bib") else parse_bibitems(text)
    if args.keys:
        wanted = {k.strip() for k in args.keys.split(",")}
        entries = [e for e in entries if e["key"] in wanted]
    if not entries:
        sys.exit("no entries found in %s" % args.file)

    results = []
    for i, e in enumerate(entries):
        results.append(verify(e, args))
        if i + 1 < len(entries):
            time.sleep(args.delay)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    date = time.strftime("%Y-%m-%d")
    if args.json:
        print(json.dumps({"checked": date, "results": results, "summary": counts}, ensure_ascii=False, indent=2))
    elif args.md:
        print("Checked %s with verify_refs.py\n" % date)
        print("| Key | Identifier | Status | Details |")
        print("|-----|------------|--------|---------|")
        for r in results:
            ident = ("doi:" + r["doi"]) if r["doi"] else (("arXiv:" + r["arxiv"]) if r["arxiv"] else "")
            print("| %s | %s | %s | %s |" % (r["key"], ident, r["status"], "; ".join(r["details"]).replace("|", "/")))
    else:
        for r in results:
            ident = r["doi"] or r["arxiv"] or "-"
            print("%-10s %-28s %s" % (r["status"], r["key"][:28], ident))
            for d in r["details"]:
                print("           - %s" % d)
    if not args.json:
        print("\nSummary: " + ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items())))
    sys.exit(1 if counts.get("mismatch") or counts.get("not-found") else 0)


if __name__ == "__main__":
    main()
