import unittest
from os.path import join as path_join
from os.path import abspath, dirname
from collections import OrderedDict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import galore.plot

test_dir = abspath(dirname(__file__))


class test_plotting_tools(unittest.TestCase):
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


class test_pdos_plotting(unittest.TestCase):
    def test_plot_pdos(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        pdos_data = OrderedDict([('Na',
                                  OrderedDict([
                                      ('energy', np.array([1, 2, 3, 4, 5])),
                                      ('s', np.array([0, 0, 0, 1, 1])),
                                      ('p', np.array([1, 1, 4, 1, 0]))])),
                                 ('Cl',
                                  OrderedDict([
                                      ('energy', np.array([1, 2, 3, 4, 5])),
                                      ('s', np.array([1, 1, 0, 0, 0])),
                                      ('p', np.array([0, 1, 2, 2, 1]))]))])
        offset = 0.5


        galore.plot.plot_pdos(pdos_data, ax=ax, offset=offset)

        line1 = ax.lines[0]
        xy1 = line1.get_xydata()
        self.assertEqual(xy1[1, 0], 2 + offset)
        self.assertEqual(xy1[1, 1], 0)

        line2 = ax.lines[1]
        xy2 = line2.get_xydata()
        self.assertEqual(xy2[2, 0], 3 + offset)
        self.assertEqual(xy2[2, 1], 4)

        line3 = ax.lines[2]
        xy3 = line3.get_xydata()
        self.assertEqual(xy3[0, 0], 1 + offset)
        self.assertEqual(xy2[0, 1], 1)

        tdos = ax.lines[4]
        xyt = tdos.get_xydata()
        self.assertEqual(xyt[2, 0], 3 + offset)
        self.assertEqual(xyt[3, 1], 1 + 1 + 0 + 2)


class test_tdos_plotting(unittest.TestCase):
    def test_plot_tdos(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        xvals = np.linspace(-5, 5, 21)
        offset = 0.8

        galore.plot.plot_tdos(xvals, xvals**2, ax=ax, offset=offset)

        self.assertEqual(len(ax.lines), 1)
        self.assertEqual(ax.lines[0].get_xydata()[11, 0], 0.5 + offset)
        self.assertAlmostEqual(ax.lines[0].get_xydata()[18, 1], 4.0**2)

        self.assertAlmostEqual(ax.get_ylim()[0], 0)
        self.assertAlmostEqual(ax.get_ylim()[1], 1.1 * 5**2)
