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
import os
import csv
import re
import sys
from collections import OrderedDict
import numpy as np


def is_gpw(filename):
    """Determine whether file is GPAW calculation by checking extension"""
    return filename.split('.')[-1] == 'gpw'


def is_doscar(filename):
    """Determine whether file is a DOSCAR by checking fourth line"""

    # This doesn't break when the file is 3 lines or less; f.readline() just
    # starts returning empty strings which also fail the test.
    with open(filename, 'r') as f:
        for i in range(3):
            f.readline()
        if f.readline().strip() == 'CAR':
            return True
        else:
            return False


def is_vasp_raman(filename):
    """Determine if file is raman-sc/vasp_raman.py data by checking header"""
    with open(filename, 'r') as f:
        line = f.readline()

    return line.strip() == '# mode    freq(cm-1)    alpha    beta2    activity'


def is_csv(filename):
    """Determine whether file is CSV by checking extension"""
    return filename.split('.')[-1] == 'csv'


def is_xml(filename):
    """Determine whether file is XML by checking extension"""
    if filename.split('.')[-1] == 'gz':
        return filename.split('.')[-2] == 'xml'
    else:
        return filename.split('.')[-1] == 'xml'


def is_complete_dos(pdos):
    """Determine whether the object is a pymatgen CompleteDos object"""
    densities_fn = getattr(pdos, "get_densities", None)
    return callable(densities_fn)


def write_txt(x_values, y_values, filename="galore_output.txt", header=None):
    """Write output to a simple space-delimited file

    Args:
        x_values (iterable): Values to print in first column
        y_value (iterable): Values to print in second column
        filename (str): Path to output file, including extension. If None,
            write to standard output instead.
        header (str): Additional line to prepend to file. If None, no header
            is used.

        """

    rows = zip(x_values, y_values)
    _write_txt_rows(rows, filename=filename, header=header)


def _write_txt_rows(rows, filename=None, header=None):
    """Write rows of data to space-separated text output

    Args:
        rows (iterable): Rows to write. Rows should be a list of values.
        filename (str or None): Filename for text output. If None, write to
            standard output instead.
        header (iterable or None): Optionally add another row to the top of the
            file. Useful if rows is a generator you don't want to mess with.

    """

    def _format_line(row):
        return ' '.join(('{0:10.6e}'.format(x) for x in row)) + '\n'

    lines = map(_format_line, rows)

    if filename is not None:
        with open(filename, 'w') as f:
            if header is not None:
                f.write(header + '\n')
            f.writelines(lines)

    else:
        if header is not None:
            print(header)
        for line in lines:
            print(line, end='')


def _write_csv_rows(rows, filename=None, header=None):
    """Write rows of data to output in CSV format

    Args:
        rows (iterable): Rows to write. Rows should be a list of values.
        filename (str or None): Filename for CSV output. If None, write to
            standard output instead.
        header (iterable or None): Optionally add another row to the top of the
            file. Useful if rows is a generator you don't want to mess with.

    """

    def _write_csv(rows, f, header):
        writer = csv.writer(f, lineterminator=os.linesep)
        if header is not None:
            writer.writerow(header)
        writer.writerows(rows)

    if filename is None:
        _write_csv(rows, sys.stdout, header=header)

    else:
        with open(filename, 'w') as f:
            _write_csv(rows, f, header=header)


def write_csv(x_values, y_values, filename="galore_output.csv", header=None):
    """Write output to a simple space-delimited file

    Args:
        x_values (iterable): Values to print in first column
        y_value (iterable): Values to print in second column
        filename (str): Path to output file, including extension. If None,
            write to standard output instead.
        header (iterable): Additional line to prepend to file. If None,
            no header is used.

        """

    rows = zip(x_values, y_values)
    _write_csv_rows(rows, filename=filename, header=header)


def write_pdos(pdos_data, filename=None, filetype="txt", flipx=False):
    """Write PDOS or XPS data to CSV file

    Args:
        pdos_data (dict): Data for pdos plot in format::

                {'el1': {'energy': values, 's': values, 'p': values ...},
                 'el2': {'energy': values, 's': values, ...}, ...}

             where DOS values are 1D numpy arrays. For deterministic output,
             use ordered dictionaries!
        filename (str or None): Filename for output. If None, write to stdout
        filetype (str): Format for output; "csv" or "txt.
        flipx (bool): Negate the x-axis (i.e. energy) values to make binding
            energies
    """

    header = ['energy']
    cols = [list(pdos_data.values())[0]['energy']]
    if flipx:
        cols[0] = -cols[0]

    for el, orbitals in pdos_data.items():
        for orbital, values in orbitals.items():
            if orbital.lower() != 'energy':
                header += ['_'.join((el, orbital))]
                cols.append(values)

    data = np.array(cols).T

    total = data[:, 1:].sum(axis=1)
    data = np.insert(data, 1, total, axis=1)
    header.insert(1, 'total')

    if filetype == 'csv':
        _write_csv_rows(data, filename=filename, header=header)
    elif filetype == 'txt':
        header = ' ' + ' '.join(('{0:12s}'.format(x) for x in header))
        _write_txt_rows(data, filename=filename, header=header)
    else:
        raise ValueError('filetype "{0}" not recognised. Use "txt" or "csv".')


def read_csv(filename):
    """Read a txt file containing frequencies and intensities

    If input file contains three columns, the first column is ignored. (It is
    presumed to be a vibrational mode index.)

    Args:
        filename (str): Path to data file

    Returns:
        n x 2 Numpy array of frequencies and intensities

    """
    return read_txt(filename, delimiter=',')


def read_txt(filename, delimiter=None):
    """Read a txt file containing frequencies and intensities

    If input file contains three columns, the first column is ignored. (It is
    presumed to be a vibrational mode index.)

    Args:
        filename (str): Path to data file

    Returns:
        n x 2 Numpy array of frequencies and intensities

    """
    xy_data = np.genfromtxt(filename, comments='#', delimiter=delimiter)

    columns = np.shape(xy_data)[1]

    if columns == 2:
        return xy_data
    elif columns == 3:
        return xy_data[:, 1:]
    elif columns < 2:
        raise Exception("Not sure how to interpret {0}: "
                        "not enough columns.".format(filename))
    else:
        raise Exception("Not sure how to interpret {0}: "
                        "too many columns.".format(filename))


def read_pdos_txt(filename, abs_values=True):
    """Read a text file containing projected density-of-states (PDOS) data

    The first row should be a header identifying the orbitals, e.g.
    "# Energy s p d f". The following rows contain the corresponding energy and
    DOS values. Spin channels indicated by (up) or (down) suffixes will be
    combined.

    Args:
        filename (str): Path to file for import
        abs_values (bool, optional):
            Convert intensity values to absolute numbers. This is primarily for
            compatibility with spin-polarised .dat files from Sumo. Set to
            False if negative values in spectrum are resonable.

    Returns:
        data (np.ndarray): Numpy structured array with named columns
            corresponding to input data format.
    """
    data = np.genfromtxt(filename, names=True)

    if abs_values:
        for col in data.dtype.names[1:]:
            data[col] = np.abs(data[col])

    # Get a list of orbitals that have 'up' and 'down' variants
    spin_pairs = []
    for col in data.dtype.names:
        if re.match('.+up', col):
            orbital = re.match('(.+)up', col).groups()[0]
            if orbital + 'down' in data.dtype.names:
                spin_pairs.append(orbital)

    if len(spin_pairs) == 0:
        return data

    else:
        # Sum up/down channel pairs into their respective up channels
        for orbital in spin_pairs:
            data[orbital + 'up'] += data[orbital + 'down']

        # Rename spin-up channels
        column_names = list(data.dtype.names)
        for orbital in spin_pairs:
            column_names[column_names.index(orbital + 'up')] = orbital
        data.dtype.names = tuple(column_names)

        # Exclude spin-down channels from returned data
        spin_down_orbs = [orb + 'down' for orb in spin_pairs]
        return data[[col for col in data.dtype.names
                     if col not in spin_down_orbs]]


def read_doscar(filename="DOSCAR"):
    """Read an x, y series of frequencies and DOS from a VASP DOSCAR file

    Args:
        filename (str): Path to DOSCAR file

    Returns:
        data (2-tuple): Tuple containing x values and y values as lists
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


def read_vasprun(filename='vasprun.xml'):
    """Read a VASP vasprun.xml file to obtain the density of states

    Pymatgen must be present on the system to use this method

    Args:
        filename (str): Path to vasprun.xml file

    Returns:
        data (pymatgen.electronic_structure.dos.Dos): A pymatgen Dos object
    """
    try:
        from pymatgen.io.vasp.outputs import Vasprun
    except ImportError as e:
        e.msg = "pymatgen package neccessary to load vasprun files"
        raise

    vr = Vasprun(filename)
    band = vr.get_band_structure()
    dos = vr.complete_dos

    if band.is_metal():
        zero_point = vr.efermi
    else:
        zero_point = band.get_vbm()['energy']

    # Shift the energies so that the vbm is at 0 eV, also taking into account
    # any gaussian broadening
    dos.energies -= zero_point
    if vr.parameters['ISMEAR'] == 0 or vr.parameters['ISMEAR'] == -1:
        dos.energies -= vr.parameters['SIGMA']

    return dos


def read_gpaw_totaldos(filename, npts=50001, width=1e-3, ref='vbm'):
    """Read total DOS from GPAW with minimal broadening

    This requires GPAW to be installed and on your PYTHONPATH!

    Args:
        filename (str): Path to GPAW calculation file. This should be a .gpw
            file generated with ``calc.write('myfilename.gpw')``.
        npts (int): Number of DOS samples
        width (float): Gaussian broadening parameter applied by GPAW. Default
            is minimal so that broadening is dominated by choices in Galore.
            Beware that there is a strong interaction between this parameter
            and npts; with a small npts and small width, many energy levels
            will be missed from the DOS!
        ref (str): Reference energy for DOS. 'vbm' or 'efermi' are accepted for
            the valence-band maximum or the Fermi energy, respectively. VBM is
            determined from calculation eigenvalues and not DOS values. If set
            to None, raw values are used.
    Returns:
        data (np.ndarray): 2D array of energy and DOS values
    """
    from gpaw import GPAW
    calc = GPAW(filename)

    if ref is None:
        ref_energy = 0
    elif ref.lower() == 'vbm':
        ref_energy, _ = calc.get_homo_lumo()
    elif ref.lower() == 'efermi':
        ref_energy = calc.get_fermi_level()

    energies, dos = calc.get_dos(npts=npts, width=width)
    return np.array(list(zip(energies - ref_energy, dos)))


def read_gpaw_pdos(filename, npts=50001, width=1e-3, ref='vbm'):
    """Read orbital-projected DOS from GPAW with minimal broadening.

    This requires GPAW to be installed and on your PYTHONPATH!

    Args:
        filename (str): Path to GPAW calculation file. This should be a .gpw
            file generated with ``calc.write('myfilename.gpw')``.
        npts (int): Number of DOS samples
        width (float): Gaussian broadening parameter applied by GPAW. Default
            is minimal so that broadening is dominated by choices in Galore.
            Beware that there is a strong interaction between this parameter
            and npts; with a small npts and small width, many energy levels
            will be missed from the DOS!
        ref (str): Reference energy for DOS. 'vbm' or 'efermi' are accepted for
            the valence-band maximum or the Fermi energy, respectively. VBM is
            determined from calculation eigenvalues and not DOS values. If set
            to None, raw values are used.

    Returns:
        pdos_data (OrderedDict): PDOS data formatted as nestled OrderedDict of:
            {element: {'energy': energies, 's': densities, 'p' ... }
    """
    from gpaw import GPAW
    calc = GPAW(filename)

    if ref is None:
        ref_energy = 0
    elif ref.lower() == 'vbm':
        ref_energy, _ = calc.get_homo_lumo()
    elif ref.lower() == 'efermi':
        ref_energy = calc.get_fermi_level()

    # Set up the structure of elements and orbitals.
    # Repeated elements will leave a single entry in the dict
    proto_orbitals = OrderedDict((('energy', np.zeros(npts)),
                                  ('s', np.zeros(npts)),
                                  ('p', np.zeros(npts)),
                                  ('d', np.zeros(npts)),
                                  ('f', np.zeros(npts))))
    pdos_data = OrderedDict([(atom.symbol, proto_orbitals.copy())
                             for atom in calc.atoms])

    # Read orbital DOS, adding to collected PDOS for that element/orbital
    for atom in calc.atoms:
        for orbital in 'spdf':
            energies, dos = calc.get_orbital_ldos(atom.index, angular=orbital,
                                                  npts=npts, width=width)
            pdos_data[atom.symbol][orbital] += dos

        pdos_data[atom.symbol]['energy'] = energies - ref_energy

    # Set any zero arrays to None so they can be easily skipped over
    # This should get rid of unused orbitals; if GPAW put some density in those
    # orbitals then we should keep that evidence rather than discard it.
    for element, orbitals in pdos_data.items():
        for orbital, dos in orbitals.items():
            if orbital != 'energy' and max(dos) == 0.:
                pdos_data[element][orbital] = None

    return pdos_data


def read_vasprun_totaldos(filename='vasprun.xml'):
    """Read an x, y series of energies and DOS from a VASP vasprun.xml file

    Pymatgen must be present on the system to use this method

    Args:
        filename (str): Path to vasprun.xml file

    Returns:
        data (np.ndarray): 2D array of energy and DOS values
    """
    dos = read_vasprun(filename)

    from pymatgen.electronic_structure.core import Spin

    # sum spin up and spin down channels
    densities = dos.densities[Spin.up]
    if len(dos.densities) > 1:
        densities += dos.densities[Spin.down]

    return np.array(list(zip(dos.energies, densities)))


def read_vasprun_pdos(filename='vasprun.xml'):
    """Read a vasprun.xml containing projected density-of-states (PDOS) data

    Pymatgen must be present on the system to use this method

    Args:
        filename (str or CompleteDos):
            Path to vasprun.xml file or pymatgen CompleteDos object.

    Returns:
        pdos_data (np.ndarray): PDOS data formatted as nestled OrderedDict of:
            {element: {'energy': energies, 's': densities, 'p' ... }
    """
    if isinstance(filename, str):
        dos = read_vasprun(filename)
    else:
        # filename is actually a pre-loaded CompleteDos
        dos = filename

    from pymatgen.electronic_structure.core import Spin, OrbitalType

    pdos_data = OrderedDict()
    for element in dos.structure.symbol_set:
        pdos_data[element] = OrderedDict([('energy', dos.energies)])
        pdos = dos.get_element_spd_dos(element)
        for orb in sorted([orb.value for orb in pdos.keys()]):
            # this way we can ensure the orbitals remain in the correct order
            orbital = OrbitalType(orb)
            # sum spin up and spin down channels
            densities = pdos[orbital].densities[Spin.up]
            if len(dos.densities) > 1:
                densities += pdos[orbital].densities[Spin.down]
            pdos_data[element][orbital.name] = densities

    return pdos_data


def read_vasp_raman(filename="vasp_raman.dat"):
    """Read output file from Vasp raman simulation

    Args:
        filename (str): Path to formatted data file generated by
            https://github.com/raman-sc/VASP - Raman intensities are computed
            by following vibrational modes and calculating polarisability. The
            generated output file is named *vasp_raman.dat* but can be renamed
            if desired. The format is five space-separated columns, headed by
            ``# mode    freq(cm-1)    alpha    beta2    activity``.

    Returns:
        2-D np.array:
            Only the columns corresponding to frequency and activity are
            retained.
    """

    data = np.genfromtxt(filename)
    return data[:, [1, -1]]
