Tutorials
=========

Simulated IR
------------

The first-order infra-red absorption spectrum can be simulated by
performing lattice dynamics calcululations to obtain the Γ-point
vibrational mode frequencies. The dielectric response of the system
determines the relative intensities of the modes, and some will be
inactive for symmetry reasons.

If you have the VASP quantum chemistry code, the simplest way to
compute these properties is with a single DFPT calculation
(e.g. ``IBRION = 7``, ``LEPSILON = .TRUE.``, ``NWRITE = 3``)
and follow-up with
`David Karhanek's analysis script <http://homepage.univie.ac.at/david.karhanek/downloads.html#Entry02>`__.
A sample output file is provided for
CaF\ `2`:sub: (computed within the local-density approximation using a 700 eV
plane-wave cutoff) is included as *test/CaF2/ir_lda_700.txt*.

This file (found as *intensities/results/results.txt* after running the script) uses
a three-column space-separated format understood by Galore. To plot
the spectrum to screen with some broadening then we can use:

.. code-block:: bash

  galore test/CaF2/ir_lda_700.txt -g 0.5 -l --plot

Breaking down this command: First we provide the path to a data
file. This can also appear elsewhere in the argument string, but as
many flags take optional arguments it is safest to put it
first. ``-g`` applies Gaussian broadening; here we specify a width of
0.5. This will use the same units as the x-axis; in this case cm\
`-1`:sup:. ``-l`` applies Lorentzian broadening; as no width is
specified, the default 2 cm\ `-1`:sup: will be used. This is generally
a sensible value for optical measurements, but some tuning may be
needed.  Finally ``--plot`` will cause Galore to print to the screen
using Matplotlib. (``-p`` can also be used a short form.)

To see the full list of command-line arguments you can use ``galore
-h`` or check the :doc:`cli` section in this manual.

.. image:: figures/ir_lda_700_quick.png
           :alt: IR output plot without adjustments
           :align: center
           :scale: 50%

Admittedly it isn't the most exciting spectrum, with a single peak
around 280 cm\ `-1`:sup:. Let's make some adjustments: we'll add a
touch more Gaussian broadening, zoom in on the peak by limiting the
axis range, add axis labels and write to a file.

.. code-block:: bash

  galore test/CaF2/ir_lda_700.txt -g 1.2 -l \
    --plot docs/source/figures/ir_lda_700_better.png \
    --xmin=200 --xmax=350 --units cm-1 --ylabel Intensity

.. image:: figures/ir_lda_700_better.png
           :alt: IR output plot with adjustments
           :align: center
           :scale: 50%

Now the plot is more publication-ready! If you would like to use
another plotting program, the broadened data can be output to a CSV
file by simply replacing ``--plot`` with ``--csv``:

.. code-block:: bash

  galore test/CaF2/ir_lda_700.txt -g 1.2 -l --csv --xmin=200 --xmax=350

will write a csv file to the standard output as no filename was
given. We can also write space-separated text data, so for example

.. code-block:: bash

    galore test/CaF2/ir_lda_700.txt -g 1.2 -l --txt ir_CaF2_broadened.txt

generates a file with two columns (i.e. energy and broadened intensity).


Simulated Photoionization Spectroscopy
--------------------------------------

Photoionization measurements allow valence band states to be probed
fairly directly; energy is absorbed by an incident photon as it ejects
an electron from the sample, and the shift in energy is measured
relative to a monochromatic photon source. Ultraviolet photoelectron
spectroscopy (UPS), x-ray photoelectron spectroscopy (XPS) and Hard
x-ray photoelectron spectroscopy (HAXPES) are fundamentally similar
techniques, differing in the energy range of the incident photons.

These binding energies may be compared with the full density
of states (DOS) computed with *ab initio* methods. However, the
intensity of interaction will vary depending on the character of the
energy states and the energy of the radiation source. The relevant
interaction parameter ("photoionization cross-section") has been
calculated systematically over the periodic table and relevant energy
values; Galore includes some such data from
`Yeh and Lindau (1985) <https://doi.org/10.1016/0092-640X(85)90016-6>`__.

In *ab initio* codes it is often possible to assign states to
particular orbital characters; often this is limited to s-p-d-f
(i.e. the second quantum number) but in principle an all-electron
codes can also assign the first quantum number. Directional character
is also sometimes assigned, usually relative to the crystallographic
axes. These various schemes are used to construct a "projected density
of states" (PDOS).

The construction of a PDOS in *ab initio* calculations is slightly
arbitrary and lies beyond the scope of Galore. However, when the
orbital assignment has been made the DOS elements can be weighted to
simulate the photoionization spectrum.

We begin by plotting a PDOS from sample data in *test/MgO*. This was
computed using VASP with standard pseudopotentials and the revTPSS
exchange-correlation functional.

.. code-block:: bash

     galore test/MgO/MgO_Mg_dos.dat test/MgO/MgO_O_dos.dat \
       --plot --pdos -g 0.2 -l 0.2 --ylabel DOS

.. image:: figures/mgo_pdos_quick.png
           :alt: Quick PDOS plot for MgO
           :align: center
           :scale: 50%

Note that the ``--pdos`` flag is required to interpret the multiple
input files. The element identity is read from these filenames, and is
expected between two underscore characters. The orbital names are
determined from the column headers in this file.

Let's turn this into a useful XPS plot. The flag ``--xps`` can be used
to pass a data file with cross-section data, or defaults to use data
for Al k-α radiation. It also flips the x-axis to match the usual
presenation of XPS data as positive ionisation or binding energies
rather than the negative energy of the stable electron states.

.. code-block:: bash

    galore test/MgO/MgO_Mg_dos.dat test/MgO/MgO_O_dos.dat \
      --plot mgo_xps.png --pdos -g 0.2 -l 0.2 --xps \
      --units ev --xmin -1 --xmax 8 --ylabel Intensity
      
.. image:: figures/mgo_xps.png
           :alt: Simulated XPS for MgO
           :align: center
           :scale: 50%
