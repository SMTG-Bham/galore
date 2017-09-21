#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import viridis as cmap
import galore
import galore.plot

vasprun = 'test/MgO/vasprun.xml.gz'
xmin, xmax = (-6, 15)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

widths = np.arange(0, 2.01, 0.4)
widths[0] = 0.05 # Use a finite width in smallest case

for g in widths:

    x_values, broadened_data = galore.process_1d_data(input=vasprun,
                                                      gaussian=g,
                                                      xmin=xmin, xmax=xmax)

    broadened_data /= g # Scale values by broadening width to conserve area

    galore.plot.plot_tdos(x_values, broadened_data, ax=ax)
    line = ax.lines[-1]
    line.set_label("{0:2.2f}".format(g))
    line.set_color(cmap(g / max(widths)))

ax.set_ylim(0, 1000)
ax.set_yticklabels([''])
legend = ax.legend(loc='best')
legend.set_title('Gaussian $\gamma$')
plt.show()
