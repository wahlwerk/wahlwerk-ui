"""The pieces sketches are drawn from, each on its rung of the ink ladder.

Every function draws into a :class:`~wahlwerk_ui.svg.Drawing` in pixels at final size,
``y`` down, and returns the element it made (or its group), so a caller can add a
``<title>`` or an id. The rung a piece sits on is part of what it is, not a parameter:

=============================  ===========================================
construction (dashed)          :func:`unit`, :func:`axis`, :func:`guide_circle`
dimension                      :func:`dimension`
structure                      :func:`box` (``paper``), :func:`rule`, :func:`link`
content                        :func:`arrow`, :func:`leader`, edges
subject                        :func:`dot`, :func:`crowd`, :func:`cross`, :func:`mark`
labels                         :func:`text`, :func:`table`
=============================  ===========================================

No piece knows anything about elections; :func:`ballot_paper` and :func:`chamber` are
compositions of the others, kept here because more than one sketch draws them.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from collections.abc import Sequence

from wahlwerk_ui.plot.chamber.seat import seat_layout
from wahlwerk_ui.style import CHAR_WIDTH_PX, FONT_SIZE_PX
from wahlwerk_ui.svg import Drawing, num

__all__ = [
    "CHOICES",
    "arrow",
    "axis",
    "ballot_paper",
    "box",
    "chamber",
    "cross",
    "crowd",
    "dimension",
    "dot",
    "guide_circle",
    "leader",
    "link",
    "mark",
    "rule",
    "table",
    "text",
    "text_width",
    "unit",
]

CHOICES: dict[str, str] = {
    "yes": "subject-dot",
    "no": "hollow",
    "abstain": "neutral",
    "absent": "construction",
}
"""How a mandate's choice is drawn: yes filled, no hollow, abstain grey, absent dashed."""


def text_width(text: str) -> float:
    """The width of ``text`` in the code face, without measuring."""
    return len(text) * CHAR_WIDTH_PX


def text(
    d: Drawing,
    x: float,
    y: float,
    content: str,
    *,
    ink: str = "plain",
    is_name: bool = False,
    anchor: str = "middle",
) -> ET.Element:
    """A label; one face, one size, ink ``faint``, ``plain`` or ``strong``."""
    return d.label(x, y, content, ink=ink, is_name=is_name, anchor=anchor)


# ===========================================================
# Construction
# ===========================================================
def unit(
    d: Drawing, x: float, y: float, w: float, h: float, label: str | None = None
) -> ET.Element:
    """A unit (a Wahlbezirk, a Wahlkreis) as a dashed outline, its name faint inside."""
    element = d.add(
        "construction",
        "rect",
        {"class": "construction", "x": num(x), "y": num(y), "width": num(w), "height": num(h)},
    )
    if label:
        text(d, x + 4, y + FONT_SIZE_PX + 1, label, ink="faint", anchor="start")
    return element


def axis(d: Drawing, x1: float, y1: float, x2: float, y2: float) -> ET.Element:
    """A dashed axis or symmetry line."""
    return d.line("construction", x1, y1, x2, y2)


def guide_circle(d: Drawing, cx: float, cy: float, r: float) -> ET.Element:
    """A dashed circle: where something would be, or the circle a seat is cut from."""
    return d.add(
        "construction",
        "circle",
        {"class": "construction", "cx": num(cx), "cy": num(cy), "r": num(r)},
    )


# ===========================================================
# Dimension
# ===========================================================
def dimension(
    d: Drawing,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    label: str = "",
    *,
    cap: float = 3,
) -> ET.Element:
    """A capped dimension line between two points, its label faint beside the middle."""
    group = d.add("dimension", "g", {"class": "dimension"})
    d.add(group, "line", {"x1": num(x1), "y1": num(y1), "x2": num(x2), "y2": num(y2)})
    angle = math.atan2(y2 - y1, x2 - x1)
    nx, ny = -math.sin(angle) * cap, math.cos(angle) * cap
    for x, y in ((x1, y1), (x2, y2)):
        d.add(
            group,
            "line",
            {"x1": num(x - nx), "y1": num(y - ny), "x2": num(x + nx), "y2": num(y + ny)},
        )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if abs(y2 - y1) < abs(x2 - x1):  # horizontal-ish: label above
            text(d, mx, my - cap - 3, label, ink="faint")
        else:  # vertical-ish: label to the right
            text(d, mx + cap + 3, my + FONT_SIZE_PX / 3, label, ink="faint", anchor="start")
    return group


# ===========================================================
# Structure
# ===========================================================
def box(
    d: Drawing, x: float, y: float, w: float, h: float, *, cls: str = "paper", rx: float = 2
) -> ET.Element:
    """A box: ``paper`` (a ballot paper, a record) or another class from the style block."""
    layer = "subject" if cls.startswith("subject") else "structure"
    return d.add(
        layer,
        "rect",
        {
            "class": cls,
            "x": num(x),
            "y": num(y),
            "width": num(w),
            "height": num(h),
            "rx": num(rx),
        },
    )


def rule(d: Drawing, x1: float, x2: float, y: float) -> ET.Element:
    """A hairline rule, under a table header or between sections."""
    return d.add(
        "structure",
        "line",
        {"class": "rule", "x1": num(x1), "y1": num(y), "x2": num(x2), "y2": num(y)},
    )


def link(d: Drawing, x1: float, y1: float, x2: float, y2: float) -> ET.Element:
    """A tree edge: down from the parent, across, down to the child."""
    mid = (y1 + y2) / 2
    return d.add(
        "structure",
        "path",
        {
            "class": "structure",
            "d": f"M{num(x1)},{num(y1)} V{num(mid)} H{num(x2)} V{num(y2)}",
        },
    )


# ===========================================================
# Content
# ===========================================================
def arrow(d: Drawing, x1: float, y1: float, x2: float, y2: float, *, head: float = 5) -> ET.Element:
    """An arrow from one point to another, the head filled and ending on the point."""
    angle = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(angle), y2 - head * math.sin(angle)
    group = d.add("structure", "g", {"class": "arrow-group"})
    d.add(
        group,
        "line",
        {"class": "arrow", "x1": num(x1), "y1": num(y1), "x2": num(bx), "y2": num(by)},
    )
    half = head * 0.45
    px, py = -math.sin(angle) * half, math.cos(angle) * half
    points = f"{num(x2)},{num(y2)} {num(bx + px)},{num(by + py)} {num(bx - px)},{num(by - py)}"
    d.add(group, "polygon", {"class": "arrowhead", "points": points})
    return group


def leader(d: Drawing, x1: float, y1: float, x2: float, y2: float) -> ET.Element:
    """A thin line from a label to what it names, with a dot on the thing."""
    group = d.add("structure", "g", {"class": "leader"})
    d.add(
        group,
        "line",
        {"class": "arrow", "x1": num(x1), "y1": num(y1), "x2": num(x2), "y2": num(y2)},
    )
    d.add(group, "circle", {"class": "arrowhead", "cx": num(x2), "cy": num(y2), "r": "1.4"})
    return group


# ===========================================================
# Subject
# ===========================================================
def dot(d: Drawing, x: float, y: float, r: float = 2.2, *, cls: str = "subject-dot") -> ET.Element:
    """One voter, one seat, one vote: a circle in the subject's ink (or ``cls``)."""
    layer = "construction" if cls == "construction" else "subject"
    return d.add(layer, "circle", {"class": cls, "cx": num(x), "cy": num(y), "r": num(r)})


def crowd(
    d: Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    n: int,
    *,
    r: float = 1.8,
    cls: str = "subject-dot",
) -> list[tuple[float, float]]:
    """``n`` anonymous voters scattered evenly in a box; returns their centres.

    Deterministic (a staggered grid nudged by the golden angle), so the same call draws
    the same crowd on every machine.
    """
    if n <= 0:
        return []
    cols = max(1, round(math.sqrt(n * w / h)))
    rows = math.ceil(n / cols)
    sx, sy = w / cols, h / rows
    golden = math.pi * (3 - math.sqrt(5))
    centres = []
    for i in range(n):
        row, col = divmod(i, cols)
        jx = math.cos(i * golden) * sx * 0.22
        jy = math.sin(i * golden) * sy * 0.22
        cx = x + (col + 0.5 + (0.25 if row % 2 else -0.25)) * sx + jx
        cy = y + (row + 0.5) * sy + jy
        cx = min(max(cx, x + r), x + w - r)
        cy = min(max(cy, y + r), y + h - r)
        centres.append((cx, cy))
        dot(d, cx, cy, r, cls=cls)
    return centres


def cross(d: Drawing, x: float, y: float, size: float = 6) -> ET.Element:
    """A cross as a voter makes it, in the subject's line."""
    s = size / 2
    return d.add(
        "subject",
        "path",
        {
            "class": "subject-line",
            "d": f"M{num(x - s)},{num(y - s)} L{num(x + s)},{num(y + s)} "
            f"M{num(x - s)},{num(y + s)} L{num(x + s)},{num(y - s)}",
        },
    )


def mark(d: Drawing, x: float, y: float, r: float = 4.5, *, is_marked: bool = False) -> ET.Element:
    """The circle a voter marks on a ballot paper, crossed when ``is_marked``."""
    element = d.add(
        "structure",
        "circle",
        {"class": "hollow", "cx": num(x), "cy": num(y), "r": num(r)},
    )
    if is_marked:
        cross(d, x, y, r * 1.5)
    return element


# ===========================================================
# Labels
# ===========================================================
def table(
    d: Drawing,
    x: float,
    y: float,
    header: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    numeric: Sequence[bool] | None = None,
    gap: float = 8,
    line: float | None = None,
) -> tuple[float, float]:
    """A small table: faint header, hairline rule, plain cells, numbers strong and right.

    A blank cell is drawn as a faint ``·`` so absent reads as absent, not as forgotten.
    Returns the width and height drawn.
    """
    line = line or round(1.35 * FONT_SIZE_PX)
    numeric = numeric or [False] * len(header)
    widths = [
        max(text_width(h), *(text_width(r[i]) for r in rows)) if rows else text_width(h)
        for i, h in enumerate(header)
    ]
    total = sum(widths) + gap * (len(widths) - 1)
    lefts = [x + sum(widths[:i]) + gap * i for i in range(len(widths))]
    for i, h in enumerate(header):
        hx, anchor = (lefts[i] + widths[i], "end") if numeric[i] else (lefts[i], "start")
        text(d, hx, y + FONT_SIZE_PX, h, ink="faint", anchor=anchor)
    rule(d, x, x + total, y + line - 2)
    for j, row in enumerate(rows):
        ry = y + line * (j + 1) + FONT_SIZE_PX + 2
        for i, cell in enumerate(row):
            if numeric[i]:
                text(d, lefts[i] + widths[i], ry, cell, ink="strong", anchor="end")
            elif cell:
                text(d, lefts[i], ry, cell, anchor="start")
            else:
                text(d, lefts[i], ry, "·", ink="faint", anchor="start")
    return total, line * (len(rows) + 1) + 4


# ===========================================================
# Compositions
# ===========================================================
def ballot_paper(
    d: Drawing,
    x: float,
    y: float,
    w: float,
    sections: Sequence[tuple[str, Sequence[str], int | None]],
    *,
    row: float = 15,
) -> float:
    """A ballot paper (a Stimmzettel, in the German example): one column per section, its options listed with a circle each.

    ``sections`` are ``(heading, options, marked)``; ``marked`` is the index of the
    option crossed, or ``None``. Returns the height drawn.
    """
    rows = max(len(options) for _, options, _ in sections)
    h = FONT_SIZE_PX + 10 + rows * row + 6
    box(d, x, y, w, h)
    cw = w / len(sections)
    for i, (heading, options, marked) in enumerate(sections):
        cx = x + i * cw
        if i:
            d.line("structure", cx, y + 3, cx, y + h - 3)
        text(d, cx + cw / 2, y + FONT_SIZE_PX + 3, heading, ink="faint")
        for j, option in enumerate(options):
            oy = y + FONT_SIZE_PX + 10 + j * row + row / 2
            mark(d, cx + 9, oy, is_marked=marked == j)
            text(d, cx + 18, oy + FONT_SIZE_PX / 3, option, anchor="start")
    return h


def chamber(
    d: Drawing,
    cx: float,
    cy: float,
    radius: float,
    choices: Sequence[str],
) -> list[tuple[float, float]]:
    """A chamber as a hemicycle of mandates, each drawn by its choice (:data:`CHOICES`).

    ``cy`` is the floor line; the seats are laid out as in the chamber plot. Returns the
    seat centres, left to right.
    """
    centres, seat_r = seat_layout(len(choices))
    scale = radius / (1 + seat_r)
    placed = []
    for (ux, uy), choice in zip(centres, choices):
        if choice not in CHOICES:
            raise ValueError(f"choice must be one of {', '.join(CHOICES)}, got {choice!r}")
        x, y = cx + ux * scale, cy - uy * scale
        dot(d, x, y, seat_r * scale * 0.92, cls=CHOICES[choice])
        placed.append((x, y))
    rule(d, cx - radius - 4, cx + radius + 4, cy + seat_r * scale + 2)
    return placed
