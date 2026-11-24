# Methods, results and discussion: journal rules, sources and this skill's own rules

Read this when you need to explain a choice made in `parts/methods.md`, `parts/results.md` or `parts/discussion.md`. Journals fix where these sections go and how long they may be; they say little about how to write them. Most of the rules in the three parts are therefore this skill's own, and are marked as such below.

Checked 2026-11-23. Verify each entry against the current page before citing it elsewhere.

## What journals require

- **Nature, formatting guide.**
  - Methods: typically no more than about 3,000 words; concise, yet sufficient for interpretation and replication; short bold subheadings; published methods are cited, with any additions or variations stated; no figures or tables (essential display items go to Extended Data); placed after the main text; references in the Methods continue the numbering.
  - Main text: sections separated by subheadings of up to 40 characters, spaces included; the guide does not prescribe Results or Discussion headings.
  - All error bars and statistics are defined in the figure legend.
- **APS, Physical Review Letters, Publishing Guidelines.** A Letter has an introduction that gives general readers the background, central sections that explain and establish the results, and a concluding section that summarizes the findings and suggests future directions. The page gives no guidance on a methods section. Up to about two pages of End Matter (appendixes or other content for specialists) follow the references and do not count against the length.
- **APS Journals Style Guide (February 2026).**
  - Headings (II.G): four levels in regular articles, numbered I., A., 1., a.; in Physical Review Letters freestanding heads are generally avoided and run-in italic heads are used; in Letters of the other journals headings are optional.
  - Ethics statements (II.M) go in the methods text where the collection of data is described.
  - "Fig." is written out as "Figure", and "Eq." as "Equation", when it begins a sentence.
  - Appendixes (II.Q): equations numbered (A1), (B1); figures and tables continue the numbering of the main text; an appendix must contain explanatory text.
- **Springer Nature, editorial policy on AI.** The use of a large language model is documented in the Methods section.

## Sources on structure

- **Docherty and Smith, "The case for structuring the discussion of scientific papers", BMJ 318, 1224 (1999).** An editorial. It calls the discussion often the weakest part of a paper, where "careful explanation gives way to polemic", and proposes a fixed order: the principal findings; strengths and weaknesses of the study; strengths and weaknesses in relation to other studies, with the differences in results discussed; the meaning of the study, with possible mechanisms and implications; unanswered questions and future research. Written for clinical research.
- **A reply in the same journal (BMJ, 2000; seen here as a search excerpt)** argued that structure cannot remove speculation, and that a discussion which never goes beyond its results says nothing new. The five moves of `parts/discussion.md` keep interpretation and ask that it be graded, for that reason.
- **Mensh and Kording, "Ten simple rules for structuring papers" (2017)**, used in `references/outline-evidence.md`: the results as a sequence of statements that support the central claim, each paragraph opening with its point. Read in an earlier session; not re-read here.

## What was measured here (2026-11-23)

- `scripts/methods_check.py`, `scripts/cite_order.py`: 13 planted-fault cases pass (`evals/text/cases.py`).
- On the example manuscript of `examples/supplement/`: the reproducibility checklist has six rows that the manuscript does not answer (the definition of the threshold, the code and its version, the time step, the initial state); three of its paragraphs open by pointing at a figure.
- On two manuscripts from arXiv (cond-mat.mes-hall, 2026; one experimental article with its supporting information, one letter with a theory supplement): every figure was cited and in order in both; in the letter the panels of two figures are named in the captions and never cited in the text; the scan of method sections gave five and three notes. The first run on the experimental article missed panels labelled "a)" in captions; the script now reads that form. Two papers are not a sample.

## Where sources differ

- **Where methods go**: in the text or appendixes (APS), after the main text (Nature), in the supplement (Science).
- **Results and Discussion**: separate, merged, or without headings at all, by venue and article type.
- **Whether a discussion should be formally structured**: proposed by Docherty and Smith, contested in the replies.

## This skill's own rules (no external source)

- **The reproducibility checklist** (`repro.md`) and its items for four kinds of work. They are a compilation of what papers in these fields are commonly asked for; they are not a reporting standard of any journal, and the lists for simulation and device experiments reflect the practice of magnetism and spintronics more than other fields.
- **"Take every value from its source"** and the rule that a row without a place is closed in the text.
- **The four moves of a results paragraph**, finding first, and the two exceptions for a paragraph that opens with a figure.
- **The table of verbs for observation, analysis and inference**, and "one hedge per inference".
- **Subheadings that state findings.** Venues allow or limit headings; that a heading should be a finding is this skill's rule, shared with `parts/outline.md`.
- **The five moves of a discussion**: adapted from Docherty and Smith, with the answer to the introduction's question first and the consequence last; **the three grades** (shown, supported, speculative) and the limit of one speculation.
- **The guides for length**: 15 to 25% of the main text for a discussion; the basis of a results paragraph in at most one sentence.
