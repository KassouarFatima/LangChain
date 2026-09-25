"""Repo-structure tests: the project has exactly three entry-point folders."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_three_entry_points_exist() -> None:
    assert (PROJECT_ROOT / "notebook" / "chef_service.py").is_file()
    assert (PROJECT_ROOT / "streamlit" / "app.py").is_file()
    assert (PROJECT_ROOT / "studio_simulation" / "simulate.py").is_file()


def test_notebook_is_a_valid_ipynb() -> None:
    notebook = json.loads(
        (PROJECT_ROOT / "notebook" / "DJEF_Chef.ipynb").read_text(encoding="utf-8")
    )
    assert notebook["nbformat"] == 4
    assert any(cell["cell_type"] == "code" for cell in notebook["cells"])
    assert any(cell["cell_type"] == "markdown" for cell in notebook["cells"])


def test_demo_gif_exists_and_is_small_enough() -> None:
    gif = PROJECT_ROOT / "docs" / "demo.gif"
    assert gif.is_file()
    assert gif.stat().st_size < 1_000_000


def test_readme_points_to_the_three_folders() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "notebook/" in readme
    assert "streamlit/" in readme
    assert "studio_simulation/" in readme


def test_author_name_appears_everywhere() -> None:
    sources = (
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "streamlit" / "app.py",
        PROJECT_ROOT / "studio_simulation" / "simulate.py",
        PROJECT_ROOT / "studio_simulation" / "README.md",
        PROJECT_ROOT / "notebook" / "DJEF_Chef.ipynb",
    )
    for path in sources:
        assert "Kassouar Fatima" in path.read_text(encoding="utf-8"), (
            f"{path} must credit the author"
        )
