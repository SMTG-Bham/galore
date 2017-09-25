#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
plt.style.use("seaborn-colorblind")
import galore
import galore.plot

vasprun = './test/MgO/vasprun.xml.gz'
xmin, xmax = (-10, 2)

fig = plt.figure()

for i, l in enumerate(np.arange(0.05, 0.50, 0.05)):
    ax = fig.add_subplot(3, 3, i + 1)
    ax.set_title("$\gamma = {0:4.2f}$".format(l))
    plotting_data = galore.process_pdos(input=[vasprun], lorentzian=l,
                                        xmin=xmin, xmax=xmax)
    galore.plot.plot_pdos(plotting_data, ax=ax)
    ax.legend().set_visible(False)

fig.tight_layout()
plt.show()
