import unittest

from lambdawaker.draw.color.utils import clamp_hue, is_inside


class TestClampHue(unittest.TestCase):
    def test_inside_simple_range(self):
        # Value is already inside [10, 50]
        self.assertEqual(clamp_hue(30, (10, 50)), 30)
        # Boundary cases
        self.assertEqual(clamp_hue(10, (10, 50)), 10)
        self.assertEqual(clamp_hue(50, (10, 50)), 50)

    def test_outside_simple_range(self):
        # Close to min (10) -> should snap to 10
        self.assertEqual(clamp_hue(5, (10, 50)), 10)
        # Close to max (50) -> should snap to 50
        self.assertEqual(clamp_hue(60, (10, 50)), 50)
        # Far away, but closer to max
        self.assertEqual(clamp_hue(200, (10, 50)), 50)

    def test_wrap_around_range(self):
        # Range is [350, 20], crosses 0
        self.assertTrue(is_inside(355, (350, 20)))
        self.assertEqual(clamp_hue(355, (350, 20)), 355)
        self.assertEqual(clamp_hue(10, (350, 20)), 10)

        self.assertEqual(clamp_hue(340, (350, 20)), 350)

    def test_wrap_around_clamping(self):
        # Range [350, 20]. Input 340 is outside, closer to 350
        self.assertEqual(clamp_hue(340, (350, 20)), 350)
        # Input 30 is outside, closer to 20
        self.assertEqual(clamp_hue(30, (350, 20)), 20)

    def test_large_inputs(self):
        # Test modulo logic (750 % 360 = 30)
        self.assertEqual(clamp_hue(750, (10, 50)), 30)
        # Negative input (-10 % 360 = 350)
        self.assertEqual(clamp_hue(-10, (340, 20)), 350)

    def test_full_circle(self):
        # Range (0, 360) should effectively not clamp
        self.assertEqual(clamp_hue(180, (0, 360)), 180)

    def test_outside_arc(self):
        self.assertEqual(clamp_hue(310, (340, 20)), 340)


if __name__ == '__main__':
    unittest.main()
