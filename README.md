# Weekly Menu Bot

Automates the Wilson High School / GAWHS weekly lunch-menu carousel using the public Health-e Pro menu data.

## What it does

1. Finds the next Monday-Friday week.
2. Pulls Health-e Pro `date_overwrites` for every month touched by that week.
3. Pulls recipes for the same date range.
4. Resolves daily recipe IDs into names and categories.
5. Handles `No school` days.
6. Renders six carousel JPGs using the template assets already included here.
7. Runs in GitHub Actions.
8. Can later publish directly to Instagram through Meta's API.

## Health-e Pro configuration

- Organization ID: `2221`
- Site ID: `14158`
- Menu ID: `125015`
- Menu: `2026-27 HS Lunch`

Source page:
`https://menus.healthepro.com/organizations/2221/sites/14158/menus/125015`

## Upload this repository

Put every file/folder from this ZIP into the root of `exodia624/weekly-menu-bot`.

The included `assets/source/` files are the menu template images from the original project, and `assets/backgrounds/` are cleaned versions used by the renderer. You do not need to re-upload the template separately.

## First test — no Instagram credentials needed

1. Open the GitHub repository.
2. Go to **Actions** → **Weekly Lunch Menu**.
3. Click **Run workflow**.
4. Leave `publish` OFF.
5. Optionally enter a Monday, such as `2026-08-24`, in `week_start`.
6. Run it.
7. Open the completed run and download the `weekly-menu-preview` artifact.
8. Check the six generated JPGs and `menu.json` against Health-e Pro.

The workflow is deliberately safe: scheduled runs only generate previews until live publishing is explicitly enabled.

## Instagram setup — later

When the graphics are verified, add these GitHub repository secrets under **Settings → Secrets and variables → Actions**:

- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`

Do **not** put the actual token in `.env`, README, source code, or a public commit.

Then manually run the workflow with `publish` enabled for the first live test.

## Important Meta note

Meta periodically changes Graph API versions and Instagram permissions. `src/instagram.py` isolates the publishing code so the Graph version or endpoints can be changed without touching the menu parser or renderer. Before the first live post, verify the current Meta Instagram publishing requirements in Meta's official documentation.

## Local test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -q
WEEK_START=2026-08-24 DRY_RUN=true python -m src.main
```

Generated files appear in `generated/`.

## If a day's items are missing

Health-e Pro stores `current_display` inside the daily `setting` JSON string. The parser is intentionally defensive, but if Health-e Pro changes that internal format, inspect `generated/menu.json` and the Actions log. The relevant code is `src/menu_parser.py`.
