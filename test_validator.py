"""Unit tests for FL Studio theme validator, guardrails, and palette extraction."""

import unittest
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

from validator import calculate_luminance, contrast_ratio, validate_theme_dict
from generator import extract_palette_from_image, FLThemeBuilder


class TestThemeValidator(unittest.TestCase):

    def test_luminance_and_contrast(self):
        # Pure black and pure white
        self.assertAlmostEqual(calculate_luminance("#000000"), 0.0, places=3)
        self.assertAlmostEqual(calculate_luminance("#FFFFFF"), 1.0, places=3)
        # Black vs White is 21:1
        self.assertAlmostEqual(contrast_ratio("#000000", "#FFFFFF"), 21.0, places=1)
        # Same color is 1:1
        self.assertAlmostEqual(contrast_ratio("#FF0000", "#FF0000"), 1.0, places=1)

    def test_luminance_crushing_guardrail(self):
        # Lightness lower than -100 triggers a warning
        issues = validate_theme_dict({"lightness": -150})
        self.assertTrue(any(i.category == "Luminance" and i.level == "WARNING" for i in issues))

        # Safe lightness does not trigger a warning
        safe_issues = validate_theme_dict({"lightness": -65})
        self.assertFalse(any(i.category == "Luminance" for i in safe_issues))

    def test_step_contrast_guardrail(self):
        # Identical step buttons trigger contrast warning
        issues = validate_theme_dict({"step_even": "#202020", "step_odd": "#202020"})
        self.assertTrue(any(i.category == "Step Contrast" for i in issues))

        # High contrast steps pass cleanly
        safe_issues = validate_theme_dict({"step_even": "#353545", "step_odd": "#181820"})
        self.assertFalse(any(i.category == "Step Contrast" for i in safe_issues))

    def test_meter_clipping_guardrail(self):
        # Meter4 and Meter5 identical triggers clipping warning
        issues = validate_theme_dict({"meters": ["#1", "#2", "#3", "#4", "#FF0000", "#FF0000"]})
        self.assertTrue(any(i.category == "Meter Clipping" for i in issues))

    def test_image_palette_extractor(self):
        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "artwork.png"
            im = Image.new("RGB", (60, 60), "#0A0E17")
            d = ImageDraw.Draw(im)
            d.rectangle([10, 10, 50, 50], fill="#00F0FF")
            im.save(img_path)

            palette = extract_palette_from_image(img_path)
            self.assertIn("selected", palette)
            self.assertIn("back_color", palette)
            self.assertIn("text_color", palette)
            self.assertTrue(palette["selected"].startswith("#"))


if __name__ == "__main__":
    unittest.main()
