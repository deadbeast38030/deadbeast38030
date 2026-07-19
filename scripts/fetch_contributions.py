#!/usr/bin/env python3
"""
fetch_contributions.py — pull real contribution-calendar data with no GitHub
token and no GraphQL API.

GitHub serves the profile's contribution calendar as a public HTML fragment
at:
    https://github.com/users/<username>/contributions

This is the same fragment the profile page itself renders. Each day is a
<td>/<rect> with a "data-date", a "data-level" (0-4), and a title/tooltip
with the contribution count. We scrape it with requests + BeautifulSoup and
write data/contributions.json with the raw days plus a few derived stats.

Usage:
    python scripts/fetch_contributions.py [username]
"""
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME_DEFAULT = "deadbeast38030"
UA = "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as either a <td class="ContributionCalendar-day">
    # (data-date/data-level attrs) or a <rect> depending on markup version.
    cells = soup.select("td.ContributionCalendar-day") or soup.select(
        "rect.ContributionCalendar-day"
    )

    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue
        count = 0
        tooltip_id = cell.get("id")
        # Counts live in a sibling <tool-tip>/title referencing this cell's id.
        if tooltip_id:
            tip = soup.find(attrs={"for": tooltip_id}) or soup.find(
                "tool-tip", attrs={"id": tooltip_id}
            )
            if tip:
                m = re.search(r"([\d,]+)\s+contribution", tip.get_text())
                if m:
                    count = int(m.group(1).replace(",", ""))
        days.append(
            {"date": date, "level": int(level) if level is not None else 0, "count": count}
        )

    return days


def derive_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    days_sorted = sorted(days, key=lambda d: d["date"])
    total = sum(d["count"] for d in days_sorted)

    current_streak = 0
    for d in reversed(days_sorted):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days_sorted:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days_sorted, key=lambda d: d["count"])

    monthly = {}
    for d in days_sorted:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME_DEFAULT
    print(f"Fetching contribution calendar for {username}...")
    html = fetch_html(username)
    days = parse_days(html)

    if not days:
        print("WARNING: parsed 0 days — GitHub may have changed its markup. "
              "Inspect the raw HTML and update the selectors in parse_days().")

    stats = derive_stats(days)
    out = {"username": username, "days": days, "stats": stats}

    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote data/contributions.json ({len(days)} days, "
          f"{stats.get('total_last_year', 0)} total contributions)")


if __name__ == "__main__":
    main()
