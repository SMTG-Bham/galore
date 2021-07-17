import os.path
from pkg_resources import resource_filename
from json import load as json_load
from collections import Iterable

import sqlite3
from scipy import polyval
from numpy import fromstring as np_fromstr
from numpy import exp, log


def get_cross_sections(weighting, elements=None):
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
        weighting (str or float): Data source for photoionization
            cross-sections. If the string is a known keyword then data will
            be drawn from files included with Galore. Otherwise, the string
            will be interpreted as a path to a JSON file containing data
            arranged in the same way as the output of this function.
        elements (iterable or None): Collection of element symbols to include
            in the data set. If None, a full set of available elements will be
            included. When using a JSON dataset (including the inbuilt
            Yeh/Lindau) this parameter will be ignored as the entire dataset
            has already been loaded into memory.

    Returns:
        dict:
            Photoionization cross-section weightings arranged by element and
            orbital as nested dictionaries of floats, i.e.::

                {el1: {orb1: cs11, orb2: cs12, ...},
                 el2: {orb1: cs21, orb2: cs22, ...}, ... }

            In addition the keys "reference", "link", "energy" and "warning"
            may be used to store metadata.

    """

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



import tarfile
import numpy as np
def read_csv_file(tar_file_name,file_path):
    '''read csv file 
    Input:  the file name
    Output: main matrix of each file'''
    
    ###Open zipfile
    with tarfile.open(tar_file_name) as tf:
        with tf.extractfile(file_path) as hello:
            data = hello.read().decode()
    a = data.split('\r\n')
    
    ###get number of elements of each raw
    a0 = a[0].split(',')
    new_a0 = [i for i in a0 if i !='']
    lenth = len(new_a0)
    
    ###build main matrix
    result = []
    for i in range(len(a)):
        c = a[i].split(',')[0:lenth]
        result.append(c)
        
    ###delet needless elements
    d = result[-2] 
    result1 = [i for i in result if i!=d]
    new_result = [i for i in result if i!=d][0:-2]
    
    ###build dict
    dic={}
    dic['headers'] = new_result[0]
    dic['electron_counts'] = [i for i in result1[-2] if i !=''][1:]
    dic['data_table'] = new_result[1:]
    
    
    return dic



def _cross_sections_from_csv_data(energy,data,reference):
    
   
    ## replace '' with nan
    for i in range(len(data['data_table'])):
        data['data_table'][i] = [float('NaN') if x == '' else x for x in data['data_table'][i]]   
    
    ## change the main matrix to float array
    data['data_table'] = np.array(data['data_table']).astype(float)
    data['electron_counts'] = np.array(data['electron_counts']).astype(float)
    
    ## build a new dict which keys are like '1s1/2', '2s1/2', '2p1/2', '2p3/2', '3s1/2', '3p1/2', '3p3/2'...
    new_lenth = len(data['electron_counts'])
    new_value=np.concatenate((data['data_table'].T[-new_lenth:].T,[data['electron_counts']]),axis=0).T
    new_dic = {}
    for i in range(new_lenth):
        new_key = data['headers'][-new_lenth:][i]
        new_dic[new_key]=new_value[i]
        
    ## add electron numbers of each orbitals    
    energy_array = np.array(data['data_table']).T[0]
    new_dic['PhotonEnergy'] = energy_array

    ## match the import energy
    index = np.where(new_dic['PhotonEnergy']==energy)[0][0]
    
    ## build result dict
    res_dict = {}
    
    ## result for s orbital
    c_s = np.array([new_dic[key] for key in new_dic if 's' in key]).T[index]
    n_electrons = np.array([new_dic[key] for key in new_dic if 's' in key]).T[-1]
    unit_c_s = np.true_divide(c_s,n_electrons)

   
    value_s = np.max(np.nan_to_num(unit_c_s))
    
    res_dict['s'] = value_s
    
    ## result for 'p', 'd', 'f' orbitals
    orbitals = ['p', 'd', 'f']
    
    
    for i in orbitals:
        main_matrix = np.array([new_dic[key] for key in new_dic if i in key])
        if np.shape(main_matrix) != (0,):
            if reference == 'Scofield':
                c_s = main_matrix.T[index]
            
                n_electrons = main_matrix.T[-1]
                unit_c_s = np.true_divide(c_s,n_electrons)
                unit_c_s = np.array([unit_c_s[i:i+2] for i in range(0, len(unit_c_s), 2)])
                percent =np.array([np.true_divide(c_s[i:i+2],c_s[i:i+2].sum()) for i in range(0, len(c_s), 2)])
                result = np.array(list(map(sum,unit_c_s*percent)))
            
                value = np.max(np.nan_to_num(result))
                res_dict[i] = value
            else:
                c_s = main_matrix.T[index]
                n_electrons = main_matrix.T[-1]
                unit_c_s = np.true_divide(c_s,n_electrons)
                value = np.max(np.nan_to_num(unit_c_s))
                res_dict[i] = value
                
    return res_dict


def get_metadata(energy,reference):
    dict = {}
    dict['energy'] = energy
    if reference == 'Scofield':
        dict['reference'] = 'J.H. Scofield, Theoretical photoionization cross sections from 1 to 1500 keV'
        dict['link'] = 'https://doi.org/10.2172/4545040' 
    else:
        dict['reference'] = 'Yeh, J.J. and Lindau, I. (1985) Atomic Data and Nuclear Data Tables 32 pp 1-155'
        dict['link'] = 'https://doi.org/10.1016/0092-640X(85)90016-6'
    return dict


def get_cross_section_from_csv(elements,energy,reference):
    result = {}
    metadata = get_metadata(energy,reference)
    result.update(metadata)
    
    
    for element in elements:
        
        if reference == 'Scofield':
            filename = 'Scofield_csv_database.tar.gz'
            filepath = 'Scofield_csv_database/Z_{element1}.csv'
        else:
            filename ='Yeh_Lindau_1985_Xsection_CSV_Database.tar.gz'
            filepath = 'Yeh_Lindau_1985_Xsection_CSV_Database/{element1}.csv'
            
        filepath = filepath.format(element1 = element)
        data = read_csv_file(filename,filepath)
        
        cross_sections = _cross_sections_from_csv_data(energy,data,reference)
        result[element] = cross_sections
        
    return result




    import tarfile
import numpy as np


def read_csv_file(tar_file_name, file_path):
    """
    Args:
        tar_file_name (str): path to tarfile of CSV data
        file_path(str): path to individual CSV file within tarfile

    Returns:
        dict: containing 'headers', 'electron_counts' 
        (lists of str and int respectively) and 'data_table', 
        a 2-D nested list of floats. Missing data is represented as None.

    """

    # Open zipfile
    with tarfile.open(tar_file_name) as tf:
        with tf.extractfile(file_path) as hello:
            # get data as string
            data = hello.read().decode()
    # string to list
    data_string = data.split('\r\n')

    # get number of colunm headers
    colunm_headers = [i for i in data_string[0].split(',') if i != '']
    lenth = len(colunm_headers)

    # build main matrix
    main_matrix = []
    rows = range(len(data_string))
    for row in rows:
        data_each_row = data_string[row].split(',')[0:lenth]
        main_matrix.append(data_each_row)

    # build cross sections table
    empty_value = main_matrix[-2]
    # remove empty values
    midterm = [i for i in main_matrix if i != empty_value]
    new_main_matrix = midterm[0:-2]

    # build result dict
    result_dict = {}
    result_dict['headers'] = colunm_headers
    result_dict['electron_counts'] = [i for i in midterm[-2] if i != ''][1:]
    result_dict['data_table'] = new_main_matrix[1:]

    return result_dict


def _cross_sections_from_csv_data(energy, data, reference):
    """
    Args:
        energy(float): energy value  
        data(dict): data from read_csv_file()
        reference(str): 'Scofield' or 'Yeh'

        Note: 1.'Scofield' for J. H. Scofield (1973)
                Lawrence Livermore National Laboratory Report No. UCRL-51326              
              2.'Yeh' for Yeh, J.J. and Lindau, I. (1985) 
                Atomic Data and Nuclear Data Tables 32 pp 1-155   

    Returns:
        orbitals_cross_sections_dict: containing orbitals 's', 'p', 'd', 'f' and f
                                      cross sections of each orbital. 
                                      Missing data is represented as None.

    """

    # replace '' in data table with NaN
    for row in range(len(data['data_table'])):
        data['data_table'][row] = [
            float('NaN') if x == '' else x for x in data['data_table'][row]]

    # change the data_table and electron_counts to float arrays
    data['data_table'] = np.array(data['data_table']).astype(float)
    data['electron_counts'] = np.array(data['electron_counts']).astype(float)

    ## Build a new_dic which keys are like '1s1/2', '2s1/2', '2p1/2', '2p3/2', '3s1/2', '3p1/2', '3p3/2'...
    ## and values are connected cross sections and number of electrons of each orbital
    ## This is for calculating the max cross sections of 's', 'p', 'd', 'f' orbitals
    new_dic = {}
    orbitals_number = len(data['electron_counts'])
    # connect the number of electron_counts to each orbitals and cross sections
    new_value = np.concatenate(
        (data['data_table'].T[-orbitals_number:].T, [data['electron_counts']]), axis=0).T
    for orbital in range(orbitals_number):
        new_key = data['headers'][-orbitals_number:][orbital]
        new_dic[new_key] = new_value[orbital]

    # add energy array to new_dic
    energy_array = np.array(data['data_table']).T[0]
    new_dic['PhotonEnergy'] = energy_array

    # match the import energy
    index = np.where(new_dic['PhotonEnergy'] == energy)[0][0]

    # build result dict
    orbitals_cross_sections_dict = {}

    # result for s orbital
    s_cross_sections = np.array([new_dic[key]
                                for key in new_dic if 's' in key]).T[index]
    electrons_number = np.array([new_dic[key]
                                for key in new_dic if 's' in key]).T[-1]
    # get unit cross sections
    unit_cross_sections = np.true_divide(s_cross_sections, electrons_number)
    # get max cross section of obital s
    max_cross_section = np.max(np.nan_to_num(unit_cross_sections))
    orbitals_cross_sections_dict['s'] = max_cross_section

    # result for 'p', 'd', 'f' orbitals
    orbitals = ['p', 'd', 'f']
    for orbital in orbitals:
        interm_matrix = np.array([new_dic[key]
                                 for key in new_dic if orbital in key])
        if np.shape(interm_matrix) != (0,):
            if reference == 'Scofield':
                obital_cross_sections = interm_matrix.T[index]
                electrons_number = interm_matrix.T[-1]
                unit_cross_sections = np.true_divide(
                    obital_cross_sections, electrons_number)

                # for orbitals like '2p1/2', '2p3/2' we need to calculate electrons number weighted mean value as result cross_section
                unit_cross_sections_array = np.array(
                    [unit_cross_sections[i:i+2] for i in range(0, len(unit_cross_sections), 2)])
                weight = np.array([np.true_divide(obital_cross_sections[i:i+2], obital_cross_sections[i:i+2].sum())
                                  for i in range(0, len(obital_cross_sections), 2)])
                result = np.array(
                    list(map(sum, unit_cross_sections_array*weight)))
                # get max cross section of this obital
                max_cross_section = np.max(np.nan_to_num(result))
                orbitals_cross_sections_dict[orbital] = max_cross_section

            elif reference == 'Yeh':
                obital_cross_sections = interm_matrix.T[index]
                electrons_number = interm_matrix.T[-1]
                unit_cross_sections = np.true_divide(
                    obital_cross_sections, electrons_number)
                # get max cross section of this obital
                max_cross_section = np.max(np.nan_to_num(unit_cross_sections))
                orbitals_cross_sections_dict[orbital] = max_cross_section

    return orbitals_cross_sections_dict


def get_metadata(energy, reference):
    """
    Args:
        energy(float): energy value  
        reference(str): 'Scofield' or 'Yeh'

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
    if reference == 'Scofield':
        metadata_dict['reference'] = 'J.H. Scofield, Theoretical photoionization cross sections from 1 to 1500 keV'
        metadata_dict['link'] = 'https://doi.org/10.2172/4545040'
    elif reference == 'Yeh':
        metadata_dict['reference'] = 'Yeh, J.J. and Lindau, I. (1985) Atomic Data and Nuclear Data Tables 32 pp 1-155'
        metadata_dict['link'] = 'https://doi.org/10.1016/0092-640X(85)90016-6'
    else:
        metadata_dict('Wrong reference')
    return metadata_dict


def get_cross_section_from_csv(elements, energy, reference):
    """
    Args:
        elements(string list): element name list
                               for Scofiled data such as ['Z__1_H_','Z_13_Al',....]
                               for Yeh data such as ['1_H','13_Al',...]

        energy(float): energy value  
        reference(str): 'Scofield' or 'Yeh'

        Note: 1.'Scofield' for J. H. Scofield (1973)
                Lawrence Livermore National Laboratory Report No. UCRL-51326              
              2.'Yeh' for Yeh, J.J. and Lindau, I. (1985) 
                Atomic Data and Nuclear Data Tables 32 pp 1-155   

    Returns:
        result(dict): containing energy value, reference information, 
                      and orbital cross sections dict of input elements

    """

    result = {}
    metadata = get_metadata(energy, reference)
    result.update(metadata)

    for element in elements:

        if reference == 'Scofield':
            filename = 'Scofield_csv_database.tar.gz'
            filepath = 'Scofield_csv_database/{element1}.csv'
        else:
            filename = 'Yeh_Lindau_1985_Xsection_CSV_Database.tar.gz'
            filepath = 'Yeh_Lindau_1985_Xsection_CSV_Database/{element1}.csv'

        filepath = filepath.format(element1=element)
        data = read_csv_file(filename, filepath)

        cross_sections = _cross_sections_from_csv_data(energy, data, reference)
        result[element] = cross_sections

    return result
