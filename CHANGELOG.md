# Changelog

## [Unreleased]

### Added
- Entry skill `skills/complete-paper/SKILL.md` with the 20-part table, writing order, modes and state files.
- First principles: (1) a paper written for people, with machine tone kept to a minimum; (2) data are final and blanks are never filled in, with every number traced to its source (ground rule 16); (3) no invented terms, and a new name only with the user's agreement. Ground rule 15: every sentence and paragraph in context, evaluated with a reverse outline, and no roadmap at the end of the introduction. Ground rule 10: earlier work is described by how this work differs from it, never as a fault.
- Ground rule 10: write for the paper, leading every part with its selling point, and state each limitation once, in the Results; scope words stay inside the claim.
- Ground rule 11: what this study did is written with "we" and an active verb ("we implement", "we show"), not in the passive or with activity verbs.
- Ground rules 12 to 14: figures, tables and equations numbered in the order of the argument; each paragraph opens with its purpose ("To validate ..."); no colons, semicolons or clause dashes in running text. Ground rule 10 now frames the Discussion as forward-looking and the gap as a need.
- Saved defaults: repeated facts (author block, funding, declarations wording) saved once in `~/.complete-paper/defaults.md`, with the form `assets/defaults.md`.
- Templates for the 20 parts under `skills/complete-paper/parts/`.
- Author intake form `skills/complete-paper/assets/intake.md` for facts only the authors can supply.
- Abstract part (five-move structure, sentence and number rules, fourteen checks) with `references/abstract-evidence.md` and `scripts/abstract_stats.py`.
- Title part (the claim sheet of `brief.md`, search queries, candidate drafting, seven checks) with `references/title-evidence.md`.
- Outline part (central claim, claim chain with display-item roles, venue budget, display-item specifications, section plan, twelve checks) with `references/outline-evidence.md`.
- Figures part (paper style table, message to plot, final size, lettering, legends, axes, layout, schematics, main or supplement by panel, lint then look, export, seventeen checks) with `references/figures-evidence.md`, `scripts/fig_style.py`, `scripts/schematic3d.py`, `scripts/fig_lint.py` and rendered examples under `examples/figures/`.
- Bibliography part (four checks per reference: exists, matches its record, supports its sentence, formatted; coverage audit; `refcheck.md` ledger; fourteen checks) with `references/references-evidence.md` and `scripts/ref_check.py`.
- Figure examples `examples/figures/before.py`, `after.py`, `schematics.py`, `figstyle.md` and their output, and the planted-fault cases `evals/figures/lint_cases.py`.
- Tables part (table, figure or sentence; a layout for the comparison; rules and alignment; title and notes; lean tables in SI units with a shared unit or narrow-column symbols defined in the caption; values copied unchanged and blanks never filled; fourteen checks) with `references/tables-evidence.md` and `scripts/table_check.py`.
- Brief part (five claim fields, the result placed against earlier work, key numbers with their sources, the evidence map, a Record section copied from the intake form, ten checks) with `scripts/brief_check.py` and `examples/brief/brief.md`.
- Methods part (place by venue, a checklist by kind of work, `repro.md` filled against the manuscript, twelve checks) with `references/body-evidence.md`, `scripts/methods_check.py` and `examples/methods/repro.md`.
- Results part (the claim chain in order, five moves from purpose to meaning, numbers with uncertainty and a reference, observation kept apart from inference, each limitation stated once here, twelve checks) with `scripts/cite_order.py`.
- Discussion part (answer, interpretation against the leading alternative, comparison by how earlier work differs, an outlook instead of a list of limitations, graded interpretation, twelve checks).
- Prose part (profile first, paragraphs, sentences, words, machine tone repaired at its cause, plain punctuation, protected content, thirteen checks) with `references/prose-evidence.md` and `scripts/prose_lint.py`.
- Audit part (every part's script in one run, eleven reading passes including the house rules, an independent reading, blocking levels, eight checks) with `references/audit-submit-evidence.md` and `scripts/audit.py`, which also runs `audit_tex.py`.
- Submit part (limits re-verified, a frozen version, review copy, clean sources, required statements and the AI-use statement, form entries, cover letter, preprint, `submission.md`, thirteen checks) with `scripts/submit_check.py`.
- Planted-fault cases `evals/text/cases.py` (41) and `evals/finish/cases.py` (25), run by the tests on a copy of the skill.
- README in English and Korean.
- Supplement part (four places for every item, a 1-to-1 ceiling, callout budget, sections that open with their answer, one style with the main text, the data package, fifteen checks) with `references/supplement-evidence.md`, `scripts/supp_check.py`, the example under `examples/supplement/` and the cases `evals/supplement/supp_cases.py`. `scripts/eq_refs.py` resolves references between a main text and a supplement linked with xr.
- Captions part (inventory, caption order, what stays out, form and length, hand-off to the text, twelve checks) with `references/captions-evidence.md` and `scripts/caption_check.py`.
- Conclusion part (form by venue, four moves with the scope inside the claim, no duplication with abstract and introduction, twelve checks) with `references/conclusion-evidence.md` and `scripts/overlap_check.py`.
- Introduction part (reader and gap, five-move funnel, citation rules with a literature check for the gap, twelve checks) with `references/intro-evidence.md`.
- Notation part (symbol choice, typeface, hats, first-use definitions, units, eight checks) and a new equations part (derivation chain, layout, numbering and citation, nine checks), with `references/notation-standards.md` and `scripts/eq_refs.py`.
- `scripts/audit_tex.py` (counts `[CITE: ...]` placeholders as open markers; the `limits` check flags limitation sentences outside the Results; the `voice` check flags passive voice and activity verbs for our own work; the `punct` and `gap` checks flag colons, semicolons and dashes and gaps written as absences; equations out of order are critical, with references through xr prefixes resolved and a section's opening pointer to its own result allowed; numbers in the conclusion found nowhere else are flagged; the `tone` and `prior` checks flag machine tone, a roadmap in the introduction and earlier work described as a fault), `scripts/reverse_outline.py` and `scripts/verify_refs.py`.
- Tests and fixtures under `tests/`.
- Claude Code plugin and marketplace manifests.
- Agent-level eval cases for `claude plugin eval` under `evals/` (five cases: invented numbers, audit without rewriting, limitations once, invented citations, title within the claim). First results, 2026-11-24: with the plugin 0.8, without 0.6; the audit case passes in both arms only with `--judge-model sonnet` (`evals/README.md`).
- README in English, Chinese, Korean and Japanese, with an author section (Gyuyoung Park, homepage, GitHub, ResearchGate).
- `tools/build_skill.py` builds `dist/complete-paper.skill` for the Claude app; a GitHub Actions workflow runs the tests on Linux (Python 3.10 and 3.14) and Windows (Python 3.9 and 3.14) and builds the package.
- Tests for the faults found on the first real manuscript, in an invented fixture (`tests/fixtures/realrun/`).
- Release tooling: `tools/version.py` (`bump` sets the version in `plugin.json` and `SKILL.md` and dates the changelog section; `check` compares them with a tag; `notes` prints a version's changelog section), `.github/workflows/release.yml` (a pushed tag `v<version>` is checked, tested, packaged and published as a GitHub release with `complete-paper.skill`), and `RELEASING.md`. The tests workflow checks that the two version files agree. The READMEs say how users update.
- `.gitattributes`: text files are stored with LF line ends on every system, so word counts and the packaged skill do not depend on the platform.

### Removed
- The authors and declarations parts, moved to `archive/parts/` and no longer installed. Author and declaration facts are still collected in the intake form and can be kept in the saved defaults; ground rule 9 (AI-use statement) now points to the submit part. The author's filled versions of both parts and their evidence file are kept in `archive/` unchanged.

### Changed
- The list of scripts moved from `SKILL.md` to `scripts/README.md`, which cuts about 1,400 tokens from every call of the skill. `SKILL.md` now says where to run the scripts: from the project folder, by their path in the skill's directory.
- The figures part says to copy `fig_style.py` and `schematic3d.py` beside the plotting scripts.
- The marketplace manifest carries the skill's one-line description.
- Author and copyright holder: Gyuyoung Park (LICENSE, SKILL.md metadata, plugin and marketplace manifests).
- The example manuscript in `examples/supplement/` has no colons or semicolons left in running text or captions, except the label of its contents line, and states its gap as a need; the counts that the cases and `suppmap.md` quote follow (613 words, 43 sentences).
- The test fixture `tests/fixtures/flawed/main.tex` uses an invented affiliation.
- The four READMEs open with what the skill does (a figure before and after, a paragraph before and after, part of an audit report), then how to install it and a first request to try. The edit-guard example moved to the Scripts section. The Chinese README uses full-width punctuation in its prose.

### Fixed
- `fig_lint.py` reported a legend laid on the axis frame (`borderaxespad=0`) as crossing the frame with matplotlib 3.11, where rounding puts its edge a fraction of a point outside. An edge within 0.5 pt of the frame now counts as on it.
- `prose_lint.py` reported wrong line numbers after the abstract and after every heading, because the headings it marks added lines. The marks now keep the line count.
- `audit.py` counted all of a letter without section headings (as in PRL) as its abstract, so the abstract looked too long and the running text had no words. The text after the abstract is now running text.
- `submit_check.py` treats a rooted path such as `/home/user/a.pdf` as absolute on Windows too, and prints relative paths with forward slashes on every system.
- From the first run on a real manuscript (audit and revise, 2026-11-24):
  - `audit_tex.py --checks xrefs`: a displayed equation counts as met where it stands, so equations cited by number only after their display are no longer reported out of order.
  - `audit_tex.py --checks tone`: a roadmap written with references ("Sections II-IV give ..., and Sec. V states ...") is found.
  - `audit_tex.py --checks gap`: "do not evaluate", "until it is evaluated" and "of unknown size" count as a gap written as an absence.
  - `audit_tex.py --checks limits`: any section other than the introduction, discussion, conclusion and the method sections counts as Results, whatever its name; "also requires low ...", "applies only to" and "comparisons are between models" are limitation cues.
  - `audit.py`: a main text and a supplement with their own reference lists are checked apart, so shared keys are no longer duplicates; tool names (Claude, Codex, ChatGPT and others) count as an AI-use statement.
  - `table_check.py`: tables inside REVTeX's `ruledtabular` have their rules drawn by the class.
  - `brief_check.py`: the `[unconfirmed]` marker is not counted in the length of RESULT.
- `audit_tex.py --checks numbers` ends the conclusion where a statement begins (data availability, acknowledgments, funding and the like) and skips DOIs, arXiv numbers and URLs, so that a run count or a DOI in the data statement is no longer reported as a number of the conclusion.
