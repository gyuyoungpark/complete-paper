# Conclusion

Stage B · Reads: `brief.md`, `outline.md`, `venue.md`, `notation.md`, the introduction's gap sentence, the Results and Discussion drafts, the abstract and introduction if they exist · Writes: the conclusion section or closing paragraph

A conclusion tells a reader who now has the evidence what to take away: the answer to the question the introduction posed, how far that answer reaches, and what it changes.

Its difficulty is that the central claim has already appeared twice, in the abstract and at the end of the introduction. Many readers read exactly those three places and little else, so repetition among them is what they notice first. The way out is that the three statements have different jobs:

- the **abstract** promises the result to a reader deciding whether to read;
- the **introduction** argues that the question matters;
- the **conclusion** delivers the verdict to a reader who has seen the evidence: what is established and what follows.

So: **same claim, different job, no shared sentence.** The conclusion is the one place where the claim can be stated at full strength, backed by evidence the reader has just seen, and the next step named. Limitations are not repeated here: each is stated once, in the Results (ground rule 10 in `SKILL.md`).

Two requirements govern everything below. It must be **strong**: the answer first, the consequence last, nothing vague between. And it must be **short**: one paragraph in most papers.

## Modes

- **Write**: no conclusion yet.
- **Revise**: a conclusion exists; cut the recap and the repetition first, then add what is missing.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read before writing:

1. `brief.md`: RESULT, SYSTEM, EVIDENCE, NOT SHOWN.
2. `outline.md`: the central claim and the claim chain.
3. The gap sentence of the introduction, or of the outline's plan for it: the conclusion answers that question.
4. The Results and Discussion drafts.
5. `venue.md`: whether a concluding section is required, optional or unwanted, and its heading.
6. `notation.md`.
7. The abstract and introduction, if they already exist, for the duplication check.

The conclusion is written after Results and Discussion and before the introduction and abstract. Those later parts must not copy its sentences; the audit repeats the duplication check on the finished manuscript.

## Steps

### Step 1. Take the form from the venue

| Situation | Form |
|---|---|
| A concluding section is required or usual (many physics journals; a letters journal may ask for a concluding section that summarizes the results) | One paragraph with the five moves below, under the venue's heading |
| The paper ends with a Discussion and has no separate conclusion (Nature-family journals) | The final paragraph of the Discussion does this job. The Answer shrinks to a clause; Consequence and Next step carry the paragraph. A paragraph that only summarizes is cut by such venues |
| A long article with both Discussion and Conclusions | The Discussion holds interpretation and comparison with earlier work in detail. The Conclusion is the take-home: one paragraph, two at most |
| A letter without headings | The last paragraph, three or four sentences |

### Step 2. Build it from four moves

| # | Move | What it does | Sentences |
|---|---|---|---|
| 1 | Answer | States the central claim, with its scope words, as the answer to the introduction's question | 1 |
| 2 | Basis | Names the one or two findings that carry the answer, as a synthesis | 0-1 |
| 3 | Consequence | Says what the result changes or makes possible | 1 |
| 4 | Next step | Names one specific test, prediction or extension | 0-1 |

- **Answer.** Lead with it, as a finding: "We have shown that ...", or the finding itself as the subject. Give the system, the kind of evidence, and the headline number if the claim is quantitative. Keep the scope words inside the claim, as the abstract does ("by atomistic simulations", "in a single-domain film"): they make the claim exact and are not a limitation. "In this paper we have studied ..." reports an activity, not a conclusion. Do not reopen the background. Use new wording, not the abstract's sentence.
- **Basis.** A synthesis that needed the results: how the findings combine to support the answer ("Together, ..."). Never a tour of the sections ("In Sec. II we ..., in Sec. III we ..."), and never a list of everything done. Omit it in a letter.
- **Consequence.** What can now be calculated, built, decided or reinterpreted, in specific terms. Check: could a reader have understood this sentence before reading the paper? If so, it adds nothing; rewrite it with what the paper found, or cut it. The introduction said what closing the gap would allow; this sentence says what this result now allows.
- **Next step.** Include it only if it is specific: a named measurement, a parameter range, a prediction with a measurable signature. Frame it as what the result opens next, never as a shortcoming (ground rule 10 in `SKILL.md`). "Further work is needed" fits every paper ever written and is cut.

Length: two to five sentences. As a guide, about 60 to 120 words in a letter and up to about 200 in a full article, or about 5% of the main text, whichever is smaller. If the Discussion has already done its work, two or three sentences are the right length, not a shortfall.

### Step 3. Do not repeat the abstract or the introduction

What each of the three carries:

| Content | Abstract | Introduction | Conclusion |
|---|---|---|---|
| Background of the field | one sentence | yes, with citations | no |
| Gap | one sentence | yes, with evidence | at most a clause naming the question |
| Central claim | yes, as a promise | yes, as a preview | yes, as the verdict, in new words |
| Supporting findings | headline finding and how strongly it supports the claim | not beyond the preview | synthesis of how the findings combine |
| Scope words | inside the claim | inside the preview | inside the verdict |
| Limitations | no | no | no; each is stated once, in the Results |
| What it leads to | one sentence of reach | what closing the gap would allow | what this result now allows, specifically |
| Next step | no | no | one specific item, if any |

- **No sentence in common** with the abstract or the introduction, and no long run of identical words. The claim may be the same; the sentence may not.
- **Something new for the first-pass reader.** The conclusion contains at least two things the abstract does not, among a synthesis of the findings, a specific consequence and a next step.
- Check it: `python scripts/overlap_check.py conclusion.txt abstract.txt introduction.txt` lists every conclusion sentence that shares a run of six or more words, or most of its content words, with a sentence in the other files.

### Step 4. Strong, not loud

- The first sentence is the answer and the last is the consequence or the next step: the two positions readers remember.
- The verb matches the evidence (see the table in `parts/abstract.md`). Present perfect for what the paper did ("We have shown"), present tense for what holds.
- One headline number at most, with its meaning attached, and only a number that appears in the Results.
- One hedge where the evidence is indirect. Stacked hedges ("may possibly suggest") weaken a claim the paper has earned.
- Strength comes from specifics, not from adjectives. No "novel", "remarkable", "for the first time", "paves the way", "opens new avenues".
- A symbol defined in the body may be used, but name the quantity in words when it first appears here, because many readers arrive from the abstract and introduction without the body.
- The sentence limits of `parts/abstract.md` apply: no sentence over 30 words, one main clause plus at most one more, no pronoun pointing into another sentence.

### Step 5. Keep out

- New results, data, figures or arguments. A conclusion may draw a new implication; it may not introduce new evidence.
- Recap of methods ("we used X to calculate Y") and of the paper's structure.
- The background and motivation again.
- Lists of every result. One answer, at most two supporting findings.
- Vague futures: "more research is needed", "future work will explore", "we hope that".
- Claims wider than NOT SHOWN allows.
- Limitations, caveats and apology. Each limitation is stated once, in the Results (ground rule 10 in `SKILL.md`); the conclusion does not repeat it.
- Pointers to figures, equations and sections. The conclusion states; the body shows.
- Citations, except one or two needed to place the consequence or the next step.

### When rules pull in different directions

Accuracy first (the scope words stay inside the claim, so that it never reaches beyond the Results), then the venue's form, then no duplication, then brevity.

## Checks

1. **Answer first**: the opening sentence states the central claim as a finding, answers the introduction's gap, and matches `brief.md`.
2. **No recap**: no sentence reports an activity ("we studied", "we investigated"), a method or the paper's structure.
3. **Basis**: at most two findings, given as a synthesis.
4. **Scope inside the claim**: the Answer carries the scope words, consistent with NOT SHOWN; no sentence states a limitation or caveat.
5. **Consequence**: specific, and not understandable in full before reading the paper.
6. **Next step**: specific, or absent.
7. **No duplication**: no sentence, and no run of six or more words, shared with the abstract or introduction; at least two things here that the abstract lacks.
8. **Nothing new as evidence**: every number and finding is in the Results.
9. **Strength**: verb matches EVIDENCE; no stacked hedges; no evaluation or novelty words; the last sentence is not a caveat.
10. **Length**: two to five sentences, within the guide and the venue's form; sentence limits met.
11. **Exclusions**: nothing from Step 5.
12. **Agreement**: terms and symbols match `notation.md`; the claim is the same claim as in the title, abstract and introduction.

## Report

Reply in the user's language; write the conclusion in the manuscript's language. Keep it short:

1. **Conclusion**, with its sentence and word count.
2. **Move map**: one line per sentence giving its move and first few words.
3. **Duplication check**: the output of `overlap_check.py`, or the statement that the abstract and introduction do not exist yet.
4. **Flags**: a consequence that could be made more specific, scope words the user should confirm, a next step that needs the user's judgment.

In Audit mode, replace items 1 and 2 with the table of the twelve checks and the smallest fix for each failure.

Propose only. Edit the manuscript when the user asks.

## Example (invented; the physics and the numbers are placeholders)

Before:

> In this paper, we have studied the switching dynamics of noncollinear antiferromagnets, which have attracted great attention for spintronic applications. Using atomistic simulations, we investigated the effect of the tilt angle. Our results clearly show ultrafast and robust field-free switching, which paves the way for future memory devices. Further studies are needed.

Fails: opens with an activity and with the background; a method recap; evaluation without a number; no scope words in the claim; a consequence a reader could have written before reading the paper; a vague future.

After (four sentences):

> We have shown by atomistic simulations that, in a single-domain Mn3Sn film, tilting the kagome plane lets spin-orbit torque reverse the octupole order without a bias field. Reversal takes 0.3 ns, and the threshold current obeys the analytical model at every tilt angle studied. The tilt angle, fixed during film growth, becomes a quantity to design for field-free switching. Measuring the threshold current in films grown at two tilt angles would test the predicted dependence directly.

Move map: 1 Answer "We have shown by atomistic simulations ..."; 2 Basis "Reversal takes 0.3 ns ..."; 3 Consequence "The tilt angle, fixed during film growth, ..."; 4 Next step "Measuring the threshold current ...". Compared with the example abstract in `parts/abstract.md`, the claim and its scope words are the same and no sentence is shared; the agreement at every tilt angle, the growth-time design consequence and the proposed measurement appear only here. The zero-temperature, single-domain model is stated once, in the Results, and not repeated here.

## Relation to other parts

- **Introduction** (`parts/intro.md`) poses the question; the Answer closes it in matching terms.
- **Abstract** (`parts/abstract.md`) is written later and must not reuse these sentences.
- **Results** (`parts/results.md`) is the one place where each limitation is stated; the conclusion does not repeat it.
- **Discussion** carries interpretation and comparison with earlier work; the conclusion does not repeat them.
- **Audit** (`parts/audit.md`) reruns the duplication check on title, abstract, introduction and conclusion together.

## Sources

The journal rules and studies behind these choices, and the points on which venues differ, are in `references/conclusion-evidence.md`; read it when you need to explain a choice.
