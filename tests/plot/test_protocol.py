"""The protocol drawing: plain data in, a structured SVG out."""

import pytest

from wahlwerk_ui.plot.protocol import protocol_drawing, protocol_html, protocol_svg

STEPS = [
    {"kind": "SumVotes", "title": "sum the tally", "citation": "Sec. 31", "parameters": [["level", "land"]], "writes": ["total:land"], "stage": 0, "children": []},
    {
        "kind": "RepeatForMehrsitze",
        "title": "allocate, then repeat",
        "citation": "Sec. 35 (8)",
        "parameters": [["factor", "2"]],
        "writes": ["chamber_size", "overhang"],
        "stage": 1,
        "children": [
            {
                "kind": "StepSequence",
                "title": "allocate the seats of one chamber size",
                "citation": None,
                "parameters": [],
                "writes": ["overhang"],
                "stage": 0,
                "children": [
                    {"kind": "ApportionSeats", "title": "apportion", "citation": None, "parameters": [], "writes": ["entitlement"], "stage": 0, "children": []},
                    {"kind": "DeductDistrictSeats", "title": "deduct", "citation": None, "parameters": [], "writes": ["list_seats", "overhang"], "stage": 1, "children": []},
                ],
            }
        ],
    },
    {"kind": "FormChamber", "title": "form the chamber", "citation": None, "parameters": [], "writes": ["chamber"], "stage": 2, "children": []},
]


def test_every_step_is_drawn_once_with_its_citation():
    svg = protocol_svg(STEPS)
    for name in ("SumVotes", "RepeatForMehrsitze (repeats)", "allocate the seats of one chamber size", "ApportionSeats", "FormChamber"):
        assert svg.count(name) == 1, name
    assert "Sec. 35 (8)" in svg and "factor=2" in svg
    assert "→ total:land" in svg


def test_frames_are_construction_and_steps_are_paper():
    markup = protocol_drawing(STEPS).markup()
    assert markup.count('class="construction"') == 2  # the loop and the sequence
    assert markup.count('class="paper"') == 4  # the leaf steps
    assert markup.count('class="arrow-group"') == 3  # two between the top steps, one inside


def test_deterministic_and_scoped():
    assert protocol_svg(STEPS) == protocol_svg(STEPS)
    html = protocol_html(STEPS, title="LWG LSA")
    assert html._repr_html_().startswith('<div id="ww-')
    assert "LWG LSA" in html


def test_too_narrow_is_refused():
    with pytest.raises(ValueError, match="too narrow"):
        protocol_drawing(STEPS, width=200)
