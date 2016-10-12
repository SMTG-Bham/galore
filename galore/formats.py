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
import csv
import sys


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
        writer = csv.writer(f)
        if header is not None:
            writer.writerow(header)
        writer.writerows(zip(x_values, y_values))

    if filename is None:
        _write_csv(x_values, y_values, sys.stdout, header=header)
    else:
        with open(filename, 'w') as f:
            _write_csv(x_values, y_values, f, header=header)
