import pytest

from wahlwerk_ui.html import Html
from wahlwerk_ui.plot.chamber.card import chamber_html

BUNDESTAG_2025 = [("linke", 64), ("gruene", 85), ("spd", 120), ("cdu-csu", 208), ("afd", 152)]


def test_card_is_renderable_html_with_legend():
    card = chamber_html(BUNDESTAG_2025, title="Bundestag")
    assert isinstance(card, Html) and isinstance(card, str)
    assert card._repr_html_() == card
    assert "Bundestag" in card
    assert card.count("<tr>") == len(BUNDESTAG_2025)


def test_kind_picks_the_plot():
    assert chamber_html(BUNDESTAG_2025).count("<circle") == 629
    pie = chamber_html(BUNDESTAG_2025, kind="pie")
    assert "<circle" not in pie
    assert pie.count("<path") == 5
    with pytest.raises(ValueError, match="kind"):
        chamber_html(BUNDESTAG_2025, kind="bars")  # type: ignore[arg-type]


def test_no_title_no_header():
    assert "font-weight:bold;color:#222" not in chamber_html(BUNDESTAG_2025)
