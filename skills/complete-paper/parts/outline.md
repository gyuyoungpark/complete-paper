# Outline

Stage A · Reads: `brief.md`, `venue.md`, any existing draft, figures and notes · Writes: `paper-state/outline.md`

An outline is the paper's argument laid out before any prose exists: one central claim, the few statements that establish it, the figure or table that supports each statement, and the order in which a reader meets them. It is a plan of evidence, not a list of section headings.

The outline is where a paper is won or lost cheaply. Reordering six sentences takes minutes; reordering six finished sections takes days. So the rule of this part is: **agree on the claims and their evidence first, and write no paragraph until the outline passes its tests.**

Order of work: claim sentences, then figure specifications, then the paragraph plan. Figures are specified here and drawn later; they are polished only after the Results draft exists, because panels move when the text is written.

## Modes

- **Write** (plan): build `outline.md` from `brief.md` and the available evidence.
- **Revise** (restructure): a draft exists. Reverse-outline it first (its actual central claim, the point of each paragraph, the message of each figure), compare that with the rules below, and propose the new order as a list of moves.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read before planning:

1. `brief.md`: RESULT, SYSTEM, METHOD, EVIDENCE, NOT SHOWN, and the inventory of data, figures and derivations that exist.
2. `venue.md`: article type, length limit and how it is counted, limits on display items, whether section headings are allowed, where Methods go.
3. Any existing draft, figures and notes.

Do not wait for the data to be complete. An outline made early shows which evidence is missing, and that list is one of its outputs.

## Steps

### Step 1. State the central claim

One sentence that a reader could repeat a year later. It must match RESULT in `brief.md` and stay inside NOT SHOWN.

- If the sentence needs "and" to join two findings, there are two papers or a missing link. A paper with two facets (a new method and a result obtained with it, say) is acceptable only when one sentence states the bridge between them.
- Test: can the paper be described to a colleague in a few sentences? Write those sentences. If that is hard, the outline is not ready.

### Step 2. Build the claim chain

Write the three to six statements that, taken together, establish the central claim.

- **Declarative.** Each is a full statement of a finding ("Reversal time falls with tilt angle"), not a topic ("Dependence on tilt angle") and not an activity ("Measurement of reversal time").
- **Necessary.** Remove the statement; if the central claim still stands, the statement belongs in the supplement or nowhere.
- **Ordered by logic, not by history.** The order in which the work was done is almost never the order in which it convinces. Put first what the reader needs first.
- **One place per subject.** A subject treated in two separate places forces the reader to carry it across the gap.

### Step 3. Assign roles and evidence

Every statement in the chain gets a role and one display item (a figure or a table), or is marked "text only". Define display items by role, not by number, so that the plan survives when the count changes.

| Role | What the item does |
|---|---|
| Orient | Shows the system, geometry or setup the reader needs in order to read everything else |
| Establish | Gives the direct evidence for the central claim |
| Discriminate | Rules out the leading alternative explanation (a control, a term switched on and off) |
| Generalize | Shows how far the claim extends: dependence on a control parameter, scaling, a phase diagram, a testable prediction |
| Benchmark | Compares with prior methods, devices or results |
| Synthesize | Gathers the findings into one picture or model |
| Limit | Shows where the result or method stops working; placed in the Results, the one place where limitations appear (ground rule 10 in `SKILL.md`) |

- **Exactly one item has the role Establish.** It gets the most space and appears no later than the second display item.
- **One item, one message.** An item carrying two unrelated statements is split; a statement spread over two items is merged.
- **An Orient item is compact.** Under space pressure it is the first to shrink: one schematic panel beside the first evidence usually does the work of a full figure.
- **Prefer Discriminate to more examples.** A further case that agrees adds less than a control that removes the competing explanation.
- **The last item is a strong place for Generalize or Synthesize**: what the result covers, or how the pieces fit.
- **Bridge.** In a two-facet paper, one panel must show the link itself: the validated output of the method as the input of the result.
- **Evidence status.** For each statement record what supports it and whether that evidence exists, is partial, or is missing. Never fill a gap with an assumed result; list it under "Holes".

Starting patterns by type of paper. These are a synthesis for orientation, not rules from any guideline; adapt them to the claim chain.

| Type of paper | Typical sequence of roles |
|---|---|
| Discovery (letter) | Orient with Establish; Generalize (control parameter); Discriminate; Synthesize or Generalize (phase diagram, model) |
| Mechanism (simulation or theory explaining an observation) | Orient (what existing models fail to explain); Establish (the proposed model reproduces it); Discriminate (terms on and off); Generalize (testable prediction) |
| Theory or proposal | Orient (setup); Establish (analytic result against numerics); Generalize (parameter space); Generalize (experimental signature and conditions) |
| Method, code or algorithm | Orient (pipeline); Establish (validation on a problem with a known answer); Benchmark (against baselines, scaling); Generalize with Limit (a new problem; where it fails) |
| Device or application | Orient (structure and principle); Establish (key characteristic); Generalize (reliability, variation, scaling); Benchmark (state of the art) |
| Machine learning or benchmark | Orient with Establish (first-page figure); Orient (method diagram); Establish (main result); Discriminate with Limit (ablations, failure cases) |

### Step 4. Fit the venue

Display items are not free. Take the limits and the counting method from `venue.md`.

- Where the venue counts figures and equations as words, compute their cost before budgeting text. Example (APS length guide, checked November 2026): a single-column figure costs 150 divided by its aspect ratio (width over height) plus 20 words, a double-column figure 300 divided by half its aspect ratio plus 40 words, and displayed mathematics 16 words per single-column row. A square single-column figure is therefore 170 words out of a 3750-word Letter, and a double-column figure twice as wide as it is tall is 340.
- When the plan exceeds the limit, in this order: merge items that serve the same statement; shrink the Orient item to a panel; move to the supplement every item that fails the deletion test (delete it: does any statement of the chain lose its support?); only then cut text.
- Split the remaining words across sections. A workable default, to be adjusted: about 20% introduction, 60% results with the methods that must stay in the main text, 20% discussion and conclusion.

### Step 5. Specify each display item

Write a specification, not a drawing. The figures and captions parts work from it.

```
Fig. 2 | Role: Establish | Width: single column | Cost: 170 words
Title (the conclusion, as a sentence): Spin-orbit torque alone reverses the octupole order
Panels, in reading order:
  (a) what is plotted against what; which curves are compared
  (b) ...
Takeaway in one sentence:
Evidence: dataset or file; status (exists / partial / missing)
```

- The title here is a planning title: it states the conclusion the item must support. Whether the published caption carries a declarative title or a descriptive one is decided in `parts/captions.md`.
- An expert should get the main message from the item and its caption without the main text.
- Panels follow the reading order of the argument, and every panel serves the item's one message.

### Step 6. Plan the sections

Follow the structure the venue requires. Within it:

- **Same order everywhere.** The preview at the end of the introduction, the Results, the Discussion and the Methods take up the statements in the order of the claim chain.
- **Headings that state findings.** Where the venue allows subsection headings in Results, use the chain's statements in short form: "Reversal time falls with tilt angle", not "Tilt-angle dependence".
- **One informal sentence per planned paragraph**, each with its role in the story:
  - Introduction: the field-level context; the specific gap; a brief preview of the results that close it. In a letter the first paragraph already tells the central story and why it matters.
  - Results: an opening paragraph on the overall approach; then, per statement, paragraphs that pose a question, present data and reasoning, and answer it. Each limitation is stated here once, where the evidence it qualifies is presented.
  - Discussion: a first paragraph that summarizes the findings; strengths and relation to earlier work, framed by what this work adds; a close on what the paper changes. A conclusion that only repeats the results is dropped.
  - Methods and supplement: what a specialist needs in order to check or reproduce the work. Technical detail that the science needs but the story does not goes here.
- **Supplement plan.** List each supplementary item with the statement it supports. The main text must carry the evidence for every statement of the chain on its own. Plan the supplement no larger than the main text; `parts/supplement.md` sets the budgets.

### Step 7. Write `outline.md`

Keep it in `paper-state/`:

```
# Outline: <working title>
Venue: <journal, article type>   Limit: <value and counting method>

## Central claim
<one sentence>
Told in a few sentences: <three to five sentences>

## Claim chain
| # | Statement | Role | Display item | Evidence | Status |
|---|---|---|---|---|---|

## Display items
<one specification per item, in order>

## Budget
| Item | Words |   (display items, displayed mathematics, each section, total against the limit)

## Section plan
<section; then one sentence per paragraph>

## Supplement
| Item | Supports statement # |

## Holes
<statements whose evidence is partial or missing, and what would close each one>
```

### When rules pull in different directions

Truth first (no statement without evidence), then the venue's limits, then the logic of the chain, then economy of display items, then the starting patterns.

## Checks

1. **Central claim**: one sentence; matches `brief.md`; no second claim hidden behind "and"; a two-facet paper states its bridge.
2. **Chain**: three to six declarative statements; each necessary; ordered by logic, not by the history of the work.
3. **Evidence**: every statement has evidence and a status; nothing reaches beyond NOT SHOWN; holes are listed, not filled.
4. **Roles**: exactly one Establish, by the second display item and with the most space; the leading alternative explanation is addressed by a Discriminate item or in the text.
5. **One message**: no item carries two unrelated statements; no statement is split across items.
6. **Titles**: read in order, the display-item titles give the argument of the abstract.
7. **Deletion**: every main-text item, if deleted, takes a statement's support with it; the others are in the supplement.
8. **Coverage**: every key result intended for the abstract appears in a display item or is marked "text only"; no display item supports a statement absent from the chain.
9. **Stand-alone**: each specification can be understood with its caption alone.
10. **Budget**: display items within the venue's cap; total within the limit by the venue's own counting.
11. **Parallel order**: introduction preview, Results, Discussion and Methods follow the chain's order.
12. **Paragraph plan**: one sentence per paragraph, each with a role; no chronological narration.

## Report

Reply in the user's language. Keep it short:

1. **Central claim** and the few-sentence telling.
2. **Claim chain** table.
3. **Display items**: role, title and cost of each; what moved to the supplement and why.
4. **Budget** against the limit.
5. **Holes**: missing or partial evidence and what would close it; statements the user must confirm.
6. `outline.md` in full when asked, and in Revise (restructure) mode the list of moves from the current draft.

Propose only. The user approves the outline before any section is written; expect several rounds. If the user and the outline disagree, change the outline, not the prose.

## Relation to other parts

- **Brief** (`parts/brief.md`) supplies the central claim and the evidence inventory; the outline never widens it.
- **Figures, tables and captions** draw and describe what the specifications define; composition is decided here, style there.
- **Abstract and title** take the central claim and the chain; check 6 ties the figure titles to the abstract.
- **Supplement** (`parts/supplement.md`) receives the items that fail the deletion test, each tied to a statement. It then decides between supplement, data package and cut, and reports every move back here.
- **Audit** repeats checks 5 to 8 and 11 on the finished manuscript by reverse-outlining it.

## Sources

The sources behind these rules, the points on which they disagree, and what is this skill's own synthesis are in `references/outline-evidence.md`; read it when you need to explain a choice.
