#! /usr/bin/env python3
###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Adam J. Jackson and Alex Ganose                                #
# at University College London (2018)                                         #
#                                                                             #
###############################################################################
#                                                                             #
# This file is part of Galore. Galore is free software: you can redistribute  #
# it and/or modify it under the terms of the GNU General Public License as    #
# published by the Free Software Foundation, either version 3 of the License, #
# or (at your option) any later version.  This program is distributed in the  #
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the     #
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    #
# See the GNU General Public License for more details.  You should have       #
# received a copy of the GNU General Public License along with this program.  #
# If not, see <http://www.gnu.org/licenses/>.                                 #
#                                                                             #
###############################################################################
from argparse import ArgumentParser
from itertools import cycle

import logging
import numpy as np
from matplotlib import pyplot as plt
plt.style.use('seaborn-colorblind')

from galore.cross_sections import get_cross_sections_scofield


def main():
    parser = get_parser()
    args = parser.parse_args()
    args = vars(args)
    run(**args)


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('--emin', type=float, default=1,
                        help="Minimum energy in keV")
    parser.add_argument('--emax', type=float, default=20,
                        help="Maximum energy in keV")
    parser.add_argument('--megabarn', action='store_true',
                        help="Set y-axis unit to megabarn/electron")
    parser.add_argument('--size', type=float, nargs=2, default=None,
                        help="Figure dimensions in cm")
    parser.add_argument('--output', '-o', type=str, default=None,
                        help="Output filename. If not given, plot to screen.")
    parser.add_argument('--fontsize', type=int, default=12,
                        help="Font size in pt")
    parser.add_argument(
        '--style', type=str, nargs='+', default=['seaborn-colorblind'],
        help='Plotting style: a sequence of matplotlib styles and paths to '
             'style files. The default palette is called "seaborn-colorblind".'
        )
    parser.add_argument('elements', type=str, nargs='+', help="""
        Space-separated symbols for elements in material.""")

    return parser


def run(elements, emin=1, emax=10, megabarn=False, size=None, output=None,
        fontsize=10, style=None):
    energies = np.linspace(emin, emax, 200)
    cross_sections = get_cross_sections_scofield(energies, elements)

    if style is not None:
        plt.style.use(style)

    if size is None:
        fig = plt.figure()
    else:
        size_inches = [float(x) / 2.54 for x in size]
        fig = plt.figure(figsize=size_inches)

    ax = fig.add_subplot(1, 1, 1)

    colors = cycle(('C0', 'C1', 'C2', 'C3', 'C4'))
    markers = cycle(('o', '^', 'D', 'x', '*'))

    if megabarn:
        unit = "Mb"
        conversion = 1E6
    else:
        unit = "barn"
        conversion = 1

    for element in elements:
        color, marker = next(colors), next(markers)
        linestyles = cycle((['-', '--', ':', '-.']))

        if 'warning' in cross_sections[element]:
            logging.warning("  {0}: {1}".format(
                element, cross_sections[element]['warning']))

        for orbital in 'spdf':
            if (orbital in cross_sections[element] and
                    cross_sections[element][orbital] is not None):
                ax.plot(energies,
                        cross_sections[element][orbital] / conversion,
                        color=color, linestyle=next(linestyles),
                        marker=marker, markevery=40,
                        label='{0}-{1}'.format(element, orbital),
                        markersize=5)

    ax.tick_params(labelsize=(fontsize - 2))
    ax.set_xlabel('Photon energy / keV', fontsize=fontsize)
    ylabel = ('Photoionization cross-section /'
              ' {} electron$^{{-1}}$'.format(unit))
    ax.set_ylabel(ylabel, fontsize=fontsize)
    ax.set_yscale('log')
    ax.legend(loc='lower right', fontsize=fontsize)
    fig.subplots_adjust(right=0.98, top=0.98)

    if output is None:
        plt.show()
    else:
        fig.savefig(output, bbox_inches='tight')


if __name__ == '__main__':
    main()
