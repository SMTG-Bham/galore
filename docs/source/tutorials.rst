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
(e.g. ``IBRION = 8`` and ``LEPSILON = .TRUE.``) and follow-up with the
analysis script found at ADDRESS. A sample output file is provided for
CaF\ `2`:sub: (computed within the local-density approximation using a 700 eV
plane-wave cutoff) is included as *test/CaF2/ir_lda_700.txt*.

This file (found as XXX/YYY/results.dat after running the script) uses
a three-column space-separated format understood by Galore. To plot
the spectrum to screen with some broadening then we can use:

..

  galore test/CaF2/ir_lda_700.txt -g 0.5 -l --plot

Breaking down this command: First we provide the path to a data
file. This can also appear elsewhere in the argument string, but as
many flags take optional arguments it is safest to put it
first. ``-g`` applies Gaussian broadening; here we specify a width of
0.5. This will use the same units as the x-axis; in this case cm\
`-1`:sup:. ``-l`` applies Lorentzian broadening; as no width is
specified, the default 2 cm\ `-1`:sup: will be used.
