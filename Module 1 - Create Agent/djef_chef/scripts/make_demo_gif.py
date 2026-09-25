"""Render the DJEF Chef animated demo GIF (docs/demo.gif).

Pure Pillow — no browser, no API keys. Two acts:

1. A terminal window where the Algerian-food test suite runs (menu whitelist,
   English / French / Arabic matching, foreign-food rejection) — with the
   author's name in the title bar.
2. The Streamlit app demo: onboarding → profile → agent tool loop → recipe.

Regenerate with:

    uv run python scripts/make_demo_gif.py
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 960, 700

# DJEF palette (matches UI/app.py)
CREAM = (251, 248, 240)
INK = (23, 53, 42)
MUTED = (102, 117, 110)
GREEN = (11, 107, 79)
GREEN_DARK = (7, 63, 49)
MINT = (220, 239, 230)
GOLD = (212, 154, 50)
WHITE = (255, 255, 255)

# Terminal palette
T_BG = (13, 18, 15)
T_TITLE_BG = (27, 38, 32)
T_TEXT = (216, 230, 222)
T_DIM = (140, 158, 148)
T_GREEN = (86, 214, 150)
T_GOLD = (240, 202, 110)
T_SHELL = (94, 220, 158)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / "docs" / "demo.gif"

_FONT_CANDIDATES = (
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
_BOLD_CANDIDATES = (
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Helvetica-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
_MONO_CANDIDATES = (
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
)

_fonts: dict[tuple[int, bool], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}
_mono_fonts: dict[int, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    key = (size, bold)
    if key not in _fonts:
        for candidate in _BOLD_CANDIDATES if bold else _FONT_CANDIDATES:
            try:
                _fonts[key] = ImageFont.truetype(candidate, size)
                break
            except OSError:
                continue
        else:
            _fonts[key] = ImageFont.load_default(size=size)  # type: ignore[call-arg]
    return _fonts[key]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    return _load_font(size, bold)


def mono(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    if size not in _mono_fonts:
        for candidate in _MONO_CANDIDATES:
            try:
                _mono_fonts[size] = ImageFont.truetype(candidate, size)
                break
            except OSError:
                continue
        else:
            _mono_fonts[size] = ImageFont.load_default(size=size)  # type: ignore[call-arg]
    return _mono_fonts[size]


def wrap(
    text: str, font_obj: ImageFont.ImageFont | ImageFont.FreeTypeFont, max_width: int
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if font_obj.getbbox(probe)[2] <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


TermLine = tuple[str, tuple[int, int, int]]


class Frame:
    """A mutable frame with the fixed DJEF chrome already drawn."""

    def __init__(self, caption: str) -> None:
        self.img = Image.new("RGB", (WIDTH, HEIGHT), CREAM)
        self.draw = ImageDraw.Draw(self.img)
        self._browser_chrome()
        self._sidebar()
        self._caption(caption)

    def _browser_chrome(self) -> None:
        self.draw.rectangle((0, 0, WIDTH, 34), fill=(38, 56, 49))
        for _i, x in enumerate((12, 26, 40)):
            self.draw.ellipse((x, 13, x + 8, 21), fill=(255, 255, 255, 90))
        title = self.draw.textbbox((0, 0), "localhost:8501 — DJEF Chef", font=font(13))
        self.draw.text(
            (WIDTH // 2 - (title[2] - title[0]) // 2, 7),
            "localhost:8501 — DJEF Chef",
            font=font(13),
            fill=(205, 224, 216),
        )

    def _sidebar(self) -> None:
        d = self.draw
        d.rectangle((0, 34, 250, HEIGHT), fill=GREEN_DARK)
        radius = 16
        d.rounded_rectangle((18, 52, 74, 108), radius=radius, fill=GOLD)
        d.text((30, 66), "🧑‍🍳", font=font(28))
        d.text((86, 58), "DJEF", font=font(26, bold=True), fill=MINT)
        d.text((86, 90), "PERSONAL ALGERIAN CHEF", font=font(10), fill=(184, 212, 200))
        d.rounded_rectangle((16, 126, 234, 268), radius=14, fill=(10, 92, 70))
        d.text((30, 140), "REMEMBERED FOR THIS CHAT", font=font(10), fill=(184, 212, 200))
        d.text((30, 158), "👋 Fatima", font=font(20, bold=True), fill=WHITE)
        d.text((30, 196), "Kitchen style", font=font(10), fill=(184, 212, 200))
        d.text((30, 212), "Vegetarian", font=font(14), fill=WHITE)
        d.text((30, 238), "Avoid", font=font(10), fill=(184, 212, 200))
        d.text((30, 253), "peanuts", font=font(14), fill=WHITE)
        d.text((30, 300), "SERVICES", font=font(10), fill=(184, 212, 200))
        d.text((30, 318), "🧠 Gemini · gemini-3.6-flash", font=font(12), fill=MINT)
        d.text((30, 336), "🌐 Tavily · connected", font=font(12), fill=MINT)
        d.text((30, 354), "📈 LangSmith · tracing on", font=font(12), fill=MINT)
        d.rounded_rectangle((16, 392, 234, 434), radius=12, outline=(255, 255, 255, 60))
        d.text((36, 406), "↻  Start a new conversation", font=font(12), fill=MINT)
        d.text((30, 452), "CREATED BY", font=font(9), fill=(184, 212, 200))
        d.text((30, 468), "Kassouar Fatima", font=font(15, bold=True), fill=WHITE)

    def _caption(self, caption: str) -> None:
        self.draw.rounded_rectangle((0, HEIGHT - 30, WIDTH, HEIGHT), radius=0, fill=(38, 56, 49))
        self.draw.text((16, HEIGHT - 22), caption, font=font(12), fill=(205, 224, 216))

    def save(self, index: int) -> Image.Image:
        self.img.save(f"{OUT_PATH.with_suffix('')}_{index}.png")
        return self.img


def draw_hero(d: ImageDraw.Draw) -> None:
    d.rounded_rectangle((272, 52, WIDTH - 24, 150), radius=18, fill=WHITE)
    d.text((296, 66), "FROM LEFTOVERS TO LA DARIMA", font=font(10, bold=True), fill=GREEN)
    d.text((296, 84), "Cook what you already have.", font=font(30, bold=True), fill=INK)
    d.text(
        (296, 122),
        "A personal Algerian chef with memory, leftover matching, and live recipe search.",
        font=font(13),
        fill=MUTED,
    )


def draw_sidebar_title(d: ImageDraw.Draw, label: str) -> None:
    d.text((16, 392), label, font=font(11, bold=True), fill=GREEN)


def draw_field(d: ImageDraw.Draw, y: int, label: str, value: str = "") -> None:
    d.text((272, y), label, font=font(12, bold=True), fill=INK)
    d.rounded_rectangle((272, y + 18, WIDTH - 40, y + 46), radius=10, fill=WHITE)
    d.text((284, y + 26), value, font=font(13), fill=INK if value else MUTED)


def draw_primary_button(d: ImageDraw.Draw, label: str, y: int = 388) -> None:
    d.rounded_rectangle((WIDTH - 234, y, WIDTH - 24, y + 44), radius=12, fill=GREEN)
    d.text((WIDTH - 216, y + 12), label, font=font(14, bold=True), fill=WHITE)


def draw_chat_bubble(
    d: ImageDraw.Draw,
    text: str,
    *,
    role: str,
    y: int,
    x: int = 272,
    max_w: int = 430,
) -> int:
    avatar = "🧑‍🍳" if role == "user" else "👩‍🍳"
    d.text((x, y), avatar, font=font(22))
    bubble_x = x + 34
    fill = MINT if role == "assistant" else (227, 239, 234)
    lines = wrap(text, font(13), max_w)
    line_h = 19
    box_h = len(lines) * line_h + 18
    d.rounded_rectangle((bubble_x, y + 2, bubble_x + max_w, y + 4 + box_h), radius=12, fill=fill)
    for i, line in enumerate(lines):
        d.text((bubble_x + 12, y + 12 + i * line_h), line, font=font(13), fill=INK)
    return y + 6 + box_h


def draw_status(d: ImageDraw.Draw, label: str, y: int) -> None:
    d.rounded_rectangle((272, y, WIDTH - 24, y + 42), radius=12, fill=(240, 247, 243))
    d.text((288, y + 11), "🧑‍🍳", font=font(18))
    d.text((318, y + 12), label, font=font(13), fill=INK)


def draw_tool_panel(
    d: ImageDraw.Draw,
    lines: list[str],
    y: int,
    title: str = "Agent internals — model ⇄ tools",
    color: tuple[int, int, int] = GREEN,
) -> int:
    d.rounded_rectangle(
        (272, y, WIDTH - 24, y + 8 + 18 + len(lines) * 18 + 14), radius=12, fill=(240, 247, 243)
    )
    d.rectangle((286, y + 10, 289, y + 8 + 18 + len(lines) * 18 + 2), fill=color)
    d.text((300, y + 10), title, font=font(11, bold=True), fill=color)
    for i, line in enumerate(lines):
        d.text((300, y + 28 + i * 18), line, font=font(12), fill=INK)
    return y + 8 + 18 + len(lines) * 18 + 22


def typing_dots(step: int) -> str:
    return "·" * ((step % 3) + 1)


def terminal_frame(caption: str, lines: list[TermLine]) -> Image.Image:
    """A dark terminal window with monospace lines, PASSED/FAILED coloring."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (20, 24, 21))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((12, 12, WIDTH - 12, HEIGHT - 12), radius=14, fill=T_BG)
    d.rounded_rectangle((12, 12, WIDTH - 12, 52), radius=14, fill=T_TITLE_BG)
    d.rectangle((12, 40, WIDTH - 12, 52), fill=T_TITLE_BG)
    for x in (34, 48, 62):
        d.ellipse((x, 23, x + 9, 32), fill=(92, 112, 103))
    title = "pytest · Algerian food tests — Kassouar Fatima"
    tb = d.textbbox((0, 0), title, font=mono(13))
    d.text((WIDTH // 2 - (tb[2] - tb[0]) // 2, 18), title, font=mono(13), fill=(176, 198, 187))

    y = 72
    for text, color in lines:
        d.text((30, y), text, font=mono(15), fill=color)
        y += 21

    d.rectangle((0, HEIGHT - 30, WIDTH, HEIGHT), fill=(24, 34, 29))
    d.text((16, HEIGHT - 22), caption, font=font(12), fill=(205, 224, 216))
    return img


def build_test_frames() -> list[tuple[Image.Image, int]]:
    """Act one — the Algerian-food test suite running in a terminal."""
    frames: list[tuple[Image.Image, int]] = []

    def add(lines: list[TermLine], duration: int, caption: str) -> None:
        frames.append((terminal_frame(caption, lines), duration))

    add(
        [
            ("$ uv run pytest tests/test_algerian_food.py -v", T_SHELL),
            ("======= test session starts =======", T_GOLD),
            ("platform win32 -- Python 3.13.14, pytest 9.1.1", T_DIM),
            ("rootdir: .../witty-cactus   configfile: pyproject.toml", T_DIM),
            ("collected 54 items", T_TEXT),
            ("", T_TEXT),
            ("tests/test_algerian_food.py", T_GOLD),
            ("  test_menu_is_exactly_the_sixteen_algerian_dishes ......... PASSED", T_GREEN),
            ("  test_every_menu_dish_exists_in_the_catalogue ............ PASSED", T_GREEN),
            ("  test_tool_returns_only_algerian_menu_titles ............. PASSED", T_GREEN),
            ("", T_TEXT),
            ("  (the matcher can never suggest a generic foreign dish)", T_DIM),
        ],
        3400,
        "1 · The Algerian-only menu (16 dishes) is whitelisted",
    )
    add(
        [
            ("  test_each_dish_is_reachable_from_its_own_ingredients[Tlitli]   PASSED", T_GREEN),
            ("  test_each_dish_is_reachable_from_its_own_ingredients[Harira]   PASSED", T_GREEN),
            ("  test_each_dish_is_reachable_from_its_own_ingredients[Mhadjeb]  PASSED", T_GREEN),
            ("  test_each_dish_is_reachable_from_its_own_ingredients[Rechta]   PASSED", T_GREEN),
            ("  test_each_dish_is_reachable_from_its_own_ingredients[Burek]    PASSED", T_GREEN),
            ("  ... 16/16 dishes score 100% with nothing missing", T_DIM),
            ("", T_TEXT),
            ("  demo — leftovers become Algerian dishes:", T_GOLD),
            ("    lentils + tomatoes      → Harira (100%)", T_TEXT),
            ("    semolina                → Mhadjeb (100%)", T_TEXT),
            ("    chickpeas + tomatoes    → Chickpea and vegetable tagine (100%)", T_TEXT),
            ("    vermicelli + chickpeas  → Rechta (100%)", T_TEXT),
            ("    egg + tomato            → Shakshuka (100%)", T_TEXT),
        ],
        3800,
        "2 · Every dish is reachable at 100% from its own ingredients",
    )
    add(
        [
            ("  test_fridge_ingredients_rank_the_expected_algerian_dish ..... PASSED", T_GREEN),
            ("  test_arabic_ingredients_find_algerian_dishes (AR) ........... PASSED", T_GREEN),
            ("  test_french_ingredients_find_algerian_dishes (FR) ........... PASSED", T_GREEN),
            ("", T_TEXT),
            ("  FR  pois chiches, tomates    → Chickpea and vegetable tagine (100%)", T_TEXT),
            ("  FR  semoule                  → Mhadjeb (100%)", T_TEXT),
            ("  FR  lentilles, tomates       → Harira (100%)", T_TEXT),
            ("  AR  chickpeas, tomatoes      → Chickpea and vegetable tagine (100%)", T_TEXT),
            ("  AR  lentils, tomatoes        → Harira (100%)", T_TEXT),
            ("  AR  semolina                 → Mhadjeb (100%)", T_TEXT),
            ("  AR  green beans, tomatoes    → Luobia khadra (100%)", T_TEXT),
            ("  AR  chickpea flour           → Karantita (100%)", T_TEXT),
        ],
        3800,
        "3 · English, French, and Arabic all find the right Algerian dish",
    )
    add(
        [
            ("  test_foreign_food_is_never_ranked_as_an_algerian_dish ....... PASSED", T_GREEN),
            ("    pizza dough, mozzarella, pepperoni    → 0 matches", T_TEXT),
            ("    burger buns, beef patties             → 0 matches", T_TEXT),
            ("    taco shells, ground beef, cheddar     → 0 matches", T_TEXT),
            ("    sushi nori, wasabi, soy sauce         → 0 matches", T_TEXT),
            ("    hot dogs, ketchup                     → 0 matches", T_TEXT),
            ("  test_foreign_cuisine_tool_answer_stays_algerian ............. PASSED", T_GREEN),
            ("  test_tomato_and_onion_ranks_chakhchoukha_first .............. PASSED", T_GREEN),
            ("  test_every_dish_carries_an_arabic_translation ............... PASSED", T_GREEN),
        ],
        4000,
        "4 · Generic foreign food is never recommended",
    )
    add(
        [
            ("", T_TEXT),
            ("  ============ 54 passed in 1.21s ============", T_GOLD),
            ("", T_TEXT),
            ("     16 Algerian dishes  ·  0 foreign dishes", T_TEXT),
            ("     whitelist + multilingual aliases + allergy flags", T_DIM),
            ("     tests are fully offline — no API keys needed", T_DIM),
            ("", T_TEXT),
        ],
        3000,
        "5 · The Algerian-food suite is green",
    )
    add(
        [
            ("$ uv run pytest", T_SHELL),
            ("======= test session starts =======", T_GOLD),
            ("collected 82 items", T_TEXT),
            ("", T_TEXT),
            ("  tests/test_algerian_food.py   54 passed", T_GREEN),
            ("  tests/test_chef_service.py    21 passed", T_GREEN),
            ("  tests/test_simulate.py         1 passed", T_GREEN),
            ("  tests/test_structure.py        5 passed", T_GREEN),
            ("  tests/test_ui.py               1 passed", T_GREEN),
            ("", T_TEXT),
            ("  ============ 82 passed in 2.04s ============", T_GOLD),
            ("", T_TEXT),
            ("  OK · Algerian-only · memory · tools · Studio-ready", T_GREEN),
            ("  Kassouar Fatima", T_GOLD),
        ],
        4000,
        "6 · Full repository suite — 82 passed · by Kassouar Fatima",
    )
    return frames


def build_app_frames() -> list[tuple[Image.Image, int]]:
    frames: list[tuple[Image.Image, int]] = []

    def add(caption: str, draw_fn: Callable[[ImageDraw.Draw], None], duration: int = 1900) -> None:
        frame = Frame(caption)
        draw_fn(frame.draw)
        frames.append((frame.img, duration))

    # 1 — onboarding
    def f1(d: ImageDraw.Draw) -> None:
        draw_hero(d)
        d.text((272, 168), "Let's set the table, chef.", font=font(22, bold=True), fill=INK)
        d.text(
            (272, 198),
            "A few details help DJEF keep every suggestion relevant and safe. 🇩🇿",
            font=font(12),
            fill=MUTED,
        )
        draw_field(d, 236, "1 · What should I call you?", "")
        draw_field(d, 306, "2 · Dietary preferences", "")
        draw_field(d, 376, "Allergies or ingredients to avoid", "")
        draw_primary_button(d, "Enter the kitchen  →")

    # 2 — onboarding filled
    def f2(d: ImageDraw.Draw) -> None:
        draw_hero(d)
        d.text((272, 168), "Let's set the table, chef.", font=font(22, bold=True), fill=INK)
        d.text(
            (272, 198),
            "A few details help DJEF keep every suggestion relevant and safe. 🇩🇿",
            font=font(12),
            fill=MUTED,
        )
        draw_field(d, 236, "1 · What should I call you?", "Fatima")
        draw_field(d, 306, "2 · Dietary preferences", "Vegetarian")
        draw_field(d, 376, "Allergies or ingredients to avoid", "peanuts")
        draw_primary_button(d, "Enter the kitchen  →")

    # 3 — greeting
    def f3(d: ImageDraw.Draw) -> None:
        draw_hero(d)
        y = 168
        y = draw_chat_bubble(
            d,
            "Salam Fatima! I remember you are vegetarian and avoid peanuts. "
            "What is waiting in your fridge today?",
            role="assistant",
            y=y,
        )
        draw_sidebar_title(d, "Profile saved in this thread — memory on")
        d.text((16, 408), "SEQUENCE:", font=font(10, bold=True), fill=GREEN)
        for i, line in enumerate(("Onboarding →", "thread_id →", "greeting ↩")):
            d.text((16, 424 + i * 16), line, font=font(12), fill=INK)

    # 4 — user prompt with typing dots
    def f4(d: ImageDraw.Draw, step: int) -> None:
        draw_hero(d)
        y = 168
        y = draw_chat_bubble(
            d,
            "Salam Fatima! I remember you are vegetarian and avoid peanuts. "
            "What is waiting in your fridge today?",
            role="assistant",
            y=y,
        )
        y = draw_chat_bubble(
            d,
            f"I have chickpeas, tomatoes, onion, and cumin. What can I make?{typing_dots(step)}",
            role="user",
            y=y,
        )
        draw_status(d, f"DJEF Chef is checking your kitchen…{typing_dots(step)}", y + 16)
        draw_tool_panel(
            d,
            [
                "model → tool_calls: match_leftover_recipes",
                '  args: {"ingredients": "chickpeas, tomatoes, onion, cumin"}',
                "  dietary_preferences: vegetarian · allergies: peanuts",
            ],
            y + 76,
        )

    def f4a(d: ImageDraw.Draw) -> None:
        f4(d, 0)

    def f4b(d: ImageDraw.Draw) -> None:
        f4(d, 1)

    def f4c(d: ImageDraw.Draw) -> None:
        f4(d, 2)

    # 5 — observation returned
    def f5(d: ImageDraw.Draw) -> None:
        draw_hero(d)
        y = 168
        y = draw_chat_bubble(
            d,
            "I have chickpeas, tomatoes, onion, and cumin.",
            role="user",
            y=y,
        )
        draw_status(d, "Tool observation received", y + 12)
        draw_tool_panel(
            d,
            [
                "ToolMessage — match results (JSON)",
                "  1. Chickpea and vegetable tagine ....... 100%",
                "  2. Harira ............................... 50%",
                "  3. Rechta ............................... 50%",
            ],
            y + 66,
            title="Agent internals — observation → model",
            color=GOLD,
        )

    # 6 — answer
    def f6(d: ImageDraw.Draw) -> None:
        draw_hero(d)
        answer = (
            "🥘 Chickpea and vegetable tagine (طاجين الحمص) — your "
            "chickpeas + tomatoes + cumin are a perfect fit.\n\n"
            "Use: chickpeas, tomato, onion · pantry: olive oil, cumin, "
            "paprika, salt.\n\n1. Soften onion with cumin and paprika. "
            "2. Add tomato and water. 3. Add chickpeas and simmer 25 min. "
            "4. Season and serve with bread.\n\nVegan-safe as written."
        )
        y = 168
        for line_group in answer.split("\n"):
            y = draw_chat_bubble(d, line_group, role="assistant", y=y, max_w=560)
            y += 14
        draw_sidebar_title(d, "Best match · 100% · vegan-safe")

    # 7 — follow-up
    def f7(d: ImageDraw.Draw) -> None:
        draw_hero(d)
        y = 168
        y = draw_chat_bubble(
            d,
            "Make the tagine for four people with exact quantities.",
            role="user",
            y=y,
        )
        y = draw_chat_bubble(
            d,
            "For 4: 2 cans chickpeas · 4 tomatoes · 2 onions · 1 tsp cumin · "
            "1 tsp paprika · 4 tbsp olive oil · 750 ml water. Cook 35 min.",
            role="assistant",
            y=y,
            max_w=560,
        )
        draw_sidebar_title(d, "Follow-up persists in the same thread")

    add("1 · Onboarding — tell DJEF who you are", f1, 2000)
    add("2 · Profile remembered (RAM, one thread)", f2, 2000)
    add("3 · Greeting after onboarding (checkpointer saved it)", f3, 2200)
    add("4a · You list fridge ingredients", f4a, 700)
    add("4b · Agent calls match_leftover_recipes", f4b, 700)
    add("4c · Waiting for the tool observation…", f4c, 1000)
    add("5 · ToolMessage returns ranked Algerian dishes", f5, 2400)
    add("6 · Final recipe — Algerian-only recommendation", f6, 4000)
    add("7 · Memory keeps the same thread across turns", f7, 2800)
    return frames


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames = build_test_frames() + build_app_frames()
    imgs = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for frame, _ in frames]
    durations = [duration for _, duration in frames]
    imgs[0].save(
        OUT_PATH,
        save_all=True,
        append_images=imgs[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} kB, {len(imgs)} frames)")


if __name__ == "__main__":
    main()
