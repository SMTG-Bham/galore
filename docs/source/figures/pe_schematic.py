#! /usr/bin/env python3

import matplotlib.pyplot as plt
import galore
import galore.formats
import galore.plot


fig = plt.figure(figsize=(6.2, 2))
xlim = (-6, 2)
new_ylim = (0, 6e-6)
final_ylim = (0, 1.5e-4)

weighting = 'haxpes'

# Total DOS
ax1 = fig.add_subplot(1, 5, 1)

tdos_data = galore.formats.read_vasprun_totaldos('test/MgO/vasprun.xml.gz')
ax1.plot(tdos_data[:, 0], tdos_data[:, 1], 'k-')
ax1.set_title("Total DOS")
ax1.set_xlim(xlim)

# PDOS
ax2 = fig.add_subplot(1, 5, 2, sharey=ax1)
pdos_data = galore.formats.read_vasprun_pdos('test/MgO/vasprun.xml.gz')
galore.plot.plot_pdos(pdos_data, ax=ax2, total=False)
ax2.set_title("Orbitals")
ax2.set_xlim(xlim)
ax2.legend().remove()

## Build a nice key of line colors
line_colors = {line.get_label(): line.get_color() for line in ax2.lines}
## Set solid lines
for line in ax2.lines:
    line.set_linestyle('-')

# Weighted PDOS
ax3 = fig.add_subplot(1, 5, 3)
weighted_data = galore.apply_orbital_weights(pdos_data,
                                             galore.get_cross_sections(
                                                 weighting))
galore.plot.plot_pdos(weighted_data, ax=ax3, total=False)
ax3.set_title("Weight by \n cross-section")
ax3.set_xlim(xlim)
ax3.legend().remove()

## Fix consistent colors
for line in ax3.lines:
    line.set_color(line_colors[line.get_label()])
    line.set_linestyle('-')

# Summed PDOS
ax4 = fig.add_subplot(1, 5, 4, sharey=ax3)
galore.plot.plot_pdos(weighted_data, ax=ax4, total=True, show_orbitals=False)
ax4.set_title("Sum")
ax4.set_xlim(xlim)
ax4.set_ylim(new_ylim)
ax4.legend().remove()

# Broadened output
ax5 = fig.add_subplot(1, 5, 5)
broadened_data = galore.process_pdos(input='test/MgO/vasprun.xml.gz',
                                     gaussian=0.5,
                                     weighting=weighting)

galore.plot.plot_pdos(broadened_data, ax=ax5, total=True, show_orbitals=False)
ax5.set_title("Broaden")
ax5.set_xlim(xlim)
ax5.set_ylim(final_ylim)
ax5.legend().remove()

fig.subplots_adjust(left=0.03, right=0.98, top=0.78)
fig.savefig('docs/source/figures/pe_schematic.pdf')
