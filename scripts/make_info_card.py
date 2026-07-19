#!/usr/bin/env python3
"""
make_info_card.py — hand-authored neofetch-style SVG info panel.
Each line fades + slides in on a short stagger, like it's printing next to
the ASCII portrait.

Env:
    STATIC=1   emit a frozen (no-animation) frame for local Quick Look previews.

Usage:
    python scripts/make_info_card.py            # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py    # writes info-card.svg (frozen)
"""
import os

# ---- Edit this block to update the card's content ----
USERNAME = "deadbeast38030"
TITLE = f"{USERNAME}@github"

FIELDS = [
    ("Now", "Building Cultivixx — AI-powered urban gardening app"),
    ("Prev", "Founder & CEO, Masun Technology"),
    ("Stack", "Python, Java, React, Node.js, Gemini API"),
    ("Highlights", "MSME + Startup India registered ventures"),
    ("Highlights", "Dean's certificate — hackathon AI farming assistant"),
    ("Studying", "B.Tech CSE/AI, Centurion University"),
]
# --------------------------------------------------------

WIDTH = 490
LINE_H = 28
PAD_TOP = 56
PAD_X = 20
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BORDER_COLOR = "#30363d"
BG_COLOR = "#0d1117"
TITLEBAR_COLOR = "#161b22"

STATIC = os.environ.get("STATIC") == "1"


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg() -> str:
    height = PAD_TOP + LINE_H * len(FIELDS) + 24
    lines_svg = []

    for i, (key, val) in enumerate(FIELDS):
        y = PAD_TOP + i * LINE_H
        key_safe = escape_xml(key)
        val_safe = escape_xml(val)

        if STATIC:
            opacity_attrs = 'opacity="1"'
            transform = ""
            anim = ""
        else:
            begin = round(0.15 * i, 2)
            opacity_attrs = 'opacity="0"'
            transform = f'transform="translate(-12,0)"'
            anim = f"""
        <animate attributeName="opacity" from="0" to="1"
                 begin="{begin}s" dur="0.35s" fill="freeze" />
        <animateTransform attributeName="transform" type="translate"
                 from="-12 0" to="0 0" begin="{begin}s" dur="0.35s" fill="freeze" />"""

        lines_svg.append(f"""
  <g {opacity_attrs} {transform}>{anim}
    <text x="{PAD_X}" y="{y}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
          font-size="14" font-weight="600" fill="{KEY_COLOR}">{key_safe}</text>
    <text x="{PAD_X + 110}" y="{y}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
          font-size="14" fill="{VAL_COLOR}">{val_safe}</text>
  </g>""")

    body = "".join(lines_svg)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"
     viewBox="0 0 {WIDTH} {height}">
  <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="8" fill="{BG_COLOR}"
        stroke="{BORDER_COLOR}" stroke-width="1"/>
  <rect x="0" y="0" width="{WIDTH}" height="34" rx="8" fill="{TITLEBAR_COLOR}"/>
  <rect x="0" y="20" width="{WIDTH}" height="14" fill="{TITLEBAR_COLOR}"/>
  <circle cx="20" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="40" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="60" cy="17" r="6" fill="#27c93f"/>
  <text x="{WIDTH/2}" y="21" text-anchor="middle" font-family="ui-monospace, monospace"
        font-size="12" fill="#8b949e">{escape_xml(TITLE)}</text>
  <line x1="{PAD_X}" y1="42" x2="{WIDTH - PAD_X}" y2="42" stroke="{BORDER_COLOR}" stroke-width="1"/>
  {body}
</svg>
"""


def main():
    svg = build_svg()
    with open("info-card.svg", "w") as f:
        f.write(svg)
    print("Wrote info-card.svg" + (" (static)" if STATIC else ""))


if __name__ == "__main__":
    main()
