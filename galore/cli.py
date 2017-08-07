#! /usr/bin/env python

###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Adam J. Jackson (2016) at University College London            #
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
from __future__ import print_function, absolute_import, division

import os
import argparse

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


def run(**args):
    if not os.path.exists(args['input']):
        raise Exception("Input file {0} does not exist!".format(args['input']))
    if galore.formats.isdoscar(args['input']):
        xy_data = galore.formats.read_doscar(args['input'])
    else:
        xy_data = np.genfromtxt(args['input'], delimiter=',', comments='#')

    if args['sampling']:
        d = args['sampling']
    elif args['units'] in ('cm', 'cm-1'):
        d = 0.1
    elif args['units'] in ('THz', 'thz'):
        d = 1e-3
    elif args['units'] in ('ev', 'eV'):
        d = 1e-2

    # Add 5% to data range if not specified
    auto_xmin, auto_xmax = auto_limits(xy_data[:, 0], padding=0.05)
    if args['xmax'] is None:
        args['xmax'] = auto_xmax
    if args['xmin'] is None:
        args['xmin'] = auto_xmin

    x_values = np.arange(args['xmin'], args['xmax'], d)
    data_1d = galore.xy_to_1d(xy_data, x_values)

    broadened_data = data_1d.copy()
    if args['lorentzian']:
        broadened_data = galore.broaden(
            broadened_data, d=d, dist='lorentzian', width=args['lorentzian'])

    if args['gaussian']:
        broadened_data = galore.broaden(
            broadened_data, d=d, dist='gaussian', width=args['gaussian'])

    if not any(
        ((args['csv'] is None), (args['txt'] is None),
         (args['plot'] is None), args['csv'], args['txt'], args['plot'])):
        print("No output selected. Please use at least one of the output "
              "options (CSV, txt, plotting). For usage information, run "
              "galore with -h argument.")

    if args['csv'] is None:
        galore.formats.write_csv(x_values, broadened_data, filename=None)
    elif args['csv']:
        galore.formats.write_csv(
            x_values, broadened_data, filename=args['csv'])

    if args['txt'] is None:
        galore.formats.write_txt(x_values, broadened_data, filename=None)
    elif args['txt']:
        galore.formats.write_txt(
            x_values, broadened_data, filename=args['txt'])

    if args['plot'] or args['plot'] is None:
        if not has_matplotlib:
            print("Can't plot, no Matplotlib")
        else:
            plt = galore.plot.plot_tdos(x_values, broadened_data, **args)
            if args['plot']:
                plt.savefig(args['plot'])
            else:
                plt.show()
            

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input', type=str, default='DOSCAR', help='Input data file')
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
        '--units',
        '--x_units',
        type=str,
        default='cm-1',
        choices=('cm', 'cm-1', 'thz', 'THz', 'ev', 'eV'),
        help='Units for x axis (usually frequency or energy)')
    parser.add_argument(
        '--txt',
        nargs='?',
        default=False,
        const=None,
        help="Write broadened output as space-delimited text; file if path "
        "provided, otherwise write to standard output.")
    parser.add_argument(
        '--csv',
        nargs='?',
        default=False,
        const=None,
        help="Write broadened output as comma-separated values; file if path "
        "provided, otherwise write to standard output.")
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
        help='Width, in units of x, of x-axis resolution')
    parser.add_argument(
        '--xmin', type=float, default=None, help='Minimum x axis value')
    parser.add_argument(
        '--xmax', type=float, default=None, help='Maximum x axis value')
    parser.add_argument(
        '--ymin', type=float, default=0, help='Minimum y axis value')
    parser.add_argument(
        '--ymax', type=float, default=None, help='Maximum y axis value')
    args = parser.parse_args()
    args = vars(args)
    run(**args)


if __name__ == '__main__':
    main()
