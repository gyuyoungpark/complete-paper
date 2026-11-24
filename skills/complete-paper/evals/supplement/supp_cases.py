#!/usr/bin/env python3
"""Planted-fault cases for scripts/supp_check.py.

Each case copies the example manuscript of examples/supplement/, plants one fault (or none), runs
the checker and states which findings must and must not appear.

    python3 evals/supplement/supp_cases.py           # every case
    python3 evals/supplement/supp_cases.py callout   # the cases whose name contains "callout"

Exit status is 1 if any case fails.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = str(ROOT / "scripts" / "supp_check.py")
EXAMPLE = ROOT / "examples" / "supplement"
CASES = []


def case(name, expect=(), absent=(), main=(), supp=(), args=(), status=None, files=None, one_file=False, no_supp=False, inputs=False):
    CASES.append(dict(name=name, expect=expect, absent=absent, main=main, supp=supp, args=args, status=status,
                      files=files or {}, one_file=one_file, no_supp=no_supp, inputs=inputs))


def edit(text, pairs, which):
    for old, new in pairs:
        if old not in text:
            raise AssertionError(f"the text to replace is not in {which}: {old[:60]!r}")
        text = text.replace(old, new)
    return text


FIGURE = """
\\begin{figure}
  \\centering
  \\includegraphics[width=0.4\\textwidth]{example-image-c}
  \\caption{%s}
  \\label{%s}
\\end{figure}
"""
S1_CALL = "(derivation in\nSec.~\\ref{S-sec:derivation} of the Supplemental Material~\\cite{sm})"
S2_CALL = "are varied over the ranges given in Sec.~\\ref{S-sec:robust}."
S3_CALL = "(Fig.~\\ref{S-fig:thermal})"
END_SUPP = "\n\\end{document}"
RESULTS_END = "The zero-temperature threshold of Eq.~(\\ref{eq:threshold}) therefore remains\nthe design value."
DAS = ("The input files, the raw output of all 212 simulation runs and the scripts that produce every figure of\n"
       "the paper and of its Supplemental Material are deposited at Zenodo, doi:10.5281/zenodo.0000000\n(placeholder).")

# ----- the example itself
case("the example is clean", absent=["ERRORS", "WARNINGS", "NOTES"])
case("the example in one file", one_file=True, expect=["3 sections, 1 table, 2 figures", "Sec. S1"], absent=["ERRORS", "WARNINGS"])
case("main text without a supplement", no_supp=True, expect=["no supplement was given or found"], status=0)
case("a file that does not exist", args=["--supp", "nowhere.tex"], no_supp=True, expect=["no such file"], status=1)

# ----- callouts
case("callout in the abstract", main=[("antiferromagnetic memory.\n\\end{abstract}", "antiferromagnetic memory (see Supplemental Material).\n\\end{abstract}")],
     expect=["the abstract sends the reader to the supplement"], status=1)
case("callout in the conclusion", main=[("keep this price within a factor of two.", "keep this price within a factor of two (Fig.~\\ref{S-fig:thermal}).")],
     expect=["the conclusion sends the reader to the supplement (Fig. S2)"])
case("callout that says nothing", main=[(RESULTS_END, RESULTS_END + " See Supplemental Material for more details.")],
     expect=["a callout that says neither what is there nor where"])
case("callout that names no place", main=[(S2_CALL, "are varied (see the Supplemental Material~\\cite{sm}).")],
     expect=["names no place in the supplement"])
case("three callouts in one paragraph",
     main=[(S3_CALL, "(Fig.~\\ref{S-fig:thermal}). The seeds are listed in Table~\\ref{S-tab:ranges}. The convergence is shown in Fig.~\\ref{S-fig:robust}")],
     expect=["3 callouts to the supplement in one paragraph"])
case("callouts far beyond the sections",
     main=[("which is the property a memory needs.", "which is the property a memory needs (Fig.~\\ref{S-fig:robust}).\n\nThe mesh is fine enough for this "
            "purpose (Table~\\ref{S-tab:ranges}), as is discussed further below in the text of this section.\n\nThe damping matters little for "
            "the time scale as well (Sec.~\\ref{S-sec:robust}), which we checked for every tilt angle.\n\nThe temperature does not change the picture "
            "either (Sec.~\\ref{S-sec:thermal}), as the last part of this section shows in detail."),
           ("Tilt is therefore a design parameter", "The derivation is in Sec.~S1. Tilt is therefore a design parameter")],
     expect=["8 sentences send the reader to the supplement", "the budget is 3: one per supplementary section (3)"], status=1)
case("an item cited again and again",
     main=[("which is the property a memory needs.", "which is the property a memory needs (Fig.~\\ref{S-fig:thermal}).\n\nThe same holds at "
            "other tilt angles and other pulse lengths within the range that we examined (Fig.~\\ref{S-fig:thermal}).")],
     expect=["Fig. S2 is cited 3 times"])
case("a range counts as one callout", main=[(S3_CALL, "(Figs.~S1--S2)")], expect=["Fig. S1, Fig. S2"], absent=["WARNINGS", "ERRORS"])
case("callouts typed in words", main=[(S3_CALL, "(Supplementary Fig.~2)"), (S2_CALL, "are varied (Supplementary Note 2).")],
     expect=["Fig. S2", "Sec. S2"], absent=["only as a whole", "ERRORS"])
case("a home-made reference macro", main=[(S3_CALL, "(\\figref{S-fig:thermal})")], expect=["Fig. S2"], absent=["ERRORS", "WARNINGS"])
case("Extended Data is not counted", main=[(RESULTS_END, RESULTS_END + " The pulse shape is given in Extended Data Fig.~3.")],
     expect=["Extended Data, not counted: 1"], absent=["ERRORS"])
case("an abbreviation for the supplement",
     main=[(S1_CALL, "(derivation in\nSec.~\\ref{S-sec:derivation} of the Supplemental Material (SM)~\\cite{sm})"),
           (S2_CALL, "are varied over wide ranges (see SM).")],
     expect=["names no place in the supplement: \"The threshold moves"])
case("a cited item that does not exist", main=[(S3_CALL, "(Fig.~S7)")], expect=["Fig. S7 is cited, but the supplement has 2 figures"], status=1)
case("the supplement is never mentioned",
     main=[(S1_CALL, "(derivation not shown)"), (S2_CALL, "are varied."), (S3_CALL, ""), ("and of its Supplemental Material ", ""),
           ("\\bibitem{sm} See Supplemental Material at [URL will be inserted by publisher] for the derivation of\n"
            "  Eq.~(\\ref{eq:threshold}), the robustness of the threshold against numerical and material parameters,\n"
            "  and the effect of temperature.\n", "")],
     expect=["the main text never mentions the supplement"], status=1)
case("the supplement is cited only as a whole",
     main=[(S1_CALL, "(derivation in the Supplemental Material~\\cite{sm})"), (S2_CALL, "are varied~\\cite{sm}."), (S3_CALL, "\\cite{sm}")],
     expect=["cites the supplement only as a whole"], absent=["cannot be reached"])
case("callouts in a file that is \\input", main=[("\\section{Results}\n", "\\section{Results}\n\\input{extra}\n")],
     files={"extra.tex": "The octupole follows the torque within the first ten picoseconds of the pulse (Sec.~S3).\n"},
     expect=["extra.tex:1"])

case("a callout in a caption counts",
     main=[("Eq.~(\\ref{eq:threshold}) with the parameters of the simulation.}",
            "Eq.~(\\ref{eq:threshold}) with the parameters of the simulation. The convergence is shown in Fig.~\\ref{S-fig:robust}.}")],
     expect=["CALLOUTS  4 sentence(s)", "caption", "4 sentences send the reader to the supplement"])

# ----- reach and order
case("a figure cited nowhere", supp=[(END_SUPP, FIGURE % ("Magnetization of a second sample.", "fig:orphan") + END_SUPP)],
     expect=["Fig. S3 is cited nowhere"], status=1)
case("a section the main text cannot reach",
     supp=[(END_SUPP, "\n\\section{Further checks}\n\\label{sec:extra}\n\nThe main text of the paper does not use this section. "
            "Figure~\\ref{fig:extra} shows a further check of the pulse shape.\n" + FIGURE % ("Threshold against pulse length.", "fig:extra") + END_SUPP),
           ("Sec.~\\ref{sec:thermal}, effect of\ntemperature.", "Sec.~\\ref{sec:thermal}, effect of\ntemperature. Sec.~\\ref{sec:extra}, further checks.")],
     expect=["Sec. S4 (\"Further checks\") cannot be reached from the main text", "contents"], absent=["cited nowhere"])
case("the supplement cites a figure it does not have", supp=[("Figure~\\ref{fig:thermal} shows", "Figure~S9 shows")],
     expect=["the supplement cites Fig. S9, which it does not contain"], status=1)
case("sections out of the order of citation",
     main=[(S1_CALL, "(derivation in\nSec.~\\ref{S-sec:robust} of the Supplemental Material~\\cite{sm})"),
           (S2_CALL, "are varied over the ranges given in Sec.~\\ref{S-sec:derivation}.")],
     expect=["not in the order in which the main text first points to them: S2, S1, S3"])

# ----- size and data
MORE = "".join(FIGURE % (f"Check number {k} of the pulse shape against the reference.", f"fig:more{k}") for k in range(3))
case("more display items than the main text",
     supp=[(END_SUPP, "\nFigures~\\ref{fig:more0}, \\ref{fig:more1} and \\ref{fig:more2} show further checks.\n" + MORE + END_SUPP)],
     expect=["the supplement has 6 figures and tables against 3 in the main text"])
case("more words than the main text",
     supp=[(END_SUPP, "\n" + ("The run was repeated with a different seed and gave the same threshold within the stated error. " * 60 + "\n\n") * 2 + END_SUPP)],
     expect=["words against 613 in the main text"])
case("a ratio set by the venue", args=["--ratio", "2"],
     supp=[(END_SUPP, "\nFigures~\\ref{fig:more0}, \\ref{fig:more1} and \\ref{fig:more2} show further checks.\n" + MORE + END_SUPP)],
     absent=["figures and tables against"])
ROWS = "".join(f"    run {k} & {k * 0.01:.2f} & {1 + k * 0.001:.3f} \\\\\n" for k in range(40))
case("a table that is data",
     supp=[(END_SUPP, "\nTable~\\ref{tab:all} lists every run.\n\\begin{table}\n\\caption{Threshold of every run.}\\label{tab:all}\n"
            "\\begin{tabular}{lcc}\n" + ROWS + "\\end{tabular}\n\\end{table}\n" + END_SUPP)],
     expect=["Table S2 is a table of about 40 rows"])
case("a gallery of images",
     supp=[(END_SUPP, "\nFigure~\\ref{fig:gallery} shows snapshots.\n\\begin{figure}\n" + "\\includegraphics[width=2cm]{example-image-a}\n" * 12
            + "\\caption{Snapshots of the moment during reversal.}\\label{fig:gallery}\n\\end{figure}\n" + END_SUPP)],
     expect=["Fig. S3 holds 12 images"])
SWEEP = "".join(FIGURE % (f"Out-of-plane component against time for a tilt angle of {a} degrees and the reference damping.", f"fig:sweep{a}")
                for a in (10, 20, 30, 40))
case("a run of near-identical figures",
     supp=[(END_SUPP, "\nFigures~\\ref{fig:sweep10}, \\ref{fig:sweep20}, \\ref{fig:sweep30} and \\ref{fig:sweep40} show all angles.\n" + SWEEP + END_SUPP)],
     expect=["have nearly the same caption"])
case("a listing of an input file",
     supp=[(END_SUPP, "\n\\begin{verbatim}\n" + "".join(f"parameter_{k} = {k}\n" for k in range(30)) + "\\end{verbatim}\n" + END_SUPP)],
     expect=["a listing of 3"])
case("a figure described as raw data",
     supp=[("Switching probability at $300\\un{K}$ and $\\theta = 30^\\circ$ against current density",
            "Raw traces of all runs at $300\\un{K}$ and $\\theta = 30^\\circ$ against current density")],
     expect=["a candidate for the data package"])

# ----- style
case("a macro defined twice, differently", supp=[("\\externaldocument[M-]{main}", "\\externaldocument[M-]{main}\n\\renewcommand{\\jc}{J_{\\mathrm{th}}}")],
     expect=["macro(s) are defined differently", "\\jc"])
case("Figure against Fig.",
     supp=[("the threshold of Fig.~\\ref{M-fig:threshold}", "the threshold of Figure~\\ref{M-fig:threshold}"),
           ("are drawn in\nFig.~\\ref{fig:robust}", "are drawn in\nFigure~\\ref{fig:robust}"),
           ("and the largest change of the threshold at $\\theta = 30^\\circ$. Figure~\\ref{fig:robust}(a) shows",
            "and the largest change of the threshold at $\\theta = 30^\\circ$, see Figure~\\ref{fig:robust}(a), which shows")],
     expect=["the main text writes \"Fig.\" in mid-sentence and the supplement \"Figure\""])
case("no S prefix", supp=[("\\renewcommand{\\thefigure}{S\\arabic{figure}}\n\\renewcommand{\\thetable}{S\\arabic{table}}\n", "")],
     expect=["are not numbered with a prefix"])
case("equations without S prefix", supp=[("\\renewcommand{\\theequation}{S\\arabic{equation}}\n", "")],
     expect=["equations are not numbered with a prefix"])
case("a float without caption",
     supp=[("  \\caption{Switching probability at $300\\un{K}$ and $\\theta = 30^\\circ$ against current density in units\n"
            "  of the zero-temperature threshold $\\jc$. Each point is the mean of 64 runs, and the line is an error\n  function fitted to the points.}\n", "")],
     expect=["Fig. S2 has no caption"])
case("a section that does not name what it supports",
     supp=[("The main text states that thermal fluctuations at $300\\un{K}$ broaden the transition and do not shift it.\n", "")],
     expect=["Sec. S3 (\"Effect of temperature\") does not say in its first paragraph"])
case("a supplement that does not name the paper",
     supp=[("\\title{Supplemental Material for:\\\\ Field-free switching of a tilted kagome antiferromagnet}", "\\title{Supplemental Material}")],
     expect=["does not carry the paper's title"])
case("a work cited only in the supplement", supp=[("is the projection", "is the projection~\\cite{Z}")],
     expect=["1 work(s) are cited only in the supplement (Z)"])
case("six sections and no table of contents",
     supp=[(END_SUPP, "".join(f"\n\\section{{Further point {k}}}\n\nThis section supports Fig.~{k} of the main text with one more remark "
                              f"about the model.\n" for k in (1, 2, 3)) + END_SUPP)],
     expect=["without a table of contents"])

# ----- data availability
case("no data availability statement", main=[("\\paragraph{Data availability.}\n" + DAS, "")], expect=["no data availability statement was found"])
case("data on request only", main=[(DAS, "The data that support the findings of this study are available from the authors upon reasonable request.")],
     expect=["the data are offered on request only"])

# ----- layouts met in real manuscripts
case("the main file inputs the supplement", inputs=True, expect=["supp_check: main.tex, shared.tex + si.tex", "words                  613",
                                                               "3 sections, 1 table, 2 figures"], absent=["ERRORS", "WARNINGS"])
case("a cover page does not cite",
     supp=[("\\noindent Contents:", "\\subsection*{This PDF file includes:}\nFigs.~S1 to S3\\\\ Table~S1\n\n\\noindent Contents:"),
           (END_SUPP, FIGURE % ("Magnetization of a second sample.", "fig:orphan") + END_SUPP)],
     expect=["Fig. S3 is cited nowhere", "3 sections, 1 table, 3 figures"], status=1)
case("a list of figures before the first section does not cite",
     supp=[("\\noindent Contents:", "\\noindent Figures: Fig.~\\ref{fig:robust}, convergence; Fig.~\\ref{fig:thermal}, temperature; "
            "Fig.~\\ref{fig:orphan}, a second sample.\n\n\\noindent Contents:"),
           (END_SUPP, FIGURE % ("Magnetization of a second sample.", "fig:orphan") + END_SUPP)],
     expect=["Fig. S3 is cited nowhere"], status=1)
case("a list of supplementary materials in the main text", one_file=True,
     main=[("\\begin{thebibliography}", "\\section*{Supplementary materials}\nMaterials and Methods\\\\ Figs.~S1 to S2\\\\ Table~S1\n\n\\begin{thebibliography}")],
     expect=["3 sections, 1 table, 2 figures"], absent=["ERRORS", "WARNINGS"])
case("a pointer heading is not a supplement", no_supp=True,
     main=[("\\begin{thebibliography}", "\\section*{Supplementary information}\nSupplementary information is available for this paper.\n\n\\begin{thebibliography}")],
     expect=["no supplement was given or found"], absent=["ERRORS"], status=0)
case("several paragraphs with two callouts",
     main=[(S3_CALL, "(Fig.~\\ref{S-fig:thermal}). The seeds are listed in Table~\\ref{S-tab:ranges}"),
           (S2_CALL, "are varied over the ranges given in Sec.~\\ref{S-sec:robust}. The convergence is drawn in Fig.~\\ref{S-fig:robust}.")],
     expect=["2 paragraphs hold more than 1 callout to the supplement"])
case("a supplement without sections",
     supp=[("\\section{Derivation of the threshold current}\n", ""), ("\\section{Robustness of the threshold}\n", ""), ("\\section{Effect of temperature}\n", "")],
     main=[("which is the property a memory needs.", "which is the property a memory needs (Fig.~\\ref{S-fig:robust}).\n\nThe mesh is fine enough for this "
            "purpose (Table~\\ref{S-tab:ranges}), as is discussed further below in the text of this section.\n\nThe damping matters little for "
            "the time scale as well (Fig.~S1), which we checked for every tilt angle that is shown here.")],
     expect=["the supplement has no sections, so every item needs a callout of its own: group its 3 figures and tables"])

# ----- the ledger
case("the ledger is written", args=["--ledger", "suppmap.md"], expect=["wrote suppmap.md"])


def run(c):
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        main = edit((EXAMPLE / "main.tex").read_text(encoding="utf-8"), c["main"], "main.tex")
        supp = edit((EXAMPLE / "supplement.tex").read_text(encoding="utf-8"), c["supp"], "supplement.tex")
        shutil.copy(EXAMPLE / "shared.tex", folder / "shared.tex")
        for name, text in c["files"].items():
            (folder / name).write_text(text, encoding="utf-8")
        if c["one_file"] or c["inputs"]:
            body = supp.split("\\maketitle", 1)[1].replace("\\end{document}", "")
            body = body.replace("M-eq:threshold", "eq:threshold").replace("M-fig:threshold", "fig:threshold")
            body = ("\\clearpage\n\\section*{Supplemental Material}\n"
                    "\\renewcommand{\\thefigure}{S\\arabic{figure}}\\renewcommand{\\thetable}{S\\arabic{table}}"
                    "\\renewcommand{\\theequation}{S\\arabic{equation}}\n" + body.replace("\\section{", "\\subsection{"))
            main = main.replace("S-sec:", "sec:").replace("S-fig:", "fig:").replace("S-tab:", "tab:")
            if c["inputs"]:
                (folder / "si.tex").write_text(body, encoding="utf-8")
                (folder / "main.tex").write_text(main.replace("\\end{document}", "\\input{si}\n\\end{document}"), encoding="utf-8")
                command = [sys.executable, CHECK, "main.tex", "--supp", "si.tex"]
            else:
                (folder / "paper.tex").write_text(main.replace("\\end{document}", body + "\\end{document}"), encoding="utf-8")
                command = [sys.executable, CHECK, "paper.tex"]
        else:
            (folder / "main.tex").write_text(main, encoding="utf-8")
            (folder / "supplement.tex").write_text(supp, encoding="utf-8")
            command = [sys.executable, CHECK, "main.tex"] + ([] if c["no_supp"] else ["--supp", "supplement.tex"])
        done = subprocess.run(command + list(c["args"]), capture_output=True, text=True, encoding="utf-8", cwd=folder)
        text = done.stdout + done.stderr
        if c["name"] == "the ledger is written":
            ledger = (folder / "suppmap.md").read_text(encoding="utf-8") if (folder / "suppmap.md").exists() else ""
            again = subprocess.run(command + list(c["args"]), capture_output=True, text=True, encoding="utf-8", cwd=folder).stdout
            text += "\nLEDGER-OK" if ("## Items" in ledger and "| Sec. S1 |" in ledger and "was left alone" in again) else "\nLEDGER-BAD"
        return done.returncode, text


def main():
    wanted, failed, total = sys.argv[1:], 0, 0
    for c in CASES:
        if wanted and not any(w in c["name"] for w in wanted):
            continue
        total += 1
        try:
            code, text = run(c)
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {c['name']}\n        {exc}")
            continue
        expect = list(c["expect"]) + (["LEDGER-OK"] if c["name"] == "the ledger is written" else [])
        missing = [e for e in expect if e not in text]
        present = [a for a in c["absent"] if a in text]
        wrong = c["status"] is not None and code != c["status"]
        if missing or present or wrong:
            failed += 1
            print(f"FAIL  {c['name']}")
            for e in missing:
                print(f"        expected, not found: {e}")
            for a in present:
                print(f"        found, not expected: {a}")
            if wrong:
                print(f"        exit status {code}, expected {c['status']}")
            print("\n".join("        | " + line for line in text.splitlines()[-22:]))
        else:
            print(f"ok    {c['name']}")
    print(f"\n{total - failed} of {total} cases pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
