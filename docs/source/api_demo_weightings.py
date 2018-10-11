#! /usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import viridis as cmap
import galore
import galore.plot

vasprun = 'test/SnO2/vasprun.xml.gz'
xmin, xmax = (-10, 4)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

weightings = ('He2', 'Alka', 'Yeh_HAXPES')

for i, weighting in enumerate(weightings):

    plotting_data = galore.process_pdos(input=[vasprun],
                                        gaussian=0.3, lorentzian=0.2,
                                        xmin=xmin, xmax=xmax,
                                        weighting=weighting)
    galore.plot.plot_pdos(plotting_data, ax=ax, show_orbitals=False,
                          units='eV', xmin=-xmin, xmax=-xmax,
                          flipx=True)

    line = ax.lines[-1]
    line.set_label(weighting)
    line.set_color(cmap(i / len(weightings)))

    ymax = max(line.get_ydata())
    line.set_data(line.get_xdata(), line.get_ydata() / ymax)

ax.set_ylim((0, 1.2))
legend = ax.legend(loc='best')
legend.set_title('Weighting')
plt.show()
