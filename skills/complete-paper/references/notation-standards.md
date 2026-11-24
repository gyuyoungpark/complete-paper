# Notation, units and equations: sources and where they disagree

Read this when you need to explain a choice made in `parts/notation.md` or `parts/equations.md`. These are conventions, not findings: none of them is supported by a study of reader comprehension here. Say "this is the standard" or "this is the venue's style", not "this is proven to read better".

Checked 2026-11-19 from the sources' own pages and summaries. Standards and style guides are revised; verify against the current version, and above all against the target venue's guide.

## What the standards say

- **Italic and roman.** Symbols for quantities and variables are italic; symbols for units and for descriptive terms are roman. A subscript or superscript is italic if it stands for a quantity, a variable or a running number, and roman if it is descriptive, for example the proton mass m_p with a roman p (NIST Special Publication 811, chapter 10; NIST "Typefaces for Symbols in Scientific Manuscripts"; the same rules appear in ISO 80000 and in IUPAC's note on italic and roman fonts).
- **Vectors and tensors.** Vectors bold italic, tensors sans-serif bold italic, matrices bold italic (NIST, following ISO).
- **Mathematical constants and operators.** e, i and pi upright, and the d of derivatives and integrals upright (ISO 80000-2; IUPAC).
- **Values and units.** A space separates the numerical value from the unit symbol, also when the value is used as an adjective; the only exceptions are the degree, minute and second of plane angle (SI Brochure, 9th edition; NIST SP 811, chapter 7). The SI Brochure also puts a space before the percent sign.
- **Standard letters.** Lists of quantity symbols give t for time and d (or delta) for thickness (ISO 31-1, superseded by ISO 80000-3; the IUPAC list of quantities for space and time). This is the basis of the t-versus-d example in the part.

## What one physics publisher says (APS Journals Style Guide, February 2026)

- Latin letters used as mathematical symbols are italic; multiletter functions (exp, ln, sin, Re, Im, Tr) are roman.
- Boldface is reserved for three-vectors and some matrices. A unit vector takes a hat: k-hat = k/k.
- d, i and e appear in both the roman and the italic lists: choose one and be consistent.
- Single-letter abbreviations used as subscripts are usually italic (k_B); either font is allowed if each letter is treated consistently. Multiletter abbreviations are roman (E_lab). Multiletter abbreviations are not used as variables (E_kin, not KE).
- Abbreviations are defined at first use in the abstract and again in the text. Symbols in table headings and captions are defined in the caption. Figure axes carry quantities with units in parentheses.
- SI units are preferred. A full space between number and unit (1 cm); percent and degree signs closed up (2.4%, 90°). No multiple slashes.
- Mathematical expressions are punctuated as parts of sentences. Equations that are important, long, complex or referred to later are displayed. Numbering is (1), (2), with (1a), (1b) for related equations and (A1) in an appendix. Equations are cited as "Eq. (2)".
- The multiplication cross is for vector products and scientific notation, the centred dot for inner products; neither is used for simple products. Brackets nest as ( ), [ ], { }.

## Where the sources disagree

| Point | International standard | APS guide | What the part does |
|---|---|---|---|
| Vector typeface | bold italic | bold (listed with the roman fonts) | venue decides; one choice in text and figures |
| d, e, i | upright | either | venue decides; one choice |
| Single-letter label subscripts | roman (m_p) | usually italic (k_B), consistent per letter | roman by default; follow the venue |
| Space before % | yes | no | venue decides |
| Hat | not regulated | unit vectors | reserved for operators when the paper has any |

## Units in magnetism and other fields with two systems

- IEEE journal instructions: use either SI or CGS as primary units, with SI strongly encouraged, and avoid combining them, such as current in amperes with magnetic field in oersteds.
- The Magnetics Society of Japan recommends SI, still accepts cgs, and asks authors not to mix the two.
- CGS units remain common in the magnetism literature, so the venue's rule and the field's habit must both be checked. The rule in the part (SI by default, one system throughout, equations written in that system) follows from these.

## Defining symbols

- IEEE journal instructions: symbols in an equation are defined before the equation appears or immediately after it.
- The stricter wording in the part (the same sentence for running text; the introducing sentence or the "where" clause for equations) is a house rule built on that.

## House rules with no external source

- The base letter names one physical quantity and subscripts select the instance.
- No symbol for a quantity used only once or twice outside equations.
- One macro per symbol in the preamble.
- Number every displayed equation in the main text by default; never type a number by hand.
- Start each derivation from a named, accepted equation and say what operation produced each step.
