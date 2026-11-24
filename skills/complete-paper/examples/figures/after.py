"""Example figure (invented data): a schematic and two data panels built with the skill's helpers."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import fig_style as fs          # noqa: E402
import schematic3d as s3        # noqa: E402

here = Path(__file__).resolve().parent
fs.use(base=9, small=8)
enc = fs.load(here / "figstyle.md")
fig, axs = fs.figure(178, 56, ncols=3, width_ratios=[1.25, 1, 1])

# (a) device and the definition of the tilt angle
film, metal, sub, pad = (enc[k]["color"] for k in ("Mn3Sn film", "heavy metal", "substrate", "contact"))
sc = s3.Scene(azim=-58, elev=24)
sc.box((0, 0, 0), (12, 7, 0.8), sub)
sc.box((1.8, 2.3, 0.8), (8.4, 2.4, 0.35), metal)
sc.box((1.8, 2.3, 1.15), (8.4, 2.4, 0.6), film, label="Mn3Sn")
sc.box((0.4, 1.7, 0.8), (1.4, 3.6, 0.95), pad).box((10.2, 1.7, 0.8), (1.4, 3.6, 0.95), pad)
theta = np.radians(30)
tilt, base = np.array([np.sin(theta), 0, np.cos(theta)]), np.array([6.0, 3.5, 1.75])
yhat = np.array([0, 1.0, 0])
sc.polygon([base - 0.9 * yhat, base + 0.9 * yhat, base + 0.9 * yhat + 2.2 * tilt, base - 0.9 * yhat + 2.2 * tilt],
           enc["tilt 45 deg"]["color"], alpha=0.55)
sc.line([base, base + [0, 0, 2.6]], style=(0, (3, 2)))
sc.arc(base, (0, 0, 1), tilt, 1.9)
sc.note(r"$\theta$", at=base + 2.7 * (np.array([0, 0, 1.0]) + tilt) / np.linalg.norm(np.array([0, 0, 1.0]) + tilt))
sc.arrow((6.5, -1.3, 0), (10.5, -1.3, 0), label=r"$j$", offset=(0, -7))     # current direction, beside the device
sc.note(r"Mn$_3$Sn", at=(8.6, 3.5, 1.75), offset=(10, 24))
sc.note("W", at=(7.4, 2.3, 0.97), offset=(-46, -26))
sc.note("contact", at=(1.1, 3.5, 1.75), offset=(-12, 20))
sc.triad((-0.2, -3.6, 0), 1.7)
sc.draw(axs[0])

# (b) octupole component against time, one curve per tilt angle
t = np.linspace(0, 1, 400)
for name, t0 in (("tilt 0 deg", None), ("tilt 15 deg", 0.60), ("tilt 30 deg", 0.40), ("tilt 45 deg", 0.22)):
    mz = 1 - 0.04 * (1 - np.exp(-t / 0.05)) if t0 is None else -np.tanh((t - t0) / 0.035)
    line, = axs[1].plot(t, mz, **enc[name])
    if t0 is None:
        fs.direct_label(axs[1], line, r"$\theta = 0^\circ$", x=0.80, dx=0, dy=-7, ha="center")
    else:
        fs.direct_label(axs[1], line, enc[name]["label"], x=t0, dx=4)
axs[1].set(xlabel=r"$t$ (ns)", ylabel=r"$m_z$", xlim=(0, 1), ylim=(-1.15, 1.15), xticks=[0, 0.5, 1], yticks=[-1, 0, 1])

# (c) threshold current against tilt angle: simulation and model
ang = np.arange(5, 50, 5)
scatter = np.array([1.03, 0.98, 1.01, 0.99, 1.02, 0.985, 1.0, 1.01, 0.995])
fine = np.linspace(4.2, 46, 200)
axs[2].plot(fine, 0.6 / np.sin(np.radians(fine)), **enc["analytical model"])
axs[2].plot(ang, scatter * 0.6 / np.sin(np.radians(ang)), **enc["simulation"], markerfacecolor="white")
axs[2].set(xlabel=r"$\theta$ (deg)", ylabel=r"$j_{\mathrm{c}}$ ($10^{11}$ A/m$^2$)", xlim=(0, 50), ylim=(0, 8.5),
           xticks=[0, 15, 30, 45], yticks=[0, 4, 8])
axs[2].legend(loc="upper right")

fs.panel_labels(fig, axs, fmt="({})")
fs.save(fig, here / "after.pdf")
fs.save(fig, here / "after.png", dpi=300)
