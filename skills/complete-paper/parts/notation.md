# Notation and units

Stage A · Reads: `brief.md`, `outline.md`, `venue.md`, existing draft, equations, figure files and plotting code · Writes: `paper-state/notation.md`

Notation works when a reader can tell from a symbol alone what kind of thing it is and which quantity it names, anywhere in the paper. This part fixes the symbols and units before the body is written and records them in `notation.md`, the table every other part reads.

Three rules carry most of the weight:
- **One quantity, one symbol; one symbol, one quantity.** No synonyms and no reuse.
- **The field's symbol, not the author's.** Use the notation the target venue's readers already know.
- **Defined where it first appears.** In the same sentence, or in the text attached to the equation.

## Modes

- **Write** (build): no table yet. Collect the quantities, choose symbols and units, write `notation.md`.
- **Revise**: apply the fixes everywhere a symbol occurs (text, equations, figures, tables, captions, supplement).
- **Audit**: check a manuscript against the rules and against `notation.md`; report violations and the smallest fix.

## Inputs

Every place a symbol can occur: the equations, figure axes and legends, tables, captions, the supplement and, for computational work, the variable names in the code. The venue's notation and unit rules come from `venue.md`.

## Steps

### Step 1. Collect

List every quantity that carries, or will carry, a symbol. Look in the equations, figure axes and legends, tables, captions, the supplement and, for computational work, the variable names in the code. For each one record what it is, its kind (scalar, vector, tensor or matrix, quantum operator, index, label) and its unit.

Leave out anything that appears only once or twice outside equations. A quantity used that rarely is clearer in words, and every extra symbol is one more thing the reader must hold.

### Step 2. Choose the symbol

Authority, highest first: the venue's rule; the symbol used in recent papers of the target venue and in the field's standard textbooks; international standards (ISO 80000, the IUPAP and IUPAC symbol lists); the authors' own earlier papers on the same system. When you cannot check the field's usage, choose the standard symbol and flag it as unverified.

**The base letter names the physical quantity; subscripts, superscripts and arguments select the instance.** If `t` is time, then `t_0`, `t_1` and `t_sw` are all times, and nothing that is not a time may be written with `t`. A thickness in the same paper therefore cannot be `t_a`; it takes the standard letter for thickness, `d`, and becomes `d_a`.

- Never two symbols for one quantity (`H_ext` in the text and `H_app` in a figure). Quantities that are related but different get different symbols and the relation is stated once (`omega = 2 pi f`).
- Never one symbol for two quantities, even in different sections or between the main text and the supplement.
- When two quantities claim the same letter: keep the letter for the one used in the main equations, give the other its next standard alternative, and record the decision in the table. Do not invent a symbol when a standard alternative exists.
- Do not distinguish two different quantities by typeface or case alone unless the field already does (`T` temperature and `t` time are fine). A vector and its magnitude are the same quantity, so bold `M` and italic `M` together are correct.
- No multi-letter variables (`KE`, `SOT`); use a letter with a descriptive subscript (`E_kin`).

Frequent collisions and a common way out (confirm against the field's usage):

| Letter | Competing meanings | A common resolution |
|---|---|---|
| t | time, thickness | `t` for time; `d` for thickness |
| T | temperature, period | `T` for temperature; write the period as `1/f` or `2 pi / omega` |
| H | magnetic field, Hamiltonian | bold `H` for the field; script or hatted `H` for the Hamiltonian |
| E | energy, electric field | `E` for energy; the field always as a bold vector or by component |
| e | elementary charge, base of natural logarithms | `e` for the charge; write exponentials as `exp( )` |
| k | wave number, Boltzmann constant | `k` for the wave number; `k_B` for the constant |
| J | exchange constant, current density | `J` for exchange; `j` for current density |
| alpha | damping constant, angle | keep `alpha` for the constant; `theta` or `phi` for angles |

### Step 3. Set the typeface

Typeface is part of the symbol: it tells the reader the kind of object. Where the venue's style differs from the international standard, the venue wins; whichever you choose, apply it in the text, the equations and the figures alike.

| Object | Set as | LaTeX | Example |
|---|---|---|---|
| Scalar quantity or variable | italic | `$M$` | M, omega |
| Vector | bold (bold italic in ISO style; bold upright in some journals) | `\mathbf{M}`, `\bm{\sigma}` for Greek | **M**, **k** |
| Magnitude and components of a vector | the same letter, italic, not bold | `$M$`, `$M_x$` | M = \|**M**\|, M_x |
| Tensor or matrix | bold, or as the venue prescribes; components italic with indices | `\mathbf{D}`, `$D_{ij}$` | D_ij |
| Quantum operator | hat (see below) | `\hat{H}`, `\hat{\mathbf{S}}` | |
| Unit symbols and prefixes | roman | `siunitx`, `\mathrm{nm}` | nm, T, A/m |
| Named functions and operators | roman | `\sin`, `\exp`, `\mathrm{Tr}` | sin, exp, Tr, Re |
| Differential d, the numbers e and i | roman in ISO style; italic in many physics journals; one choice throughout | `\mathrm{d}` or `d` | dx/dt |
| Subscript or superscript that is a variable or a running index | italic | `$x_i$`, `$J_{ij}$`, `$c_p$` | x_i |
| Subscript or superscript that is a label | roman | `$k_{\mathrm{B}}$`, `$M_{\mathrm{s}}$`, `$H_{\mathrm{ext}}$` | k_B, M_s |
| Chemical elements | roman | `Mn$_3$Sn` | Mn3Sn |

- Greek vectors need `\bm{}` (package `bm`); `\mathbf` does not embolden Greek letters.
- Labels go in subscripts. Keep superscripts for powers and for marks the field already uses; where a superscript label could be read as a power, put it in parentheses (`x^{(n)}`).
- Each mark (prime, tilde, bar, dot, star, dagger) has one meaning in the paper, listed in the table: for example dot for a time derivative, star for a complex conjugate.
- Define one macro per symbol in the preamble (`\newcommand{\Ms}{M_{\mathrm{s}}}`) and use only the macro. The notation can then be changed in one place and cannot drift.

#### Hats: quantum and classical quantities

A reader must never have to guess whether a symbol is an operator or a number.

- In a paper that contains quantum operators, the hat means "operator" and nothing else: `\hat{H}`, `\hat{S}_z`, `\hat{a}^\dagger`. The classical quantity, the eigenvalue or the expectation value has the same letter without the hat.
- In such a paper, unit vectors are written without hats, as `\mathbf{e}_x`, `\mathbf{e}_z` or `\mathbf{n}`.
- In a paper with no operators, a hat may mark unit vectors, which is the convention in some physics journals (`\hat{\mathbf{k}} = \mathbf{k}/k`).
- State which convention is in force in `notation.md`, and say in the text where the description changes from quantum to classical (for example where a spin operator is replaced by a classical vector of fixed length).

### Define at first use

- **In running text**: define the symbol in the sentence where it first appears, and say specifically what it denotes: "the saturation magnetization M_s", not "the parameter M_s".
- **In a displayed equation**: every symbol not yet defined is defined in the sentence that introduces the equation or in the "where" clause directly after it, in the order the symbols appear.
- **In the abstract**: independently of the body.
- **In captions and table headings**: a caption must be readable without the text, so name each symbol it uses ("saturation magnetization M_s") or point to the defining equation.
- Define once, with one wording. After a long gap, remind the reader by name ("the damping constant alpha") instead of redefining.
- Once a symbol is defined, use it. Do not drift between the symbol, its name and a synonym for the name.

### Units

- **System.** SI by default. If the venue requires or recommends another system, use that. Non-SI units that the field and the venue accept (eV, angstrom, Oe, emu) may be used, but then one system holds throughout: text, equations, figures, tables and supplement. Do not combine systems within one family of quantities, such as current in amperes with field in oersteds.
- **Equations follow the system.** In electromagnetism the formulas themselves differ between systems (`B = mu_0 (H + M)` against `B = H + 4 pi M`). Write every equation in the declared system and state the system once if it is not SI.
- **Conversions.** When a non-SI unit is used, give the SI equivalent at first use or in one conversion note.
- **Field conventions that hide a unit.** Say what is plotted: a magnetic field given in tesla is `mu_0 H`, and the axis label and text should say so.
- **Normalized quantities.** State what a dimensionless quantity is normalized by (`m = M / M_s`). Write "arb. units" for arbitrary units.

Formatting (SI conventions; check the venue for the starred items):

| Rule | Write | Not |
|---|---|---|
| Space between number and unit, also when used as an adjective | 5 nm, a 5 nm film, 300 K | 5nm, 300K |
| Degree sign closed up; percent sign per venue* | 30°; 2.4% or 2.4 % | 30 ° |
| Unit symbols roman, no plural, no period | 10 ns | 10 nsec, 10 ns. |
| One solidus, or negative exponents | J/(m^2 s), J m^-2 s^-1 | J/m^2/s |
| Multiplication sign in scientific notation | 1.2 × 10^11 A/m^2 | 1.2 x 10^11, 1.2e11 |
| Unit repeated in products and ranges | 5 nm × 10 nm, 10 nm to 20 nm | 5 × 10 nm |
| Digit before the decimal point | 0.3 | .3 |
| Axis labels and table headings: quantity, then unit* | t (ns), mu_0 H (T) | time [ns] with no symbol used in the text |
| Uncertainty with matching precision | 1.23 ± 0.04, or 1.23(4) | 1.2345 ± 0.04 |

In LaTeX, set every value with `siunitx` (`\qty{5}{\nano\metre}`) so that spacing and typeface are uniform.

### Step 4. Write `notation.md`

Keep it in `paper-state/`. One row per symbol, in order of first appearance:

```
| Symbol | LaTeX macro | Meaning (as worded at first use) | Kind | Unit | First defined | Note |
|---|---|---|---|---|---|---|
| t | \tm | time | scalar | s | Sec. II | |
| d_FM | \dFM | thickness of the ferromagnetic layer | scalar | nm | Sec. II | not t_FM: t is time |
| M | \vM | magnetization | vector | A/m | Eq. (1) | magnitude M |
| M_s | \Ms | saturation magnetization | scalar | A/m | Eq. (1) | label subscript, roman |
```

Below the table record: the unit system and any accepted non-SI units; the hat convention; the meaning of each mark; the choice for d, e and i; the venue's deviations from the defaults; symbols flagged as unverified.

### When rules pull in different directions

The venue's style first, then the field's established usage, then the international standard, then consistency with the authors' earlier papers. The one-to-one rule is never traded away: if the field's usual symbols collide in this paper, one of them changes.

## Checks

1. **One to one**: no quantity has two symbols; no symbol has two meanings; every base letter names one physical quantity across main text and supplement.
2. **Field standard**: each symbol is the venue's or the field's usual one, or is flagged as unverified.
3. **Typeface**: vectors bold, their magnitudes and components italic; units and named functions roman; label subscripts roman and index subscripts italic; one choice for d, e and i.
4. **Hats**: one meaning in the whole paper; operators and classical quantities distinguishable everywhere.
5. **First use**: every symbol is defined in the sentence of first appearance or in the text attached to its first equation; the abstract and each caption define their own.
6. **Consistency**: the same symbol, macro and wording in text, equations, figures, tables and supplement.
7. **Units**: one system; equations written in that system; SI equivalents given for non-SI units; formatting rules met; every axis and table heading carries a unit or "arb. units".
8. **Economy**: no symbol that is used fewer than three times outside equations.

## Report

Reply in the user's language. Keep it short:

1. `notation.md`, or the changes to it.
2. **Collisions resolved**: which letter, which quantities, what was chosen and why.
3. **Violations** (Audit): location, the rule, the smallest fix. Group repeated cases.
4. **Flags**: symbols whose field usage could not be verified, venue rules not checked, quantities with missing units.

Propose only. Rename symbols in the manuscript when the user asks, and then change every occurrence, including figure files and the supplement.

## Relation to other parts

- **Equations** (`parts/equations.md`): how equations are derived, displayed, numbered and cited. It uses only symbols from `notation.md`.
- **Figures, tables and captions**: axis labels, legends and headings use the table's symbols and units.
- **Abstract** (`parts/abstract.md`): symbols are kept to a minimum there and defined independently.
- **Audit** (`parts/audit.md`): repeats checks 1, 5, 6 and 7 on the finished manuscript.

## Sources

The standards behind these rules, and the points where they disagree with each other, are in `references/notation-standards.md`; read it when you need to explain a choice.
