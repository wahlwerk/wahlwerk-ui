"""A protocol drawn as a technical drawing: its steps in order, each as a box.

Takes plain data, one mapping per step, as the engine's
``wahlwerk.process.allocation.flow.protocol_data`` writes it:

- ``kind`` (``"ApportionSeats"``), ``title`` (what it does, a few words),
- ``citation`` (``"Sec. 35 (3)"`` or ``None``), ``parameters`` (pairs of field and value),
- ``writes`` (the facts it establishes), ``stage`` (0 for a step reading only the input),
- ``children`` (the steps it holds: a sequence's steps, a loop's block),
- ``uses`` (optional: the models it computes with, each ``field``, ``kind`` and the
  ``formula`` it calls, outermost first).

A step is a box of paper, its kind in the name ink and its settings faint under it;
the paragraph it follows sits at its right edge, the facts it writes in the margin, its
stage in the gutter; under its settings, the chain down to its formula, one line per
model it uses. A step that holds others is a dashed frame (construction, like a
unit: a grouping, not a thing) around its children; a loop's frame says that it repeats.
Arrows run from each step to the next. Nothing here knows about elections.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from typing import Any

from wahlwerk_ui.html import Html
from wahlwerk_ui.sketch.primitives import arrow, box, text, unit
from wahlwerk_ui.style import CHAR_WIDTH_PX, FONT_SIZE_PX, css
from wahlwerk_ui.svg import Drawing, Svg, scope_id

__all__ = ["protocol_drawing", "protocol_html", "protocol_svg"]

Step = Mapping[str, Any]
"""One step as plain data; see the module docstring."""

_PAD = 8
_GUTTER = 22  # the stage column
_LINE = FONT_SIZE_PX + 4
_GAP = 14  # between boxes, room for an arrow
_FRAME_PAD = 8
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
    heights = [_height(step) for step in steps]
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
def _height(step: Step) -> float:
    """The height of a step: two lines in a box, or a frame around its children."""
    children = list(step.get("children") or ())
    if not children:
        return (2 + len(step.get("uses") or ())) * _LINE + 6
    inner = sum(_height(c) for c in children) + _GAP * (len(children) - 1)
    header = 2 * _LINE if step.get("parameters") or step.get("citation") else _LINE
    return header + 4 + inner + 2 * _FRAME_PAD


def _draw(d: Drawing, step: Step, x1: float, x2: float, y: float, edge: float, *, show_stage: bool) -> None:
    height = _height(step)
    kind = str(step.get("kind", ""))
    citation = step.get("citation") or ""
    if show_stage and "stage" in step:
        text(d, _PAD + _GUTTER / 2, y + _LINE, str(step["stage"]), ink="faint")
    _writes(d, step, x2, y, edge)
    children = list(step.get("children") or ())
    if not children:
        box(d, x1, y, x2 - x1, height)
        text(d, x1 + 6, y + _LINE, kind, ink="strong", is_name=True, anchor="start")
        if citation:
            text(d, x2 - 6, y + _LINE, citation, ink="faint", anchor="end")
        settings = ", ".join(f"{k}={v}" for k, v in step.get("parameters") or ())
        text(d, x1 + 6, y + 2 * _LINE, _fit(settings or str(step.get("title", "")), x2 - x1 - 12), ink="faint", anchor="start")
        # The chain down to the formula: each model the step computes with, indented by
        # how deep it sits, and the function in wahlwerk.calc it calls.
        for number, use in enumerate(step.get("uses") or (), start=3):
            depth = str(use.get("field", "")).count(".")
            formula = str(use.get("formula", "")).removeprefix("wahlwerk.")
            line = f"{'  ' * depth}↳ {use.get('kind', '')}: {formula}"
            text(d, x1 + 6, y + number * _LINE, _fit(line, x2 - x1 - 12), ink="plain", anchor="start")
        return
    is_loop = kind.startswith(_LOOPS)
    label = str(step.get("title", kind)) if kind == "StepSequence" else kind
    if is_loop:
        label += " (repeats)"
    unit(d, x1, y, x2 - x1, height)
    # A frame's title is often long (a sequence's name), so its citation goes under it,
    # with the settings, rather than beside it.
    text(d, x1 + 6, y + _LINE, _fit(label, x2 - x1 - 12), ink="plain", is_name=True, anchor="start")
    header = _LINE
    settings = ", ".join(f"{k}={v}" for k, v in step.get("parameters") or ())
    second = " · ".join(part for part in (citation, settings) if part)
    if second:
        header += _LINE
        text(d, x1 + 6, y + header, _fit(second, x2 - x1 - 12), ink="faint", anchor="start")
    inner_y = y + header + 4 + _FRAME_PAD
    for index, child in enumerate(children):
        child_height = _height(child)
        _draw(d, child, x1 + _FRAME_PAD, x2 - _FRAME_PAD, inner_y, edge, show_stage=False)
        if index + 1 < len(children):
            mid = (x1 + x2) / 2
            arrow(d, mid, inner_y + child_height + 1, mid, inner_y + child_height + _GAP - 1)
        inner_y += child_height + _GAP


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
