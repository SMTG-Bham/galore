import urllib.request
import os
import platform
import zipfile
import numpy as np
from difflib import SequenceMatcher

import os.path
from pkg_resources import resource_filename
from json import load as json_load
from collections import Iterable

import sqlite3
from scipy import polyval
from numpy import fromstring as np_fromstr
from numpy import exp, log


def get_cross_sections(weighting, elements=None, dataset=None):
    """Get photoionization cross-section weighting data.

    For known sources, data is based on tabulation of Yeh/Lindau (1985).[1]
    Otherwise, energies in keV from 1-1500 are used with log-log polynomial
    parametrisation of data from Scofield.[2]

    References:
      1. Yeh, J.J. and Lindau, I. (1985)
         Atomic Data and Nuclear Data Tables 32 pp 1-155
      2. J. H. Scofield (1973) Lawrence Livermore National Laboratory
         Report No. UCRL-51326

    Args:
        weighting (str or float): If float and for dataset is None, data source
            for photoionization cross-sections, for dataset is str, connected
            Photon energy. If the string is a known keyword then data will
            be drawn from files included with Galore. Otherwise, the string
            will be interpreted as a path to a JSON file containing data
            arranged in the same way as the output of this function.
        elements (iterable or None): Collection of element symbols to include
            in the data set. If None, a full set of available elements will be
            included. When using a JSON dataset (including the inbuilt
            Yeh/Lindau) this parameter will be ignored as the entire dataset
            has already been loaded into memory.
        datase (str or None): If None the weighting and elements are as discribed
            above. If string, the string will be 'Scofield' or 'Yeh'. And the 
            weighting would be the connected Photon energy.

    Returns:
        dict:
            Photoionization cross-section weightings arranged by element and
            orbital as nested dictionaries of floats, i.e.::

                {el1: {orb1: cs11, orb2: cs12, ...},
                 el2: {orb1: cs21, orb2: cs22, ...}, ... }

            In addition the keys "reference", "link", "energy" and "warning"
            may be used to store metadata.

    """
    if dataset is None:
        try:
            energy = float(weighting)
            return get_cross_sections_scofield(energy, elements=elements)

        except ValueError:
            if isinstance(weighting, str):
                if weighting.lower() in ('alka', 'he2', 'yeh_haxpes'):
                    return get_cross_sections_yeh(weighting)
                elif weighting.lower() in ('xps', 'ups', 'haxpes'):
                    raise ValueError("Key '{0}' is no longer accepted for "
                                     "weighting. Please use 'alka' for Al k-alpha,"
                                     " 'he2' for He (II) or 'yeh_haxpes' for "
                                     "8047.8 eV HAXPES".format(weighting))
                else:
                    return get_cross_sections_json(weighting)

        # A string or a number would have hit a return statement by now
        raise ValueError("Weighting not understood as string or float. ",
                         "Please use a keyword, path to JSON file or an "
                         "energy value in eV")
    else:
        cross_sections_dict = {}
        energy = weighting
        metadata = _get_metadata(energy, dataset)
        cross_sections_dict.update(metadata)

        _, _, data_file_path = get_csv_file_path(dataset)
        if os.path.isfile(data_file_path) == True:
            for element in elements:
                if len(element) == 1:
                    if dataset.lower() == 'scofield':
                        data = read_csv_file(data_file_path, element + '_')
                    elif dataset.lower() == 'yeh':
                        data = read_csv_file(data_file_path, '_' + element)
                else:
                    data = read_csv_file(data_file_path, element)
                cross_sections, closest_energy = _cross_sections_from_csv_data(
                    energy, data, dataset)
                cross_sections_dict[element] = cross_sections
            print('The closest energy of input is {energy} keV'.format(
                energy=closest_energy))
            return cross_sections_dict
        else:
            print(
                "Do you want to install data? \n You can enter \n galore-install-data {dataset}".format(dataset=dataset))


def cross_sections_info(cross_sections, logging=None):
    """Log basic info from cross-sections dict.

    Args:
        cross_sections (dict): The keys 'energy', 'citation',
            'link' and 'warning' are checked for relevant information

        logging (module): Active logging module from Python standard
            library. If None, logging will be set up.

    Returns:
        module:
            Active logging module from Python standard library

    """

    if logging is None:
        import logging
        logging.basicConfig(filename='galore.log', level=logging.INFO)
        console = logging.StreamHandler()
        logging.getLogger().addHandler(console)

    if 'energy' in cross_sections:
        logging.info("  Photon energy: {0}".format(cross_sections['energy']))
    if 'citation' in cross_sections:
        logging.info("  Citation: {0}".format(cross_sections['citation']))
    if 'link' in cross_sections:
        logging.info("  Link: {0}".format(cross_sections['link']))

    return logging


def get_cross_sections_json(path):
    """Get valence-band cross-sections from JSON file

    Read photoionization data from a JSON file. File is expected to contain
    data for multiple elements and orbitals in the form
    ``{El1: {orb1: c1, orb2: c2, ...}, ...}``. While it is expected that
    Galore will be used to examine valence-band orbitals labelled (s, p, d, f)
    it may be helpful in some cases to prepare a file with alternative orbital
    labels corresponding to the pDOS labels.

    The labels 'citation', 'energy' and 'link' are reserved for metadata which
    may be displayed in the program log.
    The label 'comment' may be used for additional material in the JSON file;
    it is recommended to use this repeatedly for line-breaks, e.g.::

        {"comment": "First line of text",
         "comment": "which is continued.",
         ...}

    Args:
        path (str): Path to JSON file

    Returns:
        dict:
            Weighted photoionization cross-sections for each element and
            orbital in form::

                {el1: {'s': c11, 'p': c12, ... },
                 el2: {'s': c21, 'p': c22, ... }, ... }

            in tabulated units.

    """

    if os.path.exists(path):
        with open(path, 'r') as f:
            cross_sections = json_load(f)
    else:
        raise IOError("Cross-sections file {0} does not "
                      "exist!".format(path))

    return cross_sections


def get_cross_sections_yeh(source):
    """Get valence-band cross-sections from tabulated data

    Tabulated values of photoionization cross-sections were drawn from ref [1]
    for energy values corresponding to relevant radiation sources:
    - 1486.6 eV, corresponding to Al k-alpha (laboratory XPS)
    - 40.8 eV, corresponding to He II (laboratory UPS)
    - 8047.8 eV, corresponding to a possible HAXPES source

    References:
        1. Yeh, J.J. and Lindau, I. (1985)
           Atomic Data and Nuclear Data Tables 32 pp 1-155

    Args:
        source (str): Label corresponding to radiation source. Accepted values
            'alka' (1486.6 eV), 'he2' (40.8 eV), 'yeh_haxpes' (8047.8).
            These keys are not case-sensitive and correspond to Al k-alpha,
            He(II) and hard x-ray sources.

    Returns:
        dict:
            Weighted photoionization cross-sections in megaBarns/electron
            for each orbital in form::

                {el1: {'s': c11, 'p': c12, ... },
                 el2: {'s': c21, 'p': c22, ... }, ... }

    """

    weighting_files = {'alka': resource_filename(
                       __name__, "data/cross_sections.json"),
                       'he2': resource_filename(
                           __name__, "data/cross_sections_ups.json"),
                       'yeh_haxpes': resource_filename(
                           __name__, "data/cross_sections_haxpes.json")}

    if source.lower() in weighting_files:
        path = weighting_files[source.lower()]
        return get_cross_sections_json(path)

    else:
        raise Exception(
            "Energy source '{0}' not recognised. ".format(source),
            "Accepted values: {0}".format(", ".join((weighting_files.keys()))))


def get_cross_sections_scofield(energy, elements=None):
    """Get valence-band cross-sections from fitted data

    Energy-dependent cross-sections have been averaged and weighted for
    the uppermost s, p, d, f orbitals from data tabulated by Scofield.
    The energy/cross-section relationship was fitted to an order-8
    polynomial on a log-log scale.

    Multiple energy values can be evaluated simultaneously by passing an
    array-like group of energies as ``energy``. In this case the cross-section
    values will be arrays with the same shape as the energy arrays.

    Args:
        energy (float or array-like): Incident energy in keV
        element (iterable or None): Iterable (e.g. list) of element symbols. If
            None, include all available elements (1 <= Z <= 100).

    Returns:
        dict:
            Weighted photoionization cross-sections in Barns/electron
            for each orbital in form::

                {el1: {'s': c11, 'p': c12, ... },
                 el2: {'s': c21, 'p': c22, ... }, ... }

    Raises:
        ValueError: Energy values must lie within interpolation range
            1--1500keV

    """

    min_energy, max_energy = 1., 1500.

    def _low_value(energy):
        raise ValueError("Scofield data not available below 1 keV: refusing"
                         " to extrapolate to {0} keV".format(energy))

    def _high_value(energy):
        raise ValueError("Scofield data not available above 1500 keV: refusing"
                         " to extrapolate to {0} keV".format(energy))

    if isinstance(energy, Iterable):
        if min(energy) < min_energy:
            _low_value(energy)
        elif max(energy) > max_energy:
            _high_value(energy)
    else:
        if energy < min_energy:
            _low_value(energy)
        elif energy > max_energy:
            _high_value(energy)

    db_file = resource_filename(__name__, "data/scofield_data.db")

    if elements is None:
        elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na',
                    'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc',
                    'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga',
                    'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb',
                    'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb',
                    'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm',
                    'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
                    'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl',
                    'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa',
                    'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm']

    def _eval_fit(energy, coeffs):
        """Convert log-log polynomial fit to cross-section value"""
        log_val = polyval(coeffs, log(energy))
        return exp(log_val)

    el_cross_sections = {'energy': '{0} keV'.format(energy),
                         'citation': "J. H. Scofield (1973) Lawrence Livermore"
                                     " National Laboratory "
                                     "Report No. UCRL-51326, \n"
                                     "Parametrised as log-log order 8 "
                                     "polynomial (A. J. Jackson 2018)",
                         'link': "https://doi.org/10.2172/4545040"}

    with sqlite3.connect(db_file) as con:
        for element in elements:
            cur = con.cursor()
            cur.execute('SELECT orbital, coeffs_np FROM fits WHERE Element=?;',
                        [element])
            orbitals_fits = cur.fetchall()

            el_cross_sections.update({element: {
                orb: _eval_fit(energy, np_fromstr(coeffs))
                for orb, coeffs in orbitals_fits}})
    return el_cross_sections


def read_csv_file(data_file_path, element_name):
    """
    Generate data from csv archive without decompression

    Args:
        data_file_path: path to tarfile of CSV data
        element_name: element name for connected CSV file

    Returns:
        dict: containing 'headers', 'electron_counts' 
        (lists of str and int respectively) and 'data_table', 
        a 2-D nested list of floats. Missing data is represented as None.

    """

    # Open zipfile and match the element_name to csv file name
    with zipfile.ZipFile(data_file_path) as data_zf:
        namelist = data_zf.namelist()
        for filename in namelist:
            if SequenceMatcher(None, element_name, filename[-6:-4]).ratio() > 0.99:
                data = data_zf.read(filename).decode()

    # string to list
    data_string = data.split('\r\n')

    # get number of colunm headers
    column_headers = [column_header for column_header in data_string[0].split(
        ',') if column_header != '']
    n_columns = len(column_headers)

    # build main matrix
    main_matrix = [row.split(',')[0:n_columns] for row in data_string]

    # remove empty values
    midterm = [row for row in main_matrix if any(row) == True]
    data_table = midterm[1:-1]
    electron_counts_list = [
        occupancy for occupancy in midterm[-1] if occupancy != ''][1:]

    # replace '' in data table with NaN and change string list into float array
    data_table = np.array([[float('NaN') if cross_section == '' else float(cross_section) for cross_section in row]
                           for row in data_table])
    electron_counts = np.array([float(occupancy)
                               for occupancy in electron_counts_list])

    # build result dict
    result_dict = {}
    result_dict['headers'] = column_headers
    result_dict['electron_counts'] = electron_counts
    result_dict['data_table'] = data_table

    return result_dict


def _get_avg_orbital_cross_sections(subshells_cross_sections, electrons_numbers):
    """
    Obtain average cross sections of subshell of each obital when process Scofield data.

    Args:
        subshell_cross_sections(np.array): The subshells cross sections array of the highest orbital              
        electrons_number(np.array): corresponding electrons number of these subshells

    Returns:
        avg_orbital_cross_sections(np.array): average cross sections of subshells

    """

    subshells_cross_sections_sum = sum(subshells_cross_sections)

    subshells_electrons_numbers_sum = sum(electrons_numbers)

    avg_orbital_cross_sections = subshells_cross_sections_sum / \
        subshells_electrons_numbers_sum

    return avg_orbital_cross_sections


def _cross_sections_from_csv_data(energy, data, dataset):
    """
    Get cross sections from data dict 
    For known sources, data is based on tabulation of Yeh/Lindau (1985).[1]
    Otherwise, energies in keV from 1-1500 are used with log-log polynomial
    parametrisation of data from Scofield.[2]

    References:
      1. Yeh, J.J. and Lindau, I. (1985)
         Atomic Data and Nuclear Data Tables 32 pp 1-155
      2. J. H. Scofield (1973) Lawrence Livermore National Laboratory
         Report No. UCRL-51326

    Args:
        energy(float): energy value  
        data(dict): data from read_csv_file()
        reference(str): 'Scofield' or 'Yeh'

    Returns:
        orbitals_cross_sections_dict: containing orbitals 's', 'p', 'd', 'f' and 
                                      highest orbital cross sections of each orbital. 
                                      Missing data is represented as None.

    """

    n_subshells = len(data['electron_counts'])
    subshells_headers = data['headers'][-n_subshells:]

    # build dicts for easy calculation.
    electron_counts_by_subshells = dict(
        zip(subshells_headers, data['electron_counts']))
    cross_sections_by_subshells = dict(
        zip(subshells_headers, data['data_table'].T[-n_subshells:]))

    # match the import energy
    if dataset.lower() == 'scofield' and float(energy) > 1500:
        print('error: The maximum energy of Scofield is 1500 keV')

    energy_index = np.abs(data['data_table'].T[0] - float(energy)).argmin()
    closest_energy = data['data_table'].T[0][energy_index]

    # build result dict
    orbitals_cross_sections_dict = {}

    # result for s orbital
    s_cross_sections = np.array(
        [value[energy_index] for key, value in cross_sections_by_subshells.items() if 's' in key])
    electrons_numbers = np.array(
        [value for key, value in electron_counts_by_subshells.items() if 's' in key])
    # get highest obital cross section of obital s
    highest_obital_cross_section = s_cross_sections[-1]/electrons_numbers[-1]
    orbitals_cross_sections_dict['s'] = highest_obital_cross_section

    # result for 'p', 'd', 'f' orbitals
    orbitals = ['p', 'd', 'f']

    for orbital in orbitals:
        interm_matrix = np.array(
            [value for key, value in cross_sections_by_subshells.items() if orbital in key]).T
        electrons_numbers = np.array(
            [value for key, value in electron_counts_by_subshells.items() if orbital in key])

        if np.shape(interm_matrix) != (0,):
            if dataset.lower() == 'scofield':
                subshells_cross_sections = interm_matrix[energy_index]
                highest_obital_subshells_cross_sections = subshells_cross_sections[-2:]
                highest_obital_subshells_electrons_numbers = electrons_numbers[-2:]
                result = _get_avg_orbital_cross_sections(
                    highest_obital_subshells_cross_sections, highest_obital_subshells_electrons_numbers)
                # get highest cross section of this obital
                highest_obital_cross_section = result
                orbitals_cross_sections_dict[orbital] = highest_obital_cross_section

            elif dataset.lower() == 'yeh':
                obital_cross_sections = interm_matrix[energy_index]

                # get highest cross section of this obital
                highest_obital_cross_section = obital_cross_sections[-1] / \
                    electrons_numbers[-1]
                orbitals_cross_sections_dict[orbital] = highest_obital_cross_section

    return orbitals_cross_sections_dict, closest_energy


def _get_metadata(energy, dataset):
    """
    Args:
        energy(float): energy value  
        dataset(str): 'Scofield' or 'Yeh'

        Note: 1.'Scofield' for J. H. Scofield (1973)
                Lawrence Livermore National Laboratory Report No. UCRL-51326              
              2.'Yeh' for Yeh, J.J. and Lindau, I. (1985) 
                Atomic Data and Nuclear Data Tables 32 pp 1-155   

    Returns:
        metadata_dict: containing the input energy value 
                       and description of input reference

    """

    metadata_dict = {}
    metadata_dict['energy'] = energy
    if dataset.lower() == 'scofield':
        metadata_dict['citation'] = 'J.H. Scofield, Theoretical photoionization cross sections from 1 to 1500 keV'
        metadata_dict['link'] = 'https://doi.org/10.2172/4545040'
    elif dataset.lower() == 'yeh':
        metadata_dict['citation'] = 'Yeh, J.J. and Lindau, I. (1985) Atomic Data and Nuclear Data Tables 32 pp 1-155'
        metadata_dict['link'] = 'https://doi.org/10.1016/0092-640X(85)90016-6'
    else:
        metadata_dict(
            'Reference error: you can enter reference as "Scofield" or "Yeh" ')
    return metadata_dict


def galore_install_data(url, data_file_dir, data_file_path):

    if os.path.isfile(data_file_path) == True:
        print("Data file exists.")

    else:
        print("Downloading file...")

        try:
            os.mkdir(data_file_dir)
        except:
            pass

        urllib.request.urlretrieve(url, data_file_path)

        if os.path.isfile(data_file_path) == True:
            print("Done")


def get_csv_file_path(dataset):

    if platform.system() == "Windows":

        data_file_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'galore_data')
    else:
        data_file_dir = os.path.join(os.path.expanduser('~'), '.galore_data')

    if dataset.lower() == 'scofield':
        data_file_path = os.path.join(
            data_file_dir, 'Scofield_csv_database.zip')
        url = 'https://ndownloader.figshare.com/articles/15081888/versions/1'

    elif dataset.lower() == 'yeh':
        data_file_path = os.path.join(
            data_file_dir, 'Yeh_Lindau_1985_Xsection_CSV_Database.zip')
        url = 'https://ndownloader.figshare.com/articles/15090012/versions/1'

    return url, data_file_dir, data_file_path
