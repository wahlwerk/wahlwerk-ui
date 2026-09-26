import pytest

from wahlwerk_ui.plot.chamber.common import PARTY_COLORS, UNRECORDED_COLOR
from wahlwerk_ui.plot.chamber.pie import half_pie_svg

BUNDESTAG_2025 = [("linke", 64), ("gruene", 85), ("spd", 120), ("cdu-csu", 208), ("afd", 152)]


def test_one_wedge_per_group_with_the_total_in_the_centre():
    svg = half_pie_svg(BUNDESTAG_2025)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert svg.count("<path") == 5
    assert f'fill="{PARTY_COLORS["spd"]}"' in svg
    assert "<title>spd: 120</title>" in svg
    assert ">629</text>" in svg


def test_solid_pie_has_no_total():
    svg = half_pie_svg(BUNDESTAG_2025, hole=0)
    assert svg.count("<path") == 5
    assert "<text" not in svg


def test_skips_empty_groups_and_draws_unrecorded_grey():
    svg = half_pie_svg([("spd", 0), (None, 3)])
    assert svg.count("<path") == 1
    assert f'fill="{UNRECORDED_COLOR}"' in svg


def test_empty_chamber_draws_nothing():
    assert "<path" not in half_pie_svg([])


def test_rejects_bad_input():
    with pytest.raises(ValueError, match="hole"):
        half_pie_svg([("spd", 1)], hole=1)
    with pytest.raises(ValueError, match="'spd'"):
        half_pie_svg([("spd", -1)])
