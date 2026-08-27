import json
from datetime import date

from src.menu_parser import parse_week, recipe_name_index


def test_recipe_index_recursive():
    payload = {"data": [{"id": 10, "name": "Pizza"}, {"recipe_id": 20, "recipe_name": "Carrots"}]}
    idx = recipe_name_index(payload)
    assert idx["10"] == "Pizza"
    assert idx["20"] == "Carrots"


def test_parse_day_and_no_school():
    rows = [
        {
            "day": "2026-08-24",
            "setting": json.dumps({
                "current_display": [
                    {"type": "category", "name": "Lunch Entree", "item": "Lunch Entree"},
                    {"item": 10},
                    {"type": "category", "name": "Vegetables", "item": "Vegetables"},
                    {"item": 20},
                ]
            }),
        },
        {
            "day": "2026-08-25",
            "setting": json.dumps({"days_off": [{"status": 1, "description": "No school"}]}),
        },
    ]
    recipes = {"data": [{"id": 10, "name": "Pizza"}, {"id": 20, "name": "Carrots"}]}
    menu = parse_week(date(2026, 8, 24), rows, recipes)
    assert menu.days[0].categories["Lunch Entree"] == ["Pizza"]
    assert menu.days[0].categories["Vegetables"] == ["Carrots"]
    assert menu.days[1].no_school is True
