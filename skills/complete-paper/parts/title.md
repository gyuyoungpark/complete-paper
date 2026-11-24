# Title

Stage B · Reads: `brief.md`, `venue.md`, `notation.md`, abstract, introduction, conclusion, main figure captions · Writes: the title (typeset and plain-text versions), the abstract patch

A good title is one specific claim written in standard terminology:

```
[what was shown] + [in which system] + (how, only when the method is the point or bounds the claim)
```

A title has two jobs. It has to be **found**: people and AI literature agents search with the terms a field already uses. And it has to **survive triage**: an agent typically generates queries, retrieves, then decides from the title and a snippet whether to open the paper at all, and a person scanning a list does the same. Every rule below serves one of those jobs, under one constraint: claim no more than the paper shows.

## Modes

The checks are the same in each mode.

- **Write** (propose): no title yet, or the user wants new candidates.
- **Revise** (compare): the user supplies candidates; rank them.
- **Audit**: one existing title; report pass/fail per check and the smallest fix.

In Revise and Audit, skip Step 2 unless every given title fails; then propose replacements.

## Inputs

1. `brief.md` (the claim sheet): RESULT, SYSTEM, METHOD, EVIDENCE, NOT SHOWN, and under History the title of any version that is already public. If it does not exist, build a minimal one first (`parts/brief.md`) from the abstract, the last paragraph of the introduction, the conclusion and the main figure captions. With only the user's description, work from that and say so. Do not infer results that are not written down; a title built on a guessed result is an overclaim. With neither a manuscript nor a stated result, run only the form and plain-text checks and ask for the abstract.
2. `venue.md`: the title's length cap, capitalization, and rules for acronyms and punctuation (see "Venue rules").
3. The abstract, if it exists. The title is written after it, and the two share their search terms.

A title carries one claim: RESULT of the brief. If the manuscript reports several unrelated results, the brief is not finished; ask which one the paper is about.

## Steps

### Step 1. Write the search queries first

If the abstract part already wrote search queries, start from those. Otherwise write 3-4 queries that someone looking for this result (not this paper) would type: a researcher in a search box, or an agent turning a question into keywords. These are the words the title must contain. Writing them first keeps the title from drifting into the authors' private vocabulary.

Use the field's standard term for each concept. When two terms compete and you can search, check which one recent titles in the target venue use; otherwise flag the term as unverified.

### Step 2. Draft 5-8 candidates

**Form**
- Write a noun phrase that contains the result. No questions, and no full sentences with a main verb ("X enhances Y"). Turn the verb into a nominalization or a participle:
  - "X switches Y" -> "Switching of Y by X" or "X-driven switching of Y"
  - "X suppresses Y" -> "Suppression of Y by X"
  - "Y has no X" -> "Absence of X in Y"

  A question withholds the answer that triage needs. The ban on full sentences is a house rule of this skill and the norm in physics and engineering venues; break it only when the user or the venue asks.
- Lead with the distinguishing nouns. Lists, alerts and reference lists cut off the tail.
- There is no target length. Delete filler, then stop. If a venue cap forces a cut, drop the method first, then modifiers; keep the result and the system.
- Use a colon only where the structure needs one (`Name: descriptive phrase`).
- Use the venue's capitalization; if the venue is unknown, sentence case.

**Content**
- State the result and its direction. Cut openers that carry no information: "Study of", "Investigation of", "Analysis of", "On the", "Towards", "Insights into", "Novel", "New", a leading "A/An/The".
- Replace frames that hide the direction ("Effect of X on Y", "Role of X in Y", "Impact of X on Y") with what happened ("Enhancement / Suppression / Sign reversal of Y by X"), unless the paper really maps a dependence with no single direction.
- Use standard terminology only. No coined terms and no author-made acronyms standing alone: nobody searches for a name they have not heard yet. If the paper introduces a name, write `NAME: descriptive noun phrase` so that the descriptive half can be found. Acronyms the venue's readers already search by are fine; when unsure, spell it out and put the acronym in the abstract's first sentence.
- A hook, pun or metaphor cannot stand alone, for the same reason. If the user wants one, put the descriptive phrase after a colon.
- Do not pack synonyms or keywords into the title. They belong in the abstract (see the abstract patch in the Report).

**Scope: claim only what was shown**
- Every content word must map to a line of the claim sheet in `brief.md`.
- Match the evidence word to the evidence. "Observation of", "Measurement of" and "Demonstration of" are for experiments. For simulation or theory use "Prediction of", "Theory of", "Model of", "Micromagnetic simulation of", or name the phenomenon and let the abstract's first sentence state the method.
- Name the specific material when the claim is specific to it. Name the class ("antiferromagnets") only when the evidence covers the class.
- Magnitude words ("giant", "ultrafast", "robust", "universal", "efficient") need a number in the abstract that the field would describe that way. Prefer the measurable class: "sub-nanosecond", "room-temperature", "field-free". Do not claim "first".

**Plain-text survival**
- Formulas and symbols must be searchable as plain text: `Mn3Sn`, not `Mn$_3$Sn`; `alpha-RuCl3`, not a Greek glyph; no math. Bibliographic databases store titles as plain strings, so raw TeX is what gets indexed.
- When the two differ, give both renderings: the typeset title for `\title{}` and an ASCII title for submission forms. arXiv's title field is ASCII-only according to its help pages; TeX math is accepted there but is harvested as raw TeX.

**Other paper types**

| Type | The title must carry |
|---|---|
| Method or software | what it computes or enables + the domain; `Name: descriptor` if it has a name |
| Dataset or benchmark | what is measured + scope; `Name: descriptor` |
| Review or perspective | topic + scope; the word "review" or "perspective" is allowed |

### Keep the title stable across versions

If a version is already public, keeping its title is the default. Indexers commonly link a preprint to its published version by matching titles and authors, so a changed title can leave two records with the citations split between them. Recommend a change only when the public title is wrong (it overclaims, names the wrong system, or breaks a venue rule), and then tell the user to update the preprint record (title, journal reference, DOI) at the same time.

An open-access copy under the identical title is a precondition, not a refinement: some agents read only open-access text, and no wording compensates for a paper they cannot open.

### Venue rules

Venue rules override the style choices above. Look up the target venue's author guidelines when you can (length cap, acronyms, capitalization, punctuation) and skim about 20 recent titles from it for its habits (colon use, name-first titles, case). Otherwise mark the venue check as unchecked.

Example, from the APS Journals Style Guide (February 2026): titles are self-contained, simple and concise; no nonstandard abbreviations, acronyms or terminology; no leading articles; sentence case in PRB, PRE, PR Applied and most APS journals, title case in PRL and the PRX family. Guidelines change, so verify instead of trusting this paragraph.

### When rules pull in different directions

Accuracy first (never overclaim to satisfy a form rule), then venue rules, then keeping a public title, then findability (standard terms, system, result), then style.

Where effort pays off, in order (a judgment, not a measurement): an open-access copy with a stable title; standard terms + system + result, verified with the query test; names written as `NAME: descriptor`; plain-text formulas; no hype.

## Checks

Test every candidate and drop the failures:

1. **Query coverage**: the key terms of every Step 1 query appear in the title or in the first two sentences of the abstract. List what is missing.
2. **Triage**: from the title alone, can you say what was found and in what system? A title that only names a topic fails.
3. **Evidence**: every content word is backed by the claim sheet, and the evidence word matches.
4. **Form**: no main verb, no question mark, no empty opener, no nonstandard acronym standing alone.
5. **Plain text**: the ASCII version is unambiguous and contains the searchable formula or name.
6. **Venue**: length cap, capitalization and acronym rules are met, or marked unchecked.
7. **Public title**: the candidate matches the public title, or the change is justified (see "Keep the title stable across versions").

## Report

Reply in the user's language; write titles in the manuscript's language. Keep it short:

1. **Claim sheet**: the five fields of `brief.md`, one line each.
2. **Queries**: the 3-4 from Step 1.
3. **Candidates**: the top three, ranked. For each, the title (typeset and ASCII if they differ) and one line on what it claims and what it gives up.
4. **Recommendation**: one title and one sentence of reasoning.
5. **Abstract patch**: terms that did not fit the title and should appear in the abstract's first two sentences (synonyms, acronym expansions, alternative material names), written as a concrete phrase the user can paste. Paper-embedding retrievers encode title and abstract together, so the overflow belongs there.
6. **Flags**: overclaim risk, change from a public title, unverified terminology, unchecked venue rules.

In Revise or Audit mode, replace item 3 with a table of the given titles against the checks, followed by the smallest fix for each failure.

Propose only. Edit `\title{}` or metadata when the user asks, and then search the project for the old title and update every occurrence: main text, the title page of the supplement, cover letter, submission metadata, the README of the data package.

## Relation to other parts

- **Brief** (`parts/brief.md`) supplies the claim sheet; the title never says more than RESULT within NOT SHOWN.
- **Abstract** (`parts/abstract.md`) is written first; the title reuses its search queries (Step 1) and sends it the abstract patch.
- **Venue** (`parts/venue.md`) supplies the cap, the case and the acronym rules.
- **Supplement** (`parts/supplement.md`) carries the same title on its first page.
- **Submit** (`parts/submit.md`) uses the ASCII title in forms and preprint metadata.
- **Audit** (`parts/audit.md`) checks that title, abstract and conclusion state the same claim.

## Examples (invented, for illustration)

| Before | Problem | After |
|---|---|---|
| A study of anomalous dynamics in antiferromagnets | topic only; empty opener; class not shown | Sub-nanosecond field-free switching of a noncollinear antiferromagnet by spin-orbit torque |
| Strain enhances the anomalous Hall effect in `Mn$_3$Sn` films | full sentence; TeX in the title | Strain-enhanced anomalous Hall effect in Mn3Sn thin films |
| Can interfacial DMI stabilize skyrmions without a field? | question; answer withheld; acronym | Zero-field skyrmion stabilization by interfacial Dzyaloshinskii-Moriya interaction in Pt/Co/Ir multilayers |
| Observation of magnon Bose-Einstein condensation in a YIG disk (simulation-only paper) | evidence word claims an experiment | Micromagnetic prediction of magnon Bose-Einstein condensation in a YIG disk |
| SPINNET | a name alone cannot be searched | SpinNet: a neural-network surrogate for micromagnetic simulation |

## Sources

The studies behind these choices, and how far each one goes, are in `references/title-evidence.md`. Read it before explaining a choice, and do not tell the user that a title will raise citations or visibility to AI tools: no study supports a promise like that.
