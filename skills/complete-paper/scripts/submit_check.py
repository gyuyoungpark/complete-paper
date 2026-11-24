#!/usr/bin/env python3
"""Check a manuscript folder before submission, and make a clean copy of what is sent.

Usage:
    python3 submit_check.py main.tex
    python3 submit_check.py main.tex --supp supplement.tex --line-numbers
    python3 submit_check.py main.tex --anonymous --authors "Ada Author" "Bo Author"
    python3 submit_check.py main.tex --arxiv
    python3 submit_check.py main.tex --plain              (title and abstract as plain text for the forms)
    python3 submit_check.py main.tex --pack submitted/    (clean copy: only the files the sources use,
                                                           comments removed; add --compile to build it)

Checks:
  files       figures, inputs, bibliography and local class or style files that the sources use and
              the folder does not hold (error); names that differ only in case, absolute paths, paths
              that leave the folder, spaces in names; files in the folder that nothing uses
  leftovers   comments in the sources, text after \\end{document}, \\iffalse blocks, to-do marks
  layout      --line-numbers: the lineno package or the class option is in use
  anonymity   --anonymous: author block, acknowledgments, funding, phrases that identify the authors
              ("our previous work"), author names in the text, author names in the PDF properties
  arXiv       --arxiv: abstract over 1920 characters; neither .bib nor .bbl; mixed figure formats;
              cross-file references with xr; comments (arXiv publishes the sources)
  PDF         if main.pdf and the poppler tools are present: fonts not embedded, Type 3 fonts,
              author in the properties, page count
  supplement  --supp: the same checks of files for the supplement, and a reminder of what the venue
              wants with a deposit

The script reads LaTeX sources and follows \\input. It prepares and checks; it does not submit.
Standard library only (pdffonts, pdfinfo and pdflatex are used when installed).
Exit status is 1 on errors.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

GRAPHIC_EXT = [".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps"]
JUNK = re.compile(r"\.(aux|log|out|toc|lof|lot|fls|fdb_latexmk|synctex\.gz|blg|bak|backup|swp|nav|snm|run\.xml|bcf|dvi|spl)$|~$|^\.DS_Store$", re.I)
SELF = re.compile(r"\b(our|my)\s+(?:previous|earlier|prior|recent|own)\s+(?:work|paper|study|studies|results?|report|letter|experiments?)\b|"
                  r"\bwe\s+(?:have\s+)?(?:previously|recently|earlier)\s+(?:showed|shown|reported|demonstrated|found|proposed|developed)\b|"
                  r"\bas\s+we\s+(?:showed|reported|demonstrated)\b|\bin\s+our\s+(?:group|laboratory|lab)\b", re.I)
TODO = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b|\\todo\b|\?\?")


def read_file(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit(f"submit_check: cannot read {path}: {exc.strerror}")


def strip_comments(text):
    """The source without comments; verbatim-like environments are left as they are."""
    out, keep = [], False
    for line in text.split("\n"):
        if re.search(r"\\begin\{(verbatim|lstlisting|minted|comment)\}", line):
            keep = True
        if keep:
            out.append(line)
        else:
            cut = re.sub(r"(?<!\\)%.*", "", line)
            if cut.strip() or not line.strip().startswith("%"):
                out.append(cut.rstrip() + ("%" if line.rstrip().endswith("%") and cut.rstrip() != line.rstrip() and cut.strip() else ""))
        if re.search(r"\\end\{(verbatim|lstlisting|minted|comment)\}", line):
            keep = False
    text = "\n".join(out)
    end = text.find("\\end{document}")
    return text[:end + len("\\end{document}")] + "\n" if end >= 0 else text


def find(folder, name, exts):
    """(path found, problem) for a file named in the source."""
    if os.path.isabs(name) or name.startswith(("/", "\\")):  # rooted paths too, which Windows does not call absolute
        return None, "an absolute path"
    if ".." in name.replace("\\", "/").split("/"):
        return None, "a path that leaves the folder"
    for ext in [""] + exts:
        cand = os.path.join(folder, name + ext)
        if os.path.isfile(cand):
            real = os.listdir(os.path.dirname(cand) or ".")
            if os.path.basename(cand) not in real:
                return cand, "a name that differs from the file only in upper and lower case"
            return cand, None
    d = os.path.dirname(os.path.join(folder, name)) or folder
    if os.path.isdir(d):
        want = os.path.basename(name).lower()
        for f in os.listdir(d):
            if f.lower() == want or os.path.splitext(f)[0].lower() == want:
                return os.path.join(d, f), "a name that differs from the file only in upper and lower case"
    return None, "missing"


def collect(path, used, problems, depth=0):
    """Follow a source file: record every file it uses, and what is wrong with the names."""
    folder = os.path.dirname(os.path.abspath(path))
    used.add(os.path.abspath(path))
    raw = read_file(path)
    text = re.sub(r"(?<!\\)%.*", "", raw)

    def note(name, kind, line):
        hit, problem = find(folder, name, {"graphic": GRAPHIC_EXT, "tex": [".tex"], "bib": [".bib"], "cls": [".cls"], "sty": [".sty"], "bst": [".bst"]}[kind])
        if hit:
            used.add(os.path.abspath(hit))
        if problem == "missing" and kind in ("cls", "sty", "bst"):
            return None                                  # from the TeX distribution
        if problem:
            problems.append((f"{os.path.basename(path)}:{line}", name, kind, problem))
        if " " in name:
            problems.append((f"{os.path.basename(path)}:{line}", name, kind, "a space in the name"))
        return hit

    for n, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"\\includegraphics\*?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", line):
            if not m.group(1).startswith("example-image"):
                note(m.group(1).strip(), "graphic", n)
        for m in re.finditer(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", line):
            hit = note(m.group(1).strip(), "tex", n)
            if hit and depth < 6:
                collect(hit, used, problems, depth + 1)
        for m in re.finditer(r"\\(?:bibliography|addbibresource)\s*\{([^}]+)\}", line):
            for name in m.group(1).split(","):
                note(name.strip(), "bib", n)
        for m in re.finditer(r"\\documentclass\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", line):
            note(m.group(1).strip(), "cls", n)
        for m in re.finditer(r"\\usepackage\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", line):
            for name in m.group(1).split(","):
                note(name.strip(), "sty", n)
        for m in re.finditer(r"\\bibliographystyle\s*\{([^}]+)\}", line):
            note(m.group(1).strip(), "bst", n)
        for m in re.finditer(r"\\externaldocument\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", line):
            aux = os.path.join(folder, m.group(1).strip() + ".aux")
            if os.path.isfile(aux):
                used.add(os.path.abspath(aux))
    return raw


def plain(tex):
    t = re.sub(r"(?<!\\)%.*", "", tex)
    t = re.sub(r"\\(?:cite\w*|label|thanks|footnote)\*?\s*(?:\[[^\]]*\])*\{[^{}]*\}", "", t)
    t = re.sub(r"\$_\{?(\w+)\}?\$", r"\1", t)
    t = re.sub(r"\\\\", " ", t)
    t = re.sub(r"\\(?:mathrm|text|textrm|textit|textbf|emph|mbox)\s*\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\[A-Za-z]+\*?", "", t)
    return re.sub(r"\s+", " ", re.sub(r"[{}~]", " ", t)).strip()


def brace(text, i):
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


def tool(cmd):
    if not shutil.which(cmd[0]):
        return None
    try:
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Check a manuscript folder before submission.")
    ap.add_argument("main")
    ap.add_argument("--supp", nargs="+", default=[])
    ap.add_argument("--line-numbers", action="store_true", dest="line_numbers", help="the venue wants line numbers in the review copy")
    ap.add_argument("--anonymous", action="store_true", help="the review hides the authors")
    ap.add_argument("--authors", nargs="+", default=[], help="author names to look for in an anonymized copy")
    ap.add_argument("--arxiv", action="store_true", help="add the checks for an arXiv submission")
    ap.add_argument("--plain", action="store_true", help="print title and abstract as plain text")
    ap.add_argument("--pack", metavar="DIR", help="write a clean copy of the files that are sent")
    ap.add_argument("--compile", action="store_true", help="with --pack: build the copy with pdflatex")
    opts = ap.parse_args()
    for p in [opts.main] + opts.supp:
        if not os.path.isfile(p):
            sys.exit(f"submit_check: no such file: {p}")
    folder = os.path.dirname(os.path.abspath(opts.main))
    found = []

    def add(level, where, msg):
        found.append((level, where, msg))

    used, problems, raws = set(), [], {}
    for p in [opts.main] + opts.supp:
        raws[p] = collect(p, used, problems)
    for where, name, kind, problem in problems:
        level = "E" if problem in ("missing", "an absolute path", "a path that leaves the folder") else "W"
        what = {"graphic": "figure", "tex": "input file", "bib": "bibliography", "cls": "class", "sty": "package", "bst": "style"}[kind]
        add(level, where, f"{what} \"{name}\": {problem}" + ("" if problem != "missing" else "; the venue's system will not find it either"))
    sources = [u for u in used if u.endswith((".tex", ".ltx"))]
    raw_all = {u: read_file(u) for u in sources}
    main_raw = raws[opts.main]
    # ----- bibliography
    has_bib = any(u.endswith(".bib") for u in used)
    bbl = os.path.splitext(os.path.abspath(opts.main))[0] + ".bbl"
    typed = "\\begin{thebibliography}" in "".join(raw_all.values())
    if not (has_bib or typed or os.path.isfile(bbl)):
        add("W", os.path.basename(opts.main), "no bibliography was found: neither a .bib file, nor a .bbl, nor a typed list")
    if os.path.isfile(bbl):
        used.add(bbl)
    # ----- files that nothing uses
    extra, junk = [], []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".") and os.path.abspath(os.path.join(root, d)) != os.path.abspath(opts.pack or "\0")]
        for f in files:
            full = os.path.abspath(os.path.join(root, f))
            rel = os.path.relpath(full, folder).replace(os.sep, "/")  # the same on every system
            if full in used or os.path.splitext(full)[0] + ".tex" in used and f.endswith(".pdf"):
                continue
            (junk if JUNK.search(f) or f.startswith(".") else extra).append(rel)
    if extra:
        add("N", "folder", f"{len(extra)} file(s) that the sources do not use: " + ", ".join(sorted(extra)[:10]) + (" ..." if len(extra) > 10 else "")
                           + "; send only what is needed (--pack makes such a copy)")
    # ----- leftovers
    comments = 0
    for u, raw in raw_all.items():
        name = os.path.basename(u)
        lines = raw.split("\n")
        c = sum(1 for line in lines if re.search(r"(?<!\\)%\s*\S", line))
        comments += c
        after = raw.split("\\end{document}", 1)[1].strip() if "\\end{document}" in raw else ""
        if after:
            add("W", name, f"{len(after.split())} words after \\end{{document}}: remove them")
        if re.search(r"\\iffalse\b|\\begin\{comment\}", raw):
            add("W", name, "text switched off with \\iffalse or a comment environment is still in the file")
        for n, line in enumerate(lines, 1):
            if TODO.search(line):
                add("E", f"{name}:{n}", f"a to-do mark or an unresolved reference: \"{line.strip()[:60]}\"")
    if comments:
        add("W" if opts.arxiv else "N", "sources", f"{comments} line(s) carry comments"
            + (": arXiv publishes the sources, comments included" if opts.arxiv else "; a copy without them is safer to send") + " (--pack removes them)")
    # ----- layout
    if opts.line_numbers:
        joined = "".join(raw_all.values())
        if not (re.search(r"\\usepackage(?:\[[^\]]*\])?\{[^}]*lineno[^}]*\}", joined) and "\\linenumbers" in joined) and \
                not re.search(r"\\documentclass\s*\[[^\]]*linenumbers[^\]]*\]", joined):
            add("E", os.path.basename(opts.main), "no line numbers: add \\usepackage{lineno} and \\linenumbers, or the class option linenumbers")
    # ----- anonymity
    body = re.sub(r"(?<!\\)%.*", "", main_raw)
    names = list(opts.authors)
    for m in re.finditer(r"\\author\s*(?:\[[^\]]*\])?\s*\{", body):
        for person in re.split(r"\\and\b|\\\\", brace(body, m.end() - 1)):
            person = plain(person)
            if len(person.split()) >= 2:
                names.append(person)
    if opts.anonymous:
        if re.search(r"\\author\s*(?:\[[^\]]*\])?\s*\{\s*[^}\s]", body):
            add("E", os.path.basename(opts.main), "the author block is filled in; the review copy must not name the authors")
        for pattern, what in ((r"\\(?:affiliation|address|email)\s*\{\s*[^}\s]", "affiliation or address"),
                              (r"\\begin\{acknowledgments?\}|\\section\*?\{\s*Acknowledg|\\acknowledgments?\b|\\paragraph\*?\{\s*Acknowledg", "acknowledgments"),
                              (r"\bsupported\s+by\b|\bGrant\s+No", "a funding statement")):
            if re.search(pattern, body, re.I):
                add("E", os.path.basename(opts.main), f"{what} in the review copy: move it to the file kept for the final version")
        bib_at = body.find("\\begin{thebibliography}")
        text = body if bib_at < 0 else body[:bib_at]
        for n, line in enumerate(text.split("\n"), 1):
            m = SELF.search(line)
            if m:
                add("W", f"{os.path.basename(opts.main)}:{n}", f"\"{m.group(0)}\" identifies the authors: cite the work in the third person")
        doc = text[text.find("\\begin{document}"):]
        for person in dict.fromkeys(opts.authors):
            surname = person.split()[-1]
            if len(surname) > 2 and re.search(rf"(?<![A-Za-z]){re.escape(surname)}(?![A-Za-z])", re.sub(r"\\author\s*\{[^}]*\}", "", doc)):
                add("W", os.path.basename(opts.main), f"the name \"{surname}\" appears in the text of the review copy")
        if re.search(r"github\.com/|gitlab\.com/|bitbucket\.org/", doc, re.I):
            add("W", os.path.basename(opts.main), "a link to a code repository may name the authors: use an anonymized link for review")
    # ----- arXiv
    am = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S)
    abstract = plain(am.group(1)) if am else ""
    tm = re.search(r"\\title\s*(?:\[[^\]]*\])?\s*\{", body)
    title = plain(brace(body, tm.end() - 1)) if tm else ""
    if opts.arxiv:
        if len(abstract) > 1920:
            add("E", "abstract", f"{len(abstract)} characters as plain text; arXiv takes at most 1920")
        if not (has_bib or os.path.isfile(bbl) or typed):
            add("E", "bibliography", "arXiv needs the .bib file(s) or a .bbl named like the main file")
        kinds = {os.path.splitext(u)[1].lower() for u in used if os.path.splitext(u)[1].lower() in GRAPHIC_EXT}
        if kinds & {".eps", ".ps"} and kinds & {".pdf", ".png", ".jpg", ".jpeg"}:
            add("E", "figures", "PostScript and PDF or bitmap figures are mixed: one compiler cannot read both; convert to one family")
        if re.search(r"\\externaldocument", "".join(raw_all.values())):
            add("W", "sources", "cross-file references with xr: arXiv lists them as a cause of failure when main text and supplement are built separately; "
                                "replace them by the printed numbers in the copy for arXiv")
        if title and (title.isupper() or re.search(r"[^\x00-\x7f]", title)):
            add("N", "title", "arXiv asks for a title without all-capitals and without characters outside ASCII in the form")
    # ----- PDF
    pdf = os.path.splitext(os.path.abspath(opts.main))[0] + ".pdf"
    if os.path.isfile(pdf):
        fonts = tool(["pdffonts", pdf])
        if fonts:
            rows = [r.split() for r in fonts.splitlines()[2:] if r.strip()]
            not_emb = [r[0] for r in rows if len(r) >= 5 and "no" in r[-5:-3]]
            if not_emb:
                add("E", os.path.basename(pdf), f"{len(not_emb)} font(s) are not embedded: " + ", ".join(not_emb[:5]))
            if any("Type 3" in r for r in fonts.splitlines()):
                add("W", os.path.basename(pdf), "Type 3 fonts in the PDF (usually from a figure): text may be drawn as bitmaps; see parts/figures.md, export")
        info = tool(["pdfinfo", pdf])
        if info:
            pages = re.search(r"^Pages:\s+(\d+)", info, re.M)
            author = re.search(r"^Author:\s+(\S.*)$", info, re.M)
            if pages:
                add("N", os.path.basename(pdf), f"{pages.group(1)} page(s)")
            if opts.anonymous and author:
                add("E", os.path.basename(pdf), f"the PDF properties name an author (\"{author.group(1).strip()}\"): clear them, e.g. \\hypersetup{{pdfauthor={{}}}}")
    # ----- supplement
    if opts.supp:
        add("N", "supplement", "send it as the venue wants: usually one PDF with its own title page, and a description file where a deposit requires one")
    # ----- plain metadata
    print("submit_check: " + ", ".join([opts.main] + opts.supp))
    if opts.plain:
        print(f"\nTITLE ({len(title)} characters)\n  {title}")
        odd = sorted(set(re.findall(r"[^\x00-\x7f]", title + abstract)))
        print(f"\nABSTRACT ({len(abstract.split())} words, {len(abstract)} characters)\n  {abstract}")
        if odd:
            print("\n  characters outside ASCII: " + " ".join(odd) + " (check how the form shows them)")
        if re.search(r"[\\$^_]", title + abstract):
            print("  TeX is left in the plain text: write the formula out, or use the form's own notation")
        if names:
            print("\nAUTHORS\n  " + "; ".join(dict.fromkeys(names)))
    # ----- pack
    if opts.pack:
        dest = os.path.abspath(opts.pack)
        if os.path.exists(dest) and os.listdir(dest):
            sys.exit(f"submit_check: {opts.pack} exists and is not empty; choose a new folder")
        os.makedirs(dest, exist_ok=True)
        sent = []
        for u in sorted(used):
            if not u.startswith(folder + os.sep) or u.endswith(".aux"):
                continue
            rel = os.path.relpath(u, folder).replace(os.sep, "/")  # the same on every system
            os.makedirs(os.path.dirname(os.path.join(dest, rel)) or dest, exist_ok=True)
            if u.endswith((".tex", ".ltx")):
                with open(os.path.join(dest, rel), "w", encoding="utf-8") as handle:
                    handle.write(strip_comments(read_file(u)))
            else:
                shutil.copy2(u, os.path.join(dest, rel))
            digest = hashlib.sha256(open(os.path.join(dest, rel), "rb").read()).hexdigest()[:16]
            sent.append((rel, os.path.getsize(os.path.join(dest, rel)), digest))
        print(f"\nPACKED into {opts.pack}: {len(sent)} file(s)")
        for rel, size, digest in sent:
            print(f"  {rel:<40} {size:>9} bytes   sha256 {digest}")
        if opts.compile:
            if not shutil.which("pdflatex"):
                add("N", "pack", "pdflatex is not installed: the copy was not built")
            else:
                order = [opts.main] + opts.supp if not opts.supp else opts.supp + [opts.main] + opts.supp + [opts.main]
                ok = True
                for p in order + ([] if opts.supp else [opts.main]):
                    done = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", os.path.relpath(os.path.abspath(p), folder)],
                                          capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=dest, timeout=600)
                    ok = ok and done.returncode == 0
                log = os.path.join(dest, os.path.splitext(os.path.relpath(os.path.abspath(opts.main), folder))[0] + ".log")
                undefined = len(re.findall(r"undefined", read_file(log))) if os.path.isfile(log) else 0
                if not ok:
                    add("E", "pack", "the clean copy does not build: a file is missing from it, or the source has an error (see the .log in the folder)")
                elif undefined:
                    add("W", "pack", f"the clean copy builds, with {undefined} mention(s) of \"undefined\" in the log: citations need the bibliography run")
                else:
                    add("N", "pack", "the clean copy builds from its own files")
    for level, title_ in (("E", "ERRORS"), ("W", "WARNINGS"), ("N", "NOTES")):
        rows = [(w, m) for lv, w, m in found if lv == level]
        if rows:
            print(f"\n{title_} ({len(rows)})")
            for w, m in rows:
                print(f"  {w}: {m}")
    counts = [sum(1 for lv, _, _ in found if lv == x) for x in "EWN"]
    print(f"\n{counts[0]} error(s), {counts[1]} warning(s), {counts[2]} note(s)")
    sys.exit(1 if counts[0] else 0)


if __name__ == "__main__":
    main()
