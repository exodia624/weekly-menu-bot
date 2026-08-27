from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from .menu_parser import MenuDay, WeeklyMenu

ROOT = Path(__file__).resolve().parents[1]
BACKGROUNDS = ROOT / "assets" / "backgrounds"
GENERATED = ROOT / "generated"
GREEN = (39, 112, 66)
ORANGE = (196, 96, 34)


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int = 24) -> ImageFont.ImageFont:
    for size in range(start, minimum - 1, -2):
        f = _font(size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_width:
            return f
    return _font(minimum)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        trial = f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=font)[2] <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def _draw_bullets(draw: ImageDraw.ImageDraw, items: Iterable[str], x: int, y: int, width: int, size: int = 31) -> int:
    font = _font(size)
    bullet_indent = 34
    line_gap = 10
    for item in items:
        lines = _wrap(draw, item, font, width - bullet_indent)
        if not lines:
            continue
        draw.text((x, y), "•", font=font, fill=ORANGE)
        for i, line in enumerate(lines):
            draw.text((x + bullet_indent, y), line, font=font, fill=ORANGE)
            y += size + 5
        y += line_gap
    return y


def _category_order(categories: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    wanted = ["Lunch Entree", "Vegetables", "Fruit"]
    result: list[tuple[str, list[str]]] = []
    used: set[str] = set()
    for w in wanted:
        for key, value in categories.items():
            if key.lower() == w.lower():
                result.append((key, value)); used.add(key)
    for key, value in categories.items():
        if key not in used:
            result.append((key, value))
    return result


def render_cover(menu: WeeklyMenu) -> Path:
    img = Image.open(BACKGROUNDS / "cover.png").convert("RGB")
    draw = ImageDraw.Draw(img)
    friday = menu.monday.replace()  # clarity
    friday = menu.days[-1].day
    label = f"{menu.monday:%m/%d} - {friday:%m/%d}"
    font = _fit_font(draw, label, 620, 70, 42)
    bbox = draw.textbbox((0, 0), label, font=font)
    x = (img.width - (bbox[2] - bbox[0])) // 2
    draw.text((x, 292), label, font=font, fill=GREEN)
    path = GENERATED / "01-cover.jpg"
    img.save(path, "JPEG", quality=94)
    return path


def render_day(day: MenuDay, index: int) -> Path:
    day_name = day.day.strftime("%A").lower()
    bg = BACKGROUNDS / f"{day_name}.png"
    img = Image.open(bg).convert("RGB")
    draw = ImageDraw.Draw(img)

    header = f"{day.day:%A}  {day.day:%m/%d}".upper()
    header_font = _fit_font(draw, header, 720, 68, 40)
    draw.text((105, 92), header, font=header_font, fill=GREEN)

    if day.no_school:
        note = (day.note or "No school").upper()
        font = _fit_font(draw, note, 650, 58, 36)
        draw.text((105, 310), note, font=font, fill=ORANGE)
    elif not day.categories:
        draw.text((105, 310), "MENU NOT PUBLISHED YET", font=_font(40), fill=ORANGE)
    else:
        y = 245
        for category, items in _category_order(day.categories):
            heading = category.upper()
            draw.text((105, y), heading, font=_font(38), fill=ORANGE)
            y += 52
            y = _draw_bullets(draw, items, 125, y, width=660, size=29)
            y += 18
            if y > 1130:
                break

    path = GENERATED / f"{index:02d}-{day_name}.jpg"
    img.save(path, "JPEG", quality=94)
    return path


def render_week(menu: WeeklyMenu) -> list[Path]:
    GENERATED.mkdir(exist_ok=True)
    for old in GENERATED.glob("*.jpg"):
        old.unlink()
    paths = [render_cover(menu)]
    for i, day in enumerate(menu.days, start=2):
        paths.append(render_day(day, i))
    return paths
