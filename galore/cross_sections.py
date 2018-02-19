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
