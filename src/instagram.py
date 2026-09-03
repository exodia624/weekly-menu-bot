from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Sequence

import requests

LOG = logging.getLogger(__name__)
GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v23.0")
GRAPH = f"https://graph.instagram.com/{GRAPH_VERSION}"

class InstagramPublishError(RuntimeError):
    pass


def _post(path: str, data: dict[str, str]) -> dict:
    response = requests.post(f"{GRAPH}/{path}", data=data, timeout=45)
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}
    if not response.ok:
        raise InstagramPublishError(f"Meta API error {response.status_code}: {payload}")
    return payload


def publish_carousel(
    image_urls: Sequence[str],
    caption: str,
    instagram_user_id: str,
    access_token: str,
) -> str:
    if not 2 <= len(image_urls) <= 10:
        raise ValueError("Instagram carousels require 2-10 items")

    children: list[str] = []
    for url in image_urls:
        result = _post(
            f"{instagram_user_id}/media",
            {
                "image_url": url,
                "is_carousel_item": "true",
                "access_token": access_token,
            },
        )
        children.append(str(result["id"]))

    # Give Meta a moment to ingest all remote images.
    time.sleep(8)
    parent = _post(
        f"{instagram_user_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": access_token,
        },
    )
    time.sleep(5)
    published = _post(
        f"{instagram_user_id}/media_publish",
        {"creation_id": str(parent["id"]), "access_token": access_token},
    )
    return str(published["id"])


def raw_github_urls(paths: Sequence[Path], repository: str, ref: str) -> list[str]:
    return [f"https://raw.githubusercontent.com/{repository}/{ref}/generated/{p.name}" for p in paths]
