# Supplement map

Invented example for `parts/supplement.md`. The tables Budget, Items and Callouts were written by
`python3 scripts/supp_check.py main.tex --supp supplement.tex --ledger suppmap.md` on 2026-11-23;
the columns "Supports statement" and "Decision", and the tables Moved out and Data package, were filled in by hand.

Statements of the claim chain (from `outline.md`):
1. With a tilted kagome plane, a current alone reverses the octupole moment (Fig. 2).
2. The threshold current follows j0 / sin(theta) with no adjustable parameter (Eq. (1), Fig. 3).

## Budget

| | Main text | Supplement | Ratio |
|---|---|---|---|
| Words | 613 | 366 | 0.60 |
| Figures and tables | 3 | 3 | 1.00 |
| Numbered equations | 1 | 4 | 4.00 |
| Pages | 2 | 3 | 1.50 |

Callouts: 3 sentences in 613 words (4.9 per 1000); most in one paragraph: 1. Budget: 3 (one per section).
Pages are not compared: the main text is set in two columns and the supplement in one.

## Items

| Item | Caption or title | Cited in main text | Cited in supplement | Reached | Supports statement | Decision (keep, merge, main, data, cut) |
|---|---|---|---|---|---|---|
| Sec. S1 | Derivation of the threshold current | yes | contents | yes | 2: derives Eq. (1) | keep |
| Sec. S2 | Robustness of the threshold | yes | contents | yes | 2: "moves by less than 5%" in Results | keep |
| Sec. S3 | Effect of temperature | via its items | contents | yes | 2: "broaden ... do not shift" in Results | keep |
| Table S1 | Parameters of the simulations: reference value, range of variation, a… | no | S2 | yes | evidence of Sec. S2 | keep |
| Fig. S1 | Threshold current density at …, relative to the reference run, (a) ag… | no | S2 | yes | evidence of Sec. S2 | keep; merged from two figures |
| Fig. S2 | Switching probability at … and … against current density in units of… | yes | S3 | yes | evidence of Sec. S3 | keep |

## Callouts

| # | Where | Part | Points to | Sentence |
|---|---|---|---|---|
| 1 | main.tex:59 | Model | Sec. S1 | Reversal starts when this component exceeds the anisotropy torque, which gives the threshold where … is the a… |
| 2 | main.tex:82 | Results | Sec. S2 | The threshold moves by less than … when the damping, the mesh and the rise time of the pulse are varied over… |
| 3 | main.tex:94 | Results | Fig. S2 | At … thermal fluctuations broaden the transition from no reversal to reversal over about … of the threshold c… |
| 4 | main.tex:106 | back matter | the supplement as a whole | The input files, the raw output of all 212 simulation runs and the scripts that produce every figure of the p… |

Callout 4 is the Data availability statement; it is listed and not counted.

## Moved out

Candidates that an earlier draft carried in the supplement, and where each went.

| Candidate | Went to | Reason |
|---|---|---|
| Time traces of the moment at every tilt angle and current (4 figures) | data package, `sweep/` | the same plot repeated; no sentence discusses a single trace |
| Threshold against each of five further parameters (5 figures) | data package, `sweep/`; the largest change of each is a row of Table S1 | the reader needs the number, and a checker needs the runs |
| Table of all 212 runs | data package, `sweep/runs.csv` | a table to look values up in |
| Listing of the input file | data package, `input/` | usable as it is |
| Snapshots of the moment during reversal | cut | no statement uses them; Fig. 2 shows the reversal |
| Dependence of the switching time on pulse shape | cut; kept for the reply to referees | a result outside the claim chain |
| Convergence against cell size and dependence on damping (2 figures) | merged into Fig. S1 | two panels of one point: the threshold is robust |

## Data package

| Path in the package | Content | Replaces or backs up |
|---|---|---|
| `README.md` | what each folder holds, formats, units, software and versions, licence | |
| `fig2/`, `fig3/`, `figS1/`, `figS2/` | the plotted numbers of each figure as CSV, and the script that draws it | backs up every figure of the paper and the supplement |
| `sweep/` | output of all 212 runs; `runs.csv` with one row per run; `threshold.py` extracts the threshold | replaces nine supplementary figures and one table |
| `thermal/` | 64 runs per current density at 300 K, with the seeds | backs up Fig. S2 |
| `input/` | input files of the reference run and of each sweep | replaces a listing |

## Open items

None. The page ratio of 1.50 is a note, not a finding: the two files use different layouts.
