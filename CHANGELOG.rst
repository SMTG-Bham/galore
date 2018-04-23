Change Log
==========

Notable changes are logged here by release. This project uses `Semantic
Versioning <http://semver.org/>`__. The changelog format is inspired by
`keep-a-changelog <https://github.com/olivierlacan/keep-a-changelog>`__.

`Unreleased <https://github.com/smtg-ucl/galore/compare/0.5.0...HEAD>`__
-------------------------------------------------------------------------

`[0.5.0] <https://github.com/smtg-ucl/galore/compare/0.4.0...0.5.0>`__ - 2018-04-22
-----------------------------------------------------------------------------------
- Resample with interpolation by default; use "spikes" only when requested

`[0.4.0] <https://github.com/smtg-ucl/galore/compare/0.3.0...0.4.0>`__ - 2018-04-17
-----------------------------------------------------------------------------------
- Import (P)DOS from ``.gpw`` files generated with GPAW. This requires GPAW to be available.
- galore-plot-sc tool for convenient plotting of cross-section data

`[0.3.0] <https://github.com/smtg-ucl/galore/compare/0.2.0...0.3.0>`__ - 2018-02-19
-----------------------------------------------------------------------------------

- BUGFIX: Yeh/Lindau weightings for partially-occupied orbitals
- BUGFIX: Odd behaviour in s orbitals including one transcription error
- Expanded weighting features: HAXPES data parametrised from Scofield tables
- Verbose output including cross sections, warnings and data source citations
- galore-get-sc tool for direct access to cross-section data
- Change Yeh labels from 'xps', 'ups', 'haxpes' to 'alka', 'he2', 'yeh_haxpes'

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
