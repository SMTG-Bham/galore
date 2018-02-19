.. _cli:

Command-line interface
======================

The main interface for Galore is the ``galore`` command.
Additionally, the ``galore-get-cs`` program is provided for
convenient access to cross-section data.

galore
------

.. argparse::
   :module: galore.cli.galore
   :func: get_parser
   :prog: galore


galore-get-cs
-------------

.. argparse::
   :module: galore.cli.galore_get_cs
   :func: get_parser
   :prog: galore-get-cs
