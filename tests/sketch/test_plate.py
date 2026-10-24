import pytest

from wahlwerk_ui.sketch import primitives as sk
from wahlwerk_ui.sketch.plate import Plate
from wahlwerk_ui.svg import Svg


def _plate():
    plate = Plate("demo", "a demo")
    a = plate.panel("one", "first", caption=("one", "a note"))
    sk.dot(a.art, 10, 10)
    b = plate.panel("two", "second", caption=("two",))
    sk.unit(b.art, 0, 0, 50, 50, "unit")
    return plate


def test_panels_are_numbered_in_order():
    assert [p.number for p in _plate().panels] == [1, 2]


def test_one_svg_with_every_panel_titles_and_captions():
    svg = _plate().svg()
    assert isinstance(svg, Svg)
    assert 'id="panel-one"' in svg and 'id="panel-two"' in svg
    assert ">1  first</text>" in svg and ">a note</text>" in svg
    assert svg.rindex("layer-labels") > svg.rindex("panel-two")  # labels on top


def test_ids_are_unique_across_panels():
    svg = str(_plate().svg())
    assert 'id="one.layer-subject"' in svg and 'id="two.layer-construction"' in svg


def test_to_dict_gives_one_svg_per_panel():
    data = _plate().to_dict()
    assert [p["name"] for p in data["panels"]] == ["one", "two"]
    assert data["panels"][0]["caption"] == ["one", "a note"]
    assert data["panels"][0]["svg"].startswith("<svg")


def test_caption_is_a_name_and_two_lines_at_most():
    with pytest.raises(ValueError, match="at most 2"):
        Plate("p").panel("x", "x", caption=("a", "b", "c", "d"))
    with pytest.raises(ValueError, match="already has"):
        plate = Plate("p")
        plate.panel("x", "x")
        plate.panel("x", "y")


def test_a_slot_is_as_wide_as_its_widest_line():
    plate = Plate("p")
    panel = plate.panel("x", "x", width=20, caption=("a long caption line",))
    assert panel.slot > 20


def test_save_writes_the_plate(tmp_path):
    path = _plate().save(tmp_path)
    assert path.name == "demo.svg" and "var(" not in path.read_text("utf-8")
