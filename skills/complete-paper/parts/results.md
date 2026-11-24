# Results

Stage B · Reads: `brief.md`, `outline.md`, `notation.md`, `venue.md`, the figures, tables and captions, the methods draft · Writes: the results section

The results present the evidence for each statement of the claim chain, in the chain's order. A reader should be able to follow them with the figures alone beside the text, and should never have to work out which point a paragraph is making.

They have two jobs:

- **Each paragraph establishes one statement.** It says what is found, shows where, gives the number, and says what the finding means for the claim.
- **The evidence is separable from its reading.** What was observed and what is inferred from it are told apart by the words used.

The common failure is the tour: "Figure 2 shows ... Figure 3 shows ...", a description of the figures in order, with the findings left for the reader to extract. The remedy is fixed by the outline: the paragraphs follow the statements, not the figures, and each opens with its finding.

## Modes

- **Write**: no results section yet.
- **Revise**: a draft exists; map each paragraph to a statement first, then rewrite the openers.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

1. `outline.md`: the claim chain, the display items with their roles, and the paragraph plan. This part executes that plan; it does not make a new one.
2. `brief.md`: RESULT, EVIDENCE, NOT SHOWN, and the table of key numbers.
3. The figures, tables and their captions as they now stand.
4. The methods draft: its definitions of the plotted quantities.
5. `venue.md`: whether Results and Discussion are separate, whether subheadings are allowed and how long they may be, the citation forms.
6. `notation.md`.

Write the Results after the figures exist and before the Discussion, the Conclusion, the Introduction and the Abstract.

## Steps

### Step 1. Follow the chain

- One subsection or group of paragraphs per statement of the claim chain, in the chain's order.
- **Open with the approach** in one short paragraph when the paper has more than two statements: what was varied, what was measured or computed, and in what order the results come. No results in it.
- A statement with no paragraph is a hole: report it to the outline. A paragraph with no statement is a result outside the claim: move it to the supplement or cut it (`parts/supplement.md`).
- When writing shows that the chain is in the wrong order, change `outline.md` first.

### Step 2. Build each paragraph from five moves

| # | Move | Content | Length |
|---|---|---|---|
| 1 | Purpose | Why this step is taken: the part of the claim it tests | the opening clause ("To test ...,") |
| 2 | Basis | What we did to obtain it, as far as needed to read the figure | the rest of the first sentence, or one sentence |
| 3 | Finding | The statement this paragraph establishes, as a fact | the next sentence, at the latest the second of the paragraph |
| 4 | Evidence | What the figure or table shows: the observation, with numbers | one to three sentences |
| 5 | Meaning | What follows for the claim, or what it rules out; the link to the next statement | one sentence |

- **Purpose, then the finding at once.** "To test the torque balance, we compare it with the simulated threshold (Fig. 3). The two agree within 4% ..." The reader learns why the step was taken and what we did (ground rule 13 in `SKILL.md`), and then the finding, with the figure cited in parentheses or as support. Where the paragraph before has already given the purpose, open with the finding: "The threshold falls as the inverse sine of the tilt angle (Fig. 3)."
- **No tour.** A paragraph that opens "Figure 3 shows the threshold as a function of tilt angle" has spent its first sentence on what the caption already says.
- A paragraph may open by pointing at a figure in two cases: a schematic or set-up that orients the reader ("Figure 1 shows the geometry"), and a sentence that goes on to say what the figure establishes.
- **An open point may stand in for the finding** where the logic needs it, as an indirect question ("Whether the reversal survives at room temperature decides ..."), at most once or twice in a paper. The answer then closes the paragraph. No direct question (ground rule 7).
- **Meaning is local.** It ties the observation to this statement. Mechanism and comparison with earlier work belong to the Discussion, unless the venue merges the two sections. Limits do not move there. Each limitation is stated here, once (Step 4).

### Step 3. Report numbers so that they can be judged

- **Unit, uncertainty, number of repeats.** "0.22 ± 0.01 ns (64 runs)". What the uncertainty is was defined in the methods; here it is given.
- **A reference to compare with.** A number alone says little: give the baseline, the prediction, the earlier value or the control beside it. "A tilt of 30° costs twice the current of a film tilted by 90°."
- **Trend words carry numbers.** "Increases", "is suppressed", "strongly depends": by how much, over what range. "The switching time falls from 0.60 ns at 15° to 0.22 ns at 45°."
- **Key numbers as in `brief.md`**: the same value, the same rounding, everywhere.
- **Significant figures** match the uncertainty. Do not quote 0.2237 ns with an uncertainty of 0.01.
- **"Significant"** only with a test or a stated criterion; otherwise "large", with the number.
- **Agreement is quantified**: "agree within 4% between 5° and 45°", not "good agreement".

### Step 4. Keep observation and inference apart

| What is being reported | Words |
|---|---|
| Seen directly in the data | is, falls, reverses, crosses, we observe / find / measure (by kind of evidence, table in `parts/abstract.md`) |
| Derived by a stated analysis | we obtain, the fit gives, we extract |
| Inferred | indicates, is consistent with, implies, we attribute ... to |
| Not established | may, could; and then say what would decide it |

- One hedge per inference. "May possibly suggest" hides whether anything was shown.
- "Consistent with" is weaker than "shows": use it when other explanations remain, and name the main one in the Discussion.
- An observation that limits the claim is reported with the same weight as one that supports it. A null result that bounds the effect is a result.
- **Each limitation once, here.** The Results are the one place in the paper where a limitation is stated: beside the evidence it bounds, as a plain fact about that evidence, and not again in any other section (ground rule 10). Scope words that make the claim exact ("in simulations", "in single-domain films") are not limitations and stay with the claim wherever it appears.
- No evaluation in place of evidence: "clearly", "obviously", "remarkably", "interestingly" are removed; if the point is clear, the number shows it.

### Step 5. Cite display items so that none is orphaned

- Every figure, table and panel is cited by a sentence that uses it, and first citations run in numerical order.
- Cite the panel: "Fig. 2(b)", in the venue's form. A panel that no sentence cites goes to the supplement or out (`parts/figures.md`, Step 9).
- The text says what to see; the caption says what is plotted and how to read it (`parts/captions.md`). Do not repeat the caption in the text, and do not move the finding into the caption.
- Result equations are cited by number (`parts/equations.md`). Supplementary items are cited by the rules of `parts/supplement.md`: one callout per supplementary section, at the statement it supports.
- By reference, not by typed number: `\ref`, so that reordering cannot break the text.

### Step 6. Subheadings

Where the venue allows headings inside the Results:

- **A heading states a finding**, as a short phrase or sentence taken from the claim chain: "Reversal time falls with tilt angle", not "Tilt-angle dependence".
- One heading per statement; parallel in form; in the chain's order. Read in sequence, the headings give the argument of the abstract.
- Within the venue's length. No abbreviation that the heading does not define, no symbol that needs a definition, no citation.
- Capitalization and numbering as `venue.md` gives them.

Where the venue discourages freestanding headings, as letter journals do, the first sentence of each paragraph does this work, and run-in headings follow the venue's form.

### Step 7. Tense and person

- Past for what was done and observed in this work ("we varied", "the moment reversed"). Present for what a figure shows, for what holds in general, and for the model ("Fig. 2 shows", "the threshold diverges at zero tilt").
- "We" and an active verb for choices and actions of the authors (ground rule 11); the finding itself as the subject where possible. Three sentences in a row that begin with "We" read as a list of activities.

### Step 8. Check

```
python scripts/cite_order.py main.tex
```

It prints, for every figure and table, where it is first cited, how often, and which panels are cited; it reports uncited figures and tables (error), first citations out of order and uncited panels (warnings), and, as notes, paragraphs that open by pointing at a display item, sentences that begin with "Fig." or "Eq.", and numbers typed by hand.

Then `python scripts/audit_tex.py main.tex --checks limits,voice,punct,xrefs` lists limitation sentences outside the Results, passive voice and activity verbs for our own work, colons and semicolons in running text, and items cited out of order.

Then map the draft back: write, for each paragraph, the number of the statement it establishes. A paragraph with two numbers is split; one with none is moved or cut.

### When rules pull in different directions

Accuracy first (the verb and the number the evidence supports), then the chain's order, then purpose and finding first, then brevity. Where a venue merges Results and Discussion, each paragraph may end with its interpretation, and each limitation is still stated once, beside the evidence it bounds.

## Checks

1. **Chain**: every statement of the claim chain has its paragraphs, in order; no paragraph is outside the chain.
2. **Purpose, then finding**: each paragraph opens with its purpose and states its finding by its second sentence, or opens with the finding where the purpose is already given (or one of the two exceptions of Step 2).
3. **Five moves**: purpose, basis, finding, evidence, meaning are present; the basis is at most one sentence.
4. **Numbers**: unit, uncertainty and repeats; a reference to compare with; key numbers as in `brief.md`.
5. **Trends quantified**: no trend or agreement word without its number and range.
6. **Observation and inference**: told apart by the verbs; one hedge per inference; no evaluation words.
7. **Limits, once**: observations that bound the claim are present, each stated once, here, and nowhere else in the paper as a limitation.
8. **Display items**: every figure, table and panel cited by a sentence that uses it; first citations in order; none typed by hand.
9. **Division of labour**: no caption content repeated; no method beyond a clause; no discussion of the literature unless the venue merges the sections.
10. **Subheadings**: findings, parallel, in order, within the venue's length; or none where the venue has none.
11. **Verbs match the evidence**: as in `brief.md` and the table of `parts/abstract.md`.
12. **Agreement**: symbols and terms as in `notation.md`; definitions as in the methods.

## Report

Reply in the user's language; write the results in the manuscript's language. Keep it short:

1. **Results**, with their word count against the outline's budget.
2. **Paragraph map**: one line per paragraph with the statement it establishes and its first words.
3. **`cite_order.py`**: what it reports.
4. **Flags**: a statement whose evidence turned out weaker than the outline assumed; a number that differs from `brief.md`; a panel that no sentence needs; a result that belongs in the supplement.

In Audit mode, replace items 1 and 2 with the table of the twelve checks and the smallest fix for each failure.

Propose only. Never strengthen a verb or a number to make a paragraph read better.

## Example (invented; the physics and the numbers are placeholders)

Before:

> Figure 3 shows the threshold current density as a function of the tilt angle. As can be clearly seen, the simulation results are in good agreement with the theoretical prediction. Interestingly, the threshold increases significantly at small tilt angles.

Fails: opens with what the caption says; "clearly", "interestingly"; "good agreement" and "increases significantly" without numbers; no meaning for the claim.

After:

> To test the torque balance of Eq. (1), we compare it with the threshold found in the simulations (Fig. 3). The two agree within 4% between 5° and 45°, with no adjustable parameter. The cost of a small tilt is steep. A tilt of 30° needs twice the current of a film tilted by 90°, and a tilt of 10° needs six times that current. Tilt therefore sets the operating current, and Eq. (1) gives it before a film is grown.

Paragraph map: statement 2 of the chain; moves: purpose "To test the torque balance of Eq. (1)"; basis "we compare it with the threshold found in the simulations"; finding and evidence "The two agree within 4% ..."; numbers with a reference "twice the current of a film tilted by 90°"; meaning "Tilt therefore sets ...".

## Relation to other parts

- **Outline** (`parts/outline.md`) fixes the chain, the display items and the paragraph plan; this part reports every deviation back.
- **Figures and captions**: the figure shows, the caption explains how to read it, the text says what it establishes.
- **Methods** (`parts/methods.md`) define the plotted quantities; the Results carry one clause of method.
- **Discussion** (`parts/discussion.md`) takes mechanism and comparison with earlier work, and looks forward from the limits stated here.
- **Supplement** (`parts/supplement.md`) receives results outside the chain and sets the callouts.
- **Prose** (`parts/prose.md`) polishes sentences afterwards. **Audit** (`parts/audit.md`) reruns `cite_order.py` and compares every number with `brief.md`.

## Sources

The journal rules and sources behind these choices are in `references/body-evidence.md`; read it when you need to explain a choice.
