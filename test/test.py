import unittest
import numpy.testing
import numpy as np
import galore


class test_array_functions(numpy.testing.TestCase):
    # The Numpy unit testing framework is used as this provides
    # comparison tools for ndarrays

    def test_delta(self):
        self.assertEqual(galore.delta(1, 1.5, w=1), 1)

    def test_xy_to_1d(self):
        np.testing.assert_array_equal(
            galore.xy_to_1d(
                np.array([[2.1, 0.6], [4.3, 0.2], [5.1, 0.3]]), range(6)),
            np.array([0., 0., 0.6, 0., 0.2, 0.3]))

    def test_gaussian(self):
        self.assertAlmostEqual(galore.gaussian(3., f0=1, c=3), 0.8007374029168)


if __name__ == '__main__':
    unittest.main()
