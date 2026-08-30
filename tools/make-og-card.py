#!/usr/bin/env python3
"""Render assets/og-card.png (1200x630 Open Graph card) for mixlet.app.

Needs rsvg-convert and ImageMagick `convert` (MacPorts: librsvg, ImageMagick).
Run:  python3 tools/make-og-card.py
"""
import base64, pathlib, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ART = ROOT / "assets/sirmix_photographic_alone_tp_512_ndx.png"

art_b64 = base64.b64encode(ART.read_bytes()).decode()

BG      = "#f6f0e4"
INK     = "#2b2418"
MUTED   = "#6d5e4a"
ACCENT  = "#c06b3e"
BLUE    = "#4f86c6"
CHIPBG  = "#eee4d2"

FONT = "Avenir Next, Gill Sans, Helvetica Neue, sans-serif"

# ---- art geometry -----------------------------------------------------------
AW, AH = 512, 512
art_h = 488
art_w = art_h * AW / AH
art_x = 1200 - art_w - 84
art_y = 92

cx = art_x + art_w / 2
cy = art_y + art_h / 2 + 4

# ---- chips ------------------------------------------------------------------
CHIP_FS = 19
CHIP_LS = 1.6
CHIP_PAD = 21
CHIP_H = 46
CHIP_Y = 432
CHIP_GAP = 12

def chip_width(label):
    # small-caps-ish estimate for Avenir Next demi at CHIP_FS
    w = 0.0
    for ch in label:
        if ch in "IJl.·1 ":
            w += 0.34
        elif ch in "MW⌘":
            w += 0.92
        elif ch.isupper():
            w += 0.66
        else:
            w += 0.60
    return w * CHIP_FS + CHIP_LS * len(label) + CHIP_PAD * 2

chips = ["Mini Player", "⌘G Mix It", "Resume"]

chip_svg = []
x = 72
for label in chips:
    w = chip_width(label)
    chip_svg.append(
        f'<rect x="{x:.1f}" y="{CHIP_Y}" width="{w:.1f}" height="{CHIP_H}" rx="{CHIP_H/2}" '
        f'fill="{CHIPBG}"/>'
        f'<text x="{x + w/2:.1f}" y="{CHIP_Y + 30}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{CHIP_FS}" font-weight="600" letter-spacing="{CHIP_LS}" '
        f'font-variant="small-caps" fill="{BLUE}">{label}</text>'
    )
    x += w + CHIP_GAP

# ---- confetti ---------------------------------------------------------------
dots = [
    (648, 116, 7, ACCENT, .50), (700, 74, 4, BLUE, .50),
    (1152, 246, 9, ACCENT, .38), (1104, 168, 5, BLUE, .45),
    (612, 528, 8, ACCENT, .28), (1128, 566, 6, BLUE, .38),
    (592, 336, 5, ACCENT, .28), (1176, 430, 5, ACCENT, .30),
]
dot_svg = "".join(
    f'<circle cx="{a}" cy="{b}" r="{r}" fill="{c}" opacity="{o}"/>' for a, b, r, c, o in dots
)

# ---- floating notes + waveform ---------------------------------------------
# (x, y, size, rotation, opacity, glyph)
notes = [
    (628, 214, 58, -14, .62, "\u266b"),
    (598, 244, 38, 10, .38, "\u266a"),
    (668, 132, 34, -8, .40, "\u266a"),
    (1108, 196, 52, 12, .58, "\u266b"),
    (1150, 300, 36, -10, .40, "\u266a"),
    (1092, 108, 32, 16, .34, "\u266a"),
]
note_svg = "".join(
    f'<text x="{x}" y="{y}" font-size="{fs}" fill="{BLUE}" opacity="{o}" '
    f'transform="rotate({rot} {x} {y})">{g}</text>'
    for x, y, fs, rot, o, g in notes
)

# little equalizer bars flanking the character
def bars(x0, heights, up=True):
    out = []
    for i, h in enumerate(heights):
        x = x0 + i * 13
        y = cy + 46 - h / 2
        out.append(f'<rect x="{x}" y="{y:.1f}" width="7" height="{h}" rx="3.5" '
                   f'fill="{BLUE}" opacity="{0.24 + 0.07 * (i % 3)}"/>')
    return "".join(out)

bar_svg = bars(566, [26, 52, 38, 68, 30]) + bars(1116, [30, 66, 40, 54, 24])

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="paper" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="#fdf8ef"/>
      <stop offset="1" stop-color="#f2e9d8"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#7fabe2" stop-opacity="0.30"/>
      <stop offset="0.45" stop-color="#93b9e7" stop-opacity="0.20"/>
      <stop offset="0.80" stop-color="#a8c6ea" stop-opacity="0.07"/>
      <stop offset="1" stop-color="#a8c6ea" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="shadow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#6d5e4a" stop-opacity="0.18"/>
      <stop offset="0.55" stop-color="#6d5e4a" stop-opacity="0.10"/>
      <stop offset="1" stop-color="#6d5e4a" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1200" height="630" fill="{BG}"/>
  <rect width="1200" height="630" fill="url(#paper)"/>

  <!-- vinyl groove rings behind the character -->
  <g fill="none" stroke="{ACCENT}" stroke-opacity="0.13">
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="304" stroke-width="2"/>
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="252" stroke-width="2"/>
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="200" stroke-width="2"/>
  </g>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="296" fill="url(#glow)"/>

  {dot_svg}
  {bar_svg}
  {note_svg}

  <!-- eyebrow -->
  <text x="72" y="132" font-family="{FONT}" font-size="20" font-weight="600"
        letter-spacing="3.2" font-variant="small-caps" fill="{ACCENT}">Free for macOS</text>

  <!-- wordmark -->
  <text x="68" y="262" font-family="{FONT}" font-size="118" font-weight="600"
        letter-spacing="1.5" fill="{INK}">Mixlet</text>

  <!-- subtitle -->
  <text x="72" y="324" font-family="{FONT}" font-size="31" fill="{MUTED}">A mini player for YouTube Music</text>
  <text x="72" y="368" font-family="{FONT}" font-size="31" fill="{MUTED}">that lives on your Mac.</text>

  <!-- chips -->
  {"".join(chip_svg)}

  <!-- footer -->
  <text x="72" y="562" font-family="{FONT}" font-size="25" font-weight="600"
        letter-spacing="0.4" fill="{ACCENT}">mixlet.app</text>

  <!-- character -->
  <ellipse cx="{cx:.1f}" cy="{art_y + art_h - 6}" rx="{art_w * 0.40:.1f}" ry="26" fill="url(#shadow)"/>
  <image x="{art_x:.1f}" y="{art_y}" width="{art_w:.1f}" height="{art_h}"
         xlink:href="data:image/png;base64,{art_b64}"/>
</svg>
'''

png_path = OUT / "og-card.png"
with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
    fh.write(svg)
    svg_path = fh.name
subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630", svg_path, "-o", str(png_path)], check=True)
# strip metadata / re-pack for a smaller file
subprocess.run(["convert", str(png_path), "-strip",
                "-define", "png:compression-level=9",
                "-define", "png:compression-filter=5", str(png_path)], check=True)
pathlib.Path(svg_path).unlink()
print("wrote", png_path)
