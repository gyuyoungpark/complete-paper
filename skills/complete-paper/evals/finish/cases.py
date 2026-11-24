#!/usr/bin/env python3
"""Planted-fault cases for audit.py and submit_check.py.

Each case writes a small manuscript into a temporary folder, runs one script, and states which
findings must and must not appear.

    python3 evals/finish/cases.py            # every case
    python3 evals/finish/cases.py submit     # the cases whose name contains "submit"

Exit status is 1 if any case fails.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EX = ROOT / "examples"
CASES = []


def case(name, script, args, files, expect=(), absent=(), status=None, after=None):
    CASES.append(dict(name=name, script=script, args=args, files=files, expect=expect, absent=absent, status=status, after=after))


def edit(text, *pairs):
    for old, new in pairs:
        assert old in text, f"not in the text: {old[:50]!r}"
        text = text.replace(old, new)
    return text


EXAMPLE = {n: (EX / "supplement" / n).read_text(encoding="utf-8") for n in ("main.tex", "supplement.tex", "shared.tex")}
EXAMPLE["brief.md"] = (EX / "brief" / "brief.md").read_text(encoding="utf-8")
EXAMPLE["repro.md"] = (EX / "methods" / "repro.md").read_text(encoding="utf-8")

CLEAN = r"""\documentclass{article}
\usepackage{lineno}
\linenumbers
\title{Field-free switching of a tilted kagome antiferromagnet}
\author{Ada Author \and Bo Author}
\begin{document}
\maketitle
\begin{abstract}
Switching of noncollinear antiferromagnets (NCAFs) has required a magnetic field. Here we show by simulation that a tilt of the
kagome plane removes this requirement. The moment reverses within 0.22 ns at a tilt of 45 degrees.
\end{abstract}
\section{Introduction}
Noncollinear antiferromagnets (NCAFs) combine fast dynamics with a large readout signal~\cite{A}. Every experiment so far applies a
field along the current~\cite{B}. We ask whether a tilt of the crystal can replace that field in NCAFs, and NCAFs with tilt exist.
\section{Results}
Figure~\ref{fig:a} shows the geometry. The moment reverses for every tilted film (Fig.~\ref{fig:b}). The switching time falls from
0.60 ns at 15 degrees to 0.22 ns at a tilt of 45 degrees, and the final state follows the sign of the current.
\begin{figure}\caption{Geometry of the bilayer, with the tilt angle of the kagome plane.}\label{fig:a}\end{figure}
\begin{figure}\caption{Out-of-plane component of the moment against time for four tilt angles.}\label{fig:b}\end{figure}
\section{Conclusion}
A tilted crystal makes the reversal deterministic without a field. The result holds for a single domain at zero temperature. Films
grown on miscut substrates should therefore switch by current alone.
\section*{Data availability}
The data that support the findings of this article are openly available at Zenodo, doi:10.5281/zenodo.1234567.
\section*{Author contributions}
A.A.: Investigation, Software. B.A.: Conceptualization, Supervision.
\section*{Competing interests}
The authors declare no competing interests.
\begin{thebibliography}{9}
\bibitem{A} S. Nakatsuji, N. Kiyohara, and T. Higo, Nature \textbf{527}, 212 (2015).
\bibitem{B} H. Tsai \textit{et al.}, Nature \textbf{580}, 608 (2020).
\end{thebibliography}
\end{document}
"""
REQ = ["--require", "data", "competing", "contributions"]

# ---------------------------------------------------------------- audit
case("audit: the example manuscript", "audit.py", ["main.tex", "--supp", "supplement.tex", "--brief", "brief.md", "--repro", "repro.md"] + REQ, EXAMPLE,
     expect=["| equations | eq_refs.py | PASS", "| supplement | supp_check.py | PASS", "| duplication | overlap_check.py | PASS",
             "| brief | brief_check.py | PASS", "| methods | methods_check.py | FAIL | 6", "a placeholder image is left in the text",
             "no statement on competing was found", "no statement on contributions was found", "part checks that fail: methods"], status=1)
case("audit: a clean manuscript", "audit.py", ["main.tex"] + REQ, {"main.tex": CLEAN},
     expect=["Nothing blocks submission", "| abstract, words |", "| references | 2 |"], absent=["FAIL", "**Errors**"], status=0)
case("audit: a number only in the abstract", "audit.py", ["main.tex"], {"main.tex": edit(CLEAN, ("reverses within 0.22 ns at a tilt", "reverses within 0.35 ns at a tilt"))},
     expect=["Abstract: quotes 0.35, which the rest of the text does not contain"], status=0)
case("audit: limits", "audit.py", ["main.tex", "--abstract-chars", "100", "--display-max", "1", "--title-chars", "20", "--refs-max", "1", "--words", "50", "--abstract-words", "10"],
     {"main.tex": CLEAN},
     expect=["abstract, characters:", "over the limit of 100", "figures and tables: 2, over the limit of 1", "title, characters: 55, over the limit of 20",
             "references: 2, over the limit of 1", "running text, words:", "abstract, words:"], status=1)
case("audit: placeholders and editing marks", "audit.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("We ask whether", "TODO check this. As shown in Fig.~?? and in [CITE Smith], \\textcolor{red}{we ask} whether"))},
     expect=["(an unresolved reference) is left in the text"], status=1)
case("audit: initials that match no author", "audit.py", ["main.tex"], {"main.tex": edit(CLEAN, ("B.A.: Conceptualization", "C.D.: Conceptualization"))},
     expect=["initials that match no author: C.D.", "authors without a role in the contribution statement: B.A."], status=0)
case("audit: required statements missing", "audit.py", ["main.tex", "--require", "data", "ai", "ethics"],
     {"main.tex": edit(CLEAN, ("\\section*{Data availability}\nThe data that support the findings of this article are openly available at Zenodo, doi:10.5281/zenodo.1234567.\n", ""))},
     expect=["no statement on data was found", "no statement on ai was found", "no statement on ethics was found"], status=1)
case("audit: data on request only", "audit.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("are openly available at Zenodo, doi:10.5281/zenodo.1234567.", "are available from the authors upon reasonable request."))},
     expect=["the data are offered on request only"], status=0)
case("audit: an abbreviation defined only in the abstract", "audit.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("Noncollinear antiferromagnets (NCAFs) combine", "Such NCAFs combine"))}, expect=["NCAF is defined in the abstract and used in the text"])
case("audit: the conclusion repeats the abstract", "audit.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("A tilted crystal makes the reversal deterministic without a field.", "We show by simulation that a tilt of the kagome plane removes this requirement."))},
     expect=["| duplication | overlap_check.py | REVIEW", "REPEATS"], absent=["part checks that fail"], status=0)
case("audit: an undefined reference in the log", "audit.py", ["main.tex"],
     {"main.tex": CLEAN, "main.log": "LaTeX Warning: Reference `fig:c' on page 1 undefined on input line 12.\nLaTeX Warning: Citation `Z' on page 2 undefined on input line 30.\nOverfull \\hbox (3pt too wide)\n"},
     expect=["undefined reference: fig:c", "undefined citation: Z", "1 overfull line(s)"], status=1)
case("audit: an uncited figure fails the citation check", "audit.py", ["main.tex"], {"main.tex": edit(CLEAN, (" (Fig.~\\ref{fig:b})", ""))},
     expect=["| citations | cite_order.py | FAIL | 1"], status=1)
case("audit: a long sentence in the abstract", "audit.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("Here we show by simulation that a tilt of the\nkagome plane removes this requirement.",
                               "Here we show by simulation that a tilt of the\nkagome plane, of the kind that films grown on miscut substrates already have and that "
                               "earlier work has treated as a defect to be removed by better growth, removes this requirement for every film."))},
     expect=["Abstract: 1 sentence(s) over 30 words"], status=0)
case("audit: the bibliography file is found without --bib", "audit.py", ["main.tex"],
     {"main.tex": CLEAN.split("\\begin{thebibliography}")[0] + "\\bibliography{refs}\n\\end{document}\n",
      "refs.bib": "@article{A, author={Nakatsuji, S.}, title={Large anomalous Hall effect}, journal={Nature}, volume={527}, pages={212}, year={2015}, doi={10.1038/nature15723}}\n"
                  "@article{B, author={Tsai, H.}, title={Electrical manipulation}, journal={Nature}, volume={580}, pages={608}, year={2020}, doi={10.1038/s41586-020-2211-2}}\n"},
     expect=["| references | ref_check.py | PASS"], status=0)
case("audit: the report is written", "audit.py", ["main.tex", "--report", "audit.md"], {"main.tex": CLEAN}, expect=["wrote audit.md"], status=0,
     after=lambda folder: "## Still to be read by a person" in (Path(folder) / "audit.md").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- submit_check
BARE = {"main.tex": CLEAN}
case("submit: a clean folder", "submit_check.py", ["main.tex", "--line-numbers"], BARE, absent=["ERRORS", "WARNINGS"], status=0)
case("submit: no line numbers", "submit_check.py", ["main.tex", "--line-numbers"], {"main.tex": edit(CLEAN, ("\\usepackage{lineno}\n\\linenumbers\n", ""))},
     expect=["no line numbers"], status=1)
case("submit: missing and misnamed files", "submit_check.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("\\begin{figure}\\caption{Geometry", "\\begin{figure}\\includegraphics{figs/Device}\\includegraphics{nothing}\\includegraphics{/home/user/a.pdf}"
                               "\\includegraphics{../b.pdf}\\input{sec two}\\caption{Geometry")), "figs/device.pdf": "x"},
     expect=["figure \"nothing\": missing", "figure \"/home/user/a.pdf\": an absolute path", "figure \"../b.pdf\": a path that leaves the folder",
             "a name that differs from the file only in upper and lower case", "a space in the name"], status=1)
case("submit: leftovers", "submit_check.py", ["main.tex"],
     {"main.tex": edit(CLEAN, ("\\section{Results}", "% ask Bo about this\n\\iffalse old text \\fi\n\\section{Results} % TODO shorten"), ("\\end{document}\n", "\\end{document}\nold notes here\n")),
      "old_fig.pdf": "x", "main.aux": "x"},
     expect=["3 words after \\end{document}", "\\iffalse or a comment environment", "a to-do mark", "line(s) carry comments", "1 file(s) that the sources do not use: old_fig.pdf"],
     absent=["main.aux"], status=1)
case("submit: an anonymized copy that is not", "submit_check.py", ["main.tex", "--anonymous", "--authors", "Ada Author", "Bo Lovelace"],
     {"main.tex": edit(CLEAN, ("We ask whether", "As we showed in our previous work, and as Lovelace found, the code is at github.com/lab/x. We ask whether"),
                       ("\\section*{Data availability}", "\\section*{Acknowledgments}\nThis work was supported by Grant No. 1.\n\\section*{Data availability}"))},
     expect=["the author block is filled in", "acknowledgments in the review copy", "a funding statement in the review copy", "identifies the authors",
             "the name \"Lovelace\" appears in the text", "a link to a code repository"], status=1)
case("submit: an anonymized copy", "submit_check.py", ["main.tex", "--anonymous", "--authors", "Ada Author"],
     {"main.tex": edit(CLEAN, ("\\author{Ada Author \\and Bo Author}", "\\author{}"))}, absent=["ERRORS", "identifies the authors"], status=0)
case("submit: arXiv rules", "submit_check.py", ["main.tex", "--arxiv"],
     {"main.tex": edit(CLEAN, ("Switching of noncollinear", "Background sentence that is far too long for a preprint server. " * 32 + "Switching of noncollinear"),
                       ("\\begin{figure}\\caption{Geometry", "\\begin{figure}\\includegraphics{a}\\includegraphics{b}\\caption{Geometry"),
                       ("\\begin{document}", "\\externaldocument[S-]{supplement}\n\\begin{document} % note to self")), "a.eps": "x", "b.pdf": "x"},
     expect=["arXiv takes at most 1920", "PostScript and PDF or bitmap figures are mixed", "cross-file references with xr", "arXiv publishes the sources"], status=1)
case("submit: plain metadata", "submit_check.py", ["main.tex", "--plain"],
     {"main.tex": edit(CLEAN, ("\\title{Field-free switching of a tilted kagome antiferromagnet}", "\\title{Field-free switching of Mn$_3$Sn at $\\theta = 45^\\circ$}"))},
     expect=["TITLE (", "ABSTRACT (", "AUTHORS\n  Ada Author; Bo Author", "TeX is left in the plain text"], status=0)
case("submit: the packed copy", "submit_check.py", ["main.tex", "--pack", "out"],
     {"main.tex": edit(CLEAN, ("\\section{Results}", "% a private remark\n\\section{Results} % another"),
                       ("\\begin{figure}\\caption{Geometry", "\\begin{figure}\\includegraphics{figs/device}\\caption{Geometry")),
      "figs/device.pdf": "x", "unused.png": "x"},
     expect=["PACKED into out: 2 file(s)", "main.tex", "figs/device.pdf", "sha256"], status=0,
     after=lambda folder: "private remark" not in (Path(folder) / "out" / "main.tex").read_text(encoding="utf-8")
     and "another" not in (Path(folder) / "out" / "main.tex").read_text(encoding="utf-8")
     and (Path(folder) / "out" / "figs" / "device.pdf").exists() and not (Path(folder) / "out" / "unused.png").exists())
case("submit: the example with its supplement", "submit_check.py", ["main.tex", "--supp", "supplement.tex", "--arxiv"], EXAMPLE,
     expect=["cross-file references with xr", "line(s) carry comments"], absent=["ERRORS"], status=0)


def run(c):
    with tempfile.TemporaryDirectory() as folder:
        for name, text in c["files"].items():
            path = Path(folder) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        done = subprocess.run([sys.executable, str(SCRIPTS / c["script"])] + list(c["args"]), capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=folder,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        extra = True if c["after"] is None else bool(c["after"](folder))
        return done.returncode, done.stdout + done.stderr, extra


def main():
    wanted, failed, total = sys.argv[1:], 0, 0
    for c in CASES:
        if wanted and not any(w in c["name"] for w in wanted):
            continue
        total += 1
        code, text, extra = run(c)
        missing = [e for e in c["expect"] if e not in text]
        present = [a for a in c["absent"] if a in text]
        wrong = c["status"] is not None and code != c["status"]
        if missing or present or wrong or not extra:
            failed += 1
            print(f"FAIL  {c['name']}")
            for e in missing:
                print(f"        expected, not found: {e}")
            for a in present:
                print(f"        found, not expected: {a}")
            if wrong:
                print(f"        exit status {code}, expected {c['status']}")
            if not extra:
                print("        the files written by the script are not as expected")
            print("\n".join("        | " + line[:210] for line in text.splitlines()[-16:]))
        else:
            print(f"ok    {c['name']}")
    print(f"\n{total - failed} of {total} cases pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
