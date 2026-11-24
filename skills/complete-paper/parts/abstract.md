# Abstract

Stage B · Reads: `brief.md`, `venue.md`, `notation.md`, results, discussion, conclusion, the title's search queries and abstract patch · Writes: the abstract (typeset and plain-text versions)

An abstract states the paper's claim, the evidence for it and its scope, so that a reader who sees nothing else knows what was found, in which system, and on what grounds.

It has the title's two jobs, with more room. It has to be **found**: retrievers index the title and abstract together, and people and search agents decide from the abstract whether to open the paper. And it has to **stand alone**: most readers, human or machine, never go further, so what the abstract says is what the paper says to them. One constraint sits above every rule below: claim no more than the paper shows.

The form is a five-move narrative: background, gap, resolution, result, implications. One function per sentence, 5-7 sentences in total. Compression is the default.

## Modes

The checks are the same in each mode.

- **Write**: no abstract yet, or the user wants a new one.
- **Revise**: an abstract exists; keep what passes and fix what fails. Cut before adding: an over-long abstract is fixed by removing claims, not by rewording them.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read in this order, and stop to ask if the first item cannot be built:

1. `brief.md` (the claim sheet): RESULT, SYSTEM, METHOD, EVIDENCE, NOT SHOWN. If it does not exist, build it first from the Results, the Conclusion and the main figure captions. With only the user's description, work from that and say so. Do not infer results that are not written down.
2. `venue.md`: the abstract's length cap (words or characters), whether it is structured, whether citations are allowed, any required items.
3. `notation.md`: the names and symbols the paper uses. The abstract uses the same ones.
4. The manuscript's Results and Conclusion, the title if there is one, and the title part's "abstract patch" (terms that did not fit the title).

Write the abstract after Results, Discussion and Conclusion exist and before the title. An abstract written first promises results the paper may not deliver.

## Steps

### Step 1. Reuse the search queries

Take the 3-4 queries written for the title, or write them now: what someone looking for this result (not this paper) would type. Every key term of every query must appear in the title or the abstract, and the main ones in the abstract's first two sentences. Where a neighbouring community uses a different word, give the synonym once, inside a sentence. Do not append keyword lists.

### Step 2. Build it from five moves

| # | Move | Function | Sentences | Visible marker |
|---|---|---|---|---|
| 1 | Background | Importance: why this system or problem matters | 1 | the system or phenomenon as the subject |
| 2 | Gap | What is now needed, and why now | 1 | the need stated positively ("... calls for ...", "... needs ...") |
| 3 | Resolution | The answer to the gap: what this paper shows or introduces | 1 | begins with "Here" |
| 4 | Result | The headline finding and how strongly it supports the claim | 1-2 | the finding as the subject |
| 5 | Implications | Reach: what the result changes or enables | 1 | the result as the subject, or "These results ..." |

- **Background.** Say why the topic matters in concrete terms: what it enables or what it limits. A sentence such as "X has attracted considerable attention" tells the reader nothing; cut it. No history of the field.
- **Gap.** One gap, and it must be the one the Resolution closes. If there is a real reason it matters now (a new material or measurement capability, two recent reports that disagree), put it in the same sentence; do not invent urgency. State it as a need that has arisen and that a concrete idea can now meet ("Dense memory built from Mn3Sn calls for ..."), not as an absence ("has not been studied", "remains unknown"); see ground rule 10 in `SKILL.md`.
- **Resolution.** State the new idea or finding together with the system and the kind of evidence, so that the sentence reads as the answer to the Gap. Begin with "Here" ("Here we show that ...", "Here we introduce ..."). Do not begin with "For the first time": priority cannot be verified from the manuscript, and venues such as Physical Review Applied ask authors to avoid overstated claims of novelty or priority. The novelty should be visible in the contrast between moves 2 and 3. "We study / investigate / explore X" describes activity and withholds the answer, so it cannot be this sentence.
- **Result.** Lead with the single headline finding, phrased as a finding ("X recovers / predicts / reveals Y"), not as a recap of the method. Then say how strongly it supports the claim, using one of: comparison with prior work, the size of the improvement (a factor, percentage points), agreement with a benchmark or an independent method, or distance from a physical threshold. Keep at most two supporting findings. Everything else (extra validations, demonstrations, ablations, secondary metrics, bounds) stays in the body.
- **Implications.** One forward statement of reach: what becomes possible, what is reinterpreted, or what the community can now do. It is not a restatement of the result. State it plainly and within what was shown; "paves the way" and "opens new avenues" name nothing.

The whole abstract carries at most four distinct claims: the resolution, the headline finding, and up to two supporting findings. Listing every result buries the one that matters.

### Step 3. Apply the rules below to every draft

#### Signposts and verbs

A skimming reader or a triage agent should be able to find the gap and the answer at a glance, so each gets one visible marker and nothing else competes with them.

- Mark the gap once, by the need it names ("... calls for ..."). Mark the resolution once ("Here"). "Here" does the same work as "In this paper / work / Letter" in fewer words. If the venue or field avoids the first person, use "Here, ... is shown" or "This work shows".
- The verb in the Resolution sentence must match EVIDENCE in the claim sheet:

| Evidence | Use | Do not use |
|---|---|---|
| Experiment | show, demonstrate, observe, measure, report | predict |
| Simulation | show by [micromagnetic / atomistic / first-principles] simulation, find, predict | observe, measure, or a bare "demonstrate" |
| Theory | predict, derive, show theoretically; "prove" only for a proof | observe, demonstrate |
| Method or software | present, introduce, followed by what it computes and how well | |
| Dataset or benchmark | present, release, followed by scope and size | |
| Review | review, survey | |

- After the Resolution, make the finding the subject ("Reversal completes within ..."). Three sentences in a row that start with "We" read as a list of activities.
- No other signal phrases. Additive openers ("Moreover,", "Furthermore,", "Additionally,", "Importantly,") usually announce padding and are a recognised sign of machine-written text; join the clauses or delete the sentence.
- No marketing words: "surprising(ly)", "remarkable", "overturning", "reversing the conventional view", "two additional surprises", "novel", "unprecedented". They assess the work instead of stating it, and that judgment belongs to the reader.

#### Sentences

An abstract is read in fragments: search results show one or two sentences, retrieval systems index passages, and many readers work in a second language. Each sentence has to be short enough to take in at one reading and clear enough to stand alone.

- **Length.** No sentence over 30 words; aim for 25 or fewer. A sentence that needs more is carrying two functions: split it, or cut a claim.
- **Clauses.** One main clause and at most one more (a "which", "when", "whereas" or "and" clause). The frame "Here we show that" does not count. A chain such as "..., so ..., whereas ..., whose ..." becomes separate sentences, or the weaker clause goes.
- **Reference words.** Do not use "it", "they", "this", "these", "its", "their", "then", "such", "the former / latter" or "respectively" to point at something in another sentence. Repeat the noun instead: "this exchange" becomes "the intersublattice exchange". A pronoun whose noun is in the same sentence is fine. The one exception is "These results" opening the Implications sentence.
- **Series.** At most three items in a series, and one series per sentence.
- **Test.** Read each sentence with the others covered. If a reader could not tell what it refers to, rewrite it.

Count with `python scripts/abstract_stats.py`, which reports words per sentence and lists link words and reference words for review. These limits are house rules for readability, not results from a study.

#### Numbers and formulas

A number goes in when the claim is quantitative: RESULT in the claim sheet contains a number, or the title or abstract uses a magnitude word (sub-nanosecond, giant, high-efficiency). A number stays out when the claim is qualitative (existence, mechanism, sign, symmetry); numbers would then be conditions, and conditions belong in the body.

- Only the headline one or two, each with its meaning attached: against prior work, as an improvement factor, or against a threshold ("three times the value in ...", "an order of magnitude below ..."). No bare figures.
- No number lists, no strings of parameters (thickness, field, current density), no inline inequalities, no error bars or p-values unless the venue's format requires them.
- At most one formula, and only when the formula is itself the result (for example `T_c = T_c^MF / W`). Give a plain-text rendering for submission forms.
- Every number in the abstract must appear in the body with the same value, unit and rounding.

#### Scope, not limitations

Do not write a limitations sentence ("this study is limited to ..."): each limitation is stated once, in the Results (ground rule 10 in `SKILL.md`). If the venue requires one in the abstract, ask the user. Put the scope inside the claim instead, because a claim without its scope is an overclaim:

- Name the specific material or model, the regime (temperature, field, size, timescale) and the kind of evidence: "in Mn3Sn thin films at room temperature", "micromagnetic simulations predict".
- Use a class noun ("antiferromagnets") only when the evidence covers the class.
- Nothing in the abstract may contradict or silently widen NOT SHOWN.
- Magnitude words (giant, ultrafast, robust, universal, efficient, significant) need the number.
- One hedge where the evidence is indirect ("suggests", "is consistent with"). Do not stack them ("may potentially suggest").

#### Self-contained and plain

- One paragraph, unless the venue requires headings; then map the five moves onto its headings.
- No numbered citations, no references to figures, equations or sections, no footnotes (unless the venue's format, such as a Nature summary paragraph, says otherwise).
- Abbreviations are defined in the abstract itself, independently of the body: the spelled-out form first, then the abbreviation in parentheses, "the random-phase approximation (RPA)". Introduce one only if it is used again in the abstract or readers search by it. No nonstandard abbreviations.
- One name per concept, the same as in the title and body (`notation.md`).
- Present tense for what the paper shows and for general facts; past tense for specific things that were done or measured.
- Give a plain-text version for submission forms and preprint metadata when the typeset one contains TeX: formulas as plain strings (Mn3Sn), no custom macros, no `\cite` or `\ref`.

#### Length

The venue's cap decides. With no venue known, write the standard version and offer the short one.

For a regular article with no stricter cap, the target is about 150 words (roughly 100-180) in 5-7 sentences, and the ceiling is 250 words or 5% of the body text, whichever is smaller. Under a character cap, come close to the cap and never exceed it. No study identifies a best length (see the evidence file); the target follows from the sentence limits (six sentences of about 25 words), from venue guidance, and from the indexing limit noted below.

| Version | Size | How the moves fit |
|---|---|---|
| Standard | 5-7 sentences; target about 150 words, ceiling 250 | one sentence per move, two for Result if needed |
| Short | a character cap, e.g. 600 characters including spaces; 3-4 sentences | 1 and 2 merged into one sentence; 3; 4; 5 only if it fits |
| Summary paragraph | about 150-200 words, written for non-specialists | Background grows to two or three sentences of basic introduction; follow the journal's annotated example |

- Count, do not estimate: `python scripts/abstract_stats.py abstract.txt --cap-words 250` or `--cap-chars 600` (or `wc -w`, `wc -m`). For a character cap, count spaces.
- When cutting: supporting findings first, then filler and adjectives, then Background down to a clause, then Implications. Never the Resolution, the headline finding, the system or the scope words.
- Even where the venue allows more, stay within the target when you can. A widely used paper-embedding model truncates title plus abstract at 512 tokens, so the tail of a long abstract may not be indexed by it. (An inference from the model's documented input limit, not a measured effect on retrieval.)

#### Other paper types

| Type | Resolution and Result must carry |
|---|---|
| Theory | the prediction or theorem, the model and its assumptions, and how it could be tested |
| Method or software | what it computes or enables, the validation, and where it outperforms or matches what exists |
| Dataset or benchmark | what is measured, scope and size, and what it allows that was not possible before |
| Review or perspective | topic, scope and period covered, and the organizing conclusion |

#### Venue rules

Venue rules override the choices above. Look up the target venue's author guidelines when you can and skim about ten recent abstracts from it for its habits. Otherwise mark the venue check as unchecked.

Example, from APS author pages (checked November 2026): one paragraph, completely self-contained, no numbered references, about 5% of the article and under 500 words; Physical Review Letters caps the abstract at 600 characters including spaces; abstracts of experimental papers specify the quantities measured, the objects studied and the experimental conditions; Physical Review Applied asks for no dramatic language and no overstated claims of novelty or priority. Guidelines change, so verify instead of trusting this paragraph.

#### When rules pull in different directions

Accuracy first (never overclaim to satisfy a form rule), then venue rules, then stand-alone completeness (resolution, system, evidence), then compression, then findability, then style.

## Checks

Test every draft:

1. **Five moves**: all present, each identifiable, one function per sentence; 5-7 sentences in the standard version.
2. **Gap-resolution fit**: the Resolution begins with "Here", answers the Gap, and its novelty is obvious without a novelty word.
3. **Result**: the headline finding comes first, is phrased as a finding, and the sentence says how strongly it supports the claim.
4. **Implications**: states reach or consequence, not a restatement of the result.
5. **Claim count**: at most four distinct claims; no list of results.
6. **Claim sheet**: every content word maps to a line of the claim sheet; the Resolution verb matches EVIDENCE; nothing widens NOT SHOWN.
7. **Stand-alone**: from the abstract alone, a reader can say what was found, in which system, and by what kind of evidence.
8. **Query coverage**: the Step 1 terms appear, the main ones in the first two sentences. List what is missing.
9. **Numbers**: present if and only if the claim is quantitative; one or two, each with meaning attached; no lists or inline inequalities; each matches the body exactly (`python scripts/audit_tex.py main.tex --checks numbers` lists abstract numbers missing from the body).
10. **Wording**: one gap marker and one "Here"; no "For the first time"; no "we study / investigate" as the Resolution; no three consecutive sentences opening with "We"; no additive openers, marketing words, or empty phrases ("has attracted considerable attention", "plays a crucial role", "paves the way", "sheds light on", "it is worth noting").
11. **Sentences**: none over 30 words; at most two clauses beyond the "Here we show that" frame; no reference word pointing to another sentence, except "These results" in the last one; no series longer than three items.
12. **Self-contained**: every abbreviation expanded at first use; no citations or cross-references; plain-text version given if needed.
13. **Venue**: length counted against the cap and format rules met, or marked unchecked.
14. **Consistency**: terms and symbols match the title and body; if a version is already public, any change to the claim itself is flagged.

## Report

Reply in the user's language; write the abstract in the manuscript's language. Keep it short:

1. **Abstract**, with its sentence count, word (or character) count and longest sentence, the plain-text version if it differs, and the short version if no venue is known.
2. **Move map**: one line per move giving its first few words, so the structure can be checked at a glance.
3. **Checks**: only the failures and the unchecked items.
4. **Flags**: overclaim risk, unverified gap or novelty statement, numbers not found in the body, unchecked venue rules.
5. **For the title**: the claim in one line and the terms the title should carry, if the title is not written yet.

In Audit mode, replace items 1 and 2 with a table of the fourteen checks and the smallest fix for each failure.

Propose only. Edit the manuscript when the user asks, and then update every copy of the abstract (main file, submission metadata, cover letter, preprint record).

## Relation to other parts

- **Title** (`parts/title.md`): a separate object with stricter rules. The abstract's headline finding does not automatically become the title; a finding that is properly scoped across two sentences can turn into an overclaim when compressed into a noun phrase.
- **Prose** (`parts/prose.md`): sentence-level polish and machine-tone removal for the whole paper. This part only enforces the wording rules listed above.
- **Audit** (`parts/audit.md`): the full pre-submission cross-check, including abbreviation first use in the body, numbers without context, and agreement between abstract, body and references.

## Example (invented; the physics and the numbers are placeholders)

**Before**

> Antiferromagnets have attracted great attention in recent years due to their potential for next-generation spintronic devices. In this paper, we study the switching dynamics of noncollinear antiferromagnets using simulations. Moreover, we investigate the effect of various parameters such as current density, damping and temperature. Our novel results show that the switching is ultrafast and robust, which paves the way for future antiferromagnetic memory. However, this study is limited to a single-domain model.

Fails: empty opener; activity verbs in place of a resolution; no specific system; "ultrafast" and "robust" without a number; class claimed, one model shown; "novel"; "paves the way"; a limitations sentence where a scope phrase belongs; "However" spent on something other than the gap.

**After (standard, six sentences)**

> Noncollinear antiferromagnets such as Mn3Sn combine a large anomalous Hall signal with picosecond spin dynamics, which makes them candidates for fast magnetic memory. Dense memory built from Mn3Sn calls for electrical switching of its octupole order without an in-plane bias field. Here we show by atomistic spin-dynamics simulations that spin-orbit torque alone reverses the octupole order of a single-domain Mn3Sn film when the kagome plane is tilted from the film normal. Reversal completes within 0.3 ns, an order of magnitude faster than the field-assisted case in the same model. The threshold current follows an analytical model of the cluster-octupole dynamics. These results identify crystal orientation as a design parameter for field-free antiferromagnetic memory.

**After (short, under 600 characters)**

> Memory built from the noncollinear antiferromagnet Mn3Sn calls for electrical switching of its octupole order without an in-plane bias field. Here we show by atomistic spin-dynamics simulations that spin-orbit torque alone reverses the octupole order of a single-domain Mn3Sn film when the kagome plane is tilted from the film normal. Reversal completes within 0.3 ns, ten times faster than the field-assisted case, and the threshold current follows an analytical model. Crystal orientation thus becomes a design parameter for field-free antiferromagnetic memory.

Move map of the standard version: 1 Background "Noncollinear antiferromagnets such as Mn3Sn ..."; 2 Gap "Dense memory built from Mn3Sn calls for ..."; 3 Resolution "Here we show by atomistic spin-dynamics simulations ..."; 4 Result "Reversal completes within 0.3 ns ..." and "The threshold current follows ..."; 5 Implications "These results identify ...". The Result gives one headline finding with its meaning attached (against the field-assisted case) and one supporting finding (agreement with an analytical model). No sentence exceeds 30 words, and no sentence needs another one to be understood. The scope ("single-domain", "simulations") sits inside the claim, so no limitations sentence is needed.

## What not to promise

Do not tell the user that an abstract written this way will raise citations or AI visibility; no study supports a promise like that. The defensible claims are narrower: the result can be found with standard terms, the abstract stands alone, and nothing in it overclaims. The studies behind individual rules, and what they do not show, are in `references/abstract-evidence.md`; read it when you need to explain a choice.
