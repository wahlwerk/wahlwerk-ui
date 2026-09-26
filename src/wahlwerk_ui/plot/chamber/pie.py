"""A chamber as a half pie: one wedge per group, sized by seats.

Wedges run left to right in seating order over the upper half circle. With a ``hole``
it is a half ring, with the total in the centre, matching the seat hemicycle.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from html import escape

from wahlwerk_ui.plot.chamber.common import Group, check_groups, colors_for, label_of

__all__ = ["half_pie_svg"]


def half_pie_svg(
    groups: Sequence[Group],
    *,
    colors: Mapping[str, str] | None = None,
    width: int = 240,
    hole: float = 0.4,
) -> str:
    """An inline SVG half pie of ``groups``, ``width`` pixels wide.

    ``hole`` is the inner radius as a fraction of the outer one; ``0`` gives a solid
    pie (and no total in the centre). Hovering a wedge shows its group and seat count.
    """
    if not 0 <= hole < 1:
        raise ValueError(f"hole must be in [0, 1), got {hole}")
    check_groups(groups)
    total = sum(count for _, count in groups)
    pad = 2.0
    outer = width / 2 - pad
    inner = hole * outer
    cx, cy = width / 2, pad + outer
    height = math.ceil(cy + pad)

    def point(radius: float, angle: float) -> str:
        return f"{cx + radius * math.cos(angle):.2f},{cy - radius * math.sin(angle):.2f}"

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{total} seats">'
        )
    ]
    done = 0
    for (label, count), color in zip(groups, colors_for(groups, colors)):
        if count == 0:
            continue
        start = math.pi * (1 - done / total)
        end = math.pi * (1 - (done + count) / total)
        # Outer arc clockwise on screen (left to right), inner arc back.
        path = f"M{point(outer, start)} A{outer:.2f},{outer:.2f} 0 0 1 {point(outer, end)} "
        if inner > 0:
            path += f"L{point(inner, end)} A{inner:.2f},{inner:.2f} 0 0 0 {point(inner, start)} Z"
        else:
            path += f"L{cx:.2f},{cy:.2f} Z"
        parts.append(
            f'<path d="{path}" fill="{color}" stroke="#fff" stroke-width="1">'
            f"<title>{escape(label_of(label))}: {count}</title></path>"
        )
        done += count
    if inner > 0:
        parts.append(
            f'<text x="{cx:.2f}" y="{cy - 2:.2f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{width / 11:.1f}" font-weight="bold" '
            f'fill="#333">{total}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)
