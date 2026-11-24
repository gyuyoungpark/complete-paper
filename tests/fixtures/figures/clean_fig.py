# Test fixture for fig_lint.py: one-column figure drawn with fig_style; the lint should find no error.
# fig_style is importable because fig_lint.py runs from the skill's scripts folder.
import numpy as np

import fig_style as fs

fs.use(base=9, small=8)
enc = fs.load("figstyle.md")
fig, axs = fs.figure(86, 40, ncols=2)
t = np.linspace(0, 1, 200)
for key, t0 in (("tilt 15 deg", 0.6), ("tilt 45 deg", 0.3)):
    line, = axs[0].plot(t, -np.tanh((t - t0) / 0.03), **enc[key])
    fs.direct_label(axs[0], line, x=t0)          # labels on the curves, not a legend
axs[0].set_xlabel(r"$t$ (ns)")
axs[0].set_ylabel(r"$m_z$")
axs[0].set_xticks([0, 0.5, 1])
axs[0].set_yticks([-1, 0, 1])
axs[0].set_ylim(-1.3, 1.3)
theta = np.array([10, 20, 30, 40])
axs[1].plot(theta, 4 / np.sin(np.radians(theta)), **enc["simulation"])
axs[1].set_xlabel(r"$\theta$ (deg)")
axs[1].set_ylabel(r"$j_{\mathrm{c}}$ ($10^{11}$ A/m$^2$)")
axs[1].set_xlim(0, 50)
axs[1].set_ylim(0, 30)
fs.panel_labels(fig, axs, fmt="({})")
