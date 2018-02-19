Tutorials
=========

Simulated IR
------------

The first-order infra-red absorption spectrum can be simulated by
performing lattice dynamics calculations to obtain the Γ-point
vibrational mode frequencies. The dielectric response of the system
determines the relative intensities of the modes, and some will be
inactive for symmetry reasons.

If you have the VASP quantum chemistry code, the simplest way to
compute these properties is with a single DFPT calculation
(e.g. ``IBRION = 7``, ``LEPSILON = .TRUE.``, ``NWRITE = 3``)
and follow-up with
`David Karhanek's analysis script <http://homepage.univie.ac.at/david.karhanek/downloads.html#Entry02>`__.
A sample output file is provided for CaF\ `2`:sub: (computed within
the local-density approximation (LDA) using a 700 eV plane-wave
cutoff) is included as *test/CaF2/ir_lda_700.txt*.

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
using Matplotlib. (The abbreviation ``-p`` can also be used.)

To see the full list of command-line arguments you can use ``galore
-h`` or check the :doc:`cli` section in this manual.

.. image:: figures/ir_lda_700_quick.png
           :alt: IR output plot without adjustments
           :align: center
           :scale: 50%

Admittedly, it isn't the most exciting spectrum, with a single peak
around 280 cm\ `-1`:sup:. Let's make some adjustments: we'll add a
touch more Gaussian broadening, zoom in on the peak by limiting the
axis range, add axis labels and write to a file.

.. code-block:: bash

  galore test/CaF2/ir_lda_700.txt -g 1.2 -l \
    --plot ir_lda_700_better.png \
    --xmin 200 --xmax 350 --units cm-1 --ylabel Intensity

.. image:: figures/ir_lda_700_better.png
           :alt: IR output plot with adjustments
           :align: center
           :scale: 50%

Now the plot is more publication-ready! If you would like to use
another plotting program, the broadened data can be output to a CSV
file by simply replacing ``--plot`` with ``--csv``:

.. code-block:: bash

  galore test/CaF2/ir_lda_700.txt -g 1.2 -l --csv --xmin 200 --xmax 350

This will write a csv file to the standard output as no filename was
given. We can also write space-separated text data, so for example

.. code-block:: bash

    galore test/CaF2/ir_lda_700.txt -g 1.2 -l --txt ir_CaF2_broadened.txt

generates a file with two columns (i.e. energy and broadened intensity).

Simulated Raman
---------------

Broadening a simulated Raman spectrum is very similar to broadening a
simulated IR spectrum. Galore recognises the output format of the
`vasp_raman.py <https://github.com/raman-sc/VASP>`__ code, which
automates the process of following vibrational modes and calculating
the polarisability change on each displacement. The output file has a
simple format and Galore recognises them by inspecting the header.
Sample data is included (computed with LDA using VASP with a 500 eV
cutoff) as *test/CaF2/raman_lda_500.dat*. We generate a plot in the
same way as before:

.. code-block:: bash

    galore test/CaF2/raman_lda_500.dat -g -l --plot --units cm-1 --ylabel Intensity

.. image:: figures/raman_lda_500.png
           :alt: Simulated Raman plot for CaF2
           :align: center
           :scale: 50%

Note that for the same material we are seeing a single peak again, but
at a different frequency to the IR plot. This is not a shift; the peak
at 280 cm\ `-1`:sup: is still present but has zero activity, while the
peak calculated at 345 cm\ `-1`:sup: has zero IR activity.

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
code can also assign the first quantum number. Directional character
is also sometimes assigned, usually relative to Cartesian axes.
These various schemes are used to construct a "projected density
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
       --plot --pdos -g 0.5 -l 0.2 --ylabel DOS --units eV

.. image:: figures/mgo_pdos_quick.png
           :alt: Quick PDOS plot for MgO
           :align: center
           :scale: 50%

Note that the ``--pdos`` flag is required to enable the reading of
orbital-projected input files.  The element identity is read from
these filenames, and is expected between two underscore
characters. The orbital names are determined from the column headers
in this file.

Let's turn this into a useful XPS plot. The flag ``--weightings`` can
be used to pass a data file with cross-section data; for some cases
data is build into Galore. Here we will use the data for Al k-α
radiation which is denoted ``alka`` is built into Galore.  We also flip
the x-axis with ``--flipx`` to match the usual presentation of XPS
data as positive ionisation or binding energies rather than the
negative energy of the stable electron states. Finally the
data is written to a CSV file with the ``--csv`` option.

.. code-block:: bash

    galore test/MgO/MgO_Mg_dos.dat test/MgO/MgO_O_dos.dat \
      --plot mgo_xps.png --pdos -g 0.2 -l 0.2 --weighting alka \
      --units ev --xmin -1 --xmax 8 --ylabel Intensity \
      --csv mgo_xps.csv --flipx

.. image:: figures/mgo_xps.png
           :alt: Simulated XPS for MgO
           :align: center
           :scale: 50%

Plotting the CSV file with a standard plotting package should give a
similar result to the figure above; if not, please report this as a
bug!

Compare with literature: tin dioxide
------------------------------------

Sample VASP output data is included for rutile tin dioxide. This was
computed with the PBE0 functional, using a 4x4x5 **k**-point mesh and
700 eV basis-set cutoff.  The structure was optimised to reduce forces
to below 1E-3 eV Å\ `-1`:sup: using 0.05 eV of Gaussian broadening and
the DOS was computed on an automatic tetrahedron mesh with Blöchl
corrections. Instead of the separate .dat files used above, we will
take advantage of Galore's ability to read a compressed *vasprun.xml*
file directly. This requires the Pymatgen library to be installed::

  pip3 install --user pymatgen

XPS
^^^

.. image:: figures/sno2_xps_data.png
           :alt: Simulated XPS for SnO2 overlaid with experimental data
           :align: center
           :scale: 50%

We have digitised the experimental data plotted in Fig.3 of
`Farahani et al. (2014) <https://doi.org/10.1103/PhysRevB.90.155413>`__
in order to aid a direct comparison::

  galore test/SnO2/vasprun.xml.gz --plot -g 0.5 -l 0.4 \
    --pdos --w alka --flipx --xmin -2 --xmax 10 \
    --overlay test/SnO2/xps_data.csv  --overlay_offset -4 \
    --overlay_scale 3.5 --units ev --ylabel Intensity

(Note that here the shorter alias ``-w`` is used for the XPS
weighting.) The general character and peak positions match well, but
the relative peak intensities could be closer; the first peak is very
strong even with cross-section weightings applied. We can see that the
dip in between the second an third main peak corresponds to a crossing
point between the contributions of the Sn-s and Sn-d orbitals.

A slightly more generous assignment of 'p' vs 'd' character by the
orbital projection scheme would have made for a better fit! The
published results seem to fit better despite using similar calculation
parameters; we can't see if the orbital breakdown is indeed the
determining factor.

UPS
^^^

.. image:: figures/sno2_ups_data.png
           :alt: Simulated XPS for SnO2 overlaid with experimental data
           :align: center
           :scale: 50%

Experimental UPS data was digitized from Fig. 1 of `Themlin et
al. (1990) <https://doi.org/10.1103/PhysRevB.42.11914>`__. A
satisfactory fit is obtained for the three main peaks, but the "bump" below
zero suggests the presence of some phenomenon in the bandgap which was
not captured by the *ab initio* calculation::

  galore test/SnO2/vasprun.xml.gz --plot -g 0.5 -l 0.9 \
    --pdos --w he2 --flipx --xmin -2 --xmax 10 \
    --overlay test/SnO2/ups_data.csv --overlay_offset 0.44 \
    --units ev --ylabel Intensity --overlay_style x    

The authors noted this in their own comparison to a DOS from
tight-binding calculations:

  The location of the VBM in out UPS data was complicated by the
  presence of a slowly varying photoelectron signal, resulting from a
  surface-state band.

HAXPES
^^^^^^

.. image:: figures/sno2_haxpes_data.png
           :alt: Simulated XPS for SnO2 overlaid with experimental data
           :align: center
           :scale: 50%

A HAXPES spectrum was obtained by digitizing Fig. 1 of `Nagata et
al. (2011) <https://doi.org/10.1063/1.3596449>`__. These experiments
were performed with 5.95 keV x-rays, while the weighting parameters
from Yeh and Lindau are for 8.05 keV so an exact match is unlikely::

   galore test/SnO2/vasprun.xml.gz --plot -g 0.3 -l 0.5 --pdos \
     --w yeh_haxpes --flipx --xmin -2 --xmax 10 \
     --overlay test/SnO2/haxpes_data.csv --overlay_offset -3.7 \
     --ylabel Intensity --overlay_style -

We see that the weighting goes some way to rebalancing the peak
intensities but once again the Sn-d states are over-represented.
Surface states above the valence band are also seen again.


Python API
----------

The Python API allows custom plots to be produced by generating data
sets Galore's core functions and passing Matplotlib axes to the
plotting functions. A few examples are provided below. It is not
especially difficult to access the lines plotted to an axis and
manipulate their appearance, rescale them etc.

Overlaying different amounts of broadening
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: figures/api_dos_gaussian.png
           :alt: MgO DOS with different degrees of Lorentzian broadening
           :align: center
           :scale: 60%

.. literalinclude:: api_demo_dos_broadening.py
   :language: python
   :linenos:


Plotting different amounts of broadening on tiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: figures/api_pdos_lorentz.png
           :alt: MgO PDOS with different degrees of Lorentzian broadening
           :align: center
           :scale: 80%

.. literalinclude:: api_demo_pdos_broadening.py
   :language: python
   :linenos:


Comparing different photoemission weightings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: figures/api_demo_weightings.png
           :alt: SnO2 PDOS with different XPS weightings
           :align: center
           :scale: 60%

.. literalinclude:: api_demo_weightings.py
   :language: python
   :linenos:
