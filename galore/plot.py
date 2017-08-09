"""Plotting routines with Matplotlib"""
import numpy as np
from matplotlib import pyplot as plt
from galore import auto_limits
from six import itervalues

plt.style.use("seaborn-colorblind")

def plot_pdos(pdos_data, ax=None, total=True, offset=0, flipx=False, **kwargs):
    """Plot a projected density of states (PDOS)

    Args:
        pdos_data (dict): Data for pdos plot in format 
            {'el1': {'energy': values, 's': values, 'p': values ...},
             'el2': {'energy': values, 's': values, ...}, ...}
             where DOS values are 1D numpy arrays. For deterministic plots, 
             use ordered dictionaries!
        ax (matplotlib.Axes): Use existing Axes object for plot. If None,
            a new figure and axes will be created.
        total (bool): Include total DOS. This is sum over all others. 
            Input x-values must be consistent, no further resampling is done.
        offset (float): Bias x-axis values (e.g. to account for XPS E-Fermi)
        flipx (bool): Negate x-axis values to express negative VB energies as
            positive binding energies

    Returns:
        plt (matplotlib.pyplot):
            the pyplot state machine. Can be queried to access current figure 
            and axes.

        """

    max_y = 0

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

    tdos = np.zeros(len(next(itervalues(pdos_data))['energy']))

    for element, el_data in pdos_data.items():
        # Field 'energy' must be present, other fields are orbitals
        assert 'energy' in el_data.keys()
        if flipx:           
            x_data = -el_data['energy']
        else:
            x_data = el_data['energy']            

        orbitals = list(el_data.keys())
        orbitals.remove('energy')

        for orbital in orbitals:
            if total:
                tdos += el_data[orbital]
            else:
                max_y = max(max_y, max(el_data[orbital]))

            ax.plot(x_data, el_data[orbital],
                    label="{0}: {1}".format(element, orbital),
                    marker='')       

    if total:
        max_y = max(tdos)
        ax.plot(x_data, tdos, label="Total", color='k')

    # Range based on last dataset. If that's not satisfactory, it should have
    # been pruned already by kwargs['xmin'] and kwargs['xmax']
    ax.set_xlim([min(x_data), max(x_data)])
    ax.set_xlabel(kwargs['units'])

    if kwargs['ymax'] is None or kwargs['ymin'] is None:
        # Add 10% to data range if not specified
        if kwargs['ymax'] is None:
            kwargs['ymax'] = max_y * 1.1
        if kwargs['ymin'] is None:
            kwargs['ymin'] = 0
    ax.set_ylim([kwargs['ymin'], kwargs['ymax']])

    ax.legend(loc='best')
    
    return plt


def plot_tdos(xdata, ydata, filename=None, ax=None, **kwargs):
    """Plot a total DOS (i.e. 1D dataset)


    Args:
        xdata (iterable): x-values (energy, frequency etc.)
        ydata (iterable): Corresponding y-values (DOS or measurement intensity)
        show (bool): Display plot
        filename (str): If provided, write plot to this path/filename.
        ax (matplotlib.Axes): If provided, plot onto existing Axes object. If
            None, a new Figure will be created and the pyplot instance will be
            returned.

    Returns:
        Pyplot instance if a new Figure was created.
        
    """

    if ax:
        pass
    else:
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
    
    ax.plot(xdata, ydata, 'r-')
    ax.set_xlim([min(xdata), max(xdata)])
    ax.set_xlabel(kwargs['units'])

    if kwargs['ymax'] is None or kwargs['ymin'] is None:
        # Add 10% to data range if not specified
        auto_ymin, auto_ymax = auto_limits(ydata, padding=0.1)
        if kwargs['ymax'] is None:
            kwargs['ymax'] = auto_ymax
        if kwargs['ymin'] is None:
            kwargs['ymin'] = 0
    ax.set_ylim([kwargs['ymin'], kwargs['ymax']])

    return plt
