"""The data of after.py drawn as a first draft often is (invented data). Run fig_lint.py on both."""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcdefaults()
fig = plt.figure(figsize=(12, 3.6))
ax1 = fig.add_axes([0.05, 0.14, 0.26, 0.72])
ax2 = fig.add_axes([0.385, 0.15, 0.26, 0.72])
ax3 = fig.add_axes([0.72, 0.14, 0.26, 0.70])

theta, j = np.meshgrid(np.linspace(1, 45, 60), np.linspace(0, 8e11, 60))
final = np.tanh(4e-11 * (0.6e11 / np.sin(np.radians(theta)) - j))
im = ax1.imshow(final, origin="lower", extent=[1, 45, 0, 8e11], aspect="auto", cmap="jet", vmin=-0.6, vmax=1)
fig.colorbar(im, ax=ax1)
ax1.set_title("Phase diagram")
ax1.set_xlabel("theta [deg]")
ax1.set_ylabel("j [A/m^2]")

t = np.linspace(0, 1, 400)
for angle, t0 in ((0, None), (15, 0.60), (30, 0.40), (45, 0.22)):
    mz = 1 - 0.04 * (1 - np.exp(-t / 0.05)) if t0 is None else -np.tanh((t - t0) / 0.035)
    ax2.plot(t, mz, label=f"theta = {angle} deg")
ax2.legend(loc="center")
ax2.set_title("Switching dynamics")
ax2.set_xlabel("t (ns)")
ax2.set_ylabel("$m_z$")
ax2.set_xticks(np.linspace(0, 1, 11))

angles = np.arange(5, 50, 5)
fine = np.linspace(4.2, 46, 200)
ax3.plot(fine, 0.6e11 / np.sin(np.radians(fine)), label="model")
ax3.plot(angles, 0.6e11 / np.sin(np.radians(angles)), "o", markersize=2, label="simulation")
ax3.legend()
ax3.set_title("Threshold current")
ax3.set_xlabel("theta [deg]")
ax3.set_ylabel("$j_c (A/m^2)$")

fig.text(0.01, 0.95, "a)", fontsize=14, fontweight="bold")
fig.text(0.345, 0.93, "b)", fontsize=14, fontweight="bold")
fig.text(0.685, 0.95, "c)", fontsize=14)
fig.suptitle("Field-free switching of Mn3Sn")
fig.savefig(Path(__file__).resolve().parent / "before.png", dpi=100, bbox_inches="tight")
