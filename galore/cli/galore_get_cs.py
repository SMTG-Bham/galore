#! /usr/bin/env python3
###############################################################################
#                                                                             #
# GALORE: Gaussian and Lorentzian broadening for simulated spectra            #
#                                                                             #
# Developed by Adam J. Jackson and Alex Ganose                                #
# at University College London (2018)                                         #
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
from argparse import ArgumentParser
import galore.cross_sections


def main():
    parser = get_parser()
    args = parser.parse_args()
    args = vars(args)
    run(**args)


def get_parser():
    parser = ArgumentParser()
    # parser.add_argument('energy', type=str,
    #                   help="""
    #   Photon energy, expressed as source type: "he2" for He (II), "alka" for
    #    Al k-alpha, (values from Yeh/Lindau (1985)) or as energy in keV (values
    #    from polynomial fit to Scofield (1973)).""")
    # parser.add_argument('elements', type=str, nargs='+', help="""
    #    Space-separated symbols for elements in material.""")

    parser.add_argument('energy', type=str,
                        help="""
        If you don't input dataset:
        Photon energy, expressed as source type: "he2" for He (II), "alka" for
        Al k-alpha, (values from Yeh/Lindau (1985)) or as energy in keV (values
        from polynomial fit to Scofield (1973)).
        if you input dataset:
        Photon energy, 1 to 1500keV for Scofield dataset, 10.2 to 8047.8 eV for Yeh dataset""")

    parser.add_argument('elements',  nargs='+',
                        help="""
        Space-separated symbols for elements in material.""")

    parser.add_argument('--dataset', type=str.lower, choices=['scofield', 'yeh'],
                        help="""Accepted values are 'Scofield' and 'Yeh """)

    return parser


def run(energy, elements, dataset=None):
    cross_sections = galore.get_cross_sections(energy, elements, dataset)
    logging = galore.cross_sections.cross_sections_info(cross_sections)

    ###some input will lead to None cross sections result 
    if cross_sections is None:
        logging.warning("The cross section is None, please check the input")

    ## inform user if energy input is out of range 
    if dataset.lower() == 'scofield' and float(energy) > 1500:
        logging.warning('The maximum energy of Scofield is 1500 keV')

    ## inform user the closest energy of input  
    if dataset != None:
        logging.warning('The closest energy of input is {energy}'.format(
            energy=cross_sections['energy']))

    else:
        logging.info("Photoionisation cross sections per electron:")

        for element in elements:

            if 'warning' in cross_sections[element]:
                logging.warning("  {0}: {1}".format(
                    element, cross_sections[element]['warning']))
            else:
                orbitals = cross_sections[element]

                for orbital, value in orbitals.items():
                    if orbital == 'energy':
                        pass
                    if value is None:
                        pass
                    else:
                        logging.info("   {0} {1}: {2:.3e}".format(element,
                                                                  orbital, value))
