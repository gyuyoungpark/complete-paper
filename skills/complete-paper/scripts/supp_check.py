#!/usr/bin/env python3
"""Check how a manuscript uses its supplement: callouts, reachability, size, data, style.

Usage:
    python3 supp_check.py main.tex --supp supplement.tex
    python3 supp_check.py paper.tex                        (supplement in the same file: the split is found)
    python3 supp_check.py main.tex --supp supplement.tex --ledger suppmap.md

A file given with --supp that the main file also \\inputs is read as the supplement only.

    --supp FILE [FILE ...]   source files of the supplement
    --split REGEX            where the supplement starts when it shares a file with the main text
    --ratio R                largest supplement-to-main ratio, for words and for display items (default 1.0)
    --per-1000 N             callout budget per 1000 words of main text (default 2). The budget is the larger of
                             this and one callout per supplementary section, and never less than 3
    --per-paragraph N        most callout sentences in one paragraph (default 1)
    --sm-key KEY [KEY ...]   citation keys that stand for the supplement (found by itself in a typed reference list)
    --pages MAIN SUPP        page counts when known (read from main.pdf and the supplement's PDF if pdfinfo is installed)
    --ledger FILE            write the item and callout tables to FILE (suppmap.md); --force overwrites it

What is checked:
  callouts   every sentence of the main text that sends the reader to the supplement: how many (text
             and captions count; the statements at the end do not), where (abstract, conclusion),
             whether it names a place, whether that place exists
  reach      every supplementary figure, table and section must be cited: from the main text, or from
             a part of the supplement that the main text points to. An item cited nowhere is an error.
             A contents list or a cover page names items without citing them
  order      sections and floats of the supplement in the order in which they are first cited
  size       words, display items, equations and pages of main text and supplement, and their ratios
  data       items that look like data rather than argument: long tables, listings, galleries, runs of
             near-identical figures. They are candidates for the data package
  style      macros defined differently in the two files; "Fig." against "Figure"; a missing S prefix;
             floats without caption or label; a supplement that does not name the paper; sections that
             do not say which statement of the main text they support; references cited only in the
             supplement; the data availability statement

The script reads LaTeX source. It follows \\input and \\include, does not expand macros, and numbers
supplementary floats and sections in their order of appearance. Whether an item is needed, and whether
a callout is worth its interruption, is for the author to judge: the script lists what to judge.
Standard library only. Exit status is 1 if any error is reported, otherwise 0.
"""
import argparse
import bisect
import datetime
import difflib
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, OrderedDict, defaultdict

FLOAT_ENVS = {"figure": "fig", "SCfigure": "fig", "sidewaysfigure": "fig", "table": "table", "sidewaystable": "table",
              "longtable": "table", "video": "movie", "algorithm": "algorithm"}
NAME = {"fig": "Fig.", "table": "Table", "sec": "Sec.", "eq": "Eq.", "movie": "Movie", "data": "Data",
        "algorithm": "Algorithm", "ed": "Extended Data"}
PLURAL = {"fig": "figure", "table": "table", "sec": "section", "movie": "movie", "data": "data file", "algorithm": "algorithm"}
KIND_WORDS = [("fig", r"Figs?\.?|Figures?"), ("table", r"Tables?|Tabs?\.?"),
              ("sec", r"Secs?\.?|Sections?|Notes?|Appendix|Appendices"), ("eq", r"Eqs?\.?|Equations?"),
              ("movie", r"Movies?|Videos?"), ("data", r"Data(?:sets?)?|Files?"), ("algorithm", r"Algorithms?")]
WORDS = "|".join(w for _, w in KIND_WORDS)
GAP = r"(?:\s|~|\\,|\\ |\\;)*"
NUM = r"S?\s?\d+[A-Za-z]?(?:\([a-z]\))?"
JOIN = r"(?:--?-?|\u2013|\u2014|\bto\b|\band\b|,|&|;)"
SEQ = rf"{NUM}(?:{GAP}{JOIN}{GAP}(?:and{GAP})?\(?{NUM}\)?)*"
TYPED_S = re.compile(rf"(?<![A-Za-z])({WORDS}){GAP}\(?(S{GAP}\d+[A-Za-z]?(?:\([a-z]\))?(?:{GAP}{JOIN}{GAP}(?:and{GAP})?\(?{NUM}\)?)*)")
TYPED_W = re.compile(rf"(?<![A-Za-z])(Supplement(?:al|ary)|Suppl?\.|Supporting|Extended{GAP}Data){GAP}({WORDS}){GAP}\(?({SEQ})", re.I)
GENERIC = re.compile(r"(?<![A-Za-z])(Supplement(?:al|ary)\s+(?:Materials?|Information|Text|Methods|Discussion|Notes|Data|Files?|Document)"
                     r"|Supporting\s+Information|(?:the|our|online)\s+Supplement\b)", re.I)
ABBR_DEF = re.compile(r"(?:Supplement(?:al|ary)\s+(?:Materials?|Information)|Supporting\s+Information)\s*\((SM|SI|SOM|ESI)\)")
REF = re.compile(r"\\[A-Za-z]*[Rr]ef\*?\s*\{([^}]*)\}")       # \ref, \eqref, \cref, \autoref and home-made \figref
CITE = re.compile(r"\\(?:cite|citep|citet|citealp|citealt|onlinecite|parencite|textcite|footcite|autocite|supercite)\*?"
                  r"\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}")
HEADING = re.compile(r"\\(section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\]\s*)?\{")
SUPP_TITLE = r"Supplement(?:al|ary)\s+(?:Materials?|Information|Notes?)|Supporting\s+Information|Supplementary\s+Online"
WHOLE_TITLE = re.compile(r"^(?:Supplement(?:al|ary)\s+(?:Materials?|Information)|Supporting\s+Information)\b(?!\s*\d)|^References$|^Contents$", re.I)
COVER = re.compile(r"^(?:This\s+PDF\s+file\s+includes|Other\s+Supplement(?:al|ary)\s+Materials?|(?:Table\s+of\s+)?Contents|List\s+of)\b", re.I)
# where a supplement starts inside a file that also holds the main text
S_PREFIX = re.compile(r"\\renewcommand\*?\s*\{?\\the(?:figure|table|equation|section)\}?\s*\{\s*(?:\\[A-Za-z]+\s*\{?\s*)?S"
                      r"|\\renewcommand\*?\s*\{?\\(?:figurename|tablename)\}?\s*\{\s*Supp")
RESET = re.compile(r"\\setcounter\s*\{(?:figure|table|equation|section)\}\s*\{0\}|\\setcounter\s*\{page\}\s*\{1\}")
TITLE_SPLIT = re.compile(rf"\\(?:section|part|chapter|title)\*?\s*\{{[^{{}}]*(?:{SUPP_TITLE})"
                         rf"|\\begin\{{center\}}[^\n]*\n?[^\n]*(?:{SUPP_TITLE})"
                         rf"|\{{\s*(?:\\[A-Za-z]+\s*)+(?:{SUPP_TITLE})", re.I)
BREAK = re.compile(r"\\(?:clearpage|newpage|cleardoublepage|pagebreak|onecolumngrid|twocolumngrid|widetext)\b")
NUMBERED_EQ = "equation|align|gather|multline|eqnarray|flalign|alignat"
MAIN_POINTER = re.compile(rf"\b(main\s+(?:text|article|paper|manuscript)|the\s+Letter|the\s+Article)\b"
                          rf"|(?<![A-Za-z])(?:Figs?\.?|Figures?|Eqs?\.?|Equations?|Secs?\.?|Sections?|Tables?){GAP}\(?\d", re.I)
BACK_MATTER = re.compile(r"acknowledg|data\s+availab|code\s+availab|availability|author\s+contrib|competing|conflict|declaration|funding"
                         r"|^supplement(?:al|ary)\s+(?:materials?|information)\s*$|^supporting\s+information\s*$", re.I)
CLOSING = re.compile(r"^\W*(?:\w+\s+(?:and|&)\s+)?(?:conclu|summary|outlook)", re.I)
DATA_PHRASE = re.compile(r"\braw\s+(?:data|traces|images|spectra)\b|\ball\s+(?:the\s+)?(?:samples|devices|runs|measurements|curves|traces)\b"
                         r"|\bfull\s+(?:data\s?set|list|sweep|set)\b|\bcomplete\s+(?:set|list)\b", re.I)
DAS = re.compile(r"data\s+(?:and\s+(?:code|materials)\s+)?availability|availability\s+of\s+(?:data|code)|data\s+access|\bdata\s+that\s+supports?\b"
                 r"|\bdata\b[^.]{0,120}?\b(?:are|is|will\s+be|have\s+been|has\s+been)\s+(?:made\s+)?(?:openly\s+|publicly\s+|freely\s+)?"
                 r"(?:available|deposited)\b", re.I)
REPOSITORY = re.compile(r"zenodo|figshare|dryad|osf\.io|dataverse|materials\s?cloud|nomad|github|gitlab|doi\.org|10\.\d{4,9}/", re.I)
NOT_SHARED = {"\\thefigure", "\\thetable", "\\theequation", "\\thesection", "\\thesubsection", "\\thepage", "\\figurename",
              "\\tablename", "\\refname", "\\bibnumfmt", "\\citenumfont", "\\appendixname", "\\abstractname", "\\thefootnote"}
FORMS = {"figure": (rf"Figs?\.{GAP}(?:\\ref|\(?S?\d)", rf"Figures?{GAP}(?:\\ref|\(?S?\d)"),
         "equation": (rf"Eqs?\.{GAP}(?:\\eqref|\\ref|\(?S?\d|\(\\ref)", rf"Equations?{GAP}(?:\\eqref|\\ref|\(?S?\d|\(\\ref)"),
         "section": (rf"Secs?\.{GAP}(?:\\ref|S?\d|[IVX]+\b)", rf"Sections?{GAP}(?:\\ref|S?\d|[IVX]+\b)")}
ABBREV = re.compile(r"\b(Figs?|Eqs?|Secs?|Refs?|Tabs?|Suppl?|Nos?|vs|cf|ca|al|e\.g|i\.e|etc|approx|resp)\.")


# ---------- reading ----------

def read_tex(path, depth=0, skip=(), skipped=None):
    """[(file, line number, text)], comments removed, \\input, \\include and \\subfile followed.

    Files in `skip` are not followed (a main file that inputs its supplement); they are noted in `skipped`."""
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit(f"supp_check: cannot read {path}: {exc.strerror}")
    folder, out = os.path.dirname(os.path.abspath(path)), []
    for n, line in enumerate(raw.split("\n"), 1):
        line = re.sub(r"(?<!\\)%.*", "", line)
        m = re.search(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", line)
        if m and depth < 5:
            found = next((os.path.join(folder, c) for c in (m.group(1).strip(), m.group(1).strip() + ".tex")
                          if os.path.isfile(os.path.join(folder, c))), None)
            if found and os.path.abspath(found) in skip:
                if skipped is not None:
                    skipped.append(found)
                continue
            if found:
                out.extend(read_tex(found, depth + 1, skip, skipped))
                continue
        out.append((path, n, line))
    return out


class Doc:
    def __init__(self, lines):
        self.lines = lines
        self.text = "\n".join(t for _, _, t in lines)
        self.offsets, pos = [], 0
        for _, _, t in lines:
            self.offsets.append(pos)
            pos += len(t) + 1

    def line_index(self, pos):
        return max(bisect.bisect_right(self.offsets, pos) - 1, 0)

    def where(self, pos):
        if not self.lines:
            return "?"
        f, n, _ = self.lines[self.line_index(pos)]
        name = os.path.basename(f)
        return f"{name if len(name) <= 22 else name[:12] + chr(0x2026) + name[-7:]}:{n}"

    def files(self):
        return list(OrderedDict.fromkeys(os.path.basename(f) for f, _, _ in self.lines))


def group(text, i):
    """The content of the brace group opening at text[i], and the position after it."""
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return text[i + 1:], len(text)


def blank(text, spans):
    """The text with the given spans replaced by spaces; line breaks stay, so positions stay valid."""
    chars = list(text)
    for a, b in spans:
        for k in range(a, min(b, len(chars))):
            if chars[k] != "\n":
                chars[k] = " "
    return "".join(chars)


def plain(tex):
    t = re.sub(r"\\(?:cite\w*|onlinecite|label|bibliography\w*|includegraphics|vspace|hspace|pagestyle|externaldocument)"
               r"\*?\s*(?:\[[^\]]*\]\s*)*\{[^{}]*\}", " ", tex)
    t = re.sub(r"\\(?:ref|cref|Cref|eqref|autoref)\*?\s*\{[^{}]*\}", "0", t)
    t = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]", " ", t, flags=re.S)
    t = re.sub(rf"\\begin\{{({NUMBERED_EQ})\*?\}}.*?\\end\{{\1\*?\}}", " ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", "x", t)
    t = re.sub(r"\\(?:begin|end)\{[^{}]*\}(?:\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\.", " ", t)
    return re.sub(r"\s+", " ", re.sub(r"[{}~]", " ", t)).strip()


def count_words(tex):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", plain(tex)))


def short(tex, n=96):
    t = plain(re.sub(r"\$[^$]*\$", "\u2026", tex))
    return t if len(t) <= n else t[: n - 1].rstrip() + "\u2026"


def bare(tex):
    """A piece of source without its headings and labels, for quoting."""
    return re.sub(r"\\(?:sub)*(?:section|paragraph)\*?\s*(?:\[[^\]]*\]\s*)?\{[^{}]*\}|\\label\s*\{[^{}]*\}", " ", tex)


def compact(places):
    """'a.tex:3, a.tex:9' -> 'a.tex:3, 9' when every place is in one file."""
    files = {p.rsplit(":", 1)[0] for p in places}
    if len(files) != 1 or len(places) < 2:
        return ", ".join(places)
    return places[0] + ", " + ", ".join(p.rsplit(":", 1)[1] for p in places[1:])


def sentences(text):
    """(start, end) of the sentences of a paragraph of TeX source."""
    masked = ABBREV.sub(lambda m: m.group(0)[:-1] + "\x00", text)
    masked = re.sub(r"(?<=\d)\.(?=\d)", "\x00", masked)
    cuts = [m.end() for m in re.finditer(r"[.!?][)\]}'\"]*(?=\s+[A-Z\\(\[`])", masked)]
    spans, start = [], 0
    for c in cuts + [len(text)]:
        if text[start:c].strip():
            spans.append((start, c))
        start = c
    return spans


# ---------- structure ----------

def body_range(doc):
    a = doc.text.find("\\begin{document}")
    b = doc.text.rfind("\\end{document}")
    return (a + len("\\begin{document}") if a >= 0 else 0), (b if b >= 0 else len(doc.text))


def floats(text):
    out = []
    for m in re.finditer(r"\\begin\{(%s)(\*?)\}" % "|".join(FLOAT_ENVS), text):
        closing = "\\end{%s%s}" % (m.group(1), m.group(2))
        end = text.find(closing, m.end())
        if end < 0:
            continue
        inner = text[m.end():end]
        cap = re.search(r"\\caption\*?\s*(?:\[[^\]]*\]\s*)?\{", inner)
        out.append({"kind": FLOAT_ENVS[m.group(1)], "env": m.group(1), "start": m.start(), "end": end + len(closing),
                    "caption": group(inner, cap.end() - 1)[0] if cap else "",
                    "labels": re.findall(r"\\label\s*\{([^}]*)\}", inner),
                    "graphics": len(re.findall(r"\\includegraphics", inner)),
                    "panels": len(re.findall(r"\\subfloat|\\subfigure|\\begin\{subfigure\}|\\subcaption", inner)),
                    "rows": len(re.findall(r"\\\\", inner)) if re.search(r"\\begin\{(?:tabular|tabularx|longtable)", "\\begin{%s}" % m.group(1) + inner) else 0})
    return out


def headings(text):
    out = []
    for m in HEADING.finditer(text):
        title, after = group(text, m.end() - 1)
        tail = text[after:after + 160].split("\n\n")[0]
        label = re.search(r"\\label\s*\{([^}]*)\}", tail)
        out.append({"pos": m.start(), "level": {"section": 1, "subsection": 2, "subsubsection": 3}[m.group(1)],
                    "title": plain(title), "label": label.group(1) if label else None, "end": after})
    return out


def paragraphs(flow, a, b):
    """(start, end) of blocks of text between blank lines, inside flow[a:b]."""
    return [(a + m.start(), a + m.end()) for m in re.finditer(r"(?:[^\n]*\S[^\n]*\n?)+", flow[a:b])]


def kind_of(word):
    for kind, pattern in KIND_WORDS:
        if re.fullmatch(pattern, word, re.I):
            return kind
    return "fig"


def numbers(seq):
    out, span = [], False
    for dash, num in re.findall(r"(--?-?|\u2013|\u2014|\bto\b)|S?\s?(\d+)", seq):
        if dash:
            span = True
            continue
        n = int(num)
        if span and out and 0 < n - out[-1] <= 40:
            out.extend(range(out[-1] + 1, n + 1))
        else:
            out.append(n)
        span = False
    return out


def mentions(text, labels, prefix="", abbr=None, sm_keys=()):
    """References to the supplement in a piece of TeX: ([(kind, number)], generic?, position of the first one)."""
    found, taken, hits = [], [], []
    for m in REF.finditer(text):
        for key in m.group(1).split(","):
            key = key.strip()
            item = labels.get(key) or (labels.get(key[len(prefix):]) if prefix and key.startswith(prefix) else None)
            if item:
                found.append((m.start(), item))
    for m in TYPED_W.finditer(text):
        tier = "ed" if m.group(1).lower().startswith("extended") else kind_of(m.group(2))
        found.extend((m.start(), (tier, n)) for n in numbers(m.group(3)))
        taken.append(m.span())
    for m in TYPED_S.finditer(text):
        if not any(a <= m.start() < b for a, b in taken):
            found.extend((m.start(), (kind_of(m.group(1)), n)) for n in numbers(m.group(2)))
    m = GENERIC.search(text)
    if m:
        hits.append(m.start())
    m = re.search(rf"(?<![A-Za-z]){abbr}(?![A-Za-z])(?!\s+units?)", text) if abbr else None
    if m:
        hits.append(m.start())
    for m in CITE.finditer(text):
        if any(k.strip() in sm_keys for k in m.group(1).split(",")):
            hits.append(m.start())
    found.sort(key=lambda f: f[0])
    first = min([f[0] for f in found] + hits, default=None)
    return list(OrderedDict.fromkeys(t for _, t in found)), bool(hits), first


def macros(text):
    out = {}
    pattern = re.compile(r"\\(?:re)?newcommand\*?\s*\{?(\\[A-Za-z@]+)\}?\s*(?:\[\d\])?(?:\[[^\]]*\])?\s*\{"
                         r"|\\providecommand\*?\s*\{?(\\[A-Za-z@]+)\}?\s*(?:\[\d\])?\s*\{"
                         r"|\\def\s*(\\[A-Za-z@]+)[^{\n]*\{|\\DeclareMathOperator\*?\s*\{(\\[A-Za-z@]+)\}\s*\{")
    for m in pattern.finditer(text):
        name = next(g for g in m.groups() if g)
        out[name] = re.sub(r"\s+", " ", group(text, m.end() - 1)[0]).strip()
    return out


def cite_keys(text):
    return {k.strip() for m in CITE.finditer(text) for k in m.group(1).split(",") if k.strip()}


def pdf_pages(path):
    if not (os.path.isfile(path) and shutil.which("pdfinfo")):
        return None
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return int(m.group(1)) if m else None


# ---------- the supplement ----------

def find_split(text, start):
    """Where the supplement begins in a file that also holds the main text; None if no beginning is found."""
    body = text[start:]
    cands = sorted([(m.start(), m.end(), "prefix") for m in S_PREFIX.finditer(body)] +
                   [(m.start(), m.end(), "reset") for m in RESET.finditer(body)] +
                   [(m.start(), m.end(), "title") for m in TITLE_SPLIT.finditer(body)] +
                   [(m.start(), m.end(), "break") for m in BREAK.finditer(body)])
    titles = [c for c in cands if c[2] == "title"]
    anchor = next((c for c in cands if c[2] == "prefix"), None)
    if anchor is None:                                   # counters set back to zero next to a title
        anchor = next((c for c in cands if c[2] == "reset" and
                       any(body.count("\n", min(c[0], t[0]), max(c[0], t[0])) <= 25 for t in titles)), None)
    if anchor is None:
        anchor = titles[0] if titles else None
    if anchor is None:
        return None
    cut = anchor[0]
    for c in reversed([c for c in cands if c[0] < cut]):  # take along the title, the page break and the resets before it
        if count_words(body[c[1]:cut]) < (150 if c[2] == "title" else 12):
            cut = c[0]
        else:
            break
    return start + cut


def inventory(text):
    """Items of the supplement: sections, floats and declared files, numbered in order of appearance."""
    heads = [h for h in headings(text) if not WHOLE_TITLE.search(h["title"]) and not COVER.search(h["title"])]
    level = min((h["level"] for h in heads), default=None)
    units = [h for h in heads if h["level"] == level]
    for k, u in enumerate(units):
        u["span"] = (u["pos"], units[k + 1]["pos"] if k + 1 < len(units) else len(text))
    items, labels = OrderedDict(), {}

    def unit_at(pos):
        return next((k for k, u in enumerate(units) if u["span"][0] <= pos < u["span"][1]), None)

    for k, u in enumerate(units, 1):
        items[("sec", k)] = {"name": f"Sec. S{k}", "title": u["title"], "pos": u["pos"], "unit": k - 1, "labels": []}
        if u["label"]:
            labels[u["label"]] = ("sec", k)
            items[("sec", k)]["labels"].append(u["label"])
    for h in heads:                                       # labels of deeper headings lead to their section
        if h["level"] != level and h["label"] and unit_at(h["pos"]) is not None:
            labels[h["label"]] = ("sec", unit_at(h["pos"]) + 1)
    counts, fl = defaultdict(int), floats(text)
    for f in fl:
        counts[f["kind"]] += 1
        key = (f["kind"], counts[f["kind"]])
        f["key"] = key
        items[key] = {"name": f"{NAME[f['kind']]} S{key[1]}", "title": f["caption"], "pos": f["start"],
                      "unit": unit_at(f["start"]), "labels": f["labels"], "float": f}
        for lab in f["labels"]:
            labels[lab] = key
    flow = blank(text, [(f["start"], f["end"]) for f in fl])
    for m in re.finditer(r"(?m)^[ \t]*(?:\\noindent\s*)?(?:\\textbf\s*\{|\{\\bf\s+|\\paragraph\*?\s*\{)?\s*"
                         r"(Movie|Video|Audio|Data|Dataset|File|Code)\s+S?(\d+)\b", flow):
        key = ("movie" if m.group(1) in ("Movie", "Video", "Audio") else "data", int(m.group(2)))
        if key not in items:
            items[key] = {"name": f"{NAME[key[0]]} S{key[1]}", "title": short(flow[m.start():m.start() + 200], 70),
                          "pos": m.start(), "unit": unit_at(m.start()), "labels": [], "declared": True}
    n = 0
    for m in re.finditer(rf"\\begin\{{({NUMBERED_EQ})\}}(.*?)\\end\{{\1\}}", text, re.S):
        n += 1
        for lab in re.findall(r"\\label\s*\{([^}]*)\}", m.group(2)):
            labels[lab] = ("eq", n)
    return items, labels, units, fl


def reach(items, units, cited_by_unit, front_cites, direct, generic):
    """Which units a reader of the main text arrives at, and which items are cited on the way."""
    entered, reachable = set(), set(direct)
    if not units:
        if direct or generic:
            reachable |= set(front_cites)
        return entered, reachable
    for key in direct:
        if key in items and items[key]["unit"] is not None:
            entered.add(items[key]["unit"])
    queue = set(front_cites) if (generic or direct) else set()
    if generic and not direct:                           # only the supplement as a whole is cited: the reader browses
        entered |= set(range(len(units)))
    grew = True
    while grew:
        grew = False
        for u in list(entered):
            queue |= cited_by_unit.get(u, set())
        for key in list(queue):
            if key not in reachable:
                reachable.add(key)
                grew = True
            if key in items and items[key]["unit"] is not None and items[key]["unit"] not in entered:
                entered.add(items[key]["unit"])
                grew = True
    return entered, reachable


# ---------- the check ----------

def check(main, supp, shared_preamble, opts):
    found = []

    def add(level, where, msg):
        if (level, where, msg) not in found:
            found.append((level, where, msg))

    # ----- the supplement's items
    items, labels, units, sfloats = ({}, {}, [], [])
    stext = ""
    if supp is not None:
        a, b = body_range(supp)
        stext = blank(supp.text, [(0, a), (b, len(supp.text))]) if (a or b < len(supp.text)) else supp.text
        stext = blank(stext, [(m.start(), m.end()) for m in re.finditer(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", stext, re.S)])
        items, labels, units, sfloats = inventory(stext)
    prefix = ""
    m = re.search(r"\\externaldocument\s*\[([^\]]*)\]", main.text)
    if m:
        prefix = m.group(1)

    # ----- the main text
    a, b = body_range(main)
    mtext = blank(main.text, [(0, a), (b, len(main.text))])
    bib = [(m.start(), m.end()) for m in re.finditer(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", mtext, re.S)]
    sm_keys = set(opts.sm_key or [])
    for s, e in bib:                                      # a typed list: which entry is the supplement?
        for entry in re.finditer(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}([^\\]*(?:\\(?!bibitem|end\{thebibliography)[^\\]*)*)", mtext[s:e]):
            if re.search(SUPP_TITLE, entry.group(2), re.I):
                sm_keys.add(entry.group(1).strip())
    mtext = blank(mtext, bib)
    abbr = ABBR_DEF.search(main.text)
    abbr = abbr.group(1) if abbr else None
    mfloats = floats(mtext)
    flow = blank(mtext, [(f["start"], f["end"]) for f in mfloats])
    heads = headings(flow)
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", flow, re.S)
    abstract_span = (abstract.start(), abstract.end()) if abstract else None

    def section_of(pos):
        if abstract_span and abstract_span[0] <= pos < abstract_span[1]:
            return "Abstract"
        top = [h for h in heads if h["pos"] <= pos and h["level"] <= 2]
        if not top:
            return ""
        last = top[-1]
        if last["level"] == 2:                           # a subsection keeps the name of a back-matter or closing section
            above = [h for h in top if h["level"] == 1]
            if above and (BACK_MATTER.search(above[-1]["title"]) or CLOSING.search(above[-1]["title"])):
                return above[-1]["title"]
        return last["title"]

    made = flow.find("\\maketitle")
    pars = [p for p in paragraphs(flow, a, b) if count_words(flow[p[0]:p[1]]) >= 8 and
            (p[0] >= made or (abstract_span and abstract_span[0] <= p[0] < abstract_span[1]) or
             not re.match(r"\s*\\(?:title|author|affiliation|address|date|email|thanks|preprint|collaboration)\b", flow[p[0]:p[1]]))]
    run_in = re.compile(r"\s*(?:\\begin\{acknowledg|\\acknowledg|(?:\\(?:paragraph|subparagraph|section|subsection|textbf|textit|emph|textsc)\*?\s*\{|\{\\(?:it|bf|em)\s+)"
                        r"\s*(?:Acknowledg|Data|Code|Author|Competing|Conflict|Declaration|Funding))", re.I)
    back = [p for p in pars if BACK_MATTER.search(section_of(p[0])) or run_in.match(flow[p[0]:p[1]])]
    text_pars = [p for p in pars if p not in back]
    closing = None
    for p in reversed(text_pars):
        if CLOSING.search(section_of(p[0])) or re.match(r"\s*(?:\\\w+\{)?\s*(?:In\s+(?:summary|conclusion|closing)|To\s+(?:summari[sz]e|conclude))\b", flow[p[0]:p[1]]):
            closing = p
            break
    main_words = sum(count_words(flow[p[0]:p[1]]) for p in text_pars)
    callouts, per_par, placeless, only_generic = [], defaultdict(int), [], False

    def scan(piece_start, piece, place, par_id):
        for s, e in sentences(piece):
            targets, generic, first = mentions(piece[s:e], labels, prefix, abbr, sm_keys)
            if targets or generic:
                at = piece_start + s + first
                callouts.append({"pos": at, "where": main.where(at), "place": place, "par": par_id,
                                 "text": bare(piece[s:e]), "targets": targets, "generic": generic and not targets})
                if par_id is not None:
                    per_par[par_id] += 1

    for k, (s, e) in enumerate(pars):
        place = section_of(s) or "text"
        if (s, e) in back:
            place = "back matter"
        elif closing == (s, e) and place != "Abstract":
            place = "conclusion"
        scan(s, flow[s:e], place, k if (s, e) in text_pars else None)
    for f in mfloats:
        cap = mtext[f["start"]:f["end"]]
        scan(f["start"], cap, "caption", None)
    callouts.sort(key=lambda c: c["pos"])
    counted = [c for c in callouts if c["place"] != "back matter"]   # captions count; statements at the end do not

    # ----- callouts: number, place, content
    for c in callouts:
        named = ", ".join(f"{NAME.get(k, k)} S{n}" if k != "ed" else f"Extended Data {n}" for k, n in c["targets"]) or "the supplement as a whole"
        c["named"] = named
        if c["place"] == "Abstract":
            add("E", c["where"], f"the abstract sends the reader to the supplement ({named}): an abstract stands alone")
        elif c["place"] == "conclusion" or CLOSING.search(c["place"]):
            add("W", c["where"], f"the conclusion sends the reader to the supplement ({named}): the closing paragraph should not need it")
        if c["generic"] and c["place"] != "back matter":
            rest = GENERIC.sub(" ", plain(c["text"]))
            if re.search(r"\b(?:details?|(?:more|further|additional)\s+(?:information|discussion|data|results))\b", rest, re.I) and \
                    count_words(c["text"]) <= 16:
                add("W", c["where"], f"a callout that says neither what is there nor where: \"{short(c['text'], 80)}\"")
            else:
                placeless.append(c)
        for kind, n in c["targets"]:
            if supp is not None and kind in ("fig", "table", "sec") and (kind, n) not in items:
                have = sum(1 for k in items if k[0] == kind)
                add("E", c["where"], f"{NAME[kind]} S{n} is cited, but the supplement has {have} {PLURAL[kind]}{'' if have == 1 else 's'}")
    worst = max(per_par.values(), default=0)
    counted = [c for c in counted if not (c["targets"] and all(k == "ed" for k, _ in c["targets"]))]
    extended = sum(1 for c in callouts if c["targets"] and all(k == "ed" for k, _ in c["targets"]))
    density = 1000 * len(counted) / main_words if main_words else 0.0
    by_words = math.ceil(opts.per_1000 * main_words / 1000.0)
    budget = max(len(units), by_words, 3)
    if len(counted) > budget:
        shown = len([k for k in items if k[0] in ("fig", "table")])
        if units:
            why = (f"one per supplementary section ({len(units)}) or {opts.per_1000:g} per 1000 words ({by_words}), whichever is larger")
            how = "keep one callout per section, at the statement it supports, and let the supplement cite its own figures and tables"
        elif shown:
            why = f"{opts.per_1000:g} per 1000 words"
            how = (f"the supplement has no sections, so every item needs a callout of its own: group its {shown} figures and tables "
                   "into sections that each support one statement, and point to the sections")
        else:
            why, how = f"{opts.per_1000:g} per 1000 words", "keep the callouts that a statement needs"
        add("W", "main text", f"{len(counted)} sentences send the reader to the supplement ({density:.1f} per 1000 words; the budget is "
                              f"{budget}: {why}): {how}")
    crowded = [(par_id, n) for par_id, n in sorted(per_par.items()) if n > opts.per_paragraph]
    if len(crowded) == 1:
        s, e = pars[crowded[0][0]]
        add("W", main.where(s), f"{crowded[0][1]} callouts to the supplement in one paragraph (the budget is {opts.per_paragraph}): "
                                f"\"{short(bare(flow[s:e]), 60)}\"")
    elif crowded:
        add("W", main.where(pars[crowded[0][0]][0]),
            f"{len(crowded)} paragraphs hold more than {opts.per_paragraph} callout{'' if opts.per_paragraph == 1 else 's'} to the supplement: "
            + compact([f"{main.where(pars[i][0])} ({n})" for i, n in crowded[:8]]) + (", ..." if len(crowded) > 8 else ""))
    repeats = defaultdict(list)
    for c in counted:
        for t in c["targets"]:
            repeats[t].append(c["where"])
    for (kind, n), places in repeats.items():
        if len(places) > 2 and kind != "ed":
            add("N", "main text", f"{NAME[kind]} S{n} is cited {len(places)} times ({compact(places[:4])}): an item the main text "
                                  "needs this often may belong in the main text")
    if supp is None:
        add("N", "supplement", "no supplement was given or found: only the callouts of the main text were checked")

    # ----- reach
    direct = [t for c in callouts for t in c["targets"] if t in items]
    generic_any = any(c["generic"] or c["targets"] for c in callouts)
    cited_by_unit, front_cites, cited_in_supp, listed = defaultdict(set), set(), defaultdict(list), set()
    if supp is not None:
        own = {f["key"]: (f["start"], f["end"]) for f in sfloats}
        spans = [(None, 0, units[0]["span"][0] if units else len(stext))] + [(k, *u["span"]) for k, u in enumerate(units)]
        every = headings(stext)                           # cover pages and contents lists name items without using them
        listing = [(h["pos"], every[k + 1]["pos"] if k + 1 < len(every) else len(stext))
                   for k, h in enumerate(every) if COVER.search(h["title"])]
        sflow_ = blank(stext, list(own.values()))
        front_end = units[0]["span"][0] if units else min([f["start"] for f in sfloats], default=len(stext))
        for ps, pe in paragraphs(sflow_, 0, front_end):  # before the first section: a paragraph that names three figures lists them
            named = Counter(k for k, _ in mentions(sflow_[ps:pe], labels)[0] if k != "sec")
            if max(named.values(), default=0) >= 3:
                listing.append((ps, pe))
        for unit, s, e in spans:
            piece = stext[s:e]
            for kind, pattern in (("ref", REF), ("w", TYPED_W), ("s", TYPED_S)):
                for m in pattern.finditer(piece):
                    for t in mentions(m.group(0), labels)[0]:
                        if t not in items:
                            if t[0] in ("fig", "table", "sec") and kind != "ref":
                                add("E", supp.where(s + m.start()), f"the supplement cites {NAME[t[0]]} S{t[1]}, which it does not contain")
                            continue
                        at = s + m.start()
                        if any(x <= at < y for x, y in listing) or (unit is None and at < front_end and t[0] == "sec"):
                            listed.add(t)
                            continue                      # named in a contents list: not a citation
                        if t in own and own[t][0] <= s + m.start() < own[t][1]:
                            continue                      # a float naming itself
                        if t == ("sec", (unit or 0) + 1) and unit is not None:
                            continue                      # a section naming itself
                        (front_cites if unit is None else cited_by_unit[unit]).add(t)
                        cited_in_supp[t].append(unit)
        entered, reachable = reach(items, units, cited_by_unit, front_cites, set(direct), generic_any)
        only_generic = generic_any and not direct
        if only_generic and (units or len(items) > 1):
            add("W", "main text", "the main text cites the supplement only as a whole: at each callout name the section or the figure, "
                                  "so that the reader lands on the right page")
        if not generic_any and items:
            add("E", "main text", "the main text never mentions the supplement")
        if (units or len(items) > 1) and not only_generic:
            if len(placeless) == 1:
                add("N", placeless[0]["where"], f"names no place in the supplement: \"{short(placeless[0]['text'], 80)}\"; give the section or figure")
            elif placeless:
                add("N", placeless[0]["where"], f"{len(placeless)} callouts name no place in the supplement ("
                                                + compact([c["where"] for c in placeless[:8]]) + ("; ..." if len(placeless) > 8 else "")
                                                + "): give the section or figure")
        for key, it in items.items():
            cited_main = key in direct
            cited_supp = bool(cited_in_supp.get(key))
            it["main"], it["supp"] = cited_main, sorted({u for u in cited_in_supp.get(key, []) if u is not None})
            it["front"], it["listed"] = None in cited_in_supp.get(key, []), key in listed
            it["reachable"] = key in reachable or (key[0] == "sec" and it["unit"] in entered)
            if key[0] == "sec":
                inside = [k for k, v in items.items() if k[0] != "sec" and v["unit"] == it["unit"]]
                it["how"] = ("yes" if cited_main else "via its items" if any(k in direct for k in inside) else
                             "as a whole" if it["reachable"] and only_generic else "via the supplement" if it["reachable"] else "no")
                if not it["reachable"] and not only_generic:
                    add("W", supp.where(it["pos"]), f"{it['name']} (\"{short(it['title'], 50)}\") cannot be reached from the main text: "
                                                    f"no callout points to it{' or to anything in it' if inside else ''}")
                continue
            if not cited_main and not cited_supp:
                add("E", supp.where(it["pos"]), f"{it['name']} is cited nowhere, neither in the main text nor in the supplement: "
                                                "cite it where it is used, move it to the data package, or cut it")

    # ----- order
    if supp is not None and units:
        first = list(OrderedDict.fromkeys(items[t]["unit"] for t in direct if items[t]["unit"] is not None))
        if first != sorted(first):
            add("W", "supplement", "the sections of the supplement are not in the order in which the main text first points to them: "
                                   + ", ".join(f"S{u + 1}" for u in first))
    if supp is not None:
        for kind in ("fig", "table"):
            seq = []
            for m in list(REF.finditer(stext)) + list(TYPED_S.finditer(stext)) + list(TYPED_W.finditer(stext)):
                seq.extend((m.start(), t[1]) for t in mentions(m.group(0), labels)[0] if t[0] == kind and t in items)
            order = list(OrderedDict.fromkeys(n for _, n in sorted(seq)))
            if order != sorted(order):
                add("N", "supplement", f"{NAME[kind].rstrip('.')}s are first cited in the supplement in the order "
                                       + ", ".join(f"S{n}" for n in order[:10]) + ": number them in the order of first citation")

    # ----- size
    size = {"main": {"words": main_words, "display": len([f for f in mfloats if f["kind"] in ("fig", "table")]),
                     "equations": len(re.findall(rf"\\begin\{{(?:{NUMBERED_EQ})\}}", mtext))}}
    if supp is not None:
        sflow = blank(stext, [(f["start"], f["end"]) for f in sfloats])
        sa, sb = body_range(supp) if "\\begin{document}" in supp.text else (0, len(stext))
        spars = [p for p in paragraphs(sflow, sa, sb) if count_words(sflow[p[0]:p[1]]) >= 8]
        size["supp"] = {"words": sum(count_words(sflow[p[0]:p[1]]) for p in spars),
                        "display": len([f for f in sfloats if f["kind"] in ("fig", "table")]),
                        "equations": len(re.findall(rf"\\begin\{{(?:{NUMBERED_EQ})\}}", stext))}
        if opts.pages:
            size["main"]["pages"], size["supp"]["pages"] = opts.pages
        for key, label in (("display", "figures and tables"), ("words", "words")):
            m_, s_ = size["main"].get(key), size["supp"].get(key)
            if m_ and s_ is not None and s_ / m_ > opts.ratio + 1e-9:
                add("W", "size", f"the supplement has {s_} {label} against {m_} in the main text (ratio {s_ / m_:.2f}; the budget is "
                                 f"{opts.ratio:g}): move what is only data to the data package, merge figures that make one point, "
                                 "cut what no sentence uses")
        if size["main"].get("pages") and size["supp"].get("pages", 0) / size["main"]["pages"] > opts.ratio + 1e-9:
            add("N", "size", f"the supplement has {size['supp']['pages']} pages against {size['main']['pages']} of main text; pages "
                             "compare only when both files use the same layout, so judge by words and display items")
        if size["main"]["display"] == 0 and size["supp"]["display"] > 0:
            add("N", "size", f"the main text has no figure or table and the supplement has {size['supp']['display']}")

    # ----- data rather than argument
    if supp is not None:
        for f in sfloats:
            name, where = items[f["key"]]["name"], supp.where(f["start"])
            if f["env"] == "longtable" or f["rows"] > 25:
                add("N", where, f"{name} is a table of about {f['rows']} rows: readers look values up in it; a machine-readable file "
                                "in the data package serves them better, with a short table of the values the text discusses")
            if f["kind"] == "fig" and max(f["graphics"], f["panels"]) >= 9:
                add("N", where, f"{name} holds {max(f['graphics'], f['panels'])} images: a gallery is data; show the cases the text "
                                "discusses and deposit the rest")
            if DATA_PHRASE.search(plain(f["caption"])):
                add("N", where, f"{name} is described as a complete or raw set (\"{DATA_PHRASE.search(plain(f['caption'])).group(0)}\"): "
                                "a candidate for the data package")
        run, previous = [], None
        for f in [f for f in sfloats if f["kind"] == "fig"] + [None]:
            norm = re.sub(r"\d+(?:\.\d+)?", "#", plain(f["caption"]).lower()) if f else None
            if f and previous and len(norm) > 30 and difflib.SequenceMatcher(None, previous, norm).ratio() > 0.85:
                run.append(f)
            else:
                if len(run) >= 3:
                    add("N", supp.where(run[0]["start"]), f"{items[run[0]['key']]['name']} to {items[run[-1]['key']]['name']} have nearly "
                                                          "the same caption: a parameter sweep; keep one or two and deposit the rest as data")
                run = [f] if f else []
            previous = norm
        for m in re.finditer(r"\\begin\{(verbatim|lstlisting|minted)\}(.*?)\\end\{\1\}", stext, re.S):
            lines = m.group(2).count("\n")
            if lines > 15:
                add("N", supp.where(m.start()), f"a listing of {lines} lines: code and input files belong in the data package, "
                                                "with one sentence here that says where")

    # ----- style
    if supp is not None:
        if not shared_preamble:
            mm, sm = macros(main.text), macros(supp.text)
            differ = sorted(k for k in set(mm) & set(sm) if mm[k] != sm[k] and k not in NOT_SHARED)
            if differ:
                add("W", "style", f"{len(differ)} macro(s) are defined differently in main text and supplement: "
                                  + ", ".join(f"{k} ({short(mm[k], 18)} / {short(sm[k], 18)})" for k in differ[:5])
                                  + ": share one preamble file")
            if len(re.findall(r"\\(?:SI|qty|unit|si|num)\s*(?:\[[^\]]*\])?\{", mtext)) >= 3 and \
                    not re.search(r"\\(?:SI|qty|unit|si|num)\s*(?:\[[^\]]*\])?\{", stext) and re.search(r"\d\s*(?:\\,|~)\s*\\?(?:mathrm|text|rm)", stext):
                add("N", "style", "the main text sets units with siunitx and the supplement types them by hand")
        for what, (abbr_form, long_form) in FORMS.items():
            counts = {}
            for name, text in (("main", flow), ("supp", stext)):
                short_n = len(re.findall(r"(?<=[a-z,;:(]\s)" + abbr_form, text)) + len(re.findall(r"(?<=\()" + abbr_form, text))
                long_n = len(re.findall(r"(?<=[a-z,;:(]\s)" + long_form, text)) + len(re.findall(r"(?<=\()" + long_form, text))
                counts[name] = (short_n, long_n)
            (ms, ml), (ss, sl) = counts["main"], counts["supp"]
            if ms + ml >= 1 and ss + sl >= 2 and (ms > ml) != (ss > sl) and ms != ml and ss != sl:
                word = {"figure": ("Fig.", "Figure"), "equation": ("Eq.", "Equation"), "section": ("Sec.", "Section")}[what]
                add("W" if min(ms + ml, ss + sl) >= 3 else "N", "style", f"the main text writes \"{word[0] if ms > ml else word[1]}\" in mid-sentence and the supplement "
                                  f"\"{word[0] if ss > sl else word[1]}\": use the main text's form")
        has_floats = any(k[0] in ("fig", "table") for k in items)
        s_prefix = re.search(r"\\renewcommand\s*\{?\\the(?:figure|table)\}?\s*\{[^}]*S", supp.text) or \
            re.search(r"\\(?:figurename|tablename)\}?\s*\{\s*Supplementary", supp.text)
        if has_floats and not s_prefix:
            add("W", "style", "the supplement's figures and tables are not numbered with a prefix (S1, S2, ...): "
                              "\"Fig. 1\" would then mean two different figures")
        if size["supp"]["equations"] and not re.search(r"\\renewcommand\s*\{?\\theequation\}?\s*\{[^}]*S", supp.text):
            add("N", "style", "the supplement's equations are not numbered with a prefix: Eq. (1) of the supplement and Eq. (1) of "
                              "the main text carry the same number")
        for f in sfloats:
            if not f["caption"].strip():
                add("W", supp.where(f["start"]), f"{items[f['key']]['name']} has no caption")
            elif not f["labels"]:
                add("N", supp.where(f["start"]), f"{items[f['key']]['name']} has no label: it can only be cited by a typed number")
        main_labels = set(re.findall(r"\\label\s*\{([^}]*)\}", main.text)) - set(labels)
        back_prefix = re.search(r"\\externaldocument\s*\[([^\]]*)\]", supp.text)
        back_prefix = back_prefix.group(1) if back_prefix else ""
        silent = []
        for k, u in enumerate(units):
            s, e = u["span"]
            opener = blank(stext[u["end"]:e], [(f["start"] - u["end"], f["end"] - u["end"]) for f in sfloats if s <= f["start"] < e])
            first = [q for q in paragraphs(opener, 0, len(opener)) if count_words(opener[q[0]:q[1]]) >= 5]
            head = opener[first[0][0]:first[0][1]] if first else ""
            by_label = any(key.strip() in main_labels or (back_prefix and key.strip().startswith(back_prefix)
                                                          and key.strip()[len(back_prefix):] in main_labels)
                           for m in REF.finditer(head) for key in m.group(1).split(","))
            if head.strip() and not by_label and not MAIN_POINTER.search(TYPED_S.sub(" ", TYPED_W.sub(" ", head))):
                silent.append(k)
        if len(silent) == 1:
            u = units[silent[0]]
            add("N", supp.where(u["span"][0]), f"Sec. S{silent[0] + 1} (\"{short(u['title'], 44)}\") does not say in its first paragraph which "
                                               "statement, figure or equation of the main text it supports")
        elif silent:
            add("N", supp.where(units[silent[0]]["span"][0]),
                f"{len(silent)} of {len(units)} sections ({', '.join('S%d' % (k + 1) for k in silent)}) do not say in their first paragraph "
                "which statement, figure or equation of the main text they support")
        title_m, title_s = re.search(r"\\title\s*(?:\[[^\]]*\])?\s*\{", main.text), re.search(r"\\title\s*(?:\[[^\]]*\])?\s*\{", supp.text)
        if title_m and not shared_preamble:
            tm = set(re.findall(r"[a-z0-9]{4,}", plain(group(main.text, title_m.end() - 1)[0]).lower()))
            opening = group(supp.text, title_s.end() - 1)[0] if title_s else stext.lstrip()[:900]
            ts = set(re.findall(r"[a-z0-9]{4,}", plain(opening).lower()))
            if tm and len(tm & ts) < 0.6 * len(tm):
                add("N", "style", "the supplement does not carry the paper's title: open it with \"Supplemental Material for: <title>\" "
                                  "and the author list, so that the file can be identified when it is read alone")
        if (size["supp"]["words"] > 3000 or len(units) >= 6) and "\\tableofcontents" not in supp.text and not re.search(r"(?i)\\section\*?\{\s*Contents", supp.text):
            add("N", "style", f"a supplement of {size['supp']['words']} words in {len(units)} sections without a table of contents")
        only = sorted(cite_keys(stext) - cite_keys(mtext) - sm_keys)
        if only:
            add("N", "references", f"{len(only)} work(s) are cited only in the supplement ({', '.join(only[:6])}{', ...' if len(only) > 6 else ''}): "
                                   "citations in a supplement are often not indexed; see venue.md for whether they must also "
                                   "appear in the main reference list")
    das = DAS.search(main.text)
    if not das:
        add("N", "data", "no data availability statement was found in the main text")
    else:
        tail = main.text[das.start():das.start() + 900]
        if re.search(r"(?:up)?on\s+(?:reasonable\s+)?request", tail, re.I) and not REPOSITORY.search(tail):
            add("N", main.where(das.start()), "the data are offered on request only: requests are often not answered and data held by "
                                              "authors are lost with time; a repository with a DOI keeps them")
    return {"findings": found, "callouts": callouts, "counted": len(counted), "extended": extended, "main_words": main_words, "density": density,
            "worst": worst, "items": items, "units": units, "size": size, "sm_keys": sorted(sm_keys)}


# ---------- output ----------

def cited_from(item, key):
    if key[0] == "sec":
        return item.get("how", "no")
    return "yes" if item.get("main") else "no"


def cited_inside(item, none="-"):
    return ", ".join(f"S{u + 1}" for u in item.get("supp", [])) or ("front" if item.get("front") else "contents" if item.get("listed") else none)


def show(result, main, supp):
    size = result["size"]
    print(f"supp_check: {', '.join(main.files())}" + (f" + {', '.join(supp.files())}" if supp is not None else ""))
    if "supp" in size:
        print("\nSIZE                    main   supplement   ratio")
        for key, label in (("words", "words"), ("display", "figures and tables"), ("equations", "numbered equations"), ("pages", "pages")):
            if key in size["main"]:
                m_, s_ = size["main"][key], size["supp"].get(key, 0)
                print(f"  {label:<20}{m_:>6}   {s_:>10}   " + (f"{s_ / m_:.2f}" if m_ else "-"))
    c = result["callouts"]
    print(f"\nCALLOUTS  {result['counted']} sentence(s) in {result['main_words']} words of main text "
          f"({result['density']:.1f} per 1000); most in one paragraph: {result['worst']}"
          + (f"; Extended Data, not counted: {result['extended']}" if result["extended"] else ""))
    for k, call in enumerate(c, 1):
        print(f"  {k:>2}  {call['where']:<22} {short(call['place'], 16):<16}  {short(call['named'], 34):<34}  \"{short(call['text'], 70)}\"")
    if result["items"]:
        kinds = defaultdict(int)
        for key in result["items"]:
            kinds[key[0]] += 1
        print("\nITEMS  " + ", ".join(f"{n} {PLURAL[k]}{'' if n == 1 else 's'}" for k, n in kinds.items()))
        for key, it in result["items"].items():
            print(f"  {it['name']:<10} main: {cited_from(it, key):<18} supplement: {cited_inside(it):<13} "
                  f"{'' if it.get('reachable') else 'NOT REACHED  '}{short(it['title'], 60)}")
    errors = 0
    for level, title in (("E", "ERRORS"), ("W", "WARNINGS"), ("N", "NOTES")):
        rows = [f for f in result["findings"] if f[0] == level]
        if rows:
            print(f"\n{title} ({len(rows)})")
            for _, where, msg in rows:
                print(f"  {where}: {msg}")
        if level == "E":
            errors = len(rows)
    print(f"\n{errors} error(s), {sum(1 for f in result['findings'] if f[0] == 'W')} warning(s), "
          f"{sum(1 for f in result['findings'] if f[0] == 'N')} note(s)")
    return errors


def ledger(result, main, supp, path):
    size, out = result["size"], []
    out.append("# Supplement map\n")
    out.append(f"Written by supp_check.py on {datetime.date.today().isoformat()}. Main text: {', '.join(main.files())}. "
               f"Supplement: {', '.join(supp.files()) if supp is not None else 'none'}.")
    out.append("Fill in the last two columns of Items and act on every row whose decision is not `keep`. "
               "List under Moved out what left the supplement, and under Data package what was deposited.\n")
    out.append("## Budget\n\n| | Main text | Supplement | Ratio |\n|---|---|---|---|")
    for key, label in (("words", "Words"), ("display", "Figures and tables"), ("equations", "Numbered equations"), ("pages", "Pages")):
        if key in size["main"]:
            m_, s_ = size["main"][key], size.get("supp", {}).get(key, 0)
            out.append(f"| {label} | {m_} | {s_} | {s_ / m_:.2f} |" if m_ else f"| {label} | {m_} | {s_} | |")
    out.append(f"\nCallouts: {result['counted']} sentences in {result['main_words']} words ({result['density']:.1f} per 1000); "
               f"most in one paragraph: {result['worst']}.\n")
    out.append("## Items\n\n| Item | Caption or title | Cited in main text | Cited in supplement | Reached | Supports statement | "
               "Decision (keep, merge, main, data, cut) |\n|---|---|---|---|---|---|---|")
    for key, it in result["items"].items():
        out.append(f"| {it['name']} | {short(it['title'], 70).replace('|', '/')} | {cited_from(it, key)} | {cited_inside(it, 'no')} | "
                   f"{'yes' if it.get('reachable') else 'no'} | | |")
    out.append("\n## Callouts\n\n| # | Where | Part | Points to | Sentence |\n|---|---|---|---|---|")
    for k, c in enumerate(result["callouts"], 1):
        out.append(f"| {k} | {c['where']} | {short(c['place'], 24)} | {c['named']} | {short(c['text'], 110).replace('|', '/')} |")
    out.append("\n## Moved out\n\n| Candidate | Went to | Reason |\n|---|---|---|\n")
    out.append("## Data package\n\n| Path in the package | Content | Replaces or backs up |\n|---|---|---|\n")
    out.append("## Open items\n")
    for level, where, msg in result["findings"]:
        if level in ("E", "W"):
            out.append(f"- [{'error' if level == 'E' else 'warning'}] {where}: {msg}")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Check how a manuscript uses its supplement.")
    ap.add_argument("main", nargs="+", help="source file(s) of the main text")
    ap.add_argument("--supp", nargs="+", help="source file(s) of the supplement")
    ap.add_argument("--split", help="regular expression that matches where the supplement starts inside the main file")
    ap.add_argument("--ratio", type=float, default=1.0, help="largest supplement-to-main ratio (default 1.0)")
    ap.add_argument("--per-1000", type=float, default=2.0, dest="per_1000",
                    help="callout sentences per 1000 words, applied to texts of 1000 words or more (default 2)")
    ap.add_argument("--per-paragraph", type=int, default=1, dest="per_paragraph", help="callout sentences per paragraph (default 1)")
    ap.add_argument("--sm-key", nargs="+", dest="sm_key", help="citation key(s) that stand for the supplement")
    ap.add_argument("--pages", nargs=2, type=int, metavar=("MAIN", "SUPP"), help="page counts of main text and supplement")
    ap.add_argument("--ledger", help="write the tables to this file (suppmap.md)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing ledger")
    opts = ap.parse_args()
    missing = [p for p in opts.main + (opts.supp or []) if not os.path.isfile(p)]
    if missing:
        sys.exit("supp_check: no such file: " + ", ".join(missing))
    skipped = []                                         # a main file that inputs its supplement: one preamble, two texts
    main_doc = Doc([line for p in opts.main
                    for line in read_tex(p, skip={os.path.abspath(q) for q in opts.supp or []}, skipped=skipped)])
    shared = bool(skipped)
    if opts.supp:
        supp_doc = Doc([line for p in opts.supp for line in read_tex(p)])
    else:
        start, _ = body_range(main_doc)
        supp_doc, split_at = None, None
        if opts.split:
            m = re.search(opts.split, main_doc.text[start:], re.I)
            if not m:
                sys.exit(f"supp_check: --split {opts.split!r} matches nothing in the body of {opts.main[0]}")
            at = start + m.start()
        else:
            at = find_split(main_doc.text, start)
        if at is not None:
            cut = main_doc.line_index(at)
            tail = Doc(main_doc.lines[cut:])
            # a heading "Supplementary information" with a line or two under it is the main text's own pointer, not a supplement
            real = opts.split or count_words(tail.text) >= 150 or floats(tail.text) or S_PREFIX.search(tail.text)
            if real:
                split_at = main_doc.where(at)
                supp_doc, main_doc, shared = tail, Doc(main_doc.lines[:cut]), True
    if opts.pages is None and opts.supp:
        pages = [pdf_pages(os.path.splitext(opts.main[0])[0] + ".pdf"), pdf_pages(os.path.splitext(opts.supp[0])[0] + ".pdf")]
        if all(pages):
            opts.pages = pages
    result = check(main_doc, supp_doc, shared, opts)
    errors = show(result, main_doc, supp_doc)
    if not opts.supp and supp_doc is not None:
        print(f"(the supplement was taken to start at {split_at}; --split REGEX sets another place)")
    if opts.ledger:
        if os.path.exists(opts.ledger) and not opts.force:
            print(f"\n{opts.ledger} exists and was left alone; use --force to overwrite it")
        else:
            ledger(result, main_doc, supp_doc, opts.ledger)
            print(f"\nwrote {opts.ledger}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
