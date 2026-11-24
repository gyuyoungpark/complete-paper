# Declarations

The declarations are the statements at the end of a paper: where the data and the code are, who did what, what interests the authors have, who funded the work, and which tools were used. Each is short, and each is a commitment that someone may test: a reader asks for the data, an editor checks the identifier, an employer reads the interests.

They have two jobs:

- **True and specific.** Each statement says something that can be checked, and it holds when checked.
- **Complete for the venue.** Every statement the venue requires is present, under its heading, in its place and order.

Rule for every statement: **the agent declares nothing on its own.** The facts come from the Record of `brief.md`, confirmed by the user. "The authors declare no competing interests" is written only when the user has said so.

Modes:
- **Build**: draft every statement the venue requires.
- **Audit**: report pass/fail per test and the smallest fix; change nothing.

## 1. Read before writing

1. `venue.md`: which statements are mandatory, their headings, their order and place, any fixed wording, and what is entered in the submission form instead of the manuscript.
2. `brief.md`, section Record: contributors, funding, data and code, competing interests, AI tools.
3. `suppmap.md`: the data package, its repository and identifier.
4. The methods: what software and which data sets the work used.

## 2. Which statements, and where

The venue decides. Collect its list first; a typical one:

| Statement | Says | Usual place |
|---|---|---|
| Data availability | where the data behind the results are, and under what conditions | after the acknowledgments, or after the methods |
| Code availability | where the code is, and which version | with the data statement, or separate |
| Author contributions | who did what | after the acknowledgments |
| Competing interests | interests that could be seen to bear on the work | near the end; often also in a form |
| Funding | who paid | in the acknowledgments, or a separate statement |
| Use of AI tools | which tools were used for what | a section of its own, the methods, or the form |
| Ethics and consent | approval and consent for work with people or animals | in the methods, where the data collection is described |

Order and headings are the venue's. Write nothing in the acknowledgments that the venue wants as a statement, and the reverse.

## 3. Data availability

Say where the data are and what a reader will find there. The forms, from best to weakest:

| Situation | Statement |
|---|---|
| Deposited | "The data that support the findings of this article are openly available at [repository], [identifier] [ref]." Add in a clause what is there: the numbers behind every figure, the raw output, the input files |
| In the paper | "All data are contained in the article and its Supplemental Material." Only if that is literally so |
| Restricted | What is restricted, why (third-party ownership, export control, privacy), and how access can be asked for |
| None | "No data were created or analyzed in this study." For work that is purely analytical |
| On request | Only when nothing above is possible; requests often go unanswered and data kept by authors are lost. Say who answers and for how long |

- The statement agrees with the data package of `parts/supplement.md`: same repository, same identifier, same contents.
- A deposited data set is cited as a reference, with creators, year, version, repository and identifier, where the venue asks for that (`parts/references.md`).
- The identifier resolves on the day of submission. A placeholder does not go out.
- Do not promise what will not be done: "available upon publication" needs someone who will make it so.

## 4. Code availability

- Where the code is, the version or commit that produced the figures, and its licence. An archived release with an identifier outlasts a link to a repository.
- Third-party software is cited in the methods with name and version; it does not need to be in this statement.
- If the code cannot be shared, say so and say what is shared instead: the algorithm in the methods, the input files, the processed output.

## 5. Author contributions

- One entry per author, by initials, with roles from the venue's taxonomy. Where the venue uses CRediT, its fourteen roles are: Conceptualization; Data curation; Formal analysis; Funding acquisition; Investigation; Methodology; Project administration; Resources; Software; Supervision; Validation; Visualization; Writing – original draft; Writing – review & editing.
- Every author has at least one role. Every role named was performed by someone. The roles agree with the Record of `brief.md`.
- Equal contribution and any note on the order of authors go here or in the byline, as the venue has it.
- Initials match the byline exactly; two authors with the same initials are told apart.

## 6. Competing interests

- What counts is set by the venue; typically employment, paid roles, equity, patents and patent applications related to the work, and funding with an interest in the outcome. Some venues add restrictions on sharing data or methods.
- Ask the user directly, naming these categories. A patent application on the method of the paper is a competing interest even when it seems obvious to the authors.
- State each interest plainly: who, what, and its relation to the work.
- If there are none, use the venue's sentence for that case.

## 7. Use of AI tools

A manuscript prepared with this skill has been drafted or revised with an AI tool. Most venues want to know.

- **Find the venue's rule** in `venue.md`: what must be disclosed, what need not be (some venues exempt copy editing for grammar and style), and where the statement goes (a section of its own, the methods, the submission form).
- **Tell the user what was done.** List, from this project, the tasks the tool performed: drafting or revising text, the search for literature, code for analysis or figures, the making of figures. The user decides the wording and is responsible for it.
- **State tool and task.** "The authors used [tool, version] to draft and revise parts of the text and to write the plotting scripts. The authors reviewed all content and take full responsibility for it."
- An AI tool is not an author and is not thanked in the acknowledgments.
- **Never leave out or soften a disclosure that the venue requires.** Editing the prose so that it reads well (`parts/prose.md`) changes nothing about this duty. If the user asks to omit a required disclosure, decline and say why.

## 8. Wording

- One or two sentences each. Present tense. No adjectives.
- The venue's fixed sentences are used word for word.
- No statement contradicts another, the methods, the acknowledgments or the submission form.
- `parts/prose.md` does not restyle these statements.

## 9. Check

- The list of step 2 against `venue.md`: every required statement is present, under the venue's heading, in its order.
- Each identifier and link opens what the statement says.
- Initials in the contribution statement and in the funding against the byline.
- `python3 scripts/audit.py main.tex --require data competing contributions` reports required statements that are missing, a data statement that offers data on request only, and initials that match no author.

## 10. Test

1. **Complete**: every statement the venue requires is present, with its heading, place and order.
2. **Confirmed**: every fact comes from the Record or the user; nothing was assumed, least of all the absence of interests.
3. **Data**: a place, an identifier that resolves, and what is there; agreement with the data package; cited where the venue asks.
4. **Code**: place, version, licence; or what is shared instead.
5. **Contributions**: every author has a role; taxonomy as the venue wants; initials match the byline.
6. **Interests**: each stated plainly, or the venue's sentence for none, confirmed by the user.
7. **AI tools**: disclosed as the venue requires, with tool and task; not in the acknowledgments.
8. **Funding and ethics**: where the venue puts them; consistent with the acknowledgments and the methods.
9. **Fixed wordings**: used exactly.
10. **No contradiction** between statements, manuscript, cover letter and form.

## 11. Report

Reply in the user's language. Keep it short:

1. **The statements**, in the venue's order.
2. **Questions**: each fact that needs the user's confirmation, as a yes-or-no question where possible.
3. **Flags**: an identifier that does not resolve; a required statement with no content; a disclosure the user must decide on.

Propose only. These statements are made by the authors; the user approves each one.

## Example (invented; names, numbers and identifiers are placeholders)

> **Data availability.** The data that support the findings of this article are openly available at Zenodo, doi:10.5281/zenodo.0000000 [31]: the numbers behind every figure, the output of all 212 simulation runs, the input files and the scripts.
>
> **Author contributions.** A.A.: Investigation, Software, Formal analysis, Visualization, Writing – original draft. B.A.: Conceptualization, Methodology, Supervision, Funding acquisition, Writing – review & editing.
>
> **Competing interests.** B.A. is an inventor on a patent application related to the tilted-film memory cell described here. A.A. declares no competing interests.
>
> **Use of AI tools.** The authors used [tool, version] to revise the text for readability and to write the scripts that draw the figures. The authors reviewed all content and take full responsibility for it.

A first draft read: "Data are available from the corresponding author upon reasonable request. The authors declare no competing interests." It failed tests 2, 3 and 6: a deposit existed and was not named, and the patent application had not been asked about.

## Relation to other parts

- **Brief** (`parts/brief.md`) holds the facts. **Authors** (`parts/authors.md`) writes the byline and the acknowledgments.
- **Supplement** (`parts/supplement.md`) builds the data package that the data statement names.
- **Methods** and **references**: software and data sets are cited there; a deposited data set is a reference.
- **Submit** (`parts/submit.md`) enters the same statements in the submission form.
- **Audit** (`parts/audit.md`) checks that the required statements are present and agree.

## When rules pull in different directions

Truth first, then the venue's requirements, then brevity. Where the venue's rule is not known, disclose more, not less.

The journal rules and standards behind these choices are in `references/authors-declarations-evidence.md`; read it when you need to explain a choice.
