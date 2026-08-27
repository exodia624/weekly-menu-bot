from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from .healthepro import HealthEProClient, HealthEProConfig
from .instagram import publish_carousel, raw_github_urls
from .menu_parser import WeeklyMenu, parse_week
from .renderer import render_week

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(levelname)s %(message)s")
LOG = logging.getLogger("weekly-menu-bot")
ROOT = Path(__file__).resolve().parents[1]


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def target_monday(today: date | None = None) -> date:
    override = os.getenv("WEEK_START", "").strip()
    if override:
        d = date.fromisoformat(override)
        if d.weekday() != 0:
            raise ValueError("WEEK_START must be a Monday")
        return d
    today = today or date.today()
    # Always target the next Monday. This is ideal for a Sunday scheduled post.
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def months_touched(start: date, end: date) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        out.append((y, m))
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return out


def serialize(menu: WeeklyMenu) -> dict:
    return {
        "week_start": menu.monday.isoformat(),
        "days": [
            {
                "date": d.day.isoformat(),
                "weekday": d.day.strftime("%A"),
                "no_school": d.no_school,
                "note": d.note,
                "categories": d.categories,
            }
            for d in menu.days
        ],
    }


def caption(menu: WeeklyMenu) -> str:
    prefix = os.getenv("CAPTION_PREFIX", "GAWHS Weekly Lunch Menu")
    friday = menu.days[-1].day
    return f"{prefix} — {menu.monday:%B %-d}–{friday:%B %-d}"


def main() -> None:
    monday = target_monday()
    friday = monday + timedelta(days=4)
    cfg = HealthEProConfig(
        organization_id=int(os.getenv("HEP_ORG_ID", "2221")),
        site_id=int(os.getenv("HEP_SITE_ID", "14158")),
        menu_id=int(os.getenv("HEP_MENU_ID", "125015")),
    )
    client = HealthEProClient(cfg)

    overwrite_rows = []
    for year, month in months_touched(monday, friday):
        overwrite_rows.extend(client.date_overwrites(year, month))
    recipes = client.recipes(monday, friday)
    menu = parse_week(monday, overwrite_rows, recipes)

    summary = serialize(menu)
    (ROOT / "generated").mkdir(exist_ok=True)
    (ROOT / "generated" / "menu.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    paths = render_week(menu)

    LOG.info("Generated week %s through %s", monday, friday)
    for d in menu.days:
        LOG.info("%s: %s", d.day, "NO SCHOOL" if d.no_school else d.categories)

    dry_run = env_bool("DRY_RUN", True)
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
    user_id = os.getenv("INSTAGRAM_USER_ID", "").strip()
    repository = os.getenv("GITHUB_REPOSITORY", "").strip()
    ref = os.getenv("PUBLIC_IMAGE_REF", "").strip() or os.getenv("GITHUB_SHA", "").strip()

    if dry_run or not token or not user_id:
        LOG.info("DRY RUN: Instagram publishing skipped")
        return
    if not repository or not ref:
        raise RuntimeError("GITHUB_REPOSITORY and PUBLIC_IMAGE_REF/GITHUB_SHA are required for publishing")

    urls = raw_github_urls(paths, repository, ref)
    media_id = publish_carousel(urls, caption(menu), user_id, token)
    LOG.info("Instagram carousel published successfully: %s", media_id)


if __name__ == "__main__":
    main()
