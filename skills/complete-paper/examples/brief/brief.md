# Brief: Field-free switching of a tilted kagome antiferromagnet
Updated: 2026-11-23   Version: 3   Read: fig2/, fig3/, sweep/, notes of 2026-10, the manuscript in examples/supplement/

Invented example for `parts/brief.md`. The physics, the numbers and the references are placeholders.

## Claim
RESULT: Tilting the kagome plane of Mn3Sn lets a current alone reverse the octupole moment, above a threshold that falls as the inverse sine of the tilt angle.
SYSTEM: Mn3Sn (20 nm)/W bilayer, single domain, tilt angles from 5 to 45 degrees.
METHOD: Simulation of the three sublattice moments under spin-orbit torque, with an analytical balance of torque and anisotropy.
EVIDENCE: simulation; Fig. 2 (reversal at four tilt angles), Fig. 3 (threshold against the model, no adjustable parameter).
NOT SHOWN:
- Domain walls and multidomain states were not simulated.
- No experiment is reported.
- The threshold was not tested below a tilt of 5 degrees.
- Temperature enters only as a check at 300 K (supplement), not in the main results.

## Question
QUESTION: Can a symmetry broken in the crystal replace the in-plane field that deterministic switching of Mn3Sn has needed so far?
PRIOR: A: switching with an in-plane field, no tilt; B: mechanism of octupole reversal, field assumed; C: growth of tilted films, switching not examined.
DIFFERENCE: the tilt of the kagome plane is treated as the symmetry-breaking element, and its cost in current is quantified.
MATTERS: groups that grow Mn3Sn films for memory: the tilt set during growth becomes a quantity to design.

## Key numbers
| # | Quantity | Symbol | Value | Unit | Uncertainty or range | Condition | Source | Used in |
|---|---|---|---|---|---|---|---|---|
| 1 | switching time | t_sw | 0.60 | ns | 0.02 | tilt 15 deg, 6e11 A/m^2 | fig2/make_fig2.py | Results |
| 2 | switching time | t_sw | 0.22 | ns | 0.01 | tilt 45 deg, 6e11 A/m^2 | fig2/make_fig2.py | Results |
| 3 | agreement of threshold with the model | - | 4 | % | largest deviation | tilt 5 to 45 deg | fig3/make_fig3.py | Results |
| 4 | change of threshold under parameter variation | - | 5 | % | upper bound; largest found 4.6 | damping, mesh, rise time | sweep/threshold.py | Results, Sec. S2 |
| 5 | width of the transition at 300 K | - | 8 | % | of the threshold current | tilt 30 deg, 64 runs per point | thermal/ | Results, Sec. S3 |

## Evidence
| # | Statement that RESULT needs | Kind | Item | Status |
|---|---|---|---|---|
| 1 | With a tilted plane, a current alone reverses the moment | simulation | Fig. 2, traces at 15, 30 and 45 degrees | ready |
| 2 | Without tilt, no current reverses it | simulation and theory | Fig. 2, trace at 0 degrees; Eq. (1) diverges | ready |
| 3 | The threshold follows the inverse sine of the tilt angle | simulation and theory | Fig. 3; Eq. (1); derivation in Sec. S1 | ready |
| 4 | The threshold does not depend on numerical choices | simulation | Sec. S2, Table S1 | ready |

## Inventory
| Item | What it is | Path | Used |
|---|---|---|---|
| Time traces at four tilt angles | output of the reference runs | fig2/ | Fig. 2 |
| Threshold at nine tilt angles | bisection on the current density | fig3/ | Fig. 3 |
| Parameter sweep, 212 runs | damping, cell size, rise time | sweep/ | Sec. S2; data package |
| Runs at 300 K | 64 seeds per current density | thermal/ | Sec. S3 |
| Snapshots of the reversal | images of the moment | snapshots/ | not used |
| Dependence on pulse shape | a side result | pulse/ | not used; kept for referees |

## Record
Contributors: A.A.: simulations, analysis, first draft; B.A.: analytical model, supervision, revision.
Funding: [Placeholder funder], grant 0000, to B.A.
Thanks: [Placeholder] for discussions on film growth; computing time at [placeholder centre].
Data and code: Zenodo, doi:10.5281/zenodo.0000000 (placeholder); everything can be shared.
Competing interests: none.
AI tools: none.
History: no preprint; not submitted before.

## Open
- Version 3: "robust" removed from RESULT; robustness is statement 4 of the evidence table and a sentence of the Results.
