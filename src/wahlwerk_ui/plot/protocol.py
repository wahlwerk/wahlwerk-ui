"""A protocol drawn as a technical drawing: its steps in order, each as a box.

Takes plain data, one mapping per step, as the engine's
``wahlwerk.process.allocation.flow.protocol_data`` writes it:

- ``kind`` (``"ApportionSeats"``), ``title`` (what it does, a few words),
- ``citation`` (``"Sec. 35 (3)"`` or ``None``), ``parameters`` (pairs of field and value),
- ``writes`` (the facts it establishes), ``stage`` (0 for a step reading only the input),
- ``children`` (the steps it holds: a sequence's steps, a loop's block),
- ``uses`` (optional: the core concepts it computes with, outermost first, each
  ``field``, ``kind``, ``parameters`` and ``calls``; a field ``method.method`` sits in
  ``method``; ``arguments``, what the step hands it) and ``calls`` (optional: functions
  it calls itself); a call is ``formula`` (its full name) and ``call`` (its signature).

A step is a box of paper, its kind in the name ink and its settings faint under it;
the paragraph it follows sits at its right edge, the facts it writes in the margin, its
stage in the gutter. Two styles keep two things apart: a step, a rule of the law, is
in the step colour; a core concept it computes with (a method such as plurality, a
threshold) is a paper block inside it, with the functions of ``wahlwerk.calc`` it
calls, and a concept that holds another holds its block the same way. A step that holds others is a dashed frame in the step colour (a grouping, not
a thing) around its children; a loop's frame says that it repeats.
Arrows run from each step to the next. Nothing here knows about elections.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from typing import Any

from wahlwerk_ui.html import Html
from wahlwerk_ui.sketch.primitives import arrow, box, text
from wahlwerk_ui.style import CHAR_WIDTH_PX, FONT_SIZE_PX, css
from wahlwerk_ui.svg import Drawing, Svg, num, scope_id

__all__ = ["protocol_drawing", "protocol_html", "protocol_svg"]

Step = Mapping[str, Any]
"""One step as plain data; see the module docstring."""

_PAD = 8
_GUTTER = 22  # the stage column
_LINE = FONT_SIZE_PX + 4
_GAP = 14  # between boxes, room for an arrow
_FRAME_PAD = 8
_CONCEPT_PAD = 8  # a concept block inside its step, and inside another concept
_CONCEPT_GAP = 6
_LOOPS = ("Repeat", "Raise")  # a step whose name starts so repeats what it holds


def protocol_drawing(
    steps: Sequence[Step], *, width: int = 640, title: str = "", scope: str | None = None
) -> Drawing:
    """The protocol of ``steps`` as a :class:`~wahlwerk_ui.svg.Drawing`."""
    margin = min(200, width // 3)  # the facts written, at the right
    left = _PAD + _GUTTER
    right = width - _PAD - margin
    if right - left < 160:
        raise ValueError(f"width {width} is too narrow for a protocol drawing")
    heights = [_height(step, right - left) for step in steps]
    total = _PAD + sum(heights) + _GAP * max(len(steps) - 1, 0) + _PAD
    d = Drawing(width, total, scope=scope or scope_id("protocol", repr(steps), width), label=title or "protocol")
    y: float = _PAD
    for index, (step, height) in enumerate(zip(steps, heights)):
        _draw(d, step, left, right, y, width - _PAD, show_stage=True)
        if index + 1 < len(steps):
            mid = (left + right) / 2
            arrow(d, mid, y + height + 1, mid, y + height + _GAP - 1)
        y += height + _GAP
    return d


def protocol_svg(steps: Sequence[Step], *, width: int = 640, title: str = "") -> Svg:
    """An inline SVG of the protocol; ``Svg.save(dir, name)`` writes it for print."""
    return protocol_drawing(steps, width=width, title=title).svg()


def protocol_html(steps: Sequence[Step], *, width: int = 640, title: str = "") -> Html:
    """A card with ``title`` over the drawing, for a notebook."""
    scope = scope_id("protocol-card", repr(steps), width, title)
    drawing = protocol_drawing(steps, width=width, title=title, scope=f"{scope}-plot")
    header = f'<div class="card-title strong name">{escape(title)}</div>' if title else ""
    return Html(
        f'<div id="{scope}" class="ww card">'
        f"<style>{css(scope, {})}</style>"
        f"{header}<div>{drawing.markup(style=False)}</div></div>"
    )


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
        given = len(_wrap(_given(step), width - 12)) if step.get("calls") else 0
        return (2 + given + len(step.get("calls") or ())) * _LINE + 6 + concepts
    inner = sum(_height(c, width - 2 * _FRAME_PAD) for c in children) + _GAP * (len(children) - 1)
    header = 2 * _LINE if step.get("parameters") or step.get("citation") else _LINE
    return header + 4 + concepts + inner + 2 * _FRAME_PAD


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
    lines = 1 + len(_wrap(_needs(use), width - 12)) + len(use.get("calls") or ())
    return lines * _LINE + 8 + sum(_concept_height(c, width - 2 * _CONCEPT_PAD) + _CONCEPT_GAP for c in inner)


def _draw_concept(d: Drawing, concept: Concept, x1: float, x2: float, y: float) -> None:
    """A core concept as a block inside its step: paper, its name, what it needs (the
    arguments the step hands it and its own settings), the functions it calls by name,
    and the concepts it holds, nested the same way."""
    use, inner = concept
    box(d, x1, y, x2 - x1, _concept_height(concept, x2 - x1))
    text(d, x1 + 6, y + _LINE, str(use.get("kind", "")), ink="strong", is_name=True, anchor="start")
    line_y = y + _LINE
    for line in _wrap(_needs(use), x2 - x1 - 12):
        line_y += _LINE
        text(d, x1 + 6, line_y, _fit(line, x2 - x1 - 12), ink="faint", anchor="start")
    for call in use.get("calls") or ():
        line_y += _LINE
        text(d, x1 + 6, line_y, _fit(_call(call), x2 - x1 - 12), ink="plain", anchor="start")
    inner_y = line_y + 6
    for child in inner:
        _draw_concept(d, child, x1 + _CONCEPT_PAD, x2 - _CONCEPT_PAD, inner_y)
        inner_y += _concept_height(child, x2 - x1 - 2 * _CONCEPT_PAD) + _CONCEPT_GAP


def _needs(use: Step) -> list[str]:
    """``votes=erststimme per nominee``, ``seats=1``: what a concept is given and set to."""
    return [f"{k}={v}" for k, v in (*(use.get("arguments") or ()), *(use.get("parameters") or ()))]


def _given(step: Step) -> list[str]:
    """What a step hands the functions it calls itself, as ``seats=chamber_size``."""
    return [f"{k}={v}" for k, v in step.get("arguments") or ()]


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


def _draw(d: Drawing, step: Step, x1: float, x2: float, y: float, edge: float, *, show_stage: bool) -> None:
    height = _height(step, x2 - x1)
    kind = str(step.get("kind", ""))
    citation = step.get("citation") or ""
    if show_stage and "stage" in step:
        text(d, _PAD + _GUTTER / 2, y + _LINE, str(step["stage"]), ink="faint")
    _writes(d, step, x2, y, edge)
    children = list(step.get("children") or ())
    if not children:
        # A step is a rule of the law, in the step colour; the core concepts it computes
        # with sit inside it as paper blocks, down to the functions they call.
        box(d, x1, y, x2 - x1, height, cls="step")
        text(d, x1 + 6, y + _LINE, kind, ink="strong", is_name=True, anchor="start")
        if citation:
            text(d, x2 - 6, y + _LINE, citation, ink="faint", anchor="end")
        uses = list(step.get("uses") or ())
        drawn = {str(u.get("field", "")).split(".")[0] for u in uses}
        settings = ", ".join(f"{k}={v}" for k, v in step.get("parameters") or () if k not in drawn)
        text(d, x1 + 6, y + 2 * _LINE, _fit(settings or str(step.get("title", "")), x2 - x1 - 12), ink="faint", anchor="start")
        # The concepts it computes with first, then the functions it calls itself with
        # what they give (the caucus size: the quota, then the whole seats of it).
        inner_y = y + 2 * _LINE + 6
        for concept in _tree(uses):
            _draw_concept(d, concept, x1 + _CONCEPT_PAD, x2 - _CONCEPT_PAD, inner_y)
            inner_y += _concept_height(concept, x2 - x1 - 2 * _CONCEPT_PAD) + _CONCEPT_GAP
        line_y = inner_y - 6
        if step.get("calls"):
            for line in _wrap(_given(step), x2 - x1 - 12):
                line_y += _LINE
                text(d, x1 + 6, line_y, _fit(line, x2 - x1 - 12), ink="faint", anchor="start")
        for call in step.get("calls") or ():
            line_y += _LINE
            text(d, x1 + 6, line_y, _fit(_call(call), x2 - x1 - 12), ink="plain", anchor="start")
        return
    is_loop = kind.startswith(_LOOPS)
    label = kind  # a sequence is a step, named like one
    if is_loop:
        label += " (repeats)"
    _frame(d, x1, y, x2 - x1, height)
    # A frame's citation goes under its name,
    # with the settings, rather than beside it.
    text(d, x1 + 6, y + _LINE, _fit(label, x2 - x1 - 12), ink="plain", is_name=True, anchor="start")
    header = _LINE
    uses = list(step.get("uses") or ())
    drawn = {str(u.get("field", "")).split(".")[0] for u in uses}
    settings = ", ".join(f"{k}={v}" for k, v in step.get("parameters") or () if k not in drawn)
    second = " · ".join(part for part in (citation, settings) if part)
    if second:
        header += _LINE
        text(d, x1 + 6, y + header, _fit(second, x2 - x1 - 12), ink="faint", anchor="start")
    inner_y = y + header + 4 + _FRAME_PAD
    # A loop's own concepts (the Fraktion size it compares with) before what it repeats.
    for concept in _tree(uses):
        _draw_concept(d, concept, x1 + _FRAME_PAD, x2 - _FRAME_PAD, inner_y)
        inner_y += _concept_height(concept, x2 - x1 - 2 * _FRAME_PAD) + _CONCEPT_GAP
    for index, child in enumerate(children):
        child_height = _height(child, x2 - x1 - 2 * _FRAME_PAD)
        _draw(d, child, x1 + _FRAME_PAD, x2 - _FRAME_PAD, inner_y, edge, show_stage=False)
        if index + 1 < len(children):
            mid = (x1 + x2) / 2
            arrow(d, mid, inner_y + child_height + 1, mid, inner_y + child_height + _GAP - 1)
        inner_y += child_height + _GAP


def _frame(d: Drawing, x: float, y: float, w: float, h: float) -> None:
    """The dashed frame of steps that act as one, in the step colour."""
    d.add("structure", "rect", {"class": "step-frame", "x": num(x), "y": num(y), "width": num(w), "height": num(h), "rx": "2"})


def _writes(d: Drawing, step: Step, x: float, y: float, edge: float) -> None:
    """The facts a leaf step writes, faint in the margin beside its box."""
    if step.get("children"):
        return
    facts = list(step.get("writes") or ())
    if not facts:
        return
    room = edge - x - 10
    lines: list[str] = []
    for fact in facts:
        candidate = f"{lines[-1]}, {fact}" if lines else f"→ {fact}"
        if lines and _width(candidate) <= room:
            lines[-1] = candidate
        else:
            lines.append(candidate if not lines else f"  {fact}")
    for number, line in enumerate(lines[:2], start=1):
        last = number == 2 and len(lines) > 2
        text(d, x + 10, y + number * _LINE, _fit(line + (", …" if last else ""), room), ink="plain", anchor="start")


def _width(label: str) -> float:
    return len(label) * CHAR_WIDTH_PX


def _fit(label: str, room: float) -> str:
    """``label`` cut to ``room`` pixels, with an ellipsis if cut."""
    most = int(room // CHAR_WIDTH_PX)
    if len(label) <= most:
        return label
    return label[: max(most - 1, 0)] + "…"
