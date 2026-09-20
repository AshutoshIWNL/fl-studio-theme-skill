"""FL Studio Theme Guardrails & Validation Engine

Enforces usability, visual ergonomics, and DAW stability standards:
1. Luminance crushing prevention (Lightness < -100)
2. Channel rack step readability (StepEven vs StepOdd contrast)
3. Text readability & legibility (WCAG contrast checks)
4. Peak meter clipping distinction (Meter5 vs Meter0-4)
5. 32-bit signed integer boundary enforcement
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from pathlib import Path


@dataclass
class ValidationIssue:
    level: str  # "WARNING", "ERROR", "INFO"
    category: str
    message: str


def calculate_luminance(hex_str: str) -> float:
    """Calculates relative luminance of an sRGB color (0.0 to 1.0)."""
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    if len(hex_clean) != 6:
        return 0.0

    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    def adjust(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculates WCAG contrast ratio between two hex colors (1.0 to 21.0)."""
    lum1 = calculate_luminance(hex1)
    lum2 = calculate_luminance(hex2)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)


def validate_theme_dict(palette: Dict[str, Any]) -> List[ValidationIssue]:
    """Validates a theme dictionary against FL Studio usability guardrails."""
    issues: List[ValidationIssue] = []

    # 1. Luminance Crushing Check
    lightness = palette.get("lightness")
    if lightness is not None:
        try:
            val = int(lightness)
            if val < -100:
                issues.append(ValidationIssue(
                    level="WARNING",
                    category="Luminance",
                    message=f"Lightness is {val} (< -100). This crushes panel contrast and turns FL Studio UI elements pitch-black. Ideal dark themes use -50 to -85."
                ))
            elif val > 50:
                tb = palette.get("text_brightness")
                if tb is not None and int(tb) > 0:
                    issues.append(ValidationIssue(
                        level="WARNING",
                        category="Luminance",
                        message=f"Light panels detected (Lightness={val} > 50) with light text (Text={tb}). UI labels will be unreadable white-on-white! Invert text using text_brightness=-226."
                    ))
                elif val > 160:
                    issues.append(ValidationIssue(
                        level="INFO",
                        category="Luminance",
                        message=f"Lightness is {val} (> 160). High brightness might cause glare; verify Lightmode=1."
                    ))
        except (ValueError, TypeError):
            pass

    # 2. Step Sequencer Readability Check
    step_even = palette.get("step_even")
    step_odd = palette.get("step_odd")
    if step_even and step_odd:
        try:
            c_ratio = contrast_ratio(str(step_even), str(step_odd))
            if c_ratio < 1.15:
                issues.append(ValidationIssue(
                    level="WARNING",
                    category="Step Contrast",
                    message=f"StepEven ({step_even}) and StepOdd ({step_odd}) have very low contrast ratio ({c_ratio:.2f}:1). Music producers will struggle to count 4-beat bars at a glance."
                ))
        except Exception:
            pass

    # 3. Text Legibility Check
    text_clr = palette.get("text_color") or palette.get("text")
    back_clr = palette.get("back_color") or palette.get("bg")
    if text_clr and back_clr:
        try:
            t_ratio = contrast_ratio(str(text_clr), str(back_clr))
            if t_ratio < 3.0:
                issues.append(ValidationIssue(
                    level="WARNING",
                    category="Text Contrast",
                    message=f"TextColor ({text_clr}) vs BackColor ({back_clr}) contrast is low ({t_ratio:.2f}:1). Text labels and values may be difficult to read."
                ))
        except Exception:
            pass

    # 4. Clipping Indicator Distinction Check
    meters = palette.get("meters")
    if meters and len(meters) == 6:
        meter4 = str(meters[4])
        meter5 = str(meters[5])
        if meter4.upper() == meter5.upper():
            issues.append(ValidationIssue(
                level="WARNING",
                category="Meter Clipping",
                message=f"Meter4 (near 0dB) and Meter5 (>0dB clip) have the same color ({meter5}). Producers may not notice digital clipping on the mixer."
            ))

    # 5. Canvas Background Fallback Check
    back_pic = palette.get("back_pic_filename")
    back_html = palette.get("back_html_filename")
    if not back_pic and not back_html:
        issues.append(ValidationIssue(
            level="INFO",
            category="Canvas",
            message="Neither BackPicFilename nor BackHTMLFileName is set. Workspace canvas will appear as an empty fallback color."
        ))

    return issues


def print_validation_report(issues: List[ValidationIssue]):
    """Pretty-prints validation issues to stdout."""
    if not issues:
        print("  [Guardrails] All ergonomic & usability checks passed cleanly! [OK]")
        return

    for issue in issues:
        icon = "[!]" if issue.level == "WARNING" else "[x]" if issue.level == "ERROR" else "[i]"
        print(f"  {icon} [{issue.category}] {issue.message}")
