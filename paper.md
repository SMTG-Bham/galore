---
title: 'Galore: Gaussian and Lorentzian broadening of simulated spectra'
tags:
  - ab initio
  - density of states
  - photoemission
  - raman spectroscopy
  - ir spectroscopy
  - chemistry
  - physics
authors:
  - name: Adam J Jackson
    orcid: XXX
    affiliation: 1
  - name: Alex M Ganose
    orcid: XXX
    affiliation: 1,2
  - name: David O Scanlon
    orcid: XXX
    affiliation: 1,2
affiliations:
  - name: Dept of Chemistry, University College London, 20 Gordon Street, London WC1H 0AJ, UK
    index: 1
  - name: Diamond Light Source Ltd., Diamond House, Harwell Science and Innovation Campus, Didcot, Oxfordshire OX11 0DE, UK
    index: 2
date: September 2017
bibliography: paper.bib
---

In the analysis of chemical systems, physical measurements are often
obtained as diffuse _spectra_ where a model system would be occupied
at discrete levels. In order to compare simulated and measured spectra
it is commonplace to broaden the model values by convolution with a
Gaussian-Lorentzian function [@Hills1975, @Grevels1998]. Accounting in
this way for both the genuine bandwidth of physical interactions and
for instrumental limitations allows for direct comparisons to be made.

The features of Galore are based on two cases, particularly relevant
to materials chemistry: vibration spectroscopy and photoemission
spectroscopy.

### Vibrational spectroscopy (IR and Raman)

In infrared (IR) spectroscopy, low-energy photons are absorbed
corresponding to the energies of lattice vibrations and an absorption
spectrum is obtained. In a highly-crystalline system, symmetry
selection rules limit the absorption activity to a small
number of possible excitations with zero crystal momentum
("Gamma-point phonons"). In Raman spectroscopy another optical method
is used to observe lattice vibrations and different selection rules
apply; however, again the resulting spectrum corresponds to a limited
selection of Gamma-point movements.

It is possible to predict the frequencies and intensities of these
vibrational modes by performing *ab initio* lattice dynamics
calculations. Usually these will be performed within the
generalised-gradient approximation within density-functional theory
(DFT), using variations of density-functional perturbation theory
(DFPT) or the frozen-phonon ("direct") method [@Gonze1997; @Parlinski1997; @Togo2008].
The Phonopy package is a popular open-source tool for managing
frozen-phonon calculations with a range of DFT codes [@Togo2015].
Scripts are available for intensity
calculation:
David Karhanek's IR intensity script [-@karhanek] does
not have a Free Software license at this point in time; Fonari and
Stauffer have published a program under the MIT license for
calculating Raman intensities.[@vasp_raman_py] Theoretical Raman
linewidths can be computed using higher-order phonon calculations, but
in practice it is helpful to apply additional Lorentzian
broadening.[@Skelton2014, @Togo2015a, @Skelton2015]


### Photoemission spectroscopy

Photoemission/photoionization/photoelectron (PE) spectroscopy is a
family of methods in which high-energy photons eject electrons from
the stable electronic structure of a sample and the momentum of this
electron is used to determine the "binding energy" which originally
held it. The names of various PE methods refer to the energy range
and/or equipment involved:
- ultraviolet photoelectron spectroscopy (UPS)
- X-ray photoelectron spectroscopy (XPS)
- hard X-ray photoelectron spectroscopy (HAXPES, HXPS, HX-PES, ...)

These methods are not restricted by symmetry in the way vibrational
spectroscopy is and generate broad spectra related to the electronic
density of states (DOS). Computing the DOS is a routine part of *ab
initio* materials chemistry; the "total energy" of any such
calculation is ultimately an integral over the occupied states. When
comparing the computed DOS with a measured PE spectrum it becomes
clear that the broadening plays a very significant role in
interpretation, often merging multiple peaks into a single visible
peak with a different energy value [@Veal2015, @Savory2016, @Sathasivam2017].

The other processing step is the weighting of contributions by their
photoionisation cross-sections.
Data is included for some standard energy values, from tabulated ab
initio calculations.[@Yeh1985] This determines the different shapes
observed in the valence band edge when examined with different x-ray
sources.

## Galore

Galore provides a command-line tool and Python API for 
- importing data
- resampling it to a dense, regular X-Y series
- generating a weighted total of multiple data series
- convoluting this series with Gaussian and Lorentzian functions
- plotting or exporting the broadened data

Data can be imported from simple tabular data files, or the
orbital-projected electronic density of states (DOS) can be imported
directly from calculations with the Vienna Ab Initio Simulations
Package (VASP).

The Gaussian and Lorentzian functions follow standard general forms:
$$
y = \exp \left( \frac{-(f - f_0)^2}{2 * \gamma**2} \right)
$$
and
$$
y = \frac{0.5 \gamma}{\pi (f - f_0)^2 + (0.5 \gamma)**2}
$$

where $f$ is the x-axis value, $f_0$ is the mid-point, $\gamma$ controls the width.

# Acknowledgements

Development work by AJJ took place in the course of research into new
transparent conducting materials, led by David O. Scanlon and funded
by EPSRC (project code EP/N01572X/1).  Work by AMG was supported by a
studentship co-sponsored by the Diamond Light Source at the EPSRC
Centre for Doctoral Training in Molecular Modelling and Materials
Science (EP/L01582/1).

We acknowledge useful discussions with Alexei Sokol (who proposed that
a code such as this would be useful), Katie Inzani, Anna Regoutz and
Tim Veal. Feature requests and user testing came from Benjamin
Williamsion, Christopher Savory and Winnie L. Leung.

This would have been much more painful if not for the excellent
scientific Python ecosystem, and the Python Materials Genome project
spared us the pain of writing Yet Another Vasp Parser.

# References
