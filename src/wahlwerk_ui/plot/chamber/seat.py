"""A chamber as a hemicycle of seats.

Seats sit on concentric half-rings. Each ring holds seats in proportion to its length,
and all seats are then ordered left to right by angle, so consecutive groups fill
wedges, as in the usual parliament diagram. Geometry is in unit coordinates: the centre
of the hemicycle is ``(0, 0)``, the outer ring has radius ``1``, ``y`` points up.

Groups are ``(label, seats)`` pairs; see :mod:`wahlwerk_ui.plot.chamber.common`.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from html import escape

from wahlwerk_ui.plot.chamber.common import Group, check_groups, colors_for, label_of

__all__ = ["hemicycle_svg", "seat_layout"]

_INNER = 0.4
"""Radius of the innermost ring, as a fraction of the outer one."""

_SEAT = 0.8
"""Seat diameter as a fraction of the distance between rings."""


# ===========================================================
# Layout
# ===========================================================
def _ring_spacing(rings: int) -> float:
    """Distance between neighbouring rings, and between neighbouring seats on a ring."""
    return (1 - _INNER) / rings


def _ring_radii(rings: int) -> list[float]:
    """Radii of the rings, innermost first; the outermost is always ``1``."""
    spacing = _ring_spacing(rings)
    return [1 - (rings - 1 - i) * spacing for i in range(rings)]


def _ring_capacities(rings: int) -> list[int]:
    """How many seats fit on each ring, innermost first, one spacing apart."""
    spacing = _ring_spacing(rings)
    return [int(math.pi * r / spacing) + 1 for r in _ring_radii(rings)]


def _fill(capacities: list[int], seats: int) -> list[int]:
    """Seats per ring, proportional to capacity, by largest remainder.

    Integer arithmetic throughout, so the layout is the same on every machine. Ties in
    the remainder go to the outer ring.
    """
    total = sum(capacities)
    counts = [c * seats // total for c in capacities]
    order = sorted(range(len(capacities)), key=lambda i: (-(capacities[i] * seats % total), -i))
    for i in order[: seats - sum(counts)]:
        counts[i] += 1
    return counts


def seat_layout(seats: int) -> tuple[list[tuple[float, float]], float]:
    """Centres of ``seats`` seats, left to right, and the seat radius.

    Uses the fewest rings that hold all seats. Coordinates are unit (see module).
    """
    if isinstance(seats, bool) or not isinstance(seats, int):
        raise TypeError(f"seats must be an int, got {seats!r}")
    if seats < 0:
        raise ValueError(f"seats is negative: {seats}")
    if seats == 0:
        return [], 0.0
    rings = 1
    while sum(_ring_capacities(rings)) < seats:
        rings += 1
    spacing = _ring_spacing(rings)
    placed: list[tuple[float, float]] = []  # (angle, radius)
    for radius, count in zip(_ring_radii(rings), _fill(_ring_capacities(rings), seats)):
        for j in range(count):
            angle = math.pi / 2 if count == 1 else math.pi * (1 - j / (count - 1))
            placed.append((angle, radius))
    placed.sort(key=lambda p: (-p[0], p[1]))
    centres = [(r * math.cos(a), r * math.sin(a)) for a, r in placed]
    seat_radius = min(_SEAT * spacing, 0.25) / 2
    return centres, seat_radius


# ===========================================================
# Rendering
# ===========================================================
def hemicycle_svg(
    groups: Sequence[Group],
    *,
    colors: Mapping[str, str] | None = None,
    width: int = 240,
) -> str:
    """An inline SVG hemicycle of ``groups``, ``width`` pixels wide.

    Hovering a seat shows its group and seat count. The total sits in the centre.
    """
    check_groups(groups)
    total = sum(count for _, count in groups)
    centres, seat_radius = seat_layout(total)
    pad = 2.0
    scale = (width / 2 - pad) / (1 + seat_radius)
    cx, cy = width / 2, pad + scale
    height = math.ceil(cy + seat_radius * scale + pad)

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{total} seats">'
        )
    ]
    seat = 0
    for (label, count), color in zip(groups, colors_for(groups, colors)):
        if count == 0:
            continue
        parts.append(
            f'<g fill="{color}" stroke="#00000040" stroke-width="0.5">'
            f"<title>{escape(label_of(label))}: {count}</title>"
        )
        for x, y in centres[seat : seat + count]:
            parts.append(
                f'<circle cx="{cx + x * scale:.2f}" cy="{cy - y * scale:.2f}" '
                f'r="{seat_radius * scale:.2f}"/>'
            )
        parts.append("</g>")
        seat += count
    parts.append(
        f'<text x="{cx:.2f}" y="{cy - 2:.2f}" text-anchor="middle" '
        f'font-family="sans-serif" font-size="{width / 11:.1f}" font-weight="bold" '
        f'fill="#333">{total}</text></svg>'
    )
    return "".join(parts)
