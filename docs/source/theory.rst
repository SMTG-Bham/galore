******
Theory
******

A short academic paper is in preparation which gives an overview of
Galore's applications. Some of that information is repeated here;
this section of the user guide aims to provide essential information
and refer to the academic literature for those seeking more depth and
context.

Photoelectron spectroscopy
==========================


History
-------

Photoelectron spectroscopy (PES) is a family of methods used to
characterise the chemical nature and electronic structure of
materials.
PES is based on the photoelectric effect, which was discovered by
Hertz. :cite:`Hertz1887`
It was explored extensively by Rutherford and colleagues
:cite:`Rutherford1914`
and within a few years researchers including de Broglie :cite:`deBroglie1921`
and Robinson :cite:`Robinson1923`
were using the technique to measure electron binding energies through
the relationship

.. math::
   E_\text{k} = h\nu - E_\text{B}.

Photons with energies :math:`h\nu` ranging from 5 eV up to 12 keV eject
electrons (referred to as "photoelectrons") from the occupied
orbitals of a sample. The kinetic energy :math:`E_\text{k}` of each
photoelectron therefore depends on its binding energy :math:`E_\text{B}`.
The names of various PES methods refer to the photon energy range used:

- ultraviolet photoelectron spectroscopy (UPS): 5--100 eV
- X-ray photoelectron spectroscopy (XPS): 0.3--2 keV
- hard X-ray photoelectron spectroscopy (HAXPES, HE-PES, HXPS, HX-PES): above 2 keV

Broadening
----------

Major sources of broadening include:

- Intrinsic lifetime broadening (Lorentzian)

  - While this can play a significant role, the lifetime broadening is
    energy-dependent and care should be taken when applying it across
    the full data set.
    
- Franck--Condon phonon broadening (Gaussian)  

  - This is caused by vibrations in the system which lead to a
    distribution of accessible photoionization energies.

  - In oxides this is associated with as much as 0.8 eV broadening
    
- Instrumental broadening (Gaussian)

  - Typical values are in the range 0.2--0.3 eV.

Weighting
---------

The Gelius model
""""""""""""""""

The Gelius model was originally developed to describe molecular systems. :cite:`Gelius1972,Gelius1972a,Gelius1974`

Asymmetry corrections
"""""""""""""""""""""
    
References
----------
.. bibliography:: references.bib
   :style: unsrt
