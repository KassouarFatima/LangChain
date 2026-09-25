from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langgraph.checkpoint.memory import MemorySaver

from notebook.chef_service import (
    RECIPE_CATALOG,
    Recipe,
    build_chef_graph,
    conversation_config,
    extract_ingredients,
    match_leftover_recipes,
    normalize_ingredient,
    onboarding_message,
    rank_recipe_catalogue,
)


def test_normalize_ingredient_handles_quantities_and_languages() -> None:
    assert normalize_ingredient("2 tomatoes") == "tomato"
    assert normalize_ingredient("pommes de terre") == "potato"
    assert normalize_ingredient("pois chiches") == "chickpeas"
    assert normalize_ingredient("بيض") == "egg"
    assert normalize_ingredient("fève verte") == "green_beans"


def test_extract_ingredients_splits_natural_lists() -> None:
    assert extract_ingredients("2 tomatoes, chickpea flour and cumin") == {
        "tomato",
        "chickpea_flour",
        "cumin",
    }


def test_ranker_finds_tlitli_and_separates_missing_items() -> None:
    matches = rank_recipe_catalogue("chickpea flour, onion, cumin")

    assert matches
    assert matches[0]["title"] == "Tlitli"
    assert matches[0]["match_percent"] == 100
    assert matches[0]["still_missing"] == []


def test_ranker_matches_harira_from_lentils_and_tomato() -> None:
    matches = rank_recipe_catalogue("I have lentils, tomatoes, onion")

    harira = next(match for match in matches if match["title"] == "Harira")
    assert harira["match_percent"] == 100
    assert "lentil" in harira["use_now"]
    assert "tomato" in harira["use_now"]
    assert harira["translation"] == "حريرة"


def test_ranker_matches_mhadjeb_from_semolina() -> None:
    matches = rank_recipe_catalogue("semolina")

    mhadjeb = next(match for match in matches if match["title"] == "Mhadjeb")
    assert mhadjeb["match_percent"] == 100
    assert "semolina" in mhadjeb["use_now"]


def test_catalogue_only_contains_specific_algerian_dishes() -> None:
    titles = {recipe.title for recipe in RECIPE_CATALOG}
    expected = {
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
    }
    assert titles == expected
    assert len(RECIPE_CATALOG) >= 14


def test_ranker_reports_partial_matches() -> None:
    matches = rank_recipe_catalogue("I only have tomatoes and eggs")

    shakshuka = next(match for match in matches if match["title"] == "Shakshuka")
    assert "tomato" in shakshuka["use_now"]
    assert "egg" in shakshuka["use_now"]


def test_gluten_allergy_does_not_flag_chickpea_flour() -> None:
    matches = rank_recipe_catalogue(
        "chickpea flour and onion",
        allergies="gluten",
    )

    tlitli = next(match for match in matches if match["title"] == "Tlitli")
    assert tlitli["safety_notes"] == []


def test_gluten_allergy_flags_pasta_recipe() -> None:
    matches = rank_recipe_catalogue(
        "pasta and tomato",
        allergies="gluten",
    )

    bambalouni = next(match for match in matches if match["title"] == "Bambalouni")
    assert any("gluten" in note.casefold() for note in bambalouni["safety_notes"])


def test_gluten_allergy_flags_rechta_vermicelli() -> None:
    matches = rank_recipe_catalogue(
        "vermicelli and chickpeas",
        allergies="gluten",
    )

    rechta = next(match for match in matches if match["title"] == "Rechta")
    assert any("gluten" in note.casefold() for note in rechta["safety_notes"])


def test_tool_returns_compact_json() -> None:
    payload = match_leftover_recipes.invoke({"ingredients": "lentils, tomato, onion"})

    assert '"title": "Harira"' in payload
    assert '"match_percent": 100' in payload


def test_custom_catalogue_keeps_ranking_pure() -> None:
    tiny_catalogue = (
        Recipe(
            title="Tiny test recipe",
            category="Test",
            required=("tomato",),
            optional=("onion",),
            pantry=("salt",),
            steps=("Cook it.",),
        ),
    )

    matches = rank_recipe_catalogue("tomato", catalogue=tiny_catalogue)
    assert [match["title"] for match in matches] == ["Tiny test recipe"]
    assert len(RECIPE_CATALOG) > 5


def test_onboarding_message_contains_profile_for_memory() -> None:
    message = onboarding_message(
        name="Fatima",
        dietary_preferences=["Vegetarian"],
        allergies="peanuts",
    )

    assert "Name: Fatima" in message
    assert "Dietary preferences: Vegetarian" in message
    assert "Allergies or ingredients to avoid: peanuts" in message


def test_conversation_config_uses_an_isolated_thread() -> None:
    assert conversation_config("chef-123") == {"configurable": {"thread_id": "chef-123"}}


def test_conversation_config_rejects_empty_thread() -> None:
    try:
        conversation_config("  ")
    except ValueError as exc:
        assert "thread_id" in str(exc)
    else:
        raise AssertionError("An empty thread id should be rejected")


def test_studio_graph_omits_custom_checkpointer() -> None:
    model = GenericFakeChatModel(messages=iter(()))

    studio_graph = build_chef_graph(model=model, tools=[])
    streamlit_graph = build_chef_graph(model=model, tools=[], checkpointer=MemorySaver())

    assert studio_graph.checkpointer is None
    assert isinstance(streamlit_graph.checkpointer, MemorySaver)


def test_transient_error_classification() -> None:
    from notebook.chef_service import _is_transient_error

    assert _is_transient_error(RuntimeError("429 RESOURCE_EXHAUSTED"))
    assert _is_transient_error(RuntimeError("503 UNAVAILABLE"))
    assert _is_transient_error(RuntimeError("GoogleAPIError 502"))
    assert not _is_transient_error(RuntimeError("404 NOT_FOUND"))
    assert not _is_transient_error(RuntimeError("400 INVALID_ARGUMENT"))
    assert not _is_transient_error(RuntimeError("quota reached at home"))


def test_invoke_with_retry_recovers_from_transient_errors() -> None:
    from notebook.chef_service import invoke_with_retry

    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("503 UNAVAILABLE")
        return "finally"

    assert invoke_with_retry(flaky, attempts=5, backoff_seconds=0.01, label="test") == "finally"
    assert calls["n"] == 3


def test_invoke_with_retry_re_raises_non_transient_errors() -> None:
    from notebook.chef_service import invoke_with_retry

    def broken() -> None:
        raise ValueError("404 NOT_FOUND")

    try:
        invoke_with_retry(broken, attempts=3, backoff_seconds=0.01)
    except ValueError as exc:
        assert "404" in str(exc)
    else:
        raise AssertionError("A non-transient error should be re-raised immediately")


def test_daily_quota_vs_per_minute_detection() -> None:
    from notebook.chef_service import _is_daily_quota

    # Google's per-minute 429 carries the daily-quota text too, but ends with a
    # short "retry in Ns" hint — that resets on its own and must be retried.
    per_minute = RuntimeError(
        "429 RESOURCE_EXHAUSTED PerDayPerProjectPerModel-FreeTier limit: 20 "
        "Please retry in 11.328808182s."
    )
    assert not _is_daily_quota(per_minute)

    # Genuine daily exhaustion (no short hint) must be reported right away.
    daily = RuntimeError(
        "429 RESOURCE_EXHAUSTED PerDayPerProjectPerModel-FreeTier "
        "you exceeded your current quota"
    )
    assert _is_daily_quota(daily)


def test_gemini_error_message_is_friendly() -> None:
    from notebook.chef_service import gemini_error_message

    assert "busy" in gemini_error_message(RuntimeError("503 UNAVAILABLE"))
    assert "daily quota" in gemini_error_message(
        RuntimeError("429 RESOURCE_EXHAUSTED PerDayPerProjectPerModel-FreeTier")
    )
    assert "404" in gemini_error_message(RuntimeError("404 NOT_FOUND"))
    assert "Traceback" not in gemini_error_message(RuntimeError("503 UNAVAILABLE"))
