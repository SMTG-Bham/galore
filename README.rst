Galore
======

Introduction
------------

Apply Gaussian and Lorentzian broadening to data from *ab initio*
calculations. The two main intended applications are

1. Application of Lorentzian instrumental broadening to simulated Raman
   spectra from DFPT calculations.
2. Gaussian broadening of electronic density-of-states to simulate XPS
   data, followed by Lorentzian instrumental broadening.

Usage
-----

For full documentation of the command-line flags, please use the
in-built help.

::

    ./bin/galore -h

Python API documentation will be added once the project structure and
scope become clearer.

Instrumental broadening
^^^^^^^^^^^^^^^^^^^^^^^

Data may be provided as a set of X,Y coordinates in a text file of
comma-separated values (CSV).

To plot a CSV file to the screen with default Lorentzian broadening (2
cm-1), use the command

::

    ./bin/galore MY_DATA.csv -l -p

and to plot to a file with more generous 10 cm-1 broadening

::

    ./bin/galore MY_DATA.csv -l 10 -p MY_PLOT.png

will provide the additional data needed.

XPS simulation
^^^^^^^^^^^^^^

For data calculated with VASP, the atom types are read from a POSCAR
file and the DOS is read from the DOSCAR.

Requirements
------------

Galore uses Numpy to apply convolution operations. Matplotlib is
required for plotting.

Galore uses Pip and setuptools for installation. You *probably* already
have this; if not, your GNU/Linux package manager will be able to oblige
with a package named something like ``python-setuptools``. On Max OSX,
the Python distributed with `Homebrew <http://brew.sh>`__ includes
setuptools and Pip.

Installation
------------

Windows user installation
^^^^^^^^^^^^^^^^^^^^^^^^^

`Anaconda <https://www.continuum.io/downloads>`__ is recommended for
managing the Python environment and dependencies on Windows. From the
Anaconda shell:

::

    pip install .

Linux/Mac developer installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the directory containing this README:

::

    pip install --user -e .

which installs an *editable* (``-e``) version of galore in your
userspace. The executable program ``galore`` goes to a directory like
``~/.local/bin`` and the galore library should be available on your
Pythonpath. These are links to this project folder, which you can
continue to edit and update using Git.

Development
-----------

This code is developed by the Scanlon Materials Theory Group based at
University College London. As a result, development prioritises the
needs of this group. Other suggestions and contributions are welcome;
please use the Github issue tracker.

License
-------

Galore is made available under the GNU Public License, version 3.
