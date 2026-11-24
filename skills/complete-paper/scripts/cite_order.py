#!/usr/bin/env python3
"""Check that every figure, table and panel is cited in the text, and in order.

Usage:
    python3 cite_order.py main.tex [more.tex ...]

Reports:
  errors    a figure or table that the text never cites
  warnings  figures or tables first cited out of numerical order; a panel named in a caption,
            (a), (b), ..., that the text never cites
  notes     paragraphs that open by pointing at a display item ("Figure 3 shows ..."): the finding
            should lead and the figure follow in parentheses; sentences that begin with "Fig." or
            "Eq." (many venues spell the word out there); figure and table numbers typed by hand

and prints, for every figure and table, where it is first cited, how often, and which panels.

The script reads LaTeX source and follows \\input. Floats are numbered in their order of appearance;
items of a supplement (Fig. S1, labels with an xr prefix) are left to supp_check.py.
Standard library only. Exit status is 1 on errors.
"""
import os
import re
import sys
from collections import OrderedDict

REF = re.compile(r"\\[A-Za-z]*[Rr]ef\*?\s*\{([^}]*)\}")
TYPED = re.compile(r"(?<![A-Za-z])(Figs?\.|Figures?|Tables?|Tab\.)(?:\s|~|\\,)*((?:\d+|[IVXL]+\b)(?![.\d]*\s*(?:nm|K|T|ns|ps|eV|mA|\\%|%)))")
BEFORE_SUPP = re.compile(r"(Supplement(?:al|ary)|Supporting|Extended\s+Data|Suppl?\.)\s*$", re.I)
OPENER = re.compile(r"^\W*(?:As\s+(?:shown|seen|can\s+be\s+seen)\s+in\s+)?(?:Figures?|Figs?\.|Tables?)(?:\s|~)*(?:\\[A-Za-z]*ref\*?\s*\{[^}]*\}|\d+|[IVXL]+)"
                    r"\S{0,6}\s+(?:shows?|presents?|displays?|illustrates?|depicts?|plots?|summari[sz]es?|compares?|gives?|reports?|lists?)\b")
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def read_tex(path, depth=0):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit(f"cite_order: cannot read {path}: {exc.strerror}")
    folder, out = os.path.dirname(os.path.abspath(path)), []
    for n, line in enumerate(raw.split("\n"), 1):
        line = re.sub(r"(?<!\\)%.*", "", line)
        m = re.search(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", line)
        if m and depth < 5:
            hit = next((os.path.join(folder, c) for c in (m.group(1).strip(), m.group(1).strip() + ".tex")
                        if os.path.isfile(os.path.join(folder, c))), None)
            if hit:
                out.extend(read_tex(hit, depth + 1))
                continue
        out.append((os.path.basename(path), n, line))
    return out


def roman(s):
    if s.isdigit():
        return int(s)
    total, prev = 0, 0
    for c in reversed(s):
        v = ROMAN.get(c, 0)
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def group(text, i):
    depth, j = 0, i
    while j < len(text):
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j]
        j += 1
    return text[i + 1:]


def panels_after(tail):
    """Panel letters cited right after a figure reference: (a), (a,b), (a)-(c), 2a,b, (a) and (b)."""
    letters, pos = [], 0
    attached = re.match(r"([a-l])(?![a-z])((?:\s*(?:,|--?|\u2013)\s*[a-l](?![a-z]))*)", tail)
    if attached:
        spec = attached.group(0)
    else:
        spec, pos = "", 0
        while True:
            m = re.match(r"\s*(?:,|and|--?-?|\u2013|to|or)?\s*(?:\d+\s*)?\(([a-l](?:\s*(?:,|--?|\u2013|and)\s*[a-l])*)\)", tail[pos:])
            if not m or pos > 60:
                break
            spec += " " + m.group(0)
            pos += m.end()
    found = re.findall(r"(?<![a-z])([a-l])(?![a-z])|(--?-?|\u2013|\bto\b)", spec)
    span = False
    for letter, dash in found:
        if dash:
            span = True
        elif letter:
            if span and letters:
                letters.extend(chr(c) for c in range(ord(letters[-1]) + 1, ord(letter) + 1))
            else:
                letters.append(letter)
            span = False
    return letters


def check(lines):
    text = "\n".join(t for _, _, t in lines)
    offsets, pos = [], 0
    for _, _, t in lines:
        offsets.append(pos)
        pos += len(t) + 1

    def where(p):
        import bisect
        f, n, _ = lines[max(bisect.bisect_right(offsets, p) - 1, 0)]
        return f"{f}:{n}"

    a = text.find("\\begin{document}")
    start = a if a >= 0 else 0
    bib = re.search(r"\\begin\{thebibliography\}", text)
    end = bib.start() if bib else len(text)
    # ----- floats
    floats, labels, counts, spans = OrderedDict(), {}, {"fig": 0, "table": 0}, []
    for m in re.finditer(r"\\begin\{(figure|table|SCfigure|sidewaysfigure|sidewaystable|longtable)(\*?)\}", text):
        close = text.find("\\end{%s%s}" % (m.group(1), m.group(2)), m.end())
        if close < 0:
            continue
        inner = text[m.end():close]
        kind = "table" if "table" in m.group(1) else "fig"
        counts[kind] += 1
        cap = re.search(r"\\caption\*?\s*(?:\[[^\]]*\])?\s*\{", inner)
        caption = group(inner, cap.end() - 1) if cap else ""
        panels = sorted(set(re.findall(r"\(([a-l])\)", caption)) | set(re.findall(r"\\textbf\s*\{\(?([a-l])\)?[,.]?\}", caption))
                        | set(re.findall(r"(?:^|[.;:,]\s+|\n\s*)([a-l])\)\s", caption)))
        key = (kind, counts[kind])
        floats[key] = {"labels": re.findall(r"\\label\s*\{([^}]*)\}", inner), "pos": m.start(), "panels": panels if len(panels) >= 2 else [],
                       "cites": [], "cited_panels": set()}
        for lab in floats[key]["labels"]:
            labels[lab] = key
        spans.append((m.start(), close))
    flow = list(text)
    for s, e in spans:
        for k in range(s, e):
            if flow[k] != "\n":
                flow[k] = " "
    flow = "".join(flow)
    # ----- citations in the running text
    typed = 0
    for m in REF.finditer(flow, start, end):
        for lab in m.group(1).split(","):
            key = labels.get(lab.strip())
            if key:
                floats[key]["cites"].append(m.start())
                floats[key]["cited_panels"].update(panels_after(flow[m.end():m.end() + 80]))
    for m in TYPED.finditer(flow, start, end):
        if BEFORE_SUPP.search(flow[max(0, m.start() - 22):m.start()]):
            continue
        kind = "table" if m.group(1).lower().startswith("tab") else "fig"
        if kind == "fig" and not m.group(2).isdigit():
            continue
        key = (kind, roman(m.group(2)))
        if key in floats:
            typed += 1
            floats[key]["cites"].append(m.start())
            floats[key]["cited_panels"].update(panels_after(flow[m.end():m.end() + 80]))
    found = []

    def add(level, place, msg):
        found.append((level, place, msg))

    name = {"fig": "Fig.", "table": "Table"}
    for kind in ("fig", "table"):
        mine = [(k, f) for k, f in floats.items() if k[0] == kind]
        for key, f in mine:
            if not f["cites"]:
                add("E", where(f["pos"]), f"{name[kind]} {key[1]} is never cited in the text")
            missing = [p for p in f["panels"] if p not in f["cited_panels"]]
            if f["cites"] and missing:
                add("W", where(f["pos"]), f"{name[kind]} {key[1]}: panel{'s' if len(missing) > 1 else ''} "
                                         + ", ".join(f"({p})" for p in missing) + " named in the caption and never cited in the text")
        first = sorted((min(f["cites"]), key[1]) for key, f in mine if f["cites"])
        order = [n for _, n in first]
        if order != sorted(order):
            add("W", "text", f"{name[kind].rstrip('.')}s are first cited in the order " + ", ".join(str(n) for n in order)
                             + ": number them in the order of first citation")
    if typed:
        add("N", "text", f"{typed} figure or table number(s) are typed by hand: use \\ref, so that reordering cannot break them")
    openers = []
    for m in re.finditer(r"(?:[^\n]*\S[^\n]*\n?)+", flow[start:end]):
        par = m.group(0)
        clean = re.sub(r"\\(?:sub)*(?:section|paragraph)\*?\s*(?:\[[^\]]*\])?\{[^{}]*\}|\\label\s*\{[^{}]*\}|\\noindent|\\indent", " ", par).lstrip()
        if OPENER.match(clean):
            openers.append((where(start + m.start()), re.sub(r"\s+", " ", clean)[:70]))
    for place, quote in openers:
        add("N", place, f"the paragraph opens by pointing at a display item (\"{quote}...\"): lead with what it establishes")
    starts = [where(start + m.start()) for m in re.finditer(r"(?<=[.!?]\s)(?:Figs?\.|Eqs?\.|Tab\.|Refs?\.)(?=\s|~)", flow[start:end])]
    if starts:
        add("N", starts[0], f"{len(starts)} sentence(s) begin with an abbreviation (Fig., Eq., Ref.): many venues spell the word out at the start of a sentence"
                            + ("; also at " + ", ".join(starts[1:6]) if len(starts) > 1 else ""))
    return floats, found, where


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    files = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not files or "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    lines = [line for p in files for line in read_tex(p)]
    floats, found, where = check(lines)
    print("cite_order: " + ", ".join(files))
    if floats:
        print("\nITEM       FIRST CITED            TIMES  PANELS CITED / IN CAPTION")
        for (kind, n), f in floats.items():
            label = ("Fig. " if kind == "fig" else "Table ") + str(n)
            first = where(min(f["cites"])) if f["cites"] else "never"
            panels = (",".join(sorted(f["cited_panels"] & set(f["panels"]))) or "-") + " / " + (",".join(f["panels"]) or "-")
            print(f"  {label:<9} {first:<22} {len(f['cites']):>5}  {panels}")
    for level, title in (("E", "ERRORS"), ("W", "WARNINGS"), ("N", "NOTES")):
        rows = [(w, m) for lv, w, m in found if lv == level]
        if rows:
            print(f"\n{title} ({len(rows)})")
            for w, m in rows:
                print(f"  {w}: {m}")
    counts = [sum(1 for lv, _, _ in found if lv == x) for x in "EWN"]
    print(f"\n{counts[0]} error(s), {counts[1]} warning(s), {counts[2]} note(s)")
    sys.exit(1 if counts[0] else 0)


if __name__ == "__main__":
    main()
