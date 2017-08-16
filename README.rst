README
======

Introduction
------------

Apply Gaussian and Lorentzian broadening to data from *ab initio*
calculations. The two main intended applications are

1. Application of Lorentzian instrumental broadening to simulated Raman
   spectra from DFPT calculations.
2. Gaussian and Lorentzian broadening of electronic density-of-states,
   with orbital weighting to simulate XPS measurements.


Documentation
-------------

A brief overview is given in this README file.
Full documentation can be built using Sphinx; try ``make html`` from
the *docs* directory of this project.
Pre-compiled documentation will be made available through `readthedocs
<https://readthedocs.org>`__ when this project is made publicly
viewable.

Usage
-----

For full documentation of the command-line flags, please use the
in-built help.

::

    galore -h

Instrumental broadening
^^^^^^^^^^^^^^^^^^^^^^^

Data may be provided as a set of X,Y coordinates in a text file of
comma-separated values (CSV).
Whitespace-separated data is also readable, in which case a *.txt*
file extension should be used.

To plot a CSV file to the screen with default Lorentzian broadening (2
cm\ :sup:`-1`), use the command

::

    galore MY_DATA.csv -l -p

and to plot to a file with more generous 10 cm\ :sup:`-1` broadening

::

    galore MY_DATA.csv -l 10 -p MY_PLOT.png

will provide the additional data needed. 

XPS simulation
^^^^^^^^^^^^^^

XPS simulation requires several inputs:

- Orbital-projected density of states data. The input format for
  Galore is one file per element, with columns for energy and each
  orbital. A header should be provided with the orbital names. For an
  examples see the *test/MgO* folder. The element will be identified
  from the filename, so the filename format should be of the form
  ``X_el_Y.Z``, where `el` is the corresponding element symbol.
- Instrumental broadening parameters. The Lorentzian and Gaussian
  broadening widths are input by the user as before.
- Photoionization cross section data, which is used to weight the
  contributions of different orbitals. Galore includes data for
  valance band orbitals at Al k-α energies, drawn from a more
  extensive table computed by
  `Yeh and Lindau (1985) <https://doi.org/10.1016/0092-640X(85)90016-6>`__.
  An alternative dataset may be provided as a JSON file; it is only
  necessary to include the elements and orbitals used in the DOS input
  files.

To demonstrate this function, sample data is provided calculated with
the revTPSS function for MgO.

::

    galore test/MgO/MgO_Mg_dos.dat test/MgO/MgO_O_dos.dat -l 0.3 -g 0.2 --xps --pdos -p --xmin -1 --xmax 8

will plot the calculated valence band XPS spectrum to the screen over
a sensible range, with 0.3 eV of Lorentzian broadening and 0.2 eV of
Gaussian broadening.

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

Installation for documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to build the documentation you can add ``[docs]`` to the
pip command to ensure you have all the Sphinx requirements and
extensions.

::

   pip install --upgrade .[docs]

Development
-----------

This code is developed by the Scanlon Materials Theory Group based at
University College London. As a result, development prioritises the
needs of this group. Other suggestions and contributions are welcome;
please use the Github issue tracker.

License
-------

Galore is made available under the GNU Public License, version 3.
