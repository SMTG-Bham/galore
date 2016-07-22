#! /usr/bin/env python

import numpy as np
from itertools import repeat
try:
    from matplotlib import pyplot as plt
    has_matplotlib = True
except ImportError:
    has_matplotlib = False


def random_raman_xy(max_freq=1000):
    """Generate some plausible Raman frequencies and intensities

    For development purposes only!"""
    raman_sim = np.random.rand(15, 2)
    raman_sim[:, 0] = raman_sim[:, 0] * max_freq
    return raman_sim


def xy_to_1d(xy, d, xmin=0, xmax=False):
    """Convert a set of x,y coordinates to 1D array

    Args:
        xy: (ndarray) 2D numpy array of x, y values
        d: sample width in units of x
        xmin: x-value corresponding to start of 1D array
        xmax: x-value corresponding to end of 1D array"""
    if not xmax:
        xmax = max(xy[:, 0]) * 1.05

    x_values = np.arange(xmin, xmax, d)
    spikes = np.zeros(len(x_values))

    for x, y in xy:
        spike = y * np.array(map(lambda f: delta(f, x, w=d), x_values))
        spikes += spike
    return spikes


def delta(f1, f2, w=1):
    """Compare two frequencies, return 1 if close"""
    if abs(f1 - f2) <= 0.5 * w:
        return 1
    else:
        return 0


def lorentzian(f, f0=0, gamma=1):
    """Lorentzian function with height 1 centred on f0"""
    return 0.5 * gamma / (np.pi * (f - f0)**2 + (0.5 * gamma)**2)


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
    else:
        raise Exception('Broadening distribution '
                        ' "{0}" not known.'.format(dist))

    pad_points = int(pad / d)
    broadened_data = np.convolve(broadening, data)
    broadened_data = broadened_data[pad_points:len(data) + pad_points]
    return broadened_data


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
    raman_spikes = xy_to_1d(raman_sim, d, xmax=max_freq)
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
