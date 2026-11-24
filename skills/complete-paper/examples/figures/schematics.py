"""Three device drawings made with schematic3d (invented devices): one view, one set of colours, one light."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import fig_style as fs          # noqa: E402
import schematic3d as s3        # noqa: E402

here = Path(__file__).resolve().parent
fs.use(base=9, small=8)
fig, axs = fs.figure(178, 58, ncols=3, width_ratios=[1.3, 1, 0.8])
enc = fs.load(here / "figstyle.md")             # materials take their colours from the paper's table
substrate, contact, film, metal, barrier, free = (enc[k]["color"] for k in (
    "substrate", "contact", "Mn3Sn film", "heavy metal", "barrier", "free layer"))
VIEW = dict(azim=-58, elev=24)                 # the paper's view: every three-dimensional drawing uses it

# (a) a Hall bar: one prism, so that the cross has one outline and no seams
sc = s3.Scene(**VIEW)
sc.box((0, 0, 0), (14, 9, 0.6), substrate)
sc.prism(s3.hall_bar(11, 1.2, arms=(3.5, 7.5), arm_length=2.0, arm_width=0.7, origin=(1.5, 3.9)), 0.6, 0.3, film, label="Mn3Sn")
for x, y in ((0.3, 3.6), (12.5, 3.6)):
    sc.box((x, y, 0.6), (1.2, 1.8, 0.5), contact)
for x in (4.25, 8.25):
    for y in (0.5, 7.1):
        sc.box((x, y, 0.6), (1.5, 1.4, 0.5), contact)
sc.arrow((2.3, 4.5, 1.3), (5.4, 4.5, 1.3), label=r"$I$", offset=(4, 9))
sc.arrow((11.6, 7.2, 0.6), (11.6, 7.2, 3.4), label=r"$\mathbf{H}$", offset=(9, 2))
sc.triad((-0.6, -4.2, 0), 1.8)
sc.draw(axs[0])

# (b) a pillar on a bottom electrode: cylinders stacked along z
layers = [(0.5, metal, "W"), (0.45, film, "Mn3Sn"), (0.2, barrier, "MgO"), (0.45, free, "CoFeB")]
sc = s3.Scene(**VIEW)
sc.box((0, 0, 0), (8, 5, 0.5), substrate)
z = 0.5
for height, colour, name in layers:
    sc.cylinder((4, 2.5, z), 1.3, height, colour, label=name)
    z += height
sc.arrow((4, 2.5, z + 0.15), (4, 2.5, z + 1.6), label=r"$\mathbf{m}$", offset=(9, 0))
sc.draw(axs[1])

# (c) the same stack as a flat cross-section: the clearest drawing when only the order of layers matters
sc = s3.Scene(azim=-90, elev=0)
sc.stack((0, 0, 0), (3.2, 1), [(0.7, substrate)] + [(1.6 * h, c, n) for h, c, n in layers])
z = 0.7
for height, colour, name in layers:
    label = {"Mn3Sn": r"Mn$_3$Sn"}.get(name, name)
    sc.note(label, at=(1.6, 0, z + 0.8 * height), offset=(0, 0))
    z += 1.6 * height
sc.note("substrate", at=(1.6, 0, 0.35))
sc.draw(axs[2])

fs.panel_labels(fig, axs, fmt="({})")
fs.save(fig, here / "schematics.pdf")
fs.save(fig, here / "schematics.png", dpi=300)
