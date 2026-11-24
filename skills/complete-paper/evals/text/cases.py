#!/usr/bin/env python3
"""Planted-fault cases for the text checkers: brief_check, methods_check, cite_order, table_check, prose_lint.

Each case writes small files into a temporary folder, runs one script, and states which findings
must and must not appear.

    python3 evals/text/cases.py            # every case
    python3 evals/text/cases.py brief      # the cases whose name contains "brief"

Exit status is 1 if any case fails.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EX = ROOT / "examples"
CASES = []


def case(name, script, args, files=None, expect=(), absent=(), status=None):
    CASES.append(dict(name=name, script=script, args=args, files=files or {}, expect=expect, absent=absent, status=status))


def edit(text, *pairs):
    for old, new in pairs:
        assert old in text, f"not in the text: {old[:50]!r}"
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------- brief_check
BRIEF = (EX / "brief" / "brief.md").read_text(encoding="utf-8")
case("brief: the example is clean", "brief_check.py", ["brief.md"], {"brief.md": BRIEF}, absent=["ERRORS", "WARNINGS"], status=0)
case("brief: a missing claim field", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("SYSTEM: Mn3Sn (20 nm)/W bilayer, single domain, tilt angles from 5 to 45 degrees.", "SYSTEM: <material>"))},
     expect=["SYSTEM is missing or not filled in"], status=1)
case("brief: two sentences and praise in RESULT", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("RESULT: Tilting the kagome plane", "RESULT: We report a novel effect. Tilting the kagome plane"))},
     expect=["RESULT has 2 sentences", "words of praise (novel)"], status=1)
case("brief: a long RESULT with and", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("the tilt angle.\nSYSTEM", "the tilt angle and we also find that the switching time falls with tilt and that the result survives at room temperature for every film that we examined in this work.\nSYSTEM"))},
     expect=["words (the limit is 30)", "contains \"and\""], status=0)
case("brief: an evidence kind outside the list", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("EVIDENCE: simulation;", "EVIDENCE: numerical proof;"))}, expect=["the kind must be one of"], status=1)
case("brief: NOT SHOWN with one entry", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("- No experiment is reported.\n- The threshold was not tested below a tilt of 5 degrees.\n- Temperature enters only as a check at 300 K (supplement), not in the main results.\n", ""))},
     expect=["NOT SHOWN has one entry"])
case("brief: one quantity, two values", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("| 2 | switching time | t_sw | 0.22 | ns | 0.01 | tilt 45 deg, 6e11 A/m^2 |", "| 2 | switching time | t_sw | 0.25 | ns | 0.01 | tilt 15 deg, 6e11 A/m^2 |"))},
     expect=["\"switching time\" has two values under the same condition: 0.60 and 0.25"], status=1)
case("brief: a key number without unit and source", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("| 0.22 | ns | 0.01 | tilt 45 deg, 6e11 A/m^2 | fig2/make_fig2.py |", "| 0.22 | | 0.01 | tilt 45 deg, 6e11 A/m^2 | |"))},
     expect=["has no unit", "has no source"])
case("brief: a number in RESULT that is not in the table", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("reverse the octupole moment,", "reverse the octupole moment within 0.3 ns,"))}, expect=["RESULT quotes 0.3"])
case("brief: an evidence row that is not ready", "brief_check.py", ["brief.md"],
     {"brief.md": edit(BRIEF, ("Fig. 3; Eq. (1); derivation in Sec. S1 | ready |", "Fig. 3; Eq. (1); derivation in Sec. S1 | partial: three angles missing |"))},
     expect=["hole: evidence row 3"])
case("brief: minimal mode asks for less", "brief_check.py", ["brief.md", "--minimal"],
     {"brief.md": BRIEF.split("## Question")[0] + "## Evidence\n" + BRIEF.split("## Evidence\n")[1].split("## Inventory")[0]},
     absent=["ERRORS", "WARNINGS"], status=0)
case("brief: a key number that the manuscript does not quote", "brief_check.py", ["brief.md", "--tex", "main.tex"],
     {"brief.md": BRIEF, "main.tex": "The switching time falls from 0.60 ns to 0.25 ns. The two agree within 4 percent, 5 percent and 8 percent."},
     expect=["switching time = 0.22 does not occur in the manuscript"])

# ---------------------------------------------------------------- methods_check
MAIN = (EX / "supplement" / "main.tex").read_text(encoding="utf-8")
SUPP = (EX / "supplement" / "supplement.tex").read_text(encoding="utf-8")
SHARED = (EX / "supplement" / "shared.tex").read_text(encoding="utf-8")
REPRO = (EX / "methods" / "repro.md").read_text(encoding="utf-8")
PAPER = {"main.tex": MAIN, "supplement.tex": SUPP, "shared.tex": SHARED}
case("methods: the template has every list", "methods_check.py", ["--template", "simulation", "experiment", "theory", "algorithm"],
     expect=["| G1 |", "| S11 |", "| X10 |", "| T4 |", "| A6 |", "Kind: simulation, experiment, theory, algorithm"], status=0)
case("methods: the example checklist shows six gaps", "methods_check.py", ["main.tex", "supplement.tex", "--repro", "repro.md"],
     dict(PAPER, **{"repro.md": REPRO}), expect=["ERRORS (6)", "S11", "G9"], absent=["is not in the manuscript"], status=1)
case("methods: a heading and a label that do not exist", "methods_check.py", ["main.tex", "supplement.tex", "--repro", "repro.md"],
     dict(PAPER, **{"repro.md": edit(REPRO, ("| \"Model\", Fig. 1 |", "| \"Sample growth\", `fig:nothing` |"))}),
     expect=["the heading \"Sample growth\" is not in the manuscript", "the label `fig:nothing` is not in the manuscript"], status=1)
case("methods: n/a without a reason, and a removed row", "methods_check.py", ["main.tex", "--repro", "repro.md"],
     dict(PAPER, **{"repro.md": edit(REPRO, ("| n/a | no run was excluded |", "| n/a | |"), ("| T4 | Limits in which the result reduces to a known one | \"Model\" | threshold diverges at zero tilt |\n", ""))}),
     expect=["G5", "n/a without a reason", "items of the theory list are not in the checklist: T4"])
case("methods: words in place of values", "methods_check.py", ["m.tex"],
     {"m.tex": "\\section{Methods}\nSimulations used mumax3 with typical parameters and a sufficiently small cell of about 2 nm, "
               "as described previously. The data are not shown here.\n\\section{Results}\nA typical trace is shown.\n"},
     expect=["\"typical\" stands where a value", "\"sufficiently\"", "approximate value", "mumax is named without a version",
             "\"as described previously\"", "\"not shown\""], absent=["A typical trace"])
case("methods: software with a version passes", "methods_check.py", ["m.tex"],
     {"m.tex": "\\section{Numerical methods}\nWe used mumax3 3.10 \\cite{mumax} and VAMPIRE (version 6.0).\n"}, absent=["named without a version"], status=0)

# ---------------------------------------------------------------- cite_order
FIG = "\\begin{figure}\\includegraphics{x}\\caption{%s}\\label{%s}\\end{figure}\n"
TAB = "\\begin{table}\\caption{%s}\\label{%s}\\begin{tabular}{cc}a&b\\\\\\end{tabular}\\end{table}\n"
case("cite: the example manuscript", "cite_order.py", ["main.tex"], PAPER, expect=["Fig. 3", "NOTES (3)", "opens by pointing at a display item"],
     absent=["ERRORS", "WARNINGS"], status=0)
case("cite: an uncited figure and an uncited table", "cite_order.py", ["p.tex"],
     {"p.tex": "\\begin{document}\nThe moment reverses (Fig.~\\ref{fig:a}).\n\n" + FIG % ("A.", "fig:a") + FIG % ("B.", "fig:b") + TAB % ("C.", "tab:c") + "\\end{document}"},
     expect=["Fig. 2 is never cited", "Table 1 is never cited"], status=1)
case("cite: first citations out of order", "cite_order.py", ["p.tex"],
     {"p.tex": "\\begin{document}\nThe threshold falls (Fig.~\\ref{fig:b}). The moment reverses (Fig.~\\ref{fig:a}).\n\n" + FIG % ("A.", "fig:a") + FIG % ("B.", "fig:b") + "\\end{document}"},
     expect=["Figs are first cited in the order 2, 1"], status=0)
case("cite: a panel that is never cited", "cite_order.py", ["p.tex"],
     {"p.tex": "\\begin{document}\nThe moment reverses [Fig.~\\ref{fig:a}(a)] and the threshold falls [Figs.~\\ref{fig:a}(b) and \\ref{fig:a}(d)].\n\n"
               + FIG % ("(a) Trace. (b) Threshold. (c) Phase diagram. (d) Energy.", "fig:a") + "\\end{document}"},
     expect=["panel (c) named in the caption and never cited", "a,b,d / a,b,c,d"], absent=["(d) named"])
case("cite: panel ranges and attached letters", "cite_order.py", ["p.tex"],
     {"p.tex": "\\begin{document}\nThe moment reverses [Fig.~\\ref{fig:a}(a)--(c)] and the map follows (Fig.~2a,b).\n\n"
               + FIG % ("(a) Trace. (b) Threshold. (c) Phase diagram.", "fig:a") + FIG % ("\\textbf{a} Map. \\textbf{b} Cut.", "fig:b") + "\\end{document}"},
     absent=["never cited", "WARNINGS"], expect=["a,b,c / a,b,c", "a,b / a,b", "typed by hand"])
case("cite: typed numbers and roman tables", "cite_order.py", ["p.tex"],
     {"p.tex": "\\begin{document}\nThe parameters are in Table II and the sample in Table I. Fig. 1 is a sketch. The film is 20 nm thick.\n\n"
               + TAB % ("A.", "t:a") + TAB % ("B.", "t:b") + FIG % ("S.", "f:s") + "\\end{document}"},
     expect=["Tables are first cited in the order 2, 1", "3 figure or table number(s) are typed by hand", "1 sentence(s) begin with an abbreviation"], status=0)
case("cite: supplementary items are left alone", "cite_order.py", ["p.tex"],
     {"p.tex": "\\begin{document}\nThe moment reverses (Fig.~\\ref{fig:a}); see also Fig. S2 and Supplementary Fig. 1.\n\n" + FIG % ("A.", "fig:a") + "\\end{document}"},
     absent=["typed by hand", "ERRORS", "WARNINGS"], status=0)

# ---------------------------------------------------------------- table_check
GOOD_TABLE = ("\\begin{table}\n\\caption{Switching time for films of different tilt angle.}\\label{tab:a}\n"
              "\\begin{tabular}{S S}\n\\toprule\n{Tilt angle (deg)} & {Switching time (ns)} \\\\\n\\midrule\n15 & 0.60 \\\\\n30 & 0.35 \\\\\n45 & 0.22 \\\\\n"
              "\\bottomrule\n\\end{tabular}\n\\end{table}\n")
BAD_TABLE = ("\\begin{table}\n\\begin{tabular}{|l|c|c|}\n\\hline\nSample & Thickness & Switching time \\\\\n\\hline\nA & 20 nm & 0.6 \\\\\n\\hline\n"
             "B & 30 nm & 0.22 \\\\\n\\hline\nC & 40 nm & 0.154 \\\\\n\\hline\nD & 50 nm & \\\\\n\\hline\n\\end{tabular}\n\\caption{Samples.}\n\\end{table}\n")
case("table: a well-formed table", "table_check.py", ["t.tex"], {"t.tex": GOOD_TABLE}, absent=["[error]", "[warning]", "[note]"], status=0)
case("table: the example supplement", "table_check.py", ["supplement.tex"], PAPER, expect=["4 rows, 4 columns"], absent=["[error]", "[warning]"], status=0)
case("table: every fault at once", "table_check.py", ["t.tex"], {"t.tex": BAD_TABLE},
     expect=["the caption stands below the table", "vertical rules", "a rule after every row", "no label", "the unit nm is repeated",
             "holds numbers and its heading carries no unit", "1 to 3 decimals", "do not line up on the decimal point", "1 empty cell(s)"], status=0)
case("table: caption below where the venue wants it", "table_check.py", ["t.tex", "--caption", "below"], {"t.tex": BAD_TABLE},
     absent=["the caption stands below"], status=0)
case("table: no caption is an error", "table_check.py", ["t.tex"], {"t.tex": GOOD_TABLE.replace("\\caption{Switching time for films of different tilt angle.}", "")},
     expect=["no caption"], status=1)
case("table: a long table and a wide one", "table_check.py", ["t.tex"],
     {"t.tex": "\\begin{table}\\caption{All runs of the sweep.}\\label{t}\n\\begin{tabular}{" + "c" * 10 + "}\n\\toprule\n" + " & ".join(f"Q{k} (nm)" for k in range(10))
               + " \\\\\n\\midrule\n" + "".join(" & ".join(str(r + k) for k in range(10)) + " \\\\\n" for r in range(30)) + "\\bottomrule\n\\end{tabular}\\end{table}\n"},
     expect=["30 rows (the limit is 25)", "10 columns (the limit is 8)"], status=0)
case("table: no rules at all", "table_check.py", ["t.tex"],
     {"t.tex": "\\begin{table}\\caption{Two samples.}\\label{t}\\begin{tabular}{lc}\nSample & Thickness (nm) \\\\\nA & 20 \\\\\nB & 30 \\\\\n\\end{tabular}\\end{table}\n"},
     expect=["no horizontal rule", "no rule under the heading row"])

# ---------------------------------------------------------------- prose_lint
BAD_PROSE = ("# Results\n\nIt is worth noting that noncollinear antiferromagnets have attracted considerable attention in recent years. "
             "Studies have shown that they play a crucial role in spintronics. We performed an analysis of the switching dynamics in order to delve into this "
             "intricate landscape of phenomena, highlighting the pivotal role of tilt. Overall, these novel results pave the way for unprecedented devices.\n\n"
             "We find that the moment reverses. We observe that the time is short. We note that this may possibly suggest a new mechanism, which could "
             "potentially be very important. There are many researches on it. This shows that the the effect is clearly robust, and it doesn't depend on "
             "colour or color. The spin Hall effect (SHE) is used. The SHE is large.\n")
case("prose: the example manuscript is clean", "prose_lint.py", ["main.tex"], PAPER, expect=["43 sentences", "0 warning(s), 0 note(s)"], status=0)
case("prose: every category fires", "prose_lint.py", ["bad.txt"], {"bad.txt": BAD_PROSE},
     expect=["STACKED (2", "\"may possibly\"", "HYPE (3", "\"pave the way\"", "USAGE (1", "\"researches\"", "contraction \"doesn't\"", "doubled word \"the the\"",
             "British and American spelling are mixed", "\"Studies have shown\" without a citation", "SHE is defined and then used 1 time(s)",
             "INFLATED (5", "FILLER (5", "\"in order to\"", "INTENSIFIER (2", "TAIL (1", "CLOSER (1", "HIDDEN-VERB (1",
             "three sentences in a row begin with \"We\"", "begins \"There are\"", "begins \"This shows\""], status=0)
case("prose: strict mode fails on warnings", "prose_lint.py", ["bad.txt", "--strict"], {"bad.txt": BAD_PROSE}, status=1)
case("prose: only one category", "prose_lint.py", ["bad.txt", "--only", "hype"], {"bad.txt": BAD_PROSE}, expect=["HYPE (3"], absent=["FILLER", "INFLATED"])
case("prose: a long sentence", "prose_lint.py", ["l.txt"],
     {"l.txt": "The threshold " + "of the film that was grown on the substrate " * 6 + "falls with the tilt angle of the plane. It is short. The moment reverses at once."},
     expect=["LONG (1", "words:"])
case("prose: mathematics and citations are masked", "prose_lint.py", ["m.tex"],
     {"m.tex": "\\begin{document}\nThe novel in $x_{\\mathrm{novel}}$ is a label, and Ref.~\\cite{remarkable2020} is a key. The moment reverses within "
               "$0.22\\,\\mathrm{ns}$ at a current of $6\\times10^{11}$ in the units of the text.\n\\end{document}\n"},
     expect=["HYPE (1"], absent=["remarkable"])
case("prose: a vague attribution with its citation passes", "prose_lint.py", ["m.tex"],
     {"m.tex": "\\begin{document}\nSeveral studies have shown that the moment reverses under a field~\\cite{A,B}. The reversal takes less than a nanosecond in thin films.\n\\end{document}\n"},
     absent=["VAGUE"])
BEFORE = "The time is $0.22\\,\\mathrm{ns}$ at 300 K~\\cite{A,B}, see Fig.~\\ref{fig:a}. This may suggest a mechanism of some kind.\n"
case("prose: compare finds changed content", "prose_lint.py", ["--compare", "a.tex", "b.tex"],
     {"a.tex": BEFORE, "b.tex": "The time is $0.25\\,\\mathrm{ns}$ at 310 K~\\cite{A}, see Fig.~\\ref{fig:b}. This shows a mechanism.\n"},
     expect=["CHANGED numbers", "300", "310", "CHANGED citation keys", "only before: B", "CHANGED reference labels", "CHANGED formulas",
             "hedges: 2 before, 0 after", "the edit changed protected content"], status=1)
case("prose: compare passes an edit of style", "prose_lint.py", ["--compare", "a.tex", "b.tex"],
     {"a.tex": BEFORE, "b.tex": "At 300 K the time is $0.22\\,\\mathrm{ns}$~\\cite{A,B}, as Fig.~\\ref{fig:a} shows. This may suggest a mechanism.\n"},
     expect=["numbers, citations, references and formulas are unchanged"], status=0)


def run(c):
    with tempfile.TemporaryDirectory() as folder:
        for name, text in c["files"].items():
            (Path(folder) / name).write_text(text, encoding="utf-8")
        done = subprocess.run([sys.executable, str(SCRIPTS / c["script"])] + list(c["args"]), capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=folder)
        return done.returncode, done.stdout + done.stderr


def main():
    wanted, failed, total = sys.argv[1:], 0, 0
    for c in CASES:
        if wanted and not any(w in c["name"] for w in wanted):
            continue
        total += 1
        code, text = run(c)
        missing = [e for e in c["expect"] if e not in text]
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
            print("\n".join("        | " + line[:200] for line in text.splitlines()[-14:]))
        else:
            print(f"ok    {c['name']}")
    print(f"\n{total - failed} of {total} cases pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
