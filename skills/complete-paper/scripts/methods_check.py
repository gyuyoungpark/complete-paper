#!/usr/bin/env python3
"""Reproducibility checklist for the methods of a paper, and a scan of the methods text.

Usage:
    python3 methods_check.py --template simulation experiment > repro.md
    python3 methods_check.py main.tex [supplement.tex ...] --repro repro.md
    python3 methods_check.py main.tex --all            (scan the whole text, not only method sections)

Kinds for --template: simulation, experiment, theory, algorithm. The general items are always included.

repro.md is a table with one row per item: what a reader needs in order to repeat the work, where the
manuscript states it, and its value. The author or the agent fills in "Where stated" with a place in
the manuscript (section, equation, table, figure, supplement section) or with "n/a" and a reason.

Reports:
  errors    a checklist row with no place; a place given as a quoted heading or a `label` that the
            manuscript does not contain
  warnings  "n/a" without a reason; items of the declared kinds that were removed from the checklist;
            "data not shown" or "as described previously" in the text
  notes     in method sections: words that stand where a value should be ("standard", "typical",
            "appropriate", "sufficiently", "several"); software named without a version or citation;
            approximate values ("about 5 nm")

The scan flags places to review; it does not know which details matter for this result.
Standard library only. Exit status is 1 on errors.
"""
import argparse
import os
import re
import sys

ITEMS = {
    "general": [
        ("G1", "System: composition, geometry and dimensions"),
        ("G2", "Every parameter with value, unit and origin (measured, fitted, literature, assumed)"),
        ("G3", "Sequence of steps, in the order in which they were done"),
        ("G4", "Number of samples, devices or runs, and how they were chosen"),
        ("G5", "What was excluded, and why"),
        ("G6", "Operational definition of every derived quantity that is plotted or quoted"),
        ("G7", "What the error bars and uncertainties are, and the number of repeats behind them"),
        ("G8", "Processing between raw output and plotted points; fit model, free parameters and range"),
        ("G9", "Software: name, version, citation, settings that differ from the defaults"),
        ("G10", "Where the data and the code are"),
    ],
    "simulation": [
        ("S1", "Equation of motion or Hamiltonian, with every term"),
        ("S2", "Code, version or commit, and options that differ from the defaults"),
        ("S3", "Discretization (cell size, lattice, basis) against the relevant length or energy scale"),
        ("S4", "Time step and integrator; total simulated time"),
        ("S5", "Boundary conditions and system size"),
        ("S6", "Material parameters with their sources"),
        ("S7", "Initial state and how it was relaxed"),
        ("S8", "Excitation: shape, amplitude, duration, rise time"),
        ("S9", "Temperature: how fluctuations enter, seeds, number of realizations"),
        ("S10", "Convergence tests: discretization, time step, system size"),
        ("S11", "Criteria: how an event (switching, threshold, convergence) is decided"),
    ],
    "experiment": [
        ("X1", "Sample: layers in order with thicknesses, substrate"),
        ("X2", "Growth or synthesis: method and conditions; annealing"),
        ("X3", "Patterning and device dimensions"),
        ("X4", "Characterization of structure and properties, with instruments"),
        ("X5", "Measurement set-up: instruments (maker, model), geometry of current, field and detection"),
        ("X6", "Measurement conditions: temperature, field, frequency, amplitude, pulse width"),
        ("X7", "Calibration of field, temperature, power or current density"),
        ("X8", "Protocol: initialization, sequence, averaging"),
        ("X9", "Number of devices and samples; variation between them"),
        ("X10", "Corrections: background, offsets, heating, shunting"),
    ],
    "theory": [
        ("T1", "Assumptions and approximations, each with its range of validity"),
        ("T2", "Conventions: signs, units, definitions"),
        ("T3", "Where each step of the derivation is given"),
        ("T4", "Limits in which the result reduces to a known one"),
    ],
    "algorithm": [
        ("A1", "Problem instances or data sets: source, version, size, splits"),
        ("A2", "Baselines, and how they were tuned"),
        ("A3", "Parameters of the method, and how they were chosen"),
        ("A4", "Random seeds and number of runs"),
        ("A5", "Metrics: definition and how they were computed"),
        ("A6", "Hardware and run time"),
    ],
}
METHOD_HEAD = re.compile(r"method|model|experiment|simulation|numerical|set-?up|sample|device|fabricat|growth|measurement|"
                         r"computational|calculation|implementation|appendix|material", re.I)
VAGUE = re.compile(r"\b(standard|typical(?:ly)?|appropriate(?:ly)?|suitabl[ey]|sufficiently|conventional|as usual|several|"
                   r"a few|various|carefully|properly|reasonable|reasonably)\b", re.I)
APPROX = re.compile(r"\b(about|approximately|roughly|around|nearly)\s+\$?\d|[~\u223c]\s*\$?\d|\\sim\s*\d", re.I)
SOFTWARE = ["mumax", "OOMMF", "VAMPIRE", "Spirit", "UppASD", "LAMMPS", "Quantum ESPRESSO", "VASP", "WIEN2k", "ABINIT",
            "Wannier90", "COMSOL", "MATLAB", "Mathematica", "LabVIEW", "Origin", "NumPy", "SciPy", "PyTorch", "TensorFlow",
            "JAX", "scikit-learn", "Gurobi", "CPLEX", "Kwant", "QuTiP", "OpenMX", "Fidimag", "Ubermag", "BORIS"]
PHRASES = [(re.compile(r"\bdata\s+not\s+shown\b|\bnot\s+shown\s+here\b|\bresults?\s+not\s+shown\b", re.I),
            "\"not shown\": give the place in the supplement or the data package, or remove the sentence"),
           (re.compile(r"\bas\s+(?:described|reported|detailed)\s+(?:previously|elsewhere|earlier)\b", re.I),
            "\"as described previously\": cite the work and state what was the same and what differed here")]


def read_tex(path, depth=0):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit(f"methods_check: cannot read {path}: {exc.strerror}")
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


def template(kinds):
    rows = ["# Reproducibility checklist", "",
            "Kind: " + ", ".join(kinds), "",
            "\"Where stated\" names a place in the manuscript (section, equation, table, figure, supplement section),",
            "or says n/a with the reason in the last column. A quoted heading or a `label` is checked against the source.", "",
            "| # | Item | Where stated | Value or note |", "|---|---|---|---|"]
    for kind in ["general"] + kinds:
        rows += [f"| {i} | {text} | | |" for i, text in ITEMS[kind]]
    return "\n".join(rows) + "\n"


def parse_repro(text):
    kind = re.search(r"^Kind\s*:\s*(.+)$", text, re.M | re.I)
    kinds = [k for k in re.findall(r"[a-z]+", kind.group(1).lower()) if k in ITEMS] if kind else []
    rows = []
    for line in text.split("\n"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"[A-Z]\d+", cells[0]):
            rows.append({"id": cells[0], "item": cells[1], "where": cells[2], "note": cells[3] if len(cells) > 3 else ""})
    return kinds, rows


def check(lines, repro, scan_all):
    found = []

    def add(level, where, msg):
        found.append((level, where, msg))

    text = "\n".join(t for _, _, t in lines)
    headings = [m.group(1) for m in re.finditer(r"\\(?:sub)*(?:section|paragraph)\*?\s*(?:\[[^\]]*\])?\{([^{}]*)\}", text)]
    labels = set(re.findall(r"\\label\s*\{([^}]*)\}", text))
    if repro is not None:
        kinds, rows = parse_repro(repro)
        if not rows:
            add("E", "repro.md", "no checklist rows were found: make the file with --template")
        have = {r["id"] for r in rows}
        for kind in ["general"] + kinds:
            gone = [i for i, _ in ITEMS[kind] if i not in have]
            if gone and rows:
                add("W", "repro.md", f"items of the {kind} list are not in the checklist: {', '.join(gone)}; keep the row and write n/a with a reason")
        for r in rows:
            where = r["where"]
            if not where or re.fullmatch(r"<[^>]*>|\?+|tbd|todo", where, re.I):
                add("E", "repro.md", f"{r['id']} ({r['item'][:60]}): no place in the manuscript is given")
            elif re.match(r"n/?a\b|not applicable", where, re.I):
                if not r["note"]:
                    add("W", "repro.md", f"{r['id']} ({r['item'][:60]}): n/a without a reason")
            elif lines:
                for quoted in re.findall(r"[\"\u201c]([^\"\u201d]{3,})[\"\u201d]", where):
                    if not any(quoted.lower() in h.lower() for h in headings):
                        add("E", "repro.md", f"{r['id']}: the heading \"{quoted}\" is not in the manuscript")
                for key in re.findall(r"`([^`]+)`", where):
                    if key not in labels:
                        add("E", "repro.md", f"{r['id']}: the label `{key}` is not in the manuscript")
    # ----- the text
    section, inside = "", False
    for name, n, line in lines:
        m = re.search(r"\\(?:sub)*section\*?\s*(?:\[[^\]]*\])?\{([^{}]*)\}", line)
        if m:
            section, inside = m.group(1), bool(METHOD_HEAD.search(m.group(1)))
        if "\\begin{thebibliography}" in line:
            inside, section = False, "references"
        where = f"{name}:{n}"
        for pattern, msg in PHRASES:
            if pattern.search(line):
                add("W", where, msg)
        if not (inside or scan_all) or section == "references":
            continue
        for m in VAGUE.finditer(line):
            add("N", where, f"\"{m.group(0)}\" stands where a value or a procedure should be: \"{line.strip()[max(0, m.start() - 30):m.end() + 30].strip()}\"")
        for m in APPROX.finditer(line):
            add("N", where, f"approximate value (\"{m.group(0).strip()}\"): give the value and its uncertainty, or say why it is only approximate")
        for soft in SOFTWARE:
            for m in re.finditer(rf"(?<![A-Za-z]){re.escape(soft)}(?![A-Za-z])", line):
                tail = line[m.end():m.end() + 70]
                if not re.search(r"\d+\.\d+|version|v\d|\\cite|commit|release|R20\d\d", tail, re.I):
                    add("N", where, f"{soft} is named without a version or a citation")
    return found


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Reproducibility checklist and scan of the methods text.")
    ap.add_argument("tex", nargs="*", help="manuscript sources")
    ap.add_argument("--repro", help="the filled-in checklist (repro.md)")
    ap.add_argument("--template", nargs="*", metavar="KIND", help="print an empty checklist for these kinds and stop")
    ap.add_argument("--all", action="store_true", help="scan every section, not only method sections")
    opts = ap.parse_args()
    if opts.template is not None:
        bad = [k for k in opts.template if k not in ITEMS or k == "general"]
        if bad:
            sys.exit("methods_check: unknown kind " + ", ".join(bad) + "; choose from simulation, experiment, theory, algorithm")
        sys.stdout.write(template(opts.template))
        return
    if not opts.tex and not opts.repro:
        ap.error("give the manuscript sources, a checklist with --repro, or --template")
    lines = [line for p in opts.tex for line in read_tex(p)]
    repro = None
    if opts.repro:
        try:
            repro = open(opts.repro, encoding="utf-8").read()
        except OSError as exc:
            sys.exit(f"methods_check: cannot read {opts.repro}: {exc.strerror}")
    found = check(lines, repro, opts.all)
    print("methods_check: " + ", ".join(opts.tex + ([opts.repro] if opts.repro else [])))
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
