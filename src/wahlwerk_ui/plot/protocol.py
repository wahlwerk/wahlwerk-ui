"""A protocol drawn as a technical drawing: its steps in order, each as a box.

Takes plain data, one mapping per step, as the engine's
``wahlwerk.process.allocation.flow.protocol_data`` writes it:

- ``kind`` (``"ApportionSeats"``), ``title`` (what it does, a few words),
- ``citation`` (``"Sec. 35 (3)"`` or ``None``), ``inputs`` (pairs of argument and the
  fact it takes, optional), ``parameters`` (pairs of field and value),
- ``writes`` (the facts it establishes), ``stage`` (0 for a step reading only the input),
- ``children`` (the steps it holds: a sequence's steps, a loop's block), ``condition``
  (optional: when a loop runs another round, in words),
- ``uses`` (optional: the core concepts it computes with, outermost first, each
  ``field``, ``kind``, ``parameters`` and ``calls``; a field ``method.method`` sits in
  ``method``; ``arguments``, what the step hands it); a call is ``formula`` (its full
  name) and ``call`` (its signature). A step calls no function itself: only its concepts do.

A step is a box of paper, its kind in the name ink and its settings faint under it;
the paragraph it follows sits at its right edge, the facts it writes in the margin, its
stage in the gutter. Two styles keep two things apart: a step, a rule of the law, is
in the step colour; a core concept it computes with (a method such as plurality, a
threshold) is a paper block inside it, with the functions of ``wahlwerk.calc`` it
calls, and a concept that holds another holds its block the same way. A step that holds others is a dashed frame in the step colour (a grouping, not
a thing) around its children; a loop's frame says that it repeats.
Arrows run from each step to the next. Nothing here knows about elections.

Beside the steps, optionally, a column of chambers (``asides``, one per top-level step
or ``None``): what a run of the protocol had decided after that step, as a small half
circle at the step's height. An aside is plain data too: ``seats`` (triples of party,
seats filled, seats still open for it: a party's colour solid, or as an edge only),
``free`` (seats not yet anyone's, hollow), ``standing`` (pairs of party and members
without a seat yet, drawn below the floor) and ``caption`` (a line under it). The number
of seats stands in the middle of the half circle. A step
shorter than its chamber gets the room: the steps move apart, the chamber stays level
with its step. A page that sets each step and its chamber side by side draws them apart:
each top-level step with ``margin=margin_of(steps)``, so the parts line up, and its
chamber with :func:`aside_svg`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from html import escape
from typing import Any

from wahlwerk_ui.html import Html
from wahlwerk_ui.plot.chamber.common import party_tones
from wahlwerk_ui.plot.chamber.seat import seat_layout
from wahlwerk_ui.sketch.primitives import arrow, box, dot, text
from wahlwerk_ui.style import CHAR_WIDTH_PX, FONT_SIZE_PX, css, slug
from wahlwerk_ui.svg import Drawing, Svg, num, scope_id

__all__ = [
    "ASIDE_WIDTH",
    "aside_height",
    "aside_svg",
    "margin_of",
    "protocol_drawing",
    "protocol_html",
    "protocol_svg",
]

Step = Mapping[str, Any]
"""One step as plain data; see the module docstring."""

Aside = Mapping[str, Any]
"""What a run had decided after one top-level step, as plain data; see the module docstring."""

_PAD = 8
_GUTTER = 22  # the stage column
_LINE = FONT_SIZE_PX + 4
_GAP = 14  # between boxes, room for an arrow
_FRAME_PAD = 8
_CONCEPT_PAD = 8  # a concept block inside its step, and inside another concept
_CONCEPT_GAP = 6
_LOOPS = ("Repeat", "Raise")  # a step whose name starts so repeats what it holds


def protocol_drawing(
    steps: Sequence[Step],
    *,
    width: int = 640,
    title: str = "",
    scope: str | None = None,
    asides: Sequence[Aside | None] | None = None,
    margin: int | None = None,
) -> Drawing:
    """The protocol of ``steps`` as a :class:`~wahlwerk_ui.svg.Drawing`; with ``asides``,
    one per step, a chamber beside each step, ``ASIDE_WIDTH`` pixels more to the right.
    ``margin`` fixes the width of the facts' column (:func:`margin_of` a whole protocol),
    so drawings of its parts line up."""
    if asides is not None and len(asides) != len(steps):
        raise ValueError(f"one aside per step: {len(steps)} steps, {len(asides)} asides")
    margin = margin_of(steps, width) if margin is None else margin
    left = _PAD + _GUTTER
    right = width - _PAD - margin
    if right - left < 160:
        raise ValueError(f"width {width} is too narrow for a protocol drawing")
    heights = [_height(step, right - left) for step in steps]
    beside = list(asides) if asides is not None else [None] * len(steps)
    slots = [max(h, aside_height(a)) if a else h for h, a in zip(heights, beside)]
    total = _PAD + sum(slots) + _GAP * max(len(steps) - 1, 0) + _PAD
    extra = ASIDE_WIDTH if asides is not None else 0
    d = Drawing(
        width + extra,
        total,
        scope=scope or scope_id("protocol", repr(steps), repr(asides), width, margin),
        label=title or "protocol",
    )
    if asides is not None:
        _register(d, [a for a in beside if a])
    y: float = _PAD
    for index, (step, height, slot, aside) in enumerate(zip(steps, heights, slots, beside)):
        _draw(d, step, left, right, y, (right, width - _PAD), show_stage=True)
        if aside:
            _draw_aside(d, aside, width, y, ASIDE_WIDTH)
        if index + 1 < len(steps):
            mid = (left + right) / 2
            arrow(d, mid, y + height + 1, mid, y + slot + _GAP - 1)
        y += slot + _GAP
    return d


def margin_of(steps: Sequence[Step], width: int = 640) -> int:
    """The width of the facts' column: as wide as the longest fact, at most a third."""
    longest = max((_width(f"→ {fact}") for fact in _all_writes(steps)), default=0.0)
    return int(min(width // 3, max(120.0, longest + 24)))  # longer facts wrap


def protocol_svg(
    steps: Sequence[Step],
    *,
    width: int = 640,
    title: str = "",
    asides: Sequence[Aside | None] | None = None,
    margin: int | None = None,
) -> Svg:
    """An inline SVG of the protocol; ``Svg.save(dir, name)`` writes it for print."""
    return protocol_drawing(steps, width=width, title=title, asides=asides, margin=margin).svg()


def protocol_html(
    steps: Sequence[Step], *, width: int = 640, title: str = "", asides: Sequence[Aside | None] | None = None
) -> Html:
    """A card with ``title`` over the drawing, for a notebook."""
    scope = scope_id("protocol-card", repr(steps), repr(asides), width, title)
    drawing = protocol_drawing(steps, width=width, title=title, scope=f"{scope}-plot", asides=asides)
    header = f'<div class="card-title strong name">{escape(title)}</div>' if title else ""
    return Html(
        f'<div id="{scope}" class="ww card">'
        f"<style>{css(scope, {})}</style>"
        f"{header}<div>{drawing.markup(style=False)}</div></div>"
    )


# ===========================================================
# The chambers beside the steps
# ===========================================================
ASIDE_WIDTH = 150
"""The width of the column of chambers beside the steps."""


def aside_svg(aside: Aside, *, width: int = ASIDE_WIDTH, labels: Sequence[str | None] = ()) -> Svg:
    """One chamber as decided so far, on its own: for a page that sets each step's
    drawing and its chamber side by side. ``labels``, every party of the run in order,
    keep the colours of parties without a colour of their own the same in each."""
    d = Drawing(width, aside_height(aside, width), scope=scope_id("aside", repr(aside), width, repr(labels)), label="chamber")
    _register(d, [aside], labels)
    _draw_aside(d, aside, 0, 0, width)
    return d.svg()


def _register(d: Drawing, asides: Sequence[Aside], labels: Sequence[str | None] = ()) -> None:
    """The party colours of ``asides``, assigned in the order of ``labels`` and then of
    first appearance."""
    seen = [*labels, *(party for a in asides for party, *_ in [*a.get("seats", ()), *a.get("standing", ())])]
    for key, tone in party_tones([(label, 1) for label in dict.fromkeys(seen)], None):
        d.parties.setdefault(key, tone)


def _aside_kinds(aside: Aside) -> list[str]:
    """The class of each seat, left to right: party by party its filled seats, then its
    open ones; then the seats not yet anyone's."""
    kinds: list[str] = []
    for party, filled, still_open in aside.get("seats", ()):
        kinds += [f"party-{slug(party)}"] * int(filled) + [f"party-{slug(party)}-open"] * int(still_open)
    return kinds + ["hollow"] * int(aside.get("free", 0))


def _radius(width: float) -> float:
    return (width - 24) / 2


def aside_height(aside: Aside, width: float = ASIDE_WIDTH) -> float:
    """The height of a chamber ``width`` wide: the half circle, its caption, and a line
    for members without a seat."""
    standing = _LINE if aside.get("standing") else 0
    return _radius(width) + 14 + _LINE + standing


def _draw_aside(d: Drawing, aside: Aside, x: float, y: float, width: float) -> None:
    """A chamber as decided so far, its top at ``y``."""
    kinds = _aside_kinds(aside)
    radius = _radius(width)
    cx, floor = x + width / 2, y + radius + 2
    centres, seat_r = seat_layout(len(kinds))
    scale = radius / (1 + seat_r) if kinds else 0.0
    for (sx, sy), cls in zip(centres, kinds):
        dot(d, cx + sx * scale, floor - sy * scale, seat_r * scale * 0.85, cls=cls)
    base = floor + seat_r * scale + 2
    d.line("structure", x + 8, base, x + width - 8, base)
    if kinds:  # the size of the chamber, in the middle of its half circle
        text(d, cx, floor - 4, str(len(kinds)), ink="strong", is_name=True)
    caption = str(aside.get("caption", ""))
    if caption:
        text(d, cx, base + _LINE, _fit(caption, width - 8), ink="plain")
    standing = [(party, int(n)) for party, n in aside.get("standing", ()) if int(n) > 0]
    if standing:
        line = "no seat yet: " + ", ".join(f"{party} +{n}" for party, n in standing)
        text(d, cx, base + 2 * _LINE, _fit(line, width - 8), ink="faint")


# ===========================================================
# Layout
# ===========================================================
def _height(step: Step, width: float) -> float:
    """The height of a step ``width`` pixels wide: a box with its lines and concepts, or
    a frame around its children."""
    children = list(step.get("children") or ())
    pad = _FRAME_PAD if children else _CONCEPT_PAD
    concepts = sum(_concept_height(c, width - 2 * pad) + _CONCEPT_GAP for c in _tree(list(step.get("uses") or ())))
    if not children:
        lines = len(_argument_lines(step, width))
        return (1 + lines) * _LINE + 6 + concepts
    inner = sum(_height(c, width - 2 * _FRAME_PAD) for c in children) + _GAP * (len(children) - 1)
    header = 2 * _LINE if _frame_settings(step) else _LINE
    header += _LINE * len(_condition_lines(step, width))
    return header + 4 + concepts + inner + 2 * _FRAME_PAD


def _condition_lines(step: Step, width: float) -> list[str]:
    """A loop's condition, ``? ...``, wrapped to its frame."""
    condition = step.get("condition")
    return _wrap([f"? {condition}"], width - 12) if condition else []


def _all_writes(steps: Sequence[Step]) -> list[str]:
    """Every fact a leaf step of ``steps`` writes, nested ones included."""
    facts: list[str] = []
    for step in steps:
        children = list(step.get("children") or ())
        facts += _all_writes(children) if children else [str(f) for f in step.get("writes") or ()]
    return facts


Concept = tuple[Step, list["Concept"]]
"""A core concept a step uses and the concepts it holds in turn."""


def _tree(uses: list[Step]) -> list[Concept]:
    """The concepts in ``uses`` (outermost first, nested ones named ``method.method``) as
    a tree: each under the longest other field its own field starts with."""
    fields = [str(u.get("field", "")) for u in uses]

    def parent(field: str) -> str | None:
        above = [f for f in fields if field.startswith(f + ".")]
        return max(above, key=len) if above else None

    def children(of: str | None) -> list[Concept]:
        return [(u, children(f)) for u, f in zip(uses, fields) if parent(f) == of]

    return children(None)


def _concept_height(concept: Concept, width: float) -> float:
    use, inner = concept
    lines = 1 + len(_needs_lines(use, width)) + len(use.get("calls") or ())
    return lines * _LINE + 8 + sum(_concept_height(c, width - 2 * _CONCEPT_PAD) + _CONCEPT_GAP for c in inner)


def _draw_concept(d: Drawing, concept: Concept, x1: float, x2: float, y: float) -> None:
    """A core concept as a block inside its step: paper, its name, what it needs (the
    arguments the step hands it and its own settings), the functions it calls by name,
    and the concepts it holds, nested the same way."""
    use, inner = concept
    box(d, x1, y, x2 - x1, _concept_height(concept, x2 - x1))
    text(d, x1 + 6, y + _LINE, str(use.get("kind", "")), ink="strong", is_name=True, anchor="start")
    line_y = y + _LINE
    for line, ink in _needs_lines(use, x2 - x1):
        line_y += _LINE
        if ink == SETTING:
            _setting_text(d, x1 + 6, line_y, line)
        else:
            text(d, x1 + 6, line_y, line, ink=ink, anchor="start")
    for call in use.get("calls") or ():
        line_y += _LINE
        text(d, x1 + 6, line_y, _fit(_call(call), x2 - x1 - 12), ink="plain", anchor="start")
    inner_y = line_y + 6
    for child in inner:
        _draw_concept(d, child, x1 + _CONCEPT_PAD, x2 - _CONCEPT_PAD, inner_y)
        inner_y += _concept_height(child, x2 - x1 - 2 * _CONCEPT_PAD) + _CONCEPT_GAP


_TOKEN = re.compile(r"[A-Za-z0-9_./-]+")
"""A word of a label: a setting's value, a part of a fact's name."""


def _words(step: Step) -> set[str]:
    """The values a step is set to, as words: its settings shown (not those drawn as a
    concept) and those its arguments' facts name (``erststimme`` for
    ``section=erststimme``). Where one shows, it gets a pill."""
    drawn = {str(u.get("field", "")).split(".")[0] for u in step.get("uses") or ()}
    values = [str(v) for k, v in step.get("parameters") or () if k not in drawn]
    values += [str(v) for _, v in step.get("named") or ()]
    return {v for v in values if _TOKEN.fullmatch(v)}


def _plural(word: str) -> str:
    """``party`` to ``parties``, ``option`` to ``options``: a setting shows in the plural
    in a fact's name (``to=party`` in ``eligible parties of zweitstimme``)."""
    return f"{word[:-1]}ies" if word.endswith("y") else f"{word}s"


def _pills(d: Drawing, x: float, y: float, line: str, words: set[str]) -> None:
    """A pill behind each word of ``line`` (drawn from ``x``, baseline ``y``) that is
    one of ``words``: the setting, and where it shows again, marked alike."""
    marked = words | {_plural(word) for word in words}
    for match in _TOKEN.finditer(line):
        if match.group() in marked:
            d.add(
                "dimension",
                "rect",
                {
                    "class": "pill",
                    "x": num(x + match.start() * CHAR_WIDTH_PX - 2),
                    "y": num(y - 0.82 * FONT_SIZE_PX),
                    "width": num(len(match.group()) * CHAR_WIDTH_PX + 4),
                    "height": num(1.12 * FONT_SIZE_PX),
                    "rx": "3",
                },
            )


_VALUE = re.compile(r"=([^,]+)")
"""A setting's value in a line of ``key=value, ...``."""


def _setting_text(d: Drawing, x: float, y: float, line: str) -> None:
    """A line of settings: each key in plain ink, its value bold and blue on a pill, the
    value being what a counterfactual changes."""
    position = 0
    for match in _VALUE.finditer(line):
        start, end = match.span(1)
        _segment(d, x, y, line, position, start, ink="plain")
        value = match.group(1).rstrip()
        _pills(d, x + start * CHAR_WIDTH_PX, y, value, {value})
        text(d, x + start * CHAR_WIDTH_PX, y, value, ink="selected", is_name=True, anchor="start")
        position = end
    _segment(d, x, y, line, position, len(line), ink="plain")


def _segment(d: Drawing, x: float, y: float, line: str, start: int, end: int, *, ink: str) -> None:
    """``line[start:end]`` where it stands in the line; spaces at its ends dropped, its
    place kept (a label's leading space would collapse)."""
    piece = line[start:end]
    stripped = piece.strip()
    if stripped:
        offset = start + len(piece) - len(piece.lstrip())
        text(d, x + offset * CHAR_WIDTH_PX, y, stripped, ink=ink, anchor="start")


Line = tuple[str, str]
"""A line of text and its ink."""

WIRING = "faint"
"""The ink of what a step or concept is handed: the facts it takes, fixed by the protocol."""

SETTING = "selected"
"""What can be swapped: a setting a law sets and a counterfactual changes (``seats=83``,
``share=1/20``, ``factor=2``); its value bold and blue on a pill, its key plain. What a
step is handed stays faint."""


def _lines(wiring: list[str], settings: list[str], width: float) -> list[Line]:
    """What is handed, faint, then what can be swapped, strong, each wrapped to ``width``."""
    room = width - 12
    return [(_fit(line, room), WIRING) for line in _wrap(wiring, room)] + [
        (_fit(line, room), SETTING) for line in _wrap(settings, room)
    ]


def _needs_lines(use: Step, width: float) -> list[Line]:
    """What a concept is given (``votes=one row of votes``, ``seats=1``) and its own
    settings (``share=1/20``)."""
    return _lines(
        [f"{k}={v}" for k, v in use.get("arguments") or ()],
        [f"{k}={v}" for k, v in use.get("parameters") or ()],
        width,
    )


def _argument_lines(step: Step, width: float) -> list[Line]:
    """A step as it is called: its arguments, the facts it takes
    (``votes=erststimme by wahlkreis × option``), then its settings not drawn as a
    concept; its title when it has neither."""
    drawn = {str(u.get("field", "")).split(".")[0] for u in step.get("uses") or ()}
    wiring = [f"{k}={v}" for k, v in step.get("inputs") or ()]
    settings = [f"{k}={v}" for k, v in step.get("parameters") or () if k not in drawn]
    if not wiring and not settings:
        return [(_fit(str(step.get("title", "")), width - 12), WIRING)]
    return _lines(wiring, settings, width)


def _wrap(items: list[str], room: float) -> list[str]:
    """``items`` joined with commas into lines of at most ``room`` pixels."""
    lines: list[str] = []
    for item in items:
        if lines and _width(f"{lines[-1]}, {item}") <= room:
            lines[-1] = f"{lines[-1]}, {item}"
            continue
        if lines:
            lines[-1] += ","
        # An item too long for a line breaks at its spaces.
        line = ""
        for word in item.split(" "):
            if line and _width(f"{line} {word}") > room:
                lines.append(line)
                line = "  " + word
            else:
                line = f"{line} {word}" if line else word
        lines.append(line)
    return lines


def _call(call: Step) -> str:
    """``remainder.largest_remainder``: the function by name, its module of
    ``wahlwerk.calc`` first; what it needs stands above it."""
    return str(call.get("formula", "")).removeprefix("wahlwerk.calc.")


def _draw(
    d: Drawing, step: Step, x1: float, x2: float, y: float, column: tuple[float, float], *, show_stage: bool
) -> None:
    height = _height(step, x2 - x1)
    kind = str(step.get("kind", ""))
    citation = step.get("citation") or ""
    if show_stage and "stage" in step:
        text(d, _PAD + _GUTTER / 2, y + _LINE, str(step["stage"]), ink="faint")
    _writes(d, step, y, height, column)
    children = list(step.get("children") or ())
    if not children:
        # A step is a rule of the law, in the step colour; the core concepts it computes
        # with sit inside it as paper blocks, down to the functions they call.
        box(d, x1, y, x2 - x1, height, cls="step")
        text(d, x1 + 6, y + _LINE, kind, ink="strong", is_name=True, anchor="start")
        if citation:
            text(d, x2 - 6, y + _LINE, citation, ink="faint", anchor="end")
        uses = list(step.get("uses") or ())
        # Its arguments, the facts it takes, and its settings: the step as a call.
        lines = _argument_lines(step, x2 - x1)
        words = _words(step)
        for number, (line, ink) in enumerate(lines, start=2):
            if ink == SETTING:
                _setting_text(d, x1 + 6, y + number * _LINE, line)
                continue
            _pills(d, x1 + 6, y + number * _LINE, line, words)
            text(d, x1 + 6, y + number * _LINE, line, ink=ink, anchor="start")
        # The concepts it computes with: a step calls no function itself, only they do.
        inner_y = y + (1 + len(lines)) * _LINE + 6
        for concept in _tree(uses):
            _draw_concept(d, concept, x1 + _CONCEPT_PAD, x2 - _CONCEPT_PAD, inner_y)
            inner_y += _concept_height(concept, x2 - x1 - 2 * _CONCEPT_PAD) + _CONCEPT_GAP
        return
    is_loop = kind.startswith(_LOOPS)
    label = kind  # a sequence is a step, named like one
    if is_loop:
        label += " (repeats)"
    _frame(d, x1, y, x2 - x1, height)
    # The citation in the top right corner, as on a step's box; the name gets the rest.
    room = x2 - x1 - 12
    if citation:
        text(d, x2 - 6, y + _LINE, citation, ink="faint", anchor="end")
        room -= _width(citation) + 12
    text(d, x1 + 6, y + _LINE, _fit(label, room), ink="plain", is_name=True, anchor="start")
    header = _LINE
    uses = list(step.get("uses") or ())
    settings = _frame_settings(step)
    if settings:
        header += _LINE
        _setting_text(d, x1 + 6, y + header, _fit(settings, x2 - x1 - 12))
    # A loop's condition: when it runs another round, the check before each.
    for line in _condition_lines(step, x2 - x1):
        header += _LINE
        text(d, x1 + 6, y + header, line, ink="plain", anchor="start")
    inner_y = y + header + 4 + _FRAME_PAD
    # A loop's own concepts (the Fraktion size it compares with) before what it repeats.
    for concept in _tree(uses):
        _draw_concept(d, concept, x1 + _FRAME_PAD, x2 - _FRAME_PAD, inner_y)
        inner_y += _concept_height(concept, x2 - x1 - 2 * _FRAME_PAD) + _CONCEPT_GAP
    for index, child in enumerate(children):
        child_height = _height(child, x2 - x1 - 2 * _FRAME_PAD)
        _draw(d, child, x1 + _FRAME_PAD, x2 - _FRAME_PAD, inner_y, column, show_stage=False)
        if index + 1 < len(children):
            mid = (x1 + x2) / 2
            arrow(d, mid, inner_y + child_height + 1, mid, inner_y + child_height + _GAP - 1)
        inner_y += child_height + _GAP


def _frame_settings(step: Step) -> str:
    """A frame's settings not drawn as a concept block inside it, as ``k=v, ...``."""
    drawn = {str(u.get("field", "")).split(".")[0] for u in step.get("uses") or ()}
    return ", ".join(f"{k}={v}" for k, v in step.get("parameters") or () if k not in drawn)


def _frame(d: Drawing, x: float, y: float, w: float, h: float) -> None:
    """The dashed frame of steps that act as one, in the step colour."""
    d.add("structure", "rect", {"class": "step-frame", "x": num(x), "y": num(y), "width": num(w), "height": num(h), "rx": "2"})


def _writes(d: Drawing, step: Step, y: float, height: float, column: tuple[float, float]) -> None:
    """The facts a leaf step writes, one under the other, in the margin column beside
    its box, each wrapped at its words to the margin: every step's facts start at the
    same x, outside every frame, however deep the step is nested. As many lines as the
    box is tall; the last says how many more there are."""
    if step.get("children"):
        return
    facts = [str(fact) for fact in step.get("writes") or ()]
    if not facts:
        return
    start, end = column
    x, room = start + 10, end - start - 10
    # The arrow once, the facts under each other after it (SVG collapses leading spaces).
    indent = _width("→ ")
    lines: list[str] = []
    for fact in facts:
        lines += _break(fact, room - indent)
    fits = max(1, int((height - 4) // _LINE))
    if len(lines) > fits:
        lines = [*lines[: fits - 1], f"+{len(lines) - fits + 1} more"]
    text(d, x, y + _LINE, "→", ink="plain", anchor="start")
    words = _words(step)
    for number, line in enumerate(lines, start=1):
        _pills(d, x + indent, y + number * _LINE, line, words)
        text(d, x + indent, y + number * _LINE, line, ink="plain", anchor="start")


def _break(label: str, room: float) -> list[str]:
    """``label`` broken at its spaces into lines of at most ``room`` pixels; a word
    longer than a line is cut."""
    lines: list[str] = []
    for word in label.split(" "):
        if lines and _width(f"{lines[-1]} {word}") <= room:
            lines[-1] = f"{lines[-1]} {word}"
        else:
            lines.append(word)
    return [_fit(line, room) for line in lines]


def _width(label: str) -> float:
    return len(label) * CHAR_WIDTH_PX


def _fit(label: str, room: float) -> str:
    """``label`` cut to ``room`` pixels, with an ellipsis if cut."""
    most = int(room // CHAR_WIDTH_PX)
    if len(label) <= most:
        return label
    return label[: max(most - 1, 0)] + "…"
