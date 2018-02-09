import os.path
from pkg_resources import resource_filename
from json import load as json_load

import sqlite3
from scipy import polyval
from numpy import fromstring as np_fromstr
from numpy import exp, log


def get_cross_sections(weighting):
    """Interpret input to select weightings data"""

    weighting_files = {'xps': resource_filename(
                       __name__, "data/cross_sections.json"),
                       'ups': resource_filename(
                           __name__, "data/cross_sections_ups.json"),
                       'haxpes': resource_filename(
                           __name__, "data/cross_sections_haxpes.json")}

    if weighting.lower() in weighting_files:
        with open(weighting_files[weighting.lower()], 'r') as f:
            cross_sections = json_load(f)

    else:
        if not os.path.exists(weighting):
            raise Exception("Cross-sections file {0} does not "
                            "exist!".format(weighting))
        with open(weighting) as f:
            cross_sections = json_load(f)

    return cross_sections


def get_cross_sections_json(element, path):
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
        element (str): Element symbol
        path (str): Path to JSON file

    Returns:
        dict: Weighted photoionization cross-sections for each orbital in form
            {'s': c1, 'p': c2, ...} in tabulated units.
    """

    if os.path.exists(source):
        with open(source, 'r') as f:
            cross_sections = json_load(f)
    else:
        raise Exception("Cross-sections file {0} does not "
                        "exist!".format(weighting))

    return cross_sections[element]


def get_cross_sections_yeh(element, source):
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
        element (str): Element symbol
        source (str): Label corresponding to radiation source. Accepted values
            'xps' (1486.6 eV), 'ups' (40.8 eV), 'haxpes' (8047.8).

    Returns:
        dict: Weighted photoionization cross-sections in megaBarns/electron
            for each orbital in form {'s': c1, 'p': c2, ...}
    """

    weighting_files = {'xps': resource_filename(
                       __name__, "data/cross_sections.json"),
                       'ups': resource_filename(
                           __name__, "data/cross_sections_ups.json"),
                       'haxpes': resource_filename(
                           __name__, "data/cross_sections_haxpes.json")}

    if source.lower() in weighting_files:
        path = weighting_files[source.lower()]
        return get_cross_sections_json(element, path)

    else:
        raise Exception(
            "Energy source '{0}' not recognised. ".format(source),
            "Accepted values: {0}".format(", ".join((weighting_files.keys()))))


def get_cross_sections_scofield(element, energy):
    """Get valence-band cross-sections from fitted data

    Energy-dependent cross-sections have been averaged and weighted for
    the uppermost s, p, d, f orbitals from data tabulated by Scofield.
    The energy/cross-section relationship was fitted to an order-8
    polynomial on a log-log scale.

    Multiple energy values can be evaluated simultaneously by passing an
    array-like group of energies as ``energy``. In this case the cross-section
    values will be arrays with the same shape as the energy arrays.

    Args:
        element (str): Element symbol
        energy (float or array-like): Incident energy in keV

    Returns:
        dict:
            Weighted photoionization cross-sections in Barns/electron
            for each orbital in form {'s': c1, 'p': c2, ...}
    """

    db_file = resource_filename(__name__, "data/scofield_data.db")

    def _eval_fit(energy, coeffs):
        """Convert log-log polynomial fit to cross-section value"""
        log_val = polyval(coeffs, log(energy))
        return exp(log_val)

    with sqlite3.connect('galore/data/scofield_data.db') as con:
        cur = con.cursor()
        cur.execute('SELECT orbital, coeffs_np FROM fits WHERE Element=?;',
                    [element])
        orbitals_fits = cur.fetchall()

    return {
        orb: _eval_fit(energy, np_fromstr(coeffs))
        for orb, coeffs in orbitals_fits
        }
