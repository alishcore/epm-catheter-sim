from math import hypot, pi, sin
import unittest

from catheter import centerline, equilibrium_angle


class EquilibriumTests(unittest.TestCase):
    def test_no_actuation_leaves_tip_straight(self):
        self.assertEqual(equilibrium_angle(0.03, 1e-6, 0, 0.025, pi / 2), 0)
        self.assertEqual(equilibrium_angle(0.03, 1e-6, 0.002, 0, pi / 2), 0)
        self.assertEqual(equilibrium_angle(0.03, 1e-6, 0.002, 0.025, 0), 0)

    def test_magnetic_torque_balances_elastic_torque(self):
        for field_angle in (-3.0, -1.4, 1.4, 3.0):
            with self.subTest(field_angle=field_angle):
                angle = equilibrium_angle(0.03, 1e-6, 0.002, 0.025, field_angle)
                self.assertLess(abs(angle), abs(field_angle))
                self.assertAlmostEqual(angle, 1.5 * sin(field_angle - angle), places=12)
                self.assertGreater(angle * field_angle, 0)

    def test_more_moment_increases_bend(self):
        off = equilibrium_angle(0.03, 1e-6, 0.0002, 0.025, pi / 2)
        on = equilibrium_angle(0.03, 1e-6, 0.002, 0.025, pi / 2)
        self.assertGreater(on, off)
        self.assertGreater(off, 0)

    def test_rejects_invalid_model_parameters(self):
        with self.assertRaises(ValueError):
            equilibrium_angle(0.03, 0, 0.002, 0.025, pi / 2)
        with self.assertRaises(ValueError):
            equilibrium_angle(0.03, 1e-6, 0.002, 0.025, pi)
        with self.assertRaises(ValueError):
            equilibrium_angle(0.03, 1e-6, 0.002, float("nan"), pi / 2)


class CenterlineTests(unittest.TestCase):
    def test_straight_and_nearly_straight_tip(self):
        self.assertEqual(centerline(0.03, 0, 3), [(0, 0), (0.015, 0), (0.03, 0)])
        x, y = centerline(0.03, 1e-12)[-1]
        self.assertAlmostEqual(x, 0.03)
        self.assertGreater(y, 0)

    def test_quarter_circle(self):
        length = 0.03
        points = centerline(length, pi / 2, points=1001)
        x, y = points[-1]
        radius = length / (pi / 2)
        self.assertAlmostEqual(x, radius)
        self.assertAlmostEqual(y, radius)
        chord_sum = sum(hypot(x2 - x1, y2 - y1)
                        for (x1, y1), (x2, y2) in zip(points, points[1:]))
        self.assertAlmostEqual(chord_sum, length)
