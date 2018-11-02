.. _cli:

Command-line interface
======================

The main interface for Galore is the ``galore`` command.
Additionally, the ``galore-get-cs`` program is provided for
convenient access to cross-section data.

Style files
~~~~~~~~~~~

Advanced plot styling can be managed with style files. Galore uses
Matplotlib for plotting. The ``--style`` option allows you to pass
in the name of a default style (try `dark_background`) or the path
to a file containing keywords and values. For more information and
a sample file see the Matplotlib docs
`here <https://matplotlib.org/tutorials/introductory/customizing.html>`__.

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


galore-plot-cs
--------------

.. argparse::
   :module: galore.cli.galore_plot_cs
   :func: get_parser
   :prog: galore-plot-cs
