# Introduction

Stage B · Reads: `brief.md`, `outline.md`, `venue.md`, `notation.md`, the user's sources, the Results and Discussion drafts · Writes: the introduction

An introduction takes a reader who does not know the work from something they already care about to the one question this paper answers, and tells them the answer is coming. It argues for the question; the Results argue for the answer.

It has two jobs. It must make the venue's reader **care about the gap**, and it must **place the work fairly** among what is already known. It is not a review of the field, a history of the project, or a longer copy of the abstract.

The form is a funnel of five moves, each narrower than the one before: broad interest, specific interest, gap, importance, this work. One job per paragraph.

## Modes

- **Write**: no introduction yet.
- **Revise**: an introduction exists; keep what passes and fix what fails. Cut background before adding any.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read before writing:

1. `brief.md`: RESULT, SYSTEM, METHOD, EVIDENCE, NOT SHOWN.
2. `outline.md`: the central claim, the claim chain, and the one-sentence plan for each introduction paragraph.
3. `venue.md`: who the readers are and what the editors select for; the length allowed for the introduction; whether it carries a heading; whether the first paragraph doubles as the abstract.
4. `notation.md`: terms, abbreviations and symbols.
5. The sources: the user's bibliography file, reference list and any papers supplied. These are the only works that may be cited without a further check (see Step 3).
6. The Results and Discussion drafts, if they exist.

Write the introduction after Results, Discussion and Conclusion, and before the abstract and title. Only then is it known exactly what has to be introduced.

## Steps

### Step 1. Fix the reader and the gap

Answer two questions in one line each before writing:

- **Who is the reader?** Take the venue's own description. A letters journal for a whole discipline, or a multidisciplinary journal, expects the opening to be understood by scientists outside the subfield; a specialist journal allows a faster start.
- **What is the gap?** State it as a fact about current knowledge, in one sentence. It must be the gap that the central claim closes, and the same gap the abstract names, in the same terms.

A gap is one of: something unknown; an obstacle or limitation of existing methods; two results that disagree; a prediction not yet tested; a missing tool. If the paper seems to need two gaps, return to the outline. Whatever its kind, write it as a need that has arisen and that a concrete idea can now meet, not as an absence (ground rule 10 in `SKILL.md`).

### Step 2. Build it from five moves

| # | Move | What it does | How to recognise it |
|---|---|---|---|
| 1 | Broad interest | Starts from a problem or opportunity the venue's reader already cares about | no citation needed to accept that it matters |
| 2 | Specific interest | Narrows to the system, phenomenon or approach of this paper and says what is known | the key prior results, each cited |
| 3 | Gap | States the one need that has arisen: what is now required, blocked or in conflict | the need stated positively ("... calls for ...") with citations showing where existing work stands |
| 4 | Importance | Says what meeting the need would allow or settle, and why it matters now | a concrete consequence, not an adjective |
| 5 | This work | Says what the paper does and what it finds | "Here we show ..." / "In this work we ..." |

- **Broad interest.** Open one level above the paper's topic, not at the top of science. Test: if the first sentence could open hundreds of other papers, it is too broad. Name the actual reason the topic matters (what it enables, what it limits). "X has attracted considerable attention" names nothing.
- **Specific interest.** Give only the background a reader needs in order to see the gap. Each paragraph is more specific than the one before. Report what was found, not who did what in which year. Everything else that is merely related belongs in the Discussion or nowhere.
- **Gap.** One gap, stated precisely, with citations showing where existing work stops. Prefer a positive statement of what is covered and where it ends ("Existing treatments assume a single scalar exchange constant [refs]") to an absolute negative ("has never been studied"), which one overlooked paper refutes. Frame the gap as the need itself ("Dense memory calls for X [refs]"), not as what nobody has done.
- **Importance.** Say what meeting the need makes possible: what can then be done, predicted or decided. Tie it to what this venue's editors select for, as recorded in `venue.md`, but do not inflate the claim to meet a venue's taste.
- **This work.** State the approach and the principal finding, with the system and the kind of evidence, in one or two sentences. The verb matches the evidence (experiment: show, observe, measure; simulation: show by simulation, predict; theory: derive, predict; method: introduce, present). Use less context and somewhat more detail than the abstract. Where the preview covers several results, follow the order of the claim chain.

After move 5, at most one sentence on what the result leads to. The introduction ends there. No paragraph lists the sections ("The paper is organized as follows"), in any format (ground rule 15 in `SKILL.md`).

#### How the moves fit the format

| Format | Typical shape |
|---|---|
| Letter (three or four short paragraphs, often without headings) | P1: moves 1 and 2. P2: moves 3 and 4. P3: move 5. |
| Full article | P1: move 1. P2, sometimes P3: move 2. Next: moves 3 and 4. Last: move 5. |
| Venue with a summary first paragraph (Nature family) | The summary paragraph follows `parts/abstract.md`. The introduction after it, without a heading, expands the background and ends with the gap and a brief statement of the approach; it does not repeat the summary's sentences. |
| Conference paper in computing | Problem; where existing approaches stand; the idea; then the contributions as a short list, where the venue's papers do this. |

Length comes from `venue.md` and the budget in `outline.md`. With no rule, use the outline's share for the introduction (about a fifth of the main text by default) and prefer shorter. Nature-family guides, for example, allow up to about 500 words.

### Step 3. Cite what you claim

The introduction is where invented or misremembered references do the most damage, so the rules are strict.

- **Every statement about the field, about earlier results, and about the gap carries a citation.** Move 1 may open without one; nothing after it may.
- **Cite only what has been seen.** A work may be cited if it is in the user's bibliography or supplied papers, or if it was retrieved and its abstract or text was read in this session and supports the sentence. Never cite from memory. When a needed source is not in hand, write a visible placeholder, `[CITE: what is needed]`, and list it in the report.
- **Check the gap.** A claim that something is unknown or unsolved needs a literature check: search for the closest work, record the queries and the date, and cite what comes nearest. If no check was possible, flag the gap as unverified.
- **Cite the closest and the competing work**, including papers that partly close the gap. State the difference as fact, without disparaging the earlier work. A referee will know those papers.
- **Primary sources for specific results; a review for a broad statement.** Include the recent work that shows the gap is still open.
- **Say what the cited work did.** A string of fifteen references behind one general sentence tells the reader nothing; cite fewer, or split the sentence by what each group established.

### Step 4. Keep out

- Results before the reader is ready for them, and any number beyond the headline one.
- Novelty and priority words ("novel", "for the first time", "unprecedented"). The contrast between move 3 and move 5 shows what is new.
- Textbook material, history of the field, lists of applications, long accounts of the authors' earlier papers.
- Method details and equations, unless an equation is itself the subject.
- Empty phrases and additive openers, as listed in `parts/abstract.md`.
- Undefined abbreviations and symbols. Define each at first use here, even if the abstract defined it.
- Sentences copied from the abstract. Some overlap of content is expected; identical wording is not.
- A roadmap of the paper ("The rest of this paper is organized as follows", "Section II describes ...").
- Earlier work described as a fault ("fails to", "suffers from"). Say how this work differs from it (ground rule 10 in `SKILL.md`).

### When rules pull in different directions

Accuracy and fair citation first, then the venue's rules and readership, then the funnel, then brevity.

## Checks

1. **Funnel**: all five moves present, in order, each narrower than the last; one job per paragraph (two adjacent moves may share a paragraph in a letter).
2. **Opening**: the first sentence could not open hundreds of other papers, and gives a concrete reason the topic matters.
3. **Reader**: the opening paragraph is understandable to the venue's stated readership without the rest of the paper.
4. **Background**: every background sentence is needed to see the gap; no review beyond that.
5. **Gap**: one gap; stated as a fact about knowledge and framed as a need, not an absence; identical in substance and terms to the abstract's; closed by the central claim.
6. **Importance**: a concrete consequence follows the gap; no inflated claim.
7. **This work**: approach and principal finding stated with system and kind of evidence; verb matches EVIDENCE; nothing beyond NOT SHOWN; order follows the claim chain.
8. **Citations**: every statement about prior work is cited; every citation was seen and supports its sentence; the closest and competing works are cited; placeholders are listed.
9. **Gap check**: the literature check for the gap is recorded, or the gap is flagged as unverified.
10. **Exclusions**: nothing from Step 4 is present; no section-list paragraph.
11. **Fit**: length within the venue's rule or the outline's budget; heading or no heading as the venue requires.
12. **Agreement with the rest**: terms and symbols match `notation.md`; the Discussion's first paragraph answers the gap stated here.

## Report

Reply in the user's language; write the introduction in the manuscript's language. Keep it short:

1. **Introduction**, with its word count.
2. **Move map**: one line per paragraph giving its move and first few words.
3. **Claim and citation table**: each statement about prior work, its citation, and its status (in the user's bibliography; retrieved and read; placeholder).
4. **Gap check**: the searches run, the date, and the nearest work found.
5. **Flags**: unverified gap, missing sources, overclaim risk, unchecked venue rules.

In Audit mode, replace items 1 and 2 with the table of the twelve checks and the smallest fix for each failure.

Propose only. Edit the manuscript when the user asks.

## Example (invented; the physics and the literature are placeholders)

Opening sentence:
- Before: "Antiferromagnets have attracted great attention in recent years."
- After: "Antiferromagnets promise memory elements that switch on picosecond timescales and produce no stray field."

Gap sentence:
- Before: "However, field-free switching of Mn3Sn has never been studied."
- After: "Integrating Mn3Sn into dense memory calls for writing its octupole order electrically without the in-plane bias field that experiments have used so far [CITE: the experiments that used a bias field]."

Move map of a three-paragraph letter:
1. P1, moves 1 and 2: "Antiferromagnets promise memory elements ..."; narrows to noncollinear antiferromagnets and what is established about reading and writing their octupole order.
2. P2, moves 3 and 4: "Integrating Mn3Sn into dense memory calls for ..."; what field-free writing makes possible in a device.
3. P3, move 5: "Here we show by atomistic spin-dynamics simulations that ..."; the principal finding, then one sentence on what it leads to.

## Relation to other parts

- **Outline** (`parts/outline.md`) supplies the paragraph plan and the order of the preview.
- **Abstract** (`parts/abstract.md`): the same gap and terms in compressed form; written after the introduction.
- **Discussion**: answers the gap in its first paragraph and returns to the importance stated here.
- **Bibliography** (`parts/bibliography.md`): formats the citations and checks again that each cited work exists.
- **Prose** (`parts/prose.md`): sentence-level polish.

## Sources

The guidelines and studies behind this structure, and the points on which they differ, are in `references/intro-evidence.md`; read it when you need to explain a choice.
