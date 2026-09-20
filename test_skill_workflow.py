"""End-to-end simulation tests for AI agent prompt-to-script workflow.

Verifies that deterministic scripts reliably handle diverse user prompt scenarios:
1. Shipped preset variations
2. Freeform custom palettes
3. Inline JSON string configs
4. Custom dynamic HTML wallpaper generation
5. Roundtrip inspector verification
"""

import unittest
import json
import tempfile
from pathlib import Path

from generator import FLThemeBuilder, get_builtin_presets, hex_to_fl_color, fl_color_to_hex
from wallpapers import get_html_for_preset, generate_custom_dynamic_html
from inspector import parse_fltheme


class TestSkillPromptWorkflow(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_prompt_scenario_a_preset_variation(self):
        """Simulates: 'I want Dracula with toxic slime green accents and dynamic fog'."""
        presets = get_builtin_presets()
        self.assertIn("dracula", presets)

        builder = FLThemeBuilder("Dracula Slime")
        builder.apply_palette(presets["dracula"])
        builder.selected = "#39FF14"  # Slime green override
        builder.contrast = 40

        theme_file = self.base_path / "Dracula Slime.flstheme"
        builder.save(theme_file)

        # Parse back and verify
        parsed = parse_fltheme(theme_file)
        self.assertEqual(parsed["colors"]["Selected"]["hex"], "#39FF14")
        self.assertEqual(parsed["controls"]["Contrast"], 40)
        # Inherited from Dracula base
        self.assertEqual(parsed["colors"]["Highlight"]["hex"], "#FF79C6")

    def test_prompt_scenario_b_freeform_custom_theme(self):
        """Simulates: 'Create Autumn Sunset with orange #FF7700, Hue 25, Sat 80'."""
        builder = FLThemeBuilder("Autumn Sunset")
        builder.selected = "#FF7700"
        builder.highlight = "#FFA07A"
        builder.hue = 25
        builder.saturation = 80
        builder.lightness = -65
        builder.contrast = 32
        builder.step_even = "#2A201A"
        builder.step_odd = "#18120E"

        theme_file = self.base_path / "Autumn Sunset.flstheme"
        builder.save(theme_file)

        parsed = parse_fltheme(theme_file)
        self.assertEqual(parsed["colors"]["Selected"]["hex"], "#FF7700")
        self.assertEqual(parsed["controls"]["Hue"], 25)
        self.assertEqual(parsed["controls"]["Saturation"], 80)
        self.assertEqual(parsed["colors"]["StepEven"]["hex"], "#2A201A")

    def test_prompt_scenario_c_json_string_payload(self):
        """Simulates an AI agent passing a structured JSON payload directly."""
        json_payload = {
            "name": "Neon Genesis",
            "hue": 55,
            "saturation": 75,
            "selected": "#00FF66",
            "highlight": "#9900FF",
            "contrast": 35,
        }
        builder = FLThemeBuilder(json_payload["name"])
        builder.apply_palette(json_payload)

        fl_str = builder.to_fltheme_string()
        self.assertIn("Hue=55", fl_str)
        self.assertIn("Saturation=75", fl_str)
        self.assertIn(f"Selected={hex_to_fl_color('#00FF66')}", fl_str)

    def test_prompt_scenario_d_custom_dynamic_html(self):
        """Verifies custom dynamic HTML generation produces valid HTML with canvas."""
        html = generate_custom_dynamic_html("Solar Flare", "#FF9900", "#FFCC00", "#140A00")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<canvas id=\"canvas\"></canvas>", html)
        self.assertIn("Solar Flare &bull; FL Studio", html)
        self.assertIn("#FF9900", html)

    def test_all_builtin_presets_produce_valid_signed_integers(self):
        """Ensures every built-in preset conforms strictly to 32-bit signed limits."""
        presets = get_builtin_presets()
        for key, p in presets.items():
            builder = FLThemeBuilder(p["name"])
            builder.apply_palette(p)
            fl_text = builder.to_fltheme_string()
            for line in fl_text.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k in ("Selected", "Highlight", "Mute", "Option", "StepEven", "StepOdd",
                             "TextColor", "BackColor", "PRGridback", "PLGridback", "EEGridback") or k.startswith(("Meter", "NoteColor")):
                        val = int(v)
                        self.assertTrue(-2147483648 <= val <= 2147483647, f"{k}={val} out of signed 32-bit bounds in {key}")


if __name__ == "__main__":
    unittest.main()
