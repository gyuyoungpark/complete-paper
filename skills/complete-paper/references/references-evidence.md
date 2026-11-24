# References: journal rules, studies and registry behaviour

Read this when you need to explain a choice made in `parts/references.md`. Three kinds of material are kept apart: what journals and ethics bodies require, what studies measured, and what the registries returned when they were queried. The order of the four checks, the functions of a citation and the limits on grouping are this skill's own.

Checked 2026-11-19. Verify each entry against the current page before citing it elsewhere. Items read only through a search excerpt, an abstract or someone else's quotation are marked as such.

## What journals and ethics bodies require

- **APS Journals Style Guide (author edition, February 2026), reference list.** For all journals except Reviews of Modern Physics: references and endnotes form one list, numbered in square brackets in order of first appearance, and URLs go in the list, not in the body. Titles are "strongly encouraged", in sentence-style capitals, roman, without quotation marks. All names are given for up to ten authors; beyond ten, "et al." may follow the first. Journal names take CASSI abbreviations, the volume is bold, only the first page or article number is given, and the year stands in parentheses at the end. An e-print is written "arXiv:1302.3781" with no date, and arXiv numbers are not added to published sources. A dataset needs creators, year, version, repository and a persistent identifier; software needs author, code name, institution, year and a DOI or URL. Some journals allow footnotes apart from the list. Reviews of Modern Physics lists alphabetically and cites by author and year.
- **APS, "References in Physical Review and Physical Review Letters"** (the page did not load; read through a search excerpt). Authors are obliged to give a set of references that communicates the precedents, sources and context of the work.
- **Physical Review Letters, information for contributors** (search excerpt). References are not counted in the length of a Letter; footnote text placed among the references is counted.
- **REVTeX 4.2 author's guide** (search excerpts). The BibTeX styles display article titles, the `eprint` field is handled by the style, and APS production wants the content of the `.bbl` file inside the main `.tex` file.
- **Nature formatting guide.** References are numbered in order of appearance through text, tables, boxes, legends, Methods and Extended Data, and are cited as superscripts. Each number refers to one publication. An Article has a guideline of up to 50 references in the main text; those cited only in Methods or Supplementary Information do not count. All authors are listed unless there are more than five, then the first and "et al.". Titles are required. Preprints on recognized servers, published conference abstracts, numbered patents and datasets with a DOI may be listed; papers in preparation are mentioned in the text only. A LaTeX submission carries its references inside the single `.tex` file.
- **ICMJE Recommendations** (read through quotations by a medical library and two journals; the official page was not opened). Authors should verify references against the original documents or a bibliographic source, should be able to attest that each reference supports its statement (added in the January 2025 revision), are responsible for checking that no reference cites a retracted article except to refer to the retraction, and should not use AI-generated material as a primary source.
- **COPE discussion document on citation manipulation (2019).** Manipulative citation is behaviour meant to inflate citation counts for personal gain: excessive self-citation, excessive citation of the publishing journal, coordinated citation between journals. The problem arises when references "do not contribute to the scholarly content of the article" and are there only to raise counts. Self-citation that meets a real need of the work is legitimate.
- **Editorial in Proc. R. Soc. A (Lockwood 2020, doi:10.1098/rspa.2020.0746).** Cites a society's finding that manipulating citations, including citations that do not contribute to a manuscript's scientific content, is malpractice. Asks referees to list suggested citations separately and authors to report pressure to cite.

## What studies measured

**References that do not exist**

- In 84 short literature reviews written by ChatGPT, 55% of the references from GPT-3.5 and 18% of those from GPT-4 were fabricated, and 43% and 24% of the real ones had substantive errors (Walters & Wilder 2023, Sci. Rep. 13:14045).
- Of 176 references that GPT-4o produced for literature reviews in mental health, 35 (19.9%) were fabricated (JMIR Mental Health 2025, e80371).
- A commercial scan of the papers accepted at NeurIPS 2025 found at least 100 fabricated references, in 51 or 53 papers depending on the report, among about 4,800 papers that had each passed three to five reviewers (news reports; arXiv:2602.05930).
- An audit of 48,095 accepted papers (arXiv:2607.00738) found at least one likely fabricated reference in 18.7% of ICLR 2025 papers, 23.3% of ICML 2025, 26.2% of NeurIPS 2025 and 34.9% of USENIX Security 2025; per reference the rate was 0.3 to 0.8%. Reviewer ratings of affected and clean papers were nearly the same. The audit checks whether a work exists with the named authors, not whether it supports the citing sentence, and its authors do not attribute the rise to language models.
- A taxonomy of 100 fabricated references (arXiv:2602.05930; one author's coding of a tool-flagged sample): 66 with nothing real, 27 mixing real and invented elements, 4 with a valid identifier that belongs to another paper, 2 placeholders, 1 plausible title with no publication. The four forms in the part come from here.
- The bibliography of arXiv:2607.22693 lists a 2026 statement by a computational-linguistics conference on desk-rejecting papers with fabricated references. The statement itself was not opened.

**What checking tools can and cannot do**

- Five reference-checking tools were run on 104 hand-verified references, 33 of them problematic (arXiv:2607.22693, Table 4; a small test set built by the authors). Each tool missed between 1 and 15 of the 33 problematic references and wrongly flagged between 20 and 53 of the 71 good ones. The paper's advice is to treat tool output as preliminary and to check flagged items by hand. This is the basis for "a flag is a lead, not a verdict".
- The audit above names its sources of false alarms: extraction errors from PDFs, two real works with the same title, works not yet indexed, and web pages or other items that are not papers.

**References that do not support the sentence**

- A meta-analysis of 28 studies in medicine found 25.4% of quotations wrong and 11.9% seriously wrong (Jergas & Baethge 2015, PeerJ 3:e1364). An update with 46 studies and about 32,000 quotations found 16.9% wrong and no improvement over time (Baethge & Jergas 2025, Res. Integr. Peer Rev. 10).
- Of 250 citations sampled from five general science journals, 25% did not substantiate the statement they were attached to (Smith & Cumberledge 2020, Proc. R. Soc. A 476:20200538; the rate from the abstract, the sample from a news report).
- From repeated identical misprints in the citations of one famous paper, a model estimate that only about 20% of citers read the original (Simkin & Roychowdhury, Complex Systems 14:269; arXiv:cond-mat/0212043). It is an estimate from a model, not a count.
- For seven language models answering medical questions, between 50% and 90% of the responses were not fully supported by the sources they cited (Wu et al. 2025, Nat. Commun. 16:3615). The setting is question answering in medicine, not manuscripts.
- In a network of 242 papers and 675 citations about one claim, unfounded authority was built by citing the supportive papers and not the ones that weakened the claim, by papers that repeated the claim without data, and by turning hypotheses into facts through citation (Greenberg 2009, BMJ 339:b2680). This is the basis for "cite the evidence against".

**Retractions**

- Crossref took over the Retraction Watch database in 2023 and has exposed it in its REST API since January 2025. The data are updated every working day; corrections and expressions of concern are included but are less complete than retractions (Crossref documentation).
- Citations made after a retraction rarely acknowledge it: in anesthesiology journals 5.2% did, and 80% treated the retracted work as valid (Frasco et al.; from the abstract). A study of 7,813 retracted papers in PubMed found that they continued to be cited (Hsiao & Schneider, Quant. Sci. Stud.; from the abstract).

**Does a longer list bring citations?**

- In 50,878 ecology articles, more references, more recent references and a moderate share of self-citations were each associated with more citations (Mammola et al. 2021, Scientometrics 126:785). The authors present associations, in one field.
- In one university's output, the number of references correlated weakly with later citations (De Groote et al. 2023, Evid. Based Libr. Inf. Pract. 18(2)).
- Among Malaysian review and highly cited papers the increase was not statistically significant, and the authors advise against lengthening a list to gain citations (Ale Ebrahim et al., "Does a long reference list guarantee more citations?").
- A strong relationship was reported for a century of papers in Science (Webster; known here only through a news item quoted on a university page).
- None of these is an experiment. The part therefore argues for coverage on grounds of fairness and refereeing, and promises nothing about citations.

**Who referees, and who gets cited**

- Editors are advised to start a search for referees from the manuscript's reference list (Springer Nature guidance for editors; a post by Cell Press editors; a 1988 account in Physics Today of how a PRL editor worked).
- In over a million papers from 35 physics journals, papers by women were cited less than expected (Teich et al. 2022, Nat. Phys. 18:1161). One reason the audit asks who did the work, not whose name comes to mind first.

## What the registries returned

Seen with `curl` and with `scripts/ref_check.py` on 2026-11-19.

- `https://doi.org/<DOI>` with the header `Accept: application/vnd.citationstyles.csl+json` returned a JSON record for a Crossref DOI, a DataCite DOI (an arXiv paper) and a JaLC DOI. `https://doi.org/api/handles/<DOI>` answered with `responseCode` 1 for an existing DOI and 100 for one that does not exist.
- The record of a retracted Nature paper carried the retraction under `updated-by`, from the publisher and from Retraction Watch, and its title began with "RETRACTED ARTICLE:".
- Records contain errors. The record of a 2003 article in Complex Systems gave 2024 as its date and listed the authors' affiliation as a third author.
- BibTeX requested with `Accept: application/x-bibtex` came with titles in the publisher's capitalization, unabbreviated journal names, a Unicode dash in page ranges, `month=Sept` and `month=July` (BibTeX answers that the string name is undefined), no article number for articles in Physical Review Letters, Scientific Reports and Proc. R. Soc. A, and the key `_elezn__2017` for a first author named Železný.
- BibTeX's `unsrt` style printed "(001)fe/(001)cr" and "anomalous hall effect" from unbraced titles. The APS style file was not available for inspection.
- Crossref's rate limits since July 2026: 5 single-record requests per second without a `mailto` address and 10 with one; 1 and 3 for list queries (Crossref community announcement). OpenAlex has required an API key since 13 February 2026, which is why the script does not use it.
- The script itself: on a test manuscript with planted errors it reported the nonexistent DOI, the nonexistent arXiv number, the DOI attached to another paper's title, the retracted paper, and the wrong volume, year and first author; it found the DOI of a real paper entered without one, and no record for an invented one. On sixteen real physics references typed from memory it reported sixteen matches and no error. Its `.bib` parser read the 2,139 entries of the 39 `.bib` files shipped with a TeX distribution and agreed with BibTeX on the keys of the standard example file. It has not been run on a complete real manuscript.

## Where sources differ

| Question | One position | Other position | What the part does |
|---|---|---|---|
| Titles in the list | APS: strongly encouraged | Nature: required | Takes the rule from `venue.md` |
| Authors before "et al." | APS: up to ten | Nature: five | All authors in the `.bib`; the style shortens |
| Cap on references | Nature: about 50 in the main text of an Article | APS: none stated; not counted in the length of a Letter | Takes the cap from `venue.md`; gives an order of cuts |
| Form of a preprint | APS: "arXiv:" and the number, no date | Nature: "Preprint at", the URL and the year | Takes the form from `venue.md` |
| Longer list, more citations | A positive association in some datasets | Weak or not significant in others | Promises nothing |
| Citing in order to be noticed | The ethics document names self-citation, journal citation and coordinated citation, not this | Its test of content still applies: a reference that adds nothing to the article | The gate "which sentence does it support" |

## This skill's own rules (no external source)

- The order of the four checks, and "nothing enters the list from memory".
- The six functions of a citation and the reading depth each one needs.
- One to three works per statement, the flag above four, and the list of works cited only inside such groups.
- Origin, strongest evidence and most recent paper or review for each line of work; two papers that share a senior author counted as one group.
- The order of cuts under a cap.
- The script's thresholds: a title similarity of 0.90 for a match and below 0.60 for another work; a family name counted as found at a similarity of 0.80; an author list counted as different when fewer than 60% of the names are found. The last follows the escalation rule of the audit cited above.
