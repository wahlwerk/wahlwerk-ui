import math
from itertools import pairwise

import pytest

from wahlwerk_ui.plot.chamber.common import PARTY_COLORS, UNRECORDED_COLOR
from wahlwerk_ui.plot.chamber.seat import hemicycle_svg, seat_layout

BUNDESTAG_2025 = [("linke", 64), ("gruene", 85), ("spd", 120), ("cdu-csu", 208), ("afd", 152)]


@pytest.mark.parametrize("seats", [0, 1, 2, 5, 31, 69, 120, 598, 630, 736])
def test_layout_places_every_seat_once(seats):
    centres, radius = seat_layout(seats)
    assert len(centres) == seats
    assert len(set(centres)) == seats
    assert radius >= 0


@pytest.mark.parametrize("seats", [2, 31, 630])
def test_layout_is_a_hemicycle_ordered_left_to_right(seats):
    centres, _ = seat_layout(seats)
    for x, y in centres:
        assert y >= -1e-9
        assert math.hypot(x, y) <= 1 + 1e-9
    angles = [math.atan2(y, x) for x, y in centres]
    assert all(a >= b - 1e-9 for a, b in pairwise(angles))


@pytest.mark.parametrize("seats", [5, 120, 630])
def test_seats_do_not_overlap(seats):
    centres, radius = seat_layout(seats)
    closest = min(
        math.dist(a, b) for i, a in enumerate(centres) for b in centres[i + 1 :]
    )
    assert closest >= 2 * radius


def test_layout_rejects_bad_counts():
    with pytest.raises(ValueError, match="negative"):
        seat_layout(-1)
    with pytest.raises(TypeError):
        seat_layout(True)
    with pytest.raises(TypeError):
        seat_layout(2.0)


def test_svg_draws_one_circle_per_seat():
    svg = hemicycle_svg(BUNDESTAG_2025)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert svg.count("<circle") == 629
    assert f'fill="{PARTY_COLORS["spd"]}"' in svg
    assert "<title>spd: 120</title>" in svg


def test_svg_draws_unrecorded_seats_grey():
    svg = hemicycle_svg([(None, 3)])
    assert f'fill="{UNRECORDED_COLOR}"' in svg
    assert "<title>unrecorded: 3</title>" in svg


def test_svg_colours_can_be_overridden_and_fall_back():
    svg = hemicycle_svg([("spd", 1), ("xyz", 1)], colors={"spd": "#123456"})
    assert 'fill="#123456"' in svg
    assert svg.count("<g ") == 2


def test_svg_skips_empty_groups_and_rejects_bad_ones():
    assert hemicycle_svg([("spd", 0)]).count("<circle") == 0
    with pytest.raises(ValueError, match="'spd'"):
        hemicycle_svg([("spd", -1)])


def test_svg_escapes_labels():
    assert "<b>" not in hemicycle_svg([("<b>", 1)])
