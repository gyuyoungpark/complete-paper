# Figures

Stage B · Reads: `outline.md`, `venue.md`, `notation.md`, `figstyle.md` if it exists, the other figures of the paper, the data files and any plotting script · Writes: `figstyle.md`, one plotting script per figure, the figure files, and the list of what each caption must define

A figure is the evidence for one statement of the paper, arranged so that the eye makes the comparison. Readers often go to the figures before the text, so each figure, with its caption, has to carry its statement alone.

It has two jobs. **Show the message at a glance**: the comparison behind the statement is read off by position along a common scale, the judgement the eye makes best. **Stay decodable and quiet**: every mark can be identified, nothing covers anything else, and nothing is there that the comparison does not need.

The rule that covers both: **every mark either is data or tells the reader how to read the data. Explanation goes to the caption; everything else comes off.**

Three constants hold for the whole paper: **one figure, one message; one colour, one meaning; one size, the final size.**

Who decides what. `parts/outline.md` decides which figures exist, what each must establish, their order, and what goes to the supplement. This part draws them: the kind of plot, the schematic, colour, lettering, ticks, legends, layout, the order of panels, the file. `parts/captions.md` writes what is shown.

## Modes

- **Write**: data and a specification exist; write the plotting script and draw the figure.
- **Revise**: a figure or its script exists; fix what fails the checks and leave the data untouched.
- **Audit**: report pass/fail per check and the smallest fix; change nothing.

Order of work: the paper's style table first; then each figure as a plain draft at final size; then the checks. Polish only after the Results text exists, because panels move while the text is written.

The scripts assume matplotlib. For figures made with other tools the rules and checks are the same, and the check is done by eye on the exported image at final size.

## Inputs

Read before drawing:

1. `outline.md`: the figure's specification: role, panels in reading order, takeaway in one sentence, evidence files. If there is none, agree on the takeaway with the user before drawing.
2. `venue.md`: column widths, text sizes or lettering height, line widths, the form of panel labels, file formats, colour policy, the habits of recent figures in the venue (font, tick direction), and the policies on AI-generated images and on disclosure.
3. `notation.md`: symbols, units, typeface.
4. `figstyle.md` if it exists, and the other figures of the paper.
5. The data files and any plotting script. Plot from the data, never from numbers read off an old image. If the data cannot be read, say so and deliver a specification and a script marked as untested.

## Steps

### Step 1. Set the paper's style once

Before the first figure, write `figstyle.md` in `paper-state/`. Every figure of the paper, supplement included, is drawn from it.

```
# Figure style: <working title>
Venue: <journal>. Widths: <one column> / <two columns> mm. Text: <sizes> pt at final size. Lines: at least <width> pt.
Font: <family>. Ticks: <in, on four sides | out>. Panel labels: <"(a)" roman | "a" bold>, above the top-left corner.
Schematics: parallel projection, azimuth <deg>, elevation <deg>, light from the upper left.

## Encoding
| Meaning | Label on figure | Colour | Line | Marker |
|---|---|---|---|---|
| tilt 15 deg | $15^\circ$ | #2C7BB6 | - | none |
| simulation | simulation | #000000 | none | o |

## Colour maps
| Quantity | Map | Limits |
|---|---|---|
| m_z | RdBu_r, centred on 0 | -1 to 1 |
```

Rules for the table:

- **List first, colour second.** From `outline.md`, list everything that colour will tell apart anywhere in the paper: samples, conditions, materials, methods, signs. Then assign.
- **One meaning, one colour, in both directions.** Across the paper as far as it can be done. Inside one figure without exception: two panels never use one colour for two things, and one thing never appears in two colours.
- **Black and grey mean nothing.** A single curve, a fit, a guide line and a frame are black or grey, everywhere. Colour is spent only where it tells things apart.
- **The kind of colour follows the kind of variable.** Unordered categories: distinct hues from a colour-blind-safe set (`fig_style.OKABE_ITO`), six at most, yellow last. An ordered parameter (a family of curves in temperature, angle or thickness): one hue from light to dark. A sign or two opposed states: two opposed hues, such as blue and vermillion.
- **Keep the associations readers already have**: hot red and cold blue; the same colour for a material in the schematic and in its data; measured points and their fit in one colour, told apart as points and line.
- **Never colour alone.** Give each series a second cue (line style, marker shape or a label on the curve), and choose colours that differ in lightness, so that the figure survives greyscale printing and red-green colour-vision deficiency.
- **Colour maps.** Magnitude: a perceptually uniform sequential map (viridis, cividis, batlow). Signed quantity: a diverging map with its neutral colour at the meaningful zero. Angle or phase: a cyclic map. No rainbow maps (jet and its relatives). One map per quantity, with the same limits in every panel that shows the quantity; every map has a colour bar labelled with quantity and unit.

### Step 2. From message to plot

1. Write the takeaway as one sentence. If the figure has two, split it.
2. Name the comparison: what against what (model against data, with against without, value against control parameter).
3. Put the compared values **on one scale, next to each other**: in one panel when they share a unit, in adjacent panels with identical axes when they do not fit. Positions along a common scale are compared more accurately than lengths, angles, areas or colours.
4. Choose axes on which the claim is a simple shape: a straight line on logarithmic axes for a power law, a collapse onto one curve in scaled variables, a difference or a ratio when the gap itself is the message.
5. Give the strongest contrast to the data that carry the message; context is grey and thin.
6. Delete what the comparison does not need: curves that repeat a point already made, grid lines, boxes around legends, backgrounds, shadows, depth effects.

| The message is | Draw | Avoid |
|---|---|---|
| y depends on x | points with error bars for measured values, a line for dense or continuous data | bars over a continuous variable; smoothing that hides the points |
| A differs from B | both in one panel on shared axes; the difference or ratio when the gap is the message | separate panels with different scales; two y axes |
| The model agrees with the data | data as points, model as a line, in one panel; a residual panel when agreement is the claim | two separate plots to be compared by memory |
| A scaling law | logarithmic axes with a reference slope; scaled variables that collapse the curves | linear axes on which curvature hides the law |
| Dependence on two parameters, a phase diagram | a map with a uniform colour map, the boundary as a line, and line cuts where values must be read | a 3D surface; a rainbow map |
| A few categories compared | points or bars from zero on one axis, sorted by value | pie charts; bars cut at the base |
| A distribution | histogram or cumulative curve; every point when there are few | a bar for the mean of a small sample |
| A threshold or a transition | the curve across it, with the critical value marked | panels that show only one side |
| A spatial pattern | an image with equal aspect, a scale bar and a colour bar | stretched images; unlabelled colours |
| A pattern changing in time | small panels with the same scale and the same colour limits | panels scaled one by one |
| Geometry, setup, mechanism | a schematic (Step 8) | a photograph of the setup, unless the photograph is evidence |
| A handful of numbers | a table or a sentence | a figure |

Show the data as they are: individual points when there are few; error bars whose meaning the caption states; bars that start at zero; a cut axis marked as cut; identical limits on panels that are compared.

### Step 3. Build at final size

Take the width from `venue.md` and build the figure at exactly that size, so that a point on the figure is a point on the page. Use one column unless the detail needs more.

Copy `scripts/fig_style.py` beside the paper's plotting scripts, and `scripts/schematic3d.py` as well when the paper has schematics (Step 8). The plotting scripts import them.

```python
import fig_style as fs
fs.use(base=9, small=8)                       # points at final size
enc = fs.load("figstyle.md")
fig, axs = fs.figure(178, 56, ncols=3)        # millimetres
axs[1].plot(t, mz, **enc["tilt 15 deg"])
fs.panel_labels(fig, axs, fmt="({})")
fs.save(fig, "fig2.pdf")
```

Two families of rules, as examples (checked November 2026; `venue.md` decides):

| | Physical Review journals | Nature journals |
|---|---|---|
| Width | 8.5 cm (3 3/8 in.) for one column; one and a half or two columns for detailed figures | 89 mm; 183 mm; 120 to 136 mm for one and a half columns |
| Lettering | smallest capitals and numerals at least 2 mm high: 8 pt in Helvetica or Arial, nearer 9 pt in Times | 5 to 7 pt sans-serif; panel labels 8 pt bold |
| Lines | at least 0.18 mm (0.5 pt) | 0.25 to 1 pt |
| Panel labels | (a), (b) | a, b: lowercase, bold, upright |

- One font family for the paper; sans-serif (Helvetica or Arial) unless the venue's figures use another. Symbols come from a math font that matches it.
- Two text sizes, three at most: one for axis labels and panel labels, one for tick labels, legends and notes.
- Data lines about 1 pt; frames and ticks about 0.6 pt; nothing below the venue's minimum. Markers at least 1 mm across; open or white-filled markers where points crowd.
- Include the file at 100% in the manuscript. A figure scaled in LaTeX no longer has the sizes it was designed with.

### Step 4. Lettering

On the figure goes what the eye needs while it is on the data: the quantity and unit of each axis, the tick numbers, the panel labels, a short identification of each series, the label of a colour bar, a scale bar. Definitions, conditions, methods and explanations go to the caption. Check every piece of text: would the data be misread without it, at the moment of looking? If not, it moves to the caption.

- **Axis labels**: symbol and unit, in the venue's form, for example `$\mu_0 H$ (T)`. A label names what is plotted, not a file column or a code variable.
- **The same symbols as the text**, typeset as in `notation.md`: variables italic (`$t$`), units upright and outside math mode (`(ns)`), label subscripts upright (`$j_{\mathrm{c}}$`), index subscripts italic (`$m_z$`), vectors bold (`$\mathbf{m}$`), chemical formulas upright (`Mn$_3$Sn`). No Greek letter spelled out, no `^` or `_` left unrendered.
- **Powers of ten** belong in the unit or the label (`mT`, `($10^{11}$ A/m$^2$)`), never in a multiplier floating at the end of an axis.
- **No title above a panel and none above the figure.** The caption's title does that work. The one case for a word on a panel is a label that tells otherwise identical panels apart ("experiment" and "simulation"; "10 K" and "300 K"); set it inside the frame in the small size.
- **Notes** are a few words at most, horizontal, black. Avoid lettering over images and shaded areas where there is free space.

### Step 5. Legends and labels on the data

- **Label the curves themselves** when there are up to about five and they separate: `fs.direct_label(ax, line, r"$30^\circ$")`. The reader then never looks away from the data.
- **Otherwise a legend**: inside the frame in an area free of data, entries in the order in which the curves appear from top to bottom, no box, short entries. Explanations of the entries go to the caption; the identification itself stays on the figure, because sending the reader to the caption for every curve slows reading.
- **One legend per figure** when panels share an encoding. More than about six entries means the panel carries too much: split it, or show an ordered parameter with a colour bar.
- **Nothing overlaps.** A legend, a label, a note or an inset touches no curve, marker, error bar, filled band, axis frame, tick mark, tick label, other text or neighbouring panel, and keeps a margin of about a tick length. When there is no free area: change the limits to open one, enlarge the panel, move the legend outside the frame, or label the curves directly. A white box or a lowered opacity behind a legend that sits on data is not a fix.

### Step 6. Axes and ticks

- Three to six labelled ticks per axis, at round values (steps of 1, 2 or 5 times a power of ten). The same number of decimals along an axis; a zero before the decimal point; integers where possible.
- Limits a little beyond the data, so that no marker is cut by the frame or sits on it.
- Panels that are compared share limits. Shared axes print their numbers once, on the outer panels.
- One tick direction for the paper, taken from recent figures of the venue. Minor ticks on logarithmic axes.
- Two y axes on one panel only when the two quantities must be read against the same x values and the caption can say which curve belongs to which axis; two stacked panels are usually clearer.

### Step 7. Layout and order

- **One grid.** The frames of the panels (the axes boxes, not the text around them) share edges in rows and columns, with equal gaps; panels of the same kind have the same size. Panels that nearly line up read as a mistake: align them exactly or make them clearly different.
- **Panel labels**: the venue's form, one size and one weight, at the same offset from the top-left corner of every panel (`fs.panel_labels`). Labels in a row then stand on one line and labels in a column on one vertical.
- **Reading order is the order of the argument**: left to right, then down. The panel that orients (schematic, definition of angles and axes) comes first; the main evidence gets the most space; controls and extensions follow. The text cites the panels in that order.
- **Figure order** through the paper is the order of the claim chain in `outline.md`, and figures are numbered in the order of first citation.
- **Insets** only when the inset belongs to the same message and the panel has a free area; otherwise the content gets a panel of its own.
- Keep the white space between panels small and even.

### Step 8. Schematics

A schematic shows what the reader must know in order to read the data panels: the geometry, the stack of materials, the directions of current and field, the coordinate axes of the equations, the definition of an angle. It shows one idea and leaves out everything that neither the text nor the caption mentions.

- **Flat first.** A cross-section or a top view is the clearest drawing of a layer stack (`schematic3d.Scene(azim=-90, elev=0)` draws the side view). Draw in three dimensions only when the geometry is three-dimensional: directions that do not lie in one plane, a device whose shape matters.
- **One view for the paper.** Draw every device seen obliquely from above in the same parallel projection (`schematic3d.Scene(azim=-58, elev=24)`; elevation between about 20 and 35 degrees). Edges that are parallel in the device stay parallel on the page and vertical edges stay vertical, so lengths and angles can be compared. Turn the device so that its long axis runs across the page and no face that matters is hidden. Converging perspective only when depth itself is the message, and then weak (`perspective=`).
- **Depth from three cues only**: nearer parts cover farther ones; flat tones from one light (top lightest, one side at the base colour, the other darker); thin dark outlines of one width. No gradients, shadows, gloss, glow or textures.
- **True order, free proportions.** Keep the stacking order and the lateral arrangement true. Thicken layers that would vanish at scale, and have the caption say "not to scale".
- **Vectors and axes.** A coordinate triad in a free corner, with the axis names of the equations. One arrow style per kind of vector (current, field, magnetization), each labelled with its symbol from `notation.md`.
- **Labels** in the font and size of the data panels, horizontal, black, on a face or in free space with a thin leader line, never across an outline. Materials by chemical formula.
- **Colours from `figstyle.md`.** The material under study has the same colour here as its data; substrates and contacts are muted; four or five colours at most.
- **Drawn by code or in a vector program, never by an image-generation model.** A generated picture cannot be checked against the device and does not share the figure's fonts and colours, and some publishers do not accept generated images at all. `schematic3d.py` draws boxes, layer stacks, cylinders and flat parts with any outline (a Hall bar is one `prism`), with arrows, notes and guide lines, inside the same figure as the data panels. `examples/figures/schematics.py` draws a Hall bar, a pillar and the cross-section of its stack this way (rendered: `examples/figures/schematics.png`). For crystal structures, spin textures and curved surfaces use the dedicated tool of the field, with the same view, fonts and colours, and place the result in the grid.

### Step 9. Main text or supplement, panel by panel

`outline.md` allocates whole figures; apply the same test to each panel.

- **Deletion test**: remove the panel. If a statement of the claim chain loses its support, the panel stays in the main text. If nothing is lost, it goes to the supplement, to the data package or out; `parts/supplement.md` decides which.
- **Citation test**: a main-text panel is cited by a sentence that uses it. A panel no sentence needs is not a main-text panel.
- To the supplement: one further example of a point already shown, robustness checks, calibration. To the data package: the raw data behind a processed panel, full parameter sweeps, the same plot for every sample.
- Never to the supplement alone: the evidence for a statement of the chain, and the control that rules out the leading alternative.
- A main figure with more than about six panels is carrying two messages or supplementary material; split or trim it.
- Report every move to the outline; do not change the allocation silently.

### Step 10. Check: lint, then look

1. **Lint.** Pass all figure scripts of the paper in one call, so that colours are compared across figures:
   `python scripts/fig_lint.py fig1.py fig2.py --width-mm 86 178 --min-height-mm 2 --style figstyle.md` (or `--min-font 5 --max-font 7` where the venue states point sizes). It measures the rendered figure: overlaps, text cut at the edge, colours with two meanings, meanings with two colours, disagreement with `figstyle.md`, pairs that merge for colour-vision deficiency or in greyscale, alignment of panels and panel labels, text sizes, symbols set upright, floating multipliers, colour maps, final size, file format. Fix every error. Fix each warning or record why it stands. Read the notes.
2. **Look.** Open the rendered image at final size. What is seen first? It should be the takeaway. Then read every piece of text once. Never judge a figure from its code alone.
3. **Numbers.** Compare two or three plotted values with the data file, including unit conversions, and confirm that the limits clip nothing.

Repeat until the lint is clean and the look confirms the message.

### Step 11. Export

- Plots and schematics as vector files (PDF, or EPS where required) with the text kept as text: TrueType fonts embedded (`pdf.fonttype: 42`), nothing converted to outlines.
- Dense maps rasterized inside the vector file (`rasterized=True`) at 600 dpi. Photographs and micrographs as TIFF or PNG at 300 dpi or more. No JPEG for line art.
- No cropping at save time: `bbox_inches="tight"` changes the size that was designed.
- One script per figure, kept with its data, so that the figure can be rebuilt when a referee asks for a change.

### When rules pull in different directions

The data first: nothing is moved, smoothed, clipped or left out to make a figure cleaner. Then the venue's requirements. Then legibility: size, and nothing overlapping. Then one meaning per colour. Then economy of ink and text. Then alignment and looks. When the paper's colour for a meaning cannot be read in one figure, change it in `figstyle.md` and in every figure, not in that figure alone.

## Checks

1. **Message**: one takeaway; it is what the eye meets first; the comparison lies along a common scale.
2. **Form**: the kind of plot fits the message; no 3D plot, pie chart or second y axis without need; bars from zero; cut axes marked; data not smoothed or dropped.
3. **Economy**: every element survives the question "what is lost without it?"; no panel or figure title unless it tells panels apart; no decoration.
4. **Lettering**: on the figure only what is needed at the moment of looking; the rest is listed for the caption.
5. **Decodable**: every curve, marker, colour and map is identified on the figure or in the list for the caption.
6. **No overlap**: legends, labels, notes and insets clear of data, frames, tick marks, text and neighbouring panels; nothing cut at the edge.
7. **Colour meaning**: in the figure no colour has two meanings and no meaning two colours; the figure agrees with `figstyle.md`.
8. **Colour access**: colour-blind-safe hues, a second cue, distinct in greyscale; no rainbow map; diverging maps centred; colour bars labelled; one map and one range per quantity.
9. **Typeface**: symbols and units as in `notation.md` and the text; one font; sizes within the venue's range at final size.
10. **Axes**: quantity and unit on every axis; three to six round ticks; no floating multiplier; shared limits where panels are compared.
11. **Panel labels**: venue's form; same size, weight and offset; on one line in rows and one vertical in columns; in reading order.
12. **Alignment**: frames on one grid; equal gaps; same-kind panels the same size.
13. **Order**: panels in the order of the argument and of citation; figures in the order of the claim chain.
14. **Schematic**: one view for the paper; parallel edges parallel; one light; symbols and axes of the text; "not to scale" noted for the caption; not made by an image-generation model.
15. **Main or supplement**: every main-text panel is necessary and cited; nothing essential is in the supplement only.
16. **Size and file**: final width from `venue.md`; lines and markers above the minimum; vector file with embedded text; nothing cropped.
17. **Integrity**: the plotted values are the data; any processing of an image is applied to the whole image and stated; nothing is hidden by limits, masks or colour ranges.

## Report

Reply in the user's language; text on figures is in the manuscript's language. Keep it short:

1. **The figure**: files, final size, and one sentence on what the reader sees first.
2. **Lint**: errors (none, or the reason the figure is not finished) and each warning left standing with its reason.
3. **Decisions**: the kind of plot and why; what was removed; what moved to the caption.
4. **For the caption**: every element the caption must define (colours, line styles, markers, symbols, error bars, colour scales, "not to scale").
5. **For the outline**: panels proposed for the supplement or for removal; statements whose evidence turned out to be missing.
6. **Style table**: rows added to or changed in `figstyle.md`.
7. **Flags**: a font that was substituted, venue rules not verified, data that could not be read, a figure that could not be rendered or viewed, AI assistance that the venue wants disclosed.

Propose only. Write new files beside the user's figures and scripts; replace theirs when the user asks.

## Example (invented)

`examples/figures/before.py` draws a first draft (rendered: `examples/figures/before.png`): a 305 mm figure meant for a 178 mm page, a title on each panel and one on the figure, a rainbow map, a legend lying on the curves, the default colour cycle (blue is "theta = 0 deg" in one panel and "model" in the next), panel labels off the line, units as "[A/m^2]" in one panel and "(ns)" in another, and "1e11" floating over an axis. The lint lists each of these.

`examples/figures/after.py` draws the figure again from `examples/figures/figstyle.md` (rendered: `examples/figures/after.png`). Takeaway: a tilted kagome plane lets the current alone reverse the order, at a threshold that falls with the tilt angle. (a) A schematic defines the tilt angle and the current direction that (b) and (c) need. (b) m_z against time for four tilt angles on one blue ramp, each curve labelled on the curve. (c) Threshold current against tilt angle: simulation as open circles, model as a line, both black because nothing is told apart by colour there. The map of the first draft repeated (c) and is proposed for the supplement. Built at 178 mm with 9 pt and 8 pt text; the lint is clean.

For the caption: the blue ramp and its angles; circles and line in (c); the semi-transparent plane and the dashed normal in (a); "not to scale".

## Relation to other parts

- **Outline** (`parts/outline.md`) decides which figures exist, their roles, their order and the supplement. Drawing often shows that a panel is not needed or that evidence is missing; report it there.
- **Captions** (`parts/captions.md`) writes what is shown, from the list in the report. Text removed from a figure is not lost; it arrives in the caption.
- **Notation** (`parts/notation.md`) supplies symbols, units and typeface; a symbol on a figure that differs from the text is an error of this part.
- **Venue** (`parts/venue.md`) supplies sizes, formats and policies; this part's numbers are defaults.
- **Tables** (`parts/tables.md`) take over when the content is a handful of numbers.
- **Supplement** (`parts/supplement.md`) receives panels that fail the deletion test, drawn from the same `figstyle.md` and linted in the same run as the main figures; panels that are only data go to the data package.
- **Submit** (`parts/submit.md`) checks the disclosure of AI assistance that the venue asks for and the data and code availability that figure scripts make possible.
- **Audit** (`parts/audit.md`) runs the lint over all figures together and repeats checks 7, 9, 11 and 13 on the finished manuscript.

## What this part cannot do

A clean figure does not make weak evidence strong. The lint measures geometry and colour; it cannot tell whether the plot is the right one, whether a schematic is true to the device, or whether the figure is needed. `schematic3d.py` draws simple solids, not illustrations. Fonts depend on what is installed: where Helvetica or Arial is missing, a metric-compatible font is used and reported.

## Sources

The journal rules, the perception studies, the points on which sources differ, and the rules that are this skill's own are in `references/figures-evidence.md`; read it when you need to explain a choice.
