import pytest

from wahlwerk_ui.plot.chamber.seat import hemicycle_svg
from wahlwerk_ui.svg import LAYERS, Drawing, Svg, scope_id


def test_layers_keep_their_order_whatever_the_drawing_order():
    d = Drawing(10, 10, scope="ww-t", label="t")
    d.label(1, 1, "x")
    d.line("construction", 0, 0, 1, 1)
    markup = d.markup()
    assert markup.index("layer-construction") < markup.index("layer-labels")
    assert 'inkscape:groupmode="layer"' in markup
    assert LAYERS[0] == "construction" and LAYERS[-1] == "labels"


def test_unknown_layer_and_ink_are_errors():
    d = Drawing(10, 10, scope="ww-t", label="t")
    with pytest.raises(KeyError, match="layers are"):
        d.add("seats", "circle")
    with pytest.raises(ValueError, match="ink"):
        d.label(0, 0, "x", ink="bold")


def test_markup_leaves_the_drawing_reusable():
    d = Drawing(10, 10, scope="ww-t", label="t")
    d.line("structure", 0, 0, 1, 1)
    assert d.markup() == d.markup()
    assert "<style" not in d.markup(style=False)


def test_scope_id_is_deterministic():
    assert scope_id("a", 1) == scope_id("a", 1) != scope_id("a", 2)


def test_save_writes_the_printable_variant(tmp_path):
    svg = hemicycle_svg([("spd", 5), ("cdu", 4)])
    assert isinstance(svg, Svg) and svg._repr_svg_() == svg
    path = svg.save(tmp_path / "out", "chamber")
    text = path.read_text("utf-8")
    assert path.name == "chamber.svg"
    assert text.startswith("<?xml") and "var(" not in text and "@media" not in text
