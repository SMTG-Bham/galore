import os
from os.path import join as path_join
import sys
import unittest
import shutil
import tempfile

import numpy.testing
from numpy.testing import assert_array_equal
import numpy as np

import galore
import galore.formats
from galore.cli.galore import simple_dos_from_files
import galore.plot

from contextlib import contextmanager
import io

test_dir = os.path.abspath(os.path.dirname(__file__))

try:
    import pymatgen
    has_pymatgen = True
except ImportError:
    has_pymatgen = False


a = galore.process_1d_data(input=['vasprun.xml'],
                    gaussian=None, lorentzian=None,
                    sampling=1e-2,
                    xmin=None, xmax=None,
                    spikes=False,
                    )