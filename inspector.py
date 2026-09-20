"""FL Studio Theme Inspector & Parser

Reads and parses .flstheme files, translating FL Studio's 32-bit signed integers
into clean, human-readable hex color codes, and displaying theme summaries.
"""

from __future__ import annotations
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_USER_THEMES_PATH = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "Image-Line" / "FL Studio" / "Settings" / "Themes"


def fl_color_to_hex(val: int) -> Tuple[str, int]:
    """Converts FL Studio signed 32-bit integer to (#RRGGBB, alpha)."""
    unsigned = val & 0xFFFFFFFF
    alpha = (unsigned >> 24) & 0xFF
    r = (unsigned >> 16) & 0xFF
    g = (unsigned >> 8) & 0xFF
    b = unsigned & 0xFF
    return f"#{r:02X}{g:02X}{b:02X}", alpha


def parse_fltheme(file_path: Path) -> Dict[str, Any]:
    """Parses a .flstheme file into a structured dictionary with both raw and hex values."""
    data: Dict[str, Any] = {
        "file": str(file_path),
        "name": file_path.stem,
        "controls": {},
        "colors": {},
        "meters": [],
        "waves": [],
        "notes": [],
        "grids": {},
        "background": {},
        "raw": {}
    }

    color_keys = {
        "Selected", "Highlight", "Mute", "Option", "StepEven", "StepOdd",
        "TextColor", "BackColor", "PRGridback", "PLGridback", "EEGridback"
    }

    with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith((';', '#', '\'')):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
                data["raw"][k] = v

                # Categorize
                if k in ("Hue", "Saturation", "Lightness", "Contrast", "Lightmode", "Text", "OverrideClips"):
                    data["controls"][k] = int(v) if v.lstrip('-').isdigit() else v
                elif k in color_keys:
                    try:
                        int_val = int(v)
                        hex_val, alpha = fl_color_to_hex(int_val)
                        data["colors"][k] = {"hex": hex_val, "alpha": alpha, "raw": int_val}
                    except ValueError:
                        data["colors"][k] = {"raw": v}
                elif k.startswith("Meter"):
                    try:
                        int_val = int(v)
                        hex_val, alpha = fl_color_to_hex(int_val)
                        data["meters"].append({"index": k, "hex": hex_val, "raw": int_val})
                    except ValueError:
                        pass
                elif k.startswith("WaveClr"):
                    try:
                        int_val = int(v)
                        hex_val, alpha = fl_color_to_hex(int_val)
                        data["waves"].append({"index": k, "hex": hex_val, "raw": int_val})
                    except ValueError:
                        pass
                elif k.startswith("NoteColor"):
                    try:
                        int_val = int(v)
                        hex_val, alpha = fl_color_to_hex(int_val)
                        data["notes"].append({"index": k, "hex": hex_val, "raw": int_val})
                    except ValueError:
                        pass
                elif "Grid" in k:
                    data["grids"][k] = v
                elif k.startswith("Back"):
                    data["background"][k] = v

    return data


def format_terminal_color(hex_code: str, text: str = "  ") -> str:
    """Returns ANSI truecolor-formatted block for terminal display."""
    hex_clean = hex_code.lstrip("#")
    if len(hex_clean) == 6:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return f"\033[48;2;{r};{g};{b}m{text}\033[0m"
    return text


def print_theme_summary(theme_data: Dict[str, Any]):
    """Displays a clean CLI breakdown of the theme."""
    print(f"\n==================================================")
    print(f"  THEME: {theme_data['name']}")
    print(f"==================================================")

    print("\n[Controls]")
    for k, v in theme_data["controls"].items():
        print(f"  {k:15}: {v}")

    print("\n[Core Colors]")
    for k, info in theme_data["colors"].items():
        if "hex" in info:
            swatch = format_terminal_color(info["hex"], "    ")
            print(f"  {swatch} {k:14}: {info['hex']} (raw: {info['raw']})")
        else:
            print(f"  {k:14}: {info.get('raw')}")

    if theme_data["meters"]:
        print("\n[Mixer Peak Meters]")
        meter_str = " ".join([format_terminal_color(m["hex"], "  ") for m in theme_data["meters"]])
        hex_list = ", ".join([m["hex"] for m in theme_data["meters"]])
        print(f"  Gradient: {meter_str} [{hex_list}]")

    print("\n[Background & Canvas]")
    for k, v in theme_data["background"].items():
        print(f"  {k:18}: {v}")


def compare_themes(path1: Path, path2: Path):
    """Compares two .flstheme files side-by-side."""
    t1 = parse_fltheme(path1)
    t2 = parse_fltheme(path2)

    print("\n" + "=" * 70)
    print(f"  THEME COMPARISON: {t1['name']}  vs  {t2['name']}")
    print("=" * 70)

    print(f"\n{'Property':20} | {t1['name']:22} | {t2['name']:22}")
    print("-" * 70)

    # Controls
    all_ctrl = sorted(set(t1["controls"].keys()) | set(t2["controls"].keys()))
    for c in all_ctrl:
        v1 = t1["controls"].get(c, "-")
        v2 = t2["controls"].get(c, "-")
        diff_mark = "  " if str(v1) == str(v2) else "* "
        print(f"{diff_mark}{c:18} | {str(v1):22} | {str(v2):22}")

    print("\n[Core Colors]")
    all_clr = sorted(set(t1["colors"].keys()) | set(t2["colors"].keys()))
    for c in all_clr:
        hex1 = t1["colors"].get(c, {}).get("hex", "-")
        hex2 = t2["colors"].get(c, {}).get("hex", "-")
        s1 = format_terminal_color(hex1, " ") if hex1 != "-" else " "
        s2 = format_terminal_color(hex2, " ") if hex2 != "-" else " "
        diff_mark = "  " if hex1 == hex2 else "* "
        print(f"{diff_mark}{c:18} | {s1} {hex1:20} | {s2} {hex2:20}")

    print("\n(* indicates difference between themes)\n")


def main():
    parser = argparse.ArgumentParser(description="Inspect, compare, and parse FL Studio .flstheme files")
    parser.add_argument("path", nargs="?", help="Path to .flstheme file or directory (defaults to FL Studio themes dir)")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    parser.add_argument("--list", action="store_true", help="List all installed themes")
    parser.add_argument("--diff", nargs=2, metavar=("THEME1", "THEME2"), help="Compare two themes side-by-side")
    parser.add_argument("--export-json", help="Export a theme to a JSON file")

    args = parser.parse_args()

    if args.diff:
        p1 = Path(args.diff[0])
        p2 = Path(args.diff[1])
        if not p1.exists() or not p2.exists():
            print(f"Error: One or both files not found: {p1}, {p2}", file=sys.stderr)
            sys.exit(1)
        compare_themes(p1, p2)
        return

    if args.export_json:
        src = Path(args.path) if args.path else Path(args.export_json)
        if not src.exists():
            print(f"Error: Theme file not found: {src}", file=sys.stderr)
            sys.exit(1)
        data = parse_fltheme(src)
        out_target = Path(args.export_json)
        with open(out_target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Exported theme to: {out_target}")
        return

    target_path = Path(args.path) if args.path else DEFAULT_USER_THEMES_PATH

    if not target_path.exists():
        print(f"Error: Path not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    if target_path.is_dir():
        theme_files = sorted(target_path.glob("*.flstheme"))
        if args.list:
            print(f"Found {len(theme_files)} installed theme(s) in {target_path}:")
            for t in theme_files:
                print(f"  • {t.stem}")
            return

        if not theme_files:
            print(f"No .flstheme files found in: {target_path}")
            return

        print(f"Scanning themes in: {target_path} ({len(theme_files)} files)\n")
        all_data = []
        for tf in theme_files:
            parsed = parse_fltheme(tf)
            all_data.append(parsed)
            if not args.json:
                print_theme_summary(parsed)

        if args.json:
            print(json.dumps(all_data, indent=2))

    elif target_path.is_file():
        parsed = parse_fltheme(target_path)
        if args.json:
            print(json.dumps(parsed, indent=2))
        else:
            print_theme_summary(parsed)


if __name__ == "__main__":
    main()

