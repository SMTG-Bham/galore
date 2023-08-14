Change Log
==========

Notable changes are logged here by release. This project uses `Semantic
Versioning <http://semver.org/>`__. The changelog format is inspired by
`keep-a-changelog <https://github.com/olivierlacan/keep-a-changelog>`__.

`Unreleased <https://github.com/smtg-ucl/galore/compare/0.9.0...HEAD>`__
-------------------------------------------------------------------------

`[0.9.0] <https://github.com/smtg-ucl/galore/compare/0.8.0...0.9.0>`__ - 2023-08-14
-----------------------------------------------------------------------------------
- Minimum Python version has increased to 3.8
- Allow --xflip to be used with simple 1-d data plots (@ajjackson)
- BUGFIX: Import type annoations from collection.abc. This is required
  for Python 3.10, which deprecates the original location. (@Hashan-Peiris)

`[0.8.0] <https://github.com/smtg-ucl/galore/compare/0.7.0...0.8.0>`__ - 2023-02-28
-----------------------------------------------------------------------------------
- Minimum Python version has increased to 3.7
- Orbital-projected plots have gained pretty fill colours; these are
  controlled by `--no-fill`, `--no-total`, `--alpha` and
  `--legend-cutoff` command-line options. (@kavanase)

`[0.7.0] <https://github.com/smtg-ucl/galore/compare/0.6.2...0.7.0>`__ - 2021-07-06
-----------------------------------------------------------------------------------
- Continuous integration has been migrated from Travis to Github Actions
- Minimum Python version has been increased to 3.5.

  - Python 3.4 was not available through Github actions. It is not wise to
    support a platform we cannot test.

- BUGFIX: missing import affecting process_pdos

`[0.6.2] <https://github.com/smtg-ucl/galore/compare/0.6.1...0.6.2>`__ - 2021-05-24
-----------------------------------------------------------------------------------
- Updated setup.py to add a [vasp] extra; this handles Pymatgen
  installation which can be tricky on older Python versions.
- Update the [vasp] extra to handle some compatibility breaks between
  dependencies and different Python versions.
- Fix some incorrect values in Al k-alpha XPS cross-sections
- BUGFIX: Pymatgen CompleteDOS was not correctly accepted by galore.process_pdos()
- Implement previously ineffective "offset" option in
  galore.plot.plot_pdos(), add a matching option to
  galore.plot.plot_tdos()

`[0.6.1] <https://github.com/smtg-ucl/galore/compare/0.6.0...0.6.1>`__ - 2018-11-19
-----------------------------------------------------------------------------------
- BUGFIX: PDOS plot was failing for elemental systems

`[0.6.0] <https://github.com/smtg-ucl/galore/compare/0.5.1...0.6.0>`__ - 2018-11-02
-----------------------------------------------------------------------------------
- Matplotlib styling is exposed to the user: ``--style`` option selects CLI style
  while Python API does not overrule existing style.
- The default TDOS line colour is now the first colour from the
  selected style, which is usually blue. The previous default was a
  bright red.
- Pymatgen CompleteDos objects can be processed directly.
- Dropped Python 2.7 compatability.
- Fixed PDOS bug introduced with Python3 cleanup
  

`[0.5.1] <https://github.com/smtg-ucl/galore/compare/0.5.0...0.5.1>`__ - 2018-05-03
-----------------------------------------------------------------------------------
- galore-plot-sc can optionally show values in Megabarn/electron

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
