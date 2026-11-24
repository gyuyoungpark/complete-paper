# Equations

Stage B · Reads: `notation.md`, `venue.md`, the derivation (notes, code or the existing draft) · Writes: the displayed equations of a section, with labels; new symbols go into `notation.md` first

An equation in a paper has two jobs. It must be **followable**: a reader of the target venue can see where it comes from and what it says. And it must be **citable**: any sentence, caption, table or supplement section can point to it exactly, and the pointer stays correct when the paper is reordered.

## Modes

- **Write**: turn derivation notes or results into the equations of a section.
- **Revise**: keep the mathematics; fix order, definitions, layout and references.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

Read before writing:

1. `notation.md`: only its symbols may be used. A new symbol is added to the table first (see `parts/notation.md`).
2. `venue.md`: numbering style, the citation form ("Eq. (3)" or "(3)"), rules for appendices and supplementary material.
3. The derivation itself: notes, code or the existing draft. Do not invent steps or results; if a step cannot be reconstructed from what is given, ask.

## Steps

### Step 1. Plan the chain

Before writing, list the chain in one line each:

1. **Starting point**: an equation the field already accepts, by name (a conservation law, a model Hamiltonian, an established equation of motion), with a citation unless it is textbook material.
2. **Assumptions and approximations**, each with the condition under which it holds.
3. **Steps** that a reader in the field cannot do in their head.
4. **Result**: the equation that Results, figures or the abstract rely on.

If the chain has more than about five displayed steps, the main text keeps the starting point, the assumptions, the key intermediate and the result; the rest goes to an appendix or the supplement, cited by equation number.

### Step 2. Write

- **Start from common ground.** Name the starting equation and its source, and define every symbol in it. A paper that opens with its own final formula leaves the reader no way in.
- **Say what happens between equations.** Each displayed equation is introduced by the operation that produced it: "Linearizing Eq. (2) about the equilibrium direction gives". Never "it can easily be shown that".
- **State approximations where they enter**, with their range of validity ("for kd << 1"), not in a list at the end.
- **One message per equation.** After a result, say in a sentence what it means physically: what each term represents, or what a limiting case gives.
- **Display or inline.** Display an equation that is referred to later, is a main step or result, is long, or contains built-up fractions, sums or integrals. Short expressions stay in the line.
- **Equations are part of the sentence.** Punctuate them. The "where" clause that follows is not indented, starts in lower case, and defines the new symbols in the order they appear.
- **Layout.** Break and align multi-line equations at relation signs. Nest brackets as ( ), then [ ], then { }. Slashed fractions in the line, built-up fractions in display, never `a/b/c`. The multiplication cross is for vector products and scientific notation, the centred dot for scalar products of vectors. Named functions are roman.
- **Quantity equations.** Write equations between quantities, which hold in any units of the declared system. If an equation holds only for numerical values in particular units, say so next to it.
- **Operators and numbers.** Keep the kind of every symbol visible (see the hat rules in `parts/notation.md`), and say where a quantum expression is replaced by a classical one.

### Step 3. Number and cite

- **Number every displayed equation that is cited anywhere**, and by default every displayed equation in the main text, so that co-authors, referees and later papers can point to any of them. Follow the venue's style; a common one is (1), (2) in the body, (1a) and (1b) for a group, (A1) in an appendix and (S1) in supplementary material.
- **Never type an equation number.** Use a label and a reference (`\label{eq:dispersion}` with `\eqref{eq:dispersion}`; cross-reference fields in a word processor). Name labels by content, not by number, so that they survive reordering.
- **Cite in the venue's form**, the same way everywhere: for example "Eq. (3)", "Eqs. (3) and (4)", "Eqs. (3)-(5)", and "Equation (3)" at the start of a sentence.
- **Cite after the equation has appeared.** The exception is an explicit pointer to an appendix or the supplement.
- **Captions, tables and the supplement cite the same numbers.** A caption that needs a formula refers to it by number instead of repeating it in different notation. References from the main text to the supplement say so: "Eq. (S3) of the Supplemental Material".
- **No loose ends.** Every reference resolves; no label is defined twice; every numbered equation in the main text is either cited or a step of the chain.
- After any reordering, recompile twice and run `python scripts/eq_refs.py main.tex supplement.tex`. It lists unresolved references, duplicate labels, displayed equations without a label, labels never cited, and equation numbers typed by hand.

### When rules pull in different directions

Correctness of the mathematics first, then the venue's numbering and citation style, then followability for the venue's reader, then brevity. A derivation is shortened by moving steps to an appendix, never by leaving them out.

## Checks

1. **Starting point**: the chain begins from a named, accepted equation with its source.
2. **Followable**: each displayed equation is introduced by the operation that produced it; no step is skipped that the venue's reader could not supply; long algebra is in an appendix or the supplement and cited.
3. **Assumptions**: each approximation appears where it is used, with its condition.
4. **Symbols**: every symbol is in `notation.md` and is defined at or directly after its first equation; no symbol changes meaning along the chain.
5. **Sentences**: every displayed equation is punctuated and read as part of its sentence.
6. **Meaning**: each result equation is followed by what it says physically.
7. **Numbering**: the venue's style; every cited equation numbered; no number typed by hand.
8. **References**: all resolve; none points forward except to an appendix or the supplement; captions and supplement use the same numbers; the citation form is uniform.
9. **Units**: equations are in the declared unit system; numerical-value equations say their units.

## Report

Reply in the user's language. Keep it short:

1. **Chain**: starting point, assumptions, result, and which steps moved to the appendix or supplement.
2. **The equations**, as LaTeX, with labels.
3. **Checks**: only the failures and the unchecked items, with the output of `eq_refs.py` if it was run.
4. **Flags**: steps that could not be reconstructed, approximations whose validity range is not stated in the source, symbols added to `notation.md`.

Propose only. Edit the manuscript when the user asks.

## Relation to other parts

- **Notation** (`parts/notation.md`): symbols, typefaces, hats and units. This part adds no symbol without it.
- **Methods and Results**: carry the chain; Results cite the result equations by number.
- **Supplement** (`parts/supplement.md`): holds the long derivations; its equations are numbered separately and cited from the main text.
- **Audit** (`parts/audit.md`): reruns the reference check on the final files.

## Sources

The standards behind the layout and numbering rules, and where they disagree, are in `references/notation-standards.md`; read it when you need to explain a choice.
