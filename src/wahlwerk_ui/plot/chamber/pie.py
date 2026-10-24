"""A chamber as a half pie: one wedge per group, sized by seats.

Wedges run left to right in seating order over the upper half circle. With a ``hole``
it is a half ring, with the total in the centre, matching the seat hemicycle. Drawn as a
technical drawing (:mod:`wahlwerk_ui.style`): a dashed half axis, a floor line, the
wedges as the one saturated thing, and, if asked for, the majority as a reference mark.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from wahlwerk_ui.plot.chamber.common import (
    Group,
    check_groups,
    label_of,
    majority_of,
    party_tones,
)
from wahlwerk_ui.style import FONT_SIZE_PX, Tone
from wahlwerk_ui.svg import Drawing, Svg, num, scope_id

__all__ = ["half_pie_drawing", "half_pie_svg"]

_PAD = 2.0
"""Margin around the drawing, px."""


def half_pie_drawing(
    groups: Sequence[Group],
    *,
    colors: Mapping[str, str | Tone] | None = None,
    width: int = 240,
    hole: float = 0.4,
    majority: bool = False,
    scope: str | None = None,
) -> Drawing:
    """The half pie of ``groups`` as a :class:`~wahlwerk_ui.svg.Drawing`.

    ``hole`` is the inner radius as a fraction of the outer one; ``0`` gives a solid
    pie (and no total in the centre). ``majority`` adds a reference mark where an
    absolute majority is complete; off by default.
    """
    if not 0 <= hole < 1:
        raise ValueError(f"hole must be in [0, 1), got {hole}")
    check_groups(groups)
    total = sum(count for _, count in groups)
    show_majority = majority and total >= 2
    top = _PAD + (FONT_SIZE_PX + 6 if show_majority else 0)
    outer = width / 2 - _PAD
    inner = hole * outer
    cx, cy = width / 2, top + outer
    floor = cy + 2

    def point(radius: float, angle: float) -> tuple[float, float]:
        return cx + radius * math.cos(angle), cy - radius * math.sin(angle)

    def xy(radius: float, angle: float) -> str:
        x, y = point(radius, angle)
        return f"{num(x)},{num(y)}"

    drawing = Drawing(
        width,
        math.ceil(floor + _PAD),
        scope=scope or scope_id("pie", tuple(groups), colors, width, hole, majority),
        label=f"{total} seats",
    )

    # Construction: the half axis; structure: the floor.
    if total:
        start = inner + 2 if inner > 0 else 0.0
        drawing.line("construction", cx, cy - start, cx, cy - outer - 2)
    drawing.line("structure", _PAD, floor, width - _PAD, floor)

    # Subject: one wedge per group.
    done = 0
    for (label, count), (key, color) in zip(groups, party_tones(groups, colors)):
        if count == 0:
            continue
        drawing.parties.setdefault(key, color)
        a0 = math.pi * (1 - done / total)
        a1 = math.pi * (1 - (done + count) / total)
        # Outer arc clockwise on screen (left to right), inner arc back.
        d = f"M{xy(outer, a0)} A{num(outer)},{num(outer)} 0 0 1 {xy(outer, a1)} "
        if inner > 0:
            d += f"L{xy(inner, a1)} A{num(inner)},{num(inner)} 0 0 0 {xy(inner, a0)} Z"
        else:
            d += f"L{num(cx)},{num(cy)} Z"
        wedge = drawing.add(
            "subject", "path", {"id": f"party-{key}", "class": f"party-{key} edged", "d": d}
        )
        drawing.add(wedge, "title", text=f"{label_of(label)}: {count}")
        done += count

    # Dimension: the majority, where the seat that completes it ends.
    if show_majority:
        m = majority_of(total)
        angle = math.pi * (1 - m / total)
        x1, y1 = point(inner, angle)
        x2, y2 = point(outer + 4, angle)
        drawing.line("dimension", x1, y1, x2, y2)
        drawing.label(x2, y2 - 4, f"majority {m}", ink="faint")

    # Labels: the total in the hole.
    if inner > 0:
        drawing.label(cx, cy - 4 - FONT_SIZE_PX, str(total), ink="strong", is_name=True)
        drawing.label(cx, cy - 2, "seats", ink="faint")
    return drawing


def half_pie_svg(
    groups: Sequence[Group],
    *,
    colors: Mapping[str, str | Tone] | None = None,
    width: int = 240,
    hole: float = 0.4,
    majority: bool = False,
) -> Svg:
    """An inline SVG half pie of ``groups``, ``width`` pixels wide.

    Hovering a wedge shows its group and seat count. ``Svg.save(dir, name)`` writes it
    for print. See :func:`half_pie_drawing`.
    """
    return half_pie_drawing(groups, colors=colors, width=width, hole=hole, majority=majority).svg()
