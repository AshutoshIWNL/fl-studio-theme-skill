"""Unit tests for FL Studio theme color math and generator."""

import unittest
from generator import hex_to_fl_color, fl_color_to_hex, FLThemeBuilder


class TestFLStudioThemeMath(unittest.TestCase):

    def test_pure_colors(self):
        # Pure black (alpha 255)
        self.assertEqual(hex_to_fl_color("#000000"), -16777216)
        self.assertEqual(fl_color_to_hex(-16777216), ("#000000", 255))

        # Pure white (alpha 255)
        self.assertEqual(hex_to_fl_color("#FFFFFF"), -1)
        self.assertEqual(fl_color_to_hex(-1), ("#FFFFFF", 255))

        # White with alpha 0 (grid background format)
        self.assertEqual(hex_to_fl_color("#FFFFFF", alpha=0), 16777215)
        self.assertEqual(fl_color_to_hex(16777215), ("#FFFFFF", 0))

    def test_stock_fl_colors(self):
        # Light Cherry stock Selected color: #FF5493 -> -43885
        self.assertEqual(hex_to_fl_color("#FF5493"), -43885)
        self.assertEqual(fl_color_to_hex(-43885), ("#FF5493", 255))

        # Dark theme default Selected color: #A8E44A with alpha 0 -> 11068490
        self.assertEqual(hex_to_fl_color("#A8E44A", alpha=0), 11068490)
        self.assertEqual(fl_color_to_hex(11068490), ("#A8E44A", 0))

    def test_theme_builder_output(self):
        builder = FLThemeBuilder("Test Theme")
        fl_content = builder.to_fltheme_string()
        self.assertIn("Hue=0", fl_content)
        self.assertIn("Selected=", fl_content)
        self.assertIn("Meter0=", fl_content)
        self.assertIn("NoteColor15=", fl_content)
        self.assertIn("PRGridback=", fl_content)


if __name__ == "__main__":
    unittest.main()
