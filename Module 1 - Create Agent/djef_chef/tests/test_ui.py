from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "streamlit" / "app.py"


def test_app_renders_setup_without_a_runtime_error() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()

    assert not app.exception
    assert any("set the table" in markdown.value for markdown in app.markdown)
