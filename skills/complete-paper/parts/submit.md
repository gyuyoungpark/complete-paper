# Submit

Stage D · Reads: `audit.md`, `venue.md`, `intake.md`, `brief.md`, the audited manuscript · Writes: the submission package, the form entries, the cover letter, `paper-state/submission.md`

Submission turns the audited manuscript into the files and the form entries that the venue asks for. Nothing about the science changes here; what can go wrong is the form, and a paper returned for its form loses days.

It has two jobs:

- **Accepted by the system at the first attempt.** The right files, in the right formats, with every field of the form filled as the manuscript says.
- **What is sent is what was audited.** One frozen version, recorded, so that every later question about "the submitted version" has an answer.

Rule: **the agent prepares; the authors submit.** Submission is an act of all authors. The agent does not press the final button unless the user asks for exactly that, after seeing the package.

## Modes

- **Write** (prepare): a first submission to the venue in `venue.md`.
- **Write** (preprint): a posting on a preprint server, before, with or after the submission.
- **Audit**: check a package that already exists; change nothing.

Revise is not used. The reply to referees and the files of a resubmission are outside this version of the skill; the file checks below still apply to them.

## Inputs

1. `paper-state/audit.md`: nothing blocking. If there is no audit, run it first (`parts/audit.md`).
2. `venue.md`, the Submission group: template, review format (line numbers, spacing, columns), anonymization, cover letter and any required justification, suggested referees, forms and checklists, preprint policy, licence, charges.
3. `paper-state/intake.md`, and the Record section of `brief.md` that summarizes it: authors and affiliations, contributors, funding, acknowledgments, competing interests, data and code, AI tools, history.
4. The venue's submission page, today.

## Steps

### Step 1. Re-verify the hard limits today

Open the venue's own pages again: length and how it is counted, abstract cap, formats of files, mandatory statements, the template version. Guidelines change, and a limit recorded three months ago may not hold. Update the date and the status in `venue.md`. A limit that is now exceeded goes back to the part that owns it.

### Step 2. Freeze the version

Tag the version, or copy the project into a dated folder. From here on, a change means a new version and a new run of the audit's scripts.

### Step 3. Build the review copy

- **Template and class** of the venue, in its current version, with the options for review.
- **Line numbers**, spacing and columns as the venue asks for review: referees cite lines. In LaTeX: the `lineno` package with `\linenumbers`, or the class option where the class has one.
- **Figures and tables** where the venue wants them for review: in place, or at the end with captions.
- **Anonymized review**: no byline, acknowledgments or funding in the review copy; the authors' own work cited in the third person; no author names in file names or in the properties of the PDF; links to code replaced by anonymized ones. The removed parts are kept for the final version, from `intake.md`.
- **Required statements** in the manuscript: each one that `venue.md` lists is in place, worded by the authors from `intake.md`. Where the venue asks for an AI-use statement, draft it from what was actually done, for the authors to confirm (ground rule 9 in `SKILL.md`). A statement with nothing behind it in the intake stays a TODO marker. `audit.py --require` checks that each one is present.
- **The supplement** as its own file, with its title page, in the format the venue takes; a description file where a deposit requires one (`parts/supplement.md`).

### Step 4. Clean the sources

- **Only what is used.** Every figure, input and bibliography file that the sources use, and nothing else: no old versions, no unused figures, no auxiliary files, no letters.
- **No comments, no switched-off text.** Sources are read by production staff, and preprint servers publish them. Remove comments, text after `\end{document}`, and blocks disabled with `\iffalse`.
- **Paths**: relative, inside the folder, with the exact case of the file names, without spaces.
- **Bibliography** in the form the system takes: the `.bib` files, or the `.bbl` named like the main file, or the list typed into the source.
- **Cross-file references** made with `xr` replaced by the printed numbers where main text and supplement are built separately by the receiving system; then run `eq_refs.py` and `supp_check.py` once more.
- **Fonts embedded** in the PDF, and none of Type 3 from figures (`parts/figures.md`, export).

```
python scripts/submit_check.py main.tex --supp supplement.tex --line-numbers
python scripts/submit_check.py main.tex --anonymous --authors "Given Family" ...
python scripts/submit_check.py main.tex --pack submitted/2026-11-23 --compile
```

`--pack` writes a copy that holds only the files the sources use, with comments removed, and prints a checksum for each; `--compile` builds that copy, which proves that it is complete.

### Step 5. Prepare the entries of the form

The form asks again for what the manuscript says. Every entry is copied from the manuscript, never retyped from memory.

- **Title**: the typeset form and the plain form (`parts/title.md`).
- **Abstract** as plain text: no macros, no citations, formulas written so that they survive a text field. `submit_check.py --plain` prints both, with their lengths and any character outside ASCII.
- **Authors**: names, order, affiliations, addresses and identifiers exactly as in the byline.
- **Statements**: data availability, competing interests, funding, use of AI tools, word for word as in the manuscript.
- **Subject areas or keywords** from the venue's own list; the queries of the title part are the starting point.
- **Suggested and excluded referees**, where the venue asks: people who know the subject and have no tie to the authors (no co-author of recent years, no colleague of the same institution, no former supervisor or student); a reason for each exclusion. The user chooses; the agent may list authors of the works in PRIOR as candidates and must not vouch for anyone.
- **Related manuscripts**: a companion paper, an earlier submission, a preprint.

### Step 6. Write the cover letter

One page. The editor reads it to decide whom to send the paper to, or whether to send it at all.

| Paragraph | Content |
|---|---|
| 1 | What is submitted: title, article type, venue |
| 2 | The result in two or three sentences, for an editor who is a physicist and not a specialist: the question, the answer, the evidence. From `brief.md`, in new sentences; not the abstract pasted |
| 3 | Why this venue: the result set against the venue's stated criteria (`venue.md`), in the venue's own terms, with the specific readers who need it |
| 4 | History and relations: preprint, earlier submission and its outcome, a companion paper, overlap with earlier publications |
| 5 | Requests and statements that the venue asks for: referees to consider or to avoid, confirmation that all authors approve and that the work is not under consideration elsewhere |

- **No praise.** "Novel", "significant", "of broad interest" are the editor's conclusions. Give the fact that would lead to them.
- **No claim beyond the paper.** The letter is held to NOT SHOWN like every other part. It states no limitation, and it gives the gap as a need (ground rule 10).
- **Where the venue asks for a separate justification** of a fixed length, write it as its own text: the criteria of the venue, each answered with one fact.
- Addressed to the editor by role. Signed by the corresponding author, with contact details.

### Step 7. Preprint

- **Policy first**: what the venue allows, and when (`venue.md`).
- **Same title** as the submitted version, and kept afterwards (`parts/title.md`): a changed title can split the record.
- **Metadata**: every author; the abstract as plain text within the server's limit; a comment with pages and figures and, if wished, "submitted to"; the category that the paper's readers follow, with cross-lists; the licence chosen with the venue's policy in mind.
- **Sources are public.** Post the cleaned copy of Step 4. `submit_check.py --arxiv` adds the checks for arXiv: abstract length, bibliography files, mixed figure formats, `xr`, comments.
- **The supplement** goes into the same posting, as part of the PDF or as an ancillary file.
- **After publication**: add the journal reference and the DOI to the preprint record.

### Step 8. Check the built file

Open the PDF that the venue's system builds, not the local one, and go through every page: fonts, figures in place and legible, no "??", line numbers present, references complete, the supplement attached. Compare the page count with the local build.

### Step 9. Record the submission

Write `paper-state/submission.md`:

```
# Submission
Venue: <journal, article type>     Date: <date>     Manuscript number: <when assigned>
Version: <tag or folder>           Audit: <audit.md, date>
Files sent: <name, size, checksum>   (from submit_check.py --pack)
Form entries: <title, abstract, subject areas, statements: as entered>
Referees: <suggested, excluded, with reasons>
Cover letter: <file>
Preprint: <identifier, date, licence>
```

It is what the next round starts from.

### When rules pull in different directions

The venue's instructions first, then the agreement between the form and the manuscript, then cleanliness of the package.

## Checks

1. **Audit clean**: `audit.md` of this version has nothing blocking.
2. **Limits verified today** on the venue's pages, and `venue.md` updated.
3. **Version frozen** and named.
4. **Review format**: template, line numbers, spacing and placement of figures as the venue asks.
5. **Anonymized** where required: byline, acknowledgments, self-citations, file names, PDF properties.
6. **Clean sources**: only used files; no comments or disabled text; relative paths; bibliography in the accepted form; `submit_check.py` without errors.
7. **Builds from the package** alone.
8. **Form entries** equal the manuscript: title, abstract, authors, statements.
9. **Cover letter**: five paragraphs at most, no praise, nothing beyond the paper, history stated.
10. **Preprint**: policy checked; same title; cleaned sources; metadata complete.
11. **Built file read** page by page.
12. **Recorded** in `submission.md`.
13. **Statements**: every statement the venue requires is in the manuscript, worded by the authors; an AI-use statement is drafted where the venue asks for one, and the authors confirmed it.

## Report

Reply in the user's language. Keep it short:

1. **The package**: files with sizes and checksums; what was removed.
2. **Form entries** ready to paste: plain title, plain abstract, statements, subject areas.
3. **Cover letter.**
4. **For the authors to do or decide**: referees; licence; the preprint; anything the form asks that the Record does not answer.
5. **`submit_check.py`**: what it still reports.

Propose only. Do not submit, post or send anything unless the user asks for that step by name.

## Example (invented; the venue and the names are placeholders)

> Dear Editor,
>
> We submit the manuscript "Field-free switching of a tilted kagome antiferromagnet" for publication as a Letter.
>
> Dense memory built from the noncollinear antiferromagnet Mn3Sn calls for electrical switching without the in-plane magnetic field that experiments have used so far. We show by simulation that a tilt of the kagome plane, of the kind that films on miscut substrates already have, replaces the field. The current alone sets the final state, above a threshold that follows a one-line torque balance with no adjustable parameter.
>
> The result gives groups that grow these films a quantity to design, the tilt angle, and a formula for its cost in current. It should interest readers working on antiferromagnetic spintronics and on spin-orbit-torque memory.
>
> The work has not been published or submitted elsewhere. It is not yet posted as a preprint. All authors have approved the manuscript.
>
> Sincerely, B. Author (contact details)

The letter states the question, the answer and the evidence ("by simulation"), names the readers, and uses no word of praise. Whether the result is important enough for the venue is left to the editor, with the facts needed to judge.

## Relation to other parts

- **Audit** (`parts/audit.md`) must be clean before this part starts.
- **Venue** (`parts/venue.md`) holds every requirement and is updated here.
- **Title** (`parts/title.md`) and `intake.md` supply the entries of the form, unchanged.
- **Supplement** (`parts/supplement.md`) supplies the supplementary file and the data package, which must be public or shared with referees by now.
- **Brief** and `intake.md` record the history that the cover letter reports.

## What this part cannot do

It cannot see the venue's submission system, and it does not know a requirement that the venue's pages do not state. The built file of Step 8 is the only proof that the package was accepted as intended.

## Sources

The journal and preprint-server rules behind these choices are in `references/audit-submit-evidence.md`; read it when you need to explain a choice.
