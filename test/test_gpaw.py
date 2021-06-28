import unittest
import sys
import io
from os.path import join as path_join
from pkg_resources import resource_filename
from galore.formats import read_gpaw_totaldos, read_gpaw_pdos
from contextlib import contextmanager

try:
    from gpaw import GPAW
    import ase.build
    has_gpaw = True
except ImportError:
    has_gpaw = False

import ase.build

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


@unittest.skipIf(not has_gpaw, "GPAW not available")
class TestGPAW(unittest.TestCase):
    gpaw_file = resource_filename(__name__, path_join('CdTe', 'CdTe.gpw'))

    ref_vbm = 4.948260
    efermi = 5.0761385

    def test_tdos_read(self):
        """Check TDOS can be read from GPAW file"""
        with stdout_redirect() as stdout:
            tdos = read_gpaw_totaldos(self.gpaw_file, npts=1000)
        self.assertEqual(tdos.shape, (1000, 2))
        self.assertAlmostEqual(tdos[-1, 0], 4.3982112, places=6)
        self.assertAlmostEqual(tdos[-1, 1], 1.5670867e-8, places=6)

    def test_energy_refs(self):
        """Check alternative GPAW energy references"""
        with stdout_redirect() as stdout:
            calc = GPAW(self.gpaw_file)
        self.assertAlmostEqual(calc.get_homo_lumo()[0], self.ref_vbm, places=6,
                               msg="VBM from GPAW doesn't match reference")
        self.assertAlmostEqual(calc.get_fermi_level(), self.efermi, places=6,
                               msg="E-Fermi from GPAW doesn't match reference")

    def test_tdos_refs(self):
        """Check GPAW TDOS energy alignment options"""
        with stdout_redirect() as stdout:
            tdos_0 = read_gpaw_totaldos(self.gpaw_file, npts=1000, ref=None)
            tdos_vbm = read_gpaw_totaldos(self.gpaw_file, npts=1000, ref='vbm')
            tdos_efermi = read_gpaw_totaldos(self.gpaw_file, npts=1000,
                                             ref='efermi')

        self.assertAlmostEqual(tdos_vbm[0, 0], tdos_0[0, 0] - self.ref_vbm)
        self.assertAlmostEqual(tdos_efermi[0, 0], tdos_0[0, 0] - self.efermi)

    def test_pdos_read(self):
        with stdout_redirect() as stdout:
            pdos = read_gpaw_pdos(self.gpaw_file, npts=1000)
        for species in ('Cd', 'Te'):
            self.assertIn(species, pdos)
        for column in ('s', 'p', 'd', 'f', 'energy'):
            self.assertIn(column, pdos['Cd'])
        for species in ('Cd', 'Te'):
            self.assertIsNone(pdos[species]['f'])
        self.assertAlmostEqual(max(pdos['Cd']['s']), 0.00295165, places=6,
                               msg="PDOS value doesn't match reference")
        self.assertAlmostEqual(pdos['Cd']['energy'][100], -9.5542409,
                               places=6,
                               msg="PDOS energy value doesn't match reference")
        self.assertTrue((pdos['Cd']['energy'] == pdos['Te']['energy']).all(),
                        msg="PDOS energy ranges not consistent")

    def test_pdos_refs(self):
        """Check GPAW PDOS energy alignment options"""
        with stdout_redirect() as stdout:
            pdos_0 = read_gpaw_pdos(self.gpaw_file,
                                    npts=1000, ref=None)
            pdos_vbm = read_gpaw_pdos(self.gpaw_file,
                                      npts=1000, ref='vbm')
            pdos_efermi = read_gpaw_pdos(self.gpaw_file,
                                         npts=1000, ref='efermi')

        self.assertAlmostEqual(pdos_vbm['Te']['energy'][0],
                               pdos_0['Te']['energy'][0] - self.ref_vbm)
        self.assertAlmostEqual(pdos_efermi['Te']['energy'][0],
                               pdos_0['Te']['energy'][0] - self.efermi)
