# Audit and submission: studies, journal rules and this skill's own rules

Read this when you need to explain a choice made in `parts/audit.md` or `parts/submit.md`.

Checked 2026-11-23. Verify each entry against the current page before citing it elsewhere. Submission requirements change often.

## Why an audit across sections

- **Pitkin, Branagan and Burmeister, "Accuracy of data in abstracts of published research articles", JAMA 281, 1110 (1999).** Random samples of 44 articles from each of five general medical journals, and a consecutive sample from a sixth, were checked for data in the abstract that were inconsistent with the body or absent from it. The share of deficient abstracts ranged from 18% to 68% across the journals. The cross-check of numbers between abstract and body in `audit.py` exists because of this kind of finding. Medical journals, 1996 to 1997; no comparable count for physics was found.
- A later study in the same journal tested whether specific instructions to authors reduce such defects; it was seen here only as a search excerpt and is not relied on.

## What journals require at submission

- **APS, Physical Review Letters, Publishing Guidelines.**
  - Cover letter: the context of the results, a summary of the key findings, the submission history at Physical Review including any joint submission, and recommended or excluded referees.
  - A justification paragraph of 100 words, provided at submission, on why the paper meets the criteria of a Letter.
  - A PDF is sufficient for peer review; LaTeX source is preferred and Word is accepted; REVTeX and Word templates are provided.
  - Review is single-anonymized; the page mentions neither line numbers nor an anonymized manuscript.
  - A data availability statement is entered during submission; the disclosure of AI use is asked for at submission.
  - For a resubmission or transfer: the clean manuscript, a point-by-point response, a list of changes, a marked-up PDF and a revised cover letter.
- **Nature, formatting guide.** Text double-spaced with line numbers; a title that fits two lines (about 75 characters); summary paragraph ideally under 200 words; for a presubmission enquiry, a covering paragraph on the interest to a broad readership.
- **arXiv, "Title and abstract preparation" and "TeX submissions".**
  - Metadata: every author listed, in the order given name then family name; no AI tool as author; the abstract under 1,920 characters, without the word "Abstract", with only simple TeX; a comments field for the number of pages and figures and the status of the paper; journal reference and DOI only for a published version.
  - Sources: the TeX source is required when the paper was written in TeX; auxiliary files are removed; hidden files are deleted; figures must be in the family the compiler reads (EPS for DVI mode; PDF, PNG or JPEG for PDF mode), with no conversion on the fly; only packages of the supported TeX Live releases are available, so journal styles may have to be included.
  - Bibliography: since November 2025 arXiv runs BibTeX or Biber on uploaded `.bib` files, and a precompiled `.bbl` is no longer necessary; a `.bbl` that is uploaded is used and must be named like the main file and match the TeX Live release.
  - Listed causes of failure include cross-file references with `xr` between separately compiled PDFs.
  - arXiv's own FAQ advises removing comments from the source before submitting, and names a third-party cleaner.

## What was measured here (2026-11-23)

- `scripts/audit.py`, `scripts/submit_check.py`: 25 planted-fault cases pass (`evals/finish/cases.py`).
- The example manuscript of `examples/supplement/` is a mock: the audit reports its placeholder images and references as errors, and the six gaps of its reproducibility checklist.
- Two manuscripts from arXiv (cond-mat.mes-hall, 2026) were audited. Findings that held up: three and one sentences over 30 words in the abstracts; sentences of the conclusion shared with the abstract or introduction in one; hand-typed equation numbers in the other. Findings that did not, and what was changed: the reference check failed until the audit learned to find the `.bib` file named in the source; "to be determined", a normal phrase in physics, was reported as an unfinished passage; initials in a contribution statement were glued across names; a repeated sentence was counted as a failure, and is now a finding to review.
- `submit_check.py --pack --compile` builds the clean copy of the example from its own three files.
- No submission to a real system was made with these tools.

## This skill's own rules (no external source)

- That the audit changes nothing and sends each fix back to the part that owns the rule.
- The ten reading passes and their order; the independent reading with its four questions, and the comparison of the reader's one-sentence claim with RESULT.
- The three levels of severity and what counts as blocking.
- That the agent prepares and the authors submit.
- The five paragraphs of a cover letter. The APS list above names its contents; the order, the length and the ban on words of praise are this skill's.
- Freezing the version, the clean copy with checksums, and `submission.md`.
- The placeholder patterns, the limit checks and the phrases that identify authors in `audit.py` and `submit_check.py`; all adjustable in the scripts.
