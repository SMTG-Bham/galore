from __future__ import division, absolute_import
import unittest

from galore.cross_sections import get_cross_sections_yeh

class test_yeh_data(unittest.TestCase):
    def test_xps_yeh(self):
        """Check Al k-alpha data from Yeh/Lindau"""
        Lr_cs = get_cross_sections_yeh('xps')['Lr']
        self.assertAlmostEqual(Lr_cs['p'], 0.001666666666666667)

        H_cs = get_cross_sections_yeh('xps')['H']
        self.assertIsNone(H_cs['f'])

    def test_ups_yeh(self):
        """Check He(II) data from Yeh/Lindau"""
        Pr_cs = get_cross_sections_yeh('ups')['Pr']
        self.assertAlmostEqual(Pr_cs['f'], 0.848)
        
