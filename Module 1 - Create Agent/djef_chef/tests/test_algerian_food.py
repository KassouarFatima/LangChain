"""Algerian-food guarantee tests.

These are the exact tests shown in ``docs/demo.gif``: the 16-dish Algerian
menu stays whitelisted, every dish is reachable from its own ingredients in
English / French / Arabic, and generic foreign food is never recommended.
All tests are offline — no Gemini or Tavily calls.
"""

from __future__ import annotations

import json

import pytest

from notebook.chef_service import (
    ALGERIAN_MENU,
    RECIPE_CATALOG,
    match_leftover_recipes,
    rank_recipe_catalogue,
)

EXPECTED_MENU = (
    "Tlitli",
    "Karantita",
    "Harira",
    "Chorba frik",
    "Luobia khadra",
    "Mhadjeb",
    "Rechta",
    "Berkoukes",
    "Bambalouni",
    "Chakhchoukha",
    "Chickpea and vegetable tagine",
    "Shakshuka",
    "Dolma",
    "Tadjine zitoune",
    "Vegetable rice",
    "Burek",
)


def test_menu_is_exactly_the_sixteen_algerian_dishes() -> None:
    assert ALGERIAN_MENU == EXPECTED_MENU
    assert len(ALGERIAN_MENU) == 16


def test_every_menu_dish_exists_in_the_catalogue() -> None:
    titles = {recipe.title for recipe in RECIPE_CATALOG}
    assert tuple(sorted(titles, key=EXPECTED_MENU.index)) == EXPECTED_MENU


def test_tool_returns_only_algerian_menu_titles() -> None:
    payload = json.loads(
        match_leftover_recipes.invoke(
            {"ingredients": "chickpeas, tomatoes, onion, eggs, semolina, rice, peppers, potatoes"}
        )
    )
    titles = {match["title"] for match in payload["matches"]}
    assert titles  # at least one suggestion
    assert titles <= set(EXPECTED_MENU)


@pytest.mark.parametrize("recipe", RECIPE_CATALOG, ids=lambda r: r.title)
def test_each_dish_is_reachable_from_its_own_ingredients(recipe) -> None:
    ingredients = ", ".join(recipe.required)
    matches = rank_recipe_catalogue(ingredients)

    assert matches, f"{recipe.title} should match from {ingredients}"
    entry = next(match for match in matches if match["title"] == recipe.title)
    assert entry["match_percent"] == 100, (
        f"{recipe.title} should score 100% from its own ingredients"
    )
    assert entry["still_missing"] == []


@pytest.mark.parametrize(
    ("fridge", "expected_dish"),
    (
        ("semolina", "Mhadjeb"),
        ("lentils, tomatoes", "Harira"),
        ("chickpeas, tomatoes", "Chickpea and vegetable tagine"),
        ("vermicelli, chickpeas", "Rechta"),
        ("tomato, onion", "Chakhchoukha"),
        ("egg, tomato", "Shakshuka"),
        ("green beans, tomatoes", "Luobia khadra"),
        ("bulgur, tomatoes, onion", "Chorba frik"),
        ("pasta, tomatoes", "Bambalouni"),
        ("bell peppers, tomatoes", "Dolma"),
        ("rice, tomatoes", "Vegetable rice"),
        ("phyllo, potato, onion", "Burek"),
        ("chickpea flour", "Karantita"),
        ("chickpea flour, onion", "Tlitli"),
        ("semolina, tomatoes, chickpeas", "Berkoukes"),
    ),
)
def test_fridge_ingredients_rank_the_expected_algerian_dish(
    fridge: str, expected_dish: str
) -> None:
    top = rank_recipe_catalogue(fridge)[0]
    assert top["title"] == expected_dish, f"{fridge!r} should rank {expected_dish} first"


def test_tomato_and_onion_ranks_chakhchoukha_first_and_offers_tadjine_zitoune() -> None:
    matches = rank_recipe_catalogue("tomato, onion")
    titles = [match["title"] for match in matches]
    assert titles[0] == "Chakhchoukha"
    assert "Tadjine zitoune" in titles


@pytest.mark.parametrize(
    ("fridge", "expected_dish"),
    (
        ("حمص, طماطم", "Chickpea and vegetable tagine"),  # chickpeas, tomatoes
        ("عدس, طماطم", "Harira"),  # lentils, tomatoes
        ("سميد", "Mhadjeb"),  # semolina
        ("فاصولياء خضراء, طماطم", "Luobia khadra"),  # green beans, tomatoes
        ("طحين الحمص", "Karantita"),  # chickpea flour
    ),
)
def test_arabic_ingredients_find_algerian_dishes(fridge: str, expected_dish: str) -> None:
    top = rank_recipe_catalogue(fridge)[0]
    assert top["title"] == expected_dish


@pytest.mark.parametrize(
    ("fridge", "expected_dish"),
    (
        ("pois chiches, tomates", "Chickpea and vegetable tagine"),
        ("lentilles, tomates", "Harira"),
        ("semoule", "Mhadjeb"),
        ("haricot vert, tomates", "Luobia khadra"),
        ("pommes de terre, feuilles filo, oignons", "Burek"),
    ),
)
def test_french_ingredients_find_algerian_dishes(fridge: str, expected_dish: str) -> None:
    top = rank_recipe_catalogue(fridge)[0]
    assert top["title"] == expected_dish


@pytest.mark.parametrize(
    "foreign_input",
    (
        "pizza dough, mozzarella, pepperoni",
        "burger buns, beef patties",
        "taco shells, ground beef, cheddar",
        "sushi nori, wasabi, soy sauce",
        "hot dogs, ketchup",
        "spring rolls, sweet chilli sauce",
    ),
)
def test_foreign_food_is_never_ranked_as_an_algerian_dish(foreign_input: str) -> None:
    assert rank_recipe_catalogue(foreign_input) == []


def test_foreign_cuisine_tool_answer_stays_algerian() -> None:
    payload = json.loads(
        match_leftover_recipes.invoke({"ingredients": "pizza dough, mozzarella, pepperoni"})
    )
    assert payload["matches"] == []
    assert "Algerian" in payload["message"]


def test_gluten_intolerance_is_flagged_on_semolina_dishes() -> None:
    matches = rank_recipe_catalogue("semolina", allergies="gluten")
    top = matches[0]
    assert top["title"] == "Mhadjeb"
    assert any("gluten" in note.casefold() for note in top["safety_notes"])


def test_every_dish_carries_an_arabic_translation() -> None:
    for recipe in RECIPE_CATALOG:
        assert recipe.translation, f"{recipe.title} is missing its Arabic translation"
