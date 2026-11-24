# Abstract: what the evidence does and does not support

Read this when you need to explain a choice made in `parts/abstract.md`. Most of these studies are correlational, several come from medicine or economics, and none tests abstracts in physics directly. Use them to explain, not to promise.

Checked 2026-11-19 from publisher pages, abstracts and secondary summaries. Verify each entry against the paper itself before citing it elsewhere.

## Structure

- **The five moves follow an established pattern, not a tested optimum.** Nature's formatting guide asks for a summary paragraph with basic introduction, background and rationale, a statement of the main conclusions introduced by "Here we show" or equivalent, and two or three sentences of general context. Genre studies describe abstracts with a five-move model: introduction, purpose, method, product, conclusion (Hyland 2000).
- **Context first serves the patient reader.** Mensh & Kording (2017, PLOS Comput. Biol. 13:e1005619) recommend context-content-conclusion and note that it may not optimally engage an impatient reader. This is the reason Background and Gap get one sentence each; that limit is a house rule.

## Length and plain language: against the usual advice

- **Shorter and plainer abstracts were cited less.** In more than one million abstracts from eight disciplines, short and clear abstracts went with fewer citations than expected; the authors suggest search-engine matching as the reason (Weinberger, Evans & Allesina 2015, PLOS Comput. Biol. 11:e1004205). Correlational.
- **Abstract length and complexity correlated positively with citations** across 4.3 million papers in over 1,500 journals, with typically weak effects and large variation between journals (Sienkiewicz & Altmann 2016, R. Soc. Open Sci.).
- What follows from these: do not shorten for its own sake, and cover the search terms. What does not follow: that padding or jargon helps.

## Overclaiming

- **Spin changes expert readers' judgment.** In a randomized trial with 300 clinicians, abstracts with spin raised the rated benefit of the treatment (Boutron et al. 2014, J. Clin. Oncol., the SPIIN trial).
- **Language models are affected too.** Across 22 models, LLMs were more susceptible to spin in abstracts than humans; they could recognise it and prompting reduced its effect ("Caught in the Web of Words: Do LLMs Fall for Spin in Medical Literature?", arXiv:2502.07963).
- **Promotional language is rewarded.** In over 130,000 abstracts from Science, Nature and PNAS (1991-2023), promotional language predicted more citations and views (Communications Psychology 2025, doi:10.1038/s44271-025-00293-8). The frequency of positive words in PubMed abstracts rose from 2.0% to 17.5% between 1974-80 and 2014 (Vinkers, Tijdink & Otte 2015, BMJ 351:h6467).
- **Some venues rule it out.** Physical Review Applied's author guidelines say manuscripts should not include dramatic language or overstated claims of novelty or priority. This, and the fact that priority cannot be checked from the manuscript, is why the Resolution begins with "Here" and never with "For the first time".
- The rule against marketing and self-assessment words is therefore a choice on accuracy grounds, made knowing that hype correlates with attention. Say so if asked.

## Compression

- "One function per sentence, 5-7 sentences, at most four claims" is a house rule. It does not contradict the length findings above: those argue against shortening for its own sake, while this rule removes secondary results that bury the headline finding. No study found here tests it.

## Sentence limits and target length

- The limits on sentence length, clauses and reference words are house rules for readability. No study found here tests them on abstracts.
- The 150-word target is derived, not measured: six sentences of about 25 words. The 5% ceiling is APS guidance (abstract about 5% of the article and under 500 words). The citation studies above favour longer abstracts, so say plainly that the target is a readability choice.

## Limitations in the abstract

- **A limitations section did not change expert readers' confidence.** Randomized trial, 300 clinicians, 30 systematic-review abstracts: confidence 4.4 with the section and 4.6 without (out of 10), no significant difference; the authors caution that less expert readers may differ (BMC Med. Res. Methodol. 2014, 14:123, doi:10.1186/1471-2288-14-123).
- **Some formats require it.** PRISMA for Abstracts includes a limitations item (Beller et al. 2013, PLoS Med., doi:10.1371/journal.pmed.1001419). Venue rules override the default.
- The trial is about a separate limitations section in medical reviews. It says nothing about dropping scope from the claim, which this skill never allows.

## Numbers: mixed and field-limited

- **Economics**: among 2,370 empirical papers in three leading journals, those with numerical magnitudes in their headline results had 19% ± 11% more Google Scholar citations (Edlin & Love 2022, working paper, "Needed in Empirical Social Science: Numbers").
- **Generative search**: adding statistics was among the more effective of nine rewriting methods for increasing a document's share of a generated answer, with the retrieved set held constant (Aggarwal et al. 2024, KDD, "GEO: Generative Engine Optimization"). Web pages, already retrieved; weak transfer to papers.
- **APS guidance**: abstracts of experimental papers specify the quantities measured, the objects studied and the experimental conditions.
- The "number if and only if the claim is quantitative" rule rests on triage logic and on consistency with the title rules, not on these studies.

## Retrieval

- **Title and abstract are embedded together, with an input limit.** SPECTER2 takes "title [SEP] abstract" and truncates at 512 tokens (Singh et al. 2023; model documentation). Which retriever a given tool uses varies.
- **Search agents judge relevance by reading.** PaSa uses one agent to collect candidate papers and a second to read each one and decide whether it meets the query (He et al. 2025, ACL, arXiv:2501.10120).
- The advice to put main terms in the first two sentences is an inference from snippet display and truncation, not a measured effect.

## Signposts

- "However" for the gap and "Here we show" for the result are conventions (see the Nature guide above). No study found here measures their effect on reading or retrieval. The rule rests on triage logic and house preference.
