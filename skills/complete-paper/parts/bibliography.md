# Bibliography

Stage C · Reads: `venue.md`, every citing sentence and `[CITE: ...]` placeholder in the manuscript, the `.bib` files or the `thebibliography` block, `brief.md`, `outline.md`, the sources the user supplied · Writes: the verified reference list, `paper-state/refcheck.md`

A reference list does two jobs. It lets a reader find and check the source behind every statement that is not the authors' own, and it places the paper among the work of others. Both jobs fail in the same three ways: a reference that does not exist, a reference that does not match its record, and a reference that does not say what the sentence says it does. Language models produce all three. Human authors, copying references they have not read, produce the last two. Peer review does not reliably catch any of them.

One rule governs this part: **nothing enters the list from memory**, the agent's or the author's. Every reference is tied to a record retrieved in this session, and every citation to a passage that was read.

Each reference passes four checks, in this order, because a later check means nothing until the earlier one holds:

| # | Check | Question | Passes when |
|---|---|---|---|
| 1 | Exists | Is there such a work? | A record was retrieved in this session from the DOI resolver, arXiv, the publisher or a field index |
| 2 | Matches | Is this entry that work? | Title, authors, journal, volume, first page or article number and year agree with the record, and the DOI or arXiv number resolves to this work |
| 3 | Supports | Does it say what the sentence says? | The passage was found in the source, read at the depth the claim needs |
| 4 | Formatted | Will it print correctly for this venue? | The entry is complete, compiles without warnings and follows `venue.md` |

A fifth question concerns the list as a whole: **coverage** (Step 4).

## Modes

- **Write** (build): sentences carry `[CITE: ...]` placeholders, or the list is incomplete. Find the works, verify them, add them.
- **Revise** (retarget): the checks have passed; reformat the list for another venue.
- **Audit** (verify): a list exists. Run every check and report pass/fail with the smallest fix; change nothing.

## Inputs

Read before checking:

1. `venue.md`: citation form in the text, reference format, any cap on the number of references, the "et al." rule, whether titles are printed, how preprints, datasets, software and unpublished work are cited, and whether the list must sit inside the `.tex` file.
2. The manuscript: every sentence that carries a citation or a `[CITE: ...]` placeholder.
3. The `.bib` files, or the `thebibliography` block.
4. `brief.md`: RESULT and NOT SHOWN, for the closest earlier work.
5. `outline.md`: the claim chain, for the coverage audit.
6. Sources the user supplied: PDFs, a reading list, a reference-manager export.

## Steps

### Step 1. Run the mechanical check

```
python scripts/ref_check.py main.tex --bib refs.bib --online --ledger refcheck.md
```

- Offline, it reports citations without an entry, entries never cited, duplicate keys and duplicate works, leftover placeholders, incomplete or malformed entries, citations naming more than four works, the spread of publication years and the authors who appear most often.
- With `--online`, it resolves every DOI and arXiv number, compares title, authors, journal, volume, first page and year with the record, reports retractions, corrections and published versions of preprints, and searches Crossref for entries that have no identifier.
- `--ledger` writes the working file of Step 6. `--authors "Family, G."` adds the share of the authors' own work. `--mailto` sends an address to Crossref in exchange for higher rate limits: use the user's address only if the user agrees.
- If the shell cannot reach the network, run it without `--online` and do checks 1 and 2 by opening `https://doi.org/<DOI>` or the arXiv page with the web tools available. If no route exists, mark the references `unchecked` and give the user the command.

A flag from the script is a lead, not a verdict. It cannot do check 3 at all.

### Step 2. Does it exist, and is the entry that work? (checks 1 and 2)

**Where a record counts.** In order: the DOI resolver or the publisher's page; arXiv; a field index such as NASA ADS, INSPIRE-HEP, PubMed, DBLP or MathSciNet; a library catalogue for a book; the university repository for a thesis. A search-engine hit, a citation in another paper and an AI answer are leads to a record, not records. A language model and its output are never cited as a source: cite the works it pointed to, after opening them.

**What to look for.** Fabricated references take four forms:

| Form | Looks like | Caught by |
|---|---|---|
| Nothing exists | Plausible authors, title and journal; no record anywhere | The DOI does not resolve; no match by title |
| Mixed | Real authors with a title they did not write; a real title with other authors, journal or year | Comparing every field with the record |
| Borrowed identifier | A real DOI or arXiv number that belongs to another paper | Comparing the record's title and authors with the entry |
| Placeholder | "Firstname Lastname", "XXXX", an empty field | Reading the entry |

A plausible, on-topic title is not evidence that the work exists.

**What to do with each outcome.**

- **Match.** Nothing to do.
- **A field differs.** Open the publisher's page or the PDF and correct the entry from it. The registry is evidence, not truth: a record can carry a deposit date in place of the publication year or an affiliation among the authors, and its BibTeX export can lack the article number. Where the entry and the record disagree, the source decides.
- **The identifier belongs to another work.** The entry has the wrong identity. Search for the intended work by its title; if it cannot be found, treat it as not found.
- **Not found.** Search for the exact title with the tools available. Books, theses, reports, old papers, very recent papers and non-English journals are often missing from the indexes, so "not found" is not "fabricated". If a record turns up, write down where it was seen. If none does, mark the reference `unverified` and ask the user for the source: a PDF, the first page, a link.
- **Unverified at the end.** It does not go to submission. Either the user supplies the source, or the reference is removed and its sentence is reworded or dropped. Never keep a reference because it looks right.

**Keep the record current.**

- A retracted work is not cited as support. Cite it only to discuss the retraction, and say so in the sentence. Treat an expression of concern as a reason to find another source.
- Cite a correction or erratum with the paper when the corrected content is what the sentence uses.
- Cite the published version of a preprint, unless the content used appears only in the preprint. `venue.md` says whether to add the arXiv number.
- The version cited is the version read. If a number differs between versions, cite the one the number came from.

### Step 3. Does it support the sentence? (check 3)

The unit of checking is the **citation**: one sentence paired with one reference. `refcheck.md` lists every such pair. For each one:

1. **Name the function** of the citation.

| Function | The reference is cited as | What must be read |
|---|---|---|
| credit | the origin of an idea, a method or a first observation | the original itself, not a later paper that cites it |
| support | evidence for a statement of fact | the passage that states it; an abstract only if it states the result explicitly |
| source | where a value, parameter, dataset, figure or code was taken from | the full text; record the table, figure, equation or page |
| method | the procedure this paper follows | the part that describes the procedure |
| contrast | a result or explanation that disagrees or competes with this paper | the full text, so that the disagreement is stated fairly |
| background | a review or book for orientation ("for a review see") | the abstract or the contents |

2. **Find the passage** that does this job, and record how far the source was read: `full`, `abstract` or `title`. An abstract cannot confirm a number, a sign, a condition or a detail of method. A title confirms nothing.
3. **Give a verdict**: `yes`; `partly`, when the source shows something narrower, in which case the sentence is reworded to what the source shows; `no`, in which case the citation is removed or replaced; `unchecked`, when the source could not be opened, in which case ask the user for it.

Errors to look for:

- The sentence generalizes beyond the source: another material, temperature range, geometry or regime.
- The source reports the claim as someone else's result. Cite the original, and read it.
- A review is cited for a finding. Cite the original; keep the review for orientation.
- The right group, the wrong paper.
- The verb does not match the cited work's evidence: a prediction cited as an observation, a simulation as a measurement.
- A value was copied with a different definition, unit or sign convention (see `parts/notation.md`).
- The source says the opposite, or adds a qualification that the sentence drops.
- A paper is cited for a method it used but did not introduce.
- Several claims share one citation at the end of the sentence, and the reader cannot tell which claim each reference supports.

Placement and grouping:

- Put each citation directly after the statement it supports. When a sentence makes two claims from two sources, each source sits by its claim. The form of the marker and its side of the punctuation come from `venue.md`.
- A group of references needs a stated common property: "observed in Mn3Sn [1,2] and Mn3Ge [3]", not "has attracted much attention [1-12]".
- One to three works per statement is the default. More are justified when the statement is about how many independent groups found the same thing. The script flags a citation that names more than four works: split it by what each subset supports, or cut it to the works that carry the statement.
- Cite the evidence against a claim as well as the evidence for it. When the literature disagrees, the sentence says so.

When a language model drafted a sentence and its citation together, the pair is unchecked, however good it looks. Never write a sentence around a reference that has not been opened.

### Step 4. Coverage: who belongs in the list

**A reference earns its place by the sentence it supports. Within that limit, prefer the list that covers every independent line of work the paper rests on or competes with.** Breadth comes from coverage, never from padding.

Coverage matters beyond fairness:

- Editors often look for referees among the authors of the cited works. A referee whose directly relevant paper is missing will say so.
- Citation indexes list the paper under "cited by" for every work it cites, which is one way the cited groups come across it.
- Studies that link longer reference lists to more citations show correlations that are weak and differ by field, and one found no significant effect. Do not promise citations, and do not add a reference for this reason alone.

Audit each claim of the claim chain and each paragraph of the Introduction and Discussion:

1. **Lines of work.** List what the statement rests on: the origin, the decisive evidence, the current state, the competing explanation or method, and the earlier results closest to RESULT.
2. **Independent groups.** For each line, are the groups that established it cited: not one group only, not only the best known, not only the authors' own? Two papers that share a senior author count as one group.
3. **Closest earlier work.** The papers most similar to RESULT are cited, and the text says how this paper differs. This is the omission a referee notices first.
4. **Recent work.** The newest directly relevant papers and preprints are cited. Use the year profile from the script.
5. **Tools and data.** Software, datasets and published parameter values are cited in the form their authors ask for.
6. **Concentration.** The script lists the authors who appear most often and the share of the authors' own work. A list that leans on one group, or on the authors, needs a reason.

Find candidates by searching each line of work, starting from the search queries already written for the title and abstract. Each candidate must answer one question: **which sentence does it support, and is that sentence weaker or less fair without it?** If the only answer is that its authors might notice the paper, leave it out.

Limits that keep the argument strong:

- No reference without a sentence that needs it, and no sentence written to host references.
- For each line of work: the origin, the strongest evidence, and the most recent paper or a review. Not every paper on the topic.
- The authors' own work is cited where a reader needs it to follow or reproduce the paper, and not otherwise. Report the share.
- Nothing is added to please an editor, a likely referee or the venue.
- Nothing is cited that has not been read at the depth its function needs.
- Over the venue's cap: cut background and grouped citations first. Keep the closest earlier work, contrary evidence, and the sources of values and methods.
- Under the usual length for the venue: do not pad. Run the audit again; if it finds nothing, the list is complete.

Present every addition as a proposal with the sentence it would support. The user knows the people of the field and decides.

### Step 5. BibTeX and format (check 4)

**Take entries from the record, then repair them.** `curl -LH "Accept: application/x-bibtex" https://doi.org/<DOI>` returns an entry for most DOIs; INSPIRE-HEP, NASA ADS and publishers export entries too. A raw export needs repair: the title is in the publisher's capitalization with no braces, the journal name is not abbreviated, an article number can be missing, page ranges use a Unicode dash, the month can be an abbreviation BibTeX does not know, and a key built from a non-ASCII name is garbled. An entry from a search engine or from an AI answer is compared with the record before it is used.

**One work, one entry, one key.** Use one key pattern throughout, for example `Nakatsuji2015`. Copy keys from the `.bib` into the text; never retype them.

| Field | Rule |
|---|---|
| author | `Family, Given and Family, Given`. Give all authors and let the style shorten the list. A collaboration goes in braces: `{ATLAS Collaboration}`. Never type "et al." |
| title | As published. Brace what must keep its capitals or its math: `{H}all`, `{Mn}$_3${Sn}`, `{$T_c$}`. Do not brace the whole title |
| journal | One form for one journal throughout: the abbreviation the venue uses, unless the style abbreviates |
| volume, pages | The first page or the article number, as the record gives it. Never invent a page range for an article number. Write ranges with `--` |
| year | The year of the version cited |
| doi | The bare DOI, without `https://doi.org/` |
| eprint | The arXiv number, with `archivePrefix = {arXiv}` |
| type | `@article`, `@book`, `@incollection`, `@inproceedings`, `@phdthesis`; `@misc` for preprints, software and datasets, with version, repository and DOI or URL |

**Compile and read the log.** Run BibTeX or Biber. The `.blg` file has no warnings and the PDF has no "?". Every listed work is cited and every citation is listed. Where the venue numbers its references, the numbers follow the order of first citation.

**Format for the venue.** `venue.md` is the authority. The points on which venues differ:

- the citation form in the text (bracketed numbers, superscripts, author and year) and the order of the list;
- whether titles are printed, and how many authors are named before "et al.";
- journal abbreviations, and first page versus page range;
- how preprints, datasets, software, theses and unpublished work are written, and which of them may appear in the list at all;
- whether remarks may sit in the list as endnotes, and whether they count toward the length;
- a cap on the number of references, and what is exempt from it;
- whether the list must be pasted into the `.tex` file, and whether references cited only in the supplement must also appear in the main list.

A list typed by hand as `\bibitem` entries is checked by the script as well. Move it to a `.bib` file when the user agrees: typed lists are where errors survive.

### Step 6. Write `refcheck.md`

`--ledger` writes the frame and fills the first table; the rest is filled by hand. The script does not overwrite an existing file unless `--force` is given, so the hand-filled columns are safe.

```
# Reference check
Written by ref_check.py on <date>; comparison with the record: run | not run.

## References
| Key | Identifier | Exists | Matches record | Seen at | Notes |
  Exists: yes | not found | unchecked
  Matches record: yes | differs | MISMATCH | unchecked, with RETRACTED added where it applies; a dash when there is no record

## Citations
| # | Where | Key | Sentence | Function | Read | Supports | Action |

## Coverage
| Line of work | Cited | Missing or thin | Proposal |

## Open items
```

"Exists: yes" means that a record was retrieved in this session, by the script or by hand, and "Seen at" says where. Nothing is marked from memory.

### When rules pull in different directions

Accuracy first: a shorter verified list beats a longer unverified one. Then support: every citation does a job. Then the venue's hard limits. Then fairness: the closest earlier work and contrary evidence are the last things cut. Then breadth.

## Checks

1. **Nothing from memory**: every reference has an identifier, or a place where its record was seen in this session.
2. **Exists**: no reference is `not found` or `unchecked` without the user's decision on it.
3. **Identity**: every field matches the source; every DOI and arXiv number resolves to the cited work.
4. **Current**: no retracted work is cited as support; published versions and corrections are cited as Step 2 says.
5. **Function and depth**: every citation has a function and was read at the depth that function needs.
6. **Support**: no citation has the verdict `no`; every `partly` led to a reworded sentence; every `source` value was located in the full text.
7. **Originals**: credit goes to the original work, and the original was opened.
8. **Placement**: each citation sits by its statement; no group of more than four works lacks a stated common property.
9. **Balance**: the closest earlier work and contrary evidence are cited, and the text says how this paper differs.
10. **Coverage**: each line of work has its independent groups and its recent papers.
11. **No padding**: every reference supports a sentence that needs it; no sentence exists to host references; the own-work share and the most frequent authors are reported.
12. **BibTeX**: keys match in both directions; no duplicates; required fields are present; the list compiles without warnings.
13. **Venue**: form, order, cap and the rules for special items follow `venue.md`.
14. **Placeholders**: no `[CITE: ...]` remains.

## Report

Reply in the user's language; keep reference entries and anything proposed for the manuscript in the manuscript's language. Keep it short:

1. **Counts**: references, citations, how many passed each check, and whether the comparison with the record ran.
2. **Failures** by check, each with the smallest fix.
3. **Proposals**: additions with the sentence each supports; removals with the reason; sentences to reword.
4. **Open items**: sources the user must supply and decisions the user must make.

Propose only. Edit the manuscript and the `.bib` file when the user asks.

## Example (invented; the physics is a placeholder and the letters stand for references that do not exist)

Before:

> Noncollinear antiferromagnets have attracted great attention [A-L]. The octupole order of Mn3Sn can be switched by spin-orbit torque without a magnetic field [M,N].

Fails: the first sentence exists to host twelve references and states nothing a reader can check. In the second, [M] switched the order with a bias field applied and [N] is a prediction, yet the sentence presents field-free switching as an observed fact supported by both.

After:

> A large anomalous Hall effect was observed in Mn3Sn [A] and Mn3Ge [B,C], and the octupole order of Mn3Sn was switched electrically with an in-plane bias field applied [M]. Switching without a bias field has been predicted for tilted kagome planes [N].

| Key | Function | Read | Supports | Action |
|---|---|---|---|---|
| A | credit | full | yes | none |
| M | support | full | partly | sentence reworded: the switching needed a bias field |
| N | support | abstract | partly | verb changed to "predicted"; full text requested from the user |
| D-L | background | title | unchecked | removed with the hosting sentence; two return later, where a sentence needs them |

## Relation to other parts

- **Introduction** (`parts/intro.md`) leaves `[CITE: ...]` placeholders and records a literature check for the gap. This part resolves the placeholders and reuses that check for the closest earlier work.
- **Venue** (`parts/venue.md`) supplies every rule of format.
- **Notation** (`parts/notation.md`): a value taken from a reference is converted to this paper's symbols and units, and the conversion is noted.
- **Methods** and the data availability statement: software, data and parameter sources are `source` and `method` citations; datasets and code named in an availability statement go in the list where the venue wants them there.
- **Audit** (`parts/audit.md`) reruns the script on the final files.

## What not to promise

- That a reference which passes checks 1 and 2 supports its sentence. Identity is not support.
- That "not found" means fabricated, or that "found" means correct.
- That a broader list brings citations.

## Sources

The journal rules, studies and registry behaviour behind these choices, and the points on which sources differ, are in `references/references-evidence.md`; read it when you need to explain a choice.
