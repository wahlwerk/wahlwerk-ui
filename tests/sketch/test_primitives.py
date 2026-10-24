import pytest

from wahlwerk_ui.sketch import primitives as sk
from wahlwerk_ui.svg import Drawing


def _d():
    return Drawing(300, 200, scope="ww-t", label="t")


def test_each_piece_lands_on_its_rung():
    d = _d()
    sk.unit(d, 0, 0, 10, 10)
    sk.dimension(d, 0, 0, 10, 0, "w")
    sk.rule(d, 0, 10, 5)
    sk.dot(d, 5, 5)
    markup = d.markup(style=False)
    assert markup.index('class="construction"') < markup.index("layer-dimension")
    assert 'class="dimension"' in markup and 'class="rule"' in markup
    assert 'class="subject-dot"' in markup


def test_crowd_is_deterministic_and_stays_in_its_box():
    centres = sk.crowd(_d(), 10, 20, 100, 50, 40)
    assert centres == sk.crowd(_d(), 10, 20, 100, 50, 40)
    assert len(centres) == 40
    assert all(10 <= x <= 110 and 20 <= y <= 70 for x, y in centres)
    assert sk.crowd(_d(), 0, 0, 10, 10, 0) == []


def test_stimmzettel_crosses_only_the_marked_options():
    d = _d()
    sk.stimmzettel(d, 0, 0, 200, [("erststimme", ["a", "b"], 1), ("zweitstimme", ["x"], None)])
    markup = d.markup(style=False)
    assert markup.count('class="hollow"') == 3
    assert markup.count('class="subject-line"') == 1


def test_table_marks_absent_cells():
    d = _d()
    width, height = sk.table(
        d, 0, 0, ("kind", "count"), (("eligible", "590"), ("", "4")), numeric=(False, True)
    )
    assert width > 0 and height > 0
    assert ">·</text>" in d.markup(style=False)


def test_chamber_draws_one_seat_per_choice():
    d = _d()
    seats = sk.chamber(d, 150, 150, 100, ["yes", "no", "abstain", "absent", "yes"])
    assert len(seats) == 5
    with pytest.raises(ValueError, match="choice"):
        sk.chamber(_d(), 150, 150, 100, ["maybe"])
