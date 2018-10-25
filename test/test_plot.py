import unittest
from os.path import join as path_join
from os.path import abspath, dirname

import matplotlib.pyplot as plt

import galore.plot

test_dir = abspath(dirname(__file__))


class test_pdos_plotting(unittest.TestCase):
    def test_guess_xlabel(self):
        self.assertEqual(galore.plot.guess_xlabel(), '')
        self.assertEqual(galore.plot.guess_xlabel(units='CM'),
                         r'cm$^{-1}$')
        self.assertEqual(galore.plot.guess_xlabel(units='THz'),
                         r'THz')
        self.assertEqual(galore.plot.guess_xlabel(units='Fish'),
                         'Fish')
        self.assertEqual(galore.plot.guess_xlabel(units=r'SPLINES s$^{-1}$',
                                                  energy_label='RETICULATION'),
                         r'RETICULATION / SPLINES s$^{-1}$')
        self.assertEqual(galore.plot.guess_xlabel(energy_label='RETICULATION'),
                         r'RETICULATION')
        self.assertEqual(galore.plot.guess_xlabel(units='ev', flipx=True),
                         r'Binding energy / eV')
        self.assertEqual(galore.plot.guess_xlabel(units='ev', flipx=True,
                                                  energy_label='UNUSED'),
                         r'Binding energy / eV')
        self.assertEqual(galore.plot.guess_xlabel(units='SPLINES', flipx=True,
                                                  energy_label='RETICULATION'),
                         '-RETICULATION / SPLINES')
        self.assertEqual(galore.plot.guess_xlabel(flipx=True,
                                                  energy_label='Reticulation'),
                         r'-Reticulation')
        self.assertEqual(galore.plot.guess_xlabel(flipx=True),
                         'Binding energy')

    def test_overlay(self):
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
