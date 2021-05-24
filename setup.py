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
        version='0.6.2',
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
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.6',                     
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics'
            ],
        keywords=('spectroscopy spectra chemistry physics raman xps haxpes pes'
                  ' photoelectron dos pdos gaussian lorentzian broadening'),
        include_package_data=True,
        packages=find_packages(exclude=['docs', 'test']),
        install_requires=['numpy', 'scipy', 'matplotlib'],
        extras_require={'docs': ["sphinx",
                                 "sphinx_rtd_theme",
                                 "sphinx-argparse",
                                 "sphinxcontrib-bibtex"],
                        'vasp': ['monty <= v4.0.2;python_version < "3.6"',
                                 'pymatgen == 2018.1.19;python_version ~= "3.4"',
                                 'ruamel.yaml <= 0.15.94;python_version ~= "3.4"',
                                 'numpy ~= 1.16;python_version ~= "3.4"',
                                 'pymatgen <= 2019.6.20;python_version ~= "3.5"',
                                 'pymatgen <= 2021.2.8.1;python_version ~= "3.6"',
                                 'pymatgen;python_version >= "3.7"',
                                 'numpy >= 1.17;python_version >= "3.6"']},
        python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
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
