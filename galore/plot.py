"""Plotting routines with Matplotlib"""
from matplotlib import pyplot as plt
from galore import auto_limits

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
            kwargs['ymin'] = auto_ymin
    ax.set_ylim([kwargs['ymin'], kwargs['ymax']])

    return plt
