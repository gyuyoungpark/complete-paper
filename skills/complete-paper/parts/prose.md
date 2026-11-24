# Prose

Stage D · Reads: the complete draft, `notation.md`, `venue.md`, `brief.md` · Writes: an edited copy beside the original, wording only

Prose is the last pass over the sentences of a finished draft. It changes how things are said. It never changes what is said.

It has two jobs:

- **Readable.** A reader in the field takes in each sentence at the first reading and always knows what a paragraph is for.
- **No machine tone.** Nothing reads as generated: no inflated words, no stock frames, no sentence that says nothing.

The second job is not cosmetic. Machine tone is a symptom. An inflated word marks a sentence that had nothing specific to say; a stock opener marks a claim that nobody checked; a tail of "highlighting the potential of" marks an interpretation attached without evidence. Swapping "pivotal" for "important" repairs nothing. For every hit the question is: **what does this sentence claim?** If it claims something, say it with the specific noun, number or citation. If it claims nothing, delete it.

Two limits follow. This part does not promise that a text will pass a detector of AI writing; its aim is the reader. And it does not hide the use of an AI tool: that use is disclosed as the venue requires (ground rule 9 in `SKILL.md`; `parts/submit.md` checks the statement), however the text reads.

Rule for every edit: **an edit for style changes no number, no symbol, no citation, no label and no strength of claim.** The check in Step 8 enforces it.

## Modes

- **Write**: not used. This part edits finished text only, so a request to write runs as Revise (polish).
- **Revise** (polish): edit a finished section. Change the fewest words that fix each problem.
- **Audit**: report the profile and the hits with the smallest fix for each; change nothing.

## Inputs

1. The draft, section by section. Keep a copy of each file before the first edit.
2. `notation.md`: the paper's terms and symbols, and its list of abbreviations.
3. `venue.md`: the spelling variety, the venue's habits of person and voice, its rules for abbreviations and numbers.
4. `brief.md`: the kind of EVIDENCE, which sets the verbs, and NOT SHOWN.
5. The sentence rules of the part that wrote each section: the abstract and the conclusion have stricter limits than the body.

Run this part after the sections are complete. Polishing a paragraph that will be rewritten is wasted, and it hides the changes that matter.

## Steps

### Step 1. Take the profile

```
python scripts/prose_lint.py main.tex
```

It prints the length of sentences and paragraphs per section, then the hits by category. Read the profile before any sentence: a section with a mean of 28 words per sentence needs splitting more than it needs word choices; a section with many hits of one category has one habit to remove.

Work from large to small: paragraphs, then sentences, then words.

### Step 2. Paragraphs

- **One point, stated first.** The first sentence says what the paragraph establishes; the rest supports it. A reader who takes only first sentences gets the argument.
- **In context.** Each paragraph opens from the one before, or from the statement of the claim chain it serves, and each sentence follows from the last (ground rule 15). `python scripts/reverse_outline.py main.tex` lists the first sentences for that reading. A paragraph that serves no statement goes back to its section's part.
- **Old before new.** Begin a sentence with what the reader already has, and end it with what is new. The end of one sentence is then the start of the next, and the paragraph needs few connecting words.
- **Connect by logic, not by habit.** "However" where there is a contrast, "therefore" where something follows. A paragraph whose sentences begin "Moreover", "Furthermore", "Additionally" is a list.
- **Do not end on a recap.** A last sentence that begins "Overall" or "Taken together" and repeats the paragraph is cut. The last sentence carries the consequence or the link to the next point.
- **No paragraph about the text.** "In this section we discuss" and "as mentioned above" are replaced by the thing itself.
- Three to eight sentences as a rule. A single-sentence paragraph is a deliberate statement, used rarely.

### Step 3. Sentences

- **The actor is the subject and the action is the verb**, close together and early. "We measured the threshold", "The threshold falls with tilt"; not "A measurement of the threshold was performed", not "There is a decrease of the threshold".
- **One idea per sentence.** In the body: none over 40 words, most under 25. Vary the length; a run of sentences of equal length reads as mechanical. The abstract and the conclusion keep their own limit of 30.
- **Plain punctuation.** No colons, semicolons or dashes that join clauses in running text, captions included (ground rule 14). Split the sentence, or join with "and", "because", "so" or "which".
- **Reference words point to one thing.** "This" takes a noun ("this dependence"). "It" and "they" have their antecedent in the same sentence or the one before.
- **One hedge per inference**, and a verb that matches the evidence (`brief.md`; the grades of `parts/discussion.md`).
- **Parallel form for parallel content.** A list has three items only when there are three things.
- **Voice and person.** "We" and an active verb for what the authors chose and did (ground rule 11), unless the venue avoids the first person. Constant within a paragraph.
- **Sentences with mathematics.** Do not begin a sentence with a symbol or a numeral. Name a quantity before its symbol at first use, and again when the definition is far away. Do not use a symbol as a verb in running text ("the field exceeds 1 T", not "the field > 1 T"). Displayed equations are punctuated as parts of their sentences (`parts/equations.md`).

### Step 4. Words

- **One term for one thing.** "Film", "layer" and "sample" for the same object are three objects to the reader. The term is the one in `notation.md`.
- **The plain word**: use, show, help, about, enough; not utilize, showcase, facilitate, approximately (unless a number follows), sufficient.
- **Verbs, not nouns made from them**: "analyse", not "perform an analysis of".
- **Numbers for quantities**: "three films", "since 2019", "by 12%"; not "several", "recently", "significantly". "Significant" is kept for statistics.
- **No intensifiers and no evaluation**: very, highly, clearly, obviously, remarkably, interestingly. If the point is clear, the sentence shows it.
- **Abbreviations**: defined at first use, in the abstract and again in the text; kept only if used at least three times; no abbreviation invented for this paper unless it names the paper's own method. Captions define their own.
- **One spelling variety**, the venue's. No contractions. Latin abbreviations as the venue has them; "e.g." and "i.e." are not interchangeable.

### Step 5. Machine tone: patterns, causes, repairs

| Pattern | Example | What it usually hides | Repair |
|---|---|---|---|
| Inflated vocabulary | "delve into the intricate landscape of", "pivotal", "underscore", "showcase" | nothing specific to say | name the specific thing, or cut the sentence |
| Asserted importance | "plays a crucial role", "has attracted considerable attention", "paves the way for" | importance claimed, not shown | say for what and by how much, with a citation; or cut |
| Stock opener | "It is worth noting that", "Importantly," | nothing | delete the opener |
| Hung-on tail | ", highlighting the potential of ..." | an interpretation without a basis | make it a sentence with its evidence, or cut |
| Recap closer | "Overall, these results demonstrate ..." | repetition | cut |
| Triplet | "fast, robust and scalable" | padding to three | keep the items the paper shows |
| Manufactured contrast | "not only ... but also", "it is not X; it is Y" | emphasis in place of content | state Y |
| Vague attribution | "studies have shown" | no source | cite, or cut |
| Stacked hedges | "may potentially suggest" | no decision on what was shown | decide the grade; one hedge |
| Connector at every start, even rhythm | "Moreover, ... Furthermore, ..." | a list presented as an argument | order by logic; vary the sentences |
| Signposting | "In this section, we will discuss" | nothing | delete; headings do this |
| Praise | "novel", "remarkable", "unprecedented" | a missing number | give the number |

- **Repair the cause.** A text from which the listed words were removed, and nothing else changed, has the same empty sentences in other words.
- **These patterns are not proof of anything.** People wrote all of them before language models did. They are removed because they cost the reader attention and carry no content.
- **Formatting habits** go with them: bold lead-ins and bullet lists inside running text, headings in title case where the venue uses sentence case, a dash where a comma or a full stop is meant. Use the venue's style.

### Step 6. Drafts by writers of English as a second language

Frequent in such drafts, and in translated ones; the lint's category `usage` catches the first group.

- Uncountable nouns made plural: research, information, evidence, equipment, software, literature.
- Fixed phrases: "discuss" (not "discuss about"), "consist of" (not "is consisted of"), "on the other hand" (not "in the other hand"), "different from", "the same as".
- Spoken forms: "a lot of", "more and more", "nowadays", "and so on".
- Articles: a singular countable noun needs "a" or "the"; a quantity named for the first time usually takes "a", the same one afterwards "the".
- "Respectively" only when two lists of equal length really pair, and never for a single item.
- Sentence openers used as fillers: "Besides,", "Recently,", "Meanwhile,".

Correct these; do not rewrite the sentence around them.

### Step 7. What an edit must not touch

- Numbers, units, symbols, equations, citations, labels.
- The strength of a claim: no hedge removed, no verb raised, no limit dropped from the Results. A limitation restated in another section is reported to the author under ground rule 10, not cut silently.
- Technical terms and the names of methods, even when a plainer word exists.
- Statements with fixed wording: the declarations, the venue's prescribed sentences, quotations.
- A correct sentence in the author's own manner. The aim is a paper that reads like its authors at their clearest, not like every other paper.

### Step 8. Check the edit

```
python scripts/prose_lint.py --compare before/main.tex main.tex
python scripts/prose_lint.py main.tex
```

- `--compare` lists every number, citation key, reference label and formula that is in one version and not in the other, and the count of hedges before and after. Anything listed is restored, or shown to the user as a change of content. Exit status 1 means the edit changed protected content.
- The second run shows the new profile. Hits that remain are either wanted (a "novel" in a quotation) or still to do.
- `python scripts/audit_tex.py main.tex --checks tone,punct,voice,limits` lists the marks of machine tone, colons and semicolons, passive voice for our own work, and limitation sentences outside the Results.
- Numbers must also agree across the text, the captions and the tables (ground rule 16). The audit traces each one to its source (`parts/audit.md`, pass C). Report a disagreement found while polishing, and never fix it by editing a value.
- Then read each paragraph once as the target reader. Mark every place where you had to read twice; those are the remaining faults, whatever the lint says.

### When rules pull in different directions

Meaning first, then the venue's style, then clarity, then brevity, then the author's manner. Where a plainer sentence would lose a qualification, keep the qualification.

## Checks

1. **Meaning kept**: `--compare` reports no changed number, citation, label or formula; no hedge was removed without the author's decision.
2. **Paragraphs**: one point each, stated first; no recap closer; no paragraph about the text.
3. **Flow**: sentences begin with what is known and end with what is new; connectors only where the logic needs them.
4. **Sentences**: actor as subject, action as verb; none over 40 words in the body; lengths vary.
5. **Reference words**: every "this", "it" and "they" has one obvious antecedent.
6. **Terms**: one term per thing, as in `notation.md`.
7. **Words**: plain; verbs not nominalized; quantities as numbers; no intensifiers or evaluation.
8. **Machine tone**: no pattern of Step 5 remains, and each was repaired at its cause.
9. **Abbreviations**: defined once in the abstract and once in the text; each used at least three times.
10. **Form**: one spelling variety; no contractions; venue's style for dashes, lists and headings.
11. **Untouched**: fixed wordings, technical terms and correct sentences in the author's manner were left alone.
12. **Read through**: no sentence needs a second reading.
13. **Punctuation and context**: no colon, semicolon or joining dash in running text; every paragraph follows from the one before (ground rules 14 and 15).

## Report

Reply in the user's language. Keep it short:

1. **Profile before and after**: sentences, mean length, share over 30 words, hits per category.
2. **Changes by kind**, with two or three before-and-after pairs for each kind that matters; the full difference as a file when the user wants it.
3. **`--compare`**: its last line, and every item it listed.
4. **Left for the author**: sentences whose meaning was unclear and were not changed; claims that seem stronger than `brief.md` allows; hits that were kept on purpose.

In Audit mode, give items 1 and 4 and the list of hits with the smallest fix for each.

Propose only, as an edited copy beside the original. Never trade accuracy for smoothness: a clumsy sentence that is right stays until a right one replaces it.

## Example (invented)

Before:

> It is worth noting that noncollinear antiferromagnets have attracted considerable attention in recent years, playing a pivotal role in next-generation spintronics. In this work, we performed a comprehensive investigation of the switching dynamics, which may potentially suggest a novel mechanism, highlighting the remarkable potential of tilted films. Overall, these findings pave the way for future memory applications.

Hits: filler ("It is worth noting that", "have attracted considerable attention", "in recent years"); inflated ("pivotal", "comprehensive"); hidden verb ("performed a ... investigation of"); stacked hedges ("may potentially suggest"); praise ("novel", "remarkable", "pave the way"); a hung-on tail; a recap closer. Asked what each sentence claims: the first claims nothing that the introduction has not cited; the second claims a mechanism that the paper either shows or does not; the third claims nothing.

After:

> Switching a noncollinear antiferromagnet by current has so far required a magnetic field [A, B]. We simulated the reversal in films whose kagome plane is tilted, and found that the tilt replaces the field. The current alone sets the final state.

The first sentence now carries its citations. The mechanism is stated as found, because Fig. 2 shows it; had it been only suggested, one "suggests" would say so. The third sentence is gone. `--compare` lists the citation keys A and B as present only after the edit, and two hedges fewer. Both changes were put to the author: the citations were moved up from the next sentence, and the hedges stood in the sentence that Fig. 2 supports.

## Relation to other parts

- **Every writing part** sets rules for its own section; this part applies the rules common to all and leaves the special ones in force.
- **Notation** (`parts/notation.md`) supplies the terms. **Equations** governs displayed mathematics.
- **Brief and discussion** fix the strength of each claim; this part does not move it.
- **Submit** (`parts/submit.md`): the statements of data, funding, interests and AI use are not restyled, and the disclosure of AI tools is unaffected by this part.
- **Audit** (`parts/audit.md`) runs the lint on the final text and the comparison against the last approved version.

## What this part cannot do

- The lint finds strings. It cannot tell praise from a technical use of the same word, and it cannot see an empty sentence written in plain words. The reading in Step 8 can.
- No list of patterns stays current: the habits of language models change, and so do the words on the lists.
- It cannot make a claim clear when the claim itself is not settled. Such sentences go back to the author, unchanged.

## Sources

The sources behind these choices are in `references/prose-evidence.md`; read it when you need to explain a choice.
