#!/usr/bin/env python3
"""Check brief.md, the claim sheet that every part of the paper reads.

Usage:
    python3 brief_check.py brief.md
    python3 brief_check.py brief.md --minimal          (only the five claim fields are required)
    python3 brief_check.py brief.md --tex main.tex [supplement.tex ...]

Reports:
  errors    a claim field that is missing or not filled in; a RESULT of more than one sentence;
            an evidence kind outside the list; no entry under NOT SHOWN; an empty evidence table;
            one quantity with two values in the table of key numbers
  warnings  a RESULT of more than 30 words or with words of praise; a single entry under NOT SHOWN;
            a key number without unit or source; a number in RESULT that is not in the table;
            a field of the Question or Record section that is not filled in
  notes     "and" in RESULT (check that it does not join two findings); fields marked [unconfirmed];
            evidence rows that are not ready; with --tex, key numbers whose value does not occur in
            the manuscript

The script checks the form of the brief. Whether the result is true, and whether NOT SHOWN names
the right limits, only the authors can say. Standard library only. Exit status is 1 on errors.
"""
import argparse
import re
import sys

CLAIM = ["RESULT", "SYSTEM", "METHOD", "EVIDENCE", "NOT SHOWN"]
QUESTION = ["QUESTION", "PRIOR", "DIFFERENCE", "MATTERS"]
RECORD = ["Contributors", "Funding", "Thanks", "Data and code", "Competing interests", "AI tools", "History"]
KINDS = {"experiment", "simulation", "theory", "method", "dataset", "review"}
PRAISE = re.compile(r"\b(novel|unprecedented|remarkabl\w*|groundbreaking|breakthrough|outstanding|excellent|striking\w*|"
                    r"state-of-the-art|for the first time|the first|paves? the way|superior)\b", re.I)
EMPTY = re.compile(r"^\s*(<[^>]*>|tbd|todo|\?+|not yet|-+|\.\.\.)?\s*$", re.I)


def fields(text, names):
    """{name: value} for lines of the form 'NAME: value', with the list items or lines that follow."""
    out, lines = {}, text.split("\n")
    stop = re.compile(r"^(#|[A-Z][A-Za-z ]{1,24}:|\|)")
    for i, line in enumerate(lines):
        for name in names:
            m = re.match(rf"^\s*{re.escape(name)}\s*:\s*(.*)$", line)
            if not m:
                continue
            value, j = [m.group(1).strip()], i + 1
            while j < len(lines) and lines[j].strip() and not stop.match(lines[j].strip()):
                value.append(lines[j].strip())
                j += 1
            out[name] = "\n".join(v for v in value if v)
    return out


def table(text, heading):
    """Rows of the first table under '## heading': a list of dicts keyed by lower-case column names."""
    m = re.search(rf"^##\s*{re.escape(heading)}\b.*$", text, re.M | re.I)
    if not m:
        return None
    body = re.split(r"^##\s", text[m.end():], maxsplit=1, flags=re.M)[0]
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in body.split("\n") if line.strip().startswith("|")]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    if not rows:
        return []
    head = [h.lower() for h in rows[0]]
    return [dict(zip(head, r)) for r in rows[1:] if any(c for c in r)]


def column(row, *names):
    for key, value in row.items():
        if any(n in key for n in names):
            return value
    return ""


def detex(tex):
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\times\s*10\^\{?(-?\d+)\}?", r"e\1", tex)
    return re.sub(r"[{}$~\\]", " ", tex)


def check(text, minimal=False, tex=None):
    found = []

    def add(level, msg):
        found.append((level, msg))

    claim = fields(text, CLAIM)
    for name in CLAIM:
        if name not in claim or EMPTY.match(claim[name]):
            add("E", f"{name} is missing or not filled in")
    result = claim.get("RESULT", "")
    if result and not EMPTY.match(result):
        flat = re.sub(r"\s+", " ", re.sub(r"\[unconfirmed\]", " ", result, flags=re.I))   # the marker is not part of RESULT
        words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-/]*", flat))
        sentences = len(re.findall(r"[.!?](?=\s+[A-Z])", flat)) + 1
        if sentences > 1:
            add("E", f"RESULT has {sentences} sentences: one result, one sentence")
        if words > 30:
            add("W", f"RESULT has {words} words (the limit is 30): a sentence this long carries two findings or a method")
        praise = sorted({m.group(0).lower() for m in PRAISE.finditer(flat)})
        if praise:
            add("W", "RESULT uses words of praise (" + ", ".join(praise) + "): state the finding and let the number speak")
        if re.search(r"\band\b", flat):
            add("N", "RESULT contains \"and\": check that it does not join two findings")
    evidence = claim.get("EVIDENCE", "")
    if evidence and not EMPTY.match(evidence):
        kind = re.split(r"[;:,.(]", evidence, maxsplit=1)[0].lower()
        named = set(re.findall(r"[a-z]+", kind)) - {"and", "with", "or"}
        if not named or not named <= KINDS:
            add("E", f"EVIDENCE starts with \"{kind.strip()}\": the kind must be one of " + ", ".join(sorted(KINDS)))
    not_shown = claim.get("NOT SHOWN", "")
    if not_shown and not EMPTY.match(not_shown):
        entries = [e for e in re.split(r"\n|;", not_shown) if e.strip(" -*")]
        if len(entries) < 2:
            add("W", "NOT SHOWN has one entry: name at least two limits, and the objection a referee would raise first")
    for name, value in claim.items():
        if "[unconfirmed]" in value.lower():
            add("N", f"{name} is marked [unconfirmed]")

    evid = table(text, "Evidence")
    if evid is None or not evid:
        add("E", "the Evidence table is missing or empty: every statement that RESULT needs has a row")
    else:
        for k, row in enumerate(evid, 1):
            status = column(row, "status").lower()
            word = re.match(r"[a-z]+", status)
            if not word or word.group(0) not in ("ready", "partial", "missing"):
                add("W", f"Evidence row {k}: status \"{status}\" is not ready, partial or missing")
            elif word.group(0) != "ready":
                add("N", f"hole: evidence row {k} ({column(row, 'statement')[:60]}) is {status}")

    if not minimal:
        question = fields(text, QUESTION)
        for name in QUESTION:
            if name not in question or EMPTY.match(question[name]):
                add("W", f"{name} is not filled in")
        record = fields(text, RECORD)
        for name in RECORD:
            if name not in record or EMPTY.match(record[name]):
                add("W", f"Record: \"{name}\" is not filled in (write \"none\" if there is none)")
        numbers = table(text, "Key numbers")
        if numbers is None or not numbers:
            add("W", "the table of key numbers is missing or empty")
        else:
            seen = {}
            for k, row in enumerate(numbers, 1):
                quantity, value = column(row, "quantity"), column(row, "value")
                if not value:
                    add("E", f"key number {k} ({quantity}) has no value")
                    continue
                if not column(row, "unit"):
                    add("W", f"key number {k} ({quantity} = {value}) has no unit; write 1 for a pure number")
                if EMPTY.match(column(row, "source")):
                    add("W", f"key number {k} ({quantity} = {value}) has no source: a file, script or figure that gives it again")
                key = (quantity.lower(), column(row, "condition").lower())
                if key in seen and seen[key] != value:
                    add("E", f"\"{quantity}\" has two values under the same condition: {seen[key]} and {value}")
                seen[key] = value
            values = {column(r, "value") for r in numbers}
            for n in re.findall(r"(?<![A-Za-z_^{])\d+(?:\.\d+)?(?![A-Za-z_])", re.sub(r"[A-Z][a-z]?\d+", " ", result)):
                if not any(n in v for v in values):
                    add("W", f"RESULT quotes {n}, which is not in the table of key numbers")
            if tex:
                body = detex(tex)
                for row in numbers:
                    value = column(row, "value")
                    if value and not re.search(r"(?<![\d.])" + re.escape(value) + r"(?![\d])", body):
                        add("N", f"key number {column(row, 'quantity')} = {value} does not occur in the manuscript: unused, or quoted differently")
    return found


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Check brief.md.")
    ap.add_argument("brief")
    ap.add_argument("--minimal", action="store_true", help="require only the five claim fields and the evidence table")
    ap.add_argument("--tex", nargs="+", help="manuscript sources: list key numbers that do not occur in them")
    opts = ap.parse_args()
    try:
        text = open(opts.brief, encoding="utf-8").read()
        tex = "\n".join(open(p, encoding="utf-8", errors="replace").read() for p in opts.tex) if opts.tex else None
    except OSError as exc:
        sys.exit(f"brief_check: cannot read {exc.filename}: {exc.strerror}")
    found = check(text, opts.minimal, tex)
    print(f"brief_check: {opts.brief}")
    for level, title in (("E", "ERRORS"), ("W", "WARNINGS"), ("N", "NOTES")):
        rows = [m for lv, m in found if lv == level]
        if rows:
            print(f"\n{title} ({len(rows)})")
            for m in rows:
                print("  " + m)
    counts = [sum(1 for lv, _ in found if lv == x) for x in "EWN"]
    print(f"\n{counts[0]} error(s), {counts[1]} warning(s), {counts[2]} note(s)")
    sys.exit(1 if counts[0] else 0)


if __name__ == "__main__":
    main()
