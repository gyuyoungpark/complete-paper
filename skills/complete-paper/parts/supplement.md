# Supplement

Stage C · Reads: `venue.md`, `outline.md`, `brief.md`, the main text and its preamble, `notation.md`, `figstyle.md`, `suppmap.md` if it exists · Writes: the supplement, its callouts in the main text, `paper-state/suppmap.md`, the README of the data package

A supplement holds what a reader needs in order to check or repeat the work, and does not need in order to understand or believe it.

It has two jobs:

- **The main text stands alone.** A reader who never opens the supplement follows every statement of the claim chain and sees its evidence.
- **The supplement is cheap to use.** A reader who is sent there finds, at the place named, one question answered, in the notation and style of the main text. It is not a second paper and not a store of data.

Its difficulty is that a supplement costs the author nothing to lengthen and costs every reader something to open: the reader leaves the argument, opens another file, finds the place, and has to find the way back. Three budgets follow, and they govern everything below:

1. **Few doors.** The main text sends the reader to the supplement only where a statement needs it: one callout per supplementary section. The supplement cites its own figures and tables.
2. **No larger than the paper.** The supplement does not exceed the main text, in words and in display items.
3. **Argument only.** What can be used without explanation (numbers, traces, input files, code) goes to the data package and takes no page.

And one rule of form: **one paper, one style.** The supplement is written, drawn and typeset by the rules already set for the main text.

Terms used here. A **callout** is a sentence of the main text that sends the reader to the supplement. The **data package** is the set of files deposited in a repository and named in the data availability statement. The **middle tier** is whatever the venue offers between the two: an appendix, the End Matter of a letter, Extended Data, online Methods.

## Modes

- **Write**: first plan, before drafting: send every candidate item to its place (Step 1) and write `suppmap.md`. Then draft: write the sections and the callouts.
- **Revise**: a supplement exists. Run the check, fill in `suppmap.md`, cut in the order of Step 2, then rewrite the callouts.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read before writing:

1. `venue.md`: the official name ("Supplemental Material", "Supplementary Information", "Supporting Information"); the numbering prefix; how the main text cites it; whether every item must be cited in the main text; limits on supplementary items; the middle tier on offer; whether references cited only in the supplement must appear in the main list; file formats; the data policy.
2. `outline.md`: the claim chain and the `## Supplement` table.
3. `brief.md`: EVIDENCE and NOT SHOWN.
4. The main text: every statement made without evidence on the page ("not shown", "as expected", "we checked that").
5. `notation.md`, `figstyle.md` and the preamble of the main text. The supplement inherits all three (Step 5).
6. `suppmap.md`, if it exists.

## Steps

### Step 1. Send each item to one of four places

Ask in this order, and stop at the first yes:

| # | Question | Place |
|---|---|---|
| 1 | Does a statement of the claim chain lose its evidence without the item? | Main text. If it is a step that only a specialist must see, the venue's middle tier. Never the supplement alone |
| 2 | Does a reader who checks or repeats the work need it, and does it need words to be understood? | Supplement, inside a section that supports one named statement |
| 3 | Can it be used as it is, with one line of description? | Data package. One sentence says where |
| 4 | None of these | Cut |

- **To the supplement**: a derivation longer than the main text can carry; a control or a robustness test with its conclusion; calibration and details of method; one further example of a point already shown.
- **To the data package**: the same plot for every sample, angle or run; the raw data behind a processed figure; a full parameter sweep; a table to look values up in; input files, parameter files and code; logs of convergence; movies, unless the venue hosts them, and then both.
- **Cut**: a result outside the claim chain ("we also measured"); material kept in case a referee asks, which belongs in the reply to referees; text moved out of the main text only to meet a length limit.
- "Not shown" does not survive this step. The sentence gets a place in the supplement or in the data package, or it goes.
- A supplement is not a way around a length limit. If text that the main text needs does not fit, use the middle tier, a longer article type or a companion paper.
- Record every decision in `suppmap.md`: one row per item with the statement it supports and the decision; one row per item that moved out, with where it went.

### Step 2. Keep it no larger than the main text

- **Ceiling: 1 to 1.** The supplement has at most as many words as the main text, and at most as many figures plus tables. Count the two separately. A ceiling is not a target: most supplements should end well below it. A stricter venue limit replaces it.
- Equations are not capped, because a derivation is what a supplement is for. A section with many equations says in its first paragraph which result it derives and where that result stands, so that a reader can skip to it.
- Over the ceiling, cut in this order: (1) move to the data package what question 3 catches; (2) merge figures that make one point into panels of one figure; (3) cut every item that no sentence cites; (4) shorten each section to question, evidence, conclusion; (5) if it is still larger than the main text, it is a second paper: propose appendices in a longer article type, or a companion article.
- Compare pages only when both files use the same layout.

### Step 3. Callouts: few, specific, placed

- **One callout per supplementary section**, at the sentence whose statement the section supports. Budget for the whole main text: the number of supplementary sections, or two callouts per 1000 words, whichever is larger, and three in any case. At most one in a paragraph. Callouts in captions count; the data availability statement does not.
- **State the result, then name the place.** The sentence of the main text carries the outcome of the check as a fact, with its number; the callout adds only where the evidence is. Check: delete the callout, and the sentence still makes its statement.
  - No: "The threshold is robust (see Supplemental Material for details)."
  - Yes: "The threshold moves by less than 5% when the damping, the mesh and the rise time are varied over the ranges given in Sec. S2."
- **Name a section or a figure**, never the supplement as a whole. The reader must land on the right page.
- **Put the callout at the end of the sentence or in parentheses.** A sentence whose subject is a supplementary figure ("Figure S3 shows ...") makes the main text depend on it.
- **None in the abstract. None in the conclusion.**
- **The supplement cites its own items.** A figure or table inside a section is cited in that section. One section may send the reader to another. Every item must be cited somewhere, and every section must be reachable: from a callout, or from a section that a callout reaches. A contents list names items; it does not cite them.
- **Where the venue requires every item to be cited in the main text**, cite the range inside the one callout: "(Sec. S2; Figs. S1 to S3 and Table S1)". One sentence, one interruption.
- **An item that the main text cites three times** is needed there. Move it to the main text as a panel, or state its content once.
- **Form** follows `venue.md`. In American Physical Society journals the supplement is an entry of the reference list ("See Supplemental Material at [URL will be inserted by publisher] for ...") and each callout cites it: "Sec. S1 of the Supplemental Material [31]". In Nature-family journals: "(Supplementary Fig. 1)", "(Supplementary Note 2)".

### Step 4. Build it so that it is cheap to use

- **Title page.** The venue's name for the supplement, then "for:" and the title of the paper, then the authors as in the main text. A file read alone must name its paper.
- **Contents**, one line per section, when there are more than about five sections or 3000 words.
- **Order.** Sections in the order in which the main text first points to them. Figures and tables numbered in the order of their first citation in the supplement.
- **One question per section, answered in its first paragraph.** Two sentences open every section: which statement, figure or equation of the main text it supports, and the answer. "The main text states that the threshold of Fig. 3 moves by less than 5% when numerical and material parameters are varied. This section gives the evidence. The largest change is 4.6%." A reader who accepts the answer stops there. Method and evidence follow, and nothing that does not bear on the statement.
- **Sections, not a pile of figures.** A figure that no paragraph uses is data. A supplement of fifteen figures and no text forces fifteen callouts; grouped into four sections it needs four.
- **No new claims.** The supplement holds no result that the main text does not state, and no discussion of side findings. A result that matters is in the main text.
- **Self-contained items.** Captions follow `parts/captions.md`. Symbols are those of `notation.md`. An abbreviation is defined again at its first use here, because this file is opened in the middle.
- **One file.** Text, figures and tables in one PDF; each figure in the section that uses it, with its caption on the same page; pages numbered. File names say what the file is.
- **References** follow the venue's rule. Citations made only in a supplement are often not indexed; a work that deserves credit is cited in the main text.

### Step 5. One paper, one style

The supplement takes its rules from files that already exist. Do not restate them; apply them.

| From | The supplement takes | Check |
|---|---|---|
| the preamble of the main text | macros, packages, the way units are typeset: one file that both sources `\input` | `supp_check.py` |
| `notation.md` | symbols, units, names of quantities | checks of `parts/notation.md` on both files |
| `figstyle.md` | colours, markers, line styles, fonts, sizes; one colour, one meaning across all figures of the paper | `fig_lint.py make_fig*.py make_figS*.py --style figstyle.md`, in one run |
| `parts/captions.md` | the structure of a caption | `caption_check.py main.tex supplement.tex` |
| `parts/equations.md` | numbering, punctuation, citation form | `eq_refs.py main.tex supplement.tex` |
| `venue.md` | "Fig." or "Figure", "Eq. (S3)", the prefix | `supp_check.py` |
| the prose of the main text | tense, person, terms, sentence limits | read the two side by side |

- **Prefix.** Sections, figures, tables and equations are numbered S1, S2, ..., or in the venue's form. "Fig. 1" must never mean two figures.
- **Figures at final size**, with the lettering of the main figures. A supplementary figure is not a smaller or rougher figure.
- **Cross-references by label**, not by typed numbers:

```latex
% shared.tex: packages (among them xr), macros, units; \input by both files
% main.tex
\input{shared}
\externaldocument[S-]{supplement}      % \ref{S-sec:robust} prints S2
% supplement.tex
\input{shared}
\externaldocument[M-]{main}            % \ref{M-eq:threshold} prints 1
\renewcommand{\thesection}{S\arabic{section}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\theequation}{S\arabic{equation}}
```

  Compile supplement, main, supplement, main: each file reads the other's `.aux`. If the venue compiles the sources itself and does not support `xr`, replace the cross-file references by the printed numbers as the last step before submission, and run the checks once more.

### Step 6. The data package

- **A repository that issues a persistent identifier** (Zenodo, Figshare, Dryad, a repository of the field or the institution). "Available on request" is not a deposit: requests are often not answered, and data kept by authors are lost with time. Where sharing is restricted, the statement says what is restricted and why.
- **Contents**: a README; one folder per figure of the paper and the supplement, with the plotted numbers in an open format and the script that draws the figure; the raw data or output behind processed figures; input files, parameters, and the code or its version; everything that Step 1 sent here.
- **README**: what each folder holds; formats, units and column names; software and versions; how to reproduce one figure and repeat one run; what is absent and why; licence; how to cite. Template: `examples/supplement/data/README.md`.
- **Pointers are exact.** The supplement names the folder ("folder `sweep/` of the data package"). The data availability statement names the repository and the identifier, and says in one clause what is there. The authors word it; `parts/submit.md` checks that it is in place.
- Deposit before submission, so that referees can see what the manuscript points to.

### Step 7. Check

```
python scripts/supp_check.py main.tex --supp supplement.tex --ledger suppmap.md
python scripts/supp_check.py paper.tex              # both parts in one file: the split is found and reported
```

It reads the LaTeX sources and reports errors, warnings and notes:

| Group | Reported |
|---|---|
| Size | words, figures and tables, equations and pages of both parts, with ratios. Warning above `--ratio` (default 1) |
| Callouts | every sentence with its place and its target. Error: a callout in the abstract, or to an item that does not exist. Warning: more callouts than the budget (`--per-1000`, default 2); more than `--per-paragraph` (default 1) in a paragraph; a callout in the conclusion; a callout that says neither what nor where; a main text that cites the supplement only as a whole |
| Items | where each section, figure and table is cited. Error: an item cited nowhere. Warning: a section that cannot be reached; sections out of the order of their callouts |
| Data | notes on candidates for the data package: a table of more than 25 rows, a figure of nine or more images, a run of figures with nearly the same caption, a caption that says "raw" or "all samples", a listing |
| Style | Warning: macros defined differently in the two files; "Fig." against "Figure"; a missing prefix; a float without caption. Note: a section whose first paragraph does not name what it supports; a supplement without the paper's title; works cited only in the supplement; a data availability statement that is missing or offers data on request only |

Errors must be fixed. Warnings are fixed or answered in `suppmap.md`. Notes are for judgment. `--ledger suppmap.md` writes the tables of items and callouts for Step 1; an existing file is left alone unless `--force` is given. The script lists what to judge; whether a control is needed, and whether a callout is worth its interruption, it cannot say.

Then run the checks of Step 5 over both files, and do the reading test: open the supplement at the target of each callout, as a reader would. Does the first paragraph say what is answered, and can you return to the main text after it?

### When rules pull in different directions

The venue's rule first (name, numbering, required citations, limits). Then the main text stands alone: never thin its evidence to save a callout or to meet a budget. Then few callouts, then the size ceiling, then completeness of the supplement. A referee's explicit request outranks the budgets: add the item, and cut elsewhere or deposit as data.

## Checks

1. **Stands alone**: every statement of the claim chain has its evidence in the main text or the middle tier; no statement rests on the supplement.
2. **Allocation**: every item has a row in `suppmap.md` with the statement it supports and a decision; nothing is kept "in case".
3. **Data**: nothing that can be used without explanation takes a page; each such item is in the data package, and one sentence says where.
4. **Size**: the supplement does not exceed the main text in words or in display items, or meets the venue's limit.
5. **Callouts, number**: within the budget; at most one in a paragraph.
6. **Callouts, content**: each states its result in the main text and names a section or figure; none is vague.
7. **Callouts, place**: none in the abstract or the conclusion.
8. **Reach**: every item is cited; every section is reached; no callout points to an item that does not exist.
9. **Order**: sections follow the order of their callouts; items are numbered in the order of first citation.
10. **Openers**: the first paragraph of each section names what it supports and gives the answer.
11. **No new claims** in the supplement.
12. **Style**: one preamble; notation, units, citation forms, figure style and caption form as in the main text; the prefix on sections, figures, tables and equations; all references resolve.
13. **Identity**: the title names the paper; authors are given; contents when long.
14. **References**: handled by the venue's rule.
15. **Data availability**: a repository with a persistent identifier, a README, and a statement that names both.

## Report

Reply in the user's language; write the supplement in the manuscript's language. Keep it short:

1. **Allocation**: each item, its place, and the reason, from `suppmap.md`; what moved to the data package and what is proposed for cutting.
2. **Size**: words and display items of both parts, the ratios, and what was done to meet the ceiling.
3. **Callouts**: the list with place and target, against the budget.
4. **Check**: errors and warnings of `supp_check.py` that remain, each with its fix or its answer.
5. **Flags**: an item the user must decide on; a supplement that is a second paper; data that cannot be deposited.

In Audit mode, replace items 1 to 3 with the table of the fifteen checks and the smallest fix for each failure.

Propose only. Moving an item between main text, supplement and data package changes `outline.md`: report the move there. Delete nothing of the user's material; list what is proposed for cutting.

## Example (invented; the physics and the numbers are placeholders)

Files: `examples/supplement/` holds `main.tex`, `supplement.tex`, the shared preamble, the filled-in `suppmap.md` and the README of the data package.

Before, in the main text:

> The threshold is robust against the damping constant (Fig. S3), the cell size (Fig. S4), the rise time (Fig. S5) and the film thickness (Fig. S6); see Supplemental Material for details. Snapshots of the reversal are shown in Fig. S7, and the time traces for all tilt angles in Figs. S8 to S11. The effect of temperature is discussed in Supplementary Note 3.

Fails: three callout sentences in one paragraph, to nine figures; "robust" without a number, so the main text does not make its statement; one callout that says neither what nor where; four figures that are the same plot repeated; two names for one supplement; a supplement of eleven figures against three in the main text.

After, in the main text (two sentences in two paragraphs, one callout each):

> The threshold moves by less than 5% when the damping, the mesh and the rise time of the pulse are varied over the ranges given in Sec. S2.
>
> At 300 K thermal fluctuations broaden the transition from no reversal to reversal over about 8% of the threshold current, and they do not shift its centre (Fig. S2).

After, the opening of Sec. S2:

> The main text states that the threshold of Fig. 3 moves by less than 5% when numerical and material parameters are varied. This section gives the evidence. The largest change is 4.6%.

Allocation: the derivation of Eq. (1), the robustness test and the effect of temperature stay as three sections with two figures and one table. The time traces, the plots against five further parameters, the table of all 212 runs and the input file go to the data package; each parameter keeps one row of Table S1. Snapshots and a side result on pulse shape are cut. Result of `supp_check.py`: 613 words against 366 (0.60), three display items against three (1.00), three callouts against a budget of three, all six items reached, no error and no warning.

## Relation to other parts

- **Outline** (`parts/outline.md`) allocates whole items by the deletion test. This part decides between supplement, data package and cut, and reports every move back.
- **Figures** (`parts/figures.md`) moves panels by the same test; supplementary figures are drawn from the same `figstyle.md` and linted in the same run.
- **Captions, equations, notation** apply unchanged; `eq_refs.py` resolves references between the two files through the `xr` prefixes.
- **Bibliography** (`parts/bibliography.md`): the venue's rule for works cited only in the supplement; `ref_check.py` runs on both files.
- **Methods**: what a specialist must read to believe the result belongs in Methods or the middle tier; what a checker may want belongs here.
- **Venue** (`parts/venue.md`) supplies the name, the prefix, the citation form and the limits.
- **Audit** (`parts/audit.md`) reruns checks 1, 4 to 8 and 12 on the finished manuscript. **Submit** (`parts/submit.md`) handles file formats and the description that some venues require with the deposit.

## What this part cannot do

- It cannot decide whether a control is needed. That is a judgment of the field, and of the referees.
- The ceiling of 1 to 1 and the callout budget are choices of this skill. Journals have capped supplementary figures at the number of main figures; no study has measured a best ratio.
- `supp_check.py` reads LaTeX source only. It does not expand macros, counts words approximately, and numbers items in the order of their appearance. Extended Data and Methods kept in the main file count as main text. For a manuscript in a word processor, apply the checks by hand.

## Sources

The journal rules and studies behind these choices, the measurements made with the script, and the points on which venues differ are in `references/supplement-evidence.md`; read it when you need to explain a choice.
