# Audit

Stage D · Reads: the final manuscript and supplement, the figure scripts, the bibliography, the compile log, all state files · Writes: `paper-state/audit.md` (no edits to the manuscript)

The audit reads the finished manuscript as one object and checks that its parts agree: with each other, with the brief, and with the venue. Every part tested its own section while it was written. The errors that remain live between sections: a number in the abstract that the body does not contain, a symbol that changed its meaning on page four, a figure that nothing cites, a claim that grew between the Results and the Conclusion.

It has two jobs:

- **Nothing contradicts.** One claim, one set of numbers, one notation, from the title to the last supplementary figure.
- **Nothing is missing.** Every item is cited, every reference resolves, every required statement is present, every limit of the venue is met.

Rule: **the audit changes nothing.** It reports each failure with its place, the smallest fix and the part that owns the rule. The fix is made by going back to that part, and the audit is then run again.

## Modes

- **Audit** (full): before submission. Scripts, reading passes, independent reading.
- **Audit** (quick): the scripts only, after any change to a section.
- **Audit** (referee): the independent reading alone (Step 3).

Write and Revise do not apply: the audit changes nothing.

## Inputs

1. The state files: `brief.md`, `venue.md`, `outline.md`, `notation.md`, `figstyle.md`, `suppmap.md`, `repro.md`, `refcheck.md`.
2. The final sources of the main text and the supplement, the figure scripts, the bibliography.
3. The compiled PDF and its log, built from a clean folder.

Audit the files that will be sent, not an earlier copy.

## Steps

### Step 1. Run the scripts

```
python scripts/audit.py main.tex --supp supplement.tex --bib refs.bib \
        --brief paper-state/brief.md --repro paper-state/repro.md \
        --figures make_fig*.py --style paper-state/figstyle.md --width-mm 86 178 \
        --require data competing contributions ai \
        --abstract-chars 600 --words 3750 --display-max 4 \
        --online --report paper-state/audit.md
```

Take the limits and the required statements from `venue.md`. The script runs the checker of every part on the final files, adds the cross-checks below, and writes one report.

| Part check | Script | What a failure means |
|---|---|---|
| equations | `eq_refs.py` | an unresolved reference, a duplicate label, a number typed by hand |
| citations | `cite_order.py` | a figure, table or panel that the text does not cite, or cites out of order |
| captions | `caption_check.py` | a caption over the venue's length |
| tables | `table_check.py` | a table without caption |
| supplement | `supp_check.py` | a callout in the abstract, an item cited nowhere, a callout to nothing |
| references | `ref_check.py` | a citation without entry, a record that does not match (with `--online`) |
| prose | `prose_lint.py` | reported as a count of warnings; never fails |
| abstract | `abstract_stats.py` | the abstract over the venue's cap |
| duplication | `overlap_check.py` | a sentence of the conclusion shared with the abstract or the introduction; reported for review, it does not fail the audit |
| figures | `fig_lint.py` | faults in any figure, and colours that change meaning between figures |
| brief | `brief_check.py` | an unfinished claim sheet; key numbers that the text does not quote |
| methods | `methods_check.py` | an item a repeater needs that the manuscript does not state |
| house rules | `audit_tex.py` | limitation sentences outside the Results, passive voice and activity verbs for our own work, colons and semicolons in running text, the gap as an absence, machine tone, a roadmap, earlier work described as a fault, equations cited before they are displayed (first principle 1, ground rules 7 and 10 to 15); reported for review, it does not fail the audit |

Cross-checks made by `audit.py` itself:

- **Placeholders**: "??", TODO, "[CITE]", filler text, placeholder images, coloured or struck-out text.
- **Compile log**: undefined references and citations, labels defined twice.
- **Numbers**: a number in the abstract or the conclusion that the rest of the text does not contain.
- **Sentences**: more than 30 words in the abstract or the conclusion.
- **Abbreviations**: defined in the abstract and not again in the text.
- **Statements**: those named with `--require`; a data statement that offers data on request only.
- **Initials**: in the contribution statement, against the byline.
- **Limits**: abstract, running text, display items, references, title.

A check that was skipped is named in the report with the reason. The word count of the script is a plain count; where the venue counts in its own way, use the venue's tool for the final figure.

### Step 2. Read what no script can read

Eleven passes, each with one question. Do them in this order; write one line per finding.

| Pass | Question | How |
|---|---|---|
| A. Claim | Do all parts state the same result? | Copy out the claim sentence of the title, the abstract, the end of the introduction, the start of the discussion and the conclusion. Set them beside RESULT. Same finding, same system, a verb no stronger than the evidence, nothing beyond NOT SHOWN |
| B. Chain | Does the text establish what the outline planned? | Write one sentence per paragraph of the Results. Compare with the claim chain: every statement established, in order, no paragraph outside it (outline checks 5 to 8 and 11) |
| C. Numbers | Is every number the same everywhere? | Trace each number of the abstract and the conclusion to a sentence of the Results, a figure or table, and the key numbers of `brief.md`: value, rounding, unit. Trace each value in a table, a caption or the text to its data file or plotting script (ground rule 16). Where they differ, the data decide; report it, never edit a value (first principle 2) |
| D. Display items | Does each figure and table do its work? | For each: it supports the statement it is cited for (first principle 2); the takeaway stated where it is first cited; the caption explains every element and symbol; units and terms agree with the text (caption checks 2, 3, 11, 12); colour, typeface, panel labels and order (figure checks 7, 9, 11, 13) |
| E. Notation | One symbol, one meaning? | Notation checks 1, 5, 6 and 7: one to one, defined at first use, the same in text, figures, tables and supplement, one unit system |
| F. References | Does each citation carry its sentence? | The record check of `ref_check.py --online` on the final files; then read the sentences that cite the works named in PRIOR against what those works report |
| G. Supplement | Does the main text stand alone? | Supplement checks 1, 4 to 8 and 12 |
| H. Front and back matter | Are names and statements the same everywhere? | Byline, title and statements in the manuscript, on the supplement's title page, in the cover letter and in the form |
| I. Venue | Would the venue's system and editor accept the form? | Structure, required sections, formats and limits of `venue.md`, re-verified on the venue's page |
| J. Reading | Can it be read once? | The whole paper, start to end, as the target reader; mark every place that needed a second reading |
| K. House rules | Does the paper keep the skill's rules of advocacy and form? | Read the lines of "house rules" one by one: each limitation once, in the Results; "we" and an active verb; purpose first; plain punctuation; the gap as a need; earlier work by its difference; no roadmap. Then read the first sentences that `reverse_outline.py` lists: they tell the argument, each from the last (ground rule 15) |

Passes A and C find the errors that readers notice first: most readers see only the title, the abstract and the conclusion, and they notice when the three disagree.

### Step 3. Have it read by someone who did not write it

The author of a text reads what was meant. Give the PDF alone, without the drafts and without this conversation, to a reader who has not seen the work: a colleague, or a fresh agent. Ask for four things:

1. The claim of the paper in one sentence.
2. The three strongest objections a referee would raise.
3. What they would ask for before accepting it.
4. Every place they had to read twice.

Then compare. If their sentence in item 1 differs from RESULT, the paper says something other than what was intended; that is the most important finding an audit can make. Each objection gets one of three answers: a change in the paper, an entry in NOT SHOWN with its one sentence in the Results, or a reply kept ready for the referees. Do not argue with the reading; a real referee cannot be argued with either.

### Step 4. Sort by what blocks

| Level | Examples | Action |
|---|---|---|
| Blocking | an unresolved reference or citation; a placeholder; a required statement missing; a limit exceeded; a number in the abstract that differs from the body; a reference whose record could not be verified; a claim beyond NOT SHOWN; an uncited figure; any error of a script | fix before submission |
| Should fix | warnings of the scripts; a symbol defined late; a callout too many; a repeated sentence | fix, or record the reason in the report |
| Judgment | notes of the scripts; hits of the prose lint; preferences of form | decide and move on |

### Step 5. Write `paper-state/audit.md`

The script writes the tables; add the reading passes and the independent reading below them.

```
# Audit of <file>, <date>, version <tag or hash>

## Part checks            (from audit.py)
## Size                   (from audit.py)
## Cross-checks           (from audit.py)
## Reading passes
| Pass | Finding | Where | Smallest fix | Part |
## Independent reading
Claim as read: <their sentence>      RESULT: <the brief's sentence>
| Objection | Answer: change, NOT SHOWN, or reply |
## Blocking
## Not checked, and why
```

Run the audit again after the fixes, until nothing is blocking. Keep the last report with the record of the submission.

### When rules pull in different directions

Accuracy first, then the venue's requirements, then consistency, then polish. An inconsistency is never resolved by picking the more favourable value: find which one is right.

## Checks

1. **Final files**: the audit ran on the files that will be sent, built from a clean folder.
2. **All scripts**: every part check ran, or its absence is explained; `--online` was used for the references.
3. **No blocking item** remains.
4. **Reading passes**: all eleven were done, each with its findings recorded.
5. **Independent reading**: done, with the reader's claim sentence compared with RESULT; or stated as not done.
6. **Fixes in the owning part**: every change was made through the part that owns the rule, and the state files were updated first where the change touches them.
7. **Limits re-verified** on the venue's page, on the day.
8. **Report kept**: `audit.md` with date and version.

## Report

Reply in the user's language. Lead with what blocks:

1. **Blocking items**, each with place, fix and owning part.
2. **Should fix**, in order of effect on the reader.
3. **The claim as read** by the independent reader, beside RESULT.
4. **Not checked**: what was skipped and why; what only the authors can confirm.

Propose only. The audit never edits the manuscript.

## Example (invented)

`python scripts/audit.py main.tex --supp supplement.tex --brief ../brief/brief.md --repro ../methods/repro.md --require data competing contributions`, run in `examples/supplement/`, reports for that mock manuscript:

- part checks: eleven pass, among them the house rules with one note to review (the colon of the contents line); `methods` fails with six items that the manuscript does not state;
- cross-checks: seven errors for placeholder images and placeholder references; two errors for the missing statements on competing interests and contributions;
- blocking: all of the above.

An earlier version of the same file was also flagged by `duplication`: its conclusion shared the words "as the inverse sine of the tilt angle" with the abstract. The sentence was reworded through `parts/conclusion.md`, and the flag went away.

## Relation to other parts

- **Every part** hands the audit the tests it could not finish on a single section; the table of Step 1 and the passes of Step 2 are those checks.
- **Brief, outline, notation** are the references against which the passes compare. A finding that shows one of them to be out of date is fixed there first.
- **Submit** (`parts/submit.md`) starts only when nothing is blocking, and keeps the report.

## What this part cannot do

It cannot tell whether the physics is right, whether the result is new, or whether referees will be convinced. It finds disagreement and absence. A paper can pass every check here and be wrong.

## Sources

The studies and journal rules behind these choices are in `references/audit-submit-evidence.md`; read it when you need to explain a choice.
