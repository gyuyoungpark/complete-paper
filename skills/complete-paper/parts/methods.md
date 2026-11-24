# Methods

Stage B · Reads: `brief.md`, `outline.md`, `venue.md`, `notation.md`, `suppmap.md`, the input files, scripts, logs and lab records · Writes: the methods section, `paper-state/repro.md`

The methods let a specialist repeat the work and judge whether its result can be trusted. They are read by few people, closely, and usually when something does not add up.

They have two jobs:

- **Repeatable.** A reader with the same means obtains the same numbers without writing to the authors.
- **Sufficient for belief.** A reader can see what could have gone wrong and how it was handled: the test of convergence, the calibration, the number of samples, the criterion.

Their difficulty is that methods are written last, from memory, by the person who knows the work best. What is left out is what the author no longer sees: the default of the code that was changed, the order of two steps, the runs that were discarded, how "switched" was decided. Two devices answer it. **Take every value from its source** (the input file, the script, the lab record), never from memory. And **fill a checklist against the manuscript** (`repro.md`): for each item a reader needs, the place where the manuscript states it.

## Modes

- **Write**: no methods yet.
- **Revise**: methods exist; fill the checklist first, then add what has no place and cut what is not method.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

## Inputs

1. `brief.md`: SYSTEM, METHOD, and the kind of EVIDENCE. The kind selects the checklist.
2. `outline.md`: the claim chain. Methods follow its order.
3. `venue.md`: where methods go, their length, whether they take subheadings, figures or tables, and any reporting form.
4. `notation.md`: the symbols of every parameter.
5. The sources of truth: input files, scripts, configuration and log files, instrument settings, lab records. Open them; do not ask the user to recall values that a file holds.
6. `suppmap.md`, if it exists: what has already been sent to the supplement and the data package.

## Steps

### Step 1. Take the place and the form from the venue

| Venue's form | Where the method goes |
|---|---|
| A letter without a methods section | One or two paragraphs in the text, at the point where the result needs them. The rest goes to the venue's middle tier (End Matter, an appendix) or to the supplement. The main text still names the system, the method and the parameters that set the result |
| A regular article in physics | A section after the introduction ("Model", "Methods", "Experimental details"), with appendices for long detail |
| Methods after the main text (Nature-family journals) | A separate section with short subheadings, of limited length, without figures or tables of its own. The main text carries one clause of method per result |
| Methods in the supplement (Science) | The main text carries a summary; the full account is the first part of the supplement |

Whatever the form, three layers hold:

- **Main text**: what a reader needs in order to read a figure. One clause: "in simulations of a 20 nm film at zero temperature".
- **Methods, appendix or middle tier**: what a specialist needs in order to believe and repeat.
- **Supplement and data package**: derivations, tests of convergence, calibration (`parts/supplement.md`); input files, scripts and raw output.

A value is stated in full once, in the place where a repeater will look for it, and referred to elsewhere.

### Step 2. Collect what a repeater needs

Make the checklist for the kinds of work in the paper:

```
python scripts/methods_check.py --template simulation experiment > paper-state/repro.md
```

The kinds are `simulation`, `experiment`, `theory` and `algorithm`; the general items are always included.

**Every paper**
- the system: composition, geometry, dimensions;
- every parameter with value, unit and origin: measured here, fitted here, taken from the literature (cited), or assumed;
- the sequence of steps;
- how many samples, devices or runs, and how they were chosen; what was excluded, and why;
- the operational definition of every derived quantity that is plotted or quoted: how a threshold, a switching time or an efficiency is read from the raw output;
- what the error bars are (standard deviation, standard error, range, fit error) and the number of repeats behind them;
- the processing between raw output and plotted points; for fits, the model, the free parameters, the weights and the range;
- software with name, version, citation and every setting that differs from the default;
- where the data and the code are.

**Simulation** (micromagnetic, atomistic, first-principles, device)
- the equation of motion or the Hamiltonian, with every term;
- the code, its version or commit, options that differ from the defaults;
- the discretization (cell size, lattice, basis, k-mesh, cutoff) set against the length or energy it must resolve, such as the exchange length or the domain-wall width;
- time step and integrator; total simulated time;
- boundary conditions and system size;
- material parameters, each with its source;
- the initial state and how it was relaxed;
- the excitation: shape, amplitude, duration, rise time;
- temperature: how fluctuations enter, the seeds, the number of realizations;
- tests of convergence in discretization, time step and system size;
- the criterion by which an event is decided.

**Device or transport experiment**
- the sample: layers in order with thicknesses, the substrate;
- growth or synthesis with its conditions; annealing;
- patterning and device dimensions;
- characterization of structure and properties, with instruments;
- the measurement set-up: instruments by maker and model; the geometry of current, field and detection;
- conditions: temperature, field, frequency, amplitude, pulse width;
- calibration of field, temperature, power and current density;
- the protocol: initialization, sequence, averaging;
- the number of devices and samples, and the variation between them;
- corrections: background, offsets, heating, current shunting.

**Theory**
- assumptions and approximations, each with its range of validity;
- conventions for signs, units and definitions;
- where each step of the derivation is given;
- the limits in which the result reduces to a known one.

**Algorithm, hardware or machine learning**
- problem instances or data sets: source, version, size, splits;
- baselines, and how they were tuned;
- the parameters of the method, and how they were chosen;
- random seeds and the number of runs;
- metrics: their definition and how they were computed;
- hardware and run time.

An item that does not apply stays in the checklist with "n/a" and the reason. A reason that cannot be written is a sign that the item applies.

### Step 3. Write

- **Order.** Subsections in the order in which the claim chain needs them; inside a subsection, the order in which things were done. Headings name what was done: "Thermal field", not "Details".
- **Purpose first.** Each subsection opens with what the step is for, then what we did: "To model the switching, we integrate ..." (ground rule 13 in `SKILL.md`).
- **Parameters in a table** when there are more than about six: symbol, meaning, value, unit, source. The symbols are those of `notation.md`; the table follows `parts/tables.md`.
- **Tense and voice.** Past for what was done ("we relaxed the film for 1 ns"); present for what holds (the model, the equations, definitions). What we did takes "we" and an active verb, as in the rest of the paper (ground rule 11). Where the venue avoids the first person, follow the venue throughout.
- **Published methods.** Cite the work, then state what was the same and what differed here. "As described previously" alone is not a method when one parameter changed.
- **Definitions that the Results use.** State once how each plotted quantity is obtained from the raw output. The Results then use the name.
- **Values, not adjectives.** "Standard", "typical", "appropriate", "sufficiently fine", "several" stand where a number or a procedure should be. Replace each one, or say what makes the choice standard and cite it.
- **Approximate values** carry their uncertainty or the reason they are approximate.
- **No results, no interpretation, no history.** What was tried and abandoned is not method, unless a reader would otherwise try it.
- **Software.** Name, version, citation, non-default settings. For the authors' own code: where it is and which commit produced the figures. `parts/bibliography.md` treats these as `source` and `method` citations.
- **Statements that belong to the method** go where the venue puts them: ethics approval where the collection of data is described; the use of an AI tool in the analysis where the venue places it (`parts/submit.md` checks that it is in place).

### Step 4. Fill `paper-state/repro.md`

For every row, write where the manuscript states the item: a section, an equation, a table, a figure, a section of the supplement. Write a section as its quoted heading, or a place as its `label` in backquotes; the script then verifies that it exists.

```
| # | Item | Where stated | Value or note |
|---|---|---|---|
| S3 | Discretization against the relevant length or energy scale | Table I; "Convergence" | 1 nm against an exchange length of 4.2 nm |
| S9 | Temperature: how fluctuations enter, seeds, number of realizations | n/a | zero temperature throughout |
| S11 | Criteria: how an event is decided | | not stated |
```

A row without a place is a gap in the manuscript. Close it in the text, not in the checklist. The filled checklist is also what the cover letter and a reporting form are written from, and it can go into the data package.

### Step 5. Check

```
python scripts/methods_check.py main.tex supplement.tex --repro paper-state/repro.md
```

- **Errors**: a row without a place; a quoted heading or a label that the manuscript does not contain.
- **Warnings**: "n/a" without a reason; items of the declared kinds removed from the checklist; "data not shown" and "as described previously" anywhere in the text.
- **Notes**, in method sections: words that stand where a value should be; approximate values; software named without a version or a citation. `--all` scans every section.

The scan flags places to review. It does not know which detail decides this result; the checklist, filled honestly, does.

Then the repeat test: give the methods, the supplement and the data package to a reader who did not do the work, or to a fresh agent, and ask for the list of what they would have to guess in order to reproduce Fig. 2. Each guess is a missing sentence.

### When rules pull in different directions

Completeness for the repeater first, then the venue's form and length, then brevity. When the length limit bites, move detail to the middle tier, the supplement or the data package; do not delete it.

## Checks

1. **Checklist**: `repro.md` exists for the kinds of work in the paper; every row has a place or "n/a" with a reason.
2. **Sources**: every value was taken from an input file, a script or a record, and agrees with it.
3. **Parameters**: each has value, unit and origin; symbols match `notation.md`.
4. **Definitions**: every derived quantity that the Results plot or quote is defined operationally.
5. **Statistics**: numbers of samples or runs, the meaning of every error bar, exclusions.
6. **Software**: name, version, citation, non-default settings; the authors' code and its version.
7. **Convergence and calibration**: the tests exist, are stated, and are where the supplement part put them.
8. **Published methods**: cited, with what differed.
9. **Values, not adjectives**: no "standard", "typical" or "appropriate" in place of a value.
10. **Only method**: no results, interpretation or history.
11. **Place and form**: as the venue requires; a letter's main text still names system, method and the parameters that set the result.
12. **Order and tense**: the order of the claim chain; past for what was done, present for what holds.

## Report

Reply in the user's language; write the methods in the manuscript's language. Keep it short:

1. **Methods**, with their word count against the venue's limit.
2. **Checklist**: the rows without a place, each with the sentence that would close it or the question for the user.
3. **Values that could not be traced** to a file or record.
4. **Flags**: a setting the user should confirm; a test of convergence that does not exist; material proposed for the supplement or the data package.

In Audit mode, replace item 1 with the table of the twelve checks and the smallest fix for each failure.

Propose only. Never fill a gap with a plausible value: a parameter that cannot be found is a question for the user.

## Example (invented; the physics and the numbers are placeholders)

Before:

> Simulations were performed using a standard micromagnetic package with typical parameters for Mn3Sn. The cell size was chosen sufficiently small, and the threshold current was extracted from the switching curves as described previously.

Fails: no code or version; "standard", "typical", "sufficiently small" in place of values; no parameter has a source; the threshold has no definition; "as described previously" hides the procedure; the passive hides who did the work (ground rule 11).

After:

> To follow the reversal, we integrated the coupled Landau-Lifshitz-Gilbert equations of the three sublattice moments with [code, version] [12], using a fourth-order Runge-Kutta scheme and a time step of 1 fs. We divided the film into cells of 1 nm, a quarter of the exchange length. Halving the cell changes the threshold by less than 1% (Sec. S2). Table I lists the material parameters and their sources. Each run started from the relaxed state with the octupole moment along +z. A run counts as switched when m_z stays below -0.9 for 1 ns after the pulse. The threshold is the lowest current density, found by bisection to within 1%, at which the run switches.

`examples/methods/repro.md` is the checklist of the short manuscript in `examples/supplement/`. The script reports six rows without a place, among them the definition of the threshold and the version of the code: the gaps that the paragraph above closes.

## Relation to other parts

- **Results** (`parts/results.md`) use the definitions made here and carry one clause of method per result.
- **Supplement** (`parts/supplement.md`) takes derivations, tests of convergence and calibration; the data package takes input files, scripts and raw output.
- **Notation and tables** supply the symbols and the form of the parameter table.
- **Bibliography** (`parts/bibliography.md`): software, data and parameter sources are cited there.
- **Submit** (`parts/submit.md`) checks that the data and code availability statement and any disclosure of AI tools are in place. The authors word them from `intake.md`.
- **Audit** (`parts/audit.md`) reruns `methods_check.py` and compares the parameter values in text, tables and supplement.

## What this part cannot do

It cannot know which detail matters most for a given result; the lists of Step 2 are a floor for four kinds of work and not a reporting standard of any journal. Where the venue has its own reporting form, that form governs.

## Sources

The journal rules and sources behind these choices are in `references/body-evidence.md`; read it when you need to explain a choice.
