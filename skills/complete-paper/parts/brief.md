# Brief

Stage A · Reads: the user's results, notes, figures, data and any draft, `intake.md`, `venue.md` if it exists · Writes: `paper-state/brief.md`, `paper-state/progress.md`

The brief is the one file that says what the paper claims, what the claim rests on, and what the paper does not show. Every other part starts from it: the title, the abstract, the outline, the introduction, the conclusion, the choice of references and the supplement all read the same five lines. A paper whose parts were written from five different readings of the result contradicts itself; a paper written from one brief cannot.

It has two jobs:

- **Fix the claim once.** One result, one system, one kind of evidence, stated before any section is written and changed only on purpose.
- **Hold what only the authors know.** Which result matters, what a referee will attack, who did what, who paid, where the data are, which tools were used. The skill derives everything else from the manuscript and the venue.

Rule for every line: **write down what exists, not what is hoped for.** A result that is not in the notes, the figures or the user's words does not enter the brief.

## Modes

- **Write** (build): no brief yet. Read what exists, draft, ask the user once for what cannot be read.
- **Write** (minimal): another part was called alone and needs a brief now. Fill only the five claim fields, mark the rest "not yet".
- **Revise** (update): a result, a number or the scope has changed. Change the brief first, then list the parts that must follow.
- **Audit**: check a manuscript against the brief; report pass/fail per check and the smallest fix; change nothing.

## Inputs

1. Everything that exists: figures and their scripts, data folders, notes, slides, an old draft, an abstract written for a conference.
2. `venue.md`, if the venue is already chosen: its criteria decide how MATTERS is worded.
3. The closest earlier papers, if the user names them.
4. `paper-state/intake.md`: what the authors have already recorded about contributors, funding, data and history (Step 5).

List what was read at the top of the report. If only a spoken description exists, work from it and say so.

## Steps

### Step 1. Write the five claim fields

| Field | Content | Rules |
|---|---|---|
| RESULT | What the paper shows | One sentence of at most 30 words, with the finding as its subject and the headline number if the claim is quantitative. No second finding joined by "and". No words of praise |
| SYSTEM | The material, device, model or data set, with its regime | Composition and geometry; the ranges of temperature, field, size or time in which the result was obtained |
| METHOD | How the result was obtained | Only as far as a reader needs it to place the result: "atomistic spin-dynamics simulation at zero temperature", not the solver settings |
| EVIDENCE | The kind of evidence, and the items that carry it | The kind is one of: experiment, simulation, theory, method, dataset, review. The kind sets the verbs the paper may use (table in `parts/abstract.md`) |
| NOT SHOWN | What the paper does not show | Untested regimes, idealizations of the model, missing controls, alternative explanations not excluded. At least two entries. Write each as a fact: "thermal fluctuations were not included" |

- **RESULT is the answer to a question.** Write the question first (Step 2); a result with no question is a list of observations.
- **Two results** mean two papers, or one result and its support. Choose; the other becomes a statement of the claim chain in `outline.md`.
- **NOT SHOWN is not a weakness list to hide.** It is the boundary that keeps the title, the abstract and the conclusion from saying more than the figures do. Ask: what will the first referee say is missing? A brief with an empty NOT SHOWN is not finished. The brief records each entry plainly. The manuscript states each one once, in the Results where the evidence it bounds is presented, and the other parts look forward from it (ground rule 10 in `SKILL.md`).
- **Every content word of RESULT needs evidence.** "Field-free", "deterministic", "universal", "robust": each one names something that must have been tested (Step 4).

### Step 2. Place the result

| Field | Content |
|---|---|
| QUESTION | What was unknown or unresolved before this work, as one sentence |
| PRIOR | The one to three closest earlier works, by citation key, and what each left open |
| DIFFERENCE | What this paper adds to them, in one clause |
| MATTERS | Who needs the answer, and what it lets them do or decide |

These four feed the gap and the importance of the introduction (`parts/intro.md`), which states the gap as a need rather than an absence (ground rule 10), and the choice of references (`parts/bibliography.md`). If the user cannot name PRIOR, the literature search of the bibliography part comes before the brief is closed.

### Step 3. Record the key numbers

One row for every number that will appear in the title, the abstract or the conclusion, and for the headline number of each main figure.

```
| # | Quantity | Symbol | Value | Unit | Uncertainty or range | Condition | Source | Used in |
|---|---|---|---|---|---|---|---|---|
| 1 | switching time | t_sw | 0.22 | ns | 0.01 | tilt 45 deg, 6e11 A/m^2 | fig2/make_fig2.py | abstract, Fig. 2 |
```

- **Source** is a file, a script or a figure from which the number can be produced again. A number without a source is a question for the user.
- **One value, one rounding.** The manuscript quotes each key number exactly as it stands here. `parts/audit.md` compares every occurrence against this table.
- A ratio, a percentage or a "factor of" is a number too, and needs both of its ingredients in the table.

### Step 4. Map the evidence

For every statement that RESULT needs, name the item that supports it and its state.

```
| # | Statement that RESULT needs | Kind | Item | Status |
|---|---|---|---|---|
| 1 | With a tilted plane, current alone reverses the moment | simulation | Fig. 2, traces at four angles | ready |
| 2 | Without tilt, it does not | simulation | Fig. 2, trace at 0 deg | ready |
| 3 | The threshold follows the model | simulation and theory | Fig. 3, Eq. (1) | partial: three angles missing |
```

Status is `ready`, `partial` or `missing`. Rows that are not `ready` are the holes that `parts/outline.md` carries forward. A content word of RESULT with no row is removed from RESULT.

Below the table, list the **inventory**: every figure, data set and derivation that exists, with its path, whether or not the paper will use it. The outline chooses from this list and sends the rest to the supplement, the data package or nowhere.

### Step 5. Record what only the authors know

These facts are held in `paper-state/intake.md`, which the authors fill from `assets/intake.md` and their saved defaults ("How to start" in `SKILL.md`). The brief's Record section gives each one in a line, copied from the intake, so that every part sees at once what exists. Where the two differ, the intake wins.

| Entry | In `intake.md` | Used by |
|---|---|---|
| Contributors, and what each one did | 1. Authors; 4. Declarations | `parts/submit.md` |
| Funding: funder, grant number, which author | 3. Funding | `parts/submit.md` |
| Facilities, computing time, people to thank and for what | 2. Acknowledgments | `parts/submit.md` |
| Data and code: where they are, what can be shared, any restriction | 4. Declarations | `parts/supplement.md`, `parts/submit.md` |
| Competing interests: patents, employment, paid roles | 4. Declarations | `parts/submit.md` |
| AI tools used, and for which tasks | 4. Declarations | `parts/submit.md` (ground rule 9) |
| Earlier versions: preprint, conference paper, earlier submission and its reports | 5. Submission | `parts/submit.md`, `parts/title.md` |

Ask for what the intake leaves blank once, at the start. An item that is asked for on the day of submission is the item that gets invented.

### Step 6. Ask the user once

Collect every open point and ask in one message, in the user's language, shortest question first. Typical questions:

1. In one sentence, what does the paper show?
2. What was not known before it?
3. Which paper is closest, and what did it not do?
4. What will a referee say is missing?
5. Which numbers must appear in the abstract?
6. Who did what, who funded it, where are the data?

Offer the draft answer with each question, so that the user corrects a sentence and does not write one. Mark every field that still rests on the agent's reading as `[unconfirmed]`.

### Step 7. Write `brief.md`

Keep it in `paper-state/`.

```
# Brief: <working title>
Updated: <date>   Version: <n>   Read: <files and notes this was built from>

## Claim
RESULT: <one sentence>
SYSTEM: <material, device, model or data set; regime>
METHOD: <how, as far as it bounds the claim>
EVIDENCE: <kind>; <the items that carry the result>
NOT SHOWN:
- <fact>
- <fact>

## Question
QUESTION: <one sentence>
PRIOR: <key: what it left open>; <key: ...>
DIFFERENCE: <one clause>
MATTERS: <who needs it, and for what>

## Key numbers
| # | Quantity | Symbol | Value | Unit | Uncertainty or range | Condition | Source | Used in |

## Evidence
| # | Statement that RESULT needs | Kind | Item | Status |

## Inventory
| Item | What it is | Path | Used |

## Record
Contributors: <initials: what each did>
Funding: <funder, grant number, author>
Thanks: <who, for what>
Data and code: <where; what can be shared>
Competing interests: <none, or what>
AI tools: <none, or tool and task>
History: <preprint, earlier submission>

## Open
- <question for the user>
```

Check it: `python scripts/brief_check.py brief.md` reports missing or unfilled fields, a RESULT that is too long or carries words of praise, an evidence kind outside the list, key numbers without unit or source, one quantity with two values, numbers in RESULT that are not in the table, and evidence rows that are not ready. With `--tex main.tex` it also lists the key numbers whose value does not occur in the manuscript.

### Step 8. Update

When a result changes, the brief changes first.

1. Edit the field, raise the version, and add a line under `## Open`: what changed, and why.
2. Name the parts that read the changed field: RESULT and NOT SHOWN reach the title, abstract, introduction, conclusion and outline; a key number reaches every place in its "Used in" column; SYSTEM and METHOD reach the abstract and the methods.
3. Do not edit a section to say something the brief does not say. If the section is right, the brief is out of date: update it.

### When rules pull in different directions

What the evidence supports comes first, then the user's statement of the result, then brevity. If the user's RESULT says more than the evidence table carries, say which word has no row and offer the narrower sentence; do not narrow it silently and do not write the wider one.

## Checks

1. **One result**: RESULT is one sentence of at most 30 words with one finding; it answers QUESTION.
2. **Written down**: every field traces to a file, a figure or the user's statement; nothing is inferred; unconfirmed fields are marked.
3. **Evidence kind**: one of the six kinds, and the verbs used for the result anywhere in the manuscript agree with it.
4. **Backed**: every content word of RESULT has a row in the evidence table.
5. **Boundary**: NOT SHOWN has at least two entries, each a fact, and includes the objection a referee would raise first.
6. **Placed**: QUESTION, PRIOR, DIFFERENCE and MATTERS are filled; PRIOR names real, checked works.
7. **Numbers**: every number of the title, abstract and conclusion is in the table with unit, uncertainty and source; no quantity has two values.
8. **Holes**: every evidence row that is not `ready` is listed for the outline.
9. **Record**: contributors, funding, data, competing interests and AI tools are filled or marked "none".
10. **No praise**: no "novel", "first", "unprecedented", "remarkable" in any field.

In Audit mode add: every claim sentence of the title, the abstract, the last paragraph of the introduction and the conclusion says what RESULT says and stays inside NOT SHOWN; every key number is quoted as in the table.

## Report

Reply in the user's language. Keep it short:

1. **The five claim fields**, as they now stand.
2. **Questions**, each with a draft answer.
3. **Holes**: evidence that is partial or missing, and what would close each.
4. **Flags**: fields marked unconfirmed; numbers without a source; a second result that was set aside.

In Revise (update) mode, give the change and the list of parts that must follow. In Audit mode, give the table of checks and the smallest fix for each failure.

Propose only. The brief is the authors' statement of their own result: the user approves it before any section is written.

## Example (invented; the physics and the numbers are placeholders)

`examples/brief/brief.md` is the brief of the example manuscript in `examples/supplement/`. Its claim fields:

> RESULT: Tilting the kagome plane of Mn3Sn lets a current alone reverse the octupole moment, above a threshold that falls as the inverse sine of the tilt angle.
> SYSTEM: Mn3Sn (20 nm)/W bilayer, single domain, tilt angles from 5 to 45 degrees.
> METHOD: Simulation of the three sublattice moments under spin-orbit torque, with an analytical torque balance.
> EVIDENCE: simulation; Fig. 2 (reversal at four tilt angles), Fig. 3 (threshold against the model).
> NOT SHOWN: domain walls and multidomain states were not simulated; no experiment; the threshold was not tested below 5 degrees; temperature enters only as a check at 300 K.

A first draft of RESULT read "We demonstrate ultrafast, robust and field-free switching and establish a universal scaling law." It failed four checks: two findings joined by "and"; "demonstrate" for a simulation; "ultrafast", "robust" and "universal" without a row of evidence; no system.

## Relation to other parts

- **Venue** (`parts/venue.md`) is chosen with the brief: MATTERS is worded for that venue's criteria.
- **Outline** (`parts/outline.md`) turns RESULT into the central claim and the evidence table into the claim chain; it never widens the brief.
- **Title, abstract, introduction, conclusion** read the five claim fields and use the same words for the result.
- **Bibliography** (`parts/bibliography.md`) verifies PRIOR and searches from QUESTION.
- **Submit** (`parts/submit.md`) takes the Record section, through `intake.md`.
- **Audit** (`parts/audit.md`) checks every claim sentence and every key number of the finished manuscript against this file.

## What this part cannot do

It cannot judge whether the result is correct or important. It can only make sure that the paper says one thing, that the thing is written down, and that its limits are stated.
