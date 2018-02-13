#! /usr/bin/env python3
import os
import matplotlib.pyplot as plt
import galore
import galore.formats
import galore.plot

from tempfile import mkstemp

fd, tmp = mkstemp(suffix='.txt', text=True)
os.close(fd)

sim_xvals = [10, 15, 19.5, 20, 20.5, 21]
sim_yvals = [12, 6, 3, 2, 1, 2]

galore.formats.write_txt(sim_xvals, sim_yvals, filename=tmp)

fig = plt.figure(figsize=(4,2))

ax1 = fig.add_subplot(1, 2, 1)
for x, y in zip(sim_xvals, sim_yvals):
    ax1.plot([x, x], [0, y], 'k-')

ax1.set_xticklabels([])
ax1.set_yticklabels([])
ax1.set_title("Ideal peaks")

x, y = galore.process_1d_data(input=tmp, gaussian=2)

ax2 = fig.add_subplot(1, 2, 2, sharey=ax1)
ax2.plot(x, y, 'k-')
ax2.set_ylim((0, None))
ax2.set_xticklabels([])
ax2.set_yticklabels([])

ax2.set_title("With broadening")

fig.savefig('docs/source/figures/ir_schematic.pdf')
