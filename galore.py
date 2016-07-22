#! /usr/bin/env python

import numpy as np
from itertools import repeat
try:
    from matplotlib import pyplot as plt
    has_matplotlib = True
except ImportError:
    has_matplotlib = False

def random_raman_xy(max_freq=1000):
    # Generate some plausible Raman frequencies and intensities

    raman_sim = np.random.rand(15, 2)
    raman_sim[:,0] = raman_sim[:,0] * max_freq
    return raman_sim

    
def xy_to_1d(xy, d, xmin=0, xmax=False):
    """Convert a set of x,y coordinates to 1D array

    Args:
        xy: (ndarray) 2D numpy array of x, y values
        d: sample width in units of x
        xmin: x-value corresponding to start of 1D array
        xmax: x-value corresponding to end of 1D array"""
    if not xmax:
        xmax = max(xy[:,0]) * 1.05

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
    return 0.5 * gamma / (
    np.pi * (f - f0)**2 + (0.5 * gamma)**2
    )
        
def main():
    # Set up a mesh for discrete analysis
    d = 1
    # Need some negative frequency points so Lorentzian can be correctly
    # defined symmetrically
    pad = 50
    raman_sim = random_raman_xy()

    frequencies = np.arange(-pad, max_freq, d)
    
def triple_plot(raman_sim, frequencies):
    max_freq = max(Frequencies)
    # Plot them
    plt.subplot(3, 1, 1)
    plt.vlines(raman_sim[:,0], 0, raman_sim[:,1])
    plt.xlabel('Frequency / cm$^{-1}$')
    plt.xlim([0, max_freq])
    plt.ylabel('Intensity')
    plt.title('Random data')


    raman_spikes = np.zeros(len(frequencies))


    gamma = 2
    broadening = lorentzian(np.arange(-pad, pad, d), 0, gamma=gamma)

    plt.subplot(3, 1, 2)
    plt.title('Broadening function')
    plt.plot(np.arange(-pad, pad, d), broadening, 'r-')

    for f, h in raman_sim:
        spike = h * np.array(map(delta, frequencies, repeat(f, len(frequencies))))
        raman_spikes += spike

    pad_points = int(pad/d)
    broadened_spikes = np.convolve(broadening, raman_spikes)
    broadened_spikes = broadened_spikes[pad_points:len(frequencies) + pad_points]

    plt.subplot(3, 1, 3)
    plt.title('Discretised data, broadening')
    plt.vlines(frequencies, 0, raman_spikes)

    plt.plot(frequencies, broadened_spikes, 'r-')

    plt.xlabel('Frequency / cm$^{-1}$')
    plt.xlim([0, max_freq])
    plt.ylabel('Intensity')

    plt.tight_layout()
    filename = 'raman_sim.png'
    plt.savefig(filename)
    return(filename)

if __name__ == '__main__':
    main()
