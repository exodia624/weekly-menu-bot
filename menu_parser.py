from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from .healthepro import decode_setting, iter_dicts

LOG = logging.getLogger(__name__)


@dataclass
class MenuDay:
    day: date
    no_school: bool = False
    note: str | None = None
    categories: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class WeeklyMenu:
    monday: date
    days: list[MenuDay]


def recipe_name_index(payload: Any) -> dict[str, str]:
    """Build a loose ID -> name map without depending on one exact recipe schema."""
    out: dict[str, str] = {}
    for obj in iter_dicts(payload):
        name = obj.get("name") or obj.get("recipe_name") or obj.get("display_name")
        if not isinstance(name, str) or not name.strip():
            continue
        for key in ("id", "recipe_id", "item_id"):
            if key in obj and obj[key] is not None:
                out[str(obj[key])] = name.strip()
    return out


def _is_no_school(setting: dict[str, Any]) -> tuple[bool, str | None]:
    days_off = setting.get("days_off")
    if isinstance(days_off, dict):
        days_off = [days_off]
    if isinstance(days_off, list):
        for entry in days_off:
            if not isinstance(entry, dict):
                continue
            status = entry.get("status")
            if status in (1, "1", True, "true", "True"):
                return True, str(entry.get("description") or "No school")
    return False, None


def _item_name(obj: dict[str, Any], recipes: dict[str, str]) -> str | None:
    # Category rows also have a name, so the caller checks type first.
    for key in ("display_name", "recipe_name"):
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # Sometimes current_display carries the item name directly.
    name = obj.get("name")
    if isinstance(name, str) and name.strip() and obj.get("type") != "category":
        return name.strip()

    # Otherwise resolve common ID fields against the recipes endpoint.
    for key in ("item", "id", "recipe_id", "item_id"):
        val = obj.get(key)
        if val is not None and str(val) in recipes:
            return recipes[str(val)]
    return None


def parse_current_display(setting: dict[str, Any], recipes: dict[str, str]) -> dict[str, list[str]]:
    display = setting.get("current_display")
    if not isinstance(display, list):
        return {}

    categories: dict[str, list[str]] = {}
    current = "Other"
    categories[current] = []

    for entry in display:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("type", "")).lower() == "category":
            current = str(entry.get("name") or entry.get("item") or "Other").strip()
            categories.setdefault(current, [])
            continue
        name = _item_name(entry, recipes)
        if name and name not in categories.setdefault(current, []):
            categories[current].append(name)

    return {k: v for k, v in categories.items() if v}


def parse_week(
    monday: date,
    overwrite_rows: list[dict[str, Any]],
    recipes_payload: Any,
) -> WeeklyMenu:
    recipes = recipe_name_index(recipes_payload)
    by_day: dict[str, dict[str, Any]] = {}
    for row in overwrite_rows:
        day = row.get("day")
        if isinstance(day, str):
            by_day[day[:10]] = row

    days: list[MenuDay] = []
    for offset in range(5):
        d = monday + timedelta(days=offset)
        row = by_day.get(d.isoformat(), {})
        setting = decode_setting(row.get("setting") or row.get("setting_original"))
        no_school, note = _is_no_school(setting)
        categories = {} if no_school else parse_current_display(setting, recipes)
        days.append(MenuDay(day=d, no_school=no_school, note=note, categories=categories))
    return WeeklyMenu(monday=monday, days=days)
