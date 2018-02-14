---
title: 'Galore: Broadening and weighting for simulation of photoelectron spectroscopy'
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
    orcid: 0000-0001-5272-6530
    affiliation: 1
  - name: Alex M Ganose
    orcid: 0000-0002-4486-3321
    affiliation: 1,2
  - name: Anna Regoutz
    orcid: 0000-0002-3747-3763
    affiliation: 3
  - name: David O Scanlon
    orcid: 0000-0001-9174-8601
    affiliation: 1,2
affiliations:
  - name: Dept of Chemistry, University College London, 20 Gordon Street, London WC1H 0AJ, UK
    index: 1
  - name: Diamond Light Source Ltd., Diamond House, Harwell Science and Innovation Campus, Didcot, Oxfordshire OX11 0DE, UK
    index: 2
  - name: Dept of Materials, Imperial College London, London SW7 2AZ, UK
  - index: 3
date: February 2018
bibliography: paper.bib
---

Galore simplifies and automates the process of simulating
photoelectron spectra from _ab initio_ calculations.
This replaces the tedious process of extracting and interpolating
cross-sectional weights from reference data and generates tabulated
data or publication-ready plots as needed.
The broadening tools may also be used to obtain realistic diffuse
spectra from a theoretical set of discrete lines (e.g. infrared or
Raman spectroscopy).

### Photoelectron spectroscopy

Photoelectron spectroscopy (PES) is a family of methods used to
characterise the chemical nature and electronic structure of
materials.
XPS is based on the photoelectric effect, which was discovered by
Hertz in 1887, and later refined by Rutherford in 1914 as
$$E_\text{k} = h\nu - E_\text{B}.$$
Photons with energies $h\nu$ ranging from 5 eV up to 12 keV eject
electrons (referred to as "photoelectrons") from the occupied
orbitals of a sample. The kinetic energy $E_\text{k}$ of each
photoelectron therefore depends on its binding energy $E_\text{B}$.
The names of various PES methods refer to the photon energy range used:

- ultraviolet photoelectron spectroscopy (UPS): 5--100 eV
- X-ray photoelectron spectroscopy (XPS): 0.3--2 keV
- hard X-ray photoelectron spectroscopy (HAXPES, HE-PES, HXPS, HX-PES): above 2 keV

These methods generate spectra that are directly related
to the electronic density of states (DOS),
a distribution which is routinely calculated in _ab initio_
materials chemistry.
When comparing the computed DOS with a PES measurement, it is often
possible to identify general peak agreement simply by inverting the
energy scale (i.e. replace a positive binding energy with a negative
orbital energy), applying a little broadening, and shifting the energy
scale to account for different energy references.
This approach is taken in, e.g. @Veal2015 and @Savory2016.
Broadening is generally applied by convolution with a Gaussian
and/or Lorentzian function: intrinsic lifetime broadening causes a
Lorentzian energy distribution of the photoelectrons, whilst instrumental
factors, including the width of the X-ray source and analyser resolution,
give rise to a Gaussian line shape.

Photoemission spectra for the same material will vary depending on the
radiation source used.
The probabilities of the underlying photoionisation events are based
on the radiation and orbital energies, as well as the shape of the
orbital.
In order to account for this it is necessary to apply weighting to
states according to their photoionisation cross-sections.
This is accomplished by projecting the full DOS onto contributions
from atomic _s_, _p_, _d_, _f_ orbitals (PDOS), as is done
routinely in analysis of _ab initio_ calculations.
It is then assumed that the contributions of these orbital-projected
states to the total photoelectron spectrum will be proportional to
the photoionisation cross-sections of corresponding orbitals in free atoms.
These cross-sections have been computed by several methods and are
available as reference data (e.g. @Yeh1985).
Implemented with ad-hoc scripts and spreadsheets, this method has
already been used in a number of academic studies
(e.g. @Farahani2014, @Sathasivam2017).

![Procedure (left to right) for simulated photoelectron spectrum from _ab initio_ DOS](docs/source/figures/pe_schematic.pdf)

For further information about PES there are some helpful reviews in the
academic literature, including @Huefner2005, @Fadley2009 and @Fadley2010.

### Vibrational spectroscopy (IR and Raman)

In infrared (IR) spectroscopy, low-energy photons are absorbed
corresponding to the energies of lattice vibrations and an absorption
spectrum is obtained. In a highly-crystalline system, symmetry
selection rules limit the absorption activity to a small
number of possible excitations with zero crystal momentum
("Gamma-point phonons"). In Raman spectroscopy another optical method
is used to observe lattice vibrations and different selection rules
apply; again, the resulting spectrum corresponds to a limited
selection of Gamma-point movements.

It is possible to predict the frequencies and intensities of these
vibrational modes by performing *ab initio* lattice dynamics
calculations. Usually these will be performed within density-functional theory
(DFT), either using variations of density-functional perturbation theory
(DFPT) (based on the work of @Gonze1997)
or the frozen-phonon ("direct") method  [@Parlinski1997; @Togo2008].
When the underlying set of vibrational frequencies and mode
intensities has been calculated it is typical to broaden the data by
convolution with a Gaussian--Lorentzian function [e.g. @Hills1975; @Grevels1998].
This is necessary to correctly intepret the effect of overlapping
peaks; for example, Figure 2 shows a case in which a group of peaks
with low intensities combine to form a large peak in the broadened
spectrum.

![Schematic example of misleading peak intensities due to overlap](docs/source/figures/ir_schematic.pdf)

<!-- It is possible to predict the frequencies and intensities of these -->
<!-- vibrational modes by performing *ab initio* lattice dynamics -->
<!-- calculations. Usually these will be performed within the -->
<!-- generalised-gradient approximation within density-functional theory -->
<!-- (DFT), using variations of density-functional perturbation theory -->
<!-- (DFPT) or the frozen-phonon ("direct") method [@Gonze1997; @Parlinski1997; @Togo2008]. -->
<!-- The Phonopy package is a popular open-source tool for managing -->
<!-- frozen-phonon calculations with a range of DFT codes [@Togo2015]. -->
<!-- Scripts are available for intensity -->
<!-- calculation: -->
<!-- David Karhanek's IR intensity script [-@karhanek] does -->
<!-- not have a Free Software license at this point in time; Fonari and -->
<!-- Stauffer have published a program under the MIT license for -->
<!-- calculating Raman intensities [@vasp_raman_py]. Theoretical Raman -->
<!-- linewidths can be computed using higher-order phonon calculations, but -->
<!-- in practice it is helpful to apply additional Lorentzian -->
<!-- broadening [@Skelton2014, @Togo2015a, @Skelton2015]. -->

## Galore

Galore provides a command-line tool and Python API to import data and
resample it to a dense, regular X-Y series.
This mesh can then be convoluted with Gaussian and Lorentzian functions
to yield a smooth output, in the form of a plot or data file.
Numpy functions are used for data manipulation and convolution on a
finite grid and Matplotlib is used for plotting [@Numpy2011; @Hunter2007].
As well as simple tabular data files, the electronic DOS or PDOS may
be imported directly from the output of the Vienna Ab Initio
Simulations Package (VASP).

The Gaussian and Lorentzian functions employed have the forms:
$$
y = \exp \left( \frac{-(f - f_0)^2}{2 c^2} \right) \quad \text{where} \quad c = \frac{\gamma}{2 \sqrt{2 \log 2}}
$$
and
$$
y = \frac{0.5 \gamma}{\pi (f - f_0)^2 + (0.5 \gamma)^2}
$$

where $f$ is the x-axis value, $f_0$ is the mid-point, $\gamma$ is the
full-width-half-maximum of the peak.

Cross-sectional weights are included for some standard energy values
(He(II) UPS and Al k-alpha) from tabulated ab initio calculations
[@Yeh1985].
Users may provide their own weighting values in the same
human-readable JSON file format.
Higher-energy (HAXPES) spectra may be simulated using cross-sections
from fitted data over an energy range 1-1500 keV.
Tabulated data [@Scofield1973] was fitted to an order-8
polynomial on a log-log scale, and coefficients for each element and
orbital shape are stored in a database file. The fitting error is
generally below 1%, with outliers in the region of 2--3%.
The order-8 fit was selected based on cross-validation in order to
avoid over-fitting.

![Cross-validation error of HAXPES data fitting over full energy range across all elements and orbitals](docs/source/figures/haxpes_fit_paper.pdf)


# Acknowledgements

Development work by AJJ took place in the course of research into new
transparent conducting materials, led by David O. Scanlon and funded
by EPSRC (project code EP/N01572X/1).  Work by AMG was supported by a
studentship co-sponsored by the Diamond Light Source at the EPSRC
Centre for Doctoral Training in Molecular Modelling and Materials
Science (EP/L01582/1).

We acknowledge useful discussions with Alexey Sokol (who proposed that
a code such as this would be useful), Katie Inzani and
Tim Veal. Feature requests and user testing came from Benjamin
Williamson, Christopher Savory and Winnie L. Leung.

This would have been much more painful if not for the excellent
scientific Python ecosystem, and the Python Materials Genome project
spared us the pain of writing Yet Another Vasp Parser.

# References
