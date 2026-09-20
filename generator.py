"""FL Studio Theme Generator (.flstheme)

Encodes and decodes FL Studio theme files, supporting custom color palettes,
contrast checking, preset loading, and direct installation into FL Studio.
"""

from __future__ import annotations
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


# Default FL Studio user themes path on Windows
DEFAULT_USER_THEMES_PATH = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "Image-Line" / "FL Studio" / "Settings" / "Themes"


def hex_to_fl_color(hex_str: str, alpha: int = 255) -> int:
    """
    Converts a '#RRGGBB' or 'RRGGBB' hex color string to FL Studio's 
    32-bit signed integer format (0xAARRGGBB two's complement).
    """
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    if len(hex_clean) != 6:
        raise ValueError(f"Invalid hex color string: '{hex_str}' (expected 3 or 6 hex digits)")

    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)

    unsigned = (alpha << 24) | (r << 16) | (g << 8) | b
    # Convert to 32-bit signed integer
    return unsigned if unsigned < 0x80000000 else unsigned - 0x100000000


def fl_color_to_hex(val: int) -> Tuple[str, int]:
    """
    Converts an FL Studio 32-bit signed integer back into (#RRGGBB, alpha).
    """
    unsigned = val & 0xFFFFFFFF
    alpha = (unsigned >> 24) & 0xFF
    r = (unsigned >> 16) & 0xFF
    g = (unsigned >> 8) & 0xFF
    b = unsigned & 0xFF
    return f"#{r:02X}{g:02X}{b:02X}", alpha


def calculate_luminance(hex_str: str) -> float:
    """Calculates relative luminance of an sRGB color (0.0 to 1.0)."""
    hex_clean = hex_str.strip().lstrip("#")
    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    def adjust(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculates WCAG contrast ratio between two hex colors."""
    lum1 = calculate_luminance(hex1)
    lum2 = calculate_luminance(hex2)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)


from validator import validate_theme_dict, print_validation_report, contrast_ratio, calculate_luminance
from wallpapers import (
    get_html_for_preset,
    generate_tokyo_night_html,
    generate_cyberpunk_html,
    generate_synthwave_html,
    generate_catppuccin_html,
    generate_cyber_blossom_html,
    generate_custom_dynamic_html,
    generate_wallpaper_txt,
)


def extract_palette_from_image(image_path: Path) -> Dict[str, Any]:
    """
    Extracts a balanced, usable FL Studio theme palette from any image or album artwork.
    Uses PIL color quantization and HSV sorting for contrast and harmony.
    """
    import colorsys
    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    img = img.resize((150, 150))
    q = img.quantize(colors=8)
    rgb_img = q.convert("RGB")
    color_entries = rgb_img.getcolors(maxcolors=256)
    if not color_entries:
        raise ValueError(f"Could not extract colors from image: {image_path}")

    colors = [c[1] for c in color_entries]
    hsv_colors = []
    for rgb in colors:
        h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        hex_code = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
        hsv_colors.append((hex_code, h, s, v))

    # Sort by brightness (v)
    sorted_by_v = sorted(hsv_colors, key=lambda x: x[3])
    # Sort by saturation (s)
    sorted_by_s = sorted(hsv_colors, key=lambda x: x[2], reverse=True)

    back_color = sorted_by_v[0][0]
    step_odd = sorted_by_v[1][0] if len(sorted_by_v) > 1 else "#141419"
    step_even = sorted_by_v[2][0] if len(sorted_by_v) > 2 else "#24242F"
    selected = sorted_by_s[0][0]
    highlight = sorted_by_s[1][0] if len(sorted_by_s) > 1 else selected
    text_color = sorted_by_v[-1][0]

    return {
        "back_color": back_color,
        "pr_grid_back": back_color,
        "pl_grid_back": back_color,
        "step_odd": step_odd,
        "step_even": step_even,
        "selected": selected,
        "highlight": highlight,
        "text_color": text_color,
        "option": highlight,
        "mute": "#FF5252",
    }


class FLThemeBuilder:
    """Builds a complete, valid .flstheme configuration dictionary with wallpaper support."""

    def __init__(self, name: str = "Custom Theme"):
        self.name = name
        self.preset_key: Optional[str] = None
        # Base Master Controls (FL Studio UI panel tinting engine)
        self.hue: int = 0
        self.saturation: int = -80  # Clean, modern slate UI default
        self.lightness: int = -70   # Balanced modern dark mode
        self.contrast: int = 30
        self.light_mode: int = 1    # 1 is standard in 98%+ of FL Studio themes
        self.text_brightness: int = 255
        self.override_clips: int = 1

        # Core Accent Colors (Hex)
        self.text_color: str = "#E0E0E0"
        self.selected: str = "#7AA2F7"
        self.highlight: str = "#BB9AF7"
        self.mute: str = "#F7768E"
        self.option: str = "#7DCFFF"
        self.step_even: str = "#2B2D3A"
        self.step_odd: str = "#1E1F29"

        # Mixer Meters (6 levels from bottom to peak)
        self.meters: List[str] = [
            "#00F0FF",  # Meter0: Floor
            "#00E5A3",  # Meter1: Low-Mid
            "#A7E136",  # Meter2: Mid (~ -12dB)
            "#FFE600",  # Meter3: Upper-Mid (~ -6dB)
            "#FF7700",  # Meter4: Near 0dB
            "#FF003C",  # Meter5: Peak / Clip (>0dB)
        ]

        # Waveform colors (6 stages)
        self.wave_colors: List[str] = [
            "#00F0FF",
            "#2A9D8F",
            "#E76F51",
            "#F4A261",
            "#E63946",
            "#D62828",
        ]
        self.wave_spacings: List[float] = [0.0, 0.15, 0.30, 0.48, 0.88, 1.0]

        # 16 Piano Roll Note Colors (channels 1-16)
        self.note_colors: List[str] = [
            "#00F0FF", "#3A86FF", "#8338EC", "#FF006E",
            "#FB5607", "#FFBE0B", "#06D6A0", "#118AB2",
            "#073B4C", "#E63946", "#F1FAEE", "#A8DADC",
            "#457B9D", "#1D3557", "#2A9D8F", "#E76F51"
        ]

        # Grid Backgrounds (Custom grids enabled so PR and PL adopt theme colors)
        self.pr_grid_back: str = "#1A1B26"
        self.pr_grid_custom: int = 1
        self.pr_grid_contrast: int = 120

        self.pl_grid_back: str = "#1A1B26"
        self.pl_grid_custom: int = 1
        self.pl_grid_contrast: int = 120

        self.ee_grid_back: str = "#1A1B26"
        self.ee_grid_custom: int = 0
        self.ee_grid_contrast: int = 100

        # Background Canvas & Wallpaper options
        self.back_mode: int = 2
        self.back_pic_filename: str = "FL STUDIO.png"
        self.back_html_filename: str = "Default.txt"
        self.back_color: str = "#1A1B26"

        # Advanced Wallpaper Assets
        self.dynamic_html_content: Optional[str] = None
        self.bg_image_path: Optional[Path] = None
        self.use_custom_txt: bool = False

    def apply_palette(self, palette: Dict[str, Any]) -> "FLThemeBuilder":
        """Applies a theme dictionary with semantic color names."""
        if "name" in palette:
            self.name = palette["name"]
        if "light_mode" in palette:
            self.light_mode = 1 if palette["light_mode"] else 0
        if "lightness" in palette:
            self.lightness = int(palette["lightness"])
        if "contrast" in palette:
            self.contrast = int(palette["contrast"])
        if "saturation" in palette:
            self.saturation = int(palette["saturation"])
        if "hue" in palette:
            self.hue = int(palette["hue"])
        if "text_brightness" in palette:
            self.text_brightness = int(palette["text_brightness"])
        if "override_clips" in palette:
            self.override_clips = 1 if palette["override_clips"] else 0

        # Accents
        if "text_color" in palette:
            self.text_color = palette["text_color"]
        if "selected" in palette:
            self.selected = palette["selected"]
        if "highlight" in palette:
            self.highlight = palette["highlight"]
        if "mute" in palette:
            self.mute = palette["mute"]
        if "option" in palette:
            self.option = palette["option"]
        if "step_even" in palette:
            self.step_even = palette["step_even"]
        if "step_odd" in palette:
            self.step_odd = palette["step_odd"]
        if "back_color" in palette:
            self.back_color = palette["back_color"]

        # Lists
        if "meters" in palette and len(palette["meters"]) == 6:
            self.meters = list(palette["meters"])
        if "wave_colors" in palette and len(palette["wave_colors"]) == 6:
            self.wave_colors = list(palette["wave_colors"])
        if "note_colors" in palette and len(palette["note_colors"]) == 16:
            self.note_colors = list(palette["note_colors"])

        # Grid
        if "pr_grid_back" in palette:
            self.pr_grid_back = palette["pr_grid_back"]
            self.pr_grid_custom = 1
        if "pl_grid_back" in palette:
            self.pl_grid_back = palette["pl_grid_back"]
            self.pl_grid_custom = 1
        if "ee_grid_back" in palette:
            self.ee_grid_back = palette["ee_grid_back"]
            self.ee_grid_custom = 1

        if "pl_grid_contrast" in palette:
            self.pl_grid_contrast = int(palette["pl_grid_contrast"])
        if "pr_grid_contrast" in palette:
            self.pr_grid_contrast = int(palette["pr_grid_contrast"])
        if "ee_grid_contrast" in palette:
            self.ee_grid_contrast = int(palette["ee_grid_contrast"])

        # Wallpaper
        if "dynamic_html" in palette:
            self.dynamic_html_content = palette["dynamic_html"]
        elif "dynamic_html_content" in palette:
            self.dynamic_html_content = palette["dynamic_html_content"]
        if "back_pic_filename" in palette:
            self.back_pic_filename = palette["back_pic_filename"]
        if "back_html_filename" in palette:
            self.back_html_filename = palette["back_html_filename"]
        if "back_mode" in palette:
            self.back_mode = int(palette["back_mode"])

        return self

    def to_fltheme_string(self) -> str:
        """Generates the exact .flstheme file content."""
        lines = [
            f"Hue={self.hue}",
            f"Saturation={self.saturation}",
            f"Lightness={self.lightness}",
            f"Contrast={self.contrast}",
            f"Text={self.text_brightness}",
            f"Selected={hex_to_fl_color(self.selected)}",
            f"Highlight={hex_to_fl_color(self.highlight)}",
            f"Mute={hex_to_fl_color(self.mute)}",
            f"Option={hex_to_fl_color(self.option)}",
            f"StepEven={hex_to_fl_color(self.step_even)}",
            f"StepOdd={hex_to_fl_color(self.step_odd)}",
            f"Lightmode={self.light_mode}",
            f"OverrideClips={self.override_clips}",
            f"TextColor={hex_to_fl_color(self.text_color)}",
        ]

        # Peak meters
        for i, meter_color in enumerate(self.meters):
            lines.append(f"Meter{i}={hex_to_fl_color(meter_color)}")

        # Waveforms (if defined)
        if self.wave_colors:
            for i, (wave_clr, wave_spc) in enumerate(zip(self.wave_colors, self.wave_spacings)):
                lines.append(f"WaveClr{i}={hex_to_fl_color(wave_clr)}")
                lines.append(f"WaveSpc{i}={wave_spc}")

        # Note colors (16 MIDI channels)
        for i, note_color in enumerate(self.note_colors):
            lines.append(f"NoteColor{i}={hex_to_fl_color(note_color)}")

        # Grids
        lines.extend([
            f"PRGridback={hex_to_fl_color(self.pr_grid_back, alpha=0)}",
            f"PRGridCustom={self.pr_grid_custom}",
            f"PRGridContrast={self.pr_grid_contrast}",
            f"PLGridback={hex_to_fl_color(self.pl_grid_back, alpha=0)}",
            f"PLGridCustom={self.pl_grid_custom}",
            f"PLGridContrast={self.pl_grid_contrast}",
            f"EEGridback={hex_to_fl_color(self.ee_grid_back, alpha=0)}",
            f"EEGridCustom={self.ee_grid_custom}",
            f"EEGridContrast={self.ee_grid_contrast}",
        ])

        # Wallpaper
        lines.extend([
            f"BackMode={self.back_mode}",
            f"BackPicFilename={self.back_pic_filename}",
            f"BackHTMLFileName={self.back_html_filename}",
            f"BackColor={hex_to_fl_color(self.back_color)}",
        ])

        return "\n".join(lines) + "\n"

    def save(self, target_path: Path) -> Path:
        """Saves the theme to the given file path."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.to_fltheme_string()
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return target_path

    def generate_thumbnail(self, out_path: Path) -> Path:
        """Generates a 318x180 thumbnail preview card for FL Studio's preset browser."""
        try:
            from PIL import Image, ImageDraw
            w, h = 318, 180
            im = Image.new("RGB", (w, h), self.back_color)
            draw = ImageDraw.Draw(im)

            # Header bar
            draw.rectangle([0, 0, w, 28], fill="#1E1E26")
            draw.line([0, 28, w, 28], fill="#333340", width=1)

            # Left browser mock
            draw.rectangle([0, 29, 65, h], fill="#14141A")
            draw.line([65, 29, 65, h], fill="#333340", width=1)

            # Playlist grid lanes
            for x in range(95, w, 28):
                draw.line([x, 29, x, h], fill="#252530", width=1)
            for y in range(50, h, 24):
                draw.line([66, y, w, y], fill="#252530", width=1)

            # Vibrant pattern clips
            draw.rounded_rectangle([80, 42, 160, 62], radius=4, fill=self.selected)
            draw.rounded_rectangle([170, 66, 250, 86], radius=4, fill=self.highlight)
            draw.rounded_rectangle([100, 90, 190, 110], radius=4, fill=self.selected)
            draw.rounded_rectangle([140, 114, 270, 134], radius=4, fill=self.option)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            im.save(out_path, quality=95)
            return out_path
        except Exception:
            return out_path

    def generate_wallpaper_image(self, out_path: Path) -> Path:
        """Generates a 1920x1080 high-res ambient companion wallpaper matching the theme."""
        try:
            from PIL import Image, ImageDraw
            w, h = 1920, 1080
            im = Image.new("RGB", (w, h), self.back_color)
            draw = ImageDraw.Draw(im)

            # Palette-specific ambient artwork
            accent_rgb = tuple(int(self.selected.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            sec_rgb = tuple(int(self.highlight.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

            # Ambient soft central glow
            for r in range(450, 0, -10):
                factor = (1.0 - r / 450) ** 2
                glow_r = int(accent_rgb[0] * factor * 0.18)
                glow_g = int(accent_rgb[1] * factor * 0.18)
                glow_b = int(accent_rgb[2] * factor * 0.18)
                draw.ellipse([w // 2 - r * 2, h // 2 - r, w // 2 + r * 2, h // 2 + r], fill=(glow_r, glow_g, glow_b))

            # Elegant typography watermark in bottom right
            draw.text((w - 360, h - 55), f"{self.name.upper()} // FL STUDIO", fill=self.selected)

            out_path.parent.mkdir(parents=True, exist_ok=True)
            im.save(out_path, quality=95)
            return out_path
        except Exception:
            return out_path

    def install(self, custom_themes_dir: Optional[Path] = None, bundle_folder: bool = True) -> Path:
        """
        Installs the theme directly into FL Studio's Themes folder.
        Supports rich folder bundling for dynamic HTML, custom images, and wallpaper configs.
        """
        import shutil
        themes_dir = custom_themes_dir or DEFAULT_USER_THEMES_PATH
        theme_folder = themes_dir / self.name if bundle_folder else themes_dir
        theme_folder.mkdir(parents=True, exist_ok=True)

        # 1. Handle Automatic Companion Wallpaper Image (Loads automatically upon selecting theme!)
        wallpaper_filename = f"{self.name} - Wallpaper.png"
        if self.bg_image_path and Path(self.bg_image_path).exists():
            src_img = Path(self.bg_image_path)
            wallpaper_filename = f"{self.name} - Wallpaper{src_img.suffix}"
            shutil.copyfile(src_img, theme_folder / wallpaper_filename)
            shutil.copyfile(src_img, themes_dir / wallpaper_filename)
        else:
            self.generate_wallpaper_image(theme_folder / wallpaper_filename)
            self.generate_wallpaper_image(themes_dir / wallpaper_filename)

        self.back_pic_filename = wallpaper_filename
        self.back_mode = 2

        # 2. Handle Dynamic HTML Wallpaper (Bundled for View -> Background)
        if self.dynamic_html_content:
            html_target = theme_folder / "wallpaper.html"
            with open(html_target, "w", encoding="utf-8") as f:
                f.write(self.dynamic_html_content)
            # Also copy as <ThemeName>.html
            with open(theme_folder / f"{self.name}.html", "w", encoding="utf-8") as f:
                f.write(self.dynamic_html_content)

        # 3. Handle Custom Wallpaper Text & Logo Gradient
        if self.use_custom_txt:
            txt_content = generate_wallpaper_txt(self.back_color, "#0E0E14", self.selected)
            txt_target = theme_folder / "wallpaper.txt"
            with open(txt_target, "w", encoding="utf-8") as f:
                f.write(txt_content)
            self.back_html_filename = "wallpaper.txt"
        else:
            self.back_html_filename = "Default.txt"

        # Save main theme file in folder
        target = theme_folder / f"{self.name}.flstheme"
        self.save(target)

        # Generate companion thumbnail inside folder
        thumb_target = theme_folder / f"thm{self.name}.jpg"
        self.generate_thumbnail(thumb_target)

        # If in a subfolder, also place flat entry in root Themes/ for maximum FL Studio compatibility
        if bundle_folder and theme_folder != themes_dir:
            flat_target = themes_dir / f"{self.name}.flstheme"
            self.save(flat_target)
            flat_thumb = themes_dir / f"thm{self.name}.jpg"
            self.generate_thumbnail(flat_thumb)

        return target


def get_builtin_presets() -> Dict[str, Dict[str, Any]]:
    """Returns a collection of high-quality handcrafted presets with rich panel tints and wallpapers."""
    nurture_preset = {
        "name": "Nurture",
        "light_mode": 1,
        "hue": 55,                  # Organic lush meadow / forest green ambiance (positive Hue = green in FL Studio)
        "saturation": 75,           # Balanced vibrant foliage panel tint
        "lightness": -65,           # Calm natural dark forest tone
        "contrast": 30,
        "text_color": "#E8F5E9",    # Soft morning dew white
        "selected": "#4EFA94",      # Vibrant spring sprout / mint
        "highlight": "#A8FF78",     # Fresh leaf green
        "mute": "#FF6B6B",          # Coral flower red
        "option": "#78E08F",        # Emerald sage
        "step_even": "#1E3322",     # Deep forest green
        "step_odd": "#122115",      # Dark moss
        "pr_grid_back": "#0F1A12",
        "pl_grid_back": "#0F1A12",
        "ee_grid_back": "#0F1A12",
        "back_pic_filename": "Nurture - Wallpaper.png",
        "back_html_filename": "Default.txt",
        "back_color": "#0D1510",
        "meters": ["#4EFA94", "#78E08F", "#A8FF78", "#F6E58D", "#FFBE76", "#FF6B6B"],
        "wave_colors": ["#4EFA94", "#78E08F", "#A8FF78", "#F6E58D", "#FFBE76", "#FF6B6B"],
        "note_colors": [
            "#4EFA94", "#A8FF78", "#78E08F", "#2ED573",
            "#10AC84", "#26DE81", "#B8E994", "#7BED9F",
            "#ECCC68", "#FFA502", "#1DD1A1", "#10E79D",
            "#55E6C1", "#82CCDD", "#F8EFBA", "#FF6B6B",
        ],
    }
    return {
        "nurture": nurture_preset,
        "nature": nurture_preset,
        "tokyo-night": {
            "name": "Tokyo Night",
            "light_mode": 1,
            "hue": -25,                 # Subtle cool blue/indigo panel ambiance
            "saturation": -80,          # Clean, modern dark slate UI (no muddy green)
            "lightness": -70,           # Balanced contrast
            "contrast": 30,
            "text_color": "#C0CAF5",
            "selected": "#7AA2F7",      # Vibrant Tokyo Blue
            "highlight": "#BB9AF7",     # Soft Purple
            "mute": "#F7768E",          # Tokyo Pink / Red
            "option": "#7DCFFF",        # Cyan
            "step_even": "#24283B",
            "step_odd": "#1A1B26",
            "pr_grid_back": "#1A1B26",
            "pl_grid_back": "#1A1B26",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#1A1B26",
            "meters": ["#7AA2F7", "#7DCFFF", "#9ECE6A", "#E0AF68", "#FF9E64", "#F7768E"],
            "wave_colors": ["#7AA2F7", "#7DCFFF", "#BB9AF7", "#E0AF68", "#FF9E64", "#F7768E"],
        },
        "cyberpunk": {
            "name": "Cyberpunk 2077",
            "light_mode": 1,
            "hue": 0,
            "saturation": -180,         # Matte carbon-black panels for maximum neon contrast
            "lightness": -65,
            "contrast": 38,
            "text_color": "#FDFDFD",
            "selected": "#FCEE0A",      # Cyber Yellow
            "highlight": "#00F0FF",     # Electric Cyan
            "mute": "#FF003C",          # Neon Crimson
            "option": "#00F0FF",
            "step_even": "#2B281E",
            "step_odd": "#141419",
            "pr_grid_back": "#141419",
            "pl_grid_back": "#141419",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#101014",
            "meters": ["#00F0FF", "#2DE2E6", "#7122FA", "#FCEE0A", "#FF6C00", "#FF003C"],
            "wave_colors": ["#00F0FF", "#2DE2E6", "#7122FA", "#FCEE0A", "#FF6C00", "#FF003C"],
        },
        "catppuccin-mocha": {
            "name": "Catppuccin Mocha",
            "light_mode": 1,
            "hue": 0,
            "saturation": -120,         # Soft pastel charcoal
            "lightness": -60,
            "contrast": 22,
            "text_color": "#CDD6F4",
            "selected": "#89B4FA",      # Mocha Blue
            "highlight": "#CBA6F7",     # Mauve
            "mute": "#F38BA8",          # Red
            "option": "#94E2D5",        # Teal
            "step_even": "#313244",
            "step_odd": "#1E1E2E",
            "pr_grid_back": "#1E1E2E",
            "pl_grid_back": "#1E1E2E",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#181825",
            "meters": ["#89DCEB", "#A6E3A1", "#F9E2AF", "#FAB387", "#EBA0AC", "#F38BA8"],
            "wave_colors": ["#89DCEB", "#A6E3A1", "#F9E2AF", "#FAB387", "#EBA0AC", "#F38BA8"],
        },
        "synthwave-84": {
            "name": "Synthwave 84",
            "light_mode": 1,
            "hue": -65,                 # Subtle neon purple tint
            "saturation": 90,
            "lightness": -55,
            "contrast": 32,
            "text_color": "#FFF7F6",
            "selected": "#FF7EDB",      # Neon Pink
            "highlight": "#36F9F6",     # Neon Cyan
            "mute": "#FE4450",
            "option": "#72F1B8",        # Neon Green
            "step_even": "#3D2B5E",
            "step_odd": "#241B35",
            "pr_grid_back": "#241B35",
            "pl_grid_back": "#241B35",
            "back_pic_filename": "ultravioletbg.png",
            "back_html_filename": "Default.txt",
            "back_color": "#1A1528",
            "meters": ["#36F9F6", "#72F1B8", "#FFE75C", "#FF8849", "#FF7EDB", "#FE4450"],
            "wave_colors": ["#36F9F6", "#72F1B8", "#FFE75C", "#FF8849", "#FF7EDB", "#FE4450"],
        },
        "dracula": {
            "name": "Dracula",
            "light_mode": 1,
            "hue": -100,                # Vampiric dark purple tint
            "saturation": 95,
            "lightness": -65,
            "contrast": 22,
            "text_color": "#F8F8F2",
            "selected": "#50FA7B",      # Dracula Neon Green
            "highlight": "#FF79C6",     # Dracula Pink
            "mute": "#FF5555",          # Dracula Red
            "option": "#8BE9FD",        # Dracula Cyan
            "step_even": "#44475A",
            "step_odd": "#282A36",
            "pr_grid_back": "#282A36",
            "pl_grid_back": "#282A36",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#282A36",
            "meters": ["#8BE9FD", "#50FA7B", "#F1FA8C", "#FFB86C", "#FF79C6", "#FF5555"],
            "wave_colors": ["#8BE9FD", "#50FA7B", "#F1FA8C", "#FFB86C", "#FF79C6", "#FF5555"],
        },
        "oled-crimson": {
            "name": "OLED Crimson",
            "light_mode": 1,
            "hue": 0,
            "saturation": 0,            # Pure monochrome base
            "lightness": -125,          # Ultra dark (readable buttons & panel outlines)
            "contrast": 45,
            "text_color": "#FFFFFF",
            "selected": "#FF1744",      # Blood Red
            "highlight": "#FF5252",
            "mute": "#D50000",
            "option": "#FF1744",
            "step_even": "#262626",
            "step_odd": "#121212",
            "pr_grid_back": "#121212",
            "pl_grid_back": "#121212",
            "back_pic_filename": "FL STUDIO dark.png",
            "back_html_filename": "Default.txt",
            "back_color": "#0A0A0A",
            "meters": ["#424242", "#757575", "#B71C1C", "#D50000", "#FF1744", "#FF5252"],
            "wave_colors": ["#424242", "#757575", "#B71C1C", "#D50000", "#FF1744", "#FF5252"],
        },
        "cyber-blossom": {
            "name": "Cyber Blossom",
            "light_mode": 1,
            "hue": 0,
            "saturation": -130,         # Matte dark charcoal panels
            "lightness": -65,           # Balanced modern dark mode
            "contrast": 35,
            "text_color": "#F5E6EB",    # Soft sakura white
            "selected": "#FF2A85",      # Electric Sakura Pink
            "highlight": "#FF70A6",     # Soft Blossom Pink
            "mute": "#70A1FF",          # Ice Blue
            "option": "#D980FA",        # Sakura Lilac
            "step_even": "#282025",     # Charcoal with soft rose undertone
            "step_odd": "#161114",      # Dark obsidian shadow
            "pr_grid_back": "#120E13",
            "pl_grid_back": "#120E13",
            "ee_grid_back": "#120E13",
            "back_pic_filename": "Cyber Blossom - Wallpaper.png",
            "back_html_filename": "Default.txt",
            "back_color": "#0E0B10",
            "meters": ["#70A1FF", "#D980FA", "#FF70A6", "#FF2A85", "#FF9F43", "#FF1744"],
            "wave_colors": ["#70A1FF", "#D980FA", "#FF70A6", "#FF2A85", "#FF9F43", "#FF1744"],
            "note_colors": [
                "#FF2A85", "#FF70A6", "#D980FA", "#FF5376",
                "#FF007F", "#9B59B6", "#FF6B81", "#FFA502",
                "#70A1FF", "#2ED573", "#1DD1A1", "#55E6C1",
                "#F8EFBA", "#FDA7DF", "#ED4C67", "#B53471",
            ],
        },
        "abyssal-leviathan": {
            "name": "Abyssal Leviathan",
            "light_mode": 1,
            "hue": 25,                  # Sea Aqua / Bioluminescent Cyan
            "saturation": -40,          # Dark oceanic tint
            "lightness": -75,           # Deep oceanic trench dark mode
            "contrast": 35,
            "text_color": "#E0F7FA",    # Bioluminescent Ice White
            "selected": "#00F5D4",      # Bioluminescent Aqua / Electric Mint
            "highlight": "#70FFF0",     # Electric Seafoam
            "mute": "#FF5376",          # Deep Coral Pink
            "option": "#00BBF9",        # Deep Neon Cyan
            "step_even": "#16353D",     # Deep Abyss Teal Slate
            "step_odd": "#071116",      # Trench Black
            "pr_grid_back": "#050B0E",
            "pl_grid_back": "#050B0E",
            "ee_grid_back": "#050B0E",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#04080B",
            "meters": ["#00BBF9", "#00F5D4", "#70FFF0", "#38EF7D", "#FFD166", "#FF5376"],
            "wave_colors": ["#00BBF9", "#00F5D4", "#70FFF0", "#38EF7D", "#FFD166", "#FF5376"],
            "note_colors": [
                "#00F5D4", "#70FFF0", "#00BBF9", "#38EF7D",
                "#11998E", "#05D5B2", "#9BF6FF", "#A0C4FF",
                "#BDB2FF", "#FFC6FF", "#48CAE4", "#0077B6",
                "#03045E", "#CAF0F8", "#90E0EF", "#FF5376",
            ],
        },
        "analog-1984": {
            "name": "Analog 1984",
            "light_mode": 1,
            "hue": 0,
            "saturation": -140,         # Warm vintage brushed charcoal
            "lightness": -65,
            "contrast": 32,
            "text_color": "#F4F1DE",    # Warm Parchment
            "selected": "#FFB703",      # VU Meter Amber Gold
            "highlight": "#FFE8D6",     # Vintage Champagne
            "mute": "#D62828",          # Incandescent Peak Red
            "option": "#2A9D8F",        # Vintage Cassette Teal
            "step_even": "#2B2520",     # Vintage Teak Charcoal
            "step_odd": "#1B1613",      # Analog Tape Deck Shadow
            "pr_grid_back": "#14100E",
            "pl_grid_back": "#14100E",
            "ee_grid_back": "#14100E",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#120E0C",
            "meters": ["#2A9D8F", "#8AB17D", "#E9C46A", "#F4A261", "#E76F51", "#D62828"],
            "wave_colors": ["#2A9D8F", "#8AB17D", "#E9C46A", "#F4A261", "#E76F51", "#D62828"],
            "note_colors": [
                "#FFB703", "#FFE8D6", "#2A9D8F", "#F4A261",
                "#E76F51", "#D62828", "#E9C46A", "#8AB17D",
                "#BC6C25", "#DDA15E", "#606C38", "#283618",
                "#FEFAE0", "#F4F1DE", "#E07A5F", "#3D405B",
            ],
        },
        "cyberdeck": {
            "name": "Cyberdeck",
            "light_mode": 1,
            "hue": 60,                  # Terminal Organic Green
            "saturation": -50,          # Clean phosphor CRT glow
            "lightness": -70,
            "contrast": 36,
            "text_color": "#E8F5E9",    # Phosphor White-Green
            "selected": "#39FF14",      # Electric Phosphor Green
            "highlight": "#66FF99",     # Bright Terminal Mint
            "mute": "#FFB000",          # Terminal Amber Warning
            "option": "#00F5A0",        # Phosphor Teal
            "step_even": "#182618",     # Matrix Terminal Slate
            "step_odd": "#0B120B",      # CRT Cathode Black
            "pr_grid_back": "#060A06",
            "pl_grid_back": "#060A06",
            "ee_grid_back": "#060A06",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#040704",
            "meters": ["#00F5A0", "#39FF14", "#66FF99", "#A8FF78", "#FFB000", "#FF3B30"],
            "wave_colors": ["#00F5A0", "#39FF14", "#66FF99", "#A8FF78", "#FFB000", "#FF3B30"],
            "note_colors": [
                "#39FF14", "#66FF99", "#00F5A0", "#A8FF78",
                "#00E676", "#69F0AE", "#B9F6CA", "#00C853",
                "#76FF03", "#64DD17", "#CCFF90", "#00B0FF",
                "#FFD600", "#FFAB00", "#FF6D00", "#FF3D00",
            ],
        },
        "solaris": {
            "name": "Solaris",
            "light_mode": 1,
            "hue": 0,
            "saturation": -110,         # Deep cosmic slate
            "lightness": -68,
            "contrast": 35,
            "text_color": "#FFF8E7",    # Starburst White
            "selected": "#FFD166",      # Pulsar Core Gold
            "highlight": "#FFE57F",     # Corona White-Gold
            "mute": "#9D4EDD",          # Deep Pulsar Violet
            "option": "#06D6A0",        # Stellar Mint
            "step_even": "#2D1E12",     # Cosmic Bronze Dust
            "step_odd": "#170D08",      # Supernova Void
            "pr_grid_back": "#100805",
            "pl_grid_back": "#100805",
            "ee_grid_back": "#100805",
            "back_pic_filename": "FL STUDIO.png",
            "back_html_filename": "Default.txt",
            "back_color": "#0B0503",
            "meters": ["#06D6A0", "#FFD166", "#FF9F1C", "#FF6B6B", "#9D4EDD", "#7209B7"],
            "wave_colors": ["#06D6A0", "#FFD166", "#FF9F1C", "#FF6B6B", "#9D4EDD", "#7209B7"],
            "note_colors": [
                "#FFD166", "#FFE57F", "#06D6A0", "#FF9F1C",
                "#FF6B6B", "#9D4EDD", "#7209B7", "#F72585",
                "#4CC9F0", "#4895EF", "#4361EE", "#3F37C9",
                "#F3722C", "#F8961E", "#F9844A", "#F9C74F",
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate and install FL Studio .flstheme files")
    parser.add_argument("--name", help="Theme display name", default=None)
    parser.add_argument("--preset", choices=list(get_builtin_presets().keys()), help="Start from a pre-built preset")
    parser.add_argument("--from-json", help="Load theme parameters from a JSON file")
    parser.add_argument("--json-string", help="Inline JSON string with theme configuration")
    parser.add_argument("--selected", help="Primary accent/selection color (Hex #RRGGBB)")
    parser.add_argument("--highlight", help="Secondary highlight color (Hex #RRGGBB)")
    parser.add_argument("--text", help="Text color (Hex #RRGGBB)")
    parser.add_argument("--bg", help="Background canvas color (Hex #RRGGBB)")
    parser.add_argument("--mute", help="Muted indicator color (Hex #RRGGBB)")
    parser.add_argument("--option", help="Option/checkbox toggle color (Hex #RRGGBB)")
    parser.add_argument("--step-even", help="Channel rack step even color (Hex #RRGGBB)")
    parser.add_argument("--step-odd", help="Channel rack step odd color (Hex #RRGGBB)")
    parser.add_argument("--hue", type=int, help="Panel hue offset (-180 to 180)")
    parser.add_argument("--saturation", type=int, help="Panel saturation offset (-256 to 256)")
    parser.add_argument("--lightness", type=int, help="Lightness offset (-256 to 256)")
    parser.add_argument("--contrast", type=int, help="Contrast offset (-100 to 100)")
    parser.add_argument("--light-mode", action="store_true", help="Enable Light Mode base")
    parser.add_argument("--dynamic-html", action="store_true", help="Bundle an ambient dynamic HTML/Canvas wallpaper")
    parser.add_argument("--html-file", help="Path to custom HTML file to use as dynamic background")
    parser.add_argument("--html-content", help="Raw HTML/CSS/Canvas string for dynamic wallpaper")
    parser.add_argument("--extract-from-image", help="Extract color palette from an image or artwork file")
    parser.add_argument("--safe-mode", action="store_true", help="Auto-clamp dangerous settings (e.g. Lightness < -100)")
    parser.add_argument("--bg-image", help="Path to custom image file (.png/.jpg) to use as background wallpaper")
    parser.add_argument("--custom-txt", action="store_true", help="Generate custom wallpaper gradient and logo config")
    parser.add_argument("--install", action="store_true", help="Directly install to FL Studio user Themes folder")
    parser.add_argument("--out", "-o", help="Output path for the .flstheme file")

    args = parser.parse_args()

    builder = FLThemeBuilder(name=args.name or "Custom Theme")
    presets = get_builtin_presets()

    # Apply preset if requested
    if args.preset and args.preset in presets:
        builder.preset_key = args.preset
        builder.apply_palette(presets[args.preset])

    # Extract from image if requested
    if args.extract_from_image and Path(args.extract_from_image).exists():
        extracted = extract_palette_from_image(Path(args.extract_from_image))
        builder.apply_palette(extracted)
        print(f"[Palette Extractor] Extracted dominant theme colors from: {args.extract_from_image}")

    # Apply external JSON if requested
    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            builder.apply_palette(json.load(f))
    elif args.json_string:
        builder.apply_palette(json.loads(args.json_string))

    # Overrides from CLI
    if args.name:
        builder.name = args.name
    if args.selected:
        builder.selected = args.selected
    if args.highlight:
        builder.highlight = args.highlight
    if args.text:
        builder.text_color = args.text
    if args.bg:
        builder.back_color = args.bg
    if args.mute:
        builder.mute = args.mute
    if args.option:
        builder.option = args.option
    if args.step_even:
        builder.step_even = args.step_even
    if args.step_odd:
        builder.step_odd = args.step_odd
    if args.hue is not None:
        builder.hue = args.hue
    if args.saturation is not None:
        builder.saturation = args.saturation
    if args.lightness is not None:
        builder.lightness = args.lightness
    if args.contrast is not None:
        builder.contrast = args.contrast
    if args.light_mode:
        builder.light_mode = 1

    # Wallpaper options
    if args.html_content:
        builder.dynamic_html_content = args.html_content
    elif args.html_file and Path(args.html_file).exists():
        with open(args.html_file, "r", encoding="utf-8") as f:
            builder.dynamic_html_content = f.read()
    elif args.dynamic_html:
        if builder.preset_key:
            html_code = get_html_for_preset(builder.preset_key)
        else:
            html_code = generate_custom_dynamic_html(builder.name, builder.selected, builder.highlight, builder.back_color)
        builder.dynamic_html_content = html_code or generate_tokyo_night_html()

    if args.bg_image and Path(args.bg_image).exists():
        builder.bg_image_path = Path(args.bg_image)

    if args.custom_txt:
        builder.use_custom_txt = True

    # Guardrails validation
    theme_dict = {
        "lightness": builder.lightness,
        "step_even": builder.step_even,
        "step_odd": builder.step_odd,
        "text_color": builder.text_color,
        "back_color": builder.back_color,
        "meters": builder.meters,
        "back_pic_filename": builder.back_pic_filename,
        "back_html_filename": builder.back_html_filename,
    }
    issues = validate_theme_dict(theme_dict)
    if any(issue.level == "WARNING" for issue in issues):
        print("\n--- Guardrails Advisory ---")
        print_validation_report(issues)
        print("---------------------------\n")

    if args.safe_mode and builder.lightness < -100:
        print(f"[Safe Mode] Clamped Lightness from {builder.lightness} to -85 to prevent UI crushing.")
        builder.lightness = -85

    # Output or Install
    if args.install:
        saved_path = builder.install()
        print(f"Successfully installed theme to FL Studio:")
        print(f"  -> {saved_path}")
        if builder.dynamic_html_content:
            print(f"  -> Dynamic HTML wallpaper attached! (wallpaper.html)")
        elif builder.bg_image_path:
            print(f"  -> Custom background image attached! ({builder.bg_image_path.name})")
        print(f"Open FL Studio and navigate to Options > Theme settings to select '{builder.name}'.")
    elif args.out:
        out_path = Path(args.out)
        builder.save(out_path)
        print(f"Saved .flstheme file to: {out_path}")
    else:
        # Print theme to stdout
        print(builder.to_fltheme_string())


if __name__ == "__main__":
    main()
