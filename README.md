# Weekly Menu Bot

Weekly Menu Bot is a project I made to automatically get my school's weekly lunch menu, organize the menu data, and turn it into Instagram graphics that can be posted for students.

I originally started working on this because of my community service group's project on reducing food waste at school. One of the problems we noticed was that students don't always know what food is being served before getting lunch. The district does have an online menu, but it isn't something that everyone checks regularly.

Our original solution was making an Instagram page and manually creating the menu posts each week. This worked, but it also meant that someone had to check the menu, copy everything over, change all the dates, and make the graphics every week. I realized that most of this process could probably be automated, which is what eventually became this project.

## What It Does

The basic process is:

```text
Health-e Pro
     ↓
Retrieve menu data
     ↓
Parse and organize the menu
     ↓
Generate Instagram graphics
     ↓
GitHub Actions
     ↓
Instagram carousel
```

For each school week, the program creates six images:

1. Weekly cover
2. Monday
3. Tuesday
4. Wednesday
5. Thursday
6. Friday

The cover also includes a food waste fact, while each weekday image shows the food being served that day.

The backgrounds were originally designed in Canva. Python then adds the changing information such as dates, weekdays, categories, and food items.

## How the Menu Data Works

My school uses Health-e Pro for its online lunch menu.

Instead of manually copying the information from the website, the program retrieves the menu data directly and then processes it in Python.

The parser organizes items into categories such as:

- Lunch Entree
- Vegetables
- Fruit
- Grains
- Desserts
- Milk
- Miscellaneous

Condiments can also exist in the original menu data, but I chose not to display them on the Instagram graphics because they aren't really useful for students trying to see what the main lunch options are.

The parser can also detect days where there is no school.

## Graphic Generation

The graphics are generated using Pillow.

Each background is 1080 × 1350, which gives the posts a vertical Instagram format. The backgrounds contain the artwork and decorations, while Python draws the actual menu information on top.

One of the harder parts of this project was that every day's menu is a different length. Some days might have only a few items while another day can have a lot more.

Because of this, the renderer can't just use the exact same text size and spacing every time. It measures the content and adjusts things such as:

- Text size
- Line wrapping
- Category spacing
- Menu item spacing
- Available vertical space

This lets the same set of backgrounds work for different weeks without me having to manually reposition everything.

The green title and weekday text uses the Chewy font, while the rest of the text uses a simpler font so longer menu items are still easy to read.

## Food Waste Facts

The cover includes a food waste fact each week.

The fact is selected based on the Monday date of that week. This means different weeks can get different facts, but generating the same week again will give the same fact instead of randomly changing it every time.

I did this mainly so previews and tests stay consistent.

## Instagram Publishing

The project can publish the six generated images as one Instagram carousel using Meta's Instagram API.

The order is always:

```text
Cover
Monday
Tuesday
Wednesday
Thursday
Friday
```

The generated files are also numbered to keep this order:

```text
01-cover.jpg
02-monday.jpg
03-tuesday.jpg
04-wednesday.jpg
05-thursday.jpg
06-friday.jpg
```

Instagram credentials are not stored in the code or uploaded to the public repository. They are stored using GitHub Actions secrets.

The Instagram secrets used by the workflow are:

```text
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_USER_ID
```

The Health-e Pro configuration values are also stored as GitHub secrets:

```text
HEP_ORG_ID
HEP_SITE_ID
HEP_MENU_ID
```

This allows the workflow to use the values without putting them directly inside the public source code.

## GitHub Actions

I use GitHub Actions so the program can run without needing my computer to stay on.

The workflow runs the main parts of the project:

```text
Run tests
    ↓
Retrieve menu
    ↓
Generate graphics
    ↓
Upload preview
    ↓
Commit public image files when publishing
    ↓
Publish Instagram carousel
```

I can also manually run the workflow without publishing anything. This lets me download the generated images and check that everything looks right before making an Instagram post.

Currently, scheduled runs are kept in preview mode while manual workflow runs can be used for publishing.

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
│   ├── fonts/
│   │   ├── Chewy-Regular.ttf
│   │   └── LICENSE.txt
│   │
│   └── source/
│       ├── cover.png
│       ├── monday.png
│       ├── tuesday.png
│       ├── wednesday.png
│       ├── thursday.png
│       └── friday.png
│
├── generated/
│   ├── .gitkeep
│   ├── 01-cover.jpg
│   ├── 02-monday.jpg
│   ├── 03-tuesday.jpg
│   ├── 04-wednesday.jpg
│   ├── 05-thursday.jpg
│   ├── 06-friday.jpg
│   └── menu.json
│
├── src/
│   ├── __init__.py
│   ├── healthepro.py
│   ├── instagram.py
│   ├── main.py
│   ├── menu_parser.py
│   └── renderer.py
│
├── tests/
│   ├── __init__.py
│   └── test_menu_parser.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Main Files

### `src/healthepro.py`

Handles requests to Health-e Pro and retrieves the menu information needed by the program.

### `src/menu_parser.py`

Takes the Health-e Pro data and converts it into a simpler structure organized by date and menu category.

It also handles things such as recipe names, duplicate items, and no-school days.

### `src/renderer.py`

Takes the parsed menu and creates the actual JPG graphics using the background templates and Pillow.

This is also where text wrapping, font sizing, positioning, colors, and the weekly food waste fact are handled.

### `src/instagram.py`

Handles communication with Instagram's API.

It creates each carousel item, creates the carousel container, and then publishes the finished carousel.

### `src/main.py`

Connects the different parts of the project together and controls the overall process.

## Running the Project

First install the dependencies:

```bash
pip install -r requirements.txt pytest
```

Run the tests with:

```bash
pytest -q
```

A specific Monday can be used to generate a week:

```bash
WEEK_START=YYYY-MM-DD DRY_RUN=true python -m src.main
```

`WEEK_START` should be a Monday.

The generated images and parsed menu information are placed in:

```text
generated/
```

## Testing Through GitHub Actions

To generate a preview without posting it:

1. Go to the **Actions** tab.
2. Select **Weekly Lunch Menu**.
3. Click **Run workflow**.
4. Enter a Monday if a specific week is needed, or leave it blank.
5. Leave **Publish to Instagram** disabled.
6. Run the workflow.
7. Download the `weekly-menu-preview` artifact.

This is the main way I check the graphics before actually publishing them.

## Technology Used

| Technology | What I Used It For |
|---|---|
| Python | Main automation |
| Pillow | Creating the menu graphics |
| Requests | API and menu requests |
| GitHub Actions | Running the automation remotely |
| Pytest | Testing the menu parser |
| Instagram API | Publishing the carousel |
| Canva | Designing the original graphics |

## Why I Built It

The main reason I built this wasn't just to automate an Instagram post.

My community service group was working on ways to reduce food waste at school. We first focused on making the weekly menu easier for students to find, but maintaining the Instagram page manually also took time away from some of our larger ideas, including composting food waste and creating a garden.

Since I already knew Python, I wanted to see if I could automate the repetitive part instead.

I spent time figuring out how the school's menu website stored its information, how to turn that information into something Python could use, and eventually how to automatically generate the graphics. After that, I expanded it so GitHub Actions could run the project and Instagram could receive the finished carousel.

What started as a pretty simple idea of posting the lunch menu ended up combining coding, APIs, graphic design, automation, and our food waste project.

## Possible Improvements

There are still some things I could improve later, including:

- Fully automated scheduled Instagram posting
- More tests for unusual or missing menu data
- Better detection of problems in generated graphics
- More food waste facts and sources
- Notifications when an automated run fails
- Support for other menu designs or schools

## Font

This project uses the Chewy typeface from Google Fonts.

Chewy is distributed under the Apache License 2.0. See `assets/fonts/LICENSE.txt` for the full license text.
