#! /usr/bin/env python3
###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Adam J. Jackson and Alex Ganose                                #
# at University College London (2017)                                         #
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
import os
import argparse
from collections import OrderedDict
from json import load as json_load
import logging
import warnings

import numpy as np

import galore
import galore.formats
import galore.plot
from galore import auto_limits

try:
    import matplotlib
    has_matplotlib = True
except ImportError:
    has_matplotlib = False


def main():
    logging.basicConfig(filename='galore.log', level=logging.INFO)
    console = logging.StreamHandler()
    logging.getLogger().addHandler(console)

    warnings.filterwarnings("ignore", module="matplotlib")
    warnings.filterwarnings("ignore", module="pymatgen")

    parser = get_parser()
    args = parser.parse_args()
    args = vars(args)
    run(**args)


def run(**kwargs):
    if kwargs['sampling']:
        pass
    elif kwargs['units'] in ('cm', 'cm-1'):
        kwargs['sampling'] = 0.1
    elif kwargs['units'] in ('THz', 'thz'):
        kwargs['sampling'] = 1e-3
    elif kwargs['units'] in ('ev', 'eV'):
        kwargs['sampling'] = 1e-2
    else:
        kwargs['sampling'] = 1e-2

    if kwargs['pdos']:
        pdos_from_files(**kwargs)
    else:
        simple_dos_from_files(**kwargs)


def pdos_from_files(return_plt=False, **kwargs):
    """Read input data, process for PDOS before plotting and/or writing

    Args:
        return_plt (bool): If True, return the pyplot object instead of writing
            or displaying plot output.
        **kwargs: See command reference for full argument list

    """
    pdos_plotting_data = galore.process_pdos(**kwargs)

    # For plotting and writing, "None" means "write to screen"
    # while False means "do nothing"
    if kwargs['plot'] or kwargs['plot'] is None:
        if 'style' in kwargs and kwargs['style'] is not None:
            import matplotlib.pyplot
            matplotlib.pyplot.style.use(kwargs['style'])
        plt = galore.plot.plot_pdos(pdos_plotting_data,
                                    **kwargs)  # flipx is included in kwargs

        if kwargs['overlay'] is not None:
            plt = galore.plot.add_overlay(
                plt, kwargs['overlay'],
                overlay_offset=kwargs['overlay_offset'],
                overlay_scale=kwargs['overlay_scale'],
                overlay_style=kwargs['overlay_style'],
                overlay_label=kwargs['overlay_label'])
            plt.legend(loc='best')

        xlabel = galore.plot.guess_xlabel(units=kwargs['units'],
                                          flipx=kwargs['flipx'],
                                          energy_label=None)
        plt.xlabel(xlabel)

        if kwargs['ylabel'] is not None:
            plt.ylabel(kwargs['ylabel'])

        if return_plt:
            return plt
        elif kwargs['plot']:
            plt.savefig(kwargs['plot'])
        elif kwargs['plot'] is None:
            plt.show()

    if kwargs['csv'] or kwargs['csv'] is None:
        galore.formats.write_pdos(pdos_plotting_data,
                                  filename=kwargs['csv'],
                                  filetype='csv',
                                  flipx=kwargs['flipx'])

    if kwargs['txt'] or kwargs['txt'] is None:
        galore.formats.write_pdos(pdos_plotting_data,
                                  filename=kwargs['txt'],
                                  filetype='txt',
                                  flipx=kwargs['flipx'])


def simple_dos_from_files(return_plt=False, **kwargs):
    """Generate a spectrum or DOS over one data series

    kwargs['input'] can be a string or a list containing one string.
    In addition to main kwargs documented for CLI

    Args:
        return_plt (bool): If True, return the pyplot object instead of writing
            or displaying plot output.
        **kwargs: See command reference for full argument list

    """

    x_values, broadened_data = galore.process_1d_data(**kwargs)

    if not any(((kwargs['csv'] is None), (kwargs['txt'] is None),
                (kwargs['plot'] is None),
                kwargs['csv'], kwargs['txt'], kwargs['plot'])):
        print("No output selected. Please use at least one of the output "
              "options (CSV, txt, plotting). For usage information, run "
              "galore with -h argument.")

    if kwargs['plot'] or kwargs['plot'] is None:
        if not has_matplotlib:
            print("Can't plot, no Matplotlib")
        else:
            if 'style' in kwargs and kwargs['style'] is not None:
                import matplotlib.pyplot
                matplotlib.pyplot.style.use(kwargs['style'])
            plt = galore.plot.plot_tdos(x_values, broadened_data, **kwargs)
            if kwargs['ylabel'] is not None:
                plt.ylabel(kwargs['ylabel'])
            if return_plt:
                return plt
            elif kwargs['plot']:
                plt.savefig(kwargs['plot'])
            else:
                plt.show()

    if kwargs['csv'] is None:
        galore.formats.write_csv(x_values, broadened_data, filename=None)
    elif kwargs['csv']:
        galore.formats.write_csv(
            x_values, broadened_data, filename=kwargs['csv'])

    if kwargs['txt'] is None:
        galore.formats.write_txt(x_values, broadened_data, filename=None)
    elif kwargs['txt']:
        galore.formats.write_txt(
            x_values, broadened_data, filename=kwargs['txt'])


def get_parser():
    """Parse command-line arguments. Function is used to build the CLI docs."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input', type=str, default='vasprun.xml', nargs='+',
        help='Input data file. The supported formats are vasprun.xml (VASP '
             'output), *.gpw (GPAW output), *.csv (comma-delimited text) '
             'and *.txt (space-delimited text).')
    parser.add_argument(
        '-l',
        '--lorentzian',
        nargs='?',
        default=False,
        const=2,
        type=float,
        help='Apply Lorentzian broadening with specified width.')
    parser.add_argument(
        '-g',
        '--gaussian',
        nargs='?',
        default=False,
        const=2,
        type=float,
        help='Apply Gaussian broadening with specified width.')
    parser.add_argument(
        '-w', '--weighting',
        type=str,
        default=None,
        help='Apply cross-section weighting to data. "alka", "he2" and '
             '"yeh_haxpes" select tabulated data for valence band at 1486.6 '
             'eV, 40.8 eV and 8047.8 eV respectively. '
             'Numerical values will be interpreted as an energy in keV; '
             'for energies from 1-1500 eV cross-sections will be determined '
             'using a parametrisation from tabulated data. '
             'Alternatively, provide '
             'path to a JSON file with cross-section data.')
    parser.add_argument(
        '--units',
        '--x_units',
        type=str,
        default='',
        choices=('cm', 'cm-1', 'thz', 'THz',
                 'ev', 'eV', 'ry', 'Ry', 'ha', 'Ha'),
        help='Units for x axis (usually frequency or energy)')
    parser.add_argument(
        '--ylabel',
        type=str,
        default=None,
        help='Label for plot y-axis')
    parser.add_argument(
        '--txt',
        nargs='?',
        default=False,
        const=None,
        help='Write broadened output as space-delimited text; file if path '
             'provided, otherwise write to standard output.')
    parser.add_argument(
        '--csv',
        nargs='?',
        default=False,
        const=None,
        help='Write broadened output as comma-separated values; file if path '
             'provided, otherwise write to standard output.')
    parser.add_argument(
        '-p',
        '--plot',
        nargs='?',
        default=False,
        const=None,
        help='Plot broadened spectrum. Plot to filename if provided,'
             ' otherwise display to screen.')
    parser.add_argument(
        '-d',
        '--sampling',
        type=float,
        default=False,
        help='Width, in units of x, of x-axis resolution. If not specified, '
             'default value is based on units. If units are not specified, '
             'default value is 1e-2.')
    parser.add_argument(
        '-k',
        '--spikes',
        '--spike',
        action='store_true',
        help='Resample data as "spikes" on a zero baseline. The default is to '
             'interpolate linearly between y-values, which is reasonable for '
             'distributions such as DOS. If the input data set only contains '
             'active energies/frequencies (e.g. IR modes) then you should use '
             '--spike mode. See tutorials for examples.')
    parser.add_argument(
        '--pdos', action="store_true", help='Use orbital-projected data')
    parser.add_argument(
        '--flipx', '--xflip', action="store_true",
        help='Negate x-values in output; this may be helpful for comparison '
             'with binding energy measurments.')
    parser.add_argument(
        '--xmin', type=float, default=None, help='Minimum x axis value')
    parser.add_argument(
        '--xmax', type=float, default=None, help='Maximum x axis value')
    parser.add_argument(
        '--ymin', type=float, default=0, help='Minimum y axis value')
    parser.add_argument(
        '--ymax', type=float, default=None, help='Maximum y axis value')
    parser.add_argument(
        '--style', type=str, nargs='+', default=['seaborn-colorblind'],
        help='Plotting style: a sequence of matplotlib styles and paths to '
             'style files. The default palette is called "seaborn-colorblind".'
        )
    parser.add_argument(
        '--overlay', type=str, default=None, help='Data file for overlay')
    parser.add_argument(
        '--overlay_scale', type=float, default=None,
        help='Y-axis scale factor for data overlay')
    parser.add_argument(
        '--overlay_offset', type=float, default=0,
        help='X-axis offset for data overlay')
    parser.add_argument(
        '--overlay_style', type=str, default='o',
        help='Matplotlib line style for overlay data. Default "o" for '
             'circles, "x:" for crosses joined by dotted lines, etc.')
    parser.add_argument(
        '--overlay_label', type=str, default=None,
        help='Legend label for data overlay'
        )

    return parser

if __name__ == '__main__':
    main()
