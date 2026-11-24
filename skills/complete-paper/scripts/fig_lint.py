#!/usr/bin/env python3
"""Check matplotlib figures against the rules of parts/figures.md, by geometry and not by eye.

Usage:
    python3 fig_lint.py make_fig1.py make_fig2.py --width-mm 86 178 --min-font 7 --style figstyle.md

    --width-mm W [W ...]   final widths the venue allows
    --min-font PT          smallest text at final size (default 6)
    --max-font PT          largest text, where the venue sets one
    --min-height-mm MM     smallest height of a capital letter, for venues that state lettering height;
                           measured on the font in use
    --max-height-mm MM     largest height of a figure
    --min-line PT          thinnest line (default 0.5)
    --style figstyle.md    the paper's table of meanings, colours, lines and markers

Each script is run with a non-interactive backend, and every figure it saves (or leaves open)
is inspected as drawn. Pass all the figure scripts of a paper in one call: colours are then
also compared across figures. Inside a plotting script the same check is

    import fig_lint
    fig_lint.show(fig_lint.check(fig, widths_mm=[86, 178], min_font=7, style=fig_lint.read_style("figstyle.md")))

What is checked:
  overlap     a legend, panel label or note on top of a curve, marker, bar, axis frame, tick
              mark or other text; tick labels that run into each other or into the next panel;
              text cut off at the edge of the figure
  colour      one colour standing for two things in one figure; one thing drawn in two colours;
              colours, lines and markers that differ from the paper's table (figstyle.md); pairs
              that merge under red-green colour-vision deficiency or in greyscale; marks and
              lettering too pale to see; rainbow colour maps; a diverging map not centred on zero;
              one colour map for two quantities; a colour-mapped panel without a labelled colour bar
  alignment   panel frames that almost, but not quite, line up; panel labels that do not share
              a baseline or a left edge, sit at different offsets, or run out of reading order
  text        sizes under the venue's minimum, more than three sizes, mixed fonts; symbols set
              upright and units set in italics; units written two ways; panel titles; a figure
              title; an axis multiplier left floating; too many or too few tick labels; ticks
              pointing in on one panel and out on another; the amount of text on the figure
  size        final width against the venue's column widths; a save that crops the figure;
              raster formats, low resolution, Type 3 fonts
  chart       cut bars, two y axes, pie charts, three-dimensional axes, hairlines, tiny markers

Errors are things the rules forbid outright; warnings usually need a fix; notes ask for a look.

What a colour stands for is read from the label of each series (the legend label, or the label
given to plot() even when no legend is drawn). A single unlabelled curve stands for the quantity
on its y axis. Black, white and greys are neutral: they may be reused freely. Two labels may share
a colour when the style table gives them the same colour, or when one panel shows one as points
and the other as a line (data and its fit).

The script cannot tell whether the plot is the right plot for the message, whether a schematic
is true to the device, or whether the figure is needed. It checks what matplotlib draws: text
or lines added later in a drawing program are not seen.

It runs the scripts it is given. Needs matplotlib and numpy. Exit status is 1 if any error is
reported, otherwise 0.
"""
import argparse
import math
import os
import re
import runpy
import sys
from collections import defaultdict

import numpy as np
import matplotlib
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PathCollection, PolyCollection
from matplotlib.colors import to_hex, to_rgb, to_rgba
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle, Wedge
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox

MM_PER_PT = 25.4 / 72
CAP = 0.72                       # capital height over font size, for Helvetica-like fonts (approximate)
PALE = 2.0                       # contrast ratio (WCAG formula) below which a mark is reported as too pale
GREEK = ("alpha|beta|gamma|delta|epsilon|zeta|eta|theta|kappa|lambda|mu|nu|xi|rho|sigma|tau|phi|chi|psi|omega")
RAINBOW = {"jet", "rainbow", "gist_rainbow", "nipy_spectral", "gist_ncar", "hsv", "turbo", "gnuplot", "gnuplot2",
           "brg", "prism", "flag", "spectral"}
DIVERGING = {"rdbu", "bwr", "seismic", "coolwarm", "piyg", "prgn", "brbg", "puor", "rdgy", "rdylbu", "rdylgn",
             "spectral", "vik", "berlin", "managua", "vanimo", "roma", "broc", "cork", "bam", "lisbon", "tofino"}
NONE = (None, "None", "none", " ", "")
KIND = {"tick": "tick label", "axislabel": "axis label", "offset": "axis multiplier", "title": "panel title",
        "suptitle": "figure title", "legend": "legend text", "note": "note", "panel": "panel label"}
WHAT = {"curve": "a curve", "marker": "data points", "bar": "a bar"}
_CAPS = {}
# Machado, Oliveira and Fernandes (2009), severity 1.0, applied to linear RGB
CVD = {"protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
       "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]])}


# ---------- colour ----------

def _linear(rgb):
    c = np.asarray(rgb, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lab_from_linear(lin):
    m = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = (m @ np.clip(lin, 0, 1)) / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def lab(colour, cvd=None):
    lin = _linear(to_rgb(colour))
    return _lab_from_linear(CVD[cvd] @ lin if cvd else lin)


def delta_e(a, b, cvd=None):
    return float(np.linalg.norm(lab(a, cvd) - lab(b, cvd)))


def luminance(colour):
    return float(np.dot([0.2126, 0.7152, 0.0722], _linear(to_rgb(colour))))


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def neutral(colour):
    r, g, b = to_rgb(colour)
    return max(r, g, b) - min(r, g, b) < 0.12


# ---------- geometry ----------

def _box(artist, renderer):
    try:
        if isinstance(artist, Annotation):              # the text alone, without its leader line
            b = Text.get_window_extent(artist, renderer)
        else:
            b = artist.get_window_extent(renderer)
    except Exception:
        return None
    e = (b.x0, b.y0, b.x1, b.y1)
    if not all(map(math.isfinite, e)) or b.width <= 0 or b.height <= 0:
        return None
    return e


def _name(target):
    return os.path.basename(str(target)) if isinstance(target, (str, os.PathLike)) else "a file object"


def _overlap(a, b, shrink):
    """Do two pixel boxes share more than 2 * shrink in both directions?"""
    return (min(a[2], b[2]) - max(a[0], b[0]) > 2 * shrink) and (min(a[3], b[3]) - max(a[1], b[1]) > 2 * shrink)


def _inside(a, b, tol=0.5):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


def _cut(a, b):
    c = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    return c if c[2] > c[0] and c[3] > c[1] else None


def _grow(a, d):
    return (a[0] - d, a[1] - d, a[2] + d, a[3] + d)


def _segments_hit(xy, box):
    """Does any segment of the polyline xy (pixels) pass through the box? (Liang-Barsky, vectorised)"""
    xy = np.asarray(xy, float)
    if len(xy) < 2:
        return False
    p, q = xy[:-1], xy[1:]
    ok = np.isfinite(p).all(axis=1) & np.isfinite(q).all(axis=1)
    p, q = p[ok], q[ok]
    if not len(p):
        return False
    d = q - p
    t0, t1, alive = np.zeros(len(p)), np.ones(len(p)), np.ones(len(p), bool)
    for dp, dq in ((-d[:, 0], p[:, 0] - box[0]), (d[:, 0], box[2] - p[:, 0]),
                   (-d[:, 1], p[:, 1] - box[1]), (d[:, 1], box[3] - p[:, 1])):
        alive &= ~((dp == 0) & (dq < 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            r = dq / dp
        t0 = np.where(dp < 0, np.maximum(t0, r), t0)
        t1 = np.where(dp > 0, np.minimum(t1, r), t1)
    return bool((alive & (t0 <= t1)).any())


def _points_hit(xy, box):
    xy = np.asarray(xy, float).reshape(-1, 2)
    xy = xy[np.isfinite(xy).all(axis=1)]
    return bool(((xy[:, 0] >= box[0]) & (xy[:, 0] <= box[2]) & (xy[:, 1] >= box[1]) & (xy[:, 1] <= box[3])).any())


def _is_field(artist):
    """Colour-mapped areas (images, meshes, filled contours): a background, not a mark to keep clear of."""
    name = type(artist).__name__
    return name in ("AxesImage", "QuadMesh", "PcolorImage", "NonUniformImage") or "ContourSet" in name


def _ink_hits(artist, box, axbox, px, bars=()):
    """Which drawn part of a data artist lies inside the pixel box: 'curve', 'marker', 'bar', 'area' or ''."""
    if getattr(artist, "get_clip_on", lambda: True)():
        box = _cut(box, axbox)
        if box is None:
            return ""
    try:
        if isinstance(artist, Line2D):
            xy = artist.get_transform().transform(np.asarray(artist.get_xydata(), float))
            if artist.get_linestyle() not in NONE and _segments_hit(xy, _grow(box, artist.get_linewidth() * px / 2)):
                return "curve"
            if artist.get_marker() not in NONE and _points_hit(xy, _grow(box, artist.get_markersize() * px / 2)):
                return "marker"
            return ""
        if isinstance(artist, LineCollection):
            tr = artist.get_transform()
            return "curve" if any(_segments_hit(tr.transform(np.asarray(seg, float)), box)
                                  for seg in artist.get_segments() if len(seg) > 1) else ""
        if isinstance(artist, PathCollection):
            offs = np.ma.filled(np.ma.asarray(artist.get_offsets(), float), np.nan)
            sizes = artist.get_sizes()
            r = (math.sqrt(float(np.max(sizes))) / 2 if len(sizes) else 2) * px
            return "marker" if _points_hit(artist.get_offset_transform().transform(offs), _grow(box, r)) else ""
        if isinstance(artist, Rectangle):
            b = _box(artist, None)
            if b is None or not _overlap(b, box, 0.2 * px):
                return ""
            return "bar" if id(artist) in bars else "area"
        if isinstance(artist, (PolyCollection, Patch)):
            paths = artist.get_paths() if isinstance(artist, PolyCollection) else [artist.get_path()]
            tr, bb = artist.get_transform(), Bbox.from_extents(*box)
            return "area" if any(q.transformed(tr).intersects_bbox(bb, filled=True) for q in paths if len(q.vertices)) else ""
    except Exception:
        return ""
    return ""


def _polylines(path, transform):
    """The outline of a path as polylines in pixels: sub-paths are split, closing vertices are replaced."""
    xy = transform.transform(np.asarray(path.vertices, float))
    codes = path.codes
    if codes is None:
        return [xy]
    out, cur = [], []
    for v, c in zip(xy, codes):
        if c == 1:                                      # MOVETO
            if len(cur) > 1:
                out.append(np.array(cur))
            cur = [v]
        elif c == 79:                                   # CLOSEPOLY: back to the start of the sub-path
            if cur:
                cur.append(cur[0])
        else:
            cur.append(v)
    if len(cur) > 1:
        out.append(np.array(cur))
    return out


def _edge_hits(artist, box, px):
    """For drawings: does an outline or a line pass through the box? (A label may sit on a face.)"""
    try:
        if isinstance(artist, Line2D):
            return artist.get_linestyle() not in NONE and _segments_hit(
                artist.get_transform().transform(np.asarray(artist.get_xydata(), float)), box)
        if isinstance(artist, Patch):
            if type(artist).__name__ == "FancyArrowPatch":      # the shaft and head themselves, not their bounding box
                return any(_segments_hit(line, box) for line in _polylines(artist.get_path(), artist.get_transform()))
            edge, face = to_rgba(artist.get_edgecolor()), to_rgba(artist.get_facecolor())
            if edge[3] == 0 or artist.get_linewidth() == 0 or np.allclose(edge, face):
                return False
            return any(_segments_hit(np.vstack([line, line[:1]]), box)
                       for line in _polylines(artist.get_path(), artist.get_transform()))
    except Exception:
        return False
    return False


# ---------- reading a figure ----------

def _plain(s):
    return re.sub(r"\s+", " ", s.replace("$", "")).strip()


def _letter(s):
    """'a' for a panel label such as (a), a, A. or \\textbf{a}; None for anything else."""
    if "$" in s and not re.search(r"\\(?:mathbf|mathrm|text|textbf|bf)\b", s):
        return None                                   # an italic letter in math mode is a symbol
    t = re.sub(r"\\(?:textbf|mathbf|bf|mathrm|textrm|text)\s*\{([^{}]*)\}", r"\1", s.replace("$", "")).strip()
    m = re.fullmatch(r"(\(?)([A-Za-z])(\)?)\.?", t)
    return (m.group(2), ("(" if m.group(1) else "") + ("A" if m.group(2).isupper() else "a") + (")" if m.group(3) else "")) if m else None


def _axes_table(fig, renderer):
    rows = []
    for ax in fig.findobj(Axes):
        if not ax.get_visible():
            continue
        box = _box(ax, renderer)
        if box is None:
            continue
        kind = "colorbar" if (getattr(ax, "_colorbar", None) is not None or ax.get_label() == "<colorbar>") else \
               ("3d" if ax.name == "3d" else ("art" if not ax.axison else "main"))
        rows.append({"ax": ax, "box": box, "kind": kind, "parent": None, "name": ""})
    for i, a in enumerate(rows):
        if a["kind"] == "colorbar":
            continue
        for b in rows[:i]:
            if b["kind"] != "colorbar" and max(abs(x - y) for x, y in zip(a["box"], b["box"])) < 1.0:
                a["kind"], a["parent"] = "twin", b
                break
    for a in rows:
        if a["kind"] in ("main", "art"):
            area = (a["box"][2] - a["box"][0]) * (a["box"][3] - a["box"][1])
            for b in rows:
                if b is a or b["kind"] not in ("main", "art", "3d"):
                    continue
                if _inside(a["box"], b["box"], 0) and area < 0.7 * (b["box"][2] - b["box"][0]) * (b["box"][3] - b["box"][1]):
                    a["kind"], a["parent"] = "inset", b
                    break
    return rows


def _texts(fig, table, renderer):
    """Every visible piece of text with its role, owner and pixel box."""
    items, seen = [], set()

    def add(t, kind, row, **extra):
        if t is None or id(t) in seen or not t.get_visible() or not t.get_text().strip():
            return
        box = _box(t, renderer)
        if box is None:
            return
        seen.add(id(t))
        items.append({"t": t, "kind": kind, "row": row, "box": box, "text": t.get_text().strip(),
                      "size": float(t.get_fontsize()), **extra})

    for row in table:
        ax = row["ax"]
        if ax.axison and row["kind"] != "3d":
            for axis, name in ((ax.xaxis, "x"), (ax.yaxis, "y")):
                if not axis.get_visible():
                    continue
                lo, hi = sorted(axis.get_view_interval())
                eps = 1e-9 * (abs(hi - lo) or 1.0)
                for tick in axis.get_major_ticks():
                    if lo - eps <= tick.get_loc() <= hi + eps:
                        add(tick.label1, "tick", row, axis=name)
                        add(tick.label2, "tick", row, axis=name)
                add(axis.label, "axislabel", row, axis=name)
                add(axis.get_offset_text(), "offset", row, axis=name)
        for t in (ax.title, getattr(ax, "_left_title", None), getattr(ax, "_right_title", None)):
            add(t, "title", row)
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            for t in leg.get_texts() + [leg.get_title()]:
                add(t, "legend", row, legend=leg)
        for t in ax.texts:
            add(t, "note", row)
    for leg in fig.legends:
        for t in leg.get_texts() + [leg.get_title()]:
            add(t, "legend", None, legend=leg)
    add(getattr(fig, "_suptitle", None), "suptitle", None)
    add(getattr(fig, "_supxlabel", None), "axislabel", None, axis="x")
    add(getattr(fig, "_supylabel", None), "axislabel", None, axis="y")
    for t in fig.texts:
        add(t, "note", None)
    return items


def _marks(ax):
    """Data artists of an Axes that a label must keep clear of."""
    out = [a for a in ax.lines if a.get_visible()]
    out += [c for c in ax.collections if c.get_visible() and not _is_field(c)]
    out += [p for p in ax.patches if p.get_visible()]
    return out


def _series(row):
    """What is drawn in which colour, and what it stands for (label, or the y label of a lone curve)."""
    ax, out = row["ax"], []
    art = row["kind"] == "art"

    def add(label, colour, artist, style="", marker=""):
        try:
            hexc = to_hex(colour)
        except (ValueError, TypeError):
            return
        named = bool(label) and not str(label).startswith("_")
        has_line, has_mark = str(style) not in NONE + ("bar", "patch"), str(marker) not in NONE
        form = "both" if has_line and has_mark else "line" if has_line else "marker" if has_mark else "other"
        out.append({"label": _plain(str(label)) if named else None, "colour": hexc, "artist": artist,
                    "style": str(style), "marker": str(marker), "form": form, "line2d": isinstance(artist, Line2D)})

    in_container = set()
    for c in ax.containers:
        if isinstance(c, BarContainer) and len(c.patches):
            add(c.get_label(), c.patches[0].get_facecolor(), c, "bar")
            in_container.update(id(p) for p in c.patches)
        elif isinstance(c, ErrorbarContainer):
            line = c.lines[0] or (c.lines[2][0] if c.lines[2] else None)
            if line is not None:
                colour = line.get_color() if isinstance(line, Line2D) else line.get_edgecolor()[0]
                add(c.get_label(), colour, c, getattr(line, "get_linestyle", lambda: "")(), getattr(line, "get_marker", lambda: "")())
            in_container.update(id(x) for x in [c.lines[0], *c.lines[1], *c.lines[2]] if x is not None)
    for line in ax.lines:
        if not line.get_visible() or id(line) in in_container or not len(line.get_xdata()):
            continue
        if art and str(line.get_label()).startswith("_"):
            continue
        add(line.get_label(), line.get_color(), line, line.get_linestyle(), line.get_marker())
    for coll in ax.collections:
        if not coll.get_visible() or id(coll) in in_container or _is_field(coll):
            continue
        if getattr(coll, "get_array", lambda: None)() is not None:
            continue                                    # colour-mapped points: handled with the colour maps
        fc, ec = coll.get_facecolor(), coll.get_edgecolor()
        colour = fc[0] if len(fc) and fc[0][3] > 0 else (ec[0] if len(ec) else None)
        if colour is not None and (isinstance(coll, PathCollection) or not str(coll.get_label()).startswith("_")):
            add(coll.get_label(), colour, coll, "", "o" if isinstance(coll, PathCollection) else "")
    for p in ax.patches:
        if p.get_visible() and id(p) not in in_container and not str(p.get_label()).startswith("_"):
            add(p.get_label(), getattr(p, "base_colour", None) or p.get_facecolor(), p, "patch")
    if not art:
        named = [s for s in out if s["label"]]
        lone = [s for s in out if not s["label"]]
        if not named and len(lone) == 1 and ax.get_ylabel().strip():
            lone[0]["label"], lone[0]["implied"] = "y axis: " + _plain(ax.get_ylabel()), True
    return out


def _mappables(row):
    ax, out = row["ax"], []
    for m in list(ax.images) + list(ax.collections):
        if not m.get_visible() or getattr(m, "get_array", lambda: None)() is None or not hasattr(m, "get_cmap"):
            continue
        arr = np.ma.masked_invalid(np.ma.asarray(m.get_array(), float))
        if arr.count() == 0:
            continue
        if isinstance(m, PathCollection) and not _is_field(m) and arr.size <= 1:
            continue
        out.append({"m": m, "row": row, "cmap": m.get_cmap().name, "vmin": m.norm.vmin, "vmax": m.norm.vmax,
                    "norm": type(m.norm).__name__, "lo": float(arr.min()), "hi": float(arr.max())})
    return out


def _reading_order(rows):
    """Panels in reading order: lines from the top, each line from the left."""
    left, out = sorted(rows, key=lambda r: (-r["box"][3], r["box"][0])), []
    while left:
        y0, y1 = left[0]["box"][1], left[0]["box"][3]
        mid = (y0 + y1) / 2
        line = [r for r in left if y0 < (r["box"][1] + r["box"][3]) / 2 < y1 or r["box"][1] < mid < r["box"][3]]
        out += sorted(line, key=lambda r: (r["box"][0], -r["box"][3]))
        left = [r for r in left if not any(r is x for x in line)]
    return out


def _is_number(text):
    t = re.sub(r"\\mathdefault\{([^{}]*)\}", r"\1", text.replace("$", "")).replace("\u2212", "-").strip()
    return bool(re.fullmatch(r"[-+]?[\d.,]+(?:[eE][-+]?\d+)?", t)) or "10^" in t or "\\times" in t


def _cap_ratio(text, renderer):
    """Height of a capital letter over the font size, measured on the font that the text uses."""
    name = text.get_fontname()
    if name not in _CAPS:
        try:
            prop = text.get_fontproperties().copy()
            prop.set_size(100)
            _, h, _ = renderer.get_text_width_height_descent("H", prop, ismath=False)
            ratio = h / renderer.points_to_pixels(100)
            _CAPS[name] = ratio if 0.5 < ratio < 0.9 else CAP
        except Exception:
            _CAPS[name] = CAP
    return _CAPS[name]


def _norm(value):
    """Line styles and markers as words, so that '-' and 'solid', or '' and 'None', compare equal."""
    v = str(value).strip().strip("`").lower()
    return {"-": "solid", "--": "dashed", ":": "dotted", "-.": "dashdot", "": "none"}.get(v, v)


def _tickdir(tick):
    return tick.get_tickdir() if hasattr(tick, "get_tickdir") else getattr(tick, "_tickdir", "out")


# ---------- the check ----------

def check(fig, widths_mm=None, min_font=6.0, max_font=None, min_height_mm=None, max_height_mm=None, min_line=0.5,
          style=None, saved=None, max_series=6):
    """Inspect one figure. Returns {'findings': [(level, where, message)], 'palette': [...], ...}.

    widths_mm: allowed final widths; min_font / max_font: text size in points at final size;
    min_height_mm: smallest height of a capital letter (for venues that state lettering height);
    max_height_mm: largest height of the figure; min_line: thinnest line in points;
    style: read_style("figstyle.md"), or {label: colour}; saved: [{'name', 'dpi', 'tight'}] from savefig.
    """
    found = []
    style = {k: (dict(v) if isinstance(v, dict) else {"colour": v}) for k, v in (style or {}).items()}

    def add(level, where, msg):
        if (level, where, msg) not in found:
            found.append((level, where, msg))

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer() if hasattr(fig.canvas, "get_renderer") else fig._get_renderer()
    px = fig.dpi / 72.0                                 # pixels per point
    width_px, height_px = fig.get_size_inches() * fig.dpi
    w_mm, h_mm = (v * 25.4 for v in fig.get_size_inches())
    table = _axes_table(fig, renderer)
    texts = _texts(fig, table, renderer)
    panels = [r for r in table if r["kind"] in ("main", "art", "3d")]
    saved = saved or []
    tight = any(s.get("tight") for s in saved)

    # ----- panel labels and panel names -----
    cands = []
    for it in texts:
        if it["kind"] not in ("note", "title"):
            continue
        got = _letter(it["text"])
        if not got:
            continue
        t = it["t"]
        try:                                            # where the text is anchored, in pixels (valid after a draw)
            anchor = np.asarray(t.get_transform().transform(t.get_position()), float) if it["kind"] == "note" else None
        except Exception:
            anchor = None
        if anchor is None or not np.isfinite(anchor).all():
            anchor = np.array([it["box"][0], it["box"][1]])
        owner = it["row"] if (it["row"] is not None and it["row"] in panels) else None
        if owner is None and panels:
            owner = min(panels, key=lambda r: math.hypot(anchor[0] - r["box"][0], anchor[1] - r["box"][3]))
        if owner is None:
            continue
        dx, dy = (anchor[0] - owner["box"][0]) / px, (anchor[1] - owner["box"][3]) / px
        if abs(dx) <= 70 and -32 <= dy <= 32:
            cands.append({**it, "letter": got[0], "form": got[1], "owner": owner, "anchor": anchor, "dx": dx, "dy": dy})
    labels = []
    if cands:
        forms = defaultdict(list)
        for c in cands:
            forms[c["form"]].append(c)
        best = max(forms.values(), key=len)
        letters = sorted(c["letter"].lower() for c in best)
        if letters[0] == "a" or len(best) >= 2:
            labels = best
            if len(forms) > 1:
                add("W", "figure", "panel labels are written in different forms: " + ", ".join(
                    f"{c['text']}" for group in forms.values() for c in group[:1]))
    for c in labels:
        c["kind"] = "panel"
        for it in texts:
            if it["t"] is c["t"]:
                it["kind"] = "panel"
        if not c["owner"]["name"]:
            c["owner"]["name"] = c["text"] if "(" in c["text"] else f"panel {_plain(c['text'])}"
    ordered = _reading_order(panels)
    for n, r in enumerate(ordered, 1):
        r["name"] = r["name"] or f"panel {n}"
    for r in table:
        if r["kind"] in ("inset", "twin") and r["parent"] is not None:
            r["name"] = ("inset of " if r["kind"] == "inset" else "second axis of ") + (r["parent"]["name"] or "a panel")
        elif r["kind"] == "colorbar":
            r["name"] = "colour bar"

    def where(row):
        return row["name"] if row is not None else "figure"

    def quote(s, n=28):
        s = " ".join(s.split())
        return "'" + (s if len(s) <= n else s[: n - 1] + "…") + "'"

    # ----- size, saving -----
    if widths_mm and not any(abs(w_mm - w) <= 0.6 for w in widths_mm):
        target = max(widths_mm) if w_mm > max(widths_mm) else min(widths_mm, key=lambda w: abs(w - w_mm))
        sizes_now = sorted({round(it["size"], 1) for it in texts if it["kind"] != "panel"})
        shrunk = f" Scaled to {target:g} mm, its {sizes_now[0]:g}-pt text becomes {sizes_now[0] * target / w_mm:.1f} pt." if sizes_now else ""
        add("W", "figure", f"the figure is {w_mm:.1f} mm wide; the venue's widths are {', '.join(f'{w:g}' for w in widths_mm)} mm."
                           f"{shrunk} Build the figure at its final size, so that a point on the figure is a point on the page")
    if max_height_mm and h_mm > max_height_mm + 0.6:
        add("W", "figure", f"the figure is {h_mm:.0f} mm tall; the limit given is {max_height_mm:g} mm, and the caption needs room as well")
    for s in saved:
        ext = os.path.splitext(str(s.get("name", "")))[1].lower()
        if s.get("tight"):
            tb = fig.get_tightbbox(renderer)
            add("W", "figure", f"{_name(s['name'])} is saved with bbox_inches='tight': the file is about "
                               f"{tb.width * 25.4 + 5:.0f} mm wide, not {w_mm:.0f} mm. Set the size and the margins instead of cropping")
        if ext in (".jpg", ".jpeg"):
            add("W", "figure", f"{_name(s['name'])}: JPEG blurs lines and text; save vector (PDF, EPS, SVG) or TIFF/PNG")
        elif ext in (".png", ".tif", ".tiff") and not any(os.path.splitext(str(o.get("name", "")))[1].lower() in (".pdf", ".eps", ".svg", ".ps") for o in saved):
            if not any(m for r in table if r["kind"] != "colorbar" for m in _mappables(r)):
                add("N", "figure", f"{_name(s['name'])}: line art saved only as a raster image; save a vector file as well")
            dpi = s.get("dpi") or matplotlib.rcParams["savefig.dpi"]
            dpi = fig.dpi if dpi == "figure" else dpi
            if float(dpi) < 300:
                add("W", "figure", f"{_name(s['name'])} is saved at {float(dpi):.0f} dpi: use 300 or more (600 for line art)")
        if ext == ".pdf" and matplotlib.rcParams["pdf.fonttype"] == 3:
            add("N", "figure", "PDF text is stored as Type 3 fonts: set pdf.fonttype to 42 so that text stays text")

    # ----- text: size, font, amount -----
    sized = [it for it in texts if it["kind"] != "panel"]
    small = sorted({(round(it["size"], 1), it["kind"]) for it in sized if it["size"] < min_font - 0.05})
    if small:
        add("E", "figure", f"text under {min_font:g} pt at final size: " + ", ".join(f"{KIND[k]} {s:g} pt" for s, k in small[:6]))
    if min_height_mm:                                    # 5% of tolerance: 8-pt Helvetica is 2.0 mm, its clones 1.9 mm
        caps = {(round(it["size"], 1), it["t"].get_fontname(), round(it["size"] * MM_PER_PT * _cap_ratio(it["t"], renderer), 2))
                for it in sized}
        low = sorted(c for c in caps if c[2] < 0.95 * min_height_mm)
        if low:
            add("E", "figure", f"lettering under {min_height_mm:g} mm high: " + "; ".join(
                f"capitals of {size:g}-pt {font} are {height:.2f} mm" for size, font, height in low[:4]))
    if max_font:
        big = sorted({(round(it["size"], 1), it["kind"]) for it in sized if it["size"] > max_font + 0.05})
        if big:
            add("W", "figure", f"text over {max_font:g} pt: " + ", ".join(f"{KIND[k]} {s:g} pt" for s, k in big[:6]))
    sizes = sorted({round(it["size"], 1) for it in sized})
    if len(sizes) > 3:
        add("N", "figure", f"{len(sizes)} text sizes ({', '.join(f'{s:g}' for s in sizes)} pt): two or three are enough")
    for kind, name in (("tick", "tick labels"), ("axislabel", "axis labels"), ("legend", "legend text"), ("panel", "panel labels")):
        ks = sorted({round(it["size"], 1) for it in texts if it["kind"] == kind})
        if len(ks) > 1:
            add("W", "figure", f"{name} come in several sizes: {', '.join(f'{s:g}' for s in ks)} pt")
    fonts = sorted({it["t"].get_fontname() for it in texts})
    if len(fonts) > 1:
        add("W", "figure", "more than one font: " + ", ".join(fonts))
    if matplotlib.rcParams["mathtext.fontset"] == "cm" and not matplotlib.rcParams["text.usetex"] and \
            any("$" in it["text"] for it in texts) and "serif" not in " ".join(fonts).lower().replace("sans", ""):
        add("N", "figure", "symbols are set in Computer Modern while the text is sans-serif: choose a math font that matches "
                           "(mathtext.fontset 'dejavusans', 'stixsans' or 'custom')")
    words = sum(len(_plain(it["text"]).split()) for it in texts if it["kind"] in ("note", "title", "suptitle", "legend"))
    if words > 12 * max(len(panels), 1):
        add("N", "figure", f"about {words} words of notes, legends and titles on the figure: explanations belong in the caption")
    for it in texts:
        if it["kind"] == "note" and len(_plain(it["text"]).split()) > 6:
            add("N", where(it["row"]), f"a note of {len(_plain(it['text']).split())} words, {quote(it['text'])}: say it in the caption")

    # ----- titles -----
    for it in texts:
        if it["kind"] == "suptitle":
            add("W", "figure", f"figure title {quote(it['text'])}: the title of a figure is the first line of its caption")
        elif it["kind"] == "title":
            add("N", where(it["row"]), f"panel title {quote(it['text'])}: keep a title only if it names what differs between panels; "
                                       "otherwise the axis labels and the caption carry it")

    # ----- overlaps -----
    frame = (0, 0, width_px, height_px)

    def named(it, place=None):                           # place: the panel the finding is filed under
        text = f"{KIND[it['kind']]} {quote(it['text'])}"
        if place is not None and it["row"] is not None and it["row"] is not place:
            text += f" of {where(it['row'])}"
        return text

    for it in texts:
        if not _inside(it["box"], frame, 0.7 * px) and not tight:
            if it["kind"] == "tick":
                add("E", where(it["row"]), f"tick labels of the {it.get('axis')} axis are cut off at the edge of the figure: widen the margin")
            else:
                add("E", where(it["row"]), f"{named(it)} is cut off at the edge of the figure")
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            if a.get("legend") is not None and a.get("legend") is b.get("legend"):
                continue
            if not _overlap(a["box"], b["box"], 0.5 * px):   # more than 1 pt in both directions
                continue
            ticks = [x for x in (a, b) if x["kind"] == "tick"]
            if len(ticks) == 2 and a["row"] is b["row"] and a.get("axis") == b.get("axis"):
                add("E", where(a["row"]), f"tick labels overlap on the {a.get('axis')} axis: use fewer ticks or shorter numbers")
            elif len(ticks) == 2:
                add("E", where(a["row"]), f"tick labels of the {a.get('axis')} axis overlap tick labels of the {b.get('axis')} axis"
                    + (f" of {where(b['row'])}" if b["row"] is not a["row"] else ""))
            elif len(ticks) == 1:
                t, o = (a, b) if a["kind"] == "tick" else (b, a)
                add("E", where(o["row"] or t["row"]), f"{named(o)} overlaps the tick labels of the {t.get('axis')} axis"
                    + (f" of {where(t['row'])}" if t["row"] is not o["row"] else ""))
            else:
                place = a["row"] or b["row"]
                add("E", where(place), f"{named(a, place)} overlaps {named(b, place)}")
    boxes = []                                          # legends and loose text against marks and frames
    for row in table:
        leg = row["ax"].get_legend()
        if leg is not None and leg.get_visible():
            b = _box(leg, renderer)
            if b:
                boxes.append(("legend", "the legend", b, row))
    for leg in fig.legends:
        b = _box(leg, renderer)
        if b:
            boxes.append(("legend", "the figure legend", b, None))
            if not _inside(b, frame, 0.7 * px) and not tight:
                add("E", "figure", "the figure legend is cut off at the edge of the figure")
    for it in texts:
        if it["kind"] in ("note", "panel"):
            boxes.append((it["kind"], named(it), it["box"], it["row"]))
    for kind, name, box, own in boxes:
        for row in table:
            if row["kind"] == "colorbar":
                if _overlap(box, row["box"], 0.5 * px):
                    add("E", where(own), f"{name} overlaps a colour bar")
                continue
            if not _overlap(box, row["box"], 0.2 * px):
                continue
            ax, rb = row["ax"], row["box"]
            if row["kind"] == "art":
                if kind != "legend" and any(_edge_hits(m, _grow(box, -0.4 * px), px) for m in _marks(ax)):
                    add("W", where(row), f"{name} crosses a line or an outline of the drawing: move it onto a face or into free space")
                continue
            if row["kind"] == "3d":
                continue
            if ax.name == "rectilinear" and ax.axison:   # the axis frame and the tick marks
                tol = 0.5 * px                           # an edge laid on the frame (borderaxespad=0) does not cross it
                sides = {"left": box[0] < rb[0] - tol and rb[0] + tol < box[2],
                         "right": box[0] < rb[2] - tol and rb[2] + tol < box[2],
                         "bottom": box[1] < rb[1] - tol and rb[1] + tol < box[3],
                         "top": box[1] < rb[3] - tol and rb[3] + tol < box[3]}
                crossed = [side for side, hit in sides.items() if hit and ax.spines[side].get_visible()]
                if crossed and not (own is not None and own is not row and own["parent"] is row):
                    add("E", where(row), f"{name} crosses the axis frame ({', '.join(crossed)})")
                elif _inside(box, rb, 0.4 * px):
                    for axis, low, high in ((ax.xaxis, 1, 3), (ax.yaxis, 0, 2)):
                        ticks = axis.get_major_ticks()
                        if not ticks or _tickdir(ticks[0]) == "out":
                            continue
                        reach = ticks[0].tick1line.get_markersize() * px
                        if (box[low] - rb[low] < reach and ticks[0].tick1line.get_visible()) or \
                                (rb[high] - box[high] < reach and ticks[0].tick2line.get_visible()):
                            add("W", where(row), f"{name} sits on the tick marks: keep it {reach / px:.0f} pt or more from the frame")
            bar_ids = {id(q) for c in ax.containers if isinstance(c, BarContainer) for q in c.patches}
            worst, what = "", None                      # the data
            for m in _marks(ax):
                hit = _ink_hits(m, box, rb, px, bar_ids)
                if hit and (hit != "area" or not worst):
                    worst, what = hit, m
                    if hit != "area":
                        break
            if worst:
                label = what.get_label() if isinstance(what.get_label(), str) and not what.get_label().startswith("_") else ""
                tail = f" ({quote(label)})" if label else ""
                if worst == "area":
                    add("N", where(row), f"{name} lies on a filled area{tail}: check that it stays legible, or move it to free space")
                else:
                    add("E", where(row), f"{name} overlaps {WHAT[worst]}{tail}")
    for it in texts:                                    # labels of one panel running into another panel
        if it["kind"] not in ("tick", "axislabel", "offset", "title") or it["row"] is None:
            continue
        for row in table:
            if row is it["row"] or row["kind"] == "twin" or it["row"]["kind"] == "twin":
                continue
            if row["parent"] is it["row"] or it["row"]["parent"] is row:
                continue
            if _overlap(it["box"], row["box"], 0.4 * px):
                what = f"tick labels of the {it.get('axis')} axis run" if it["kind"] == "tick" else f"{named(it)} runs"
                add("E", where(it["row"]), f"{what} into {row['name']}")
    for row in table:                                   # insets on top of data
        if row["kind"] == "inset" and row["parent"] is not None and row["parent"]["kind"] == "main":
            tb = row["ax"].get_tightbbox(renderer)
            ib = (tb.x0, tb.y0, tb.x1, tb.y1) if tb is not None else row["box"]
            if any(_ink_hits(m, ib, row["parent"]["box"], px) in WHAT for m in _marks(row["parent"]["ax"])):
                add("E", where(row["parent"]), "the inset, with its labels, covers data of the panel")

    # ----- panel labels: alignment, offset, order -----
    grid = [r for r in panels]
    if len(grid) >= 2 and not labels:
        add("N", "figure", f"{len(grid)} panels and no panel labels found near their top-left corners")
    if labels:
        if len({(c["t"].get_ha(), c["t"].get_va()) for c in labels}) > 1:
            add("W", "figure", "panel labels are anchored differently (ha/va): give all of them the same anchor")
        if len({str(c["t"].get_fontweight()) for c in labels}) > 1:
            add("W", "figure", "panel labels mix weights (bold and regular)")
        for a in labels:
            for b in labels:
                if a is b or a["letter"] >= b["letter"]:
                    continue
                A, B = a["owner"]["box"], b["owner"]["box"]
                same_row = abs(A[3] - B[3]) < 8 * px     # panels whose tops are meant to be level
                same_col = abs(A[0] - B[0]) < 8 * px
                dyp, dxp = abs(a["anchor"][1] - b["anchor"][1]) / px, abs(a["anchor"][0] - b["anchor"][0]) / px
                if same_row and dyp > 0.5:
                    add("E", "figure", f"panel labels {a['text']} and {b['text']} are not on one horizontal line (off by {dyp:.1f} pt)")
                if same_col and dxp > 0.5:
                    add("E", "figure", f"panel labels {a['text']} and {b['text']} are not on one vertical line (off by {dxp:.1f} pt)")
        offs = [(c["dx"], c["dy"]) for c in labels]
        if max(abs(o[0] - offs[0][0]) for o in offs) > 1.0 or max(abs(o[1] - offs[0][1]) for o in offs) > 1.0:
            add("W", "figure", "panel labels sit at different offsets from their panels: " + ", ".join(
                f"{c['text']} ({c['dx']:+.0f}, {c['dy']:+.0f}) pt" for c in sorted(labels, key=lambda c: c["letter"])))
        owners = []
        for c in labels:
            if not any(c["owner"] is o for o in owners):
                owners.append(c["owner"])
        order = [c["letter"].lower() for o in _reading_order(owners) for c in labels if c["owner"] is o]
        heights = [o["box"][3] - o["box"][1] for o in owners]
        if order != sorted(order) and max(heights) < 1.4 * min(heights):     # skipped when a panel spans rows
            add("W", "figure", "panel labels are not in reading order (left to right, then down): " + ", ".join(order))
        expected = [chr(ord("a") + k) for k in range(len(order))]
        if sorted(order) != expected:
            add("W", "figure", "panel labels skip or repeat a letter: " + ", ".join(sorted(order)))
        if len(labels) != len(grid):
            add("N", "figure", f"{len(grid)} panels but {len(labels)} panel label(s)")

    # ----- panel frames: near misses -----
    misses = []
    for i, a in enumerate(grid):
        for b in grid[i + 1:]:
            for k, edge in ((0, "left"), (2, "right"), (1, "bottom"), (3, "top")):
                d = abs(a["box"][k] - b["box"][k]) / px
                if 0.35 < d < 6:
                    misses.append((d, f"the {edge} edges of {a['name']} and {b['name']} differ by {d:.1f} pt"))
            for k, dim in ((0, "widths"), (1, "heights")):
                da, db = a["box"][k + 2] - a["box"][k], b["box"][k + 2] - b["box"][k]
                d = abs(da - db) / px
                if 0.35 < d < 6:
                    misses.append((d, f"the {dim} of {a['name']} and {b['name']} differ by {d:.1f} pt"))
    for _, msg in sorted(misses)[:6]:
        add("W", "figure", msg + ": panels that nearly line up should line up exactly")

    # ----- colour -----
    palette, forms, all_series = [], defaultdict(set), []
    for row in table:
        if row["kind"] == "colorbar":
            continue
        ss = _series(row)
        all_series.append((row, ss))
        bg = row["ax"].get_facecolor()
        bg = fig.get_facecolor() if to_rgba(bg)[3] == 0 else bg
        for s in ss:
            if s["label"]:
                palette.append((row["name"], s["label"], s["colour"]))
                forms[(row["name"], s["label"])].add(s["form"])
            if s["style"] != "patch" and row["kind"] != "art" and contrast(s["colour"], bg) < PALE:
                add("W", where(row), f"{quote(s['label'] or 'a series')} is drawn in {s['colour']}, contrast {contrast(s['colour'], bg):.1f} "
                                     f"against the background: under {PALE:g}, too pale to follow")
        if row["kind"] == "art":
            continue
        loose = [s for s in ss if not s["label"]]
        if len(loose) >= 2 and len({s["colour"] for s in loose}) >= 2:
            add("N", where(row), f"{len(loose)} series have no label in the script: the check cannot tell what their colours stand for")
        drawn = [s for s in ss if s["style"] not in ("patch", "bar")]
        if len(drawn) > max_series:
            add("N", where(row), f"{len(drawn)} series in one panel: more than about {max_series} are hard to tell apart; "
                                 "split the panel or show fewer")
        close, grey = 0, []
        for i, a in enumerate(drawn):                   # pairs that merge for some readers
            for b in drawn[i + 1:]:
                if a["colour"] == b["colour"] or (a["style"], a["marker"]) != (b["style"], b["marker"]):
                    continue                            # the same colour is judged below; a second cue is enough here
                normal = delta_e(a["colour"], b["colour"])
                worst = min(delta_e(a["colour"], b["colour"], k) for k in CVD)
                pair = f"{quote(a['label'] or a['colour'])} and {quote(b['label'] or b['colour'])}"
                if normal < 10:
                    close += 1
                elif normal >= 20 and worst < 12:
                    add("W", where(row), f"{pair} are hard to tell apart with red-green colour-vision deficiency "
                                         f"(difference {worst:.0f}, against {normal:.0f} for normal vision): change a colour, or add a line style or marker")
                elif abs(lab(a["colour"])[0] - lab(b["colour"])[0]) < 8:
                    grey.append(pair)
        if grey:
            add("N", where(row), f"{len(grey)} pair(s) of series have the same lightness and no second cue, so they merge in greyscale: "
                                 + "; ".join(grey[:3]) + (" ..." if len(grey) > 3 else ""))
        if close:
            add("N", where(row), f"{close} pair(s) of series differ by less than 10 in colour (CIELAB) and share line style and marker: "
                                 "they can be followed only by their order; label them directly or mark the order with an arrow")
    by_colour, by_label = defaultdict(set), defaultdict(set)
    for name, label, colour in palette:
        by_label[label].add(colour)
        if not neutral(colour):
            by_colour[colour].add(label)
    merged = []                                          # treat nearly identical colours as one
    for c in sorted(by_colour):
        home = next((g for g in merged if delta_e(g[0], c) < 3), None)
        (home.append(c) if home else merged.append([c]))

    def declared_same(a, b):                             # the style table gives both meanings one colour, on purpose
        return a in style and b in style and delta_e(style[a]["colour"], style[b]["colour"]) < 3

    def points_and_line(a, b, group):                    # one panel shows a as points and b as a line: data and its fit
        def panels_of(label):
            return {n for n, lbl, c in palette if lbl == label and c in group}
        return any({frozenset(forms[(n, a)]), frozenset(forms[(n, b)])} == {frozenset({"line"}), frozenset({"marker"})}
                   for n in panels_of(a) & panels_of(b))

    for group in merged:
        meanings = sorted(set().union(*(by_colour[c] for c in group)))
        clash = [(a, b) for i, a in enumerate(meanings) for b in meanings[i + 1:]
                 if not declared_same(a, b) and not points_and_line(a, b, group)]
        if clash:
            involved = sorted({m for pair in clash for m in pair})
            uses = "; ".join(f"{quote(lbl, 34)} in {', '.join(sorted({n for n, l, c in palette if l == lbl and c in group}))}"
                             for lbl in involved)
            add("E", "figure", f"one colour, {len(involved)} meanings: {group[0]} stands for {uses}")
    for label, colours in sorted(by_label.items()):
        if len(colours) > 1 and max(delta_e(a, b) for a in colours for b in colours) >= 3:
            add("E", "figure", f"one meaning, {len(colours)} colours: {quote(label, 34)} is drawn in {', '.join(sorted(colours))}")
    if style:
        listed = {to_hex(v["colour"]): k for k, v in style.items()}
        for row, ss in all_series:
            for s in ss:
                label, colour = s["label"], s["colour"]
                if not label:
                    continue
                if label in style:
                    want = style[label]
                    if delta_e(colour, want["colour"]) >= 3:
                        add("E", row["name"], f"{quote(label, 34)} is {to_hex(want['colour'])} in the style table, drawn {colour}")
                    for key, got in (("line", s["style"]), ("marker", s["marker"])):
                        if s["line2d"] and want.get(key) and _norm(want[key]) != _norm(got):
                            add("W", row["name"], f"{quote(label, 34)}: {key} '{want[key]}' in the style table, drawn with '{got}'")
                elif not neutral(colour):
                    owner = next((k for c, k in listed.items() if delta_e(c, colour) < 3), None)
                    if s.get("implied"):
                        if not owner:
                            add("N", row["name"], f"a single curve in {colour}, which the style table does not list: "
                                                  "draw it in black, or add a row that says what the colour means")
                    elif owner:
                        add("E", row["name"], f"{colour} is the colour of {quote(owner, 34)} in the style table, used here for {quote(label, 34)}")
                    else:
                        add("N", row["name"], f"{quote(label, 34)} ({colour}) is not in the style table: add a row")
    for it in texts:                                    # lettering too pale to read
        row = it["row"]
        if row is not None and it["kind"] in ("note", "panel", "legend") and \
                any(_is_field(a) for a in list(row["ax"].images) + list(row["ax"].collections)):
            continue                                    # it may sit on an image: not judged
        try:
            ink = to_rgba(it["t"].get_color())
        except (ValueError, TypeError):
            continue
        bg = fig.get_facecolor()
        if row is not None and it["kind"] in ("note", "legend") and _inside(it["box"], row["box"]) and to_rgba(row["ax"].get_facecolor())[3]:
            bg = row["ax"].get_facecolor()
        if ink[3] and contrast(ink[:3], bg) < 3:
            add("W", where(row), f"{named(it)} is set in {to_hex(ink[:3])}, contrast {contrast(ink[:3], bg):.1f} against its background: "
                                 "under 3, hard to read")

    maps = [m for row in table if row["kind"] != "colorbar" for m in _mappables(row)]
    bars = {}
    for row in table:
        cb = getattr(row["ax"], "_colorbar", None)
        if cb is not None:
            bars[id(cb.mappable)] = _plain(cb.ax.get_ylabel() or cb.ax.get_xlabel() or (cb.ax.get_title() or ""))
    by_map = defaultdict(set)
    limits = defaultdict(set)
    for m in maps:
        name, base = m["cmap"], m["cmap"].lower().removesuffix("_r")
        w = where(m["row"])
        if base in RAINBOW:
            add("W", w, f"colour map '{name}': rainbow maps are not uniform to the eye and fail for colour-vision deficiency; "
                        "use a uniform map (viridis, cividis, batlow), or a cyclic one for an angle")
        span = (m["vmax"] - m["vmin"]) or 1.0
        if base in DIVERGING and m["norm"] not in ("TwoSlopeNorm", "CenteredNorm") and abs(m["vmax"] + m["vmin"]) > 0.02 * abs(span):
            add("W", w, f"diverging map '{name}' with limits {m['vmin']:.3g} to {m['vmax']:.3g}: the neutral colour is not at zero. "
                        "Centre the limits on the meaningful zero")
        if base not in DIVERGING and base not in RAINBOW and m["lo"] < 0 < m["hi"] and min(-m["lo"], m["hi"]) > 0.05 * (m["hi"] - m["lo"]):
            add("N", w, f"signed data on the sequential map '{name}': zero has no colour of its own; a diverging map shows the sign")
        if id(m["m"]) not in bars:
            if not any(id(o["m"]) in bars and o["cmap"] == m["cmap"] and (o["vmin"], o["vmax"]) == (m["vmin"], m["vmax"]) for o in maps):
                add("N", w, "colour-mapped data without a colour bar that shares its map and limits")
        elif not bars[id(m["m"])]:
            add("W", w, "the colour bar has no label: name the quantity and its unit")
        else:
            by_map[base].add(bars[id(m["m"])])
            limits[bars[id(m["m"])]].add((round(float(m["vmin"]), 6), round(float(m["vmax"]), 6)))
    for base, quantities in by_map.items():
        if len(quantities) > 1:
            add("E", "figure", f"one colour map ('{base}'), {len(quantities)} quantities: " + ", ".join(quote(q) for q in sorted(quantities)))
    for quantity, lims in limits.items():
        if len(lims) > 1:
            add("N", "figure", f"{quote(quantity)} is mapped with different limits in different panels: the same colour then means different values")

    # ----- axes: labels, units, typeface, ticks -----
    unit_forms, dirs = defaultdict(list), defaultdict(list)
    for row in table:
        ax = row["ax"]
        if row["kind"] in ("art", "3d") or not ax.axison:
            continue
        for axis, name in ((ax.xaxis, "x"), (ax.yaxis, "y")):
            if not axis.get_visible() or row["kind"] == "colorbar" and not axis.get_label().get_text() and not [
                    it for it in texts if it["row"] is row and it["kind"] == "tick" and it.get("axis") == name]:
                continue
            shown = [it for it in texts if it["row"] is row and it["kind"] == "tick" and it.get("axis") == name]
            label = axis.get_label().get_text().strip() if axis.get_label().get_visible() else ""
            rect = ax.name == "rectilinear"
            if shown and not label and rect and row["kind"] != "colorbar" and any(_is_number(it["text"]) for it in shown):
                group = ax.get_shared_x_axes() if name == "x" else ax.get_shared_y_axes()
                mates = [a for a in group.get_siblings(ax) if a is not ax]
                if not any((a.xaxis if name == "x" else a.yaxis).get_label().get_text().strip() for a in mates) and \
                        not getattr(fig, "_supxlabel" if name == "x" else "_supylabel", None):
                    add("W", where(row), f"the {name} axis has numbers but no label")
            if label:
                core = _plain(label)
                if re.search(r"\([^()]+\)\s*$", core):
                    unit_forms["(unit)"].append(row["name"])
                elif re.search(r"\[[^\[\]]+\]\s*$", core):
                    unit_forms["[unit]"].append(row["name"])
                elif re.search(r"\s/\s*\S+\s*$", core) and "$" not in label.split("/")[-1][:1]:
                    unit_forms["quantity / unit"].append(row["name"])
                if "$" not in label and re.match(r"^[A-Za-zΑ-ω](?:_\{?\w+\}?)?\s*(?:[\(\[/]|$)", label):
                    add("W", where(row), f"axis label {quote(label)}: the symbol is upright; set symbols in math mode so that they "
                                         "match the text (italic for a variable)")
                spelled = re.search(rf"(?<![A-Za-z\\])({GREEK})(?![A-Za-z])", re.sub(r"\$[^$]*\$", "", label), re.I)
                if spelled:
                    add("W", where(row), f"axis label {quote(label)}: '{spelled.group(1)}' is spelled out; use the symbol, "
                                         "as in the text and the equations")
                for seg in re.findall(r"\$([^$]*)\$", label):
                    inner = re.search(r"(?:\s|\\[, ]|~)[\(\[]\s*([A-Za-z][A-Za-z/ ^\-0-9.{}]*)[\)\]]\s*$", seg)
                    if inner and not re.search(r"\\(?:mathrm|text|rm|mathsf)", seg) and len(inner.group(1)) <= 12:
                        add("W", where(row), f"axis label {quote(label)}: the unit sits inside math mode and comes out italic; "
                                             "units are upright")
            if len(shown) > 7 and rect and row["kind"] != "colorbar" and axis.get_scale() == "linear":
                add("N", where(row), f"{len(shown)} tick labels on the {name} axis: four to six are enough to read a value")
            if 0 < len(shown) < 2 and rect and axis.get_scale() == "linear":
                add("W", where(row), f"only {len(shown)} tick label on the {name} axis: a scale needs at least two")
            off = axis.get_offset_text()
            if off.get_visible() and off.get_text().strip() and shown:
                add("W", where(row), f"the {name} axis carries a floating multiplier ({off.get_text().strip()}): fold it into the unit "
                                     "(nm, mT) or into the axis label")
            nums = [it["text"].replace("−", "-").replace("$", "") for it in shown]
            if any(re.fullmatch(r"-?\.\d+", n) for n in nums):
                add("N", where(row), f"tick labels on the {name} axis start with a decimal point: write 0.2, not .2")
            decs = {len(n.split(".")[1]) if "." in n else 0 for n in nums if re.fullmatch(r"-?\d+(?:\.\d+)?", n)}
            if len(decs) > 1:
                add("N", where(row), f"tick labels on the {name} axis have different numbers of decimals: {', '.join(nums[:6])}")
            if any(re.fullmatch(r"-?\d+\.\d{4,}", n) for n in nums):
                add("N", where(row), f"tick labels on the {name} axis have four or more decimals: rescale the unit or round the ticks")
            ticks = axis.get_major_ticks()
            if ticks and shown and row["kind"] == "main":
                dirs[_tickdir(ticks[0])].append(row["name"])
    if len(unit_forms) > 1:
        add("W", "figure", "units are written in more than one way: " + "; ".join(f"{k} in {', '.join(sorted(set(v)))}" for k, v in unit_forms.items()))
    if len(dirs) > 1:
        add("W", "figure", "ticks point " + " and ".join(f"'{k}' in {', '.join(sorted(set(v)))}" for k, v in dirs.items())
            + ": use one direction in the whole paper")
    for it in texts:
        if it["kind"] == "legend" and "$" not in it["text"] and re.match(r"^[A-Za-zΑ-ω](?:_\w+)?\s*=", it["text"]):
            add("W", where(it["row"]), f"legend entry {quote(it['text'])}: the symbol is upright; set it in math mode")

    # ----- legends -----
    entries = {}
    for row in table:
        leg = row["ax"].get_legend()
        if leg is None or not leg.get_visible():
            continue
        names = tuple(t.get_text() for t in leg.get_texts())
        entries[row["name"]] = names
        if len(names) > 6:
            add("N", where(row), f"a legend of {len(names)} entries: label the curves directly, or split the panel")
        if len(names) == 1:
            add("N", where(row), f"a legend with one entry ({quote(names[0])}): say it in the caption or on the axis")
        if leg.get_frame_on() and leg.get_frame().get_alpha() not in (0, 0.0):
            add("N", where(row), "the legend has a frame: a frame is one more box to read; drop it unless it sits on grid lines")
    same = defaultdict(list)
    for name, names in entries.items():
        same[names].append(name)
    for names, where_ in same.items():
        if len(where_) > 1 and len(names) > 1:
            add("N", "figure", f"the same legend is repeated in {', '.join(where_)}: show it once")

    # ----- marks and chart types -----
    for row in table:
        ax = row["ax"]
        if row["kind"] == "3d":
            add("N", where(row), "a three-dimensional plot: values cannot be read from it; consider a map with line cuts")
            continue
        if row["kind"] == "twin":
            add("N", where(row), "two y axes on one panel: where the two curves cross means nothing, and the reader must be told "
                                 "which curve reads on which axis; two stacked panels with a shared x axis avoid both")
        if any(isinstance(q, Wedge) for q in ax.patches):
            add("N", where(row), "a pie chart: angles are read poorly; bars or points on a common axis are read better")
        if row["kind"] in ("art", "colorbar"):
            continue
        thin = [ln for ln in ax.lines if ln.get_visible() and ln.get_linestyle() not in NONE and 0 < ln.get_linewidth() < min_line - 1e-6]
        if thin:
            add("W", where(row), f"{len(thin)} line(s) thinner than {min_line:g} pt ({min(ln.get_linewidth() for ln in thin):g} pt): "
                                 "hairlines break up in print")
        tiny = [ln for ln in ax.lines if ln.get_visible() and ln.get_marker() not in NONE and 0 < ln.get_markersize() < 2.8]
        if tiny:
            add("N", where(row), f"markers of {min(ln.get_markersize() for ln in tiny):.1f} pt: under 1 mm they are hard to see")
        for c in ax.containers:
            if isinstance(c, BarContainer) and len(c.patches):
                upright = getattr(c, "orientation", "vertical") == "vertical"
                lo, hi = ax.get_ylim() if upright else ax.get_xlim()
                scale = ax.get_yscale() if upright else ax.get_xscale()
                if scale == "linear" and min(lo, hi) > 0:
                    add("W", where(row), "bars on an axis that does not start at zero: the bar lengths misstate the ratios")
                elif scale == "log":
                    add("N", where(row), "bars on a logarithmic axis: a bar has no natural base there; use points")
                break

    return {"findings": found, "palette": palette, "size": (w_mm, h_mm), "sizes": sizes, "fonts": fonts,
            "panels": [r["name"] for r in ordered], "maps": [(where(m["row"]), m["cmap"], bars.get(id(m["m"]), "")) for m in maps]}


# ---------- reporting, running scripts ----------

def show(result, name="figure", stream=sys.stdout):
    w, h = result["size"]
    print(f"\n{name}", file=stream)
    print(f"  {w:.1f} x {h:.1f} mm | text {', '.join(f'{s:g}' for s in result['sizes']) or 'none'} pt | "
          f"{', '.join(result['fonts']) or 'no text'} | panels: {', '.join(result['panels']) or 'none'}", file=stream)
    for level, title in (("E", "ERRORS"), ("W", "WARNINGS"), ("N", "NOTES")):
        rows = [f for f in result["findings"] if f[0] == level]
        if rows:
            print(f"  {title} ({len(rows)})", file=stream)
            for _, place, msg in rows:
                print(f"    {place}: {msg}", file=stream)
    if result["palette"]:
        seen = []
        for panel, label, colour in result["palette"]:
            if (label, colour) not in seen:
                seen.append((label, colour))
        print("  colours: " + "; ".join(f"{label} {colour}" for label, colour in seen[:16])
              + (" …" if len(seen) > 16 else ""), file=stream)
    if result["maps"]:
        print("  colour maps: " + "; ".join(sorted({f"{cmap} for {q or 'an unlabelled quantity'}" for _, cmap, q in result["maps"]})), file=stream)
    return sum(1 for f in result["findings"] if f[0] == "E")


def read_style(path):
    """{label on figure: {'colour', 'line', 'marker'}} from the Encoding table of figstyle.md."""
    out, header = {}, None
    for raw in open(path, encoding="utf-8"):
        if not raw.lstrip().startswith("|"):
            header = None if not raw.strip() else header
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if header is None:
            if "meaning" in low and any(c.startswith(("colour", "color")) for c in low):
                header = low
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        r = dict(zip(header, cells))
        m = re.search(r"#[0-9A-Fa-f]{6}", next((v for k, v in r.items() if k.startswith(("colour", "color"))), ""))
        if m:
            label = next((v for k, v in r.items() if k.startswith("label")), "") or r.get("meaning", "")
            out[_plain(label.strip("`"))] = {"colour": m.group(0), "line": r.get("line", ""), "marker": r.get("marker", "")}
    return out


def run_script(path, opts):
    """Run one plotting script; return [(name, result)] for every figure it saved or left open."""
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    saves, order, results = defaultdict(list), [], {}
    original = Figure.savefig

    def safe_check(fig):
        try:
            return check(fig, saved=saves[id(fig)], **opts)
        except Exception as exc:                         # a fault of the check must not look like a fault of the figure
            w, h = (v * 25.4 for v in fig.get_size_inches())
            return {"findings": [("E", "figure", f"the check itself failed ({type(exc).__name__}: {exc}); report this")],
                    "palette": [], "size": (w, h), "sizes": [], "fonts": [], "panels": [], "maps": []}

    def savefig(self, fname, *args, **kw):
        out = original(self, fname, *args, **kw)
        if id(self) not in saves:
            order.append(self)
        saves[id(self)].append({"name": fname, "dpi": kw.get("dpi"),
                                "tight": kw.get("bbox_inches", matplotlib.rcParams["savefig.bbox"]) == "tight"})
        results[id(self)] = safe_check(self)             # checked as saved: the script may clear or close it afterwards
        return out

    keep = (matplotlib.use, plt.show)
    Figure.savefig, plt.show = savefig, (lambda *a, **k: None)
    matplotlib.use = lambda *a, **k: None                # the script must not switch to a screen backend
    here, argv = os.getcwd(), sys.argv
    folder = os.path.dirname(os.path.abspath(path))
    try:
        os.chdir(folder)
        sys.argv = [os.path.basename(path)]
        sys.path.insert(0, folder)
        runpy.run_path(os.path.basename(path), run_name="__main__")
        for num in plt.get_fignums():                    # figures left open and never saved
            fig = plt.figure(num)
            if id(fig) not in saves:
                order.append(fig)
                results[id(fig)] = safe_check(fig)
        out = []
        for fig in order:
            names = ", ".join(_name(s["name"]) for s in saves[id(fig)]) or "a figure that is never saved"
            out.append((f"{os.path.basename(path)} -> {names}", results[id(fig)]))
        return out
    finally:
        Figure.savefig = original
        matplotlib.use, plt.show = keep
        os.chdir(here)
        sys.argv = argv
        if folder in sys.path:
            sys.path.remove(folder)
        plt.close("all")


def across(everything, style=None):
    """One colour with several meanings, or one meaning in several colours, in different figures of the paper."""
    style = style or {}
    by_colour, by_label = defaultdict(lambda: defaultdict(set)), defaultdict(lambda: defaultdict(set))
    for name, result in everything:
        fig_name = name.split(" -> ")[-1]
        for _, label, colour in result["palette"]:
            by_label[label][colour].add(fig_name)
            if not neutral(colour) and not label.startswith("y axis:"):
                by_colour[colour][label].add(fig_name)
    lines = []
    for colour, labels in sorted(by_colour.items()):
        names = sorted(labels)
        declared = all(a in style and b in style and delta_e(style[a]["colour"], style[b]["colour"]) < 3
                       for i, a in enumerate(names) for b in names[i + 1:])
        if len(labels) > 1 and len({f for group in labels.values() for f in group}) > 1 and not declared:
            lines.append(f"    {colour} stands for " + "; ".join(f"'{lbl}' in {', '.join(sorted(labels[lbl]))}" for lbl in names))
    for label, colours in sorted(by_label.items()):
        if len(colours) > 1 and len({f for group in colours.values() for f in group}) > 1:
            lines.append(f"    '{label}' is drawn in " + "; ".join(f"{c} in {', '.join(sorted(f))}" for c, f in sorted(colours.items())))
    return lines


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Check matplotlib figures against the rules of parts/figures.md.")
    ap.add_argument("scripts", nargs="+", help="plotting scripts; each is run, and every figure it makes is checked")
    ap.add_argument("--width-mm", nargs="*", type=float, default=[], help="final widths the venue allows, in mm")
    ap.add_argument("--min-font", type=float, default=6.0, help="smallest text in points at final size (default 6)")
    ap.add_argument("--max-font", type=float, help="largest text in points, where the venue sets one")
    ap.add_argument("--min-height-mm", type=float, help="smallest capital-letter height in mm, where the venue states lettering height")
    ap.add_argument("--max-height-mm", type=float, help="largest figure height in mm, where the venue sets one")
    ap.add_argument("--min-line", type=float, default=0.5, help="thinnest line in points at final size (default 0.5)")
    ap.add_argument("--style", help="figstyle.md: the paper's table of meanings and colours")
    args = ap.parse_args()
    missing = [p for p in args.scripts + ([args.style] if args.style else []) if not os.path.isfile(p)]
    if missing:
        sys.exit("fig_lint: no such file: " + ", ".join(missing))
    matplotlib.use("Agg", force=True)
    style = read_style(args.style) if args.style else None
    opts = dict(widths_mm=args.width_mm, min_font=args.min_font, max_font=args.max_font, min_height_mm=args.min_height_mm,
                max_height_mm=args.max_height_mm, min_line=args.min_line, style=style)
    errors, everything = 0, []
    for path in args.scripts:
        try:
            got = run_script(path, opts)
        except SystemExit:
            raise
        except BaseException as exc:                     # the script itself failed
            print(f"\n{path}\n  ERRORS (1)\n    the script did not run: {type(exc).__name__}: {exc}")
            errors += 1
            continue
        if not got:
            print(f"\n{path}\n  no figure was made")
        for name, result in got:
            errors += show(result, name)
            everything.append((name, result))
    lines = across(everything, style)
    if lines:
        print(f"\nACROSS FIGURES ({len(lines)}): within a paper one colour should keep one meaning\n" + "\n".join(lines))
    print(f"\n{errors} error(s) in {len(everything)} figure(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
