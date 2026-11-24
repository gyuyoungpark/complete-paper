#!/usr/bin/env python3
r"""
audit_tex.py: mechanical checks for a LaTeX manuscript (complete-paper skill).

Standard library only, Python 3.8 or later. LaTeX sources only; \input and
\include files are followed.

Checks
  refs       citation order against \bibitem order (numbered styles),
             citations without an entry, entries never cited, duplicates
  xrefs      figures, tables and equations first cited in numerical order,
             equations cited before they are displayed, labels never
             cited, references to undefined labels
  abbrev     abbreviations used before or without a definition, defined but
             barely used, acronyms in the title; the abstract, the body and
             the supplement are separate scopes
  numbers    numbers in the abstract that do not appear in the body, and
             numbers in the conclusion that appear nowhere else
  questions  question marks in the title, abstract, captions and body
  todo       TODO markers, [CITE: ...] placeholders and other placeholders
             left in the text, and TODO notes in source comments
  limits     sentences that state a limitation of this work outside the
             Results (title, abstract, captions, other sections); each
             limitation is stated once, in the Results
  voice      passive voice that hides who did the work ("simulations were
             performed") and activity verbs ("we study", "we investigate");
             write what we did with "we" and an active verb
  punct      colons, semicolons and dashes in running text, captions and
             the abstract (the title form "Name: descriptor" is allowed)
  gap        the gap described as an absence ("has not been studied",
             "remains unknown") in the abstract and the introduction
  tone       machine-tone phrases ("crucial", "delve", "Furthermore",
             "not only ... but also") and a roadmap of the paper in the
             introduction ("The rest of this paper is organized as follows")
  prior      earlier work described as a fault ("fails to", "suffers
             from") instead of by how this work differs from it
  length approximate word counts of abstract, body and captions,
             compared with the limits you pass
  figcode    titles, annotations and arrows in plotting code (needs --code)

Severity
  CRITICAL  would cause a desk rejection, a production query or a correction
  SHOULD    a referee or editor would likely comment
  NICE      worth a look
  INFO      counts, no judgment

The checks are heuristics. Read every flagged line before acting on it.
Exit status: 1 if any CRITICAL finding, otherwise 0.

Examples
  python audit_tex.py main.tex
  python audit_tex.py main.tex --supp supplement.tex --code figures/
  python audit_tex.py main.tex --checks refs,xrefs --json
  python audit_tex.py main.tex --checks length --max-words 3750 --max-abstract-words 150
"""

import argparse
import bisect
import json
import os
import re
import sys

ALL_CHECKS = ["refs", "xrefs", "abbrev", "numbers", "questions", "todo", "limits", "voice", "punct", "gap",
              "tone", "prior", "length", "figcode"]
SEV_ORDER = {"CRITICAL": 0, "SHOULD": 1, "NICE": 2, "INFO": 3}


class Finding:
    def __init__(self, check, severity, where, message):
        self.check = check
        self.severity = severity
        self.where = where
        self.message = message

    def as_dict(self):
        return {"check": self.check, "severity": self.severity,
                "where": self.where, "message": self.message}


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


def split_comment(line):
    """Return (code, comment) for one source line; '%' escaped as '\\%' is kept."""
    start = 0
    while True:
        j = line.find("%", start)
        if j < 0:
            return line, ""
        k, slashes = j - 1, 0
        while k >= 0 and line[k] == "\\":
            slashes += 1
            k -= 1
        if slashes % 2 == 0:
            newline = "\n" if line.endswith("\n") else ""
            return line[:j] + newline, line[j + 1:].rstrip("\n")
        start = j + 1


class Doc:
    """A LaTeX document with comments removed and inputs inlined.

    Offsets into self.text map back to file:line through where()."""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.base = os.path.dirname(self.path)
        self.comments = []        # (file, line, comment text)
        self.missing_inputs = []  # (file, line, name)
        self._pieces, self._offsets, self._origins = [], [], []
        self._n = 0
        self._seen = set()
        self._load(self.path)
        self.text = "".join(self._pieces)

    def _emit(self, s, rel, lineno):
        if not s:
            return
        self._offsets.append(self._n)
        self._origins.append((rel, lineno))
        self._pieces.append(s)
        self._n += len(s)

    def _resolve(self, name, cur_dir):
        name = name.strip()
        for d in (cur_dir, self.base):
            p = os.path.join(d, name)
            for cand in (p, p + ".tex"):
                if os.path.isfile(cand):
                    return os.path.abspath(cand)
        return None

    def _load(self, path):
        if path in self._seen:
            return
        self._seen.add(path)
        rel = os.path.relpath(path, self.base)
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        cur_dir = os.path.dirname(path)
        for i, line in enumerate(lines, 1):
            code, comment = split_comment(line)
            if comment.strip():
                self.comments.append((rel, i, comment.strip()))
            pos = 0
            for m in INPUT_RE.finditer(code):
                self._emit(code[pos:m.start()], rel, i)
                sub = self._resolve(m.group(1), cur_dir)
                if sub:
                    self._load(sub)
                else:
                    self.missing_inputs.append((rel, i, m.group(1)))
                pos = m.end()
            self._emit(code[pos:], rel, i)

    def where(self, offset):
        if not self._offsets:
            return os.path.basename(self.path)
        idx = max(0, bisect.bisect_right(self._offsets, offset) - 1)
        rel, line = self._origins[idx]
        return "%s:%d" % (rel.replace("\\", "/"), line)


# --------------------------------------------------------------------------
# Text helpers (all keep string length, so offsets stay valid)
# --------------------------------------------------------------------------

def blank_spans(text, spans):
    if not spans:
        return text
    chars = list(text)
    for a, b in spans:
        for k in range(max(0, a), min(len(chars), b)):
            if chars[k] != "\n":
                chars[k] = " "
    return "".join(chars)


def subtract(spans, holes):
    out = []
    holes = sorted(holes)
    for a, b in spans:
        cur = a
        for h0, h1 in holes:
            if h1 <= cur or h0 >= b:
                continue
            if h0 > cur:
                out.append((cur, h0))
            cur = max(cur, h1)
        if cur < b:
            out.append((cur, b))
    return out


def keep_spans(text, spans):
    return blank_spans(text, subtract([(0, len(text))], spans))


def match_brace(text, i):
    """text[i] is '{'; return the index just past its matching '}'."""
    depth, n, k = 0, len(text), i
    while k < n:
        c = text[k]
        if c == "\\":
            k += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return n


def command_arg_spans(text, names, inner=True):
    """Spans of the first {...} argument of \\name[opt]{...}."""
    rx = re.compile(r"\\(?:%s)\*?\s*(?:\[[^\]]*\]\s*)?\{" % "|".join(names))
    spans = []
    for m in rx.finditer(text):
        open_i = m.end() - 1
        close = match_brace(text, open_i)
        spans.append((open_i + 1, close - 1) if inner else (m.start(), close))
    return spans


def env_spans(text, names, inner=False):
    spans = []
    for name in names:
        rx = re.compile(r"\\begin\s*\{%s\}(.*?)\\end\s*\{%s\}" % (re.escape(name), re.escape(name)), re.S)
        for m in rx.finditer(text):
            spans.append((m.start(1), m.end(1)) if inner else (m.start(), m.end()))
    return sorted(spans)


MATH_ENVS = ["equation", "equation*", "align", "align*", "gather", "gather*",
             "multline", "multline*", "eqnarray", "eqnarray*", "flalign", "flalign*",
             "alignat", "alignat*", "displaymath", "math"]
INLINE_MATH_RES = [re.compile(r"\$\$.*?\$\$", re.S), re.compile(r"\\\[.*?\\\]", re.S),
                   re.compile(r"\\\(.*?\\\)", re.S), re.compile(r"(?<!\\)\$.*?(?<!\\)\$", re.S)]


def math_spans(text):
    spans = env_spans(text, MATH_ENVS)
    t = blank_spans(text, spans)
    inline = []
    for rx in INLINE_MATH_RES:
        found = [(m.start(), m.end()) for m in rx.finditer(t)]
        inline += found
        t = blank_spans(t, found)
    return spans, inline


def blank_math(text):
    display, inline = math_spans(text)
    return blank_spans(text, display + inline)


NONPROSE_CMDS = ["label", "ref", "eqref", "autoref", "cref", "Cref", "pageref", "vref",
                 "[a-zA-Z]*cite[a-zA-Z]*", "nocite", "url", "href", "includegraphics",
                 "input", "include", "bibliography", "bibliographystyle", "usepackage",
                 "documentclass", "begin", "end", "newcommand", "renewcommand",
                 "providecommand", "DeclareMathOperator", "graphicspath", "color",
                 "textcolor", "hypersetup", "setlength", "vspace", "hspace", "SI", "si",
                 "unit", "qty", "num", "ce", "bibitem"]
COMMAND_RE = re.compile(r"\\[A-Za-z@]+\*?|\\.")


def prose(text):
    """Blank math, non-prose command arguments and command names."""
    t = blank_math(text)
    t = blank_spans(t, command_arg_spans(t, NONPROSE_CMDS, inner=False))
    return COMMAND_RE.sub(lambda m: " " * len(m.group()), t)


class Regions:
    FRONT = ["author", "affiliation", "altaffiliation", "thanks", "email", "date",
             "keywords", "pacs", "address", "homepage", "institute", "orcid"]

    def __init__(self, text):
        m = re.search(r"\\begin\s*\{document\}", text)
        self.doc_start = m.end() if m else 0
        m = re.search(r"\\end\s*\{document\}", text)
        self.doc_end = m.start() if m else len(text)
        self.abstract = env_spans(text, ["abstract"], inner=True)[:1]
        self.bib = env_spans(text, ["thebibliography"])
        self.title = command_arg_spans(text, ["title"])[:1]
        self.captions = command_arg_spans(text, ["caption"])
        self.floats = env_spans(text, ["figure", "figure*", "table", "table*", "wrapfigure",
                                       "SCfigure", "sidewaysfigure", "sidewaystable"])
        self.front = command_arg_spans(text, self.FRONT, inner=False)

    def body(self):
        return subtract([(self.doc_start, self.doc_end)],
                        self.abstract + self.bib + self.title + self.front)

    def kind_at(self, o):
        for spans, name in ((self.title, "title"), (self.abstract, "abstract"),
                            (self.captions, "caption"), (self.bib, "bibliography")):
            if any(a <= o < b for a, b in spans):
                return name
        if o < self.doc_start or o >= self.doc_end:
            return "preamble"
        return "body"


# --------------------------------------------------------------------------
# refs
# --------------------------------------------------------------------------

CITE_RE = re.compile(r"\\(?:[a-zA-Z]*cite[a-zA-Z]*|nocite)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}")
BIBITEM_RE = re.compile(r"\\bibitem\s*(\[[^\]]*\])?\s*\{([^}]+)\}")
CITATION_ORDER_STYLES = {"unsrt", "unsrtnat", "apsrev4-1", "apsrev4-2", "apsrmp4-1", "apsrmp4-2",
                         "naturemag", "nature", "ieeetr", "IEEEtran", "achemso", "aipnum4-1",
                         "aipnum4-2", "pnas2011", "pnas2016", "sciencemag", "Science", "rsc",
                         "elsarticle-num", "unsrt_abbrv_custom"}
SORTED_NUMBERED_STYLES = {"plain", "abbrv", "acm", "siam", "plainurl", "abbrvurl"}


def read_bbl(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    items = []
    for i, line in enumerate(lines, 1):
        for m in BIBITEM_RE.finditer(line):
            items.append((m.group(2).strip(), "%s:%d" % (os.path.basename(path), i), m.group(1)))
    return items


def bib_keys_from_files(doc, names):
    keys = set()
    found_any = False
    for name in names:
        name = name.strip()
        if not name:
            continue
        p = os.path.join(doc.base, name if name.endswith(".bib") else name + ".bib")
        if os.path.isfile(p):
            found_any = True
            with open(p, encoding="utf-8", errors="replace") as f:
                for m in re.finditer(r"@\s*(\w+)\s*[{(]\s*([^,\s]+)\s*,", f.read()):
                    if m.group(1).lower() not in ("comment", "string", "preamble"):
                        keys.add(m.group(2).strip())
    return keys if found_any else None


def check_refs(doc, author_year=False):
    out = []
    text = doc.text
    R = Regions(text)
    scan = blank_spans(text, R.bib)
    cited, first = [], {}
    nocite_all = False
    for m in CITE_RE.finditer(scan):
        for key in m.group(1).split(","):
            key = key.strip()
            if not key:
                continue
            if key == "*":
                nocite_all = True
                continue
            if key not in first:
                first[key] = m.start()
                cited.append(key)
    out.append(Finding("refs", "INFO", doc.where(0), "%d distinct citation keys" % len(cited)))

    items = [(m.group(2).strip(), doc.where(m.start()), m.group(1)) for m in BIBITEM_RE.finditer(text)]
    source = "\\bibitem list"
    style = None
    m = re.search(r"\\bibliographystyle\s*\{([^}]+)\}", text)
    if m:
        style = m.group(1).strip()
    if not items:
        bbl = os.path.splitext(doc.path)[0] + ".bbl"
        if os.path.isfile(bbl):
            items = read_bbl(bbl)
            source = os.path.basename(bbl)
    if not items:
        m = re.search(r"\\bibliography\s*\{([^}]+)\}", text)
        if m:
            keys = bib_keys_from_files(doc, m.group(1).split(","))
            if keys is None:
                out.append(Finding("refs", "SHOULD", doc.where(m.start()),
                                   "could not find the .bib file(s) %s; phantom check skipped" % m.group(1)))
            else:
                for k in cited:
                    if k not in keys:
                        out.append(Finding("refs", "CRITICAL", doc.where(first[k]),
                                           "citation '%s' has no entry in the .bib file" % k))
            if style in SORTED_NUMBERED_STYLES:
                out.append(Finding("refs", "SHOULD", doc.where(m.start()),
                                   "bibliography style '%s' sorts references alphabetically; numbered venues "
                                   "usually require first-citation order (e.g. unsrt, apsrev4-2)" % style))
            elif style:
                note = ("numbers references by first citation" if style in CITATION_ORDER_STYLES
                        else "ordering not known to this script; check it")
                out.append(Finding("refs", "INFO", doc.where(m.start()),
                                   "bibliography style '%s': %s. Run BibTeX and re-run this check "
                                   "to verify the order from the .bbl file." % (style, note)))
        elif cited:
            out.append(Finding("refs", "SHOULD", doc.where(0), "citations found but no bibliography"))
        return out

    keys = [k for k, _, _ in items]
    seen, dups = set(), []
    for k, w, _ in items:
        if k in seen:
            dups.append((k, w))
        seen.add(k)
    for k, w in dups:
        out.append(Finding("refs", "CRITICAL", w, "duplicate entry key '%s'" % k))
    for k in cited:
        if k not in seen:
            out.append(Finding("refs", "CRITICAL", doc.where(first[k]),
                               "citation '%s' has no entry in the %s" % (k, source)))
    if not nocite_all:
        for k, w, _ in items:
            if k not in first:
                out.append(Finding("refs", "SHOULD", w, "entry '%s' is never cited" % k))

    labelled = sum(1 for _, _, opt in items if opt and "(" in opt)
    if author_year or (items and labelled > len(items) / 2):
        out.append(Finding("refs", "INFO", doc.where(0),
                           "author-year style detected or requested; numbering-order check skipped"))
        return out

    order_in_list = []
    for k in keys:
        if k in first and k not in order_in_list:
            order_in_list.append(k)
    expected = [k for k in cited if k in seen]
    shown = 0
    mismatches = 0
    for i, (got, want) in enumerate(zip(order_in_list, expected)):
        if got != want:
            mismatches += 1
            if shown < 10:
                out.append(Finding("refs", "CRITICAL", doc.where(first[want]),
                                   "reference [%d] should be '%s' (first cited here) but the %s has '%s' "
                                   "in that position" % (i + 1, want, source, got)))
                shown += 1
    if mismatches > shown:
        out.append(Finding("refs", "CRITICAL", doc.where(0),
                           "%d more positions out of first-citation order" % (mismatches - shown)))
    return out


# --------------------------------------------------------------------------
# xrefs
# --------------------------------------------------------------------------

FLOAT_KIND = {"figure": "figure", "figure*": "figure", "wrapfigure": "figure", "SCfigure": "figure",
              "sidewaysfigure": "figure", "table": "table", "table*": "table",
              "sidewaystable": "table"}
EQ_ENVS = set(MATH_ENVS) | {"subequations", "split", "dmath", "dmath*"}
TOKEN_RE = re.compile(r"\\(begin|end)\s*\{([^}]+)\}|\\label\s*\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|crefrange|Crefrange|vref|Vref|pageref|"
                    r"subref|labelcref|nameref)\*?\s*\{([^}]+)\}")
KIND_NAME = {"figure": "Fig.", "table": "Table", "equation": "labeled Eq."}


def collect_labels(text):
    stack, labels = [], []
    for m in TOKEN_RE.finditer(text):
        if m.group(1) == "begin":
            stack.append(m.group(2).strip())
        elif m.group(1) == "end":
            name = m.group(2).strip()
            for j in range(len(stack) - 1, -1, -1):
                if stack[j] == name:
                    del stack[j:]
                    break
        else:
            key, kind = m.group(3).strip(), None
            for env in reversed(stack):
                if env in ("subfigure", "subtable"):
                    kind = "sub"
                    break
                if env in FLOAT_KIND:
                    kind = FLOAT_KIND[env]
                    break
                if env in EQ_ENVS:
                    kind = "equation"
                    break
            if kind is None:
                low = key.lower()
                if low.startswith(("fig:", "fig.", "fig-")):
                    kind = "figure"
                elif low.startswith(("tab:", "tbl:", "table:")):
                    kind = "table"
                elif low.startswith(("eq:", "eqn:", "eq.")):
                    kind = "equation"
                elif low.startswith(("sec:", "sect:", "app:")):
                    kind = "section"
                else:
                    kind = "other"
            labels.append((key, kind, m.start()))
    return labels


def xr_prefixes(text):
    """Prefixes of the xr package, as in \\externaldocument[S-]{supplement}."""
    return [p for p in re.findall(r"\\externaldocument\s*\[([^\]]*)\]", text) if p]


def opener_spans(text):
    """(start, end, section end) of the first paragraph after each \\section heading."""
    secs = [s for s in sections(text) if s[1] != "appendix"]
    out = []
    for i, (s, _) in enumerate(secs):
        m = SECTION_RE.match(text, s)
        if not m:
            continue
        end_sec = secs[i + 1][0] if i + 1 < len(secs) else len(text)
        k = match_brace(text, m.end() - 1)
        a = k + re.match(r"(?:\s|\\label\s*\{[^}]*\})*", text[k:]).end()
        b = re.search(r"\n[ \t]*\n", text[a:end_sec])
        out.append((a, a + b.start() if b else end_sec, end_sec))
    return out


# "Fig. 2", "Figs. 2 and 3", "Figs. 2a,b and 4", "Figs. 2-4", "Table II": numbers typed without \ref, as in text
# converted from Word; cite_order.py reads them too
TYPED_NUM = r"(?:\d+|[IVXL]+\b)(?:[a-z](?![a-z])(?:\s*(?:,|--?|\u2013)\s*[a-z](?![a-z]))*)?"
TYPED_RE = re.compile(r"(?<![A-Za-z\\])(Figs?\.|Figures?|Tables?|Tabs?\.)(?:\s|~)*(" + TYPED_NUM
                      + r"(?:(?:\s|~)*(?:,\s*and|,|and|&|or|to|--?|\u2013|\u2014)(?:\s|~)*" + TYPED_NUM + r")*)")
NOT_MAIN_RE = re.compile(r"(?:Supplement(?:al|ary)|Supporting|Extended\s+Data|Suppl?\.)\s*$", re.I)
ROMAN_VALUE = {"I": 1, "V": 5, "X": 10, "L": 50}


def typed_number(s):
    if s.isdigit():
        return int(s)
    total, prev = 0, 0
    for c in reversed(s):
        v = ROMAN_VALUE.get(c, 0)
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def typed_mentions(text, R):
    """(offset, kind, number) of every figure and table number typed in the running text, ranges expanded;
    "Extended Data Fig. 1" and "Supplementary Table 2" are left out."""
    t = blank_math(text)
    t = blank_spans(t, R.bib + [(0, R.doc_start), (R.doc_end, len(t))])
    out = []
    for m in TYPED_RE.finditer(t):
        if NOT_MAIN_RE.search(t[max(0, m.start() - 22):m.start()]):
            continue
        kind = "table" if m.group(1).lower().startswith("tab") else "figure"
        nums, prev, span = [], None, False
        # a dash or "to" before a number is a range; before a letter it joins panels ("2a-c")
        for tok in re.finditer(r"(\d+|[IVXL]+)|(?:--?|\u2013|\u2014|\bto\b)(?=(?:\s|~)*(?:\d|[IVXL]))", m.group(2)):
            if tok.group(1) is None:
                span = True
                continue
            s = tok.group(1)
            if kind == "figure" and not s.isdigit():
                continue
            n = typed_number(s)
            if span and prev is not None and 0 < n - prev <= 50:
                nums += list(range(prev + 1, n + 1))
            else:
                nums.append(n)
            prev, span = n, False
        out += [(m.start(), kind, n) for n in nums]
    return out


def float_labels(text, labels):
    """{'figure': [...], 'table': [...]}: the label of each float in its order of appearance (None without one)."""
    order = {"figure": [], "table": []}
    rx = re.compile(r"\\begin\s*\{(%s)\}" % "|".join(re.escape(e) for e in sorted(FLOAT_KIND, key=len, reverse=True)))
    for m in rx.finditer(text):
        kind = FLOAT_KIND[m.group(1)]
        end = text.find("\\end{%s}" % m.group(1), m.end())
        end = end if end >= 0 else len(text)
        order[kind].append(next((k for k, kd, o in labels if kd == kind and m.end() <= o < end), None))
    return order


def check_xrefs(doc, other_labels=frozenset(), other_given=False, typed=True):
    out = []
    text = doc.text
    R = Regions(text)
    labels = collect_labels(text)
    defined = {k for k, _, _ in labels}
    label_off = {k: o for k, _, o in labels}
    prefixes = xr_prefixes(text)
    openers = opener_spans(text)
    first_out, first_eq, any_ref, undefined, external = {}, {}, set(), {}, 0
    for m in REF_RE.finditer(text):
        inside_float = any(a <= m.start() < b for a, b in R.floats)
        for key in m.group(1).split(","):
            key = key.strip()
            if not key:
                continue
            any_ref.add(key)
            if key not in defined and any(key.startswith(p) for p in prefixes) and not other_given:
                external += 1                            # points into the other document, which was not given
                continue
            if key not in defined and key not in other_labels and key not in undefined:
                undefined[key] = m.start()
            if not inside_float and key not in first_out:
                first_out[key] = m.start()
            # a section's opening paragraph may name the result it derives further down (ground rule 12)
            ahead = any(a <= m.start() < b and b <= label_off.get(key, -1) < e for a, b, e in openers)
            if not inside_float and not ahead and key not in first_eq:
                first_eq[key] = m.start()
    counted = 0
    if typed:                                            # "Fig. 2" typed as text counts as a citation of Fig. 2
        order = float_labels(text, labels)
        for o, kind, n in typed_mentions(text, R):
            key = order[kind][n - 1] if 0 < n <= len(order[kind]) else None
            if key is None:
                continue
            counted += 1
            any_ref.add(key)
            if not any(a <= o < b for a, b in R.floats):
                first_out[key] = min(first_out.get(key, o), o)
    if counted:
        out.append(Finding("xrefs", "INFO", doc.where(0), "%d figure or table number(s) typed as text, without \\ref, "
                           "counted as citations" % counted))
    if external:
        out.append(Finding("xrefs", "INFO", doc.where(0), "%d reference(s) into another document through xr; "
                           "pass --supp to check them" % external))
    for key, o in undefined.items():
        out.append(Finding("xrefs", "CRITICAL", doc.where(o), "reference to undefined label '%s'" % key))

    for kind in ("figure", "table", "equation"):
        items = [(n + 1, key, off) for n, (key, off) in
                 enumerate([(k, o) for k, kd, o in labels if kd == kind])]
        name = KIND_NAME[kind]
        for n, key, off in items:
            if key in first_out:
                continue
            if kind == "equation":
                if key not in any_ref:
                    out.append(Finding("xrefs", "NICE", doc.where(off),
                                       "%s %d ('%s') is labeled but never referenced; consider leaving it "
                                       "unnumbered" % (name, n, key)))
            elif key in any_ref:
                out.append(Finding("xrefs", "SHOULD", doc.where(off),
                                   "%s %d ('%s') is cited only inside a float or caption, not in the running "
                                   "text" % (name, n, key)))
            else:
                out.append(Finding("xrefs", "CRITICAL", doc.where(off),
                                   "%s %d ('%s') is never cited" % (name, n, key)))
        if kind == "equation":
            # a displayed equation is met where it stands: numbers follow position, so its display counts as
            # its first appearance; a number cited before its display is a forward reference (below)
            first = {key: min(first_eq.get(key, off), off) for _, key, off in items}
        else:
            first = first_out
        cited_items = [(n, key, first[key]) for n, key, _ in items if key in first]
        for n_i, key_i, f_i in cited_items:
            earlier_later = [(n_j, key_j, f_j) for n_j, key_j, f_j in cited_items if n_j < n_i and f_j > f_i]
            if earlier_later:
                n_j, key_j, f_j = min(earlier_later)
                out.append(Finding("xrefs", "CRITICAL", doc.where(f_i),
                                   "%s %d ('%s') is first cited here, before %s %d ('%s', first cited at %s); "
                                   "reorder the argument, or move the item so that numbers follow first citation"
                                   % (name, n_i, key_i, name, n_j, key_j, doc.where(f_j))))
        if kind == "equation":
            m = re.search(r"\\appendix\b", text)
            appendix = m.start() if m else len(text)
            for n, key, off in items:
                if key in first_eq and first_eq[key] < off < appendix:
                    out.append(Finding("xrefs", "SHOULD", doc.where(first_eq[key]),
                                       "%s %d ('%s') is cited before it is displayed; a reference may point "
                                       "forward only to an appendix or the supplement" % (name, n, key)))
        if items:
            out.append(Finding("xrefs", "INFO", doc.where(0), "%d %s label(s)" % (len(items), kind)))
    return out


# --------------------------------------------------------------------------
# abbrev
# --------------------------------------------------------------------------

ABBR_RE = re.compile(r"(?<![A-Za-z0-9_\\])([A-Z]{2,7})(s?)(?![A-Za-z0-9])")
KNOWN = {"II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII", "XIII", "XIV", "XV",
         "XX", "XXX", "DOI", "URL", "PDF", "USA", "UK", "EU", "OK", "TODO", "TBD", "FIXME", "CITE",
         "FIG", "FIGS", "SM", "ID", "MW", "GW", "TW", "KW", "MV", "GV", "KV", "MA", "KA",
         "MJ", "GJ", "TJ", "AM", "PM"}


def is_subsequence_from_word_start(abbr, phrase):
    abbr = abbr.lower()
    phrase = phrase.lower()
    for m in re.finditer(r"(?<![a-z])[a-z]", phrase):
        if phrase[m.start()] != abbr[0]:
            continue
        it = iter(phrase[m.start():])
        if all(ch in it for ch in abbr):
            return True
    return False


def scope_abbrevs(t, doc, scope, known, out):
    occ = {}
    for m in ABBR_RE.finditer(t):
        occ.setdefault(m.group(1), []).append(m.start(1))
    for abbr, offs in sorted(occ.items(), key=lambda kv: kv[1][0]):
        if abbr in known:
            continue
        defs = []
        for o in offs:
            end = o + len(abbr)
            before = t[max(0, o - 2):o]
            after = t[end:end + 4]
            if re.search(r"\(\s*$", before) and re.match(r"s?\s*[),;]", after):
                defs.append(o)
                continue
            m = re.match(r"s?\s*\(([^()]{3,80})\)", t[end:end + 90])
            if m and is_subsequence_from_word_start(abbr, m.group(1)):
                defs.append(o)
        first = offs[0]
        if not defs:
            out.append(Finding("abbrev", "SHOULD", doc.where(first),
                               "%s: '%s' is used %d time(s) but never defined" % (scope, abbr, len(offs))))
            continue
        d0 = defs[0]
        if first < d0:
            out.append(Finding("abbrev", "SHOULD", doc.where(first),
                               "%s: '%s' is used here before its definition at %s"
                               % (scope, abbr, doc.where(d0))))
        uses = len(offs) - len(defs)
        if uses <= 1:
            out.append(Finding("abbrev", "NICE", doc.where(d0),
                               "%s: '%s' is defined but used only %d more time(s); consider spelling it out"
                               % (scope, abbr, uses)))
        if len(defs) > 1:
            out.append(Finding("abbrev", "NICE", doc.where(defs[1]),
                               "%s: '%s' is defined %d times" % (scope, abbr, len(defs))))


def check_abbrev(doc, known, scope_prefix=""):
    out = []
    R = Regions(doc.text)
    p = prose(doc.text)
    if R.abstract:
        scope_abbrevs(keep_spans(p, R.abstract), doc, scope_prefix + "abstract", known, out)
    scope_abbrevs(keep_spans(p, R.body()), doc, scope_prefix + "body", known, out)
    if R.title:
        t = keep_spans(p, R.title)
        for m in ABBR_RE.finditer(t):
            if m.group(1) not in known:
                out.append(Finding("abbrev", "SHOULD", doc.where(m.start()),
                                   "acronym '%s' in the title; spell it out unless readers search by it"
                                   % m.group(1)))
    return out


# --------------------------------------------------------------------------
# numbers
# --------------------------------------------------------------------------

NUM_RE = re.compile(r"(?<![A-Za-z0-9_.\\])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\d.]*[A-Za-z])")
# where a statement starts after the conclusion: a run-in heading or environment for data, code, funding,
# acknowledgments, interests, contributions, ethics or AI use
STATEMENT_START_RE = re.compile(
    r"\\(?:paragraph|subsubsection|subsection|section)\*?\s*\{[^{}]*(?:availab|acknowledg|funding|competing|"
    r"conflicts?\s+of|contribution|ethic|\bAI\b|artificial\s+intelligence)[^{}]*\}"
    r"|\\begin\{acknowledg\w*\}|\\acknowledg\w*\b", re.I)
# identifiers whose digits are not quantities: DOIs, arXiv numbers, URLs
IDENTIFIER_RE = re.compile(r"(?:doi:\s*)?10\.\d{4,9}/\S+|arXiv:\s*\d{4}\.\d{4,5}(?:v\d+)?|https?://\S+", re.I)


def check_numbers(doc):
    out = []
    R = Regions(doc.text)
    if not R.abstract:
        out.append(Finding("numbers", "INFO", doc.where(0), "no abstract environment found"))
        return out + conclusion_numbers(doc, R)
    a = keep_spans(doc.text, R.abstract)
    a = blank_spans(a, [(m.start(), m.end()) for m in
                        re.finditer(r"[_^](\{[^{}]*\}|\\?[A-Za-z0-9])", a)])
    a = blank_spans(a, command_arg_spans(a, ["label", "ref", "eqref", "[a-zA-Z]*cite[a-zA-Z]*", "url"],
                                         inner=False))
    a = COMMAND_RE.sub(lambda m: " " * len(m.group()), a)
    nums = []
    for m in NUM_RE.finditer(a):
        nums.append((m.group(1), m.start(1)))
    body = keep_spans(doc.text, R.body())
    body_norm = body.replace("{,}", ",")
    distinct = []
    for s, o in nums:
        if s in distinct:
            continue
        distinct.append(s)
        pattern = r"(?<![\d.])%s(?![\d])" % re.escape(s)
        alt = s.replace(",", "")
        if not (re.search(pattern, body_norm) or re.search(r"(?<![\d.,])%s(?![\d])" % re.escape(alt), body_norm)):
            out.append(Finding("numbers", "SHOULD", doc.where(o),
                               "number '%s' in the abstract does not appear in the body; check that the "
                               "body states the same value" % s))
    if len(distinct) > 2:
        out.append(Finding("numbers", "NICE", doc.where(R.abstract[0][0]),
                           "the abstract contains %d distinct numbers (%s); keep the one or two headline "
                           "numbers, each with its meaning" % (len(distinct), ", ".join(distinct))))
    out += conclusion_numbers(doc, R)
    return out


def conclusion_numbers(doc, R):
    """Numbers in a Conclusion section that appear nowhere else in the body (ground rule 16)."""
    out = []
    text = doc.text
    secs = sections(text)
    for i, (start, heading) in enumerate(secs):
        if not re.search(r"conclu|summary|outlook", heading, re.I):
            continue
        end = secs[i + 1][0] if i + 1 < len(secs) else R.doc_end
        # the conclusion stops where a statement begins (data availability, acknowledgments, funding, ...)
        stop = STATEMENT_START_RE.search(text, start + 1, end)
        if stop:
            end = stop.start()
        span = (start, end)
        part = keep_spans(text, subtract([span], R.floats + R.bib))
        part = blank_spans(part, command_arg_spans(part, ["section", "subsection", "label", "ref", "eqref",
                                                          "[a-zA-Z]*cite[a-zA-Z]*", "url", "href"], inner=False))
        part = blank_spans(part, [(m.start(), m.end()) for m in IDENTIFIER_RE.finditer(part)])
        part = blank_spans(part, [(m.start(), m.end()) for m in re.finditer(r"[_^](\{[^{}]*\}|\\?[A-Za-z0-9])", part)])
        part = COMMAND_RE.sub(lambda m: " " * len(m.group()), part)
        rest = keep_spans(text, subtract(R.body(), [span])).replace("{,}", ",")
        seen = set()
        for m in NUM_RE.finditer(part):
            s = m.group(1)
            if s in seen:
                continue
            seen.add(s)
            alt = s.replace(",", "")
            if not (re.search(r"(?<![\d.])%s(?![\d])" % re.escape(s), rest)
                    or re.search(r"(?<![\d.,])%s(?![\d])" % re.escape(alt), rest)):
                out.append(Finding("numbers", "SHOULD", doc.where(m.start(1)),
                                   "number '%s' in the conclusion appears nowhere else in the paper; check it "
                                   "against the Results and the data" % s))
    return out


# --------------------------------------------------------------------------
# questions
# --------------------------------------------------------------------------

def check_questions(doc):
    out = []
    R = Regions(doc.text)
    t = blank_math(doc.text)
    t = blank_spans(t, env_spans(t, ["verbatim", "lstlisting", "quote", "quotation", "comment", "minted"]))
    t = blank_spans(t, command_arg_spans(t, ["url", "href", "enquote", "textquote", "label", "ref",
                                             "[a-zA-Z]*cite[a-zA-Z]*"], inner=False))
    for m in re.finditer(r"\?", t):
        o = m.start()
        if t[o - 1:o] == "?" or t[o + 1:o + 2] == "?":
            continue  # '??' placeholders are reported by the todo check
        kind = R.kind_at(o)
        if kind in ("bibliography", "preamble"):
            continue
        sev = "CRITICAL" if kind in ("title", "abstract", "caption") else "SHOULD"
        out.append(Finding("questions", sev, doc.where(o),
                           "question mark in the %s; rewrite as a statement or an indirect question" % kind))
    return out


# --------------------------------------------------------------------------
# todo
# --------------------------------------------------------------------------

TODO_RE = re.compile(r"TODO|TBD|FIXME|XXX|\[CITE\b|\?\?|\bX\.XX\b|\\textcolor\s*\{\s*red\s*\}")


def check_todo(doc):
    out = []
    R = Regions(doc.text)
    spans = [(R.doc_start, R.doc_end)] + R.title
    t = keep_spans(doc.text, spans)
    hits = []
    red_until = -1
    for m in TODO_RE.finditer(t):
        if m.start() < red_until:
            continue  # a TODO inside red text is one marker, not two
        if m.group().startswith("\\textcolor"):
            brace = t.find("{", m.end())
            if brace >= 0 and not t[m.end():brace].strip():
                red_until = match_brace(t, brace)
        hits.append(m)
    for m in hits[:60]:
        if m.group().startswith("\\textcolor"):
            what = "red text (often a TODO marker)"
        elif m.group() == "[CITE":
            what = "citation placeholder '[CITE: ...]'"
        else:
            what = "'%s'" % m.group()
        out.append(Finding("todo", "CRITICAL", doc.where(m.start()),
                           "%s left in the text; must be resolved before submission" % what))
    if len(hits) > 60:
        out.append(Finding("todo", "CRITICAL", doc.where(0), "%d more markers not listed" % (len(hits) - 60)))
    out.append(Finding("todo", "INFO", doc.where(0), "%d TODO marker(s) in the text" % len(hits)))
    notes = [(f, l, c) for f, l, c in doc.comments if re.search(r"TODO|FIXME|XXX", c)]
    if notes:
        f, l, _ = notes[0]
        out.append(Finding("todo", "NICE", "%s:%d" % (f, l),
                           "%d source comment(s) contain TODO/FIXME notes; remove comments before "
                           "uploading LaTeX source" % len(notes)))
    for f, l, name in doc.missing_inputs:
        out.append(Finding("todo", "NICE", "%s:%d" % (f, l), "could not find input file '%s'" % name))
    return out


# --------------------------------------------------------------------------
# limits
# --------------------------------------------------------------------------

LIMIT_RE = re.compile(
    r"\b(?:limitations?|drawbacks?|shortcomings?|weakness(?:es)?|caveats?"
    r"|limited\s+to"
    r"|(?:beyond|outside)\s+the\s+scope"
    r"|(?:further|more|future)\s+(?:work|studies|research|investigations?)\s+(?:is|are|will\s+be|would\s+be)\s+"
    r"(?:needed|required|necessary)"
    r"|not\s+(?:included|considered|taken\s+into\s+account)"
    r"|(?:additionally|also|still)\s+requires?\s+(?:a\s+|an\s+)?(?:low|small|high|large|long|fine|sufficient)"
    r"|(?:apply|applies|hold|holds|(?:is|are)\s+valid)\s+only\s+(?:to|for|in|when)"
    r"|(?:comparisons|results)\s+are\s+(?:only\s+)?between\s+models)\b", re.I)
SELF_RE = re.compile(
    r"\b(?:we|our|us|this\s+(?:work|study|paper|letter|article|model|approach|method|analysis)"
    r"|the\s+present\s+(?:work|study|model|approach|analysis)"
    r"|these\s+(?:results|simulations|calculations|measurements|findings))\b", re.I)
PRIOR_RE = re.compile(r"\b(?:previous(?:ly)?|prior|earlier|existing|conventional|state-of-the-art|reported)\b", re.I)
SECTION_RE = re.compile(r"\\section\*?\s*(?:\[[^\]]*\]\s*)?\{")
HOME_RE = re.compile(r"result", re.I)
# sections that are not Results whatever they are called; any other section heading counts as Results,
# because physics papers often name the Results after their content ("Comparison with ...")
NOT_HOME_RE = re.compile(r"intro|discuss|conclu|summary|outlook|perspective|background|acknowledg|declaration"
                         r"|availability|supplementary\s+material", re.I)


def results_like(heading):
    return bool(HOME_RE.search(heading)) or not (NOT_HOME_RE.search(heading) or DESCRIBE_RE.search(heading))
DESCRIBE_RE = re.compile(r"method|model|simulation|computation|numerical|experiment|appendix|supplement", re.I)
SENT_END_RE = re.compile(r"(?<!\bFig)(?<!\bFigs)(?<!\bEq)(?<!\bEqs)(?<!\bRef)(?<!\bRefs)(?<!\bSec)"
                         r"(?<!\be\.g)(?<!\bi\.e)(?<!\bal)(?<!\bvs)(?<!\bcf)[.!?](?=\s|$)")


def sections(text):
    """(start offset, heading) for each \\section, plus the appendix."""
    out = []
    for m in SECTION_RE.finditer(text):
        close = match_brace(text, m.end() - 1)
        out.append((m.start(), " ".join(text[m.end():close - 1].split())))
    m = re.search(r"\\appendix\b", text)
    if m:
        out.append((m.start(), "appendix"))
    return sorted(out)


def sentence_at(t, o):
    starts = [m.end() for m in SENT_END_RE.finditer(t, 0, o)]
    a = starts[-1] if starts else 0
    m = SENT_END_RE.search(t, o)
    b = m.end() if m else len(t)
    return a, b


def about_earlier_work(text, p, a, b):
    """True if the sentence p[a:b] is about earlier work and not about this paper."""
    sent = p[a:b]
    prior = PRIOR_RE.search(sent) or re.search(r"\\[a-zA-Z]*cite", text[a:b]) or re.search(r"\bet\s+al\b", sent)
    return bool(prior) and not SELF_RE.search(sent)


def check_limits(doc):
    out = []
    text = doc.text
    R = Regions(text)
    p = prose(text)
    secs = sections(text)
    home = 0
    flagged = set()
    for m in LIMIT_RE.finditer(p):
        o = m.start()
        kind = R.kind_at(o)
        if kind in ("bibliography", "preamble"):
            continue
        a, b = sentence_at(p, o)
        if (a, b) in flagged:
            continue
        if about_earlier_work(text, p, a, b):
            continue  # a limitation of earlier work: part of the gap, not of this paper
        flagged.add((a, b))
        cue = " ".join(m.group().split()).lower()
        heading = None
        if kind == "body" and secs:
            before = [h for s, h in secs if s <= o]
            heading = before[-1] if before else "text before the first section"
        if kind == "body" and heading and results_like(heading):
            home += 1
            continue
        if kind == "body" and not secs:
            out.append(Finding("limits", "NICE", doc.where(o),
                               "limitation cue '%s'; no section headings, so check that this sentence is in "
                               "the Results and that the limitation is stated nowhere else" % cue))
        elif kind == "body" and heading and DESCRIBE_RE.search(heading):
            out.append(Finding("limits", "NICE", doc.where(o),
                               "limitation cue '%s' in the section '%s'; describe what the model or experiment "
                               "includes as plain description, not as a shortcoming" % (cue, heading)))
        else:
            where = "section '%s'" % heading if kind == "body" else kind
            out.append(Finding("limits", "SHOULD", doc.where(o),
                               "limitation cue '%s' in the %s; state each limitation once, in the Results, "
                               "and nowhere else" % (cue, where)))
    if secs:
        out.append(Finding("limits", "INFO", doc.where(0),
                           "%d sentence(s) with a limitation cue in the Results; each limitation should "
                           "appear there once" % home))
    return out


# --------------------------------------------------------------------------
# voice
# --------------------------------------------------------------------------

PASSIVE_RE = re.compile(
    r"\b(?:is|are|was|were|has\s+been|have\s+been)\s+(?:\w+ly\s+)?"
    r"(?:performed|carried\s+out|conducted|implemented|developed|proposed|derived|calculated|computed|"
    r"simulated|measured|obtained|investigated|studied|examined|explored|employed|used|introduced|"
    r"demonstrated|found|fabricated|prepared|analy[sz]ed|evaluated|estimated|extracted|fitted|"
    r"chosen|adopted|applied)\b", re.I)
ACTIVITY_RE = re.compile(r"\bwe\s+(?:have\s+)?(?:stud(?:y|ied)|investigat(?:e|ed)|explor(?:e|ed)|examin(?:e|ed))\b",
                         re.I)


def check_voice(doc):
    out = []
    text = doc.text
    R = Regions(text)
    p = prose(text)
    n_passive = 0
    for rx, what in ((ACTIVITY_RE, "activity"), (PASSIVE_RE, "passive")):
        for m in rx.finditer(p):
            o = m.start()
            kind = R.kind_at(o)
            if kind in ("bibliography", "preamble", "caption"):
                continue  # captions describe what is shown and need no "we"
            a, b = sentence_at(p, o)
            if about_earlier_work(text, p, a, b):
                continue  # earlier work keeps its own authors as the actor
            phrase = " ".join(m.group().split())
            sev = "SHOULD" if kind in ("title", "abstract") else "NICE"
            if what == "activity":
                msg = ("'%s' names an activity and withholds the outcome; say what we did or found "
                       "(implement, derive, simulate, measure, show)" % phrase)
            else:
                n_passive += 1
                if sev == "NICE" and n_passive > 40:
                    continue
                msg = "passive '%s' hides who did the work; write it as 'we' with an active verb" % phrase
            out.append(Finding("voice", sev, doc.where(o), "%s: %s" % (kind, msg)))
    if n_passive > 40:
        out.append(Finding("voice", "NICE", doc.where(0), "%d more passive constructions not listed"
                           % (n_passive - 40)))
    return out


# --------------------------------------------------------------------------
# punct
# --------------------------------------------------------------------------

PUNCT_RE = re.compile(r"(?<![\d\s])\s*[:;](?!\d)|---|\u2014")
MARKER_RE = re.compile(r"\[(?:TODO|CITE)\b[^\]]*\]")


def check_punct(doc):
    out = []
    text = doc.text
    R = Regions(text)
    p = prose(text)
    p = blank_spans(p, [(m.start(), m.end()) for m in MARKER_RE.finditer(p)])
    counts = {}
    shown = 0
    for m in PUNCT_RE.finditer(p):
        o = m.end() - 1
        kind = R.kind_at(o)
        if kind in ("bibliography", "preamble", "title"):
            continue  # the title form "Name: descriptor" is allowed
        if R.doc_start <= o < R.doc_end and kind == "body":
            if re.search(r"\\(?:sub)*section\*?\s*(?:\[[^\]]*\])?\{[^{}]*$", text[max(0, o - 200):o]):
                continue  # inside a heading
        mark = m.group().strip()
        what = {":": "colon", ";": "semicolon"}.get(mark, "dash")
        counts[what] = counts.get(what, 0) + 1
        if shown < 40:
            shown += 1
            sev = "SHOULD" if kind == "abstract" else "NICE"
            out.append(Finding("punct", sev, doc.where(o),
                               "%s in the %s; split the sentence or join with 'and', 'because', 'so' or 'which'"
                               % (what, kind)))
    if counts:
        out.append(Finding("punct", "INFO", doc.where(0), "colons, semicolons and dashes in running text: "
                           + ", ".join("%d %s(s)" % (n, k) for k, n in sorted(counts.items()))))
    return out


# --------------------------------------------------------------------------
# gap
# --------------------------------------------------------------------------

ABSENCE_RE = re.compile(
    r"\b(?:ha(?:s|ve)\s+(?:not|never)\s+(?:yet\s+)?been|ha(?:s|ve)\s+yet\s+to\s+be"
    r"|no\s+(?:previous\s+|prior\s+)?(?:study|studies|work|works|report|reports|method|methods)\s+ha(?:s|ve)"
    r"|there\s+(?:is|are|has\s+been|have\s+been)\s+no"
    r"|remains?\s+(?:unexplored|unknown|unclear|elusive|unresolved|open|an\s+open\s+question|a\s+challenge)"
    r"|(?:is|are)\s+(?:still\s+)?missing|little\s+is\s+known|poorly\s+understood"
    r"|do(?:es)?\s+not\s+(?:yet\s+)?(?:evaluate|address|quantify|consider|examine|assess|treat|account\s+for)"
    r"|until\s+(?:it|this|they)\s+(?:is|are)\s+(?:evaluated|known|quantified|resolved)"
    r"|of\s+unknown\s+(?:size|magnitude|accuracy))\b", re.I)


def check_gap(doc):
    out = []
    text = doc.text
    R = Regions(text)
    p = prose(text)
    secs = sections(text)
    first_sec = secs[0][0] if secs else None
    for m in ABSENCE_RE.finditer(p):
        o = m.start()
        kind = R.kind_at(o)
        if kind == "abstract":
            where_, sev = "abstract", "SHOULD"
        elif kind == "body" and first_sec is not None:
            before = [h for s, h in secs if s <= o]
            if before and not re.search(r"intro", before[-1], re.I):
                continue
            where_, sev = "introduction", "NICE"
        else:
            continue  # without section headings the introduction cannot be told apart
        out.append(Finding("gap", sev, doc.where(o),
                           "'%s' in the %s describes an absence; state the gap as a need that has arisen and "
                           "that this work meets ('... calls for ...')" % (" ".join(m.group().split()), where_)))
    return out


# --------------------------------------------------------------------------
# tone
# --------------------------------------------------------------------------

AI_TONE_RE = re.compile(
    r"\b(?:delve[sd]?|delving|crucial(?:ly)?|pivotal|notably|intricate|intricacies|leverag(?:e|es|ed|ing)"
    r"|showcas(?:e|es|ed|ing)|underscor(?:e|es|ed|ing)|seamless(?:ly)?|comprehensive|holistic|multifaceted"
    r"|realm|tapestry|(?:a|is\s+a)\s+testament|groundbreaking|game[- ]chang\w*|cutting[- ]edge|unprecedented"
    r"|remarkabl[ey]|noteworthy|it\s+is\s+worth\s+noting|it\s+should\s+be\s+noted"
    r"|plays?\s+(?:a|an)\s+(?:crucial|key|pivotal|vital|important|central)\s+role|paves?\s+the\s+way"
    r"|sheds?\s+(?:new\s+)?light|opens?\s+(?:up\s+)?new\s+avenues|furthermore|moreover|additionally"
    r"|not\s+only\b[^.]{0,120}\bbut\s+also)\b", re.I)
ROADMAP_RE = re.compile(
    r"\b(?:the\s+(?:rest|remainder)\s+of\s+(?:this|the)\s+(?:paper|article|letter|manuscript|work)"
    r"|(?:is|are)\s+(?:organized|organised|structured)\s+as\s+follows"
    r"|(?:this|the)\s+(?:paper|article|manuscript)\s+is\s+(?:organized|organised|structured)"
    r"|in\s+sec(?:tion|s?\.)\s+[^.]{0,30}?\bwe\s+(?:describe|present|discuss|introduce|derive|summarize|conclude)"
    # "Sections II-IV give ...", "Sec. V states ...": the references are blanked in the prose text
    r"|\bsec(?:tions?|s?\.)(?:[\s~,\-–]|and\b|to\b)*(?:gives?|presents?|describes?|discuss(?:es)?|introduces?"
    r"|derives?|summari[sz]es?|states?|concludes?|contains?|reports?)\b)", re.I)


def in_introduction(o, secs):
    if not secs:
        return False
    before = [h for s, h in secs if s <= o]
    return not before or bool(re.search(r"intro", before[-1], re.I))


def check_tone(doc):
    out = []
    text = doc.text
    R = Regions(text)
    p = prose(text)
    secs = sections(text)
    n = 0
    for m in AI_TONE_RE.finditer(p):
        kind = R.kind_at(m.start())
        if kind in ("bibliography", "preamble"):
            continue
        n += 1
        if n <= 40:
            sev = "SHOULD" if kind in ("title", "abstract") else "NICE"
            out.append(Finding("tone", sev, doc.where(m.start()),
                               "%s: '%s' reads as machine prose; say it plainly or cut it"
                               % (kind, " ".join(m.group().split()[:6]))))
    if n:
        out.append(Finding("tone", "INFO", doc.where(0), "%d machine-tone phrase(s)" % n))
    seen = set()
    for m in ROADMAP_RE.finditer(p):
        kind = R.kind_at(m.start())
        span = sentence_at(p, m.start())
        if span in seen:
            continue
        seen.add(span)
        if kind == "abstract" or (kind == "body" and in_introduction(m.start(), secs)):
            out.append(Finding("tone", "SHOULD", doc.where(m.start()),
                               "roadmap of the paper ('%s'); end the introduction with this work and its finding"
                               % " ".join(m.group().split())))
    return out


# --------------------------------------------------------------------------
# prior
# --------------------------------------------------------------------------

FAULT_RE = re.compile(
    r"\b(?:fail(?:s|ed)?\s+to|failure\s+of|suffer(?:s|ed)?\s+from|incorrect(?:ly)?|erroneous(?:ly)?|flawed"
    r"|wrong(?:ly)?|inaccura(?:te|tely|cy)|poor(?:ly)?|misleading|overlook(?:s|ed)?|inadequate(?:ly)?"
    r"|unable\s+to|cannot\s+(?:explain|account\s+for|capture|describe|reproduce)"
    r"|(?:does|do|did)\s+not\s+(?:explain|account\s+for|capture|describe|reproduce)"
    r"|limitations?|drawbacks?|shortcomings?|weakness(?:es)?|only\s+(?:considered|studied|treated))\b", re.I)


def check_prior(doc):
    out = []
    text = doc.text
    R = Regions(text)
    p = prose(text)
    done = set()
    for m in FAULT_RE.finditer(p):
        kind = R.kind_at(m.start())
        if kind in ("bibliography", "preamble"):
            continue
        a, b = sentence_at(p, m.start())
        if (a, b) in done or not about_earlier_work(text, p, a, b):
            continue
        done.add((a, b))
        out.append(Finding("prior", "SHOULD", doc.where(m.start()),
                           "%s: earlier work described as a fault ('%s'); say how this work differs from it "
                           "('Unlike Ref. [n], ...')" % (kind, " ".join(m.group().split()))))
    return out


# --------------------------------------------------------------------------
# length
# --------------------------------------------------------------------------

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\u2019\-.]*")


def count_words(text, spans):
    t = keep_spans(text, spans)
    display, inline = math_spans(t)
    chars = list(blank_spans(t, display + inline))
    for a, b in inline:
        chars[a] = "M"  # inline math counts as one word
    t = "".join(chars)
    t = blank_spans(t, command_arg_spans(t, NONPROSE_CMDS, inner=False))
    t = COMMAND_RE.sub(lambda m: " " * len(m.group()), t)
    return len(WORD_RE.findall(t))


def check_length(doc, max_words=None, max_abstract=None, captions_count=False):
    out = []
    R = Regions(doc.text)
    abstract_w = count_words(doc.text, R.abstract) if R.abstract else 0
    body_spans = subtract(R.body(), R.floats)
    body_w = count_words(doc.text, body_spans)
    caption_w = sum(count_words(doc.text, [c]) for c in R.captions)
    title_w = count_words(doc.text, R.title) if R.title else 0
    n_fig = sum(1 for k, kd, _ in collect_labels(doc.text) if kd == "figure")
    n_tab = sum(1 for k, kd, _ in collect_labels(doc.text) if kd == "table")
    out.append(Finding("length", "INFO", doc.where(0),
                       "approximate words: title %d, abstract %d, body %d (excluding floats and display "
                       "math), captions %d; labeled figures %d, tables %d"
                       % (title_w, abstract_w, body_w, caption_w, n_fig, n_tab)))
    if max_abstract and abstract_w > max_abstract:
        out.append(Finding("length", "CRITICAL", doc.where(R.abstract[0][0]),
                           "abstract is about %d words; limit %d" % (abstract_w, max_abstract)))
    if max_words:
        total = body_w + (caption_w if captions_count else 0)
        if total > max_words:
            out.append(Finding("length", "CRITICAL", doc.where(R.doc_start),
                               "main text is about %d words%s; limit %d. Venues count differently "
                               "(equations, figures, references); confirm with venue.md"
                               % (total, " including captions" if captions_count else "", max_words)))
    return out


# --------------------------------------------------------------------------
# figcode
# --------------------------------------------------------------------------

FIG_RULES = {
    ".py": [(r"\.set_title\s*\(|\bsuptitle\s*\(|\bplt\.title\s*\(", "SHOULD", "figure title"),
            (r"\bannotate\s*\(|\b(?:ax|axs|axes|plt)\w*(?:\[[^\]]*\])?\.arrow\s*\(|FancyArrow|\bArrow\s*\(",
             "SHOULD", "annotation or arrow"),
            (r"\b(?:ax|axs|axes|fig|plt|subfig)\w*(?:\[[^\]]*\])?\.text\s*\(", "NICE",
             "text in figure; allowed only for panel letters")],
    ".m": [(r"^\s*(?:title|sgtitle|suptitle)\s*\(", "SHOULD", "figure title"),
           (r"\bannotation\s*\(", "SHOULD", "annotation or arrow"),
           (r"^\s*text\s*\(", "NICE", "text in figure; allowed only for panel letters")],
    ".r": [(r"\bggtitle\s*\(|title\s*=", "SHOULD", "figure title"),
           (r"\bannotate\s*\(|\barrow\s*\(", "SHOULD", "annotation or arrow")],
    ".gp": [(r"^\s*set\s+title", "SHOULD", "figure title"),
            (r"^\s*set\s+(?:label|arrow)", "SHOULD", "label or arrow")],
    ".jl": [(r"\btitle\s*=|\bLabel\s*\(", "SHOULD", "figure title"),
            (r"\btext!\s*\(|\barrows!?\s*\(|\bannotation", "SHOULD", "annotation or arrow")],
}
FIG_RULES[".ipynb"] = FIG_RULES[".py"]
FIG_RULES[".plt"] = FIG_RULES[".gp"]


HELPERS = {"fig_style.py", "schematic3d.py", "fig_lint.py"}   # the figures part's own modules, copied beside the scripts


def iter_code_files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p.replace("\\", "/")
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules")]
                for f in files:
                    if f not in HELPERS:
                        yield os.path.join(root, f).replace("\\", "/")


def check_figcode(paths):
    out = []
    n_files = 0
    for path in iter_code_files(paths):
        ext = os.path.splitext(path)[1].lower()
        rules = FIG_RULES.get(ext)
        if not rules:
            continue
        n_files += 1
        try:
            if ext == ".ipynb":
                with open(path, encoding="utf-8") as f:
                    nb = json.load(f)
                lines = []
                for ci, cell in enumerate(nb.get("cells", [])):
                    if cell.get("cell_type") != "code":
                        continue
                    src = cell.get("source", [])
                    src = src if isinstance(src, list) else src.splitlines(True)
                    for li, s in enumerate(src, 1):
                        lines.append(("%s [cell %d, line %d]" % (path, ci + 1, li), s))
            else:
                with open(path, encoding="utf-8", errors="replace") as f:
                    lines = [("%s:%d" % (path, i), s) for i, s in enumerate(f, 1)]
        except (OSError, ValueError) as e:
            out.append(Finding("figcode", "NICE", path, "could not read: %s" % e))
            continue
        for where, line in lines:
            code = line.split("#", 1)[0] if ext in (".py", ".ipynb", ".r", ".gp", ".plt", ".jl") else line.split("%", 1)[0]
            for rx, sev, what in rules:
                if re.search(rx, code, re.I if ext == ".r" else 0):
                    out.append(Finding("figcode", sev, where, "%s: %s" % (what, line.strip()[:100])))
                    break
    out.append(Finding("figcode", "INFO", ", ".join(paths), "%d plotting file(s) scanned" % n_files))
    return out


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def run(args):
    checks = ALL_CHECKS if args.checks == "all" else [c.strip() for c in args.checks.split(",") if c.strip()]
    unknown = [c for c in checks if c not in ALL_CHECKS]
    if unknown:
        sys.exit("unknown check(s): %s; choose from %s" % (", ".join(unknown), ", ".join(ALL_CHECKS)))
    known = set(KNOWN) | {k.strip() for k in (args.known or "").split(",") if k.strip()}

    main = Doc(args.main)
    supp = Doc(args.supp) if args.supp else None
    main_labels = frozenset(k for k, _, _ in collect_labels(main.text))
    supp_labels = frozenset(k for k, _, _ in collect_labels(supp.text)) if supp else frozenset()
    if supp:                                             # labels reached through xr prefixes, e.g. S-eq:result
        supp_labels = supp_labels | {p + k for p in xr_prefixes(main.text) for k in supp_labels}
        main_labels = main_labels | {p + k for p in xr_prefixes(supp.text) for k in main_labels}

    results = []  # (document name, findings)
    for doc, is_supp in ((main, False), (supp, True)):
        if doc is None:
            continue
        f = []
        if "refs" in checks:
            f += check_refs(doc, args.author_year)
        if "xrefs" in checks:
            # in a supplement, a typed "Fig. 2" usually means the main text's figure, so it is not read there
            f += check_xrefs(doc, supp_labels if not is_supp else main_labels, other_given=supp is not None, typed=not is_supp)
        if "abbrev" in checks:
            f += check_abbrev(doc, known, "supplement " if is_supp else "")
        if "numbers" in checks and not is_supp:
            f += check_numbers(doc)
        if "questions" in checks:
            f += check_questions(doc)
        if "todo" in checks:
            f += check_todo(doc)
        if "limits" in checks:
            f += check_limits(doc)
        if "voice" in checks:
            f += check_voice(doc)
        if "punct" in checks:
            f += check_punct(doc)
        if "gap" in checks and not is_supp:
            f += check_gap(doc)
        if "tone" in checks:
            f += check_tone(doc)
        if "prior" in checks:
            f += check_prior(doc)
        if "length" in checks and not is_supp:
            f += check_length(doc, args.max_words, args.max_abstract_words, args.captions_count)
        results.append((os.path.basename(doc.path), f))
    if "figcode" in checks and args.code:
        results.append(("plotting code", check_figcode(args.code)))
    elif "figcode" in checks and args.checks != "all":
        results.append(("plotting code", [Finding("figcode", "INFO", "-", "pass --code DIR to scan plotting code")]))
    return results


def main_cli():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("main", help="main .tex file (the one with \\documentclass)")
    ap.add_argument("--supp", help="supplement .tex file, checked as its own scope")
    ap.add_argument("--checks", default="all", help="comma-separated subset of: " + ", ".join(ALL_CHECKS))
    ap.add_argument("--code", nargs="*", help="plotting code files or directories for the figcode check")
    ap.add_argument("--known", help="comma-separated abbreviations that need no definition")
    ap.add_argument("--author-year", action="store_true", help="skip the numbering-order check")
    ap.add_argument("--max-words", type=int, help="main-text word limit")
    ap.add_argument("--max-abstract-words", type=int, help="abstract word limit")
    ap.add_argument("--captions-count", action="store_true", help="count captions toward --max-words")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    if not os.path.isfile(args.main):
        sys.exit("file not found: %s" % args.main)

    results = run(args)
    counts = {s: 0 for s in SEV_ORDER}
    for _, fs in results:
        for f in fs:
            counts[f.severity] += 1

    if args.json:
        print(json.dumps({"documents": [{"name": n, "findings": [f.as_dict() for f in fs]} for n, fs in results],
                          "summary": counts}, ensure_ascii=False, indent=2))
    else:
        for name, fs in results:
            print("== %s ==" % name)
            for check in ALL_CHECKS:
                group = [f for f in fs if f.check == check]
                if not group:
                    continue
                print("[%s]" % check)
                for f in sorted(group, key=lambda f: SEV_ORDER[f.severity]):
                    print("  %-8s %-22s %s" % (f.severity, f.where, f.message))
            print()
        print("Summary: %d critical, %d should fix, %d nice to have" %
              (counts["CRITICAL"], counts["SHOULD"], counts["NICE"]))
    sys.exit(1 if counts["CRITICAL"] else 0)


if __name__ == "__main__":
    main_cli()
