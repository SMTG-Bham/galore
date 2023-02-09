from pkg_resources import resource_filename
import numpy as np
import galore
import unittest
from numpy.testing import assert_array_almost_equal


class test_process_pdos(unittest.TestCase):
    def test_lorentzian(self):
        self.assertAlmostEqual(galore.lorentzian(3., f0=1, fwhm=(3 * 2.35482)),
                               0.068238617255)

    def test_broaden(self):
        broadened_data = galore.xy_to_1d(np.array([[1., 0.5], [3., 1.5]]),
                                         range(6),
                                         spikes=False)
        lorentzian = 0.2

        assert_array_almost_equal(
            galore.broaden(broadened_data,
                           d=2,
                           dist='lorentzian',
                           width=lorentzian),
            np.array([
                0.00595715, 1.60246962, 3.19897467, 4.7825862, 0.01190685, 0.
            ]))

    def test_process_pdos(self):
        vasprun = resource_filename(__name__, 'SnO2/vasprun.xml.gz')
        xmin, xmax = (-10, 4)
        weighting = 'Alka'

        plotting_data = galore.process_pdos(input=[vasprun],
                                            gaussian=0.3,
                                            lorentzian=0.2,
                                            xmin=xmin,
                                            xmax=xmax,
                                            weighting=weighting)
        self.assertEqual(plotting_data['O']['energy'][0], -10.0)


if __name__ == '__main__':
    unittest.main()
