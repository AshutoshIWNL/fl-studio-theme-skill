"""Dynamic HTML and Wallpaper Generator for FL Studio

Generates lightweight, GPU-accelerated, ambient dynamic HTML/CSS/Canvas
wallpapers and static backgrounds specifically tuned for music production.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any


def generate_tokyo_night_html() -> str:
    """Generates an ambient Tokyo Night dynamic HTML wallpaper."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Tokyo Night Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: radial-gradient(circle at 50% 30%, #1e2030 0%, #1a1b26 60%, #12131a 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 14px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(122, 162, 247, 0.2);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="watermark">Tokyo Night &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  // Subtle ambient floating stars / dust motes
  const stars = [];
  const STAR_COUNT = 45; // Keep low for zero CPU impact in DAW
  for (let i = 0; i < STAR_COUNT; i++) {
    stars.push({
      x: Math.random() * w,
      y: Math.random() * h,
      radius: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.5 + 0.2,
      speed: Math.random() * 0.15 + 0.05,
      color: Math.random() > 0.4 ? '#7AA2F7' : '#BB9AF7'
    });
  }

  function draw() {
    ctx.clearRect(0, 0, w, h);
    for (let s of stars) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.globalAlpha = s.alpha * (0.6 + 0.4 * Math.sin(Date.now() * 0.001 * s.speed * 5));
      ctx.shadowBlur = 8;
      ctx.shadowColor = s.color;
      ctx.fill();
      ctx.restore();

      s.y -= s.speed;
      if (s.y < 0) {
        s.y = h;
        s.x = Math.random() * w;
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
</script>
</body>
</html>
"""


def generate_cyberpunk_html() -> str:
    """Generates an ambient Cyberpunk 2077 digital grid wallpaper."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cyberpunk 2077 Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0d0e15;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: monospace;
  }
  .grid {
    position: absolute;
    width: 200%;
    height: 100%;
    bottom: -30%;
    left: -50%;
    background-image: 
      linear-gradient(rgba(0, 240, 255, 0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 240, 255, 0.08) 1px, transparent 1px);
    background-size: 50px 50px;
    transform: perspective(600px) rotateX(65deg);
    animation: moveGrid 12s linear infinite;
  }
  @keyframes moveGrid {
    0% { transform: perspective(600px) rotateX(65deg) translateY(0); }
    100% { transform: perspective(600px) rotateX(65deg) translateY(50px); }
  }
  .horizon-glow {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 60%;
    background: radial-gradient(ellipse at 50% 50%, rgba(252, 238, 10, 0.06) 0%, rgba(0, 240, 255, 0.03) 40%, transparent 80%);
    pointer-events: none;
  }
  .hud-badge {
    position: absolute;
    top: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 3px;
    color: #FCEE0A;
    opacity: 0.35;
    text-transform: uppercase;
    font-weight: bold;
    border: 1px solid rgba(252, 238, 10, 0.25);
    padding: 6px 14px;
    background: rgba(13, 14, 21, 0.7);
  }
</style>
</head>
<body>
<div class="horizon-glow"></div>
<div class="grid"></div>
<div class="hud-badge">[ CYBERPUNK 2077 // FL STUDIO ]</div>
</body>
</html>
"""


def generate_synthwave_html() -> str:
    """Generates an Outrun / Synthwave 84 dynamic horizon wallpaper."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Synthwave 84 Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: linear-gradient(180deg, #100b1a 0%, #1e1333 45%, #2a153c 60%, #150921 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
  }
  .sun {
    position: absolute;
    top: 25%;
    left: 50%;
    transform: translateX(-50%);
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: linear-gradient(180deg, #ffd319 0%, #ff2975 60%, #8c1eff 100%);
    box-shadow: 0 0 50px rgba(255, 41, 117, 0.45);
  }
  .grid {
    position: absolute;
    bottom: 0;
    left: -50%;
    width: 200%;
    height: 50%;
    background-image: 
      linear-gradient(rgba(255, 126, 219, 0.15) 1px, transparent 1px),
      linear-gradient(90deg, rgba(54, 249, 246, 0.15) 1px, transparent 1px);
    background-size: 40px 40px;
    transform: perspective(400px) rotateX(60deg);
    animation: scroll 8s linear infinite;
  }
  @keyframes scroll {
    0% { transform: perspective(400px) rotateX(60deg) translateY(0); }
    100% { transform: perspective(400px) rotateX(60deg) translateY(40px); }
  }
</style>
</head>
<body>
<div class="sun"></div>
<div class="grid"></div>
</body>
</html>
"""


def generate_catppuccin_html() -> str:
    """Generates an ambient Catppuccin Mocha smooth gradient wallpaper."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Catppuccin Mocha Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #181825;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
  }
  .glow-1 {
    position: absolute;
    width: 600px;
    height: 600px;
    top: -100px;
    left: 20%;
    background: radial-gradient(circle, rgba(137, 180, 250, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    animation: drift 20s ease-in-out infinite alternate;
  }
  .glow-2 {
    position: absolute;
    width: 500px;
    height: 500px;
    bottom: -50px;
    right: 25%;
    background: radial-gradient(circle, rgba(203, 166, 247, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    animation: drift 24s ease-in-out infinite alternate-reverse;
  }
  @keyframes drift {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(40px, 30px) scale(1.1); }
  }
</style>
</head>
<body>
<div class="glow-1"></div>
<div class="glow-2"></div>
</body>
</html>
"""


def generate_nurture_html() -> str:
    """Generates an organic Nature/Nurture dynamic HTML wallpaper with floating spores & fireflies."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Nurture / Nature Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: radial-gradient(circle at 50% 40%, #17281c 0%, #0f1c13 55%, #0a130d 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(120, 224, 143, 0.25);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="watermark">NURTURE &bull; NATURE'S HARMONY</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  // Floating organic fireflies & dandelion spores
  const spores = [];
  const SPORE_COUNT = 40;
  for (let i = 0; i < SPORE_COUNT; i++) {
    spores.push({
      x: Math.random() * w,
      y: Math.random() * h,
      radius: Math.random() * 2.0 + 0.8,
      alpha: Math.random() * 0.6 + 0.2,
      vx: (Math.random() - 0.5) * 0.2,
      vy: -(Math.random() * 0.25 + 0.1),
      pulse: Math.random() * Math.PI * 2,
      color: Math.random() > 0.35 ? '#78E08F' : '#A8FF78'
    });
  }

  function draw() {
    ctx.clearRect(0, 0, w, h);
    for (let s of spores) {
      s.pulse += 0.02;
      ctx.save();
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.globalAlpha = s.alpha * (0.5 + 0.5 * Math.sin(s.pulse));
      ctx.shadowBlur = 10;
      ctx.shadowColor = s.color;
      ctx.fill();
      ctx.restore();

      s.x += s.vx + Math.sin(s.pulse) * 0.15;
      s.y += s.vy;
      if (s.y < 0) {
        s.y = h + 10;
        s.x = Math.random() * w;
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
</script>
</body>
</html>
"""


def generate_dracula_html() -> str:
    """Generates a Gothic Dracula mist dynamic HTML wallpaper."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Dracula Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #1e1f29;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
  }
  .mist-1 {
    position: absolute;
    width: 800px;
    height: 800px;
    top: -200px;
    left: 10%;
    background: radial-gradient(circle, rgba(189, 147, 249, 0.07) 0%, transparent 65%);
    border-radius: 50%;
    animation: mistFloat 22s ease-in-out infinite alternate;
  }
  .mist-2 {
    position: absolute;
    width: 700px;
    height: 700px;
    bottom: -150px;
    right: 15%;
    background: radial-gradient(circle, rgba(255, 121, 198, 0.05) 0%, transparent 70%);
    border-radius: 50%;
    animation: mistFloat 28s ease-in-out infinite alternate-reverse;
  }
  @keyframes mistFloat {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(50px, 40px) scale(1.15); }
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 4px;
    color: rgba(80, 250, 123, 0.25);
    font-family: monospace;
    font-weight: bold;
  }
</style>
</head>
<body>
<div class="mist-1"></div>
<div class="mist-2"></div>
<div class="watermark">[ DRACULA // FL STUDIO ]</div>
</body>
</html>
"""


def generate_oled_crimson_html() -> str:
    """Generates an ultra-minimalist OLED pulse dynamic HTML wallpaper."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OLED Crimson Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #000000;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .pulse-core {
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 23, 68, 0.08) 0%, rgba(255, 23, 68, 0.02) 60%, transparent 80%);
    box-shadow: 0 0 80px rgba(255, 23, 68, 0.15);
    animation: pulse 4s ease-in-out infinite;
  }
  .pulse-ring {
    position: absolute;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    border: 1px solid rgba(255, 23, 68, 0.08);
    animation: expand 4s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.6; }
    50% { transform: scale(1.18); opacity: 1; }
  }
  @keyframes expand {
    0%, 100% { transform: scale(0.95); opacity: 0.3; }
    50% { transform: scale(1.25); opacity: 0.8; }
  }
</style>
</head>
<body>
<div class="pulse-core"></div>
<div class="pulse-ring"></div>
</body>
</html>
"""


def generate_cyber_blossom_html() -> str:
    """Generates an ambient Cyber Blossom dynamic HTML wallpaper with floating sakura petals."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cyber Blossom Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: radial-gradient(circle at 50% 25%, #1c1424 0%, #120e18 60%, #0a070e 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(255, 42, 133, 0.22);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="watermark">Cyber Blossom &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  class Petal {
    constructor() {
      this.reset(true);
    }
    reset(initial = false) {
      this.x = Math.random() * w;
      this.y = initial ? Math.random() * h : -20;
      this.size = 6 + Math.random() * 8;
      this.speedY = 0.5 + Math.random() * 0.9;
      this.speedX = -0.3 + Math.random() * 0.6;
      this.angle = Math.random() * Math.PI * 2;
      this.rotSpeed = (Math.random() - 0.5) * 0.03;
      this.oscFreq = 0.01 + Math.random() * 0.02;
      this.oscAmp = 20 + Math.random() * 30;
      this.baseX = this.x;
      this.opacity = 0.35 + Math.random() * 0.45;
      this.colorType = Math.random();
    }
    update(t) {
      this.y += this.speedY;
      this.x = this.baseX + Math.sin(t * this.oscFreq + this.angle) * this.oscAmp;
      this.angle += this.rotSpeed;
      if (this.y > h + 20 || this.x < -30 || this.x > w + 30) {
        this.reset();
      }
    }
    draw() {
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate(this.angle);
      ctx.globalAlpha = this.opacity;
      
      const grad = ctx.createLinearGradient(-this.size, -this.size, this.size, this.size);
      if (this.colorType > 0.4) {
        grad.addColorStop(0, '#FF2A85');
        grad.addColorStop(1, '#FF70A6');
      } else {
        grad.addColorStop(0, '#D980FA');
        grad.addColorStop(1, '#FF2A85');
      }
      ctx.fillStyle = grad;
      ctx.shadowColor = '#FF2A85';
      ctx.shadowBlur = 8;

      ctx.beginPath();
      ctx.moveTo(0, -this.size);
      ctx.bezierCurveTo(this.size * 0.8, -this.size * 0.6, this.size * 0.9, this.size * 0.6, 0, this.size);
      ctx.bezierCurveTo(-this.size * 0.9, this.size * 0.6, -this.size * 0.8, -this.size * 0.6, 0, -this.size);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
  }

  const petals = Array.from({ length: 42 }, () => new Petal());
  let t = 0;

  function animate() {
    ctx.clearRect(0, 0, w, h);
    t++;
    for (let p of petals) {
      p.update(t);
      p.draw();
    }
    requestAnimationFrame(animate);
  }
  animate();
</script>
</body>
</html>
"""


def generate_custom_dynamic_html(theme_name: str, primary_hex: str, secondary_hex: str, bg_hex: str) -> str:
    """Generates a custom GPU-accelerated ambient dynamic particle HTML wallpaper."""
    p_clean = primary_hex.lstrip('#')
    s_clean = secondary_hex.lstrip('#')
    b_clean = bg_hex.lstrip('#')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{theme_name} Dynamic Wallpaper</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: radial-gradient(circle at 50% 30%, #{b_clean} 0%, #0d0e12 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  canvas {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }}
  .watermark {{
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba({int(p_clean[0:2], 16)}, {int(p_clean[2:4], 16)}, {int(p_clean[4:6], 16)}, 0.22);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }}
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="watermark">{theme_name} &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {{
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }}
  window.addEventListener('resize', resize);
  resize();

  class Particle {{
    constructor() {{
      this.reset(true);
    }}
    reset(initial = false) {{
      this.x = Math.random() * w;
      this.y = initial ? Math.random() * h : h + 10;
      this.size = 1.5 + Math.random() * 3.5;
      this.speedY = -(0.2 + Math.random() * 0.6);
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.color = Math.random() > 0.4 ? '#{p_clean}' : '#{s_clean}';
      this.opacity = 0.2 + Math.random() * 0.6;
    }}
    update() {{
      this.y += this.speedY;
      this.x += this.speedX;
      if (this.y < -10 || this.x < -10 || this.x > w + 10) {{
        this.reset();
      }}
    }}
    draw() {{
      ctx.save();
      ctx.globalAlpha = this.opacity;
      ctx.shadowColor = this.color;
      ctx.shadowBlur = 10;
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }}
  }}

  const particles = Array.from({{ length: 45 }}, () => new Particle());

  function animate() {{
    ctx.clearRect(0, 0, w, h);
    for (let p of particles) {{
      p.update();
      p.draw();
    }}
    requestAnimationFrame(animate);
  }}
  animate();
</script>
</body>
</html>
"""


def generate_wallpaper_txt(bg_top_hex: str, bg_bottom_hex: str, caption_hex: str = "") -> str:
    """Generates an FL Studio wallpaper .txt config with gradient and tinted logo."""
    top_clean = bg_top_hex.lstrip("#").upper()
    bot_clean = bg_bottom_hex.lstrip("#").upper()
    lines = [
        "' background gradient colors",
        f"Background=$FF{top_clean},$FF{bot_clean}",
        "' logo, size, colors"
    ]
    if caption_hex:
        cap_clean = caption_hex.lstrip("#").upper()
        lines.append(f"Caption=O,150,$FF{cap_clean}")
    else:
        lines.append("Caption=O,150")

    return "\n".join(lines) + "\n"


def generate_abyssal_leviathan_html() -> str:
    """Generates an ambient Abyssal Leviathan dynamic HTML wallpaper with bioluminescent jellyfish."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Abyssal Leviathan Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: radial-gradient(circle at 50% 20%, #0c1824 0%, #070e17 50%, #03060a 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(0, 245, 212, 0.22);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="watermark">Abyssal Leviathan &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  class Plankton {
    constructor() { this.reset(true); }
    reset(init = false) {
      this.x = Math.random() * w;
      this.y = init ? Math.random() * h : h + 10;
      this.size = 1 + Math.random() * 2.5;
      this.speedY = -(0.2 + Math.random() * 0.4);
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.opacity = 0.2 + Math.random() * 0.5;
      this.color = Math.random() > 0.4 ? '#00F5D4' : '#7209B7';
    }
    update() {
      this.y += this.speedY;
      this.x += this.speedX;
      if (this.y < -10) this.reset();
    }
    draw() {
      ctx.save();
      ctx.globalAlpha = this.opacity;
      ctx.fillStyle = this.color;
      ctx.shadowColor = this.color;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  class Jellyfish {
    constructor(x, y, scale, speed) {
      this.x = x;
      this.y = y;
      this.baseY = y;
      this.scale = scale;
      this.speed = speed;
      this.phase = Math.random() * Math.PI * 2;
    }
    update(t) {
      this.phase += this.speed;
      this.y -= 0.35;
      if (this.y < -150) this.y = h + 120;
    }
    draw() {
      ctx.save();
      ctx.translate(this.x, this.y);
      const pulse = Math.sin(this.phase) * 0.15;
      const r = 35 * this.scale;
      const hRad = r * (1 + pulse);
      const vRad = r * (1 - pulse * 0.7);

      // Bell
      ctx.beginPath();
      ctx.ellipse(0, 0, hRad, vRad, 0, Math.PI, 0);
      const grad = ctx.createRadialGradient(0, -vRad * 0.3, 2, 0, 0, hRad);
      grad.addColorStop(0, 'rgba(0, 245, 212, 0.45)');
      grad.addColorStop(0.6, 'rgba(114, 9, 183, 0.25)');
      grad.addColorStop(1, 'rgba(0, 245, 212, 0.05)');
      ctx.fillStyle = grad;
      ctx.shadowColor = '#00F5D4';
      ctx.shadowBlur = 15;
      ctx.fill();

      // Tentacles
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = 'rgba(0, 245, 212, 0.3)';
      for (let i = -2; i <= 2; i++) {
        ctx.beginPath();
        const startX = i * (hRad / 3);
        ctx.moveTo(startX, 0);
        const wave = Math.sin(this.phase + i) * 8;
        ctx.bezierCurveTo(startX + wave, 25 * this.scale, startX - wave, 55 * this.scale, startX + wave * 0.5, 90 * this.scale);
        ctx.stroke();
      }
      ctx.restore();
    }
  }

  const planktons = Array.from({ length: 35 }, () => new Plankton());
  const jellies = [
    new Jellyfish(w * 0.25, h * 0.6, 1.1, 0.02),
    new Jellyfish(w * 0.72, h * 0.85, 0.85, 0.025),
    new Jellyfish(w * 0.5, h * 0.3, 0.65, 0.018),
  ];

  let lastTime = 0;
  const fpsInterval = 1000 / 35;
  let isVisible = true;
  document.addEventListener('visibilitychange', () => { isVisible = !document.hidden; });

  function animate(now) {
    requestAnimationFrame(animate);
    if (!isVisible) return;
    if (now - lastTime < fpsInterval) return;
    lastTime = now;

    ctx.clearRect(0, 0, w, h);
    for (let p of planktons) { p.update(); p.draw(); }
    for (let j of jellies) { j.update(); j.draw(); }
  }
  requestAnimationFrame(animate);
</script>
</body>
</html>
"""


def generate_analog_1984_html() -> str:
    """Generates an ambient Analog 1984 dynamic HTML wallpaper with dual spinning cassette reels."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analog 1984 Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: radial-gradient(circle at 50% 35%, #1f1a16 0%, #13100e 60%, #0a0807 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(255, 159, 28, 0.22);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
  .scanlines {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(rgba(18, 16, 14, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
    background-size: 100% 3px, 6px 100%;
    pointer-events: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="scanlines"></div>
<div class="watermark">Analog 1984 &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  let angle = 0;
  let lastTime = 0;
  const fpsInterval = 1000 / 30;
  let isVisible = true;
  document.addEventListener('visibilitychange', () => { isVisible = !document.hidden; });

  function drawReel(cx, cy, radius, rot) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot);

    // Outer wheel
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.fillStyle = '#1c1714';
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.25)';
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    // 3 Cutouts
    for (let i = 0; i < 3; i++) {
      ctx.save();
      ctx.rotate((i * Math.PI * 2) / 3);
      ctx.beginPath();
      ctx.arc(0, -radius * 0.52, radius * 0.22, 0, Math.PI * 2);
      ctx.fillStyle = '#0f0c0a';
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }

    // Center hub
    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.28, 0, Math.PI * 2);
    ctx.fillStyle = '#28201a';
    ctx.strokeStyle = '#FF9F1C';
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    // 6 Sprockets
    for (let j = 0; j < 6; j++) {
      ctx.save();
      ctx.rotate((j * Math.PI * 2) / 6);
      ctx.fillStyle = '#FF9F1C';
      ctx.fillRect(-3, -radius * 0.28, 6, 8);
      ctx.restore();
    }
    ctx.restore();
  }

  function animate(now) {
    requestAnimationFrame(animate);
    if (!isVisible) return;
    if (now - lastTime < fpsInterval) return;
    lastTime = now;

    ctx.clearRect(0, 0, w, h);
    angle += 0.012;

    const cx = w / 2;
    const cy = h / 2;
    const reelR = Math.min(w, h) * 0.14;
    const spacing = reelR * 1.6;

    // Amber Backlight Glow
    const bgGlow = ctx.createRadialGradient(cx, cy, 10, cx, cy, spacing * 1.5);
    bgGlow.addColorStop(0, 'rgba(255, 159, 28, 0.12)');
    bgGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = bgGlow;
    ctx.fillRect(cx - spacing * 1.5, cy - reelR * 1.5, spacing * 3, reelR * 3);

    // Cassette Window Outline
    ctx.strokeStyle = 'rgba(255, 159, 28, 0.2)';
    ctx.lineWidth = 2;
    ctx.strokeRect(cx - spacing * 1.25, cy - reelR * 1.2, spacing * 2.5, reelR * 2.4);

    // Connecting Tape Ribbon
    ctx.beginPath();
    ctx.moveTo(cx - spacing, cy + reelR);
    ctx.lineTo(cx + spacing, cy + reelR);
    ctx.strokeStyle = '#3d3027';
    ctx.lineWidth = 5;
    ctx.stroke();

    // Left & Right Reels
    drawReel(cx - spacing, cy, reelR, angle);
    drawReel(cx + spacing, cy, reelR, angle * 0.95);
  }
  requestAnimationFrame(animate);
</script>
</body>
</html>
"""


def generate_cyberdeck_html() -> str:
    """Generates an ambient Cyberdeck dynamic HTML wallpaper with green phosphor digital rain."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cyberdeck Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #040804;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: "Courier New", Courier, monospace;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(0, 255, 102, 0.22);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
  .crt {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(rgba(18, 26, 18, 0) 50%, rgba(0, 0, 0, 0.35) 50%);
    background-size: 100% 4px;
    pointer-events: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="crt"></div>
<div class="watermark">Cyberdeck // 0x464C &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h, cols, ypos;
  const chars = '0123456789ABCDEF0xFLMIDIPCMASIOdB44.1k96k';

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    cols = Math.floor(w / 24) + 1;
    ypos = Array.from({ length: cols }, () => Math.random() * -h);
  }
  window.addEventListener('resize', resize);
  resize();

  let lastTime = 0;
  const fpsInterval = 1000 / 30;
  let isVisible = true;
  document.addEventListener('visibilitychange', () => { isVisible = !document.hidden; });

  function animate(now) {
    requestAnimationFrame(animate);
    if (!isVisible) return;
    if (now - lastTime < fpsInterval) return;
    lastTime = now;

    // Phosphor decay trail
    ctx.fillStyle = 'rgba(4, 8, 4, 0.08)';
    ctx.fillRect(0, 0, w, h);

    ctx.font = '14px monospace';

    for (let i = 0; i < cols; i++) {
      const text = chars.charAt(Math.floor(Math.random() * chars.length));
      const x = i * 24;
      const y = ypos[i];

      // Leading character is bright phosphor white/green
      ctx.fillStyle = '#A3FFCD';
      ctx.shadowColor = '#00FF66';
      ctx.shadowBlur = 8;
      ctx.fillText(text, x, y);

      if (y > 100 + Math.random() * 10000) {
        ypos[i] = 0;
      } else {
        ypos[i] = y + 16;
      }
    }
  }
  requestAnimationFrame(animate);
</script>
</body>
</html>
"""


def generate_solaris_html() -> str:
    """Generates an ambient Solaris dynamic HTML wallpaper with a breathing celestial pulsar."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Solaris Dynamic Wallpaper</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: radial-gradient(circle at 50% 30%, #161026 0%, #0d0817 60%, #06040a 100%);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  .watermark {
    position: absolute;
    bottom: 40px;
    right: 50px;
    font-size: 13px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: rgba(255, 209, 102, 0.22);
    font-weight: 700;
    pointer-events: none;
    user-select: none;
  }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div class="watermark">Solaris &bull; FL Studio</div>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  class Star {
    constructor() { this.reset(true); }
    reset(init = false) {
      this.angle = Math.random() * Math.PI * 2;
      this.dist = 40 + Math.random() * (Math.max(w, h) * 0.45);
      this.speed = (0.0005 + Math.random() * 0.001) * (Math.random() > 0.5 ? 1 : -1);
      this.size = 1 + Math.random() * 2;
      this.opacity = 0.2 + Math.random() * 0.55;
      this.color = Math.random() > 0.35 ? '#FFD166' : '#9D4EDD';
    }
    update() {
      this.angle += this.speed;
    }
    draw(cx, cy) {
      const x = cx + Math.cos(this.angle) * this.dist;
      const y = cy + Math.sin(this.angle) * this.dist * 0.65;
      ctx.save();
      ctx.globalAlpha = this.opacity;
      ctx.fillStyle = this.color;
      ctx.shadowColor = this.color;
      ctx.shadowBlur = 6;
      ctx.beginPath();
      ctx.arc(x, y, this.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  const stars = Array.from({ length: 42 }, () => new Star());
  let t = 0;
  let lastTime = 0;
  const fpsInterval = 1000 / 35;
  let isVisible = true;
  document.addEventListener('visibilitychange', () => { isVisible = !document.hidden; });

  function animate(now) {
    requestAnimationFrame(animate);
    if (!isVisible) return;
    if (now - lastTime < fpsInterval) return;
    lastTime = now;

    ctx.clearRect(0, 0, w, h);
    t += 0.015;

    const cx = w / 2;
    const cy = h * 0.42;

    // Pulsar core glow
    const pulse = Math.sin(t) * 12;
    const r = 50 + pulse;
    const coreGlow = ctx.createRadialGradient(cx, cy, 5, cx, cy, r * 3);
    coreGlow.addColorStop(0, 'rgba(255, 209, 102, 0.45)');
    coreGlow.addColorStop(0.4, 'rgba(157, 78, 221, 0.25)');
    coreGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = coreGlow;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 3, 0, Math.PI * 2);
    ctx.fill();

    // 2 Coronal Rings
    for (let i = 1; i <= 2; i++) {
      ctx.save();
      ctx.beginPath();
      const ringR = (r * (i * 1.6)) + (Math.sin(t * 1.2 + i) * 6);
      ctx.ellipse(cx, cy, ringR * 1.5, ringR * 0.7, t * 0.05 * i, 0, Math.PI * 2);
      ctx.strokeStyle = i === 1 ? 'rgba(255, 209, 102, 0.25)' : 'rgba(157, 78, 221, 0.2)';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = '#FFD166';
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.restore();
    }

    // Orbiting Stardust
    for (let s of stars) { s.update(); s.draw(cx, cy); }
  }
  requestAnimationFrame(animate);
</script>
</body>
</html>
"""


def get_html_for_preset(preset_key: str) -> str | None:
    """Returns dynamic HTML string for a recognized preset."""
    mapping = {
        "nurture": generate_nurture_html,
        "nature": generate_nurture_html,
        "tokyo-night": generate_tokyo_night_html,
        "cyberpunk": generate_cyberpunk_html,
        "synthwave-84": generate_synthwave_html,
        "catppuccin-mocha": generate_catppuccin_html,
        "dracula": generate_dracula_html,
        "oled-crimson": generate_oled_crimson_html,
        "cyber-blossom": generate_cyber_blossom_html,
        "cyber blossom": generate_cyber_blossom_html,
        "abyssal-leviathan": generate_abyssal_leviathan_html,
        "abyssal": generate_abyssal_leviathan_html,
        "analog-1984": generate_analog_1984_html,
        "analog": generate_analog_1984_html,
        "cyberdeck": generate_cyberdeck_html,
        "solaris": generate_solaris_html,
    }
    generator_fn = mapping.get(preset_key.lower().replace("_", "-") if preset_key else "")
    return generator_fn() if generator_fn else None


