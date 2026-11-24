# Captions

Stage B · Reads: the figures and tables, `outline.md`, `notation.md`, `venue.md`, the paragraph that first cites each figure · Writes: figure and table captions

A caption gives the reader everything needed to read the figure and nothing about what to conclude from it. **The caption says what is shown; the main text says what it means.**

It has two jobs that pull against each other. It must **stand alone**: figure and caption together are understood without the main text, because figures are skimmed first, reused in talks, and extracted from papers on their own. And it must **stay lean**: explanation, trends and significance appear once, in the text, not a second time under the figure.

The rule that reconciles the two: **say what is compared, never how the comparison comes out.**

## Modes

- **Write**: a figure exists, or is specified, and has no caption.
- **Revise**: a caption exists; add what is missing for it to stand alone and move commentary to the text.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read before writing:

1. **The figure itself**: the image, or the script and data that produce it. Write from what is actually on the figure, not from the plan. If the figure cannot be inspected, say so and write from the specification, flagged as unchecked.
2. `outline.md`: the figure's role, panels and takeaway. The takeaway is for the main text.
3. `notation.md`: symbols, units and terms.
4. `venue.md`: label format ("FIG. 1.", "Fig. 1 |", "Figure 1."), panel labels, word cap, whether titles are descriptive or declarative in this venue, where statistics and methods details go, credit lines.
5. The paragraph of the main text that first cites the figure.

## Steps

### Step 1. Take inventory

List every element on the figure, panel by panel:

- axes: quantity, symbol, unit, and scale if not linear;
- every curve, marker, colour, line style and shaded region;
- colour scales, insets, arrows, guide lines, annotations, scale bars;
- error bars and what they represent;
- abbreviations and symbols printed anywhere on the figure;
- the kind of data: measured, simulated, calculated, or taken from other work.

For each element decide where the reader learns what it is: on the figure (an axis label that names the quantity, a legend key) or in the caption. **Anything not explained on the figure must be explained in the caption.** Nothing may be left to the main text.

### Step 2. Build the caption

Write the parts in this order.

1. **Label**, in the venue's format.
2. **Title**: one line for the whole figure, naming the quantity, the system and the comparison or the variable. "Spin-orbit-torque switching of a Mn3Sn film for several tilt angles of the kagome plane", not "Simulation results".
3. **Panels**, in order, each introduced by its label exactly as printed on the figure: what is plotted against what, and which curves or markers are which.
4. **Symbols and abbreviations**: every one that appears on the figure or in the caption and is not spelled out on the figure, **even if the main text defines it**. Use the names in `notation.md`.
5. **Conditions**: the fixed quantities a reader needs in order to read the data (temperature, field, sample or geometry, model parameters), with values and units.
6. **Marks and statistics**: what error bars are and from how many samples; what lines are (a fit, and to which equation; a guide to the eye); the length of scale bars; the meaning of colour scales and insets.
7. **Source and credit**: data taken from other work carry the reference. A reproduced or adapted figure carries the reference and the permission line the venue requires.

Shared information is given once: "Symbols show the simulation and lines Eq. (4). Colours are as in (a)." Keep captions in plain sentences, without colons or semicolons (ground rule 14 in `SKILL.md`).

### Step 3. Keep out

The following belong to the main text, not the caption:

- **Trends**: "increases with", "decreases", "saturates", "scales as".
- **Outcomes of comparisons**: "agrees well with", "is larger than", "outperforms".
- **Interpretation**: "indicating", "suggesting", "demonstrating", "confirming", "due to", "because".
- **Evaluation**: "clearly", "remarkably", "as expected", "excellent".
- **Significance and implications** of the result.
- **Procedure**: how the measurement or simulation was done, where the paper has a Methods section. A condition needed to read the data is not procedure.
- **Filler openers**: "This figure shows", "Plot of". Start with the content.
- **Restating the obvious**: an axis that already says "Time (ns)" needs no sentence.

Three things look like interpretation but are description, and stay in:

- **Identifying a mark**: "Arrows mark the switching fields." "The dashed line marks the Neel temperature."
- **Naming what a line is**: "Solid line: fit to Eq. (3)."
- **Explaining a schematic**: what each drawn element represents.

**Declarative titles.** Some venues and some schools of advice use a title that states the finding ("Tilting the kagome plane lowers the switching threshold"). Use one only when `venue.md` records that the venue's captions do so, or when the user asks. It is then a single sentence that can be read directly off the figure, and the rest of the caption stays descriptive. The default is a descriptive title.

### Step 4. Form and length

- One paragraph. The title may be a phrase where the venue's captions use phrases; the rest is in sentences or the compact "label: meaning" form. Present tense.
- **Compact.** Aim for about 30 to 80 words for a single panel and up to about 150 for a figure with several panels. Stay under the venue's cap (Nature, for example, asks for fewer than 300 words per legend). Where captions count toward the length limit, every sentence must earn its place.
- Test each sentence: is it needed to read the figure? If not, delete it or move it to the text.
- **Not by colour alone.** Identify curves by line style or marker as well as colour ("solid red line", "open circles"), so the caption works in greyscale and for readers who do not distinguish the colours.
- **Same symbols, units and terms** as on the figure and in the text. Panel labels in the caption match the figure exactly: "(a)" where the figure prints "(a)".
- Abbreviations are defined in the caption independently of the text.
- Supplementary figures follow the same rules and need them more: they are read with even less context.
- Table captions: a short title above the table; symbols and abbreviations defined in the caption or in footnotes below; units in the column headings. When every column shares one unit, the caption states it once. When a column is too narrow for a name, the caption names each symbol and gives its unit. Details are in `parts/tables.md`.

### Step 5. Hand the meaning to the text

Because the caption carries no interpretation, check that the text does. For each figure, find the sentence in the main text, where the figure is first cited, that states its takeaway from `outline.md`. If there is none, report it: a figure whose meaning is stated nowhere is worse than a caption that says too much.

### When rules pull in different directions

The venue's requirements first, then stand-alone completeness, then description only, then brevity. A caption is shortened by removing commentary and repetition, never by leaving an element of the figure unexplained.

## Checks

1. **Stand-alone**: from figure and caption alone, a reader in the field can say what each panel plots, what every curve, marker and colour is, and under which conditions.
2. **Inventory**: every element of the figure is explained on the figure or in the caption; none is left to the main text.
3. **Symbols**: every symbol and abbreviation is defined on the figure or in the caption, and matches `notation.md`.
4. **Description only**: no trend, outcome, interpretation or evaluation; the exceptions are the three listed in Step 3 and a declarative title where the venue uses one.
5. **Title**: names the quantity, the system and the comparison; covers the whole figure; not generic.
6. **Panels**: each described, in order, with labels as printed.
7. **Data**: measured, simulated or calculated is stated; external data and reproduced figures carry their reference and credit.
8. **Marks**: error bars, fits, guide lines, scale bars, colour scales and insets are defined.
9. **Economy**: no procedure, no filler, no restating of plain axis labels; within the cap; counted, not estimated.
10. **Colour**: no element is identified by colour alone.
11. **Consistency**: units, terms and numbering agree with the figure and the text; figures are cited in the text in numerical order.
12. **Hand-off**: each figure's takeaway is stated in the main text where the figure is first cited.

`python scripts/caption_check.py main.tex` counts the words of every caption and lists words from the watch-list of Step 3 for review.

## Report

Reply in the user's language; write captions in the manuscript's language. Keep it short:

1. **The captions**, each with its word count.
2. **Moved to the text**: every sentence of commentary removed from a caption, with the place in the text where it belongs or already is.
3. **Missing from the text**: figures whose takeaway is not stated in the main text.
4. **Changes needed on the figure**: unlabeled axes, missing units, elements distinguished by colour only, symbols that differ from `notation.md`.
5. **Flags**: figures that could not be inspected, credit lines that need permission, unchecked venue rules.

Propose only. Edit the manuscript when the user asks.

## Example (invented)

Before:

> FIG. 2. Simulation results. The reversal time clearly decreases with increasing tilt angle, demonstrating that crystal orientation enables field-free switching. The threshold current agrees well with the model.

Fails: generic title; no panel is described; no symbol is defined; a trend ("decreases"), an evaluation ("clearly"), an interpretation ("demonstrating"), and the outcome of a comparison ("agrees well").

After:

> FIG. 2. Spin-orbit-torque switching of a single-domain Mn3Sn film for several tilt angles of the kagome plane. (a) Octupole component m_z as a function of time t after the current is applied, for tilt angles theta = 0, 15, 30 and 45 degrees (solid, dashed, dotted and dash-dotted lines). (b) Threshold current density j_c as a function of theta. Circles show the atomistic spin-dynamics simulation and the solid line the analytical model, Eq. (4). The damping constant is alpha = 0.003 in both panels.

Moved to the text: "The reversal time decreases with increasing tilt angle [Fig. 2(a)], and the threshold current follows the analytical model [Fig. 2(b)]."

## Relation to other parts

- **Outline** (`parts/outline.md`) decides what each figure is for. Its planning title states the conclusion; the published caption follows the rules here.
- **Figures** (`parts/figures.md`) draws the figure. Problems found on the figure during inventory are reported, not patched in the caption.
- **Notation** (`parts/notation.md`) supplies symbols and units.
- **Results**: carries the trends, the comparisons and their meaning.
- **Audit** (`parts/audit.md`) repeats checks 2, 3, 11 and 12 on the finished manuscript.

## Sources

The journal rules and reader studies behind these choices, including the evidence that argues for stating a takeaway, are in `references/captions-evidence.md`; read it when you need to explain a choice.
