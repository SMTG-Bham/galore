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
from collections import OrderedDict

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


def pdos(**kwargs):
    # Read files into dict, check for consistency
    energy_label = None
    pdos_data = OrderedDict()
    for pdos_file in kwargs['input']:

        if not os.path.exists(pdos_file):
            raise Exception("Input file {0} does not "
                            "exist!".format(kwargs['input']))

        basename = os.path.basename(pdos_file)
        try:
            element = basename.split("_")[-2]
        except IndexError:
            raise Exception("Couldn't guess element name from filename. "
                            "Please format filename as XXX_EL_YYY.EXT"
                            "Where EL is the element label, and XXX, YYY "
                            "and EXT are labels of your choice. We recommend"
                            "SYSTEM_EL_dos.dat")

        pdos_data[element] = galore.formats.read_pdos_txt(pdos_file)

        if energy_label is None:
            energy_label = pdos_data[element].dtype.names[0]
        else:
            try:
                assert pdos_data[element].dtype.names[0] == energy_label
            except AssertionError as error:
                error.args += ("Energy labels are not consistent "
                               "between input files",)
                raise

    # Work out sampling details; 5% pad added to data if no limits specified
    # In XPS mode, the user specifies these as binding energies so values are
    # reversed while treating DOS data.
    d = kwargs['sampling']
    limits = (auto_limits(pdos_data[energy_label], padding=0.05)
                  for (element, pdos_data)
                  in pdos_data.items())
    xmins, xmaxes = zip(*limits)

    if kwargs['xmax'] is None:
        kwargs['xmax'] = max(xmaxes)

    if kwargs['xmin'] is None:
        kwargs['xmin'] = min(xmins)

    if kwargs['xps']:
        kwargs['xmin'], kwargs['xmax'] = -kwargs['xmax'], -kwargs['xmin']

    x_values = np.arange(kwargs['xmin'], kwargs['xmax'], d)

    # Resample data into new dictionary
    pdos_plotting_data = OrderedDict()
    for element, data in pdos_data.items():

        orbital_labels = data.dtype.names[1:]



        pdos_resampled = [galore.xy_to_1d(data[[energy_label, orbital]],
                                          x_values)
                          for orbital in orbital_labels]

        broadened_data = [orbital_data.copy()
                          for orbital_data in pdos_resampled]

        if kwargs['lorentzian']:
            broadened_data = [galore.broaden(broadened_orbital_data, d=d,
                                             dist='lorentzian',
                                             width=kwargs['lorentzian'])
                              for broadened_orbital_data in broadened_data]

        if kwargs['gaussian']:
            broadened_data = [galore.broaden(broadened_orbital_data, d=d,
                                             dist='gaussian',
                                             width=kwargs['gaussian'])
                              for broadened_orbital_data in broadened_data]

        pdos_plotting_data[element] = OrderedDict([('energy', x_values)])
        pdos_plotting_data[element].update(
            OrderedDict((orbital, broadened_data[i])
                        for i, orbital in enumerate(orbital_labels)))

        if kwargs['xps']:
            pdos_plotting_data = galore.apply_xps_weights(pdos_plotting_data)

    plt = galore.plot.plot_pdos(pdos_plotting_data,
                                flipx=kwargs['xps'], # XPS uses reversed axis
                                **kwargs)

    if kwargs['xps'] and kwargs['units']:
        xlabel = "Binding energy / " + kwargs['units']
    elif kwargs['xps']:
        xlabel = "Binding energy"
    elif kwargs['units']:
        xlabel = energy_label + " / " + kwargs['units']
    else:
        xlabel= energy_label
    plt.xlabel(xlabel)

    if kwargs['plot']:
        plt.savefig(kwargs['plot'])
    elif kwargs['plot'] is None:
        plt.show()

def simple_dos(**args):
    if len(args['input']) > 1:
        raise ValueError("Simple DOS only uses one input file, "
                         "not list: {0}".format(args['input']))
    args['input'] = args['input'][0]

    if not os.path.exists(args['input']):
        raise Exception("Input file {0} does not exist!".format(args['input']))
    if galore.formats.isdoscar(args['input']):
        xy_data = galore.formats.read_doscar(args['input'])
    else:
        xy_data = np.genfromtxt(args['input'], delimiter=',', comments='#')

    # Add 5% to data range if not specified
    auto_xmin, auto_xmax = auto_limits(xy_data[:, 0], padding=0.05)
    if args['xmax'] is None:
        args['xmax'] = auto_xmax
    if args['xmin'] is None:
        args['xmin'] = auto_xmin

    d = args['sampling']
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


def run(**args):
    if args['sampling']:
        pass
    elif args['units'] in ('cm', 'cm-1'):
        args['sampling'] = 0.1
    elif args['units'] in ('THz', 'thz'):
        args['sampling'] = 1e-3
    elif args['units'] in ('ev', 'eV'):
        args['sampling'] = 1e-2

    if args['pdos']:
        pdos(**args)
    else:
        simple_dos(**args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input', type=str, default='DOSCAR', nargs='+', help='Input data file')
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
        '--xps',
        action='store_true',
        help='Apply XPS cross-section weighting to data'
        )
    parser.add_argument(
        '--units',
        '--x_units',
        type=str,
        default='eV',
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
        '--pdos', action="store_true", help='Use orbital-projected data')
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
