###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Adam J. Jackson (2016) at University College London            #
#                                                                             #
###############################################################################
#                                                                             #
# This file is part of Galore. Galore is free software: you can redistribute  #
# it and/or modify it under the terms of the GNU General Public License as    #
# published by the Free Software Foundation, either version 3 of the License, #
# or (at your option) any later version.  This program is distributed in the  #
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the     #
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    #
# See the GNU General Public License for more details.  You should have       #
# received a copy of the GNU General Public License along with this program.  #
# If not, see <http://www.gnu.org/licenses/>.                                 #
#                                                                             #
###############################################################################

from __future__ import print_function
import os
import csv
import sys
import numpy as np

def isdoscar(filename):
    """Determine whether file is a DOSCAR by checking fourth line"""
    with open(filename, 'r') as f:
        for i in range(3):
            f.readline()
        if f.readline().strip() == 'CAR':
            return True
        else:
            return False


def write_txt(x_values, y_values, filename="galore_output.txt", header=None):
    """Write output to a simple space-delimited file

    Args:
        x_values: (iterable) Values to print in first column
        y_value: (iterable) Values to print in second column
        filename: (str) Path to output file, including extension. If False,
            write to standard output instead.
        header: (str) Additional line to prepend to file. If None, no header
            is used.

        """
    lines = ["{x:10.6e} {y:10.6e}\n".format(
        x=x, y=y) for x, y in zip(x_values, y_values)]
    if header:
        lines = [header + "\n"] + lines

    if filename is not None:
        with open(filename, 'w') as f:
            f.writelines(lines)
    else:
        for line in lines:
            print(line, end='')


def write_csv(x_values, y_values, filename="galore_output.csv", header=None):
    """Write output to a simple space-delimited file

    Args:
        x_values: (iterable) Values to print in first column
        y_value: (iterable) Values to print in second column
        filename: (str) Path to output file, including extension. If None,
            write to standard output instead.
        header: (iterable) Additional line to prepend to file. If None,
            no header is used.

        """

    def _write_csv(x_values, y_values, f, header=None):
        writer = csv.writer(f, lineterminator=os.linesep)
        if header is not None:
            writer.writerow(header)
        writer.writerows(zip(x_values, y_values))

    if filename is None:
        _write_csv(x_values, y_values, sys.stdout, header=header)

    else:
        with open(filename, 'w') as f:
            _write_csv(x_values, y_values, f, header=header)


def read_pdos_txt(filename):
    """Read a text file containing projected density-of-states (PDOS) data

    The first row should be a header identifying the orbitals, e.g.
    "# Energy s p d f". The following rows contain the corresponding energy and
    DOS values.

    Args:
        filename (str): Path to file for import

    Returns:
        data (np.ndarray): Numpy structured array with named columns
            corresponding to input data format.
    """
    data = np.genfromtxt(filename, names=True)
    return data
    

def read_doscar(filename="DOSCAR"):
    """Read an x, y series of frequencies and DOS from a VASP DOSCAR file

    Args:
        filename: (str) Path to DOSCAR file

    Returns:
        data: (2-tuple) Tuple containing x values and y values as lists
"""
    with open(filename, 'r') as f:
        # Scroll to line 6 which contains NEDOS
        for i in range(5):
            f.readline()
        nedos = int(f.readline().split()[2])

        # Get number of fields and infer number of spin channels
        first_dos_line = f.readline().split()
        spin_channels = (len(first_dos_line) - 1) / 2
        if spin_channels == 1:

            def _tdos_from_line(line):
                return (float(line[0]), float(line[1]))
        elif spin_channels == 2:

            def _tdos_from_line(line):
                line = [float(x) for x in line]
                return (line[0], line[1] + line[2])
        else:
            raise Exception("Too many columns in DOSCAR")

        dos_pairs = (
            [_tdos_from_line(first_dos_line)] +
            [_tdos_from_line(f.readline().split()) for i in range(nedos - 1)])

        return np.array(dos_pairs)
