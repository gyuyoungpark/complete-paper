# Test fixture for the figcode check. Not meant to run.
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1])
ax.set_title("Stability window")                        # planted: title
ax.annotate("peak", xy=(0.5, 0.5), xytext=(0.7, 0.7),
            arrowprops={"arrowstyle": "->"})            # planted: annotation
ax.text(-0.15, 1.02, "a", transform=ax.transAxes)        # panel letter: allowed, reported as NICE
