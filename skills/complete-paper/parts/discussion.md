# Discussion

Stage B · Reads: `brief.md`, `outline.md`, `venue.md`, `refcheck.md`, the results section, the gap sentence of the introduction · Writes: the discussion section (or the interpretation that follows each result, when the venue merges the two)

The discussion says what the results mean: the answer they give to the paper's question, why that answer should be believed over the alternatives, how it sits beside earlier work, and what it opens next.

It has two jobs:

- **Interpret, with the evidence in view.** Every interpretive sentence can be traced to a result, and says how firmly it follows.
- **Look forward.** The Results have stated each limit once, beside the evidence it bounds. The discussion builds on that: what the same model, method or device can do next, and what it would add (ground rule 10 in `SKILL.md`).

It is the section where a paper most often says more than it showed. The results are fixed by the figures; the discussion is free text, and the pull is to repeat the results at greater length, to select the comparisons that flatter, and to let "suggests" drift into "demonstrates". So the discussion is built from named moves, each with a test, and every sentence of interpretation carries one of three grades.

## Modes

- **Write**: no discussion yet.
- **Revise**: a draft exists; grade every interpretive sentence first, then cut the repeated results.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

1. `brief.md`: QUESTION, RESULT, PRIOR, DIFFERENCE, NOT SHOWN.
2. `outline.md`: the claim chain and the plan for this section.
3. The Results as written, and the gap sentence of the introduction or of the outline's plan for it.
4. `refcheck.md` and the reference list: what the closest works reported, with numbers.
5. `venue.md`: whether the Discussion is separate, merged with the Results, or the last paragraphs of a letter; whether a Conclusion follows.

Write it after the Results and before the Conclusion.

## Steps

### Step 1. Take the form from the venue

| Situation | Form |
|---|---|
| Separate Discussion, then a Conclusion | All five moves here; the Conclusion takes the verdict in one paragraph (`parts/conclusion.md`) |
| Discussion closes the paper (Nature-family journals) | The five moves; the last paragraph does the work of a conclusion |
| Results and Discussion merged | Interpretation and comparison follow each result where they arise; Answer and Outlook still get their own paragraphs at the end |
| A letter | One or two paragraphs before the closing one: the interpretation with its main alternative, the comparison that matters most, the outlook in a sentence or two |

### Step 2. Build it from five moves

| # | Move | What it does | Typical length |
|---|---|---|---|
| 1 | Answer | Answers the question of the introduction in one or two sentences | first paragraph |
| 2 | Interpretation | Says why the result comes out as it does, and why the leading alternative does not explain it | one or two paragraphs |
| 3 | Comparison | Sets the result beside the closest earlier work, with numbers, and accounts for differences | one or two paragraphs |
| 4 | Outlook | Says what the same model, method or device can do next, and what that would add | one paragraph |
| 5 | Consequence | Says what follows that could be tested, built or decided | one paragraph, or the Conclusion |

- **Answer.** Start with the answer, in the terms of the gap sentence. Not a summary of the results: one finding, as the reply to one question. If the introduction asked "whether such a tilt makes the reversal deterministic, and at what cost in current", the first sentences say: it does, and the cost is this.
- **Interpretation.** Give the mechanism or the reason, and tie each step to a result or an equation. Then name the explanation a sceptical reader would reach for first, and say which observation excludes it, or that none does. An interpretation with no rival considered has not been tested.
- **Comparison.** With the works named in PRIOR and any that a specialist would expect: what they found, what this work finds, in the same quantity and units. Agreement is stated with numbers. A disagreement is explained (different regime, sample, definition) or stated as open; it is not left out. Compare the approaches as well as the outcomes, by how they differ and never as a fault: "Unlike the field-assisted switching of Ref. [5], the reversal here needs no field" (ground rule 10).
- **Outlook.** Start from NOT SHOWN, whose entries the Results have already stated once. Turn each one that matters into what can be done next and what it would add: "The same model can include domain walls, which would give the threshold of films that reverse by domain-wall motion." Never restate an entry as a shortcoming here ("domain walls were not simulated"). Scope words that belong to the claim ("in single-domain films") stay with the claim.
- **Consequence.** A prediction with a measurable signature, a design rule, a decision that can now be made. It must not be understandable in full without the paper's result. Where a Conclusion follows, leave the consequence to it and end the Discussion on the outlook.

Order: Answer first. Outlook before Consequence, so that the section ends on what the result makes possible. Interpretation and Comparison in whichever order the argument needs. After the Answer, a paragraph that reports a step of reasoning or a comparison opens with what it is for ("To place the threshold among earlier measurements, we compare ...") (ground rule 13).

### Step 3. Grade every interpretive sentence

| Grade | Meaning | Wording |
|---|---|---|
| Shown | Follows from a result of this paper | plain statement, with the figure or equation |
| Supported | The results agree with it and exclude the main alternative; other explanations are possible | "indicates", "is consistent with ... and not with ..." |
| Speculative | Not tested here | "we speculate that", once, followed by what would test it |

- Mark the grade of each sentence while drafting; the marks come out before the text is returned, and the wording stays.
- At most one speculative idea per paper, in a sentence of its own. Speculation mixed into a sentence that also states a result borrows the result's authority.
- The verbs match the kind of EVIDENCE in `brief.md`. A simulation predicts and finds; it does not observe.
- Nothing in the discussion is stronger than its counterpart in the Results. If a sentence here needs "demonstrates" where the Results say "is consistent with", one of the two is wrong.

### Step 4. Keep out

- **Results again.** Refer to a result in a clause ("the 1/sin θ dependence of Fig. 3"); do not walk through the figures a second time.
- **New results.** Data that appear here for the first time belong in the Results or the supplement.
- **The introduction again.** The background was given once.
- **Limitations again.** "This study has some limitations", or any limitation restated. Each was stated once in the Results. Here it appears only as a next step under Outlook.
- **Vague futures.** "Further studies are needed" fits every paper. Name the measurement or drop the sentence.
- **Defensive repetition.** The scope words of the claim and the one statement of each limit in the Results do more than a disclaimer in every paragraph.
- **Selective comparison.** Citing only the works that agree. The comparison includes the closest work that disagrees.
- **Evaluation.** "Important", "remarkable", "paves the way". State the consequence and let the reader weigh it.

### Step 5. Length and shape

- A guide: 15 to 25% of the main text in a full article; in a letter, the two or three paragraphs before the end.
- Paragraphs, each with its move; subheadings only in long articles and where the venue allows them.
- The sentence rules of `parts/abstract.md` hold in relaxed form: no sentence over about 35 words, and no pronoun that points into another paragraph.

### Step 6. Check

- `python scripts/overlap_check.py discussion.txt results.txt introduction.txt` lists sentences of the discussion that share a run of six or more words, or most of their content words, with the other sections: candidates for "results again" and "introduction again".
- Go through NOT SHOWN line by line: each entry is stated once in the Results, and appears here at most as a next step under Outlook, never as a limitation. `python scripts/audit_tex.py main.tex --checks limits,prior` lists limitation sentences outside the Results and earlier work described as a fault.
- Go through PRIOR: each work appears under Comparison.
- Count the sentences with two hedges ("may possibly", "might suggest") and with none where the grade is "supported".

### When rules pull in different directions

Accuracy first (the grade the evidence supports), then the venue's form, then the outlook, then brevity. A shorter discussion with a concrete outlook is better than a longer one that keeps the speculation.

## Checks

1. **Answer first**: the opening sentences answer the introduction's question, in its terms, and are not a summary of the results.
2. **Interpretation traced**: each step points to a result or an equation.
3. **Alternative considered**: the leading rival explanation is named, with what excludes it or the statement that it remains.
4. **Comparison**: every work in PRIOR appears, with numbers in the same quantity, described by how it differs and never as a fault; a disagreement is explained or stated as open.
5. **Outlook, not limits**: no limitation is restated; entries of NOT SHOWN appear only as next steps, each with what it would add.
6. **Grades**: each interpretive sentence is shown, supported or speculative, and worded accordingly; at most one speculation.
7. **Not stronger than the Results**: no verb here exceeds its counterpart there.
8. **Nothing repeated**: no walk through the figures; no background again; no shared sentences.
9. **Nothing new as evidence**: no data that the Results do not contain.
10. **Consequence**: specific and dependent on this result, or left to the Conclusion.
11. **Order**: answer first; outlook before consequence; the last sentence is not a caveat.
12. **Form**: as the venue requires; consistent with `notation.md` and the terms of the Results.

## Report

Reply in the user's language; write the discussion in the manuscript's language. Keep it short:

1. **Discussion**, with its word count.
2. **Move map**: one line per paragraph with its move; the grade of each interpretive sentence.
3. **NOT SHOWN table**: each entry, the Results sentence that states it, and the next step here if there is one.
4. **Flags**: an alternative that the results do not exclude; a disagreement with earlier work that is not explained; a claim the user may want to narrow.

In Audit mode, replace items 1 and 2 with the table of the twelve checks and the smallest fix for each failure.

Propose only. If the discussion can only be written by claiming more than `brief.md` allows, stop and say so.

## Example (invented; the physics and the numbers are placeholders)

Before:

> As shown in Fig. 2, the octupole moment was reversed for all tilted films, and Fig. 3 shows that the threshold agrees with the model. These results clearly demonstrate that tilted Mn3Sn is a promising candidate for future memory applications. However, this study has some limitations, and further studies are needed.

Fails: results again; "clearly demonstrate" for a simulation; a consequence anyone could have written; a limitation restated as a caveat; a vague future; no alternative and no comparison.

After:

> A tilt of the kagome plane replaces the in-plane field. The current alone selects the final state, at a threshold set by the tilt angle (Answer). The reason is geometric. For a tilted plane the damping-like torque has a component along the easy axis of the octupole, and the 1/sin θ dependence of Fig. 3 is the signature of that projection (shown). A field-like torque of the same symmetry would instead shift the threshold by an amount independent of θ, which the simulations exclude to within 4% (supported). Experiments on untilted films needed a field to switch [A], as Eq. (1) predicts, because the threshold diverges at θ = 0. The same equation predicts that the films of Ref. [C], grown with a tilt of 30°, switch at twice the current of the 90° limit (Comparison). The same model can include domain walls, which would give the threshold of films that reverse by domain-wall motion, and thermal fluctuations, which would carry the prediction to room temperature (Outlook).

The words in parentheses mark the moves and the grades; they are taken out before the text is returned.

## Relation to other parts

- **Introduction** (`parts/intro.md`) poses the question that the Answer closes, in matching terms.
- **Results** (`parts/results.md`) hold the evidence; nothing here is stronger than there.
- **Conclusion** (`parts/conclusion.md`) takes the answer with its scope words, the consequence and the next step; it shares no sentence with this section.
- **Bibliography** (`parts/bibliography.md`): every comparison is a citation with a checked claim.
- **Brief**: a limit discovered while writing goes into NOT SHOWN first, and its one statement into the Results.
- **Audit** (`parts/audit.md`) reruns checks 5, 7 and 8 on the finished manuscript.

## Sources

The sources behind these choices, and where they differ, are in `references/body-evidence.md`; read it when you need to explain a choice.
