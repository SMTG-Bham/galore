import unittest
try:
    from unittest import mock
except ImportError:
    import mock
from pkg_resources import resource_filename

from galore.cross_sections import get_cross_sections
from galore.cross_sections import get_cross_sections_json
from galore.cross_sections import get_cross_sections_yeh
from galore.cross_sections import get_cross_sections_scofield


def mock_get_cross_sections_json(path):
    return (path, 'JSON')


def mock_get_cross_sections_yeh(source):
    return (source, 'YEH')


def mock_get_cross_sections_scofield(energy, elements):
    return (energy, elements, 'SCOFIELD')


class test_cross_sections_dispatch(unittest.TestCase):
    @mock.patch(
        'galore.cross_sections.get_cross_sections_json',
        side_effect=mock_get_cross_sections_json)
    def test_json_dispatch(self, mock_func):
        """Check JSON weighting files are dispatched correctly"""
        json_file = 'nonexistent.json'
        self.assertEqual(get_cross_sections(json_file),
                         (json_file, 'JSON'))
        self.assertEqual(get_cross_sections(json_file,
                                            elements=['Na']),
                         (json_file, 'JSON'))

    @mock.patch('galore.cross_sections.get_cross_sections_yeh',
                         side_effect=mock_get_cross_sections_yeh)
    def test_yeh_dispatch(self, mock_func):
        """Check tabulated weightings are dispatched correctly"""
        self.assertEqual(get_cross_sections('alka'),
                         ('alka', 'YEH'))

    @mock.patch('galore.cross_sections.get_cross_sections_scofield',
                         side_effect=mock_get_cross_sections_scofield)
    def test_scofield_dispatch(self, mock_func):
        """Check parametrised weightings are dispatched correctly"""
        self.assertEqual(get_cross_sections(42),
                         (42., None, 'SCOFIELD'))
        self.assertEqual(get_cross_sections('1.4e2',
                                            elements=['Sc', 'O']),
                         (1.4e2, ['Sc', 'O'], 'SCOFIELD'))


class test_json_data(unittest.TestCase):
    def test_json_error(self):
        """Check we can't open non-existent JSON files"""
        with self.assertRaises(IOError):
            get_cross_sections_json('non-existent.json')

    def test_json_read(self):
        """Check JSON file is opened without trouble"""
        json_file = resource_filename(__name__, 'json_test.json')
        json_data = get_cross_sections_json(json_file)
        self.assertEqual(json_data['He']['s'], 'CORRECT')


class test_yeh_data(unittest.TestCase):
    def test_xps_yeh(self):
        """Check Al k-alpha data from Yeh/Lindau"""
        Lr_cs = get_cross_sections_yeh('AlKa')['Lr']
        self.assertAlmostEqual(Lr_cs['p'], 0.001666666666666667)

        H_cs = get_cross_sections_yeh('alka')['H']
        self.assertIsNone(H_cs['f'])

    def test_ups_yeh(self):
        """Check He(II) data from Yeh/Lindau"""
        Pr_cs = get_cross_sections_yeh('He2')['Pr']
        self.assertAlmostEqual(Pr_cs['f'], 0.848)

class test_yeh_old_keys(unittest.TestCase):
    def test_yeh_old_keys(self):
        with self.assertRaises(ValueError):
            get_cross_sections('xps')
        with self.assertRaises(ValueError):
            get_cross_sections('ups')
        with self.assertRaises(ValueError):
            get_cross_sections('haxpes')
        

class test_scofield_data(unittest.TestCase):
    def setUp(self):
        self.ref_values = [('C', 's', 2, 1,
                            # Raw value from table corresponds to full
                            # shell in this case. Parametrised value
                            # is multiplied by occupancy to match.
                            1.9334e3),
                           ('Ga', 'd', 10, 5,
                            # 3/2 and 5/2 orbital energies are
                            # 1. Normalised to 1 electron
                            # 2. Combined as simple mean
                            # 3. Multiplied by total shell occupancy
                            (6.3849e1 / 4 + 9.1599e1 / 6) / 2 * 10)]

    def test_scofield_limits(self):
        """Check Scofield parametrisation refuses to extrapolate"""
        with self.assertRaises(ValueError):
            get_cross_sections_scofield(0.5, elements=['H'])
        with self.assertRaises(ValueError):
            get_cross_sections_scofield((10, 11, 0.5), elements=['H'])
        with self.assertRaises(ValueError):
            get_cross_sections_scofield(1600, elements=['H'])
        with self.assertRaises(ValueError):
            get_cross_sections_scofield((10, 11, 1600, 12), elements=['H'])

    def test_scofield_ref(self):
        """Check Scofield parametrisation: spot-check vs tables"""

        for el, orb, occ, energy, value in self.ref_values:
            cs = get_cross_sections_scofield(energy, elements=[el])
            # Check error is below 1 percent; small error is due to
            # fitting, not implementation in this part of code!
            self.assertAlmostEqual(cs[el][orb] * occ,
                                   value, delta=(value * 0.01))
