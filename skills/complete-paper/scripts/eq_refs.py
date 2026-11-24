#!/usr/bin/env python3
"""Check equation labels and references in LaTeX sources.

Usage:
    python3 eq_refs.py main.tex [supplement.tex ...]

Reports, across all files given:
  - references that do not resolve to a label
  - labels defined more than once
  - equation numbers typed by hand ("Eq. (3)" instead of Eq.~\\eqref{...})
  - numbered display environments that carry no label
  - equation labels that are never cited (information only)
  - unnumbered displays (information only)

Exit status is 1 if a reference is unresolved, a label is duplicated, or a
number is typed by hand; otherwise 0. The check reads the source text only:
it does not expand macros or follow \\input, so pass every file explicitly.

Main text and supplement as two documents. If a file links to another with the
xr package and a prefix, as in \\externaldocument[S-]{supplement}, each file
that holds a \\documentclass starts a document of its own (files without one
belong to the document before them in the argument list). A reference then
resolves inside its own document, or, with the prefix, in another document:
\\ref{S-eq:result} points to \\label{eq:result} of the supplement. The same label
key in two documents is then not a duplicate. Without a prefix, all files form
one set of labels.
"""
import re
import sys

NUMBERED = ["equation", "align", "gather", "multline", "eqnarray", "flalign", "alignat"]
REF_CMD = r"\\(?:eqref|ref|cref|Cref|autoref|labelcref)\*?\s*\{([^}]*)\}"
HAND = re.compile(r"\b(?:Eqs?\.|Equations?)\s*~?\s*\(?\s*[AS]?\d+[a-z]?\b")


def strip_comments(text):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.split("\n"))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    files = sys.argv[1:]
    if not files or files[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    docs = []          # one per document: labels, equation labels, references, xr prefixes
    unlabeled, hand, unnumbered = [], [], 0

    for f in files:
        text = strip_comments(open(f, encoding="utf-8", errors="replace").read())
        if "\\documentclass" in text or not docs:
            docs.append({"labels": {}, "eq": set(), "refs": [], "prefixes": []})
        d = docs[-1]
        d["prefixes"] += [p for p in re.findall(r"\\externaldocument\s*\[([^\]]*)\]", text) if p]

        for m in re.finditer(r"\\label\s*\{([^}]*)\}", text):
            d["labels"].setdefault(m.group(1), []).append((f, line_of(text, m.start())))
        for m in re.finditer(REF_CMD, text):
            for key in m.group(1).split(","):
                if key.strip():
                    d["refs"].append((key.strip(), f, line_of(text, m.start())))

        for env in NUMBERED:
            pat = re.compile(r"\\begin\{%s\}(.*?)\\end\{%s\}" % (env, env), re.S)
            for m in pat.finditer(text):
                found = re.findall(r"\\label\s*\{([^}]*)\}", m.group(1))
                d["eq"].update(found)
                if not found:
                    unlabeled.append((f, line_of(text, m.start()), env))

        unnumbered += len(re.findall(r"\\begin\{(?:%s)\*\}" % "|".join(NUMBERED), text))
        unnumbered += len(re.findall(r"\\\[", text)) + len(re.findall(r"\$\$", text)) // 2

        for m in HAND.finditer(text):
            hand.append((f, line_of(text, m.start()), m.group(0).strip()))

    linked = any(d["prefixes"] for d in docs)
    if not linked and len(docs) > 1:                     # no prefix anywhere: one set of labels, as LaTeX sees it
        one = {"labels": {}, "eq": set(), "refs": [], "prefixes": []}
        for d in docs:
            for key, places in d["labels"].items():
                one["labels"].setdefault(key, []).extend(places)
            one["eq"] |= d["eq"]
            one["refs"] += d["refs"]
        docs = [one]
    for d in docs:
        d["eq"] |= {k for k in d["labels"] if k.lower().startswith(("eq:", "eq.", "eqn:", "eq_"))}

    cited, unresolved = set(), []
    for i, d in enumerate(docs):
        for key, f, n in d["refs"]:
            if key in d["labels"]:
                cited.add((i, key))
                continue
            hit = None
            for p in d["prefixes"]:
                if key.startswith(p):
                    hit = next(((j, key[len(p):]) for j, o in enumerate(docs) if j != i and key[len(p):] in o["labels"]), hit)
            if hit:
                cited.add(hit)
            else:
                unresolved.append((key, f, n))
    duplicate = {k: v for d in docs for k, v in d["labels"].items() if len(v) > 1}
    uncited = sorted(k for i, d in enumerate(docs) for k in d["eq"] if (i, k) not in cited)
    n_labels = sum(len(d["labels"]) for d in docs)
    n_eq = sum(len(d["eq"]) for d in docs)
    n_refs = sum(len(d["refs"]) for d in docs)

    def section(title, rows):
        print(f"{title}: {len(rows)}")
        for r in rows:
            print("   " + r)

    section("Unresolved references", [f"{f}:{n}  {k}" for k, f, n in unresolved])
    section("Duplicate labels", [f"{k}  at " + ", ".join(f"{f}:{n}" for f, n in v)
                                 for k, v in duplicate.items()])
    section("Equation numbers typed by hand", [f"{f}:{n}  {s}" for f, n, s in hand])
    section("Numbered displays without a label", [f"{f}:{n}  {env}" for f, n, env in unlabeled])
    section("Equation labels never cited (information)", uncited)
    print(f"Unnumbered displays (information): {unnumbered}")
    print(f"Labels: {n_labels}   equation labels: {n_eq}   references: {n_refs}")
    if linked:
        print(f"Documents: {len(docs)}, linked by the prefixes " + ", ".join(sorted({p for d in docs for p in d['prefixes']})))

    sys.exit(1 if (unresolved or duplicate or hand) else 0)


if __name__ == "__main__":
    main()
