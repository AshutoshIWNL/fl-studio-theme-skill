---
name: fl-studio-theme
description: >-
  Expert skill for creating, editing, and analyzing custom FL Studio themes (.flstheme).
  Use this skill whenever the user wants to generate, design, customize, or inspect themes
  for FL Studio (v21, v24, v25/2025+), convert palettes (such as Dracula, Tokyo Night, Catppuccin,
  Cyberpunk, or custom hex schemes), or install them directly into FL Studio.
---

# FL Studio Theme Designer Skill

This skill teaches agents how to design, generate, inspect, and install professional themes for **Image-Line FL Studio** (`.flstheme` files).

## 1. Overview & Storage Locations

FL Studio stores theme files in plain-text `.flstheme` format.

- **User Themes Directory (Default Install Target)**:
  - **Windows**: `%USERPROFILE%\Documents\Image-Line\FL Studio\Settings\Themes\`
  - **macOS**: `~/Documents/Image-Line/FL Studio/Settings/Themes/`
- **Application Preset Directory (Read-Only reference)**:
  - `C:\Program Files (x86)\Image-Line\FL Studio 2025\Artwork\Themes\`

When a `.flstheme` file is placed in the User Themes folder, FL Studio automatically recognizes it under **Options > Theme settings** (shortcut `F10`).

---

## 2. The Color Encoding Specification

Colors in `.flstheme` files are stored as **32-bit signed two's complement integers** representing **`0xAARRGGBB`** (Alpha, Red, Green, Blue):

- **Opaque colors (`Alpha = 255` or `0xFF`)** have the 31st bit set, so in 32-bit signed arithmetic they are **negative numbers**:
  $$\text{unsigned} = (255 \ll 24) \mid (R \ll 16) \mid (G \ll 8) \mid B$$
  $$\text{signed} = \text{unsigned if unsigned} < 0x80000000 \text{ else } \text{unsigned} - 0x100000000$$
- **Colors with `Alpha = 0` (used for grid backgrounds)** are positive integers:
  $$\text{unsigned} = (0 \ll 24) \mid (R \ll 16) \mid (G \ll 8) \mid B$$

### Quick Reference Table
| Color | Hex | Alpha | FL Studio Signed Integer |
| :--- | :--- | :--- | :--- |
| Pure Black | `#000000` | 255 | `-16777216` |
| Pure White | `#FFFFFF` | 255 | `-1` |
| Pure White (no alpha) | `#FFFFFF` | 0 | `16777215` |
| FL Lime Green | `#A8E44A` | 0 | `11068490` |
| Light Cherry Pink | `#FF5493` | 255 | `-43885` |
| Cyber Yellow | `#FCEE0A` | 255 | `-197110` |
| Tokyo Blue | `#7AA2F7` | 255 | `-8740105` |

---

## 3. Parameter Schema & Design Rules

Every `.flstheme` file is composed of key-value pairs (`Key=Value`):

### A. Global Sliders & Engine (Crucial for Non-Black Backgrounds)
- `Hue`: Integer (`-180` to `180`). **Tints the entire DAW window panels, toolbars, and mixer strips**:
  - `0`: Neutral slate / warm gray
  - `+20` to `+35`: Sea grass / Aqua-Teal
  - `+50` to `+70`: Organic Meadow / Forest Green (e.g. `55` for Nurture, `60` for Forest)
  - `+120` to `+150`: Olive / Khaki Green
  - `-20` to `-30`: Cool Slate Blue (e.g. `-25` for Tokyo Night)
  - `-40` to `-50`: Indigo / Blue-Purple
  - `-60` to `-80`: Purple / Magenta (e.g. `-65` for Synthwave 84, `-69` for Veela)
  - `-140` to `-170`: Crimson / Blood Red
- `Saturation`: Integer (`-256` to `256`). Controls the color vibrancy of panels. Set `50` to `90` for tasteful panel tinting, or `-80` to `-180` for neutral matte carbon panels.
- `Lightness`: Integer (`-256` to `256`).
  > ⚠️ **Luminance Crushing Warning**: Setting `Lightness` lower than `-100` (e.g. `-180` to `-240`) crushes panel contrast and turns the entire UI into pure pitch black! Ideal modern dark themes use `-50` to `-85`.
- `Contrast`: Integer (`-100` to `100`). Contrast between panel elements. Recommended: `18` to `35`.
- `Lightmode`: Use `1` (standard in 98%+ of modern FL themes for proper icon/font contrast).
- `Text`: Integer (`-256` to `255`). Global text brightness offset. Usually `255` (brightest).
- `OverrideClips`: `0` or `1`. If `1`, playlist clips dynamically inherit the theme tint.

### B. Canvas & Wallpaper (Crucial for Workspace Background)
- `BackMode`: Must be set to `2` (Stretched/Fit) to render wallpapers and gradients.
- `BackPicFilename`: Stock FL Studio wallpapers include `"FL STUDIO.png"`, `"FL STUDIO dark.png"`, `"ultravioletbg.png"`, or `"veela-background-plain.png"`.
- `BackHTMLFileName`: Must be `"Default.txt"` (or `"Ultra green.txt"`).
  > ⚠️ **Why Themes Turn Black**: If `BackPicFilename` and `BackHTMLFileName` are left blank, FL Studio renders NO wallpaper and NO gradient, resulting in a solid black void behind all windows!
- `BackColor`: Signed int. Fallback canvas background color.

### C. Grid Lines & Custom Backgrounds
- `PRGridback`, `PLGridback`, `EEGridback`: Grid background tints for Piano Roll, Playlist, and Event Editor.
- `PRGridCustom`, `PLGridCustom`: **Must be set to `1`**, otherwise FL Studio ignores `PRGridback`/`PLGridback`!
- `PRGridContrast`, `PLGridContrast`: Set to `100` to `150` for crisp grid lines.

### D. Core Accent Colors
- `TextColor`: Signed int. Color of text, numbers, and labels across panels.
- `Selected`: Signed int. Primary accent color. Used for active tabs, selected patterns, active knob rings, and focused borders.
- `Highlight`: Signed int. Secondary accent. Used for cursor hover, playhead indicator, and secondary highlights.
- `Mute`: Signed int. Muted LED indicator or muted channel button color.
- `Option`: Signed int. Checkboxes, radio buttons, dropdown menus, and toggle icons.
- `StepEven` / `StepOdd`: Signed int. The alternating 4-step buttons on the Channel Rack.
  > **DAW Usability Rule**: Always keep distinct lightness/contrast between `StepEven` and `StepOdd` so beats 1-4 and 5-8 are easily distinguishable!

### C. Peak Meters (`Meter0` to `Meter5`)
The 6 mixer meter levels from bottom to top:
- `Meter0`: Floor / silence level (bottom)
- `Meter1`: Low signal (-24dB to -18dB)
- `Meter2`: Mid signal (~ -12dB)
- `Meter3`: High signal (~ -6dB)
- `Meter4`: Near 0dB warning (e.g. orange or bright yellow)
- `Meter5`: > 0dB Clipping indicator (critical! must be high-visibility, usually red/crimson)

### D. Audio Waveforms (`WaveClr0` to `WaveClr5` & `WaveSpc0` to `WaveSpc5`)
Colors used to render sample waveforms in the Playlist and Sampler:
- Spacings: `WaveSpc0=0.0`, `WaveSpc1=0.15`, `WaveSpc2=0.30`, `WaveSpc3=0.48`, `WaveSpc4=0.88`, `WaveSpc5=1.0`.

### E. Piano Roll Note Colors (`NoteColor0` to `NoteColor15`)
16 distinct colors for MIDI channels 1 through 16.

### F. Grid Lines & Backgrounds
- `PRGridback`, `PLGridback`, `EEGridback`: Grid background tints for Piano Roll, Playlist, and Event Editor.
- `PRGridCustom`, `PLGridCustom`, `EEGridCustom`: `1` to enable custom background tint, `0` for default.
- `PRGridContrast`, `PLGridContrast`, `EEGridContrast`: Grid line contrast (`0` to `200`, `100` is default).

### G. Canvas / Wallpaper
- `BackMode`: `0` (Center), `1` (Tile), `2` (Stretch).
- `BackPicFilename`: Optional image name (e.g. `bg.png`).
- `BackHTMLFileName`: Optional background definition file (`Default.txt`, `Ultra green.txt`).
- `BackColor`: Fallback canvas background color.

## 4. The Dynamic Wallpaper Design Framework

FL Studio on Windows embeds a web engine that can render HTML, CSS, JavaScript, and Canvas directly as the DAW background!
Rather than using rigid cookie-cutter templates, the AI agent uses its creativity to design bespoke visual concepts tailored to the user's aesthetic, strictly governed by this DAW framework:

### A. DAW Performance Budget (Zero Audio Latency)
- **CPU Target**: Strictly `< 0.5%` CPU utilization. Must NEVER cause audio buffer underruns or buffer latency spikes.
- **100% Offline**: Pure self-contained vanilla HTML/CSS/Canvas (no CDN links like `cdnjs`, Google Fonts, Three.js that fail offline in a studio).
- **GPU-Accelerated**: Use hardware-accelerated CSS transforms (`transform: translate3d(...)`, `will-change: transform, opacity`) or lightweight `<canvas>` 2D rendering.
- **Element Cap**: Keep active particles/shapes between **30 and 60 items**.

### B. Ergonomics for Music Production
- **Ambient & Atmospheric**: DAW windows (Mixer, Playlist, Channel Rack) float on top of this wallpaper. Movements must be calm, slow, and atmospheric (avoid strobe effects or hyper-saturated primary backgrounds).
- **Base Contrast**: Deep dark canvas base (`#0A0A0F` to `#1E1E28`) matching the theme's `BackColor`.
- **Opacity Control**: Animated elements should maintain `0.15` to `0.55` opacity so foreground text and knob markers remain legible.
- **Theme Branding**: Include a subtle bottom-right watermark: `<Theme Name> • FL Studio` (`opacity: 0.22; pointer-events: none;`).

---

## 5. Helper Tools & Guardrails Engine

The skill includes standalone deterministic tools in `fl-studio-theme-skill/`:

1. **`generator.py` (Theme Compiler)**:
   - Generates `.flstheme` files and auto-bundles thumbnails (`thm<ThemeName>.jpg`), companion static wallpapers, dynamic HTML wallpapers, and custom images.
   - **Pre-built Presets**:
     - `nurture` / `nature`: Organic Porter Robinson *Nurture* aesthetic (lush forest greens, floating spores & fireflies)
     - `cyber-blossom`: Neo-Tokyo sakura pink & deep charcoal with drifting petals animation
     - `tokyo-night`: Midnight Tokyo slate/indigo with ambient starry canvas
     - `cyberpunk`: Cyberpunk 2077 neon yellow & cyan with animated 3D cyber grid
     - `synthwave-84`: Outrun purple/magenta with retro sunset horizon
     - `catppuccin-mocha`: Pastel charcoal with drifting pastel auroras
     - `dracula`: Vampiric gothic slate with misty fog animation
     - `oled-crimson`: Pure OLED black with blood red accents & pulsing audio core
     - `abyssal-leviathan`: Deep-sea bioluminescent cyan & coral with floating jellyfish & plankton simulation
     - `analog-1984`: Vintage warm parchment & VU amber with dual spinning cassette tape reels
     - `cyberdeck`: Phosphor green CRT terminal with matrix digital rain & scanline decay
     - `solaris`: Celestial supernova gold & violet with breathing pulsar core & coronal rings
     - `ceramic-cherry`: Pure porcelain white panels with cherry pink & violet accents, dark berry typography, and drifting petal refractions
     - `alabaster-tangerine`: Bauhaus alabaster white panels with tangerine orange & azure blue accents and drafting crosshairs
     - `porcelain-pear`: Porcelain white panels with pear lime & emerald mint accents, dark forest typography, and drifting dew drops
     - `oled-pink`: Pure pitch black OLED panels drenched in electric hot pink with pulsing audio rings
     - `oled-emerald`: Pure pitch black OLED panels drenched in radioactive emerald green with glowing spectrum aura
   - **CLI Ingestion**:
     ```bash
     # Direct custom theme with bespoke dynamic HTML string
     python generator.py --name "Rainy Lo-Fi" --selected "#D4A373" --html-content "..." --install

     # Extract palette directly from artwork or album cover
     python generator.py --name "Discovery" --extract-from-image "C:/art/cover.png" --dynamic-html --install
     ```

2. **`validator.py` (Ergonomic Guardrails & Linter)**:
   - Evaluates themes against usability benchmarks:
     - **Luminance Crushing**: Warns if `Lightness < -100` (which turns panels pitch black).
     - **Step Contrast**: Enforces minimum 1.25:1 contrast between `StepEven` and `StepOdd`.
     - **Text Contrast**: Enforces WCAG AA text legibility.
     - **Clipping Distinction**: Ensures `Meter5` (>0dB clip) is visually distinct from low/mid levels.

3. **`inspector.py` (Theme Inspector & Diff Tool)**:
   - Lists and inspects all installed themes, decoding their integer values back to hex colors:
     ```bash
     python inspector.py --list
     python inspector.py "C:\path\to\theme.flstheme"
     python inspector.py --diff ThemeA.flstheme ThemeB.flstheme
     python inspector.py --export-json Theme.flstheme
     ```

---

## 6. Agent Procedure: When Asked to Create a Theme

> 🔒 **Engine Immutability Rule**:
> NEVER modify `generator.py` or `wallpapers.py` when creating custom user themes!
> `generator.py` is a self-contained CLI compiler.
> Always generate custom themes by invoking `generator.py` with CLI flags (`--name`, `--selected`, `--hue`, `--html-content`, etc.) or via `--json-string` / `--from-json`.

1. **Understand Aesthetic & Concept**:
   - Determine primary mood, accent colors, and background animation metaphor (e.g. rain on window, fireflies, cosmic stardust, glowing jellyfish).
2. **Select Harmonious Palette & Panel Engine**:
   - Background (`#0A0A0F` to `#1E1E28`)
   - Text (`#C0C0D0` to `#FFFFFF`)
   - Accent / Selected & Highlight
   - High-contrast Channel Rack steps (`StepEven` lighter, `StepOdd` darker)
   - Peak meters (6-color gradient terminating in distinct clipping warning)
   - Panel Hue & Saturation (use `0` and `-80` to `-140` for clean dark charcoal, `+50` to `+70` for lush green, `-25` for blue).
3. **Author Dynamic HTML (If Requested)**:
   - Write a bespoke, self-contained HTML5/Canvas/CSS document adhering to the Dynamic Wallpaper Framework.
4. **Compile & Install via Deterministic CLI**:
   - Execute:
     ```bash
     python generator.py --name "<Name>" --selected "<Hex>" --highlight "<Hex>" --hue <Int> --saturation <Int> --html-content "<HTML>" --install
     ```
   - Verify `validator.py` reports clean guardrails.
   - Inform the user of how to select the theme in FL Studio via `F10` (Options > Theme settings).
