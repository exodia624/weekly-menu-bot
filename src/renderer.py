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

DATE_BOXES = {
    "monday": (610, 78, 990, 220),
    "tuesday": (625, 78, 990, 220),
    "wednesday": (645, 78, 990, 220),
    "thursday": (640, 78, 990, 220),
    "friday": (520, 78, 990, 220),
}


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

        if bbox[2] - bbox[0] <= max_width:
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
    size: int,
    line_gap: int,
) -> int:
    font = _font(size)
    bullet_indent = max(24, size + 3)
    line_height = size + 3

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

            y += line_height

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


def _measure_menu_height(
    draw: ImageDraw.ImageDraw,
    categories: list[tuple[str, list[str]]],
    width: int,
    item_size: int,
    heading_size: int,
    line_gap: int,
    category_gap: int,
) -> int:
    total = 0
    item_font = _font(item_size)
    bullet_indent = max(24, item_size + 3)
    line_height = item_size + 3

    for _, items in categories:
        total += heading_size + 12

        for item in items:
            lines = _wrap(
                draw,
                item,
                item_font,
                width - bullet_indent,
            )

            total += (
                max(1, len(lines)) * line_height
                + line_gap
            )

        total += category_gap

    return total


def _menu_style(
    draw: ImageDraw.ImageDraw,
    categories: list[tuple[str, list[str]]],
    width: int,
    available_height: int,
) -> tuple[int, int, int, int]:
    for item_size in range(28, 17, -1):
        heading_size = item_size + 8
        line_gap = max(2, item_size // 5)
        category_gap = max(5, item_size // 2)

        height = _measure_menu_height(
            draw,
            categories,
            width,
            item_size,
            heading_size,
            line_gap,
            category_gap,
        )

        if height <= available_height:
            return (
                item_size,
                heading_size,
                line_gap,
                category_gap,
            )

    return 18, 26, 2, 5


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

    # Sample the actual Canva background color
    # instead of using a guessed cream.
    background = img.getpixel((540, 410))

    draw.rectangle(
        (240, 280, 850, 390),
        fill=background,
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

    date_text = f"{day.day:%m/%d}"

    # Use the actual background color from the slide,
    # then fully cover the old 00/00 placeholder.
    background = img.getpixel((720, 245))

    draw.rectangle(
        DATE_BOXES[day_name],
        fill=background,
    )

    date_font = _fit_font(
        draw,
        date_text,
        max_width=340,
        start=68,
        minimum=42,
    )

    draw.text(
        (650, 92),
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
        categories = _category_order(
            day.categories
        )

        start_y = 275
        max_y = 1285
        content_width = 650

        (
            item_size,
            heading_size,
            line_gap,
            category_gap,
        ) = _menu_style(
            draw,
            categories,
            content_width,
            max_y - start_y,
        )

        y = start_y

        for category, items in categories:
            draw.text(
                (105, y),
                category.upper(),
                font=_font(heading_size),
                fill=ORANGE,
            )

            y += heading_size + 12

            y = _draw_bullets(
                draw,
                items,
                x=125,
                y=y,
                width=content_width,
                size=item_size,
                line_gap=line_gap,
            )

            y += category_gap

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