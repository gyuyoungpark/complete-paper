#!/usr/bin/env python3
"""Planted-fault cases for scripts/fig_lint.py.

Each case builds a small figure with one fault, or with none, and states which findings must
appear and which must not. Run after any change to fig_lint.py, fig_style.py or schematic3d.py.

    python3 evals/figures/lint_cases.py            # every case
    python3 evals/figures/lint_cases.py legend     # the cases whose name contains "legend"

Exit status is 1 if any case fails.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
from matplotlib.colors import TwoSlopeNorm, to_hex  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import fig_lint as fl                    # noqa: E402
import fig_style as fs                   # noqa: E402
import schematic3d as s3                 # noqa: E402

X = np.linspace(0, 1, 60)
BLUE, RED, GREEN = "#0072B2", "#D55E00", "#009E73"
CASES = []


def case(name, expect=(), absent=(), **opts):
    def register(build):
        CASES.append((name, build, expect, absent, opts))
        return build
    return register


def fresh(nrows=1, ncols=1, w=3.4, h=2.3, **kw):
    matplotlib.rcdefaults()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.dpi": 100})
    kw.setdefault("layout", "constrained")
    return plt.subplots(nrows, ncols, figsize=(w * ncols, h * nrows), squeeze=False, **kw)


def name_axes(ax, x=r"$t$ (ns)", y=r"$m_z$"):
    ax.set_xlabel(x)
    ax.set_ylabel(y)


def one(**kw):
    fig, axs = fresh(**kw)
    name_axes(axs[0, 0])
    return fig, axs[0, 0]


# ----- legends, notes and insets against data, frames and ticks -----

@case("legend on a curve", expect=["the legend overlaps a curve"])
def _():
    fig, ax = one()
    ax.plot(X, X, color=BLUE, label="A")
    ax.plot(X, 1 - X, color=RED, ls="--", label="B")
    ax.legend(loc="center")
    return fig


@case("legend in free space", absent=["overlaps", "crosses", "tick marks"])
def _():
    fig, ax = one()
    ax.plot(X, X**3, color=BLUE, label="A")
    ax.plot(X, 0.5 * X**3, color=RED, ls="--", label="B")
    ax.legend(loc="upper left", frameon=False)
    return fig


@case("legend on inward tick marks", expect=["sits on the tick marks"])
def _():
    fig, ax = one()
    ax.tick_params(direction="in", top=True, right=True)
    ax.plot(X, X**3, color=BLUE, label="A")
    ax.plot(X, 0.5 * X**3, color=RED, ls="--", label="B")
    ax.legend(loc="upper left", borderaxespad=0, frameon=False)
    return fig


@case("legend across the axis frame", expect=["the legend crosses the axis frame"])
def _():
    fig, ax = one()
    ax.plot(X, X**3, color=BLUE, label="A")
    ax.plot(X, 0.5 * X**3, color=RED, ls="--", label="B")
    ax.legend(loc="upper left", bbox_to_anchor=(-0.12, 1.12))
    return fig


@case("note on a bar", expect=["overlaps a bar"])
def _():
    fig, ax = one()
    ax.bar([1, 2, 3], [3, 5, 4], color="0.4")
    ax.text(2, 2.5, "peak", ha="center", color="white")
    return fig


@case("note on a shaded band", expect=["lies on a filled area"], absent=["overlaps a"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.axvspan(0.6, 0.9, color="0.85", lw=0)
    ax.text(0.75, 0.2, "II", ha="center")
    return fig


@case("note on data points", expect=["overlaps data points"])
def _():
    fig, ax = one()
    ax.scatter(X[::6], X[::6] ** 2, color="black", s=12)
    ax.text(X[30], X[30] ** 2, "onset")
    return fig


@case("inset over the data", expect=["the inset, with its labels, covers data"])
def _():
    fig, ax = one()
    ax.plot(X, np.sin(6 * X), color="black")
    inset = ax.inset_axes([0.3, 0.3, 0.4, 0.4])
    inset.plot(X, X, color="black")
    name_axes(inset)
    return fig


@case("inset in free space", absent=["covers data"])
def _():
    fig, ax = one()
    ax.plot(X, X**6, color="black")
    inset = ax.inset_axes([0.2, 0.5, 0.36, 0.42])
    inset.plot(X, X, color="black")
    name_axes(inset)
    return fig


@case("text cut off at the edge", expect=["cut off at the edge"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    fig.text(0.95, 0.5, "outside the page")
    return fig


@case("tick labels run into each other", expect=["tick labels overlap on the x axis"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_xticks(np.linspace(0, 1, 26))
    return fig


@case("axis label runs into the next panel", expect=["runs into"])
def _():
    fig, axs = fresh(1, 2, w=1.7, layout=None)
    for ax in axs[0]:
        ax.plot(X, X, color="black")
        name_axes(ax)
    axs[0, 1].set_ylabel("a rather long label\nof the y axis", labelpad=16)
    return fig


@case("note on an outline of a schematic", expect=["crosses a line or an outline"])
def _():
    fig, axs = fresh()
    scene = s3.Scene()
    scene.box((0, 0, 0), (10, 6, 1), "#D9D9D9").note("substrate", at=(0, 0, 1))
    scene.draw(axs[0, 0])
    return fig


@case("note on a face of a schematic", absent=["crosses a line"])
def _():
    fig, axs = fresh()
    scene = s3.Scene()
    scene.box((0, 0, 0), (10, 6, 1), "#D9D9D9").note("substrate", at=(5, 3, 1))
    scene.draw(axs[0, 0])
    return fig


# ----- colour -----

def two_panels(first, second, **kw):
    fig, axs = fresh(1, 2, w=2.6, **kw)
    for ax, draw in zip(axs[0], (first, second)):
        draw(ax)
        name_axes(ax)
    return fig


@case("one colour, two things, two panels", expect=["one colour, 2 meanings"])
def _():
    return two_panels(lambda ax: ax.plot(X, X, color=BLUE, label="sample A"),
                      lambda ax: ax.plot(X, X**2, color=BLUE, label="model"))


@case("points and their fit in one colour, one panel", absent=["one colour"])
def _():
    fig, ax = one()
    ax.plot(X[::6], X[::6], "o", color=BLUE, label="data")
    ax.plot(X, X, "-", color=BLUE, label="fit")
    return fig


@case("points and their fit in one colour, two panels", expect=["one colour, 2 meanings"])
def _():
    return two_panels(lambda ax: ax.plot(X[::6], X[::6], "o", color=BLUE, label="data"),
                      lambda ax: ax.plot(X, X, "-", color=BLUE, label="fit"))


@case("two meanings share a colour by the style table", absent=["one colour"], style={"data": BLUE, "fit": BLUE})
def _():
    return two_panels(lambda ax: ax.plot(X[::6], X[::6], "o", color=BLUE, label="data"),
                      lambda ax: ax.plot(X, X, "-", color=BLUE, label="fit"))


@case("one thing in two colours", expect=["one meaning, 2 colours"])
def _():
    return two_panels(lambda ax: ax.plot(X, X, color=BLUE, label="sample A"),
                      lambda ax: ax.plot(X, X**2, color=RED, label="sample A"))


@case("black for two things", absent=["one colour"])
def _():
    return two_panels(lambda ax: ax.plot(X, X, color="black", label="data"),
                      lambda ax: ax.plot(X, X**2, color="black", label="model"))


@case("single curves of two quantities in one colour", expect=["one colour, 2 meanings"])
def _():
    fig = two_panels(lambda ax: ax.plot(X, X, color=BLUE), lambda ax: ax.plot(X, X**2, color=BLUE))
    fig.axes[1].set_ylabel(r"$R$ ($\Omega$)")
    return fig


@case("single curves of two quantities in black", absent=["one colour"])
def _():
    fig = two_panels(lambda ax: ax.plot(X, X, color="black"), lambda ax: ax.plot(X, X**2, color="black"))
    fig.axes[1].set_ylabel(r"$R$ ($\Omega$)")
    return fig


@case("colour differs from the style table", expect=["in the style table, drawn"],
      style={"A": {"colour": BLUE, "line": "-", "marker": "none"}})
def _():
    fig, ax = one()
    ax.plot(X, X, color=RED, label="A")
    return fig


@case("line style differs from the style table", expect=["line '-' in the style table"],
      style={"A": {"colour": BLUE, "line": "-", "marker": "none"}})
def _():
    fig, ax = one()
    ax.plot(X, X, color=BLUE, ls="--", label="A")
    return fig


@case("a colour of the style table used for something else", expect=["is the colour of 'A' in the style table"],
      style={"A": {"colour": BLUE}})
def _():
    fig, ax = one()
    ax.plot(X, X, color=BLUE, label="B")
    return fig


@case("red and green told apart by colour alone", expect=["red-green colour-vision deficiency"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="#2ca02c", label="A")
    ax.plot(X, X**2, color="#d62728", label="B")
    return fig


@case("red and green with a second cue", absent=["red-green"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="#2ca02c", label="A")
    ax.plot(X, X**2, color="#d62728", ls="--", label="B")
    return fig


@case("the colour-blind-safe palette", absent=["red-green", "too pale"])
def _():
    fig, ax = one()
    for k, colour in enumerate(fs.CYCLE):
        ax.plot(X, X ** (1 + k / 2), color=colour, label=f"s{k}")
    return fig


@case("eight curves on one ramp", expect=["differ by less than 10 in colour"])
def _():
    fig, ax = one()
    for k in range(8):
        ax.plot(X, X ** (1 + k / 3), color=plt.get_cmap("Blues")(0.3 + 0.08 * k), label=f"{k}")
    return fig


@case("a series too pale to follow", expect=["too pale to follow"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="#F0E442", label="A")
    return fig


@case("lettering too pale to read", expect=["hard to read"])
def _():
    fig, ax = one()
    ax.plot(X, X**3, color="black")
    ax.text(0.1, 0.8, "regime I", color="#F0E442", transform=ax.transAxes)
    return fig


def mapped(ax, cmap, lo, hi, label, **kw):
    mesh = ax.pcolormesh(np.outer(np.linspace(lo, hi, 20), np.ones(20)), cmap=cmap, **kw)
    ax.figure.colorbar(mesh, ax=ax, label=label)
    name_axes(ax, r"$x$ (nm)", r"$y$ (nm)")


@case("rainbow colour map", expect=["rainbow maps"])
def _():
    fig, axs = fresh()
    mapped(axs[0, 0], "jet", 0, 1, r"$T$ (K)")
    return fig


@case("diverging map off centre", expect=["the neutral colour is not at zero"])
def _():
    fig, axs = fresh()
    mapped(axs[0, 0], "RdBu_r", -0.2, 1, r"$m_z$")
    return fig


@case("diverging map centred by its norm", absent=["neutral colour"])
def _():
    fig, axs = fresh()
    mapped(axs[0, 0], "RdBu_r", -0.2, 1, r"$m_z$", norm=TwoSlopeNorm(0, -0.2, 1))
    return fig


@case("signed data on a sequential map", expect=["signed data on the sequential map"])
def _():
    fig, axs = fresh()
    mapped(axs[0, 0], "viridis", -1, 1, r"$m_z$")
    return fig


@case("one colour map for two quantities", expect=["one colour map"])
def _():
    fig, axs = fresh(1, 2)
    mapped(axs[0, 0], "viridis", 0, 1, r"$T$ (K)")
    mapped(axs[0, 1], "viridis", 0, 5, r"$n$ (nm$^{-2}$)")
    return fig


@case("two panels share one colour bar", absent=["without a colour bar", "one colour map"])
def _():
    fig, axs = fresh(1, 2)
    for ax in axs[0]:
        mesh = ax.pcolormesh(np.outer(X[:20], np.ones(20)), cmap="viridis", vmin=0, vmax=1)
        name_axes(ax, r"$x$ (nm)", r"$y$ (nm)")
    fig.colorbar(mesh, ax=list(axs[0]), label=r"$T$ (K)")
    return fig


@case("map without a colour bar", expect=["without a colour bar"])
def _():
    fig, axs = fresh()
    axs[0, 0].pcolormesh(np.outer(X[:20], np.ones(20)), cmap="viridis")
    name_axes(axs[0, 0], r"$x$ (nm)", r"$y$ (nm)")
    return fig


# ----- panel labels and panel frames -----

def row_of_three():
    fig, axs = fresh(1, 3, w=2.2)
    for ax in axs[0]:
        ax.plot(X, X, color="black")
        name_axes(ax)
    return fig, axs[0]


@case("panel labels off the line", expect=["are not on one horizontal line", "different offsets"])
def _():
    fig, _ = row_of_three()
    fig.text(0.01, 0.95, "(a)")
    fig.text(0.34, 0.92, "(b)")
    fig.text(0.67, 0.95, "(c)")
    return fig


@case("panel labels at one offset", absent=["panel labels", "panel label"])
def _():
    fig, axs = row_of_three()
    fs.panel_labels(fig, axs)
    return fig


@case("panel labels inside the frames", absent=["panel labels", "overlaps"])
def _():
    fig, axs = row_of_three()
    for ax, letter in zip(axs, "abc"):
        ax.text(0.05, 0.93, f"({letter})", transform=ax.transAxes, va="top")
    return fig


@case("panel labels as left titles", absent=["panel title", "panel labels"])
def _():
    fig, axs = row_of_three()
    for ax, letter in zip(axs, "abc"):
        ax.set_title(f"({letter})", loc="left")
    return fig


@case("panel labels out of reading order", expect=["not in reading order"])
def _():
    fig, axs = row_of_three()
    fs.panel_labels(fig, [axs[0], axs[2], axs[1]])
    return fig


@case("panel labels in two forms", expect=["written in different forms"])
def _():
    fig, axs = row_of_three()
    fs.panel_labels(fig, axs[:2])
    axs[2].annotate("c", xy=(0, 1), xycoords="axes fraction", xytext=(-25, 5), textcoords="offset points")
    return fig


@case("a panel that spans two rows", absent=["not on one", "reading order", "different offsets"])
def _():
    matplotlib.rcdefaults()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.dpi": 100})
    fig = plt.figure(figsize=(5, 3.2), layout="constrained")
    grid = fig.add_gridspec(2, 2)
    axs = [fig.add_subplot(grid[:, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, 1])]
    for ax in axs:
        ax.plot(X, X, color="black")
        name_axes(ax)
    fs.panel_labels(fig, axs)
    return fig


@case("panels that nearly line up", expect=["panels that nearly line up should line up exactly"])
def _():
    matplotlib.rcdefaults()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.dpi": 100})
    fig = plt.figure(figsize=(5, 2))
    for box in ([0.1, 0.22, 0.35, 0.70], [0.6, 0.22, 0.35, 0.715]):
        ax = fig.add_axes(box)
        ax.plot(X, X, color="black")
        name_axes(ax)
    return fig


# ----- text, units, typeface, ticks -----

@case("text under the smallest size", expect=["text under 6 pt"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_xlabel(r"$t$ (ns)", fontsize=4)
    return fig


@case("lettering under 2 mm", expect=["lettering under 2 mm high"], min_height_mm=2)
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.tick_params(labelsize=6.5)
    return fig


@case("8-pt sans-serif lettering reaches 2 mm", absent=["lettering under"], min_height_mm=2)
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    return fig


@case("text over the largest size", expect=["text over 7 pt"], max_font=7)
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    return fig


@case("symbol set upright", expect=["the symbol is upright"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_xlabel("t (ns)")
    return fig


@case("symbol and unit set correctly", absent=["upright", "inside math mode", "spelled out", "more than one way"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_xlabel(r"$\mu_0 H$ (T)")
    ax.set_ylabel(r"$j_{\mathrm{c}}$ ($10^{11}$ A/m$^2$)")
    return fig


@case("unit inside math mode", expect=["the unit sits inside math mode"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_ylabel(r"$j_c (A/m^2)$")
    return fig


@case("a function of a variable is not a unit", absent=["inside math mode"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_ylabel(r"$P(k)$")
    return fig


@case("Greek letter spelled out", expect=["is spelled out"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_xlabel("theta (deg)")
    return fig


@case("units written two ways", expect=["units are written in more than one way"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_ylabel(r"$V$ [mV]")
    return fig


@case("axis multiplier left floating", expect=["floating multiplier"])
def _():
    fig, ax = one()
    ax.plot(X, 3e11 * X, color="black")
    return fig


@case("numbers without an axis label", expect=["the x axis has numbers but no label"])
def _():
    fig, axs = fresh()
    axs[0, 0].plot(X, X, color="black")
    axs[0, 0].set_ylabel(r"$m_z$")
    return fig


@case("categories need no axis label", absent=["has numbers but no label"])
def _():
    fig, axs = fresh()
    axs[0, 0].bar(["Pt", "W", "Ta"], [1, 3, 2], color="0.4")
    axs[0, 0].set_ylabel(r"$\theta_{\mathrm{SH}}$ (%)")
    return fig


@case("shared axes labelled on the outside only", absent=["has numbers but no label"])
def _():
    fig, axs = fresh(2, 2, w=1.8, h=1.5, sharex=True, sharey=True)
    for ax in axs.flat:
        ax.plot(X, X, color="black")
    for ax in axs[-1]:
        ax.set_xlabel(r"$t$ (ns)")
    for ax in axs[:, 0]:
        ax.set_ylabel(r"$m_z$")
    return fig


@case("panel title and figure title", expect=["panel title 'Result'", "figure title 'Overview'"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.set_title("Result")
    fig.suptitle("Overview")
    return fig


@case("ticks in and out in one figure", expect=["ticks point"])
def _():
    fig = two_panels(lambda ax: ax.plot(X, X, color="black"), lambda ax: ax.plot(X, X, color="black"))
    fig.axes[0].tick_params(direction="in")
    return fig


# ----- marks, chart types, size and saving -----

@case("hairline", expect=["thinner than 0.5 pt"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black", lw=0.3)
    return fig


@case("thin line allowed by the venue", absent=["thinner than"], min_line=0.25)
def _():
    fig, ax = one()
    ax.plot(X, X, color="black", lw=0.3)
    return fig


@case("bars cut at the base", expect=["does not start at zero"])
def _():
    fig, axs = fresh()
    axs[0, 0].bar(["a", "b", "c"], [10.2, 10.6, 10.9], color="0.4")
    axs[0, 0].set_ylim(10, 11)
    return fig


@case("pie chart", expect=["a pie chart"])
def _():
    fig, axs = fresh()
    axs[0, 0].pie([3, 2, 1])
    return fig


@case("two y axes", expect=["two y axes on one panel"])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    ax.twinx().plot(X, 5 * X**2, color=RED)
    return fig


@case("legend on a polar plot", absent=["crosses the axis frame"])
def _():
    matplotlib.rcdefaults()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.dpi": 100})
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw={"projection": "polar"}, layout="constrained")
    ax.plot(np.linspace(0, 2 * np.pi, 100), 1 + 0.3 * np.cos(3 * np.linspace(0, 2 * np.pi, 100)), color=BLUE, label="A")
    ax.plot(np.linspace(0, 2 * np.pi, 100), 0.6 + 0 * X[:1].repeat(100), color=RED, ls="--", label="B")
    ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))
    return fig


@case("width that is not a column width", expect=["the figure is 100.0 mm wide"], widths_mm=[86, 178])
def _():
    fig, ax = one(w=100 / 25.4)
    ax.plot(X, X, color="black")
    return fig


@case("figure taller than the page", expect=["mm tall"], max_height_mm=50)
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    return fig


@case("cropped, low-resolution raster", expect=["bbox_inches='tight'", "saved at 100 dpi"],
      saved=[{"name": "fig.png", "dpi": 100, "tight": True}])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    return fig


@case("Type 3 fonts in a PDF", expect=["Type 3 fonts"], saved=[{"name": "fig.pdf", "dpi": None, "tight": False}])
def _():
    fig, ax = one()
    ax.plot(X, X, color="black")
    return fig


@case("a figure built with the skill's style is clean", absent=["ERROR", "overlaps", "panel labels", "one colour"],
      widths_mm=[86, 178], min_height_mm=2, levels="EW")
def _():
    fs.use(base=9, small=8)
    fig, axs = fs.figure(178, 60, ncols=3)
    axs[0].plot(X[::5], X[::5] ** 2, "o", color="black", markerfacecolor="white", label="measured")
    axs[0].plot(X, X**2, color="black", label="fit")
    axs[0].legend(loc="upper left")
    axs[1].plot(X, np.exp(-3 * X), color=BLUE, label="sample A")
    axs[1].plot(X, np.exp(-6 * X), color=RED, ls="--", label="sample B")
    axs[1].legend(loc="upper right")
    mesh = axs[2].pcolormesh(np.outer(np.linspace(-1, 1, 30), np.ones(30)), cmap="RdBu_r", vmin=-1, vmax=1, rasterized=True)
    fig.colorbar(mesh, ax=axs[2], label=r"$m_z$", ticks=[-1, 0, 1])
    for ax, (x, y) in zip(axs, ((r"$\mu_0 H$ (T)", r"$R_{xy}$ ($\Omega$)"), (r"$t$ (ns)", r"$m_x$"), (r"$x$ (nm)", r"$y$ (nm)"))):
        ax.set(xlabel=x, ylabel=y)
    fs.panel_labels(fig, axs)
    return fig


# ----- the command line -----

def command_line():
    lint, out = str(ROOT / "scripts" / "fig_lint.py"), []

    def run(*args):
        done = subprocess.run([sys.executable, lint, *args], capture_output=True, text=True, encoding="utf-8")
        return done.returncode, done.stdout + done.stderr

    examples = ROOT / "examples" / "figures"
    code, text = run(str(examples / "after.py"), "--width-mm", "86", "178", "--min-height-mm", "2",
                     "--style", str(examples / "figstyle.md"))
    out.append(("example after.py passes", code == 0 and "ERRORS" not in text and "WARNINGS" not in text, text))
    code, text = run(str(examples / "before.py"), "--width-mm", "86", "178", "--style", str(examples / "figstyle.md"))
    out.append(("example before.py fails", code == 1 and "one colour, 2 meanings" in text and "the legend overlaps" in text, text))
    with tempfile.TemporaryDirectory() as folder:
        broken, unsaved = Path(folder) / "broken.py", Path(folder) / "unsaved.py"
        broken.write_text("raise RuntimeError('no data file')\n")
        unsaved.write_text("import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([0, 1], [0, 1])\nplt.show()\n")
        code, text = run(str(broken))
        out.append(("a script that fails is an error", code == 1 and "did not run" in text, text))
        code, text = run(str(unsaved))
        out.append(("a figure that is never saved is still checked", "never saved" in text and "no label" in text, text))
    return out


def schematic_checks():
    """The projection keeps what parts/figures.md promises, and every kind of solid draws."""
    out = []
    scene = s3.Scene(azim=-58, elev=24)
    scene.centre = np.zeros(3)
    x, y, z = scene.project(np.eye(3))
    out.append(("schematic: x runs right and slightly down, y right and up, z straight up",
                bool(x[0] > 0 > x[1] and y[0] > 0 and y[1] > 0 and abs(z[0]) < 1e-12 and z[1] > 0), f"{x} {y} {z}"))
    a = scene.project([[0, 0, 0], [3, 1, 0]])
    b = scene.project([[5, 2, 4], [8, 3, 4]])
    da, db = a[1] - a[0], b[1] - b[0]
    out.append(("schematic: parallel edges stay parallel and keep their length",
                bool(abs(da[0] * db[1] - da[1] * db[0]) < 1e-12 and abs(np.hypot(*da) - np.hypot(*db)) < 1e-12), f"{da} {db}"))
    outline = s3.hall_bar(8, 1, arms=(2.5, 5.5), arm_length=1.5, arm_width=0.6)
    out.append(("schematic: a Hall bar with two pairs of arms has 20 corners", len(outline) == 4 + 8 * 2, str(len(outline))))
    fig, axs = fresh()
    scene = s3.Scene()
    scene.box((0, 0, 0), (10, 6, 1), "#D9D9D9").prism(outline, 1.0, 0.3, RED, label="film")
    scene.cylinder((9, 5, 1), 0.4, 0.6, "#D4B55A").stack((0.5, 4.5, 1), (1, 1), [(0.2, BLUE), (0.2, GREEN, "cap")])
    scene.arrow((1, 0.5, 1.4), (4, 0.5, 1.4), label=r"$I$").triad((-1, -3, 0), 1.5).draw(axs[0, 0])
    parts = {(q.get_label(), getattr(q, "base_colour", None)) for q in axs[0, 0].patches if not q.get_label().startswith("_")}
    out.append(("schematic: parts keep the colour they stand for, unshaded", parts == {("film", RED), ("cap", GREEN)}, str(parts)))
    plt.close(fig)
    fig, axs = fresh()
    s3.Scene(azim=-90, elev=0).stack((0, 0, 0), (3, 1), [(1, BLUE, "A"), (1, RED, "B")]).draw(axs[0, 0])
    tones = {to_hex(q.get_facecolor()) for q in axs[0, 0].patches}
    out.append(("schematic: a flat side view is drawn without shading", tones == {BLUE.lower(), RED.lower()}, str(tones)))
    plt.close(fig)
    return out


def main():
    wanted = sys.argv[1:]
    failed = total = 0
    for name, build, expect, absent, opts in CASES:
        if wanted and not any(w in name for w in wanted):
            continue
        opts = dict(opts)
        levels = opts.pop("levels", "EWN")
        fig = build()
        result = fl.check(fig, **opts)
        plt.close(fig)
        lines = [f"{'ERROR' if lv == 'E' else 'WARNING' if lv == 'W' else 'NOTE'} {place}: {msg}"
                 for lv, place, msg in result["findings"] if lv in levels]
        text = "\n".join(lines)
        missing = [e for e in expect if e not in text]
        present = [a for a in absent if a in text]
        total += 1
        if missing or present:
            failed += 1
            print(f"FAIL  {name}")
            for e in missing:
                print(f"        expected, not found: {e}")
            for a in present:
                print(f"        found, not expected: {a}")
            for line in lines:
                print(f"        | {line}")
        else:
            print(f"ok    {name}")
    if not wanted:
        for name, passed, text in schematic_checks() + command_line():
            total += 1
            if passed:
                print(f"ok    {name}")
            else:
                failed += 1
                print(f"FAIL  {name}\n" + "\n".join("        | " + line for line in text.splitlines()[-25:]))
    print(f"\n{total - failed} of {total} cases pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
