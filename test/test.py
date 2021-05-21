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


class test_dos_functions(unittest.TestCase):
    def test_simple_dos_spikes(self):
        """Test total DOS / spectrum plotter from CSV data, spike sampling"""
        ylabel = 'some label'
        xmin = -3
        xmax = 220
        sampling = 1e-1
        plt = simple_dos_from_files(input=path_join(test_dir,
                                                    'test_xy_data.csv'),
                                    return_plt=True, xmax=xmax, xmin=xmin,
                                    sampling=sampling,
                                    spikes=True,
                                    lorentzian=2.3, gaussian=3.2,
                                    csv=False, txt=False, plot=None,
                                    units='cm-1', ymax=None, ymin=None,
                                    ylabel=ylabel,
                                    flipx=False)
        fig = plt.gcf()
        ax = fig.axes[0]
        self.assertEqual(ax.get_ylabel(), ylabel)
        self.assertEqual(ax.get_xlabel(), r'cm$^{-1}$')
        self.assertAlmostEqual(ax.get_xlim()[0], xmin, places=2)
        self.assertLess(ax.get_xlim()[1], xmax)
        self.assertGreater(ax.get_xlim()[1], (xmax * 0.99))
        self.assertEqual(len(ax.lines), 1)
        xvals, yvals = ax.lines[0].get_xydata().T
        self.assertAlmostEqual(xvals[5], (xmin + 5 * sampling))
        self.assertAlmostEqual(yvals[5], 0.0, places=3)
        self.assertAlmostEqual(yvals[2000], 0.65245445, places=4)

    def test_simple_dos_linear(self):
        """Test total DOS / spectrum plotter from CSV data, linear sampling"""
        ylabel = 'some label'
        xmin = -3
        xmax = 220
        sampling = 1e-1
        plt = simple_dos_from_files(input=path_join(test_dir,
                                                    'test_xy_data.csv'),
                                    return_plt=True, xmax=xmax, xmin=xmin,
                                    sampling=sampling,
                                    lorentzian=2.3, gaussian=3.2,
                                    csv=False, txt=False, plot=None,
                                    units='cm-1', ymax=None, ymin=None,
                                    ylabel=ylabel,
                                    flipx=False)
        fig = plt.gcf()
        ax = fig.axes[0]
        self.assertEqual(ax.get_ylabel(), ylabel)
        self.assertEqual(ax.get_xlabel(), r'cm$^{-1}$')
        self.assertAlmostEqual(ax.get_xlim()[0], xmin, places=2)
        self.assertLess(ax.get_xlim()[1], xmax)
        self.assertGreater(ax.get_xlim()[1], (xmax * 0.99))
        self.assertEqual(len(ax.lines), 1)
        xvals, yvals = ax.lines[0].get_xydata().T
        self.assertAlmostEqual(xvals[5], (xmin + 5 * sampling))
        self.assertAlmostEqual(yvals[5], 0.0, places=3)
        self.assertAlmostEqual(yvals[2000], 98.64411, places=4)


class test_array_functions(unittest.TestCase):
    def test_delta(self):
        self.assertEqual(galore.delta(1, 1.5, w=1), 1)

    def test_xy_to_1d_spikes(self):
        """Check resampling of distinct values as spikes"""
        assert_array_equal(
            galore.xy_to_1d(
                np.array([[2.1, 0.6], [4.3, 0.2], [5.1, 0.3]]), range(6),
                spikes=True),
            np.array([0., 0., 0.6, 0., 0.2, 0.3]))

    def test_xy_to_1d_linear(self):
        """Check resampling with linear interpolation"""
        assert_array_equal(
            galore.xy_to_1d(
                np.array([[1., 0.5], [3., 1.5]]), range(6),
                spikes=False),
            np.array([0., 0.5, 1.0, 1.5, 0., 0.0]))

    def test_gaussian(self):
        self.assertAlmostEqual(galore.gaussian(3., f0=1, fwhm=(3 * 2.35482)),
                               0.8007374029168)


class test_io_functions(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_identify_raman(self):
        doscar_path = path_join(test_dir, 'DOSCAR.1')
        raman_path = path_join(test_dir, 'CaF2', 'raman_lda_500.dat')
        self.assertFalse(galore.formats.is_vasp_raman(doscar_path))
        self.assertTrue(galore.formats.is_vasp_raman(raman_path))

    def test_identify_doscar(self):
        doscar_path = path_join(test_dir, 'DOSCAR.1')
        raman_path = path_join(test_dir, 'CaF2', 'raman_lda_500.dat')
        self.assertTrue(galore.formats.is_doscar(doscar_path))
        self.assertFalse(galore.formats.is_doscar(raman_path))

    def test_write_txt(self):
        x_values = range(5)
        y_values = [x**2 / 200 for x in range(5)]
        filename = path_join(self.tempdir, 'write_txt_test.txt')
        galore.formats.write_txt(
            x_values, y_values, filename=filename, header="# Frequency  Value")
        with open(filename, 'r') as f:
            self.assertEqual(f.read(), txt_test_string)

    def test_write_txt_stdout(self):
        with stdout_redirect() as stdout:
            x_values = range(5)
            y_values = [x**2 / 200 for x in range(5)]
            filename = path_join(self.tempdir, 'write_txt_test.txt')
            galore.formats.write_txt(
                x_values, y_values, filename=None, header="# Frequency  Value")
            self.assertEqual(stdout.getvalue(), txt_test_string)

    def test_write_csv(self):
        x_values = range(5)
        y_values = [x**2 / 200 for x in range(5)]
        filename = path_join(self.tempdir, 'write_csv_test.csv')
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
        doscar_path = path_join(test_dir, 'DOSCAR.1')
        data = galore.formats.read_doscar(doscar_path)
        self.assertEqual(data[20, 0], -31.795)
        self.assertEqual(data[14, 1], 0.329)

    def test_read_raman(self):
        raman_path = path_join(test_dir, 'CaF2', 'raman_lda_500.dat')
        raman_data = np.array([[3.45589820e+02, 9.89999400e-01],
                               [3.45589690e+02, 9.89999400e-01],
                               [3.45580570e+02, 9.89999400e-01],
                               [2.78757900e+02, 0.00000000e+00],
                               [2.78757810e+02, 0.00000000e+00],
                               [2.78757760e+02, 1.00000000e-07],
                               [6.11230000e-01, 0.00000000e+00],
                               [6.11260000e-01, 0.00000000e+00],
                               [6.11920000e-01, 3.80000000e-06]])
        assert_array_equal(galore.formats.read_vasp_raman(raman_path),
                           raman_data)

    def test_read_txt_pdos_spin(self):
        sample_txt = path_join(test_dir, 'spin_samples', 'mixed.dat')
        data = galore.formats.read_pdos_txt(sample_txt)
        self.assertAlmostEqual(data['s'][0], 0.1)
        self.assertAlmostEqual(data['s'][6], 1.1)
        self.assertAlmostEqual(data['p'][0], 0.5)
        self.assertAlmostEqual(data['p'][6], 2.5)
        self.assertAlmostEqual(data['d'][1], 0.4)
        self.assertIn('f', data.dtype.names)
        self.assertNotIn('fup', data.dtype.names)
        self.assertNotIn('f(down)', data.dtype.names)
        self.assertAlmostEqual(data['f'][1], 1.1)

    @unittest.skipUnless(has_pymatgen, "requires pymatgen")
    def test_read_vasprun_totaldos(self):
        vr_path = path_join(test_dir, 'MgO', 'vasprun.xml.gz')
        data = galore.formats.read_vasprun_totaldos(vr_path)
        self.assertEqual(data[150, 0], -17.2715)
        self.assertEqual(data[195, 1], 16.8066)

    @unittest.skipUnless(has_pymatgen, "requires pymatgen")
    def test_read_vasprun_pdos(self):
        vr_path = path_join(test_dir, 'MgO', 'vasprun.xml.gz')
        pdos = galore.formats.read_vasprun_pdos(vr_path)
        self.assertEqual(pdos['Mg']['s'][150], 0.053)
        self.assertEqual(pdos['O']['p'][189], 0.004)

    @unittest.skipUnless(has_pymatgen, "requires pymatgen")
    def test_identify_complete_dos(self):
        from monty.serialization import loadfn
        dos = loadfn(path_join(test_dir, 'MgO', 'CompleteDos.yaml.gz'))
        self.assertTrue(galore.formats.is_complete_dos(dos))

        raman_path = path_join(test_dir, 'CaF2', 'raman_lda_500.dat')
        self.assertFalse(galore.formats.is_complete_dos(raman_path))

    @unittest.skipUnless(has_pymatgen, "requires pymatgen")
    def test_read_complete_dos(self):
        from monty.serialization import loadfn
        dos = loadfn(path_join(test_dir, 'MgO', 'CompleteDos.yaml.gz'))
        pdos = galore.formats.read_vasprun_pdos(dos)
        self.assertEqual(pdos['Mg']['s'][150], 0.053)
        self.assertEqual(pdos['O']['p'][189], 0.004)

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
