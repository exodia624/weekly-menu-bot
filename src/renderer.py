from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from .menu_parser import MenuDay, WeeklyMenu


ROOT = Path(__file__).resolve().parents[1]
BACKGROUNDS = ROOT / "assets" / "backgrounds"
GENERATED = ROOT / "generated"

GREEN = (39, 112, 66)
ORANGE = (196, 96, 34)
CREAM = (255, 248, 238)


def _font(
    size: int,
    bold: bool = True,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass

    return ImageFont.load_default()


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start: int,
    minimum: int = 24,
) -> ImageFont.ImageFont:
    for size in range(start, minimum - 1, -2):
        font = _font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            return font

    return _font(minimum)


def _wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    width: int,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    lines: list[str] = []
    line = words[0]

    for word in words[1:]:
        trial = f"{line} {word}"
        bbox = draw.textbbox((0, 0), trial, font=font)

        if bbox[2] - bbox[0] <= width:
            line = trial
        else:
            lines.append(line)
            line = word

    lines.append(line)

    return lines


def _draw_bullets(
    draw: ImageDraw.ImageDraw,
    items: Iterable[str],
    x: int,
    y: int,
    width: int,
    size: int = 29,
) -> int:
    font = _font(size)
    bullet_indent = 34
    line_gap = 7

    for item in items:
        lines = _wrap(
            draw,
            item,
            font,
            width - bullet_indent,
        )

        if not lines:
            continue

        draw.text(
            (x, y),
            "•",
            font=font,
            fill=ORANGE,
        )

        for line in lines:
            draw.text(
                (x + bullet_indent, y),
                line,
                font=font,
                fill=ORANGE,
            )

            y += size + 4

        y += line_gap

    return y


def _category_order(
    categories: dict[str, list[str]],
) -> list[tuple[str, list[str]]]:
    preferred = [
        "Lunch Entree",
        "Vegetables",
        "Fruit",
    ]

    result: list[tuple[str, list[str]]] = []
    used: set[str] = set()

    for preferred_name in preferred:
        for key, value in categories.items():
            if key.lower() == preferred_name.lower():
                result.append((key, value))
                used.add(key)

    for key, value in categories.items():
        if key not in used:
            result.append((key, value))

    return result


def render_cover(menu: WeeklyMenu) -> Path:
    img = Image.open(
        BACKGROUNDS / "cover.png"
    ).convert("RGB")

    draw = ImageDraw.Draw(img)

    friday = menu.days[-1].day

    label = (
        f"{menu.monday:%m/%d} - "
        f"{friday:%m/%d}"
    )

    # Remove the Canva placeholder date.
    draw.rectangle(
        (250, 285, 835, 385),
        fill=CREAM,
    )

    font = _fit_font(
        draw,
        label,
        max_width=580,
        start=68,
        minimum=42,
    )

    bbox = draw.textbbox(
        (0, 0),
        label,
        font=font,
    )

    text_width = bbox[2] - bbox[0]

    x = (img.width - text_width) // 2

    draw.text(
        (x, 292),
        label,
        font=font,
        fill=GREEN,
    )

    path = GENERATED / "01-cover.jpg"

    img.save(
        path,
        "JPEG",
        quality=94,
    )

    return path


def render_day(
    day: MenuDay,
    index: int,
) -> Path:
    day_name = day.day.strftime("%A").lower()

    img = Image.open(
        BACKGROUNDS / f"{day_name}.png"
    ).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Keep the Canva weekday lettering.
    # Only replace 00/00 with the real date.
    date_text = f"{day.day:%m/%d}"

    draw.rectangle(
        (600, 85, 990, 215),
        fill=CREAM,
    )

    date_font = _fit_font(
        draw,
        date_text,
        max_width=340,
        start=68,
        minimum=42,
    )

    draw.text(
        (610, 92),
        date_text,
        font=date_font,
        fill=GREEN,
    )

    if day.no_school:
        note = (
            day.note
            or "No school"
        ).upper()

        font = _fit_font(
            draw,
            note,
            max_width=700,
            start=52,
            minimum=34,
        )

        draw.text(
            (105, 300),
            note,
            font=font,
            fill=ORANGE,
        )

    elif not day.categories:
        draw.text(
            (105, 300),
            "MENU NOT PUBLISHED YET",
            font=_font(38),
            fill=ORANGE,
        )

    else:
        y = 275

        for category, items in _category_order(
            day.categories
        ):
            heading = category.upper()

            draw.text(
                (105, y),
                heading,
                font=_font(36),
                fill=ORANGE,
            )

            y += 48

            y = _draw_bullets(
                draw,
                items,
                x=125,
                y=y,
                width=650,
                size=28,
            )

            y += 14

            if y > 1230:
                break

    path = GENERATED / (
        f"{index:02d}-{day_name}.jpg"
    )

    img.save(
        path,
        "JPEG",
        quality=94,
    )

    return path


def render_week(
    menu: WeeklyMenu,
) -> list[Path]:
    GENERATED.mkdir(exist_ok=True)

    for old in GENERATED.glob("*.jpg"):
        old.unlink()

    paths = [
        render_cover(menu)
    ]

    for i, day in enumerate(
        menu.days,
        start=2,
    ):
        paths.append(
            render_day(day, i)
        )

    return paths
