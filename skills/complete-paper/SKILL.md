---
name: complete-paper
description: "Turn research results into a complete, internally consistent manuscript, or write, revise or audit any single part of one: claim brief, venue rules, outline, notation and units, equations, figures, tables, captions, methods, results, discussion, conclusion, introduction, abstract, title, bibliography with existence checks, supplement, prose pass, consistency audit and submission package. Use when the user wants to write up results as a paper, draft or fix one section (for example 'write the abstract' or 'check my references'), or preflight a manuscript before submission. Never invents data or citations: anything missing becomes a visible TODO marker. (논문화, 논문 작성, 초록·제목·캡션·참고문헌 작성과 점검)"
license: MIT
metadata:
  version: "0.1.0"
  author: "Gyuyoung Park"
---

# Complete paper

This skill turns results into a complete manuscript, title to supplement, in which every part agrees with every other part. It also works on one part at a time.

## First principles

Three principles come before every rule in this skill. Principles 2 and 3 are never traded away. Principle 1 wins over every ground rule below, except accuracy (ground rules 1 and 2) and the venue's hard requirements.

### 1. A paper written for people

The purpose of this skill is a paper that people find easy and pleasant to read. Every rule below serves that purpose.

- **Write like a careful human author, not like a language model.** Keep machine tone to a minimum. Its marks are stock intensifiers and buzzwords ("crucial", "pivotal", "notably", "delve", "intricate", "leverage", "showcase", "underscore", "seamless", "comprehensive", "a testament to", "in the realm of"). Others are chains of "Furthermore", "Moreover" and "Additionally", triple lists by reflex, "not only ... but also" templates, a summary sentence closing every paragraph ("Overall, ..."), and sentences all of one length and shape.
- **Prefer the concrete.** The plain word, the short sentence, the specific number with its meaning, the named system instead of a category.
- **Check.** `python scripts/audit_tex.py main.tex --checks tone` lists the common marks. `parts/prose.md` does the full pass.

### 2. The data are final, and nothing is filled in

- **Never change data to fit the message.** A value that was calculated or measured and entered by the authors is never edited, rounded differently, dropped or moved: not in the text, a table, a figure, a caption or a data file. If a figure or table does not support the statement it is cited for, say so and change the statement, never the data.
- **Never fill a blank.** A missing value, an empty table cell or a missing data point stays empty, marked with a TODO marker (ground rule 1), and the user is told. An AI agent never supplies it, estimates it or copies it from elsewhere.
- **Check that the numbers agree and that the data carry the message.** Every number in the text, a caption or a table matches its source (ground rule 16). Every figure and table supports the statement it is cited for. Report each disagreement to the user.

### 3. No invented terms

- **Use the field's words.** Terms, technical words, names and abbreviations are the ones the field already uses, in their established meaning. Do not coin a word or phrase for something the field already names.
- **A new name only when a new thing needs one.** When a new phenomenon or quantity must be named, choose the name the community would most likely adopt. It must collide with no existing concept, and it must be the most intuitive and the simplest to explain. Tell the user the proposed name, why it was chosen and the alternatives considered, and use it only once the user agrees.

The work is split into 20 parts. **Read only the part you are working on**: open its file under `parts/`, follow it, and stop. Do not read all parts at once. Files under `references/` hold background and venue details; open one only when a part tells you to.

## Ground rules (every part, every mode)

1. **Never fabricate.** Do not write a number, result, figure, table entry, citation, DOI, author, affiliation, grant number or statement that is not in the user's material or in `paper-state/intake.md`. Never fill an intake field yourself, except by copying the user's own saved defaults (see "Saved defaults"). Where something is missing, leave a marker that contains the word `TODO` and says what is missing:
   - LaTeX: `\textcolor{red}{\textbf{[TODO: what is missing]}}`
   - Markdown: `> 🔴 **TODO**: what is missing`
   - Other formats: `[TODO: what is missing]`, highlighted if the format allows.
   - A citation not yet in hand, in any format: `[CITE: what is needed]`. Audit counts it as a TODO marker.
   Placeholder symbols (`X.XX`, `??`) are allowed inside a marker. A specific number that looks real is not.
2. **Claim no more than the brief shows.** Every claim traces to a line of `paper-state/brief.md`. Evidence words match the evidence: experiments are "observed" or "measured"; simulations and theory "predict" or "show in simulation". The "Not shown" list in the brief is a hard boundary.
3. **The author decides.** Propose changes to claims; do not make them silently. Audit mode reports and never edits. The author is responsible for the content and its authorship; AI is never an author.
4. **Venue rules win** over the house style in this skill, but never over accuracy. Every part reads its own line under "Directives" in `venue.md` before applying its defaults. Unknown venue rules are marked "unchecked", never guessed.
5. **Abbreviations**: expand at first use, then use the short form. The abstract, the main text and the supplement each apply this rule on their own. Do not abbreviate a term used only once or twice.
6. **Numbers carry their meaning.** A number appears only if it matters to the result, and the sentence says why: against prior work, as a factor or difference, or against a physical threshold. No lists of numbers, no false precision.
7. **No direct questions** in the body, abstract, title or captions. Turn them into statements or indirect questions ("whether the effect is intrinsic").
8. **One notation.** Symbols, terms and units follow `paper-state/notation.md`. SI units unless the venue says otherwise; no mixed unit systems.
9. **Disclose AI use.** This skill drafts text. Where the venue asks for it, draft an AI-use statement that reflects what was actually done, for the author to confirm; `parts/submit.md` checks that it is in place.
10. **Write for the paper; state each limitation once.**
   - Not neutral. Every part leads with the selling point: the central claim of `paper-state/outline.md` and what it adds beyond earlier work. Order, emphasis and the choice of comparisons serve that point: the strongest evidence comes first, and comparisons with earlier work show what this work adds.
   - Advocacy works through selection, order and specifics. It never widens a claim (rule 2), never misstates earlier work, and never leans on evaluative adjectives ("novel", "remarkable", "unprecedented").
   - Earlier work is a contrast, never a fault. When the text cites another group's results, it says how this work differs from them ("Unlike the field-assisted switching of Ref. [5], the reversal here needs no field", "Smith et al. measured X in Y, and we extend it to Z"). It never calls their results wrong, poor, flawed or limited ("fails to", "suffers from", "incorrect", "a drawback of"). `python scripts/audit_tex.py main.tex --checks prior` lists such sentences.
   - Each limitation or weakness is stated once in the whole paper: in the Results, where the evidence it qualifies is presented, as a plain fact about that evidence. No other part restates it as a limitation. No limitations or caveat sentence in the title, abstract, introduction, discussion, conclusion, captions, supplement or cover letter.
   - Look forward, not back. Where the Discussion, or the conclusion's next step, goes beyond the present evidence, it says what can be done next, as an opportunity the work opens ("The same model can include thermal fluctuations, which would extend the prediction to room temperature"), never as a shortcoming ("thermal fluctuations were not included").
   - Background and gap as a need. In the abstract and the introduction, the gap is a need that has arisen and that a concrete idea now makes possible to meet ("Dense memory built from Mn3Sn calls for switching without a bias field"), not an absence ("No study has ...", "has not been studied", "remains unknown"). Where earlier work reaches is shown with citations, as a fact.
   - Scope words that make a claim exact ("in simulations", "in single-domain films") are part of the claim, not a limitation. They stay wherever the claim appears, so that no part claims more than the Results show.
   - Methods and the supplement describe what the model or experiment includes as plain description, without calling it a shortcoming.
   - If the venue requires a limitations section or statement elsewhere, ask the user. With their agreement the limitations move there, still once, and the Results do not repeat them.
11. **Say what we did, in the first person.** What this study did is written with "we" as the subject and an active verb that names the action: "we implement", "we derive", "we simulate", "we measure", "we show".
   - Not the passive that hides who did it ("simulations were performed", "it was found that", "a model is proposed").
   - Not activity verbs that withhold the outcome ("we study", "we investigate", "we explore", "we examine").
   - Once the action is credited, a finding may take the finding as its subject ("Reversal completes within 0.3 ns"). This also keeps a run of sentences opening with "We" from reading as a list (`parts/abstract.md`).
   - Earlier work keeps its own authors as the actor ("Smith et al. measured ..."), so that the contrast with what we did stays visible.
   - Captions describe what is shown and need no "we". If the venue avoids the first person, follow the venue ("Here, ... is shown", "This work shows").
12. **Number in the order of the argument.** Figures, tables and equations are numbered in the order of their first citation in the text, and that order is the order of the argument. The supplement's items follow the same rule on their own.
   - When the text cites Eq. (2) before Eq. (1), or Fig. 3 before Fig. 2, fix the argument first: move the paragraph so that the reader meets the items in the order the logic needs.
   - If the argument is already in the right order, move the display instead, so that the item cited first becomes number 1 (LaTeX numbers follow position).
   - No reference to an equation that has not yet been displayed, except to an appendix or the supplement. One more exception: a section's opening paragraph may name the result the section derives further down, so that a reader can skip to it (`parts/supplement.md`). That pointer does not count as a first citation.
   - Check after every reordering: `python scripts/audit_tex.py main.tex --checks xrefs`.
13. **Say why before what.** A paragraph or subsection that reports work opens with its purpose, then says what we did, then what it shows: "To validate the model, we compare it with ... The agreement shows ...", "To model the switching, we ...". The reader then knows why each step was taken and how its result serves the claim. This holds in the methods, results, discussion and supplement, together with rule 11.
14. **Plain punctuation.** In the manuscript, captions included, no colons, semicolons or dashes that join clauses or lists in running text. Split the sentence, or join with "and", "because", "so" or "which".
   - Kept: the title form "Name: descriptor" where `parts/title.md` calls for it, ratios and times (1:2), punctuation inside equations and references, and forms the venue requires.
   - `python scripts/audit_tex.py main.tex --checks punct` lists the rest for review.
15. **Every sentence and paragraph in context.** Each sentence follows from the one before. Each paragraph opens by linking to what came before or to the statement of the claim chain it serves. Nothing is dropped in without context.
   - Evaluate it with a reverse outline: `python scripts/reverse_outline.py main.tex` lists the first sentence of every paragraph, section by section. Read them in order. They should tell the argument, each following from the last.
   - For each paragraph, name the statement of `outline.md` it serves. A paragraph that serves none is cut or moved. A paragraph or sentence that does not follow from its neighbour gets a bridging sentence or moves.
   - No roadmap. The introduction does not end with the paper's structure ("The rest of this paper is organized as follows", "Section II describes ..."). It ends with this work and its finding.
   - Every part that writes text applies this rule to its own section; the prose and audit parts evaluate the whole manuscript.
16. **Numbers agree everywhere.** Before handing over any part that states numbers, trace each number in the text, a caption or a table to its source: the data file, the plotting script, the table, or the Results sentence it repeats. The value, unit, rounding and sign are the same everywhere.
   - When they disagree, the data decide. Correct the text to match the data, or ask the user which is right. Never edit the data to match the text (first principle 2).
   - `python scripts/audit_tex.py main.tex --checks numbers` lists numbers in the abstract or the conclusion that appear nowhere else in the paper.
   - The prose and audit parts repeat this for the whole manuscript, together with the check that each figure and table supports its statement.

## Parts

The order is the order of writing, not the order in the printed paper. Summary parts (conclusion, introduction, abstract, title) come late because they summarize what is already written.

| # | Stage | Part | File | Produces |
|---|---|---|---|---|
| 0 | A Foundation | brief | `parts/brief.md` | `paper-state/brief.md`: the claim in five fields, its place among earlier work, key numbers with their sources, the evidence map, what was not shown |
| 1 | A | venue | `parts/venue.md` | `paper-state/venue.md`: limits, section order, styles, required statements |
| 2 | A | outline | `parts/outline.md` | `paper-state/outline.md`: central claim, claim chain, display-item specifications, budget, holes |
| 3 | A | notation | `parts/notation.md` | `paper-state/notation.md`: symbols, typefaces, units |
| 4 | B Body | equations | `parts/equations.md` | Derivation chain, displayed equations, labels and citations |
| 5 | B | figures | `parts/figures.md` | Figures built at final size from one style table (one message, one colour per meaning), schematics drawn by code, checked by a lint |
| 6 | B | tables | `parts/tables.md` | Lean tables of exact values in SI units, laid out for the comparison, explanation in the caption; small sets of values go to the text |
| 7 | B | captions | `parts/captions.md` | Self-contained captions that say what is shown and leave its meaning to the text |
| 8 | B | methods | `parts/methods.md` | Methods a specialist can repeat, every value from its source, checked against a list for the kind of work; `repro.md` |
| 9 | B | results | `parts/results.md` | Results in the order of the claim chain, each paragraph from its purpose to its finding, numbers with uncertainty and a reference; the one place where each limitation is stated |
| 10 | B | discussion | `parts/discussion.md` | The answer, its interpretation against the leading alternative, comparison with earlier work by how it differs, and an outlook on what the work opens next |
| 11 | B | conclusion | `parts/conclusion.md` | Conclusion in four moves (answer with its scope words, basis, consequence, next step), sharing no sentence with the abstract or introduction |
| 12 | B | intro | `parts/intro.md` | Introduction in five moves, from broad interest to this work, with a citation table and a gap check |
| 13 | B | abstract | `parts/abstract.md` | Abstract |
| 14 | B | title | `parts/title.md` | Title, typeset and plain-text |
| 15 | C Front and back matter | bibliography | `parts/bibliography.md` | References that exist, match their record and support their sentence, with fair coverage, in venue style; `refcheck.md` |
| 16 | C | supplement | `parts/supplement.md` | Each item sent to main text, supplement, data package or cut; a supplement no larger than the paper, reached by few, specific callouts, in the paper's style; `suppmap.md` |
| 17 | D Finish | prose | `parts/prose.md` | Machine tone removed at its cause, readable sentences, with a check that no number, symbol, citation or claim changed |
| 18 | D | audit | `parts/audit.md` | Whole-manuscript consistency report from every part's script, eleven reading passes and an independent reading, including every number traced to its source and every figure and table checked against its statement; `audit.md` |
| 19 | D | submit | `parts/submit.md` | Review copy, clean source package, form entries, required statements, cover letter, preprint; `submission.md` |

Dependencies:

- Every part needs `brief.md`. Body parts (4 to 14) also need `venue.md`, `outline.md` and `notation.md`.
- Within stage B, write in table order. Equations come first, because methods, results, captions and the supplement cite them by number. Captions follow figures and tables; results follow methods; discussion, conclusion, introduction, abstract and title follow results.
- Stage C parts do not depend on the body text, except the supplement, which follows the body. Run them at any time.
- Stage D needs a complete draft. Audit runs after prose; submit runs after a clean audit.

## Modes

Every part runs in one of three modes. Pick the mode from the request; when it is ambiguous, use the default in parentheses.

- **Write**: the text does not exist yet. Draft it from the state files and the user's material. (Default when the target section is empty.)
- **Revise**: the text exists and the user wants it improved. Cut before adding; keep the author's claims and wording unless a rule is broken; list every change of meaning. (Default when the user says "improve", "tighten", "fix".)
- **Audit**: report problems against the part's checks; do not edit. Ask which findings to fix. (Default when the user says "check", "review", "audit", "preflight".)

## State files

State lives in the user's project, in a folder named `paper-state/` next to the manuscript, so work survives across sessions and every part starts from the same facts.

| File | Written by | Read by |
|---|---|---|
| `intake.md` | the authors, from [assets/intake.md](assets/intake.md) | every part that needs facts only the authors know: brief, venue, methods, bibliography, submit |
| `brief.md` | brief (its Record section copied from `intake.md`) | every part |
| `venue.md` | venue | every part that writes text, plus bibliography, submit |
| `outline.md` | outline | figures, tables, captions, methods, results, discussion, conclusion, intro, abstract, title, supplement, audit |
| `notation.md` | notation | every part that writes text, plus figures, tables, audit |
| `figstyle.md` | figures | figures, captions, supplement, audit |
| `refcheck.md` | bibliography | bibliography, audit, submit |
| `suppmap.md` | supplement | supplement, outline, methods, audit |
| `repro.md` | methods | methods, audit, submit |
| `audit.md` | audit | submit |
| `submission.md` | submit | the next round of the paper |
| `progress.md` | every part | the entry point, at the start of each session |

`progress.md` is one table: part, status (`todo`, `provisional`, `draft`, `revised`, `audited`), last mode, date, open TODO count, notes. Update it after every part. A part written before its inputs existed (for example an abstract written before the results section) is `provisional` and must be revisited.

When a part needs a state file the user changed by hand, the file wins over anything remembered from earlier in the session.

## Saved defaults

Facts that repeat from paper to paper are saved once and reused: the user's name as printed, ORCID, email and affiliations, frequent co-authors, funders and grant numbers, standing acknowledgments, declarations wording, the AI-use statement already approved, usual venues and the figure style. They live in `~/.complete-paper/defaults.md`, in the user's home folder, outside every project and outside this skill's folder, so that updating the skill leaves them alone. The form is [assets/defaults.md](assets/defaults.md).

- **Save only on request.** When the user fills in or confirms such a field in a project's `intake.md`, offer once to save it as a default, and write it on a yes. Never save anything the user did not supply.
- **Reuse.** At the start of a new paper, if the file exists, copy its fields into the new `intake.md`, each marked "(default)", and ask the user to confirm the block once, because co-authors, affiliations and grants change between papers. A confirmed field loses the mark.
- **The project wins.** A field the user changes in a project overrides the default for that paper. Ask whether to update the default as well.
- **Private.** The file holds personal data. It stays on the user's machine and goes into no request to an outside service.

## How to start

1. Find the manuscript and `paper-state/`. The manuscript is usually the `.tex` file that contains `\documentclass`, or a `.md` or `.docx` file. If `paper-state/progress.md` exists, read it and continue from it.
2. If `paper-state/intake.md` does not exist, copy [assets/intake.md](assets/intake.md) there, fill in what `~/.complete-paper/defaults.md` covers (see "Saved defaults"), and ask the authors to confirm those fields and fill in the rest. Do not wait for it: continue with what is available, and leave TODO markers wherever a part needs a blank field.
3. Decide the scope from the request:
   - **Whole paper** ("write this up as a paper"): run the parts in table order. After each stage, show the user what was produced and ask before starting the next stage.
   - **One part** ("write the abstract", "check my references"): check the prerequisites below, then open only that part's file.
   - **Audit or preflight**: open `parts/audit.md`.
4. Prerequisites for a single part:
   - No `brief.md`: build a **minimal brief** first (headline result, evidence, what was not shown, figure list) by following `parts/brief.md` in its minimal form, then continue.
   - No `venue.md`: run the venue part to fix the venue, article type and stage. If there is no venue and the user cannot be asked, write `venue.md` with every rule at the corresponding part's default and the status "no venue chosen"; every venue check then stays unchecked.
   - No `outline.md` or `notation.md`: create them first only if the part depends on figure order (figures, captions, results, supplement) or on symbols (equations, methods, results); otherwise continue and note the gap.
   - A summary part whose source text does not exist yet: write from the brief, mark the part `provisional`, and say so.
5. Before writing into a manuscript, ask where the text should go (an existing file and section, or a new file) unless that is obvious.

## The shape of every part file

Each file under `parts/` has the same sections, in this order, so you never need to re-learn the structure:

- **Header line**: stage, what the part reads, what it writes.
- **Modes**: what Write, Revise and Audit mean for this part.
- **Inputs**: what to read, in order: state files, then the part's own rules, then only the manuscript sections it needs.
- **Steps**: what to do.
- **Checks**: pass/fail conditions. Audit mode reports exactly these.
- **Report**: what to tell the user at the end.

A part may open with a short statement of its purpose after the header line, and may end with optional sections after Report: relation to other parts, examples, and what not to promise. The evidence behind a part's rules lives in `references/`, not in the part.

## Scripts

Nineteen Python 3 scripts live in `scripts/` in this skill's directory, listed with what each checks in [scripts/README.md](scripts/README.md). Each part names the scripts it runs, with the command, so open the list only when you need a script that no part has named.

- **Where to run.** Run every command from the user's project folder, where the manuscript and `paper-state/` are, and call the script by its path in this skill's directory: `python <skill-dir>/scripts/audit.py main.tex --brief paper-state/brief.md`. In the parts, `scripts/...` means that path, and every other path is relative to the project folder.
- Run a script with `--help` before its first use. The scripts find problems; you still read the flagged lines before reporting them.


## Background files

Open one only when its part says so.

| File | Used by |
|---|---|
| [references/outline-evidence.md](references/outline-evidence.md) | outline |
| [references/tables-evidence.md](references/tables-evidence.md) | tables |
| [references/body-evidence.md](references/body-evidence.md) | methods, results, discussion |
| [references/prose-evidence.md](references/prose-evidence.md) | prose |
| [references/audit-submit-evidence.md](references/audit-submit-evidence.md) | audit, submit |
| [references/figures-evidence.md](references/figures-evidence.md) | figures |
| [references/references-evidence.md](references/references-evidence.md) | bibliography |
| [references/supplement-evidence.md](references/supplement-evidence.md) | supplement |
| [references/captions-evidence.md](references/captions-evidence.md) | captions |
| [references/conclusion-evidence.md](references/conclusion-evidence.md) | conclusion |
| [references/intro-evidence.md](references/intro-evidence.md) | intro |
| [references/abstract-evidence.md](references/abstract-evidence.md) | abstract |
| [references/title-evidence.md](references/title-evidence.md) | title |
| [references/notation-standards.md](references/notation-standards.md) | notation, equations |

## Report format

At the end of every part, reply in the user's language (the manuscript keeps its own language) with:

1. **Done**: what was written or changed, with file and section.
2. **TODO markers**: how many were added and where.
3. **Flags**: overclaim risk, unchecked venue rules, claims without evidence, anything the author must confirm.
4. **Next**: the next part in the order, or the part this one showed needs revisiting.

## Not covered in this version

Responses to referees, statistical analysis of raw data, checking that derivations are correct, and submitting on the user's behalf. The skill prepares a submission; the author submits it.
