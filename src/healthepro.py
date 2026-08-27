from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

import requests

LOG = logging.getLogger(__name__)
BASE = "https://menus.healthepro.com/api"


class HealthEProError(RuntimeError):
    pass


@dataclass(frozen=True)
class HealthEProConfig:
    organization_id: int = 2221
    site_id: int = 14158
    menu_id: int = 125015


class HealthEProClient:
    def __init__(self, config: HealthEProConfig, timeout: int = 30) -> None:
        self.config = config
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "weekly-menu-bot/1.0"})

    def _get_json(self, url: str) -> Any:
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                last_exc = exc
                LOG.warning("Health-e Pro request failed (attempt %s/3): %s", attempt + 1, exc)
        raise HealthEProError(f"Unable to fetch Health-e Pro data: {last_exc}")

    def date_overwrites(self, year: int, month: int) -> list[dict[str, Any]]:
        url = (
            f"{BASE}/organizations/{self.config.organization_id}/menus/"
            f"{self.config.menu_id}/year/{year}/month/{month}/date_overwrites"
        )
        payload = self._get_json(url)
        data = payload.get("data", payload) if isinstance(payload, dict) else payload
        if not isinstance(data, list):
            raise HealthEProError("Unexpected date_overwrites response shape")
        return [x for x in data if isinstance(x, dict)]

    def recipes(self, start_date: date, end_date: date) -> Any:
        url = (
            f"{BASE}/organizations/{self.config.organization_id}/menus/{self.config.menu_id}"
            f"/start_date/{start_date.isoformat()}/end_date/{end_date.isoformat()}/recipes/"
        )
        return self._get_json(url)


def decode_setting(value: Any) -> dict[str, Any]:
    """Health-e Pro stores each daily setting as JSON encoded inside a string."""
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        LOG.warning("Could not decode a date_overwrite setting JSON string")
        return {}
    return decoded if isinstance(decoded, dict) else {}


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)
