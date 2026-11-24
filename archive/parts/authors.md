# Authors and acknowledgments

The byline and the acknowledgments say who answers for the work, who helped, and who paid. Indexes, funders, employers and committees read them more carefully than they read the paper.

They have two jobs:

- **Credit and accountability are placed correctly.** Everyone who qualifies as an author is one; no one else is; help and funding are acknowledged for what they were.
- **Every name can be matched.** Authors, institutions and funders appear in the exact form under which databases know them.

One rule stands above the rest: **this part decides nothing.** Who is an author, in what order, and with which affiliation are decisions of the authors. The agent formats what they decided, checks it for consistency, and asks about everything else. It never adds, removes or reorders a name.

Modes:
- **Build**: write the byline, the footnotes and the acknowledgments from the Record of `brief.md`.
- **Audit**: report pass/fail per test and the smallest fix; change nothing.

## 1. Read before writing

1. `brief.md`, section Record: contributors and what each did, funding, thanks, history.
2. `venue.md`: the form of names and affiliations, the layout of the byline, footnote marks, how the contact author is given, how equal contribution is marked, identifiers, where acknowledgments and funding go, and whether the review is anonymized.
3. The authors' earlier papers, or their own statement, for the form of each name.

Whatever is missing is a question for the user; nothing here can be looked up or guessed.

## 2. Who is listed

- **The authors decide, by their field's and the venue's criteria.** A common statement of them: a substantial contribution to the conception or design of the work, or to obtaining, analysing or interpreting its data; a part in drafting or critically revising the text; approval of the final version; and willingness to answer for the work. Many venues ask that all who meet their criteria be authors and that all authors meet them.
- **Flag, do not judge.** A contributor in the Record with no stated contribution; a person thanked for work that the Record describes as central; an author who has not seen the final version: each is a question for the user.
- **Contributors who are not authors** are acknowledged, with what they did.
- **An AI tool is not an author** and is not thanked. Its use is disclosed where the venue asks (`parts/declarations.md`).

## 3. Names

- The form each author uses in other publications, so that their papers are found under one name: the same given names or initials, the same spelling, the same diacritics. Ask each author; do not normalize.
- Full given names where the venue allows them.
- A name in its own script beside the romanized form, where the author wants it and the venue offers it.
- A persistent identifier (ORCID) for every author who has one, entered where the venue takes it.
- Collaborations and consortia in the venue's form.

## 4. Order and marks

- The order is the authors' statement, made by their field's convention. Record it as given.
- Equal contribution, present address and deceased authors are marked as the venue prescribes, in its wording and with its symbols in its order.
- A sentence that explains the order, where the authors want one, goes with the contribution statement.

## 5. Affiliations

- The institution where the work was done. A later affiliation is a "present address" footnote, not a second affiliation.
- The official name of the institution in the language of the paper, written the same way for every author, in the order the venue gives: department, institution, city, country.
- The layout the venue uses: addresses grouped under the authors, or numbered and linked by superscripts. Do not reorder authors to suit a layout.
- Every author has at least one affiliation or an address.

## 6. Contact author

- The author who will answer questions after publication, with an address that will still work in five years. More than one may be named.
- In the venue's form and place: a byline footnote in many physics journals, a line under the affiliations or an end note elsewhere.
- The contact author for readers need not be the person who handles the submission.

## 7. Acknowledgments

One short paragraph, in this order: people, facilities, funding.

- **People**: who, and for what. "We thank A. B. for the samples of series II" tells the reader something; "for fruitful discussions" tells little, and "for help" nothing.
- **Facilities and computing time**: in the wording the facility prescribes, where it prescribes one. Ask the user for it.
- **Funding**: the funder's official name, the grant number, and the author it was awarded to, by initials where the venue wants that. Funders often prescribe the sentence; use theirs. Where the venue wants funding as a separate statement, the same content goes there.
- **Leave out**: thanks for typing, editing or general encouragement; dedications; thanks to anonymous referees where the venue asks authors not to give them; any mention of AI tools; author contributions, which have their own statement.
- **Plain wording.** "We thank", not "we are deeply indebted to" or "we gratefully acknowledge the invaluable".
- People thanked by name should know it and agree; ask the user to confirm.

## 8. Anonymized review

Where the venue hides the authors from referees: remove the byline, the acknowledgments and the funding from the review copy, as the venue instructs, and keep them in a separate file for the final version. The rest of the anonymization (self-citations, file properties) is in `parts/submit.md`.

## 9. Test

1. **Decided by the authors**: the list and the order were given by the user; nothing was added, removed or reordered.
2. **Names**: each in the form its author uses elsewhere; diacritics intact; identifiers entered.
3. **Affiliations**: where the work was done; official names, one spelling each; venue's order and layout; present addresses as footnotes.
4. **Marks**: equal contribution, contact author and other footnotes in the venue's wording and symbols.
5. **Contact**: at least one contact author with a lasting address.
6. **Acknowledged, not listed**: every contributor of the Record is either an author or acknowledged, with what they did.
7. **Funding**: official funder names, grant numbers, recipients; prescribed wordings used.
8. **Nothing misplaced**: no AI tool, no contribution statement and no dedication in the acknowledgments.
9. **Consistency**: the same names, order and affiliations in the manuscript, the supplement's title page, the cover letter and the submission form.
10. **Review copy**: anonymized where the venue requires it.

## 10. Report

Reply in the user's language. Keep it short:

1. **Byline and footnotes**, as source for the venue's template.
2. **Acknowledgments.**
3. **Questions**: every name form, affiliation, grant number or prescribed wording that was not confirmed.
4. **Flags**: a contributor without a stated contribution; a person thanked for central work; a difference between the manuscript and another file.

Propose only. Questions of authorship are answered by the authors; if they disagree among themselves, say so to the user and stop.

## Example (invented)

Before:

> The authors would like to gratefully acknowledge the invaluable help and fruitful discussions with many colleagues. This work was supported by the national research foundation. We also thank ChatGPT for improving the language.

Fails: nobody is named and nothing they did; the funder is not identified and has no grant number; an AI tool is thanked.

After:

> We thank C. Colleague for the tilted Mn3Sn films and D. Colleague for discussions on the torque symmetry. Simulations ran at the [name] computing centre under project 0000. This work was supported by [funder, official name] under Grant No. 0000 (B.A.).

The use of the language tool goes into the disclosure that the venue asks for.

## Relation to other parts

- **Brief** (`parts/brief.md`) holds the Record this part is written from.
- **Declarations** (`parts/declarations.md`) writes the contribution statement, competing interests, funding where it is a separate statement, and the disclosure of AI tools.
- **Venue** (`parts/venue.md`) supplies every form.
- **Supplement and submit**: the same byline on the supplement's title page, in the cover letter and in the submission form.
- **Audit** (`parts/audit.md`) compares the initials in the contribution statement and the funding with the byline.

## When rules pull in different directions

The authors' decisions first, then the venue's form, then consistency with the authors' earlier papers.

The journal rules and standards behind these choices are in `references/authors-declarations-evidence.md`; read it when you need to explain a choice.
