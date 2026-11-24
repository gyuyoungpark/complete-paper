#!/usr/bin/env python3
"""Check the tables of a LaTeX manuscript against the rules of parts/tables.md.

Usage:
    python3 table_check.py main.tex [supplement.tex ...]
    python3 table_check.py main.tex --caption below      (venues that put the title under the table)
    python3 table_check.py main.tex --max-rows 25 --max-cols 8

Reports, per table:
  errors    no caption
  warnings  vertical rules; a rule after every row; the caption on the wrong side of the table;
            no rule or no heading row
  notes     a unit repeated in the cells of a column instead of standing in the heading; a heading
            without unit over a column of numbers; mixed numbers of decimals in a column; numbers of
            different length in a column that is not aligned on the decimal point; empty cells; more
            rows or columns than the limits; no label

The script reads tabular, tabular*, tabularx and longtable environments (also inside ruledtabular),
follows \\input, and treats the rows above the first inner rule as headings. It does not judge whether
a table should be a figure or a sentence. Standard library only. Exit status is 1 on errors.
"""
import argparse
import os
import re
import sys

RULE = re.compile(r"\\(?:hline|toprule|midrule|bottomrule|colrule|botrule|hhline\{[^}]*\}|cline\{[^}]*\}|cmidrule(?:\([^)]*\))?\{[^}]*\})")
INNER = re.compile(r"\\(?:hline|midrule|colrule)")
NUMBER = re.compile(r"^[-+\u2212]?\d+(?:\.(\d+))?(?:\(\d+\))?$")
WITH_UNIT = re.compile(r"^[-+\u2212]?\d+(?:\.\d+)?\s*([A-Za-z\u00b5%][A-Za-z\u00b5%/^0-9\-]*)$")


def read_tex(path, depth=0):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit(f"table_check: cannot read {path}: {exc.strerror}")
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


def group(text, i):
    """Content of the brace group that opens at text[i], and the position after it."""
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
                return text[i + 1:j], j + 1
        j += 1
    return text[i + 1:], len(text)


def clean(cell):
    """A cell as plain text: mathematics signs and spacing commands removed, units kept."""
    c = re.sub(r"\\multicolumn\s*\{\d+\}\s*\{[^}]*\}\s*", "", cell)
    c = re.sub(r"\\(?:un|mathrm|text|textrm|mathit|textbf|textit|si|unit)\s*\{([^{}]*)\}", r"\1", c)
    c = re.sub(r"\\(?:SI|qty)\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"\1 \2", c)
    c = re.sub(r"\\num\s*\{([^{}]*)\}", r"\1", c)
    c = c.replace("\\%", "%").replace("\\,", " ").replace("~", " ").replace("\\ ", " ")
    c = re.sub(r"\\pm\s*[\d.]+", "", c)
    c = re.sub(r"\\times\s*10\^\{?-?\d+\}?", "", c)
    c = re.sub(r"\\[a-zA-Z]+", " ", c)
    return re.sub(r"\s+", " ", re.sub(r"[${}]", "", c)).strip()


def tables(text):
    """Every tabular-like environment with the float around it."""
    out = []
    floats = [(m.start(), text.find("\\end{%s}" % m.group(1), m.end()), m.group(1))
              for m in re.finditer(r"\\begin\{(table\*?|sidewaystable|longtable)\}", text)]
    for m in re.finditer(r"\\begin\{(tabular\*?|tabularx|longtable)\}", text):
        env, pos = m.group(1), m.end()
        if env in ("tabular*", "tabularx"):
            _, pos = group(text, pos) if text[pos:pos + 1] == "{" else ("", pos)
        opt = re.match(r"\s*\[[^\]]*\]", text[pos:])
        if opt:
            pos += opt.end()
        if text[pos:pos + 1] != "{":
            continue
        spec, pos = group(text, pos)
        end = text.find("\\end{%s}" % env, pos)
        if end < 0:
            continue
        around = next(((a, b) for a, b, _ in floats if a <= m.start() and (b < 0 or end <= b + 20)), None)
        out.append({"start": m.start(), "spec": spec, "body": text[pos:end], "end": end, "float": around, "env": env})
    return out


def analyse(t, text, caption_side, max_rows, max_cols):
    found = []

    def add(level, msg):
        found.append((level, msg))

    a, b = t["float"] if t["float"] else (t["start"], t["end"])
    b = b if b > 0 else t["end"]
    outer = text[a:t["start"]] + text[t["end"]:b] + (t["body"] if t["env"] == "longtable" else "")
    cap = re.search(r"\\caption\*?\s*(?:\[[^\]]*\])?\s*\{", outer)
    if not cap:
        add("E", "no caption: a table needs a title that says what its rows and columns are")
    else:
        before = "\\caption" in text[a:t["start"]] or t["env"] == "longtable"
        if caption_side == "above" and not before:
            add("W", "the caption stands below the table; this venue puts it above (see venue.md, or run with --caption below)")
        if caption_side == "below" and before and t["env"] != "longtable":
            add("W", "the caption stands above the table; this venue puts it below")
    if "\\label" not in text[a:b]:
        add("N", "no label: the table can only be cited by a typed number")
    spec = re.sub(r"\{[^{}]*\}", "", t["spec"])
    if "|" in spec:
        add("W", "vertical rules in the column specification: use space and alignment to separate columns")
    body = t["body"]
    raw_rows = [r for r in re.split(r"\\\\(?:\[[^\]]*\])?", body)]
    rows, rule_after, header_end = [], [], None
    for r in raw_rows:
        inner = bool(INNER.search(r)) or bool(re.search(r"\\(?:toprule|bottomrule|botrule)", r))
        if rows and INNER.search(r) and header_end is None:
            header_end = len(rows)
        if rows and inner:
            rule_after[-1] = True
        content = RULE.sub(" ", r).replace("\\endhead", " ").replace("\\endfirsthead", " ").strip()
        if not content:
            continue
        cells = []
        for c in re.split(r"(?<!\\)&", content):
            span = re.match(r"\s*\\multicolumn\s*\{(\d+)\}", c)
            cells.append(clean(c))
            cells.extend([""] * (int(span.group(1)) - 1 if span else 0))
        rows.append(cells)
        rule_after.append(False)
    if not rows:
        return found, 0, 0
    # REVTeX's ruledtabular draws the rules itself: double rules at top and foot, one under the first row
    ruled = "\\begin{ruledtabular}" in text[a:t["start"]] and "\\end{ruledtabular}" in text[t["end"]:b + 20]
    if not RULE.search(body) and not ruled:
        add("W", "no horizontal rule: set one above the headings, one below them and one at the foot")
    if header_end is None:
        if not ruled:
            add("W", "no rule under the heading row, so headings and entries cannot be told apart")
        header_end = 1
    head, data = rows[:header_end], rows[header_end:]
    ncols = max(len(r) for r in rows)
    inner_rules = sum(1 for k, flag in enumerate(rule_after[header_end:-1]) if flag)
    if len(data) >= 4 and inner_rules >= len(data) - 1:
        add("W", "a rule after every row: rules belong above the headings, below them and at the foot; group rows with space")
    if len(data) > max_rows:
        add("N", f"{len(data)} rows (the limit is {max_rows}): a table to look values up in belongs in the data package, "
                 "with the rows that the text discusses kept here")
    if ncols > max_cols:
        add("N", f"{ncols} columns (the limit is {max_cols}): split the table, or turn it so that the cases run down the page")
    letters = [c for c in re.findall(r"[A-Za-z]", spec)]
    blanks = 0
    for k in range(ncols):
        column = [r[k] if k < len(r) else "" for r in data]
        heading = " ".join(r[k] for r in head if k < len(r)).strip()
        blanks += sum(1 for c in column if not c) if k else 0
        units = [m.group(1) for c in column for m in [WITH_UNIT.match(c)] if m]
        numeric = [m for c in column for m in [NUMBER.match(c)] if m]
        if units and len(units) >= 3 and max(units.count(u) for u in set(units)) >= 3:
            unit = max(set(units), key=units.count)
            add("N", f"column {k + 1} (\"{heading[:30]}\"): the unit {unit} is repeated in the cells; put it once in the heading, in parentheses")
        if len(numeric) >= 3 and len(numeric) >= 0.6 * len([c for c in column if c]):
            if heading and not re.search(r"\(|\[|/|%|ratio|number|index|count|^#|^N\b|^n\b|No\.", heading) and not units:
                add("N", f"column {k + 1} (\"{heading[:30]}\") holds numbers and its heading carries no unit; give the unit, or \"arb. units\"")
            decimals = sorted({len(m.group(1) or "") for m in numeric})
            if len(decimals) > 1:
                add("N", f"column {k + 1} (\"{heading[:30]}\"): {decimals[0]} to {decimals[-1]} decimals in one column; quote one precision, "
                         "set by the uncertainty (ignore if the rows are different quantities)")
            widths = {len(m.group(0).split(".")[0].lstrip("+-\u2212")) for m in numeric}
            kind = letters[k] if k < len(letters) else ""
            if kind in ("c", "l", "r") and (len(decimals) > 1 or (len(widths) > 1 and kind != "r")) and any(m.group(1) for m in numeric):
                add("N", f"column {k + 1} is set as \"{kind}\": numbers of different length do not line up on the decimal point; "
                         "use an S column (siunitx) or a d column (dcolumn)")
    if blanks:
        add("N", f"{blanks} empty cell(s): say in a note what an empty cell means, or fill it (a dash for \"does not apply\")")
    return found, len(data), ncols


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Check the tables of a LaTeX manuscript.")
    ap.add_argument("tex", nargs="+")
    ap.add_argument("--caption", choices=["above", "below"], default="above", help="where the venue puts the caption (default above)")
    ap.add_argument("--max-rows", type=int, default=25)
    ap.add_argument("--max-cols", type=int, default=8)
    opts = ap.parse_args()
    lines = [line for p in opts.tex for line in read_tex(p)]
    text = "\n".join(t for _, _, t in lines)
    offsets, pos = [], 0
    for _, _, t in lines:
        offsets.append(pos)
        pos += len(t) + 1

    def where(p):
        import bisect
        f, n, _ = lines[max(bisect.bisect_right(offsets, p) - 1, 0)]
        return f"{f}:{n}"

    found_all, counts = [], {"E": 0, "W": 0, "N": 0}
    print("table_check: " + ", ".join(opts.tex))
    all_tables = tables(text)
    if not all_tables:
        print("\nno tables found")
    for k, t in enumerate(all_tables, 1):
        found, nrows, ncols = analyse(t, text, opts.caption, opts.max_rows, opts.max_cols)
        print(f"\nTABLE {k} at {where(t['start'])}: {nrows} rows, {ncols} columns")
        for level in "EWN":
            for lv, msg in found:
                if lv == level:
                    counts[lv] += 1
                    print(f"  [{ {'E': 'error', 'W': 'warning', 'N': 'note'}[lv] }] {msg}")
        found_all.extend(found)
    print(f"\n{counts['E']} error(s), {counts['W']} warning(s), {counts['N']} note(s)")
    sys.exit(1 if counts["E"] else 0)


if __name__ == "__main__":
    main()
