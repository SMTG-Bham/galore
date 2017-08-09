from __future__ import division, absolute_import

import os
import sys
import unittest
import shutil
import tempfile

import numpy.testing
from numpy.testing import assert_array_equal
import numpy as np

import galore
import galore.formats

from contextlib import contextmanager
import io


@contextmanager
def stdout_redirect():
    """Enable tests to inspect stdout in suitable format for Python version"""
    if sys.version_info > (3,):
        output = io.StringIO()
    else:
        output = io.BytesIO()
    sys.stdout = output
    try:
        yield output
    finally:
        output.close()


class test_array_functions(unittest.TestCase):
    # The Numpy unit testing framework is used as this provides
    # comparison tools for ndarrays
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_delta(self):
        self.assertEqual(galore.delta(1, 1.5, w=1), 1)

    def test_xy_to_1d(self):
        assert_array_equal(
            galore.xy_to_1d(
                np.array([[2.1, 0.6], [4.3, 0.2], [5.1, 0.3]]), range(6)),
            np.array([0., 0., 0.6, 0., 0.2, 0.3]))

    def test_gaussian(self):
        self.assertAlmostEqual(galore.gaussian(3., f0=1, c=3), 0.8007374029168)

    def test_write_txt(self):
        x_values = range(5)
        y_values = [x**2 / 200 for x in range(5)]
        filename = os.path.join(self.tempdir, 'write_txt_test.txt')
        galore.formats.write_txt(
            x_values, y_values, filename=filename, header="# Frequency  Value")
        with open(filename, 'r') as f:
            self.assertEqual(f.read(), txt_test_string)

    def test_write_txt_stdout(self):
        with stdout_redirect() as stdout:
            x_values = range(5)
            y_values = [x**2 / 200 for x in range(5)]
            filename = os.path.join(self.tempdir, 'write_txt_test.txt')
            galore.formats.write_txt(
                x_values, y_values, filename=None, header="# Frequency  Value")
            self.assertEqual(stdout.getvalue(), txt_test_string)

    def test_write_csv(self):
        x_values = range(5)
        y_values = [x**2 / 200 for x in range(5)]
        filename = os.path.join(self.tempdir, 'write_csv_test.csv')
        galore.formats.write_csv(
            x_values,
            y_values,
            filename=filename,
            header=["Frequency", "Value"])
        with open(filename, 'r') as f:
            self.assertEqual(f.read(), csv_test_string)

    def test_write_csv_stdout(self):
        with stdout_redirect() as stdout:
            x_values = range(5)
            y_values = [x**2 / 200 for x in range(5)]
            galore.formats.write_csv(
                x_values,
                y_values,
                filename=None,
                header=["Frequency", "Value"])
            self.assertEqual(stdout.getvalue(), csv_test_string)

    def test_read_spinpol_doscar(self):
        doscar_path = os.path.join(os.path.dirname(__file__), 'DOSCAR.1')
        data = galore.formats.read_doscar(doscar_path)
        self.assertEqual(data[20,0], -31.795)
        self.assertEqual(data[14,1], 0.329)

txt_test_string = """# Frequency  Value
0.000000e+00 0.000000e+00
1.000000e+00 5.000000e-03
2.000000e+00 2.000000e-02
3.000000e+00 4.500000e-02
4.000000e+00 8.000000e-02
"""

csv_test_string = os.linesep.join(
    ("Frequency,Value", "0,0.0", "1,0.005", "2,0.02", "3,0.045", "4,0.08", ""))

if __name__ == '__main__':
    unittest.main()
