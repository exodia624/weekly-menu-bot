# Weekly Menu Bot

An automated system that retrieves my school's online lunch menu and transforms the weekly menu data into polished JPG graphics ready to be uploaded each week.

The project was developed in part for my community service group's effort to reduce food waste on campus. By making weekly lunch options easier for students to see ahead of time, the project aims to help students choose the correct lunch line and avoid taking meals they do not want that may ultimately be thrown away.

## Overview

Updating a weekly school lunch menu manually involves checking menu data, copying items into graphics, updating dates, formatting each slide, and preparing the final post.

**Weekly Menu Bot automates that process.**

The pipeline:

**Health-e Pro → Python → Dynamic Graphics → GitHub Actions → Instagram**

Each run generates:

1. Weekly cover
2. Monday menu
3. Tuesday menu
4. Wednesday menu
5. Thursday menu
6. Friday menu

The graphics use reusable Canva-designed backgrounds while Python dynamically inserts the current menu information.

## Features

### Automated Menu Retrieval

The bot retrieves the upcoming week's lunch information from Health-e Pro and automatically resolves menu items and categories.

It supports categories such as:

- Lunch Entree
- Vegetables
- Fruit
- Grains
- Desserts
- Milk
- Miscellaneous
- Condiments

The parser also detects days when school is not in session.

### Dynamic Graphic Generation

Menu slides are rendered with Python and Pillow using reusable 1080 × 1350 templates.

The renderer automatically handles:

- Weekday and date placement
- Menu categories
- Bullet-pointed food items
- Text wrapping
- Dynamic font sizing
- Variable menu lengths
- No-school days
- Missing/unpublished menus

This allows the same templates to be reused every week without manually editing the graphics.

### Weekly Food-Waste Facts

Each cover includes a quantitative food-waste fact.

A deterministic weekly randomizer selects from a collection of facts, meaning:

- Different weeks can receive different facts
- Regenerating the same week produces the same fact
- Results remain reproducible during testing

### Automated Carousel Assembly

Generated images use numbered filenames:

```text
01-cover.jpg
02-monday.jpg
03-tuesday.jpg
04-wednesday.jpg
05-thursday.jpg
06-friday.jpg
```

The publishing pipeline also explicitly sorts these files before creating the carousel, ensuring that the cover is always first and the weekdays remain in chronological order.

### GitHub Actions Automation

GitHub Actions handles the automated workflow:

```text
Retrieve menu data
        ↓
Parse menu
        ↓
Run tests
        ↓
Generate graphics
        ↓
Create preview artifact
        ↓
Publish carousel
```

Preview runs can be performed without Instagram credentials, allowing graphics and menu data to be checked before anything is published.

## Technology

| Technology | Purpose |
|---|---|
| Python | Core automation |
| Pillow | Dynamic image rendering |
| Requests | Health-e Pro and API communication |
| GitHub Actions | Automated execution and testing |
| Pytest | Parser testing |
| Meta Graph API | Instagram carousel publishing |
| Canva | Original graphic/template design |

## Project Structure

```text
weekly-menu-bot/
│
├── .github/
│   └── workflows/
│       └── weekly-menu.yml
│
├── assets/
│   ├── backgrounds/
│   │   ├── cover.png
│   │   ├── monday.png
│   │   ├── tuesday.png
│   │   ├── wednesday.png
│   │   ├── thursday.png
│   │   └── friday.png
│   │
│   └── source/
│
├── generated/
│   ├── 01-cover.jpg
│   ├── 02-monday.jpg
│   ├── 03-tuesday.jpg
│   ├── 04-wednesday.jpg
│   ├── 05-thursday.jpg
│   ├── 06-friday.jpg
│   └── menu.json
│
├── src/
│   ├── healthepro.py
│   ├── instagram.py
│   ├── main.py
│   ├── menu_parser.py
│   └── renderer.py
│
├── tests/
│   └── test_menu_parser.py
│
├── .env.example
├── requirements.txt
└── README.md
```

## How It Works

### 1. Determine the Week

The program identifies the upcoming Monday through Friday.

A specific Monday can also be supplied for testing.

### 2. Retrieve Menu Data

The bot communicates with Health-e Pro to retrieve the menu information required for the selected week.

Configuration identifiers are intentionally omitted from this README.

### 3. Parse the Menu

Health-e Pro's daily settings contain structured menu information.

The parser:

- Identifies menu categories
- Resolves recipe IDs into names
- Removes duplicate items
- Organizes meals by day
- Detects no-school days

The resulting structured menu is also written to:

```text
generated/menu.json
```

### 4. Render the Graphics

Pillow combines the menu information with the corresponding background template.

The renderer adjusts text size and wrapping to accommodate differences in the number and length of menu items each day.

### 5. Assemble the Carousel

The final carousel is explicitly ordered:

```text
Cover
Monday
Tuesday
Wednesday
Thursday
Friday
```

### 6. Run Through GitHub Actions

The entire process can run remotely through GitHub Actions, meaning the automation does not require a computer to remain running.

## Running Locally

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt pytest
```

Run the tests:

```bash
pytest -q
```

Generate a preview:

```bash
WEEK_START=YYYY-MM-DD DRY_RUN=true python -m src.main
```

The selected date must be a Monday.

Generated graphics will appear inside:

```text
generated/
```

## Testing With GitHub Actions

The workflow can also be triggered manually:

1. Open **Actions**
2. Select **Weekly Lunch Menu**
3. Select **Run workflow**
4. Enter an optional Monday
5. Leave publishing disabled
6. Run the workflow
7. Download the generated preview artifact

This allows the complete pipeline to be tested without publishing anything publicly.

## Instagram Publishing

The project contains support for publishing the generated images as an Instagram carousel through Meta's API.

Credentials are stored as GitHub Actions secrets rather than committed to the repository:

```text
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_USER_ID
```

Access tokens and account identifiers should never be committed to the repository.

The workflow is designed so generation can be tested independently before live publishing is enabled.

## Health-e Pro Configuration

The deployment uses organization-, site-, and menu-specific identifiers.

These values have been intentionally omitted from the public documentation.

```text
Organization ID: [hidden]
Site ID:         [hidden]
Menu ID:         [hidden]
```

Menu:

```text
2026-27 HS Lunch
```

## Design Considerations

One challenge was that menu length changes significantly from day to day.

Using fixed-size text could either create excessive empty space on short menus or cause longer menus to overlap decorative elements.

The renderer therefore measures the menu before drawing it and selects an appropriate font size and spacing based on the available vertical space.

The templates and rendering coordinates were also designed to preserve the original decorative artwork while keeping dynamically generated information readable.

## Reliability & Safety

Several safeguards are built into the project:

- Instagram publishing can be disabled with `DRY_RUN`
- Scheduled runs currently support preview-first operation
- Menu parsing handles missing data
- No-school days are detected automatically
- API requests retry after temporary failures
- Generated carousel order is explicitly enforced
- Automated parser tests run before image generation
- Instagram credentials are kept outside the source code

## Future Improvements

Potential improvements include:

- Fully enabling scheduled Instagram publishing
- Additional tests for unusual Health-e Pro responses
- Automatic validation of generated graphics
- Expanded food-waste fact sources
- Improved monitoring and failure notifications
- Additional menu/template configurations

## Why I Built This

At my school, different lunch lines serve different meals, and students may not know what each line is serving until they receive their food. This can result in students getting meals they did not want and throwing them away.

As part of my community service group's efforts to reduce food waste on campus, I wanted to make the weekly lunch menu more accessible to students. Instead of manually checking the school's menu website and creating new graphics every week, I built a system that retrieves the menu data and automatically converts it into consistent, social-media-ready graphics.

By automating the process, the menus can be shared with students each week with minimal manual work, helping students know their lunch options before getting in line and supporting our broader goal of reducing avoidable food waste.

The project combines **software automation, web data retrieval, graphic design, and community service** to address the practical problem of food waste at my school.