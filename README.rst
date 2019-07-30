README
======

.. image:: https://zenodo.org/badge/63942513.svg
   :target: https://zenodo.org/badge/latestdoi/63942513
   :alt: Zenodo latest DOI
.. image:: https://travis-ci.org/SMTG-UCL/galore.svg?branch=master
   :target: https://travis-ci.org/SMTG-UCL/galore
   :alt: Travis CI Status
.. image:: https://coveralls.io/repos/github/SMTG-UCL/galore/badge.svg?branch=master
   :target: https://coveralls.io/github/SMTG-UCL/galore?branch=master
.. image:: https://readthedocs.org/projects/galore/badge/?version=latest
   :target: http://galore.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: http://joss.theoj.org/papers/10.21105/joss.00773/status.svg
   :target: https://doi.org/10.21105/joss.00773
   :alt: Paper in Journal of Open Source Software

Introduction
------------

Galore is a package which applies Gaussian and Lorentzian broadening
to data from *ab initio* calculations. The two main intended
applications are

1. Gaussian and Lorentzian broadening of electronic density-of-states,
   with orbital weighting to simulate UPS/XPS/HAXPES measurements.
2. Application of Lorentzian instrumental broadening to simulated Raman
   spectra from DFPT calculations.

Documentation
-------------

A brief overview is given in this README file.
A full manual, including tutorials and API documentation,
is available online at `readthedocs.io <http://galore.readthedocs.io/en/latest/>`__.
You can build a local version using Sphinx with ``make html`` from
the *docs* directory of this project.

An brief formal overview of the background and purpose of this code has been
`published <http://joss.theoj.org/papers/10.21105/joss.00773>`__
in *The Journal of Open Source Software*.

Usage
-----

Broadening, weighting and plotting are accessed with the ``galore`` program.
For full documentation of the command-line flags, please use the
in-built help::

    galore -h

Instrumental broadening
^^^^^^^^^^^^^^^^^^^^^^^

Data may be provided as a set of X,Y coordinates in a text file of
comma-separated values (CSV).
Whitespace-separated data is also readable, in which case a *.txt*
file extension should be used.

To plot a CSV file to the screen with default Lorentzian broadening (2
cm\ :sup:`-1`), use the command::

    galore MY_DATA.csv -l -p

and to plot to a file with more generous 10 cm\ :sup:`-1` broadening::

    galore MY_DATA.csv -l 10 -p MY_PLOT.png

will provide the additional data needed.

Other file formats are supported, including IR and Raman intensity
simulation output. See the Tutorials for usage examples.

Photoelectron spectra
^^^^^^^^^^^^^^^^^^^^^

UPS, XPS or HAXPES spectra can be simulated using Galore. This requires
several inputs:

- Orbital-projected density of states data.
  - This may be provided as an output file from the VASP or GPAW codes.
  - Formatted text files may also be used.
- Instrumental broadening parameters. The Lorentzian and Gaussian
  broadening widths are input by the user as before.
- Photoionization cross section data, which is used to weight the
  contributions of different orbitals.

  - Galore includes data for
    valance band orbitals at Al k-α (XPS) and He II (UPS) energies,
    drawn from a more extensive table computed by
    `Yeh and Lindau (1985) <https://doi.org/10.1016/0092-640X(85)90016-6>`__.
    An alternative dataset may be provided as a JSON file; it is only
    necessary to include the elements and orbitals used in the DOS input
    files.
  - Cross-sections for high-energy (1-1500 keV) photons have been
    fitted from tabulated data computed by `Scofield (1973) <https://doi.org/10.1039/C6TA03376H>`__.

See the `Tutorials <http://galore.readthedocs.io/en/latest/tutorials.html>`__ for a walkthrough using sample data.

The orbital data can also be accessed without working on a particular
spectrum with the ``galore-get-cs`` program. For example::

  galore-get-cs 4 Sn O

will print a set of valence orbital weightings for Sn and O
corresponding to a 4 keV hard x-ray source.
These values have been converted from atomic orbital data
to *per electron* cross-sections.

The ``galore-plot-cs`` program is provided for plotting over a range
of energies using the high-energy fitted data::

  galore-plot-cs Pb S --emin 2 --emax 10 -o PbS.pdf

generates a publication-quality plot of cross-sections which may help
in the selection of appropriate HAXPES energies for experiments with
a given material.

Requirements
------------

Galore is currently compatible with Python 3.4+. Python 2.7 is no longer
supported as many scientific Python libraries are committed to dropping Python
2 support `by the end of 2020 <http://www.python3statement.org>`__.

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
Anaconda shell::

    pip3 install .

Linux/Mac developer installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the directory containing this README::

    pip3 install --user -e .

which installs an *editable* (``-e``) version of galore in your
userspace. The executable program ``galore`` goes to a user directory
like ``~/.local/bin`` (which may need to be added to your PATH) and
the galore library should be available on your PYTHONPATH. These are
links to the project source folder, which you can continue to edit and
update using Git.

To import data from VASP calculations you will need the Pymatgen
library. If you don't have Pymatgen yet, the requirements can be added
to the Galore installation with by adding ``[vasp]`` to the pip
command e.g.::

   pip3 install --user -e .[vasp]

Installation for documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to build the documentation you can add ``[docs]`` to the
pip command to ensure you have all the Sphinx requirements and
extensions::

   pip3 install --upgrade .[docs]

Support
-------

If you're having trouble with Galore or think you've found a bug, please
report it using the
`Github issue tracker <https://github.com/SMTG-UCL/galore/issues>`__.
Issues can also be used for questions and discussion about the Galore
methodology/implementation.

Development
-----------

This code is developed by the Scanlon Materials Theory Group based at
University College London. Suggestions and contributions are welcome;
please read the CONTRIBUTING guidelines and use the Github issue tracker.

How to cite Galore
------------------

If you use Galore in your research, please consider citing the following work:

    Adam J. Jackson, Alex M. Ganose, Anna Regoutz, Russell G. Egdell, David O. Scanlon (2018). *Galore: Broadening and weighting for simulation of photoelectron spectroscopy.* Journal of Open Source Software, 3(26), 773, `doi: 10.21105/joss.007733 <https://doi.org/10.21105/joss.00773>`_

Galore includes a machine-readable
`citation file <https://github.com/SMTG-UCL/galore/blob/master/CITATION.cff>`__
in an `emerging standard format <https://citation-file-format.github.io>`__
with citation details for the actual code,
but as conventions for software citation are still developing
the JOSS paper is a more reliable method of giving credit.

License
-------

Galore is made available under the GNU Public License, version 3.


Acknowledgements
----------------

Development work by Adam J. Jackson took place in the course of
research into new transparent conducting materials, led by
David O. Scanlon and funded by EPSRC (project code EP/N01572X/1).
Work by Alex M. Ganose was supported by a studentship co-sponsored by
the Diamond Light Source at the EPSRC Centre for Doctoral Training in
Molecular Modelling and Materials Science (EP/L01582/1).  Anna Ragoutz
was our expert advisor on all things PES, guiding the feature-set and
correcting the implementation of weighting, and was supported by an
Imperial College Research Fellowship.

We acknowledge useful discussions with Alexey Sokol (who proposed that
a code such as this would be useful), Katie Inzani, and
Tim Veal. Feature requests and user testing came from Benjamin
Williamsion, Christopher Savory and Winnie L. Leung.

This would have been much more painful if not for the excellent
scientific Python ecosystem, and the Python Materials Genome project
spared us the pain of writing Yet Another Vasp Parser.
