"""A chamber as a hemicycle of seats.

Seats sit on concentric half-rings. Each ring holds seats in proportion to its length,
and all seats are then ordered left to right by angle, so consecutive groups fill
wedges, as in the usual parliament diagram. Geometry is in unit coordinates: the centre
of the hemicycle is ``(0, 0)``, the outer ring has radius ``1``, ``y`` points up.

Drawn as a technical drawing (:mod:`wahlwerk_ui.style`): the rings as dashed
construction guides under the seats, a dashed half axis, a floor line, the seats as the
one saturated thing, and, if asked for, the majority as a reference mark.

Groups are ``(label, seats)`` pairs; see :mod:`wahlwerk_ui.plot.chamber.common`.
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
from wahlwerk_ui.style import EDGE_MIN_DIAMETER_PX, FONT_SIZE_PX, Tone
from wahlwerk_ui.svg import Drawing, Svg, num, scope_id

__all__ = ["hemicycle_drawing", "hemicycle_svg", "seat_layout"]

_INNER = 0.4
"""Radius of the innermost ring, as a fraction of the outer one."""

_SEAT = 0.8
"""Seat diameter as a fraction of the distance between rings."""

_PAD = 2.0
"""Margin around the drawing, px."""


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


def _rings_for(seats: int) -> int:
    rings = 1
    while sum(_ring_capacities(rings)) < seats:
        rings += 1
    return rings


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
    rings = _rings_for(seats)
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
# Drawing
# ===========================================================
def hemicycle_drawing(
    groups: Sequence[Group],
    *,
    colors: Mapping[str, str | Tone] | None = None,
    width: int = 240,
    majority: bool = False,
    scope: str | None = None,
) -> Drawing:
    """The hemicycle of ``groups`` as a :class:`~wahlwerk_ui.svg.Drawing`.

    ``majority`` adds a reference mark after the seat that completes an absolute
    majority (more than half the seats), labelled with its count. Off by default: which
    majority matters is a question of the law, not of the drawing.
    """
    check_groups(groups)
    total = sum(count for _, count in groups)
    centres, seat_r = seat_layout(total)
    show_majority = majority and total >= 3
    top = _PAD + (FONT_SIZE_PX + 6 if show_majority else 0)
    scale = (width / 2 - _PAD) / (1 + seat_r)
    cx, cy = width / 2, top + (1 + seat_r) * scale
    floor = cy + seat_r * scale + 2

    def at(radius: float, angle: float) -> tuple[float, float]:
        return cx + radius * scale * math.cos(angle), cy - radius * scale * math.sin(angle)

    drawing = Drawing(
        width,
        math.ceil(floor + _PAD),
        scope=scope or scope_id("hemicycle", tuple(groups), colors, width, majority),
        label=f"{total} seats",
    )

    # Construction: one dashed guide per ring, and the half axis above the label.
    radii = sorted({round(math.hypot(x, y), 9) for x, y in centres})
    for radius in radii:
        r = radius * scale
        drawing.add(
            "construction",
            "path",
            {
                "class": "construction",
                "d": f"M{num(cx - r)},{num(cy)} A{num(r)},{num(r)} 0 0 1 {num(cx + r)},{num(cy)}",
            },
        )
    inner = (radii[0] - 2 * seat_r) if radii else 0.0
    if total:
        drawing.line("construction", cx, cy - inner * scale, cx, cy - (1 + seat_r) * scale - 2)

    # Structure: the floor the hemicycle stands on.
    drawing.line("structure", _PAD, floor, width - _PAD, floor)

    # Subject: the seats, one group per party.
    edged = 2 * seat_r * scale >= EDGE_MIN_DIAMETER_PX
    seat = 0
    for (label, count), (key, color) in zip(groups, party_tones(groups, colors)):
        if count == 0:
            continue
        drawing.parties.setdefault(key, color)
        group = drawing.add("subject", "g", {"id": f"party-{key}", "class": f"party-{key}"})
        drawing.add(group, "title", text=f"{label_of(label)}: {count}")
        for n, (x, y) in enumerate(centres[seat : seat + count], start=1):
            attrs = {
                "id": f"seat-{key}-{n:03d}",
                "cx": num(cx + x * scale),
                "cy": num(cy - y * scale),
                "r": num(seat_r * scale),
            }
            if edged:
                attrs["class"] = "edged"
            drawing.add(group, "circle", attrs)
        seat += count

    # Dimension: the majority, between the seat that completes it and the next.
    if show_majority:
        m = majority_of(total)
        angles = [math.atan2(y, x) for x, y in centres]
        boundary = (angles[m - 1] + angles[m]) / 2
        x1, y1 = at(inner, boundary)
        x2, y2 = at(1 + seat_r + 2 / scale, boundary)
        drawing.line("dimension", x1, y1, x2, y2)
        drawing.label(x2, y2 - 4, f"majority {m}", ink="faint")

    # Labels: the total, and what it counts.
    drawing.label(cx, cy - 4 - FONT_SIZE_PX, str(total), ink="strong", is_name=True)
    drawing.label(cx, cy - 2, "seats", ink="faint")
    return drawing


def hemicycle_svg(
    groups: Sequence[Group],
    *,
    colors: Mapping[str, str | Tone] | None = None,
    width: int = 240,
    majority: bool = False,
) -> Svg:
    """An inline SVG hemicycle of ``groups``, ``width`` pixels wide.

    Hovering a seat shows its group and seat count. The total sits in the centre.
    ``Svg.save(dir, name)`` writes it for print. See :func:`hemicycle_drawing`.
    """
    return hemicycle_drawing(groups, colors=colors, width=width, majority=majority).svg()
