# Test fixture for fig_lint.py. Planted: a figure far wider than any column, a figure title,
# a panel title, a rainbow map without a colour bar, one colour for two meanings, and a
# floating multiplier on an axis.
import matplotlib.pyplot as plt
import numpy as np

fig, axs = plt.subplots(1, 2, figsize=(12, 3))
fig.suptitle("Field-free switching")
axs[0].imshow(np.random.default_rng(0).random((20, 20)), cmap="jet")
x = np.linspace(0, 1, 50)
axs[1].plot(x, 1e11 * (1 + x), color="C0", label="model")
axs[1].plot(x, 1e11 * (1 + x ** 2), color="C0", label="theta = 0 deg")
axs[1].set_title("Threshold current")
axs[1].set_xlabel("x")
axs[1].legend()
