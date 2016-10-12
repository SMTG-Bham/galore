import os, sys
import unittest
import shutil
import tempfile

import numpy.testing
import numpy as np

import galore
import galore.formats

from contextlib import contextmanager
import io


@contextmanager
def stdout_to_bytes():
    output = io.BytesIO()
    sys.stdout = output
    try:
        yield output
    finally:
        output.close()


class test_array_functions(numpy.testing.TestCase):
    # The Numpy unit testing framework is used as this provides
    # comparison tools for ndarrays
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_delta(self):
        self.assertEqual(galore.delta(1, 1.5, w=1), 1)

    def test_xy_to_1d(self):
        np.testing.assert_array_equal(
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
        with stdout_to_bytes() as stdout:
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
        with stdout_to_bytes() as stdout:
            x_values = range(5)
            y_values = [x**2 / 200 for x in range(5)]
            galore.formats.write_csv(
                x_values,
                y_values,
                filename=None,
                header=["Frequency", "Value"])
            self.assertEqual(stdout.getvalue(), csv_test_string)


txt_test_string = """# Frequency  Value
0.000000e+00 0.000000e+00
1.000000e+00 0.000000e+00
2.000000e+00 0.000000e+00
3.000000e+00 0.000000e+00
4.000000e+00 0.000000e+00
"""

csv_test_string = """Frequency,Value\r
0,0\r
1,0\r
2,0\r
3,0\r
4,0\r
"""

if __name__ == '__main__':
    unittest.main()
