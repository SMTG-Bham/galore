"""
Galore: Gaussian and Lorentzian broadening of simulated spectra
"""

from os.path import abspath, dirname
from setuptools import setup, find_packages
import unittest

project_dir = abspath(dirname(__file__))


def unit_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('test', pattern='test*.py')
    return test_suite

if __name__ == "__main__":

    setup(
        name='galore',
        version='0.9.0',
        description='Broadening and weighting for simulated spectra',
        long_description="""
    Apply Gaussian and Lorentzian broadening to data from ab initio
    calculations. The two main intended applications are

    1. Broadening of electronic density-of-states to simulate photoemission
       spectroscopy (PES) data. Orbital contributions may also be weighted to
       account for the frequency-dependent photoionisation cross-section.

    2. Application of Lorentzian instrumental broadening to simulated
       Raman spectra from DFPT calculations.
    """,
        url="https://github.com/SMTG-UCL/galore",
        author="Scanlon Materials Theory Group",
        author_email="d.scanlon@ucl.ac.uk",
        license='GPL v3',

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics'
            ],
        keywords=('spectroscopy spectra chemistry physics raman xps haxpes pes'
                  ' photoelectron dos pdos gaussian lorentzian broadening'),
        include_package_data=True,
        packages=find_packages(exclude=['docs', 'test']),
        install_requires=['numpy>= 1.17', 'scipy',
                          'matplotlib; python_version >= "3.8"'],
        extras_require={'docs': ["sphinx",
                                 "sphinx_rtd_theme",
                                 "sphinx-argparse",
                                 "sphinxcontrib-bibtex"],
                        'vasp': ['pymatgen']},
        python_requires='>=3.8, <4',
        entry_points={
            'console_scripts': [
                'galore=galore.cli.galore:main',
                'galore-get-cs=galore.cli.galore_get_cs:main',
                'galore-plot-cs=galore.cli.galore_plot_cs:main'
                ]
            },
        test_suite='setup.unit_tests'
        )

# If a package includes data files (e.g. elemental masses), these should be
# added to setup as package_data={'package_name': ['rel_path2datafile.dat']}
# Other top-level data files (e.g. example config files) can be added with
# data_files=[('installation_directory', ['rel_path/datafile.dat'])].
# See https://packaging.python.org/distributing/
#
# For GUI, add gui_scripts to entry_points
