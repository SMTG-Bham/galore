"""Plotting routines with Matplotlib"""
from collections import defaultdict
from os.path import basename as path_basename
from itertools import cycle
import logging

import numpy as np
from matplotlib import pyplot as plt

from galore import auto_limits
import galore.formats

_unit_labels = {'cm': r'cm$^{-1}$',
                'cm-1': r'cm$^{-1}$',
                'thz': 'THz',
                'ev': 'eV',
                'ry': 'Ry',
                'ha': 'Ha'}
_energy_units = ('ev', 'ry', 'ha')
_frequency_units = ('cm', 'cm-1', 'thz')


def guess_xlabel(units=None, flipx=False, energy_label=None):
    """Infer a decent x-xaxis label from available information

    Args:
        units (str): Energy or frequency unit string
        flipx (bool): Is energy scale negated to form binding energy
        energy_label (str): Header from .dat file if used"""

    if (units is not None) and units.lower() in _unit_labels:
        unit_label = _unit_labels[units.lower()]
    else:
        unit_label = units

    if flipx:
        if (units is not None) and units.lower() in _energy_units:
            xlabel = 'Binding energy / ' + unit_label
        elif (energy_label is not None) and (units is not None):
            xlabel = '-' + energy_label + ' / ' + unit_label
        elif (energy_label is not None):
            xlabel = '-' + energy_label
        else:
            xlabel = 'Binding energy'

    else:
        if (units is not None) and (energy_label is not None):
            xlabel = energy_label + ' / ' + unit_label
        elif (units is not None):
            xlabel = unit_label
        elif (energy_label is not None):
            xlabel = energy_label
        else:
            xlabel = ''

    return xlabel


def add_overlay(plt, overlay, overlay_scale=None, overlay_offset=0.,
                overlay_style='o', overlay_label=None):
    """Overlay data points from file over existing plot

    Args:
        plt (matplotlib.pyplot): Pyplot object with target figure/axes active
        overlay (str): Path to overlay data file
        overlay_scale (float): y-axis scale factor for overlay data. If None,
            scale to match maximum and print this value.
        overlay_offset (float): x-xaxis offset for overlay data
        overlay_style (str): Matplotlib short code for marker/line style
        overlay_label (str): Legend label for data overlay (default: filename)

    """

    if galore.formats.is_csv(overlay):
        xy_data = galore.formats.read_csv(overlay)
    else:
        xy_data = galore.formats.read_txt(overlay)

    ax = plt.gca()
    if overlay_scale is None:
        ymax = np.max(xy_data[:, 1])
        lines = ax.lines
        ymax_plot = max(max(line.get_xydata()[:, 1]) for line in lines)

        overlay_scale = ymax_plot / ymax
        logging.info("Scaling overlay intensity by {0}".format(overlay_scale))

    if overlay_label is None:
        overlay_label = path_basename(overlay)

    plt.plot(xy_data[:, 0] + overlay_offset,
             xy_data[:, 1] * overlay_scale,
             overlay_style,
             label=overlay_label)

    return plt


def plot_pdos(pdos_data, ax=None, total=True, show_orbitals=True,
              offset=0., flipx=False, **kwargs):
    """Plot a projected density of states (PDOS)

    Args:
        pdos_data (dict): Data for pdos plot in format::

                {'el1': {'energy': values, 's': values, 'p': values ...},
                 'el2': {'energy': values, 's': values, ...}, ...}

             where DOS values are 1D numpy arrays. For deterministic plots,
             use ordered dictionaries!
        ax (matplotlib.Axes): Use existing Axes object for plot. If None,
            a new figure and axes will be created.
        total (bool): Include total DOS. This is sum over all others.
            Input x-values must be consistent, no further resampling is done.
        show_orbitals (bool): Show orbital contributions. If False, they will
            not be plotted but are still used to calculate the total DOS.
        offset (float): Bias x-axis values (e.g. to account for XPS E-Fermi),
        flipx (bool): Negate x-axis values to express negative VB energies as
            positive binding energies.

    Returns:
        (matplotlib.pyplot):
            The pyplot state machine. Can be queried to access current figure
            and axes.

        """
    # Any unset kwargs will be seen as None
    kwargs = defaultdict((lambda: None), **kwargs)

    linecycler = cycle(['--'] * 6 + [':'] * 6 + ['-.'] * 6)

    max_y = 0

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    tdos = np.zeros(len(list(pdos_data.values())[0]['energy']))

    for element, el_data in pdos_data.items():
        # Field 'energy' must be present, other fields are orbitals
        assert 'energy' in el_data.keys()
        if flipx:
            x_data = -el_data['energy'] + offset
        else:
            x_data = el_data['energy'] + offset

        orbitals = list(el_data.keys())
        orbitals.remove('energy')

        for orbital in orbitals:
            if total:
                tdos += el_data[orbital]
            else:
                max_y = max(max_y, max(el_data[orbital]))

            if show_orbitals:
                ax.plot(x_data, el_data[orbital],
                        label="{0}: {1}".format(element, orbital),
                        marker='', linestyle=next(linecycler))

    if total:
        max_y = max(tdos)
        ax.plot(x_data, tdos, label="Total", color='k', linestyle='-')

    # Range based on last dataset. If that's not satisfactory, it should have
    # been pruned already by kwargs['xmin'] and kwargs['xmax']
    ax.set_xlim([min(x_data), max(x_data)])

    xlabel = guess_xlabel(units=kwargs['units'], flipx=flipx,
                          energy_label=None)
    ax.set_xlabel(xlabel)

    # Set axis range as data range + 10% if not specified
    if kwargs['ymax'] is None:
        kwargs['ymax'] = max_y * 1.1
    if kwargs['ymin'] is None:
        kwargs['ymin'] = 0
    ax.set_ylim([kwargs['ymin'], kwargs['ymax']])
    ax.set_yticklabels([''])
    ax.legend(loc='best')

    return plt


def plot_tdos(xdata, ydata, ax=None, offset=0., **kwargs):
    """Plot a total DOS (i.e. 1D dataset)


    Args:
        xdata (iterable): x-values (energy, frequency etc.)
        ydata (iterable): Corresponding y-values (DOS or measurement intensity)
        show (bool): Display plot
        offset (float): Energy shift to x-axis
        ax (matplotlib.Axes): If provided, plot onto existing Axes object. If
            None, a new Figure will be created and the pyplot instance will be
            returned.

    Returns:
        (matplotlib.pyplot):
            The pyplot state machine. Can be queried to access current figure
            and axes.

    """

    # Any unset kwargs will be seen as None
    kwargs = defaultdict((lambda: None), **kwargs)

    if ax:
        pass
    else:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    if kwargs['flipx']:
        xdata = -xdata + offset
    else:
        xdata = xdata + offset

    ax.plot(xdata, ydata, 'C0-')
    ax.set_xlim([min(xdata), max(xdata)])

    xlabel = guess_xlabel(units=kwargs['units'], flipx=kwargs['flipx'])

    ax.set_xlabel(xlabel)

    if kwargs['ymax'] is None or kwargs['ymin'] is None:
        # Add 10% to data range if not specified
        auto_ymin, auto_ymax = auto_limits(ydata, padding=0.1)
        if kwargs['ymax'] is None:
            kwargs['ymax'] = auto_ymax
        if kwargs['ymin'] is None:
            kwargs['ymin'] = 0
    ax.set_ylim([kwargs['ymin'], kwargs['ymax']])
    ax.set_yticklabels([''])

    return plt
