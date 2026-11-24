#!/usr/bin/env python3
"""One figure style for one paper: final size, fonts, colours, panel labels.

Copy this file next to the paper's plotting scripts, then start each script with

    import fig_style as fs
    fs.use(base=8, small=7)                       # point sizes at final size, from venue.md
    style = fs.load("figstyle.md")                # the paper's encoding table (optional)
    fig, axs = fs.figure(178, 60, ncols=3)        # width and height in millimetres
    axs[1].plot(t, mz, **style["simulation"])     # colour, line and marker from the table
    fs.panel_labels(fig, axs, fmt="({})")         # "(a)", "(b)", ... at one offset from every panel
    fs.save(fig, "fig2.pdf")

Figures are built at their final size, so a point on the figure is a point on the page:
include them in the manuscript at 100%. Take widths, font sizes and the form of panel
labels from venue.md. The numbers in VENUES are a convenience, checked on the date in
references/figures-evidence.md; the venue's own page is the authority.

`python3 fig_style.py` prints the palette and the venue presets. Needs matplotlib.
"""
import re
import string

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import to_hex

MM = 1 / 25.4                    # millimetres to inches

# Colour-blind-safe categorical palette (Okabe and Ito; Wong 2011). Yellow is weak on white: use it last.
OKABE_ITO = {"blue": "#0072B2", "vermillion": "#D55E00", "green": "#009E73", "orange": "#E69F00",
             "sky": "#56B4E9", "purple": "#CC79A7", "yellow": "#F0E442", "black": "#000000"}
CYCLE = [OKABE_ITO[k] for k in ("blue", "vermillion", "green", "orange", "sky", "purple")]

# Final widths in mm by number of columns, smallest and largest text in pt (None: not stated),
# and the form of panel labels. Provenance of every number is in references/figures-evidence.md.
VENUES = {
    # APS: 3 3/8 in. for one column; lettering at least 2 mm high, which is about 8-pt type
    "aps": {"widths": {1: 86, 2: 178}, "text": (8, None), "label": "({})", "label_weight": "normal"},
    "nature": {"widths": {1: 89, 2: 183}, "text": (5, 7), "label": "{}", "label_weight": "bold", "label_size": 8},
}
SANS = ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"]


def _first_installed(names):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return next((n for n in names if n in have), names[-1])


def use(base=8, small=None, font="sans", ticks="in", line=1.0, frame=0.6):
    """Set matplotlib's defaults for the whole script. Sizes are points at final size.

    base: axis labels and panel labels; small: tick labels, legends and notes (default base - 1).
    font: "sans" (Arial or Helvetica when installed) or "serif" (STIX, close to Times).
    ticks: "in" (ticks on all four sides, pointing inward) or "out" (bottom and left only).
    """
    small = base - 1 if small is None else small
    if font == "serif":
        family, mathset = "STIXGeneral", {"mathtext.fontset": "stix"}
    else:
        family = _first_installed(SANS)
        mathset = ({"mathtext.fontset": "dejavusans"} if family == "DejaVu Sans" else
                   {"mathtext.fontset": "custom", "mathtext.rm": family, "mathtext.it": family + ":italic",
                    "mathtext.bf": family + ":bold", "mathtext.sf": family, "mathtext.cal": family,
                    "mathtext.tt": "monospace", "mathtext.fallback": "stixsans"})
    mpl.rcParams.update({
        "font.family": [family], "font.size": base,
        "axes.labelsize": base, "axes.titlesize": base, "figure.titlesize": base,
        "xtick.labelsize": small, "ytick.labelsize": small, "legend.fontsize": small,
        "legend.title_fontsize": small, "axes.unicode_minus": True, **mathset,
        "lines.linewidth": line, "lines.markersize": 3.5, "lines.markeredgewidth": 0.6,
        "axes.linewidth": frame, "patch.linewidth": frame, "hatch.linewidth": 0.4,
        "xtick.major.width": frame, "ytick.major.width": frame,
        "xtick.minor.width": 0.75 * frame, "ytick.minor.width": 0.75 * frame,
        "xtick.major.size": 3, "ytick.major.size": 3, "xtick.minor.size": 1.6, "ytick.minor.size": 1.6,
        "xtick.direction": ticks, "ytick.direction": ticks,
        "xtick.top": ticks == "in", "ytick.right": ticks == "in",
        "axes.spines.top": ticks == "in", "axes.spines.right": ticks == "in",
        "axes.labelpad": 2, "xtick.major.pad": 2.5, "ytick.major.pad": 2.5,
        "legend.frameon": False, "legend.handlelength": 1.6, "legend.handletextpad": 0.5,
        "legend.borderaxespad": 0.6, "legend.labelspacing": 0.3, "legend.columnspacing": 1.0,
        "axes.prop_cycle": mpl.cycler(color=CYCLE), "image.cmap": "viridis",
        "errorbar.capsize": 0, "axes.formatter.use_mathtext": True, "axes.formatter.limits": (-3, 4),
        "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": None,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.facecolor": "white", "savefig.facecolor": "white", "savefig.transparent": False,
    })
    return family


def figure(width_mm, height_mm, nrows=1, ncols=1, **kw):
    """A figure of exactly this final size, with panels on an aligned grid."""
    kw.setdefault("layout", "constrained")
    fig, axs = plt.subplots(nrows, ncols, figsize=(width_mm * MM, height_mm * MM), **kw)
    engine = fig.get_layout_engine()
    if engine is not None and hasattr(engine, "set"):
        try:
            engine.set(w_pad=2 / 72, h_pad=2 / 72, wspace=0.03, hspace=0.03)
        except TypeError:
            pass
    return fig, axs


def panel_labels(fig, axes, fmt="({})", weight="normal", size=None, dx=None, dy=5, start="a"):
    """Label panels a, b, c ... at the same offset from the top-left corner of every panel.

    Because the offset is the same for all panels, labels in a row share a baseline and labels
    in a column share a left edge whenever the panel frames themselves are aligned.
    fmt: "({})" for (a), "{}" for a; dx, dy: offset in points from the frame's top-left corner
    (dx defaults to the left edge of the widest tick-label and axis-label block).
    """
    axes = [a for a in (axes.flat if hasattr(axes, "flat") else list(axes))]
    size = size or mpl.rcParams["axes.labelsize"]
    if dx is None:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        dx = -max((a.get_window_extent(r).x0 - a.get_tightbbox(r).x0) for a in axes) * 72 / fig.dpi
    letters = string.ascii_lowercase[string.ascii_lowercase.index(start.lower()):]
    if start.isupper():
        letters = letters.upper()
    out = []
    for ax, letter in zip(axes, letters):
        out.append(ax.annotate(fmt.format(letter), xy=(0, 1), xycoords="axes fraction", xytext=(dx, dy),
                               textcoords="offset points", ha="left", va="bottom", fontsize=size,
                               fontweight=weight, annotation_clip=False))
    return out


def direct_label(ax, line, text=None, x=None, dx=3, dy=0, **kw):
    """Write a label next to a curve instead of in a legend: at its last point, or at data position x."""
    import numpy as np
    xs, ys = np.asarray(line.get_xdata(), float), np.asarray(line.get_ydata(), float)
    i = len(xs) - 1 if x is None else int(np.nanargmin(np.abs(xs - x)))
    kw.setdefault("fontsize", mpl.rcParams["legend.fontsize"])
    kw.setdefault("color", "black")
    kw.setdefault("va", "center")
    kw.setdefault("ha", "left" if dx >= 0 else "right")
    return ax.annotate(text or line.get_label(), xy=(xs[i], ys[i]), xytext=(dx, dy),
                       textcoords="offset points", annotation_clip=False, **kw)


class Encoding(dict):
    """The paper's encoding table: meaning -> keyword arguments for plot()."""

    def colour_of(self, meaning):
        return self[meaning]["color"]


def load(path="figstyle.md"):
    """Read the table 'Meaning | Label on figure | Colour | Line | Marker' from figstyle.md."""
    rows, header = [], None
    for raw in open(path, encoding="utf-8"):
        if not raw.lstrip().startswith("|"):
            header = None if not raw.strip() else header
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if header is None:
            if any(c.startswith(("colour", "color")) for c in low) and "meaning" in low:
                header = low
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(dict(zip(header, cells)))
    enc = Encoding()
    for r in rows:
        colour = next((v for k, v in r.items() if k.startswith(("colour", "color"))), "")
        m = re.search(r"#[0-9A-Fa-f]{6}", colour)
        if not m:
            continue
        label = next((v for k, v in r.items() if k.startswith("label")), "") or r["meaning"]
        kw = {"color": to_hex(m.group(0)), "label": label.strip("`")}
        line = r.get("line", "").strip("` ")
        marker = r.get("marker", "").strip("` ")
        kw["linestyle"] = line if line and line.lower() != "none" else "none"
        if marker and marker.lower() != "none":
            kw["marker"] = marker
        enc[r["meaning"]] = kw
    return enc


def save(fig, name, **kw):
    """Save at the designed size (no cropping), and say what was written."""
    fig.savefig(name, **kw)
    w, h = fig.get_size_inches()
    print(f"saved {name}: {w / MM:.1f} mm x {h / MM:.1f} mm")


if __name__ == "__main__":
    print("categorical palette:", ", ".join(f"{k} {v}" for k, v in OKABE_ITO.items()))
    for name, v in VENUES.items():
        lo, hi = v["text"]
        print(f"{name}: widths {v['widths']} mm, text {lo} pt" + (f" to {hi} pt" if hi else " or larger")
              + f", labels {v['label'].format('a')}")
    print("sans font found:", _first_installed(SANS))
