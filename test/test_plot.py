import unittest
from os.path import join as path_join
from os.path import abspath, dirname

import galore.plot

test_dir = abspath(dirname(__file__))


class test_pdos_plotting(unittest.TestCase):
    def test_pdos_from_data(self):
        pass

    def test_overlay(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        galore.plot.add_overlay(plt, path_join(test_dir, 'test_xy_data.csv'),
                                overlay_scale=2, overlay_offset=1,
                                overlay_style="x:", overlay_label="foo")
        ax = plt.gca()
        line = ax.lines[0]
        xy = line.get_xydata()
        self.assertEqual(xy[3, 0], 201)
        self.assertEqual(xy[3, 1], 0.6)
        self.assertEqual(xy.shape, (8, 2))
