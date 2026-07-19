#!/usr/bin/env python3
"""
render_heatmap_svg.py — draw data/contributions.json as the classic
53-week x 7-day calendar of rounded, colored boxes, with a diagonal
line-after-line slide-down reveal (plays once on load, then freezes).

Usage:
    python scripts/render_heatmap_svg.py
"""
import json
from datetime import datetime

PALETTE = [
    "#161b22",  # 0 - none
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4 - brightest
]

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 28
TOP_PAD = 20
BOTTOM_PAD = 46
WEEKS = 53
DAYS = 7

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data():
    with open("data/contributions.json") as f:
        return json.load(f)


def build_grid(days: list[dict]):
    """Bucket days into a week-major grid: grid[week_idx][weekday] = day dict."""
    if not days:
        return [], []

    days_sorted = sorted(days, key=lambda d: d["date"])
    first_date = datetime.strptime(days_sorted[0]["date"], "%Y-%m-%d")
    # Align so column 0 starts on the Sunday of (or before) the first day.
    start_weekday = (first_date.weekday() + 1) % 7  # convert Mon=0 -> Sun=0

    grid = [[None] * DAYS for _ in range(WEEKS)]
    month_starts = {}

    col = 0
    row = start_weekday
    for d in days_sorted:
        if col >= WEEKS:
            break
        grid[col][row] = d
        month_key = d["date"][:7]
        if month_key not in month_starts:
            month_starts[month_key] = col
        row += 1
        if row >= DAYS:
            row = 0
            col += 1

    return grid, month_starts


def build_svg(data: dict) -> str:
    days = data.get("days", [])
    stats = data.get("stats", {})
    grid, month_starts = build_grid(days)

    width = LEFT_PAD + WEEKS * CELL + 20
    height = TOP_PAD + DAYS * CELL + BOTTOM_PAD

    boxes = []
    stagger_per_diag = 0.012
    for week in range(WEEKS):
        for day in range(DAYS):
            cell = grid[week][day] if week < len(grid) else None
            level = cell["level"] if cell else 0
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = LEFT_PAD + week * CELL
            y = TOP_PAD + day * CELL
            # Diagonal stagger: cells on the same (week+day) anti-diagonal
            # animate together, sweeping top-left to bottom-right.
            begin = round((week + day) * stagger_per_diag, 3)
            date_title = cell["date"] if cell else ""
            boxes.append(f"""
    <rect x="{x}" y="-{BOX}" width="{BOX}" height="{BOX}" rx="2" fill="{color}">
      <title>{date_title}: {cell["count"] if cell else 0} contributions</title>
      <animate attributeName="y" from="-{BOX}" to="{y}"
               begin="{begin}s" dur="0.4s" fill="freeze" calcMode="spline"
               keySplines="0.2 0.8 0.2 1" />
      <animate attributeName="opacity" from="0" to="1"
               begin="{begin}s" dur="0.25s" fill="freeze" />
    </rect>""")

    month_labels = []
    for month_key, col in sorted(month_starts.items(), key=lambda kv: kv[1]):
        month_num = int(month_key.split("-")[1]) - 1
        x = LEFT_PAD + col * CELL
        month_labels.append(
            f'<text x="{x}" y="{TOP_PAD - 6}" font-family="ui-monospace, monospace" '
            f'font-size="10" fill="#8b949e">{MONTH_LABELS[month_num]}</text>'
        )

    legend_y = TOP_PAD + DAYS * CELL + 20
    legend_x = LEFT_PAD
    legend_boxes = []
    for i, color in enumerate(PALETTE):
        legend_boxes.append(
            f'<rect x="{legend_x + 34 + i * (BOX + 3)}" y="{legend_y - BOX + 2}" '
            f'width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>'
        )

    total = stats.get("total_last_year", 0)
    streak = stats.get("longest_streak", 0)

    footer = (
        f'<text x="{legend_x}" y="{legend_y + 4}" font-family="ui-monospace, monospace" '
        f'font-size="11" fill="#8b949e">Less</text>'
        + "".join(legend_boxes)
        + f'<text x="{legend_x + 34 + len(PALETTE) * (BOX + 3) + 6}" y="{legend_y + 4}" '
        f'font-family="ui-monospace, monospace" font-size="11" fill="#8b949e">More</text>'
        + f'<text x="{width - 20}" y="{legend_y + 4}" text-anchor="end" '
        f'font-family="ui-monospace, monospace" font-size="11" fill="#8b949e">'
        f'{total} contributions in the last year · {streak}-day best streak</text>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="transparent" />
  {''.join(month_labels)}
  {''.join(boxes)}
  {footer}
</svg>
"""


def main():
    data = load_data()
    svg = build_svg(data)
    with open("contrib-heatmap.svg", "w") as f:
        f.write(svg)
    print("Wrote contrib-heatmap.svg")


if __name__ == "__main__":
    main()
