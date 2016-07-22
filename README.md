# Galore

## Introduction

Apply Gaussian and Lorentzian broadening to data from *ab initio*
calculations. The two main intended applications are

1. Application of Lorentzian instrumental broadening to simulated
   Raman spectra from DFPT calculations.
2. Gaussian broadening of electronic density-of-states to simulate XPS
   data, followed by Lorentzian instrumental broadening.

## Usage

#### Instrumental broadening
Data may be provided as a set of X,Y coordinates in a text file of
comma-separated values (CSV).

#### XPS simulation

For data calculated with VASP, the atom types are read from a POSCAR
file and the DOS is read from the DOSCAR.

## Requirements

Galore uses Numpy to apply convolution operations. Matplotlib is
required for plotting.

## Development

This code is developed by the Scanlon Materials Theory Group based at
University College London. As a result, development prioritises the
needs of this group. Other suggestions and contributions are welcome;
please use the Github issue tracker.

## License
Galore is made available under the GNU Public License, version 3.
