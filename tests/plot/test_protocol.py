"""The protocol drawing: plain data in, a structured SVG out."""

import pytest

from wahlwerk_ui.plot.protocol import protocol_drawing, protocol_html, protocol_svg

STEPS = [
    {"kind": "SumVotes", "title": "sum the tally", "citation": "Sec. 31", "parameters": [["level", "land"]], "writes": ["total:land"], "stage": 0, "children": []},
    {
        "kind": "RaiseByOverhang",
        "title": "allocate, then repeat",
        "citation": "Sec. 35 (8)",
        "parameters": [["factor", "2"]],
        "writes": ["chamber_size", "overhang"],
        "stage": 1,
        "children": [
            {
                "kind": "AllocateSeats",
                "citation": None,
                "parameters": [],
                "writes": ["overhang"],
                "stage": 0,
                "children": [
                    {"kind": "ApportionSeats", "title": "apportion", "citation": None, "parameters": [], "writes": ["entitlement"], "stage": 0, "children": []},
                    {"kind": "DeductUnitSeats", "title": "deduct", "citation": None, "parameters": [], "writes": ["list_seats", "overhang"], "stage": 1, "children": []},
                ],
            }
        ],
    },
    {"kind": "FillVacantSeatsFromLists", "title": "form the chamber", "citation": None, "parameters": [], "writes": ["chamber"], "stage": 2, "children": []},
]


def test_every_step_is_drawn_once_with_its_citation():
    svg = protocol_svg(STEPS)
    for name in ("SumVotes", "RaiseByOverhang (repeats)", "AllocateSeats", "ApportionSeats", "FillVacantSeatsFromLists"):
        assert svg.count(name) == 1, name
    assert "Sec. 35 (8)" in svg and ">factor=<" in svg and ">2<" in svg
    assert ">→<" in svg and ">total:land<" in svg


def test_frames_and_steps_are_in_the_step_colour():
    markup = protocol_drawing(STEPS).markup()
    assert markup.count('class="step-frame"') == 2  # the loop and the sequence
    assert markup.count('class="step"') == 4  # the leaf steps
    assert 'class="paper"' not in markup  # no concepts given, so no paper blocks
    assert markup.count('class="arrow-group"') == 3  # two between the top steps, one inside


def test_deterministic_and_scoped():
    assert protocol_svg(STEPS) == protocol_svg(STEPS)
    html = protocol_html(STEPS, title="LWG LSA")
    assert html._repr_html_().startswith('<div id="ww-')
    assert "LWG LSA" in html


def test_too_narrow_is_refused():
    with pytest.raises(ValueError, match="too narrow"):
        protocol_drawing(STEPS, width=200)


def test_the_chain_down_to_the_formula_is_drawn():
    call = {"formula": "wahlwerk.calc.plurality.plurality", "call": "plurality(votes, seats=1)"}
    step = {
        "kind": "SingleMandatePerUnit",
        "parameters": [["method", "Plurality"], ["level", "wahlkreis"]],
        "writes": ["unit_mandates"],
        "stage": 1,
        "uses": [{"field": "method", "kind": "Plurality", "arguments": [["seats", "1"]], "parameters": [], "calls": [call]}],
    }
    plain = str(protocol_svg([{**step, "uses": []}]))
    drawn = str(protocol_svg([step]))
    assert "plurality.plurality" in drawn and "plurality.plurality" not in plain
    assert "seats=1" in drawn and "plurality(votes" not in drawn  # what it needs above, the name below
    assert 'class="step"' in drawn  # the step in the step colour
    assert drawn.count('class="paper"') == 1  # the concept, a paper block inside it
    assert "method=Plurality" not in drawn  # drawn as a block, not repeated as a setting


def test_concepts_nest_like_steps():
    inner = {"field": "method.method", "kind": "HareNiemeyer", "parameters": [], "calls": [
        {"formula": "wahlwerk.calc.remainder.largest_remainder", "call": "largest_remainder(votes, seats, quota)"}]}
    outer = {"field": "method", "kind": "MajorityFirst", "parameters": [], "calls": [
        {"formula": "wahlwerk.calc.majority.majority_first", "call": "majority_first(votes, seats, quota)"}]}
    step = {"kind": "ApportionSeats", "parameters": [], "writes": [], "stage": 0, "uses": [outer, inner]}
    drawn = protocol_drawing([step])
    assert str(drawn.svg()).count('class="paper"') == 2


def test_a_loop_shows_its_condition():
    looped = [dict(STEPS[1], condition="while overhang > 0")]
    assert "? while overhang &gt; 0" in protocol_svg(looped)
    assert "while overhang" not in protocol_svg(STEPS[1:2])


def test_outcomes_stand_in_one_column_outside_every_frame():
    import re

    svg = protocol_svg(STEPS, width=640)
    xs = {
        float(x)
        for x, label in re.findall(r'<text[^>]* x="([\d.]+)"[^>]*>([^<]+)</text>', svg)
        if label in ("total:land", "entitlement", "list_seats", "overhang", "chamber")
    }
    assert len(xs) == 1  # nested or not, every fact starts at the same x
    (x,) = xs
    assert x > 640 - min(200, 640 // 3) - 8  # in the margin, right of the boxes


def test_a_step_shows_its_arguments_under_its_title():
    step = {
        "kind": "SingleMandatePerUnit",
        "inputs": [["votes", "erststimme by wahlkreis × option"]],
        "parameters": [["method", "Plurality"]],
        "writes": ["unit_mandates"],
        "stage": 0,
        "children": [],
    }
    svg = protocol_svg([step])
    assert ">SingleMandatePerUnit<" in svg  # the title stays as it is
    # What it is handed, faint; what a counterfactual can swap, strong, on its own line.
    assert "faint" in _label(svg, "votes=erststimme by wahlkreis × option")
    # Only the value is marked: its key plain, the value bold and blue on a pill.
    assert _label(svg, "method=") == "label plain"
    assert _label(svg, "Plurality") == "label selected name"
    assert 'class="pill"' in svg


def _label(svg, content):
    """The class of the text element holding ``content``."""
    import re

    (cls,) = re.findall(r'<text class="([^"]+)"[^>]*>' + re.escape(content) + "<", svg)
    return cls


def test_a_long_fact_wraps_in_the_margin():
    step = {"kind": "SumGroupBy", "parameters": [["section", "erststimme"]],
            "writes": ["erststimme by wahlkreis × option and more words"], "stage": 0, "children": []}
    svg = protocol_svg([step], width=480)
    assert "…" not in svg  # broken at its words, not cut
    assert ">erststimme by<" in svg or ">erststimme by wahlkreis<" in svg


def test_a_setting_is_marked_in_the_plural_too():
    step = {"kind": "ApplyThresholdTo", "inputs": [["votes", "zweitstimme by land × party"]],
            "named": [["section", "zweitstimme"], ["level", "land"], ["to", "party"]],
            "writes": ["eligible parties of zweitstimme"], "stage": 0, "children": []}
    svg = protocol_svg([step], width=900)
    # zweitstimme, land, party in the argument; parties and zweitstimme in the result
    assert svg.count('class="pill"') == 5
