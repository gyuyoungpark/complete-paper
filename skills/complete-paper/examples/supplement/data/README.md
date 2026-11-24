# Data for "Field-free switching of a tilted kagome antiferromagnet"

Template of the README of a data package, filled in for the invented example of `parts/supplement.md`.
The folders named below are not part of the example; the paper, its numbers and the DOI are placeholders.

Repository: Zenodo, doi:10.5281/zenodo.0000000. Version 1.0 of 2026-11-23, deposited before submission.
Paper: A. Author and B. Author, journal and DOI to be added on publication.
Contact: corresponding author, address as in the paper.
Licence: CC BY 4.0 for data and figures, MIT for code.

## What is here

| Folder | Content | Used in the paper for |
|---|---|---|
| `fig2/` | `mz_theta00.csv` ... `mz_theta45.csv`; `make_fig2.py` | Fig. 2 |
| `fig3/` | `threshold_vs_theta.csv`; `make_fig3.py` | Fig. 3 |
| `figS1/` | `threshold_vs_cell.csv`, `threshold_vs_damping.csv`; `make_figS1.py` | Fig. S1 |
| `figS2/` | `probability_300K.csv`; `make_figS2.py` | Fig. S2 |
| `sweep/` | one folder per run (212 runs) with the input file and the time trace; `runs.csv` lists every run with its parameters and its threshold; `threshold.py` extracts the threshold from a trace | Sec. S2 and Table S1 |
| `thermal/` | 64 runs per current density at 300 K; `seeds.csv` | Sec. S3 |
| `input/` | input file of the reference run; `make_inputs.py` writes the input of every run of `sweep/` and `thermal/` | Model section |
| `style/` | `figstyle.md`, `fig_style.py`: colours, sizes and fonts of all figures | all figures |

## Formats and units

- Tables are CSV, UTF-8, one header line. A column name gives the quantity and its unit: `t_ns`, `j_A_per_m2`, `mz`, `theta_deg`.
- SI units throughout. Symbols as in the paper: `jc` is the threshold current density, `theta` the tilt angle of the kagome plane.
- Time traces are sampled every 1 ps.

## Reproduce a figure

    python3 fig3/make_fig3.py        # writes fig3/fig3.pdf from fig3/threshold_vs_theta.csv

Needs Python 3.11, numpy 2.1 and matplotlib 3.9. Each script reads only the CSV files in its own folder and the two files in `style/`.

## Repeat a run

- Solver: name, version and commit of the code; where to obtain it.
- `input/reference.in` is the run of Fig. 2 at a tilt of 30 degrees. One run takes about 20 minutes on one GPU.
- `python3 input/make_inputs.py` writes the inputs of all other runs. `python3 sweep/threshold.py sweep/run_017` prints the threshold of one run.

## What is not here

- Snapshots of the full magnetization field of every run (about 2 TB). They can be written again by setting `save_fields = 1` in the input file.

## How to cite

Cite the paper, and this record by its DOI when the data or the scripts are reused.
