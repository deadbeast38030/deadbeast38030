#!/usr/bin/env python3
"""
make_ascii_svg.py — convert source-prepped.png into a self-typing,
monochrome ASCII-art SVG (avi-ascii.svg / here: deadbeast-ascii.svg).

Design choices (deliberate):
- Monochrome: one light-gray fill. Per-character rainbow coloring is what
  makes most ASCII portraits look noisy instead of clean.
- High contrast: a busy/bright background washes out to the space glyph
  ' ', so only the subject actually prints.
- Row-by-row wipe animation via SMIL <animate> on a clipPath, staggered
  top-to-bottom. Prints once and freezes (no infinite loop).

Usage:
    python scripts/make_ascii_svg.py [source-prepped.png] [output.svg]
"""
import sys

from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53
CHAR_W = 7
CHAR_H = 13
FILL = "#c9d1d9"  # GitHub dark-mode-friendly light gray
BG = "transparent"


def image_to_ascii_rows(img: Image.Image, cols: int, rows: int) -> list[str]:
    gray = img.convert("L").resize((cols, rows))
    pixels = gray.load()
    ramp_len = len(RAMP) - 1
    lines = []
    for y in range(rows):
        row_chars = []
        for x in range(cols):
            brightness = pixels[x, y] / 255.0  # 1.0 = white/bright, 0.0 = black
            idx = int((1.0 - brightness) * ramp_len)
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    row_stagger = 0.045  # seconds between each row's wipe starting
    wipe_dur = 0.5

    row_groups = []
    for i, row in enumerate(rows):
        row = row.rstrip() or " "
        safe_row = escape_xml(row)
        y = (i + 1) * CHAR_H
        clip_id = f"clip{i}"
        begin = round(i * row_stagger, 3)
        row_groups.append(f"""
  <clipPath id="{clip_id}">
    <rect x="0" y="{y - CHAR_H}" width="0" height="{CHAR_H}">
      <animate attributeName="width" from="0" to="{width}"
               begin="{begin}s" dur="{wipe_dur}s" fill="freeze" />
    </rect>
  </clipPath>
  <text x="0" y="{y - 2}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
        font-size="{CHAR_H}" fill="{FILL}" clip-path="url(#{clip_id})"
        xml:space="preserve">{safe_row}</text>""")

    body = "".join(row_groups)
    total_dur = round(len(rows) * row_stagger + wipe_dur, 2)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="{BG}" />
  {body}
</svg>
"""


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "deadbeast-ascii.svg"

    img = Image.open(src)
    rows = image_to_ascii_rows(img, COLS, ROWS)
    svg = build_svg(rows)

    with open(out, "w") as f:
        f.write(svg)
    print(f"Wrote {out} ({COLS}x{ROWS} grid, {len(rows)} animated rows)")


if __name__ == "__main__":
    main()
