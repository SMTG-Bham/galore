#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import viridis as cmap
import galore
import galore.plot

vasprun = 'test/MgO/vasprun.xml.gz'
xmin, xmax = (-4, 6)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for g in np.arange(0., 1.01, 0.2):

    x_values, broadened_data = galore.process_1d_data(input=vasprun,
                                                      gaussian=g)

    galore.plot.plot_tdos(x_values, broadened_data, ax=ax)
    line = ax.lines[-1]
    line.set_label("{0:2.1f}".format(g))
    line.set_color(cmap(g))

#fig.tight_layout()
legend = ax.legend(loc='best')
legend.set_title('Gaussian $\gamma$')
plt.show()
