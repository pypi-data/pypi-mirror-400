import unittest
from colorswan import OkColor

class TestOkColor(unittest.TestCase):
    def setUp(self):
        self.converter = OkColor()

    def test_srgb_white_conversion(self):
        # Default behavior: returns Oklab object directly
        result = self.converter.convert("#FFFFFF")
        
        self.assertAlmostEqual(result.L, 1.0, places=3)
        self.assertAlmostEqual(result.a, 0.0, places=3)
        self.assertAlmostEqual(result.b, 0.0, places=3)

    def test_srgb_black_conversion(self):
        # Default behavior: returns Oklab object directly
        result = self.converter.convert("#000000")
        
        self.assertAlmostEqual(result.L, 0.0, places=3)
        self.assertAlmostEqual(result.a, 0.0, places=3)
        self.assertAlmostEqual(result.b, 0.0, places=3)

    def test_red_conversion_oklch(self):
        # Requesting OKLCH explicitly
        result = self.converter.convert("#FF0000", return_type="oklch")
        
        # Expected approx: L=0.62796, C=0.25768, h=29.2338
        self.assertAlmostEqual(result.L, 0.62796, places=2)
        self.assertAlmostEqual(result.C, 0.25768, places=2)
        self.assertAlmostEqual(result.h, 29.23, places=2)

    def test_tuple_input_all_return(self):
        # Requesting "all" returns dictionary
        result = self.converter.convert((255, 255, 255), return_type="all")
        self.assertAlmostEqual(result['oklab'].L, 1.0, places=3)
        self.assertAlmostEqual(result['oklch'].L, 1.0, places=3)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.converter.convert("invalid")
