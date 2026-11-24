# Tables

Stage B · Reads: `outline.md`, `brief.md`, `venue.md`, `notation.md`, the data files, the paragraph that first cites each table · Writes: the tables in the manuscript or supplement, the list of what each caption must define, the values moved to the text

A table is for looking up exact values and comparing them. A figure shows a pattern; a table gives the numbers that a reader will copy, check or set beside their own.

It has two jobs:

- **The comparison takes seconds.** The values to be compared stand next to each other, in one column, in one unit, at one precision.
- **The table stands alone.** Title, headings and notes say what every row, column and entry is; a reader who opens the paper at the table can use it.

## Modes

- **Write** (build): data exist and no table yet. Build the table, or decide that the values belong in the text.
- **Revise**: a table exists; fix its design first, then its wording.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

1. `outline.md`: the statement the table supports, and its role.
2. `brief.md`: the key numbers. A key number in a table equals its entry in the brief.
3. `notation.md`: symbols, units, and the form in which uncertainties are written.
4. `venue.md`: numbering (roman or arabic), where the title goes and how it begins, rules, marks for footnotes, file format, size.
5. The data files. Every value comes from them, unchanged (first principle 2 in `SKILL.md`).

## Steps

### Step 1. Table, figure or sentence

| Content | Form |
|---|---|
| Up to about four numbers | A sentence |
| Exact values that readers will look up or reuse: parameters, samples, fit results, comparison with earlier values | A table |
| A trend or a shape across many points | A figure; the numbers go to the data package |
| Different quantities with different units for a few cases | A table |
| More than about 25 rows, or values nobody reads through | The data package, with the rows that the text discusses kept in a short table (`parts/supplement.md`) |

Do not show the same data as a table and as a figure. Where both seem needed, the figure goes in the paper and the numbers in the data package.

- A few values, for example a 2 × 2 comparison, read better in the text than in a table.
- A table that is not a key result stays short: only the rows and columns its statement needs. The rest goes to the supplement or the data package.

### Step 2. Design for the comparison

- **Compare down a column.** Numbers that the reader will compare stand in one column, in adjacent rows. Cases are rows; quantities are columns. If the comparison runs across, turn the table.
- **Order rows by meaning**: the control or reference first; then by the varied parameter or by size. Not alphabetically, and not in the order of measurement.
- **One quantity and one unit per column.** SI units (ground rule 8). The unit stands once, in the heading, in parentheses or in the venue's form. When every column shares one unit, state it once in the caption instead. Units stay in the cells only where each row is a different quantity, as in a table of parameters.
- **One precision per column**, set by the uncertainty. Not 0.6, 0.22 and 0.154 under one heading. Take each value from its data file at that precision. If the values in hand differ in precision, ask the user for them at the precision the data support, and never round or pad them yourself (first principle 2).
- **Uncertainty in one form** throughout the paper: 1.23(4) or 1.23 ± 0.04, as `notation.md` records. Say once what it is (standard deviation, fit error).
- **Align numbers on the decimal point**; align text to the left.
- **Headings**: the name or symbol of the quantity as in `notation.md`, then the unit. First letter capitalized. A spanning heading groups related columns. When a column is too narrow for a name, the heading gives only the symbol, and the caption names each symbol and gives its unit.
- **No explanation in cells.** No notes column and no sentences in cells. What needs explaining goes to the caption or a note (Step 4).
- **No empty cell without a meaning.** A dash for "does not apply"; a stated mark for "not measured"; both explained in a note. A value that exists but is not in hand stays empty with a TODO marker, and the user is told. It is never filled in, estimated or copied from elsewhere (first principle 2).
- **Emphasis** (bold for the best value) only when the title says what it marks.
- **Earlier values** carry their citation, in a column or in a note.
- **Size**: about seven columns fit one column of a journal page. A wider table is split or turned.

### Step 3. Rules and layout

- Horizontal rules only: above the headings, below them, and at the foot. A further rule under a spanning heading.
- No vertical rules. No rule between rows of the body: group rows with space.
- No shading and no colour.
- In LaTeX, use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), or the venue's own environment (`ruledtabular` in REVTeX draws the journal's double rules). Align numbers with an `S` column of `siunitx` or a `d` column of `dcolumn`.

```latex
\begin{table}
  \caption{Switching time of the octupole moment for films of different tilt angle, at a current
  density of $6\times10^{11}\,\mathrm{A/m^2}$. The uncertainty of each time is $0.01\,\mathrm{ns}$.}
  \label{tab:switching}
  \begin{tabular}{S[table-format=2.0] S[table-format=2.0] S[table-format=1.2]}
    \toprule
    {Tilt angle (deg)} & {Thickness (nm)} & {Switching time (ns)} \\
    \midrule
    15 & 20 & 0.60 \\
    30 & 20 & 0.35 \\
    45 & 20 & 0.22 \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Step 4. Title and notes

- The title follows `parts/captions.md` and the venue's form. It says what the rows are, what the columns are, and the conditions common to every entry. It defines symbols and nonstandard abbreviations that apply to the whole table.
- List for the caption what the table does not show itself: the names and units of symbols used alone in headings, a unit shared by every column, abbreviations, and the source of any value taken from a reference.
- It reports no result and no interpretation: those are in the text.
- **Notes** under the table, marked in the venue's way, give what applies to single entries: an exception, a different condition, the source of a value.
- A table of parameters says where each value comes from: measured here, fitted here, from the literature (cited), or assumed.

### Step 5. Number and cite

- Number tables in the order of their first citation, in the venue's numerals.
- Every table is cited by a sentence that uses it. A table of parameters may be introduced as such ("Table I lists ..."); a table of results is cited by the sentence that states the finding.
- Tables in an appendix or the supplement are numbered as the venue and `parts/supplement.md` say.

### Step 6. Check

```
python scripts/table_check.py main.tex supplement.tex            # --caption below where the venue wants that
python scripts/cite_order.py main.tex                            # every table cited, and in order
```

`table_check.py` reports a table without caption (error); vertical rules, a rule after every row, a caption on the wrong side, a missing heading rule (warnings); and, as notes, a unit repeated in the cells, a heading without unit over numbers, mixed decimals in a column, numbers not aligned on the decimal point, empty cells, more than 25 rows or eight columns, and a missing label.

Then compare by hand: every number that also appears in the text, the abstract or a figure is the same number, and every value matches its data file (ground rule 16). Report a disagreement. The data decide.

### When rules pull in different directions

The venue's form first (numerals, title position, rules), then correctness of every entry, then the comparison, then compactness.

## Checks

1. **Needed**: the table carries exact values that a reader will look up or compare; it is not a figure's data repeated, and not four numbers that fit a sentence.
2. **Comparison**: the values to be compared stand in one column, in adjacent rows, ordered by meaning.
3. **Units**: SI; one per column, in the heading, or once in the caption when every column shares it; symbols and units as in `notation.md`.
4. **Precision**: one per column, matching the uncertainty; one form of uncertainty, explained once.
5. **Alignment**: numbers on the decimal point, text to the left.
6. **Rules**: three horizontal rules, none vertical, none between body rows.
7. **Cells**: none empty without a stated meaning; emphasis explained.
8. **Stands alone**: title, headings and notes define every row, column, symbol and abbreviation.
9. **Sources**: every value that is not from this work carries its citation; parameters carry their origin.
10. **Cited and numbered**: in the order of first citation, in the venue's numerals and form.
11. **Agreement**: numbers equal those in the text, the abstract, the figures and `brief.md`.
12. **Size and place**: fits the column or the page; long tables are in the data package.
13. **Lean**: no explanation in cells; a supporting table only as long as its statement needs; a few values in the text instead.
14. **Values untouched**: every value copied from its data file; none rounded, changed or filled in by the agent; every blank marked and reported.

## Report

Reply in the user's language. Keep it short:

1. **The table**, as source, with its title.
2. **Design choices**: what is compared, the order of rows, the precision.
3. **`table_check.py`**: what it reports.
4. **For the caption**: the list from Step 4.
5. **Flags**: a value without source or uncertainty; a blank value; a number that differs from the text or its data file; a table proposed for the data package, for a figure or for the text.

In Audit mode, replace items 1 and 2 with the table of the fourteen checks and the smallest fix for each failure.

Propose only. Never round, change, fill in or drop a value (first principle 2). Reorder rows only by the rules of Step 2, and say so.

## Example (invented; the numbers are placeholders)

Before: a table with vertical and horizontal lines around every cell; samples in the order they were grown; "20 nm", "30 nm", "40 nm" typed in each cell; switching times given as 0.6, 0.22 and 0.154; one empty cell; the caption below, reading "Results."

After: rows ordered by tilt angle with the untilted film first; headings "Tilt angle (deg)", "Thickness (nm)", "Switching time (ns)"; times taken again from the data file at two decimals (0.60, 0.22, 0.15), with the uncertainty 0.01 stated in the title; a dash, explained in a note, where the film did not switch; three rules; the title above: "Switching time of the octupole moment for films of different tilt angle at a current density of 6 × 10^11 A/m^2. A dash marks films that did not switch."

## Relation to other parts

- **Outline** decides that the table exists and what it supports. **Figures** (`parts/figures.md`) take over when the content is a pattern.
- **Captions** (`parts/captions.md`) govern the wording of the title and write it from the list in Step 4; **notation** the symbols, units and the form of uncertainties.
- **Methods** (`parts/methods.md`) use this part for the table of parameters.
- **Supplement** (`parts/supplement.md`) sends long tables to the data package.
- **Audit** (`parts/audit.md`) reruns `table_check.py` and compares the numbers of tables, text and abstract.

## Sources

The journal rules behind these choices are in `references/tables-evidence.md`; read it when you need to explain a choice.
