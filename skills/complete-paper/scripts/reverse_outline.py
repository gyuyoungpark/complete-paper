#!/usr/bin/env python3
"""reverse_outline.py: the first sentence of every paragraph, section by section.

Read the list in order. It should tell the paper's argument, and each first
sentence should follow from the one before. This is how ground rule 15 of the
complete-paper skill is evaluated: a paragraph whose first sentence serves no
statement of the outline, or does not follow from its neighbour, is cut, moved
or given a bridging sentence.

Marked for review (heuristics, not verdicts):
  ONE SENTENCE   a paragraph of one sentence, often dropped in without context
  POINTS BACK    a section opens with "This", "These", "It", "Such" ...: there
                 is nothing before it in the section to point to
  ADDITIVE       opens with "Furthermore", "Moreover", "Additionally", "In
                 addition": the link to the previous paragraph is not said

Standard library only. LaTeX sources; \\input and \\include are followed.
Floats, displayed equations, the abstract and the bibliography are skipped.

Usage:
  python reverse_outline.py main.tex
  python reverse_outline.py main.tex --width 140
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_tex import (Doc, Regions, SENT_END_RE, blank_spans, command_arg_spans,  # noqa: E402
                       env_spans, math_spans, prose, sections, subtract)

HEADINGS = ["part", "chapter", "section", "subsection", "subsubsection", "paragraph"]
POINTS_BACK = re.compile(r"^(?:This|These|That|Those|It|They|Such|Their|Its|Here,? this)\b")
ADDITIVE = re.compile(r"^(?:Furthermore|Moreover|Additionally|In addition|Also)\b")


def readable(s):
    """A sentence of LaTeX source made readable: citations dropped, references and math shortened."""
    s = re.sub(r"~?\\[a-zA-Z]*cite[a-zA-Z]*\*?\s*(?:\[[^\]]*\]\s*){0,2}\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:eq)?ref\*?\s*\{[^}]*\}|\\(?:autoref|cref|Cref)\s*\{[^}]*\}", "#", s)
    s = re.sub(r"\$([^$]*)\$", lambda m: re.sub(r"\\([A-Za-z]+)", r"\1", m.group(1)).replace("{", "").replace("}", ""), s)
    s = re.sub(r"\\[A-Za-z@]+\*?", "", s).replace("{", "").replace("}", "").replace("~", " ")
    return " ".join(s.split())


def paragraphs(doc):
    text = doc.text
    R = Regions(text)
    keep = subtract(R.body(), R.floats + env_spans(text, ["thebibliography", "abstract"]))
    display, _ = math_spans(text)
    p = prose(text)
    chars = list(p)
    for a, b in display:                                 # a displayed equation stays inside its paragraph
        for i in range(a, b):
            if chars[i] != "\n":
                chars[i] = "M"
    p = "".join(chars)
    p = blank_spans(p, command_arg_spans(text, HEADINGS, inner=False))
    p = blank_spans(p, subtract([(0, len(p))], keep))
    out = []
    for m in re.finditer(r"\S(?:.*?)(?=\n[ \t]*\n|\Z)", p, re.S):
        if len(re.findall(r"[A-Za-z]{2,}", m.group())) < 3:
            continue                                     # leftovers of commands, not a paragraph
        a, b = m.start(), m.end()
        ends = [e for e in SENT_END_RE.finditer(p, a, b)]
        first_end = ends[0].end() if ends else b
        n = max(1, len(ends) + (1 if not ends or p[ends[-1].end():b].strip() else 0))
        out.append((a, readable(text[a:first_end]), n))
    return out


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("main", help="main .tex file")
    ap.add_argument("--width", type=int, default=160, help="cut each first sentence to this many characters")
    args = ap.parse_args()
    if not os.path.isfile(args.main):
        sys.exit("file not found: %s" % args.main)

    doc = Doc(args.main)
    secs = sections(doc.text)
    current, k, marked, total = None, 0, 0, 0
    for off, first, n in paragraphs(doc):
        heading = ([h for s, h in secs if s <= off] or ["(before the first section)"])[-1]
        opens_section = heading != current
        if opens_section:
            print("\n== %s ==" % heading)
            current = heading
        k += 1
        total += 1
        marks = []
        if n == 1:
            marks.append("ONE SENTENCE")
        if opens_section and POINTS_BACK.match(first):
            marks.append("POINTS BACK")
        if ADDITIVE.match(first):
            marks.append("ADDITIVE")
        marked += bool(marks)
        line = first if len(first) <= args.width else first[:args.width - 3] + "..."
        print("%3d. (%d) %s%s" % (k, n, line, "   <- " + ", ".join(marks) if marks else ""))
    print("\nparagraphs: %d   marked for review: %d   (n) = sentences in the paragraph" % (total, marked))


if __name__ == "__main__":
    main()
