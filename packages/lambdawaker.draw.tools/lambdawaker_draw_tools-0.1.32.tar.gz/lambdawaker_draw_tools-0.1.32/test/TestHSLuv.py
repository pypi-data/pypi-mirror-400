import unittest

from lambdawaker.draw.color.HSLuvColor import HSLuvColor


class TestHSLuv(unittest.TestCase):
    def test_saturation_clamping(self):
        # Range limited to 20-80
        color = HSLuvColor(0, 50, 50, s_range=(20, 80))

        nc = color + "40S"
        self.assertEqual(nc.saturation, 80, "Should clamp at max range 80")

        nc = color + "-100S"
        self.assertEqual(nc.saturation, 20, "Should clamp at min range 20")

    def test_lightness_clamping(self):
        color = HSLuvColor(0, 50, 90, l_range=(0, 100))
        color + "20L"
        self.assertEqual(color.lightness, 100, "Should not exceed 100")

    def test_hue_simple_wrap(self):
        # Default full circle 0-360
        color = HSLuvColor(350, 50, 50)
        nc = color = color + "20H"
        self.assertEqual(nc.hue, 10, "350 + 20 should wrap to 10")

        nc = color + "-20H"
        self.assertEqual(nc.hue, 350, "10 - 20 should wrap to 350")

    def test_hue_sector_crossing_zero(self):
        # Range: 340 to 20 (The 40-degree "Red" slice)
        color = HSLuvColor(350, 50, 50, h_range=(340, 20))

        nc = color + "10H"
        self.assertEqual(nc.hue, 0)

        nc = color + "40H"
        self.assertEqual(nc.hue, 20, "Should snap to nearest boundary (20) when exiting sector")

        nc = color - "40H"
        print(nc.hue)
        self.assertEqual(340, nc.hue, "Should snap to nearest boundary (20) when exiting sector")

    def test_hue_sector_wide(self):
        # Range: 10 to 340 (Everything EXCEPT the 30-degree gap at 0)
        color = HSLuvColor(180, 50, 50, h_range=(10, 340))

        nc = color + "150H"  # 330 (Valid)
        self.assertEqual(nc.hue, 330)

        nc = color + "20H"  # 350 (Invalid, inside the 10-340 gap)
        # 350 is closer to 340 than to 10.
        self.assertEqual(nc.hue, 340)

    def test_string_parsing(self):
        color = HSLuvColor(100, 50, 50)
        with self.assertRaises(ValueError):
            color + "50X"  # Invalid suffix
        with self.assertRaises(ValueError):
            color + "H50"  # Invalid format

    def test_to_rgb(self):
        color = HSLuvColor(100, 50, 50)
        print(color.to_rgba())
        self.assertEqual((112, 123, 81), color.to_rgba())

    def test_slicing(self):
        tuple = HSLuvColor(100, 50, 50)[:4]
        print(tuple)

if __name__ == '__main__':
    unittest.main()
