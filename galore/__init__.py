###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Scanlon Materials Theory Group at University College London    #
# (c) 2017                                                                    #
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

from __future__ import print_function

import os.path
from collections import OrderedDict
from collections.abc import Sequence
import logging

from math import sqrt, log
import numpy as np
from scipy.interpolate import interp1d

import galore.formats
from galore.cross_sections import cross_sections_info


def auto_limits(data_1d, padding=0.05):
    """Return limiting values outside data range

    Args:
        data_1d (iterable): Data to obtain range from
        padding (float): Scale factor for padding relative to data range

    Returns:
        (2-tuple) (xmin, xmax)

    """
    xmin, xmax = min(data_1d), max(data_1d)
    auto_xmax = xmax + padding * (xmax - xmin)
    auto_xmin = xmin - padding * (xmax - xmin)
    return auto_xmin, auto_xmax


def process_1d_data(input=['vasprun.xml'],
                    gaussian=None, lorentzian=None,
                    sampling=1e-2,
                    xmin=None, xmax=None,
                    spikes=False,
                    **kwargs):
    """Read 1D data series from files, process for output

    Args:
        input (str or 1-list):
            Input data file. Pass as either a string or a list containing one
            string
        **kwargs:
            See main command reference

    Returns:
        2-tuple (np.ndarray, np.ndarray):
            Resampled x-values and corresponding broadened data as 1D numpy
            arrays

    """

    if 'flipx' in kwargs and kwargs['flipx']:
        raise Exception("x-flip not currently implemented in 1D mode.")

    if type(input) == str:
        pass
    elif len(input) > 1:
        raise ValueError("Simple DOS only uses one input file, "
                         "not list: {0}".format(input))
    else:
        input = input[0]

    if not os.path.exists(input):
        raise Exception(
            "Input file {0} does not exist!".format(input))
    if galore.formats.is_xml(input):
        xy_data = galore.formats.read_vasprun_totaldos(input)
    elif galore.formats.is_gpw(input):
        xy_data = galore.formats.read_gpaw_totaldos(input)
    elif galore.formats.is_doscar(input):
        xy_data = galore.formats.read_doscar(input)
    elif galore.formats.is_vasp_raman(input):
        xy_data = galore.formats.read_vasp_raman(input)
    elif galore.formats.is_csv(input):
        xy_data = galore.formats.read_csv(input)
    else:
        xy_data = galore.formats.read_txt(input)

    # Add 5% to data range if not specified
    auto_xmin, auto_xmax = auto_limits(xy_data[:, 0], padding=0.05)
    if xmax is None:
        xmax = auto_xmax
    if xmin is None:
        xmin = auto_xmin

    d = sampling
    x_values = np.arange(xmin, xmax, d)
    data_1d = galore.xy_to_1d(xy_data, x_values, spikes=spikes)

    broadened_data = data_1d.copy()
    if lorentzian:
        broadened_data = galore.broaden(
            broadened_data, d=d, dist='lorentzian', width=lorentzian)

    if gaussian:
        broadened_data = galore.broaden(
            broadened_data, d=d, dist='gaussian', width=gaussian)

    return (x_values, broadened_data)


def process_pdos(input=['vasprun.xml'],
                 gaussian=None, lorentzian=None,
                 weighting=None, sampling=1e-2,
                 xmin=None, xmax=None, flipx=False, **kwargs):
    """Read PDOS from files, process for output

    Args:
        input (list or str):
            Files for processing. Vasp output or space-separated files with
                XXX_EL_YYY.EXT filename pattern where EL is the element label.
                We recommend SYSTEM_EL_dos.dat. Alternatively, a
                `pymatgen.electronic_structure.dos.CompleteDos` can be
                provided. Spin channels indicated by an (up) or (down) suffix
                in file header will be combined for each orbital type.
        **kwargs:
            See main command reference

    Returns:
        dict:
            Weighted and resampled orbital data in format::

                {'el1': {'energy': values, 's': values, 'p': values ...},
                 'el2': {'energy': values, 's': values, ...}, ...}

    """
    if isinstance(input, str) or not isinstance(input, Sequence):
        input = [input]

    # Read files into dict, check for consistency
    energy_label = None
    pdos_data = OrderedDict()
    for pdos_file in input:
        if (galore.formats.is_complete_dos(pdos_file)
                or galore.formats.is_xml(pdos_file)):
            pdos_data = galore.formats.read_vasprun_pdos(pdos_file)
            kwargs['units'] = 'eV'
            break

        elif galore.formats.is_gpw(pdos_file):
            pdos_data = galore.formats.read_gpaw_pdos(pdos_file)
            kwargs['units'] = 'eV'
            break

        if not os.path.exists(pdos_file):
            raise Exception("Input file {0} does not "
                            "exist!".format(input))

        basename = os.path.basename(pdos_file)
        try:
            element = basename.split("_")[-2]
        except IndexError:
            raise Exception("Couldn't guess element name from filename. "
                            "Please format filename as XXX_EL_YYY.EXT"
                            "Where EL is the element label, and XXX, YYY "
                            "and EXT are labels of your choice. We recommend"
                            "SYSTEM_EL_dos.dat")

        data = galore.formats.read_pdos_txt(pdos_file)

        if energy_label is None:
            energy_label = data.dtype.names[0]
        else:
            try:
                assert data.dtype.names[0] == energy_label
            except AssertionError as error:
                error.args += ("Energy labels are not consistent "
                               "between input files",)
                raise

        orbital_labels = data.dtype.names[1:]
        pdos_data[element] = OrderedDict([('energy', data[energy_label])])
        pdos_data[element].update(OrderedDict((orbital, data[orbital])
                                  for orbital in orbital_labels))

    # Work out sampling details; 5% pad added to data if no limits specified
    # In x-flip mode, the user specifies these as binding energies so values
    # are reversed while treating DOS data.
    d = sampling
    limits = (auto_limits(data['energy'], padding=0.05)
              for (element, data) in pdos_data.items())
    xmins, xmaxes = zip(*limits)

    if xmax is None:
        xmax = max(xmaxes)

    if xmin is None:
        xmin = min(xmins)

    if flipx:
        xmin, xmax = -xmax, -xmin

    x_values = np.arange(xmin, xmax, d)

    # Resample data into new dictionary
    pdos_plotting_data = OrderedDict()
    for element, el_data in pdos_data.items():
        pdos_plotting_data[element] = OrderedDict([('energy', x_values)])
        for orbital, orb_data in el_data.items():
            if orbital == 'energy':
                continue
            elif orb_data is None:
                continue

            xy_data = np.column_stack([el_data['energy'], orb_data])

            pdos_resampled = galore.xy_to_1d(xy_data, x_values)
            broadened_data = pdos_resampled.copy()

            if lorentzian:
                broadened_data = galore.broaden(broadened_data, d=d,
                                                dist='lorentzian',
                                                width=lorentzian)

            if gaussian:
                broadened_data = galore.broaden(broadened_data, d=d,
                                                dist='gaussian',
                                                width=gaussian)

            pdos_plotting_data[element][orbital] = broadened_data

    if weighting:
        cross_sections = galore.get_cross_sections(weighting,
                                                   elements=pdos_data.keys())
        pdos_plotting_data = galore.apply_orbital_weights(
            pdos_plotting_data, cross_sections)

    return pdos_plotting_data


def xy_to_1d(xy, x_values, spikes=False):
    """Convert a set of x,y coordinates to 1D array

    Data is resampled to a given sequence of regularly-spaced x-values. By
    default linear interpolation is used between neighbouring points, which is
    suitable for resampling distribution data.

    Where the data consists of a set of discrete energy levels, it should be
    resampled to a series of "spikes". y-values are placed on the nearest
    x-value by subtracting d/2 and rounding up. d is determined by examining
    the first two elements of x_values.

    Args:
        xy: (ndarray) 2D numpy array of x, y values
        x_values: (iterable) An evenly-spaced x-value mesh
    Returns:
        (np.array): re-sampled y values corresponding to x_values
    """

    x_values = np.array(x_values)
    n_x_values = x_values.size
    d = x_values[1] - x_values[0]

    # Structured arrays are allowed, in which case first field is x,
    # second is y. A bit of hackery is needed to slice these interchangeably.
    if xy.dtype.names is None:
        x_field, y_field = (Ellipsis, 0), (Ellipsis, 1)
    else:
        x_field, y_field = xy.dtype.names

    if spikes:
        spikes = np.zeros(n_x_values)
        spike_locations = x_values.searchsorted(xy[x_field] - (0.5 * d))

        for location, value in zip(spike_locations, xy[y_field]):
            if location == 0 or location == n_x_values:
                pass
            else:
                spikes[location] += value

        return spikes

    else:
        y_func = interp1d(xy[x_field], xy[y_field],
                          assume_sorted=False,
                          bounds_error=False, fill_value=0)
        return y_func(x_values)


def delta(f1, f2, w=1):
    """Compare two frequencies, return 1 if close"""
    if abs(f1 - f2) <= 0.5 * w:
        return 1
    else:
        return 0


def lorentzian(f, f0=0, fwhm=1):
    """Lorentzian function with height 1 centered on f0.

    Args:
        f (np.array): 1D array of x-values (e.g. frequencies)
        f0 (float): Origin of function
        fwhm (float): full-width half-maximum (FWHM);
            i.e. the width of the function at half its maximum value.

    """
    return 0.5 * fwhm / (np.pi * ((f - f0)**2 + (0.5 * fwhm)**2))


def gaussian(f, f0=0, fwhm=1):
    """Gaussian function with height 1 centered on f0

       f (np.array): 1D array of x-values (e.g. frequencies)
       f0 (float): Origin of function
       fwhm (float): full-width half-maximum (FWHM); i.e. the width of the
       function at half its maximum value.

    """
    c = fwhm / (2 * sqrt(2 * log(2)))
    return np.exp(-np.power(f - f0, 2) / (2 * c**2))


def broaden(data, dist='lorentz', width=2, pad=False, d=1):
    """Given a 1d data set, use convolution to apply a broadening function

    Args:
        data (np.array): 1D array of data points to broaden
        dist (str): Type of distribution used for broadening. Currently only
            "Lorentz" is supported.
        width (float): Width parameter for broadening function. Determines the
            full-width at half-maximum (FWHM) of the broadening function.
        pad (float): Distance sampled on each side of broadening function.
        d (float): x-axis distance associated with each sample in 1D data

    """

    if not pad:
        pad = width * 20

    if dist.lower() in ('lorentz', 'lorentzian'):
        fwhm = width
        broadening = lorentzian(np.arange(-pad, pad, d), f0=0, fwhm=fwhm)
    elif dist.lower() in ('gauss', 'gaussian'):
        fwhm = width
        broadening = gaussian(np.arange(-pad, pad, d), f0=0, fwhm=fwhm)
    else:
        raise Exception('Broadening distribution '
                        ' "{0}" not known.'.format(dist))

    pad_points = int(pad / d)
    broadened_data = np.convolve(broadening, data)
    broadened_data = broadened_data[pad_points:len(data) + pad_points]

    return broadened_data


def apply_orbital_weights(pdos_data, cross_sections):
    """Weight orbital intensities by cross-section for photoemission simulation

    Args:
        pdos_data (dict): DOS data in format::

                {'el1': {'energy': values, 's': values, 'p': values ...},
                 'el2': {'energy': values, 's': values, ...}, ...}

             where DOS values are 1D numpy arrays. Orbital labels must match
             cross_sections data. It is recommended to use
             collections.OrderedDict instead of regular dictionaries, to ensure
             consistent output.

             In addition, the fields "citation", "link" and "energy" are
             recognised and logged as "INFO".

        cross_sections (dict): Weightings in format::

                {'el1': {'1s': x1, '2s': x2, '2p': x3 ...},
                 'el2': {'3s': y1, '3p': y2 ...}, ...}

             The labels should correspond to the headers in the input data. It
             is fine not so specify the level (e.g. use 's', 'p', etc.) as is
             done in the sample data; however, this means that all levels are
             being treated equally and hence probably the core levels will be
             weighted incorrectly. It is possible to set the cross-section of
             undesired orbitals (e.g. projection onto d-orbital for early
             elements) to None; in this case the orbital will be dropped from
             the returned data set.

    Returns:
        weighted_pdos_data (dict): Weighted data in same format as input
    """

    if type(cross_sections) != dict:
        raise TypeError('Cross-section data should be a dictionary. Try using '
                        'galore.get_cross_sections for a suitable data set.')

    logging.info("Applying cross-section weighting values to PDOS:")

    cross_sections_info(cross_sections, logging=logging)

    logging.info("  Orbital cross-section weights per electron:")

    weighted_pdos_data = OrderedDict()
    for el, orbitals in pdos_data.items():
        if 'warning' in cross_sections[el]:
            logging.warning("  {0}: {1}".format(
                el, cross_sections[el]['warning']))
        weighted_orbitals = OrderedDict()
        for orbital, data in orbitals.items():
            if orbital == 'energy':
                weighted_orbitals.update({'energy': data})
            else:
                try:
                    cs = cross_sections[el][orbital]
                except KeyError:
                    logging.warning("Could not find cross-section data for " +
                                    "element {0}, ".format(el) +
                                    "orbital {0}. ".format(orbital) +
                                    "Skipping this orbital.")
                    cs = None

                if cs is None:
                    pass
                else:
                    logging.info("   {0} {1}: {2:.3e}".format(el, orbital, cs))
                    weighted_orbitals.update({orbital: data * cs})

        weighted_pdos_data.update({el: weighted_orbitals})

    return weighted_pdos_data
