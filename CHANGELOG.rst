Change Log
==========

Notable changes are logged here by release. This project uses `Semantic
Versioning <http://semver.org/>`__. The changelog format is inspired by
`keep-a-changelog <https://github.com/olivierlacan/keep-a-changelog>`__.

`Unreleased <https://github.com/smtg-ucl/galore/compare/0.2.0...HEAD>`__
-------------------------------------------------------------------------


`[0.2.0] <https://github.com/smtg-ucl/galore/compare/0.1.0...0.2.0>`__ - 2017-09-29
-----------------------------------------------------------------------------------

-  Gaussian broadening added. In the CLI, this stacks with Lorentzian
   broadening. Specified as a FWHM.
-  Text file output
-  Support for PDOS plotting
-  Read vasprun.xml files using Pymatgen
-  XPS simulation tools; x-axis flipping and PDOS contributions weighted
   by cross-section.
-  Documentation including tutorials, hosted at http://galore.readthedocs.io/en/latest/
-  Fancy formatting of units
-  Support for files from `David Karhanek's IR analysis script <http://homepage.univie.ac.at/david.karhanek/downloads.html#Entry02>`__
   and the `raman-sc program <https://github.com/raman-sc/VASP>`__ for simulated optical spectra.
-  Source repository made public
- Python API refactored for cleaner scripts


[0.1.0] - 2016-08-11
--------------------

Added
~~~~~

-  Initial prototype from random data
-  Convolution algorithm used to apply Lorentzian broadening
-  command-line interface
-  Plotting to screen and file
-  Test framework
-  setuptools-based distribution
