"""Distribution Builder for FL Studio Themes Pack

Builds and packages all shipped theme presets into a standalone distribution ZIP
archive for users who want to install themes directly without Python.
"""

from __future__ import annotations
import shutil
import zipfile
from pathlib import Path

from generator import FLThemeBuilder, get_builtin_presets
from wallpapers import get_html_for_preset


def build_distribution(dist_dir: Path = Path("dist")):
    """Generates all themes and compiles them into a release zip."""
    pack_dir = dist_dir / "fl-studio-themes"
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)

    presets = get_builtin_presets()
    unique_presets = {}
    for k, v in presets.items():
        name = v["name"]
        if name not in unique_presets:
            unique_presets[name] = (k, v)

    print(f"Building {len(unique_presets)} shipped theme bundles...")

    for theme_name, (preset_key, palette) in unique_presets.items():
        print(f"  -> Compiling theme: {theme_name}")
        builder = FLThemeBuilder(theme_name)
        builder.preset_key = preset_key
        builder.apply_palette(palette)

        # Dynamic HTML
        html_code = get_html_for_preset(preset_key)
        if html_code:
            builder.dynamic_html_content = html_code

        # Install into pack_dir
        builder.install(custom_themes_dir=pack_dir, bundle_folder=True)

    # Create README in pack
    readme_pack = pack_dir / "README_INSTALL.txt"
    with open(readme_pack, "w", encoding="utf-8") as f:
        f.write(
            "FL Studio Themes Pack\n"
            "=====================\n\n"
            "HOW TO INSTALL:\n"
            "1. Copy all folders and .flstheme files from this folder.\n"
            "2. Paste them into your FL Studio Themes directory:\n"
            "   - Windows: %USERPROFILE%\\Documents\\Image-Line\\FL Studio\\Settings\\Themes\\\n"
            "   - macOS: ~/Documents/Image-Line/FL Studio/Settings/Themes/\n"
            "3. Open FL Studio and press F10 (or Options > Theme settings).\n"
            "4. Select your favorite theme!\n\n"
            "DYNAMIC HTML WALLPAPERS:\n"
            "To activate an animated HTML background:\n"
            "Go to View > Background > Set dynamic wallpaper / HTML document... and choose\n"
            "the 'wallpaper.html' file inside that theme's folder.\n"
        )

    # Create zip
    zip_path = dist_dir / "fl-studio-themes-pack.zip"
    print(f"\nCompressing into {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in pack_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(pack_dir)
                zf.write(file, arcname)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Build complete! Archive created: {zip_path} ({size_mb:.2f} MB)")
    return zip_path


if __name__ == "__main__":
    build_distribution()
