#!/usr/bin/env python3
"""Make a LaTeX reading copy of a Word manuscript (.docx), so that the other scripts can check it.

Usage:
    python3 docx_to_tex.py manuscript.docx                     writes manuscript_copy.tex beside it
    python3 docx_to_tex.py manuscript.docx -o paper-state/manuscript_copy.tex
    python3 docx_to_tex.py manuscript.docx --add-results       see "headings" below

What becomes what:
  front       the title (Title style, or the first paragraph) becomes \\title, the next line \\author, the other
              lines before the abstract \\affiliation; the abstract is the text under an "Abstract" heading, or
              else the first paragraph of 40 words or more before the first heading
  headings    Word's Heading styles; a paragraph that is only a known section name; a short bold line without
              a final period. Known names (Introduction, Results, Discussion, Methods, ...) become \\section,
              back matter (Data availability, Acknowledgements, Competing interests, ...) \\section*, and the
              other headings \\subsection. Leading numbers ("2.1") are dropped. When the Word text has no
              Results heading, the subsections after the Introduction count as part of it; --add-results puts
              a \\section{Results} before the first of them
  citations   superscript numbers (1 / 1,2 / 3-5) become \\cite{r1,...}, with ranges expanded and adjacent
              superscript runs joined. A superscript after "10", or a 2 or 3 after a unit of length, is an
              exponent; numbers outside the reference list stay superscripts and are reported
  references  the numbered list under "References" (EndNote style: number, tab, entry; or Word's own list
              numbering) becomes thebibliography with \\bibitem{rN}
  equations   a table or paragraph that holds a formula and its number "(n)" becomes an equation with
              \\label{eq:n}; "Eq. (n)" and "Eqs. (n) and (m)" in the text become \\ref{eq:n} when equation n
              exists. Other formulas become $...$ or \\[...\\]. An equation object that is not Word's own
              (MathType, an image) keeps its number and an empty body
  legends     "Fig. N | title" and "Figure N: title" become figure floats with \\caption and \\label{fig:N},
              "Table N | title" a table float with the Word table that follows it, in the order of N, placed
              where the first legend stands. A legend line that holds only a title takes the paragraph after
              it as its text. "Extended Data" and "Supplementary" legends go into an extdata environment that
              the scripts do not count as main items. A line that is only "Figure 2" (where an image stands)
              is left out
  text        %, &, #, _, $, ^, ~, braces and backslashes escaped; tracked deletions, field codes, comments,
              images and text boxes left out
Mentions such as "Fig. 2" and "Extended Data Fig. 1" stay as typed: cite_order.py and audit_tex.py read typed
mentions, and keep "Extended Data Fig. N" and "Supplementary Fig. N" apart from the main "Fig. N".

The copy is for the scripts only. It is not a typeset version of the paper and is not meant to compile.
Check every finding against the Word text before reporting it, and make every fix in the Word file.
Not read: citations by author and year or by numbers in brackets, footnotes, comments, text boxes.
The script will not overwrite a .tex file that it did not write (use --force).
Standard library only. Exit status is 1 if the file cannot be read.
"""
import argparse
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
MARK = "% Reading copy of "

SECTION = re.compile(r"introduction|background|results?(?:\s+and\s+discussions?)?|discussions?|conclusions?(?:\s+and\s+outlook)?|"
                     r"summary\s+and\s+outlook|outlook|methods?|materials\s+and\s+methods|methods\s+and\s+materials|online\s+methods|"
                     r"experimental(?:\s+(?:section|methods|details|procedures?))?|theory|model|related\s+work|main", re.I)
BACK = re.compile(r"(?:data|code|data\s+and\s+code|software)\s+availability(?:\s+statement)?|availability\s+of\s+(?:data|code|materials).*|"
                  r"acknowledge?ments?|author\s+contributions?|contributions|competing\s+(?:financial\s+)?interests?|"
                  r"conflicts?\s+of\s+interests?|declaration\s+of\s+(?:competing\s+)?interests?|declarations?|additional\s+information|"
                  r"supplementary\s+(?:information|materials?)|supporting\s+information|funding|ethics(?:\s+\w+){0,3}|"
                  r"correspondence(?:\s+and\s+requests.*)?|use\s+of\s+(?:generative\s+)?(?:AI|artificial\s+intelligence).*|"
                  r"AI\s+(?:use|statement|disclosure).*|peer\s+review\s+information|reporting\s+summary|inclusion\s+and\s+ethics", re.I)
ABSTRACT = re.compile(r"abstract|summary", re.I)
REFS = re.compile(r"(?:(?:methods|online|additional)\s+)?references?(?:\s+and\s+notes|\s+for\s+(?:the\s+)?methods)?|bibliography|"
                  r"reference\s+list|literature\s+cited|works\s+cited", re.I)
LEGEND_HEAD = re.compile(r"figure\s+(?:legends?|captions?)|figures?(?:\s+and\s+tables?)?|legends?(?:\s+(?:for|to)\s+figures?)?|captions?|"
                         r"extended\s+data(?:\s+(?:figures?|figure\s+legends?|legends?|tables?))?|tables?(?:\s+and\s+figures?)?", re.I)
LEGEND = re.compile(r"(?P<pre>(?:Extended\s+Data|Supplementary)\s+)?(?P<kind>Fig(?:ure)?s?\.?|Table)\s*(?P<n>S?\d+)\s*"
                    r"(?P<sep>[|:.\u2013\u2014]|-(?!\d))\s*(?P<rest>.*)", re.I | re.S)
LABEL_LINE = re.compile(r"(?:(?:Extended\s+Data|Supplementary)\s+(?:(?:Fig(?:ure)?s?\.?|Table)\s*)?|(?:Fig(?:ure)?s?\.?|Table)\s*)S?\d+[a-z]?", re.I)
NUMBERING = re.compile(r"^\s*(?:\d+(?:\.\d+)*\.?|(?:[IVX]+|[A-Z])[.)])\s+(?=\S)")
CITE_LIKE = re.compile(r"\s*\d{1,4}(?:\s*[-\u2013\u2014]\s*\d{1,4})?(?:\s*,\s*\d{1,4}(?:\s*[-\u2013\u2014]\s*\d{1,4})?)*\s*,?\s*")
EQ_MENTION = re.compile(r"(?<![A-Za-z])(Eqs?\.|Equations?)(\s*)((?:\(\s*\d+[a-z]?\s*\)|\d+[a-z]?)"
                        r"(?:\s*(?:,\s*and|,|and|or|to|\u2013|\u2014|--?)\s*(?:\(\s*\d+[a-z]?\s*\)|\d+[a-z]?))*)")
TEX_ESC = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_",
           "^": r"\^{}", "~": r"\textasciitilde{}", "\u00a0": " ", "\u2009": " ", "\u202f": " ", "\u2002": " ", "\u2003": " "}
MATH_ESC = {"\\": r"\backslash ", "{": r"\{", "}": r"\}", "$": r"\$", "%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_",
            "^": r"\hat{}", "~": r"\sim ", "\u00a0": " ", "\u2009": " "}
SYMBOL = dict(zip([0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6B, 0x6C, 0x6D, 0x6E, 0x70, 0x71, 0x72, 0x73, 0x74,
                   0x75, 0x77, 0x78, 0x79, 0x7A, 0x44, 0x46, 0x47, 0x4C, 0x50, 0x51, 0x53, 0x57, 0x59, 0xB0, 0xB1, 0xB4, 0xB8,
                   0xBB, 0xA3, 0xB3, 0xB9, 0xAE, 0xA5, 0xB6, 0x2D, 0xD7],
                  "\u03b1\u03b2\u03c7\u03b4\u03b5\u03c6\u03b3\u03b7\u03b9\u03ba\u03bb\u03bc\u03bd\u03c0\u03b8\u03c1\u03c3\u03c4"
                  "\u03c5\u03c9\u03be\u03c8\u03b6\u0394\u03a6\u0393\u039b\u03a0\u0398\u03a3\u03a9\u03a8\u00b0\u00b1\u00d7\u00f7"
                  "\u2248\u2264\u2265\u2260\u2192\u221e\u2202\u2212\u22c5"))


def esc(s):
    return re.sub(r"[\\{}$%&#_^~\u00a0\u2009\u202f\u2002\u2003]", lambda m: TEX_ESC[m.group(0)], s)


def esc_math(s):
    return re.sub(r"[\\{}$%&#_^~\u00a0\u2009]", lambda m: MATH_ESC[m.group(0)], s)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def on(rpr, name):
    """Whether a toggle property such as <w:b/> is set in a property element; None if it is not given."""
    el = rpr.find(W + name) if rpr is not None else None
    if el is None:
        return None
    return el.get(W + "val", "true").lower() not in ("0", "false", "off", "none")


# --------------------------------------------------------------------------
# styles
# --------------------------------------------------------------------------

def read_styles(z):
    styles = {}
    try:
        root = ET.fromstring(z.read("word/styles.xml"))
    except (KeyError, ET.ParseError):
        return styles
    for s in root.iter(W + "style"):
        name = s.find(W + "name")
        based = s.find(W + "basedOn")
        ppr, rpr, tpr = s.find(W + "pPr"), s.find(W + "rPr"), s.find(W + "tblPr")
        lvl = ppr.find(W + "outlineLvl") if ppr is not None else None
        va = rpr.find(W + "vertAlign") if rpr is not None else None
        first = next((c for c in s.findall(W + "tblStylePr") if c.get(W + "type") == "firstRow"), None)
        styles[s.get(W + "styleId")] = {
            "name": (name.get(W + "val") if name is not None else s.get(W + "styleId") or "").lower(),
            "based": based.get(W + "val") if based is not None else None,
            "outline": int(lvl.get(W + "val")) if lvl is not None and (lvl.get(W + "val") or "").isdigit() else None,
            "bold": on(rpr, "b"),
            "sup": None if va is None else va.get(W + "val") == "superscript",
            "borders": tpr.find(W + "tblBorders") if tpr is not None else None,
            "head": first.find(W + "tcPr/" + W + "tcBorders") if first is not None else None,
        }
    return styles


def style_get(styles, sid, key):
    """A style property, looked up through basedOn."""
    for _ in range(12):
        s = styles.get(sid)
        if s is None:
            return None
        if s.get(key) is not None:
            return s[key]
        sid = s["based"]
    return None


# --------------------------------------------------------------------------
# paragraphs, runs and formulas
# --------------------------------------------------------------------------

def omml(node):
    """The LaTeX of an OMML formula: scripts, fractions, roots, delimiters and n-ary operators; text as is."""
    tag = node.tag
    local = tag.rsplit("}", 1)[-1]
    if local.endswith("Pr"):
        return ""

    def part(name):
        c = node.find(M + name)
        return omml(c) if c is not None else ""

    if tag == M + "r":
        return "".join(esc_math(t.text or "") for t in node.iter(M + "t"))
    if tag == M + "sSub":
        return "{%s}_{%s}" % (part("e"), part("sub"))
    if tag == M + "sSup":
        return "{%s}^{%s}" % (part("e"), part("sup"))
    if tag == M + "sSubSup":
        return "{%s}_{%s}^{%s}" % (part("e"), part("sub"), part("sup"))
    if tag == M + "f":
        return "\\frac{%s}{%s}" % (part("num"), part("den"))
    if tag == M + "rad":
        deg = part("deg")
        return ("\\sqrt[%s]{%s}" % (deg, part("e"))) if deg.strip() else "\\sqrt{%s}" % part("e")
    if tag == M + "d":
        pr = node.find(M + "dPr")

        def chr_of(name, default):
            el = pr.find(M + name) if pr is not None else None
            return el.get(M + "val", "") if el is not None else default
        beg, end = chr_of("begChr", "("), chr_of("endChr", ")")
        inner = ",".join(omml(e) for e in node.findall(M + "e"))
        return esc_math(beg) + inner + esc_math(end)
    if tag == M + "nary":
        pr = node.find(M + "naryPr")
        el = pr.find(M + "chr") if pr is not None else None
        op = el.get(M + "val", "\u222b") if el is not None else "\u222b"
        sub, sup = part("sub"), part("sup")
        return op + ("_{%s}" % sub if sub.strip() else "") + ("^{%s}" % sup if sup.strip() else "") + " " + part("e")
    return "".join(omml(c) for c in node)


class Reader:
    def __init__(self, styles):
        self.styles = styles
        self.unknown_symbols = 0

    def run_props(self, rpr, pstyle):
        rstyle = rpr.find(W + "rStyle").get(W + "val") if rpr is not None and rpr.find(W + "rStyle") is not None else None
        va = rpr.find(W + "vertAlign") if rpr is not None else None
        sup = (va.get(W + "val") == "superscript") if va is not None else bool(style_get(self.styles, rstyle, "sup"))
        bold = on(rpr, "b")
        if bold is None:
            bold = style_get(self.styles, rstyle, "bold")
        if bold is None:
            bold = style_get(self.styles, pstyle, "bold")
        return sup, bool(bold)

    def walk(self, node, segs, pstyle):
        tag = node.tag
        local = tag.rsplit("}", 1)[-1]
        if tag in (W + "del", W + "moveFrom", W + "pPr", W + "rPr", W + "instrText", W + "delText", W + "sectPr") or local == "Fallback":
            return
        if tag == M + "oMathPara":
            for om in node.iter(M + "oMath"):
                segs.append(("math", omml(om), True))
            return
        if tag == M + "oMath":
            segs.append(("math", omml(node), False))
            return
        if local == "AlternateContent":
            kids = list(node)
            if kids:
                self.walk(kids[0], segs, pstyle)
            return
        if tag == W + "r":
            rpr = node.find(W + "rPr")
            if on(rpr, "vanish") or on(rpr, "webHidden"):
                return                                    # hidden text
            sup, bold = self.run_props(rpr, pstyle)
            for c in node:
                ct = c.tag
                if ct == W + "t":
                    segs.append(("sup" if sup else "text", c.text or "", bold))
                elif ct in (W + "tab", W + "ptab"):
                    segs.append(("tab", "\t", None))
                elif ct in (W + "br", W + "cr"):
                    segs.append(("text", " ", None))
                elif ct == W + "noBreakHyphen":
                    segs.append(("text", "-", bold))
                elif ct == W + "sym":
                    code = int(c.get(W + "char", "0"), 16) & 0xFF if re.fullmatch(r"[0-9A-Fa-f]{1,4}", c.get(W + "char", "")) else 0
                    ch = SYMBOL.get(code) if "symbol" in (c.get(W + "font") or "").lower() else None
                    if ch:
                        segs.append(("text", ch, bold))
                    else:
                        self.unknown_symbols += 1
                elif ct in (W + "drawing", W + "pict", W + "object"):
                    segs.append(("object", "ole" if ct == W + "object" else "image", None))
            return
        for c in node:
            self.walk(c, segs, pstyle)

    def para(self, p):
        ppr = p.find(W + "pPr")
        ps = ppr.find(W + "pStyle") if ppr is not None else None
        pstyle = ps.get(W + "val") if ps is not None else None
        lvl = ppr.find(W + "outlineLvl") if ppr is not None else None
        outline = int(lvl.get(W + "val")) if lvl is not None and (lvl.get(W + "val") or "").isdigit() else style_get(self.styles, pstyle, "outline")
        segs = []
        self.walk(p, segs, pstyle)
        tex, plain, prose = [], [], []
        for kind, val, extra in segs:
            if kind == "text":
                tex.append(esc(val))
                plain.append(val)
                prose.append(val)
            elif kind == "sup":
                if val.strip():
                    tex.append("\x00" + val + "\x01")
                    plain.append(val)
                else:
                    tex.append(" ")
            elif kind == "tab":
                tex.append("\t")
                plain.append("\t")
                prose.append("\t")
            elif kind == "math":
                tex.append("$" + val + "$")
                plain.append(" ")
        texts = [(v, b) for k, v, b in segs if k in ("text", "sup") and v.strip()]
        sname = (self.styles.get(pstyle) or {}).get("name", "")
        return {"kind": "p", "tex": "".join(tex).replace("\x01\x00", ""), "plain": "".join(plain), "prose": "".join(prose),
                "style": sname, "outline": outline if outline is not None and outline < 9 else None,
                "bold": bool(texts) and all(b for _, b in texts), "numbered": ppr is not None and ppr.find(W + "numPr") is not None,
                "math": [v for k, v, _ in segs if k == "math"], "display": any(k == "math" and d for k, _, d in segs),
                "objects": sum(1 for k, _, _ in segs if k == "object"), "ole": sum(1 for k, v, _ in segs if k == "object" and v == "ole")}

    def table(self, tbl):
        rows = []
        for tr in tbl.findall(W + "tr"):
            cells = []
            for tc in tr.findall(W + "tc"):
                tcpr = tc.find(W + "tcPr")
                span = tcpr.find(W + "gridSpan") if tcpr is not None else None
                vm = tcpr.find(W + "vMerge") if tcpr is not None else None
                cells.append({"paras": [self.para(p) for p in tc.iter(W + "p")],
                              "span": int(span.get(W + "val", "1")) if span is not None and (span.get(W + "val") or "").isdigit() else 1,
                              "cont": vm is not None and vm.get(W + "val", "continue") == "continue",
                              "borders": tcpr.find(W + "tcBorders") if tcpr is not None else None})
            rows.append(cells)
        tpr = tbl.find(W + "tblPr")
        ts = tpr.find(W + "tblStyle") if tpr is not None else None
        sid = ts.get(W + "val") if ts is not None else None
        return {"kind": "tbl", "rows": rows, "direct": tpr.find(W + "tblBorders") if tpr is not None else None,
                "style_borders": style_get(self.styles, sid, "borders"), "style_head": style_get(self.styles, sid, "head")}


def visible(el, side):
    b = el.find(W + side) if el is not None else None
    if b is None:
        return None
    return (b.get(W + "val") or "nil") not in ("nil", "none")


def tabular(t):
    """The Word table as a tabular, with the rules that its borders draw."""
    rows = t["rows"]

    def border(side):
        for src in (t["direct"], t["style_borders"]):
            v = visible(src, side)
            if v is not None:
                return v
        return False

    def cell_side(row, side):
        return any(visible(c["borders"], side) for c in row)

    ncols = max((sum(c["span"] for c in r) for r in rows), default=1)
    spec = ("|" if border("insideV") else "").join("l" * ncols) if ncols else "l"
    lines = ["\\begin{tabular}{%s}" % spec]
    if rows and (border("top") or cell_side(rows[0], "top")):
        lines.append("\\toprule")
    for i, r in enumerate(rows):
        cells = []
        for c in r:
            text = "" if c["cont"] else norm(" ".join(p["tex"] for p in c["paras"]).replace("\t", " "))
            cells.append(("\\multicolumn{%d}{l}{%s}" % (c["span"], text)) if c["span"] > 1 else text)
        lines.append(" & ".join(cells) + " \\\\")
        last = i == len(rows) - 1
        if last:
            if border("bottom") or cell_side(r, "bottom"):
                lines.append("\\bottomrule")
        elif (border("insideH") or cell_side(r, "bottom") or cell_side(rows[i + 1], "top")
              or (i == 0 and visible(t["style_head"], "bottom"))):
            lines.append("\\midrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------

EQ_NUMBER = re.compile(r"\(\s*(S?\d+[a-z]?)\s*\)")


def classify(b):
    """(role, info) of one block: heading, legend, label, eq, display, tbl or text."""
    if b["kind"] == "tbl":
        flat = [p for r in b["rows"] for c in r for p in c["paras"]]
        texts = [norm(p["prose"]) for p in flat if norm(p["prose"])]
        if (any(p["math"] or p["objects"] for p in flat) and texts and EQ_NUMBER.fullmatch(texts[-1])
                and all(EQ_NUMBER.fullmatch(t) for t in texts)):
            math = " ".join(m for p in flat for m in p["math"])
            return "eq", {"n": EQ_NUMBER.fullmatch(texts[-1]).group(1), "math": math, "object": not math.strip()}
        return "tbl", {}
    prose = norm(b["prose"])
    if b["math"] or b["objects"]:
        if EQ_NUMBER.fullmatch(prose):
            math = " ".join(b["math"])
            return "eq", {"n": EQ_NUMBER.fullmatch(prose).group(1), "math": math, "object": not math.strip()}
        if not prose and b["math"]:
            return "display", {"math": " ".join(b["math"])}
    t = norm(b["plain"])
    if not t:
        return "empty", {}
    if LABEL_LINE.fullmatch(t):
        return "label", {}
    m = LEGEND.match(b["tex"].strip())
    if m:
        return "legend", m.groupdict()
    h = heading(b, t)
    if h:
        return "heading", h
    return "text", {}


def heading(b, t):
    name = NUMBERING.sub("", t).strip().rstrip(":.").strip()
    if not name:
        return None
    if b["style"] == "title":
        return {"level": 0, "name": name, "strong": True}
    m = re.fullmatch(r"heading\s*(\d)", b["style"])
    level = int(m.group(1)) if m else (b["outline"] + 1 if b["outline"] is not None else None)
    if level:
        return {"level": level, "name": name, "strong": True}
    if len(t) > 150 or len(t.split()) > 15:
        return None
    if any(rx.fullmatch(name) for rx in (SECTION, BACK, ABSTRACT, REFS, LEGEND_HEAD)):
        return {"level": 1, "name": name, "strong": True}
    if b["bold"] and not re.search(r"[.,;:]$", t) and "\x00" not in b["tex"]:
        return {"level": 2, "name": name, "strong": False}
    return None


# --------------------------------------------------------------------------
# conversion
# --------------------------------------------------------------------------

def cite_numbers(raw):
    out = []
    for part in raw.replace("\u2013", "-").replace("\u2014", "-").split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if hi < lo or hi - lo > 100:
                return None
            out += list(range(lo, hi + 1))
        elif part.isdigit():
            out.append(int(part))
        elif part:
            return None
    seen = set()
    return [n for n in out if not (n in seen or seen.add(n))] or None


def exponent(before, raw):
    if re.search(r"(?:^|[^\d.])10$", before):
        return True                                       # 10^5, 3 x 10^8
    return raw.strip() in ("2", "3") and bool(re.search(r"\d\s?(?:m|cm|mm|nm|km|pm|\u00b5m|\u03bcm|\u00c5)$", before))


class Converter:
    def __init__(self):
        self.bib_numbers = set()
        self.eq_numbers = set()
        self.cites = 0
        self.outside = []                                 # superscript numbers outside the reference list
        self.eq_missing = []

    def finish(self, s, cite=True):
        """Resolve the superscript marks and the typed equation numbers of one piece of text."""
        def sup(m):
            raw = m.group(1)
            nums = cite_numbers(raw) if cite and CITE_LIKE.fullmatch(raw) and not exponent(s[:m.start()], raw) else None
            if nums and (not self.bib_numbers or all(n in self.bib_numbers for n in nums)):
                self.cites += 1
                return "\\cite{%s}" % ",".join("r%d" % n for n in nums)
            if nums:
                self.outside.append(raw.strip())
            return "\\textsuperscript{%s}" % esc(raw.strip())
        s = re.sub(r"\x00(.*?)\x01", sup, s, flags=re.S)
        if cite:
            s = EQ_MENTION.sub(self.eq_ref, s)
        return s.replace("\t", " ").strip()

    def eq_ref(self, m):
        before = m.string[max(0, m.start() - 20):m.start()]
        if re.search(r"(?:Supplementary|Extended\s+Data|Suppl\.)\s*$", before, re.I):
            return m.group(0)
        done = [False]

        def one(t):
            n = t.group(1) or t.group(2)
            if n not in self.eq_numbers:
                self.eq_missing.append(n)
                return t.group(0)
            done[0] = True
            return "(\\ref{eq:%s})" % n if t.group(1) else "\\ref{eq:%s}" % n
        items = re.sub(r"\(\s*(\d+[a-z]?)\s*\)|(\d+[a-z]?)", one, m.group(3))
        return m.group(1) + ("~" if done[0] else m.group(2)) + items


def convert(path, add_results=False):
    try:
        z = zipfile.ZipFile(path)
        root = ET.fromstring(z.read("word/document.xml"))
    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        sys.exit(f"docx_to_tex: cannot read {path} as a Word file: {exc}")
    reader = Reader(read_styles(z))
    blocks = []

    def collect(node):
        for el in node:
            if el.tag == W + "p":
                blocks.append(reader.para(el))
            elif el.tag == W + "tbl":
                blocks.append(reader.table(el))
            elif el.tag in (W + "sdt", W + "sdtContent", W + "customXml"):
                collect(el)
    body = root.find(W + "body")
    collect(body if body is not None else root)
    roles = [classify(b) for b in blocks]
    keep = [i for i, (r, _) in enumerate(roles) if r != "empty"]
    blocks, roles = [blocks[i] for i in keep], [roles[i] for i in keep]
    n = len(blocks)
    notes = []
    conv = Converter()

    def words(b):
        return len(re.findall(r"[A-Za-z0-9]+", b.get("plain", "")))

    # ----- front matter: title, byline, affiliations, abstract
    ti = next((i for i, (r, h) in enumerate(roles) if r == "heading" and h["level"] == 0), None)
    if ti is None:
        ti = next((i for i, b in enumerate(blocks) if b["kind"] == "p"), None)
    title = conv.finish(blocks[ti]["tex"], cite=False) if ti is not None else ""
    start = (ti + 1) if ti is not None else 0
    fh = next((i for i in range(start, n) if roles[i][0] == "heading" and roles[i][1]["strong"]), n)
    abstract, body_start = [], fh
    if fh < n and ABSTRACT.fullmatch(roles[fh][1]["name"]):
        end = next((i for i in range(fh + 1, n) if roles[i][0] == "heading"), n)
        keywords = [i for i in range(fh + 1, end) if re.match(r"\s*key\s*words?\b", blocks[i].get("plain", ""), re.I)]
        abstract = [blocks[i]["tex"] for i in range(fh + 1, end) if roles[i][0] == "text" and i not in keywords]
        front_idx, body_start = list(range(start, fh)) + keywords, end
    else:
        long = [i for i in range(start, fh) if blocks[i]["kind"] == "p" and words(blocks[i]) >= 40]
        if long:
            abstract, front_idx, body_start = [blocks[long[0]]["tex"]], list(range(start, long[0])), long[0] + 1
        else:
            front_idx = list(range(start, fh))
            notes.append("no abstract found: no \"Abstract\" heading, and no paragraph of 40 words or more before the first heading")
    front = [conv.finish(blocks[i]["tex"], cite=False) for i in front_idx if blocks[i]["kind"] == "p"]

    # ----- body
    out, bib, floats, slot, consumed = [], [], {"fig": [], "table": [], "other": []}, {}, set()
    state, sections, subsections, unnumbered_refs, objects, ole = "body", 0, 0, 0, 0, 0
    for i in range(body_start, n):
        if i in consumed:
            continue
        role, info = roles[i]
        b = blocks[i]
        if role == "heading":
            name = info["name"]
            if REFS.fullmatch(name):
                state = "refs"
                continue
            state = "body"
            if LEGEND_HEAD.fullmatch(name) or BACK.fullmatch(name):
                out.append("\\section*{%s}" % esc(name))
                continue
            level = max(info["level"], 1)
            out.append("\\%s{%s}" % ({1: "section", 2: "subsection"}.get(level, "subsubsection"), esc(name)))
            sections += level == 1
            subsections += level > 1
            continue
        if role == "legend":
            kind = "other" if info["pre"] else ("table" if info["kind"].lower().startswith("tab") else "fig")
            rest = info["rest"].strip()
            nxt = i + 1
            if not re.search(r"[.!?]\s+\S", rest) and nxt < n and roles[nxt][0] == "text":
                rest += " " + blocks[nxt]["tex"].strip()
                consumed.add(nxt)
                nxt += 1
            tab = None
            if kind != "fig" and nxt < n and roles[nxt][0] == "tbl":
                tab = tabular(blocks[nxt])
                consumed.add(nxt)
            name = norm((info["pre"] or "") + info["kind"] + " " + info["n"])
            if kind not in slot:
                slot[kind] = len(out)
                out.append("\x04%s\x04" % kind)
            floats[kind].append({"n": info["n"], "name": name, "caption": rest, "tabular": tab})
            continue
        if role == "label":
            continue
        if role == "eq":
            conv.eq_numbers.add(info["n"])
            objects += info["object"]
            out.append(("%% equation (%s) is an object whose content is not read\n" % info["n"] if info["object"] else "")
                       + "\\begin{equation}\n%s\n\\label{eq:%s}\n\\end{equation}" % (info["math"].strip(), info["n"]))
            continue
        if role == "display":
            out.append("\\[\n%s\n\\]" % info["math"].strip())
            continue
        if role == "tbl":
            out.append(tabular(b))
            continue
        if state == "refs":
            m = re.match(r"\s*\[?(\d{1,4})(?:\]|\.|\))?\s*(?=[^\d\s.,])(.+)", b["tex"], re.S)
            if m:                                          # EndNote style: the number, a tab, the entry
                bib.append((int(m.group(1)), m.group(2)))
            else:                                          # Word's own list numbering, or no number at all
                unnumbered_refs += not b["numbered"]
                bib.append(((bib[-1][0] + 1) if bib else 1, b["tex"]))
            continue
        ole += b["ole"]
        out.append(b["tex"])

    conv.bib_numbers = {k for k, _ in bib}
    if unnumbered_refs:
        notes.append(f"{unnumbered_refs} reference(s) carry no number; they are numbered in the order of the list")
    keys = [k for k, _ in bib]
    if len(set(keys)) != len(keys):
        notes.append("the reference list numbers an entry twice: " + ", ".join(sorted({str(k) for k in keys if keys.count(k) > 1})))

    def order_key(f):
        return int(re.sub(r"\D", "", f["n"]) or 0)

    for kind, items in floats.items():
        if kind == "other" or not items:
            continue
        nums = [order_key(f) for f in items]
        if nums != sorted(nums):
            notes.append(f"the {'figure' if kind == 'fig' else 'table'} legends stand in the order {', '.join(map(str, nums))}; "
                         "the copy numbers them in the order of their numbers")
        if sorted(nums) != list(range(1, len(nums) + 1)):
            notes.append(f"the {'figure' if kind == 'fig' else 'table'} legends are numbered {', '.join(map(str, sorted(nums)))}: "
                         "a number is missing or given twice")

    body_out = [conv.finish(x) if not x.startswith("\x04") else x for x in out]
    for kind, at in slot.items():
        items = sorted(floats[kind], key=order_key) if kind != "other" else floats[kind]
        envs = []
        for f in items:
            cap = conv.finish(f["caption"])
            if kind == "other":
                envs.append("%% %s\n\\begin{extdata}\n\\caption{%s}%s\n\\end{extdata}"
                            % (f["name"], cap, ("\n" + f["tabular"]) if f["tabular"] else ""))
            else:
                env = "figure" if kind == "fig" else "table"
                envs.append("\\begin{%s}\n\\caption{%s}\n\\label{%s:%s}%s\n\\end{%s}"
                            % (env, cap, "fig" if kind == "fig" else "tab", f["n"], ("\n" + f["tabular"]) if f["tabular"] else "", env))
        if kind == "other":
            envs.insert(0, "% Extended Data and supplementary legends: the scripts do not count these as main items")
        body_out[at] = "\n\n".join(envs)

    # ----- a Results heading
    results = any(re.match(r"\\section\{results?\b", x, re.I) for x in body_out)
    first_sub = None
    for k, x in enumerate(body_out):
        if x.startswith("\\section") and not re.match(r"\\section\{introduction\}", x, re.I):
            break
        if x.startswith("\\subsection{"):
            first_sub = k
            break
    if not results and first_sub is not None:
        if add_results:
            body_out.insert(first_sub, "% added by docx_to_tex.py --add-results: the Word text has no Results heading\n\\section{Results}")
            sections += 1
        else:
            notes.append("the Word text has no Results heading: the subsections after the Introduction count as part of it; "
                         "run again with --add-results to read them as Results")

    if conv.outside:
        notes.append("superscript numbers outside the reference list stay superscripts: " + ", ".join(conv.outside[:10]))
    if conv.eq_missing:
        notes.append("equation numbers cited in the text with no numbered equation of that number: "
                     + ", ".join(sorted(set(conv.eq_missing), key=lambda x: (len(x), x))))
    if not bib:
        notes.append("no reference list found under a \"References\" heading")
    elif not conv.cites:
        notes.append("no superscript citations found: citations by author and year, or by numbers in brackets, are not read")
    if reader.unknown_symbols:
        notes.append(f"{reader.unknown_symbols} symbol(s) of a symbol font could not be read and are left out")
    if objects:
        notes.append(f"{objects} numbered equation(s) are objects (MathType or images) whose content is not read")
    if ole:
        notes.append(f"{ole} object(s) inside running text (MathType formulas, for example) are left out of the copy")
    broken = sum(len(re.findall(r"Error! (?:Reference source not found|Bookmark not defined)", x)) for x in out)
    if broken:
        notes.append(f"{broken} broken Word cross-reference(s) (\"Error! Reference source not found.\") are in the text")

    lines = [MARK + os.path.basename(path) + ", made by docx_to_tex.py. It is not a typeset version of the paper.",
             "% Check every finding of the scripts against the Word text, and make every fix in the Word file.",
             "\\documentclass{article}", "\\usepackage{amsmath}", "\\newenvironment{extdata}{}{}", "\\begin{document}", ""]
    if title:
        lines.append("\\title{%s}" % title)
    for k, f in enumerate(front):
        lines.append(("\\author{%s}" if k == 0 else "\\affiliation{%s}") % f)
    if abstract:
        lines += ["", "\\begin{abstract}", "\n\n".join(conv.finish(a) for a in abstract), "\\end{abstract}"]
    lines += ["\\maketitle", ""]
    for x in body_out:
        lines += [x, ""]
    if bib:
        lines.append("\\begin{thebibliography}{%d}" % max(99, len(bib)))
        lines += ["\\bibitem{r%d} %s" % (k, conv.finish(t, cite=False)) for k, t in bib]
        lines.append("\\end{thebibliography}")
    lines.append("\\end{document}")
    counts = {"sections": sections, "subsections": subsections, "citations": conv.cites, "references": len(bib),
              "equations": len(conv.eq_numbers), "figures": len(floats["fig"]), "tables": len(floats["table"]),
              "other legends": len(floats["other"]), "front lines": len(front), "abstract paragraphs": len(abstract), "title": title}
    return "\n".join(lines) + "\n", counts, notes


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", help="the Word manuscript (.docx)")
    ap.add_argument("-o", "--out", help="the .tex file to write (default: <name>_copy.tex beside the .docx)")
    ap.add_argument("--add-results", action="store_true", dest="add_results",
                    help="put a Results heading before the first subsection after the Introduction, when the Word text has none")
    ap.add_argument("--force", action="store_true", help="overwrite a .tex file that docx_to_tex.py did not write")
    opts = ap.parse_args()
    if not os.path.isfile(opts.docx):
        sys.exit(f"docx_to_tex: no such file: {opts.docx}")
    out = opts.out or os.path.splitext(opts.docx)[0] + "_copy.tex"
    if os.path.isfile(out) and not opts.force:
        with open(out, encoding="utf-8", errors="replace") as fh:
            if not fh.readline().startswith(MARK):
                sys.exit(f"docx_to_tex: {out} exists and was not written by docx_to_tex.py; choose another name or pass --force")
    tex, counts, notes = convert(opts.docx, opts.add_results)
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(tex)
    print(f"docx_to_tex: wrote {out} from {opts.docx}")
    print(f"  title: {counts['title'][:90] or '(none found)'}")
    print(f"  front: {counts['front lines']} line(s) between title and abstract, {counts['abstract paragraphs']} abstract paragraph(s)")
    print(f"  headings: {counts['sections']} section(s), {counts['subsections']} subsection(s)")
    print(f"  citations: {counts['citations']} \\cite command(s); references: {counts['references']} \\bibitem entries")
    print(f"  numbered equations: {counts['equations']}; figures: {counts['figures']}; tables: {counts['tables']}; "
          f"Extended Data and supplementary legends: {counts['other legends']}")
    if notes:
        print("\nNOTES")
        for note in notes:
            print("  - " + note)
    print("\nThe copy is for the scripts only: check every finding against the Word text before reporting it.")


if __name__ == "__main__":
    main()
