# Reproducibility checklist

Invented example for `parts/methods.md`: the checklist of the manuscript in `examples/supplement/`.
That manuscript was written to show the use of a supplement and says little about its method.
The six rows without a place are real gaps; `methods_check.py` reports each as an error.

Kind: simulation, theory

"Where stated" names a place in the manuscript (section, equation, table, figure, supplement section),
or says n/a with the reason in the last column. A quoted heading or a `label` is checked against the source.

| # | Item | Where stated | Value or note |
|---|---|---|---|
| G1 | System: composition, geometry and dimensions | "Model", Fig. 1 | Mn3Sn (20 nm)/W bilayer; kagome plane tilted about y |
| G2 | Every parameter with value, unit and origin (measured, fitted, literature, assumed) | Table S1; "Model" | reference values and ranges; sources are placeholders in this example |
| G3 | Sequence of steps, in the order in which they were done | "Model" | relax, apply pulse, record m_z |
| G4 | Number of samples, devices or runs, and how they were chosen | "Robustness of the threshold" | 212 runs in the sweep; 64 runs per point at 300 K |
| G5 | What was excluded, and why | n/a | no run was excluded |
| G6 | Operational definition of every derived quantity that is plotted or quoted | | not stated: the main text does not say how the switching time and the threshold are read from a trace |
| G7 | What the error bars and uncertainties are, and the number of repeats behind them | Fig. S2 caption | mean of 64 runs; error function fit |
| G8 | Processing between raw output and plotted points; fit model, free parameters and range | `sec:robust` | threshold by bisection; script threshold.py in the data package |
| G9 | Software: name, version, citation, settings that differ from the defaults | | not stated: the solver and its version are named only in the README of the data package |
| G10 | Where the data and the code are | Data availability paragraph | Zenodo, doi:10.5281/zenodo.0000000 (placeholder) |
| S1 | Equation of motion or Hamiltonian, with every term | "Model"; `sec:derivation` | coupled equations of the three sublattice moments; energy of Eq. (S1) |
| S2 | Code, version or commit, and options that differ from the defaults | | not stated, see G9 |
| S3 | Discretization (cell size, lattice, basis) against the relevant length or energy scale | Table S1; Fig. S1(a) | 1 nm; threshold changes by less than 1% below 2 nm |
| S4 | Time step and integrator; total simulated time | | not stated: time step and integrator are not stated |
| S5 | Boundary conditions and system size | n/a | single domain, one macrospin per sublattice: no boundary |
| S6 | Material parameters with their sources | Table S1 | damping 0.003; thickness 20 nm |
| S7 | Initial state and how it was relaxed | | not stated: the initial state is not stated |
| S8 | Excitation: shape, amplitude, duration, rise time | "Results"; Table S1 | 6e11 A/m^2; rise time 10 ps |
| S9 | Temperature: how fluctuations enter, seeds, number of realizations | `sec:thermal` | 300 K, 64 seeds per current density |
| S10 | Convergence tests: discretization, time step, system size | `sec:robust` | cell size, damping, rise time |
| S11 | Criteria: how an event (switching, threshold, convergence) is decided | | not stated, see G6 |
| T1 | Assumptions and approximations, each with its range of validity | `sec:derivation` | single domain; torque balance at the angle of largest restoring torque |
| T2 | Conventions: signs, units, definitions | "Model" | current along x, spin polarization along y, tilt about y |
| T3 | Where each step of the derivation is given | `sec:derivation` | Eqs. (S1) to (S4) |
| T4 | Limits in which the result reduces to a known one | "Model" | threshold diverges at zero tilt |
