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

from __future__ import print_function

from itertools import repeat
from collections import OrderedDict
from pkg_resources import resource_filename
from json import load as json_load

import numpy as np
try:
    import matplotlib.pyplot as plt
    has_matplotlib = True
except ImportError:
    has_matplotlib = False

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


def random_raman_xy(max_freq=1000):
    """Generate some plausible Raman frequencies and intensities

    For development purposes only!"""
    raman_sim = np.random.rand(15, 2)
    raman_sim[:, 0] = raman_sim[:, 0] * max_freq
    return raman_sim


def xy_to_1d(xy, x_values):
    """Convert a set of x,y coordinates to 1D array

    Args:
        xy: (ndarray) 2D numpy array of x, y values
        x_values: (iterable) Object containing x-value mesh

    """

    spikes = np.zeros(len(x_values))
    d = x_values[1] - x_values[0]

    for x, y in xy:
        spike = y * np.fromiter(map(lambda f: delta(f, x, w=d), x_values),
                                float)
        spikes += spike
    return spikes


def delta(f1, f2, w=1):
    """Compare two frequencies, return 1 if close"""
    if abs(f1 - f2) <= 0.5 * w:
        return 1
    else:
        return 0


def lorentzian(f, f0=0, gamma=1):
    """Lorentzian function with height 1 centered on f0"""
    return 0.5 * gamma / (np.pi * (f - f0)**2 + (0.5 * gamma)**2)


def gaussian(f, f0=0, c=1):
    """Gaussian function with height 1 centered on f0"""
    return np.exp(-np.power(f - f0, 2) / (2 * c**2))


def broaden(data, dist='lorentz', width=2, pad=False, d=1):
    """Given a 1d data set, use convolution to apply a broadening function

    Args:
        data: (np.array) 1D array of data points to broaden
        dist: (str) Type of distribution used for broadening. Currently only
            "Lorentz" is supported.
        width: (float) Width parameter for broadening function. Units
            should be consistent with d.
        pad: (float) Distance sampled on each side of broadening function.
        d: (float) x-axis distance associated with each sample in 1D data

    """

    if not pad:
        pad = width * 20

    if dist.lower() in ('lorentz', 'lorentzian'):
        gamma = width
        broadening = lorentzian(np.arange(-pad, pad, d), f0=0, gamma=gamma)
    elif dist.lower() in ('gauss', 'gaussian'):
        c = width
        broadening = gaussian(np.arange(-pad, pad, d), f0=0, c=c)
    else:
        raise Exception('Broadening distribution '
                        ' "{0}" not known.'.format(dist))

    pad_points = int(pad / d)
    broadened_data = np.convolve(broadening, data)
    broadened_data = broadened_data[pad_points:len(data) + pad_points]
    return broadened_data


def apply_xps_weights(pdos_data, cross_sections=None):
    """Weight orbital intensities by cross-section for XPS simulation

    Args:
        pdos_data (dict): DOS data in format
            {'el1': {'energy': values, 's': values, 'p': values ...},
             'el2': {'energy': values, 's': values, ...}, ...}
             where DOS values are 1D numpy arrays. Orbital labels must match
             cross_sections data. It is recommended to use
             collections.OrderedDict instead of regular dictionaries, to ensure
             consistent output.

        cross_sections (dict): Weightings in format
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

    if cross_sections is None:

        cross_sections_file = resource_filename(__name__,
                                                "data/cross_sections.json")
        with open(cross_sections_file, 'r') as f:
            cross_sections = json_load(f)

    weighted_pdos_data = OrderedDict()
    for el, orbitals in pdos_data.items():
        weighted_orbitals = OrderedDict()
        for orbital, data in orbitals.items():
            if orbital == 'energy':
                weighted_orbitals.update({'energy': data})
            else:
                try:
                    cs = cross_sections[el][orbital]
                except KeyError as error:
                    error.args += ("Could not find cross-section data for "
                                   "element {0}, orbital {1}".format(el,
                                                                     orbital),)
                    raise
                if cs is None:
                    pass
                else:
                    weighted_orbitals.update({orbital: data * cs})

        weighted_pdos_data.update({el: weighted_orbitals})

    return weighted_pdos_data

def main():
    """For now main() contains a proof-of-concept example with random data.

    This example should be replaced with a useful user interface, and
    fresh examples prepared to demonstrate the UI and API.
    """
    # Set up a mesh for discrete analysis
    d = 1
    # Need some negative frequency points so Lorentzian can be correctly
    # defined symmetrically
    pad = 50
    max_freq = 1000
    raman_sim = random_raman_xy(max_freq=max_freq)

    gamma = 2
    frequencies = np.arange(0, max_freq, d)

    raman_spikes = xy_to_1d(raman_sim, frequencies)
    broadened_spikes = broaden(raman_spikes, pad=pad, d=d, width=gamma)

    broadening = lorentzian(np.arange(-pad, pad, d), f0=0, gamma=gamma)

    triple_plot(raman_sim, frequencies, d, broadening, pad, raman_spikes,
                broadened_spikes)


def triple_plot(raman_sim,
                frequencies,
                d,
                broadening,
                pad,
                raman_spikes,
                broadened_spikes,
                filename=False):
    """Plot the proof-of-concept with random data which is set up in main().
    """
    max_freq = max(frequencies)
    # Plot them
    plt.subplot(3, 1, 1)
    plt.vlines(raman_sim[:, 0], 0, raman_sim[:, 1])
    plt.xlabel('Frequency / cm$^{-1}$')
    plt.xlim([0, max_freq])
    plt.ylabel('Intensity')
    plt.title('Random data')

    plt.subplot(3, 1, 2)
    plt.title('Broadening function')
    plt.plot(np.arange(-pad, pad, d), broadening, 'r-')

    plt.subplot(3, 1, 3)
    plt.title('Discretised data, broadening')
    plt.vlines(frequencies, 0, raman_spikes)
    plt.plot(frequencies, broadened_spikes, 'r-')

    plt.xlabel('Frequency / cm$^{-1}$')
    plt.xlim([0, max_freq])
    plt.ylabel('Intensity')

    plt.tight_layout()

    if filename:
        plt.savefig(filename)
    else:
        plt.show()


if __name__ == '__main__':
    main()
