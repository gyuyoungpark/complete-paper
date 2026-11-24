# Tables: journal rules and this skill's own rules

Read this when you need to explain a choice made in `parts/tables.md`. Journals agree that a table needs a title and headings with units; they differ in numerals, in where the title goes, and in the rules they draw.

Checked 2026-11-23. Verify each entry against the current page before citing it elsewhere.

## What journals require

- **APS Journals Style Guide (February 2026), section II.T.**
  - Numbering: roman numerals, in the order of citation in the text; tables in appendixes continue the sequence.
  - When to use one: material of more than about four lines becomes a numbered table; shorter material may stay in the running text.
  - Caption: every numbered table has one; it begins "TABLE I." and continues with a brief explanation; it defines the symbols and nonstandard abbreviations that apply to the whole table; it carries no footnote marks.
  - Headings: above a single horizontal rule; first letter capitalized; units in parentheses in the heading.
  - Rules: a simple table has three sets: a double rule at the top, a double rule at the foot, a single rule between headings and entries. Related entries are grouped by vertical space.
  - Footnotes: lower-case roman letters, assigned row by row, placed under the final rule; a source in the reference list is cited in short form.
  - Alignment: numbers by digit or decimal point; a unit shared by a column moves into the heading, units that vary by entry stay in the entries.
  - Long tables continue with repeated headings; extensive tabular data may go to the Supplemental Material.
- **Nature, formatting guide.** Each table has a short one-line title in bold; symbols and abbreviations are defined directly below the table, followed by brief essential description; tables are kept as small as possible. Extended Data tables are submitted as images.

## Where sources differ

- **Numerals**: roman in APS journals, arabic in most others.
- **Title**: above the table in APS journals, as a caption that may run to several sentences; a one-line title with notes below in Nature.
- **Rules**: the double rules of APS are produced by its own environment; `booktabs` gives single rules of different weight. Both agree on three horizontal rules and on none between body rows.

## What was measured here (2026-11-23)

- `scripts/table_check.py` passes its planted-fault cases in `evals/text/cases.py`. It has not been run on the tables of a published manuscript; its notes on precision and on units are heuristics and say so.

## This skill's own rules (no external source)

- The decision between sentence, table, figure and data package, and its thresholds (about four numbers for a sentence, about 25 rows and eight columns as limits of a printed table, about seven columns in one journal column).
- "Compare down a column", ordering rows by meaning, one precision per column, and a stated meaning for every empty cell. These are common advice in guides to table design; no study was consulted for them here.
- No vertical rules and no rule between rows. APS states the three sets of rules; the ban on other lines is this skill's reading of it and of common typographic practice.
