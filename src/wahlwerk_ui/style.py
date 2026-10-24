"""The drawing style of wahlwerk: a technical drawing, not an illustration.

The reference is an old architectural plate: thin clean lines, the construction geometry
left visible, every label in one small face, nothing shaded, and no line thick enough to
be the first thing seen. It is the style of the IR-bands Knowledge diagrams and of
phd_ui's sketches, carried over to chambers.

The ink ladder
--------------
**Hierarchy is carried by ink, and only secondarily by weight.** Every stroke lives in
one narrow band, :data:`STROKE_MIN_PX` to :data:`STROKE_MAX_PX`, so a plot reads as one
drawing; what separates a guide from a seat is how strongly it is inked, not how fat it
is. The rungs, faintest first:

==============  =========================================================
construction    ring guides, the half axis: dashed, almost invisible
dimension       reference marks read against the drawing (majority)
structure       the frame: the floor line
content         edges of the drawn things: seat and wedge outlines
subject         the parties, or a sketch's subject: the only saturated colour
==============  =========================================================

Two strokes on the same rung claim to be the same kind of thing, so before adding one,
decide which rung it is on. Reach for a lighter ink before a thinner line, and never for
a thicker one.

Labels: one face, one size, four inks
-------------------------------------
Every label is set in :data:`FONT_FAMILY` at :data:`FONT_SIZE_PX`. The four inks are
faint (a construction note), plain (the usual annotation), strong (a value being read
off) and strong at :data:`LABEL_WEIGHT` (the name of the subject). A plot that needs a
bigger label needs fewer labels.

Both themes
-----------
Every colour is a :class:`Tone` with a light and a dark value. A drawing shown in a
notebook or a page carries both and follows the theme (``prefers-color-scheme`` and
JupyterLab's ``data-jp-theme-light``); a drawing saved for print carries the light
values resolved, since Illustrator and Inkscape read no CSS variables.

This module is the one source of these values. Party colours are in
:mod:`wahlwerk_ui.parties` and re-exported here; wahlwerk-site's ``lib/tokens.ts`` copies
them. Change them there first.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

__all__ = [
    "CHAR_WIDTH_PX",
    "CONSTRUCTION",
    "CONTENT",
    "DASH",
    "DIMENSION",
    "EDGE_MIN_DIAMETER_PX",
    "FALLBACK_COLORS",
    "FONT_FAMILY",
    "FONT_SIZE_PX",
    "INKS",
    "LABEL_FAINT",
    "LABEL_PLAIN",
    "LABEL_STRONG",
    "LABEL_WEIGHT",
    "LINE",
    "PARTY_COLORS",
    "STEP_FILL",
    "STEP_LINE",
    "STROKE_FRAME_PX",
    "STROKE_HAIRLINE_PX",
    "STROKE_MAX_PX",
    "STROKE_MIN_PX",
    "STROKE_SUBJECT_PX",
    "STRUCTURE",
    "SUBJECT_FILL",
    "SUBJECT_LINE",
    "SURFACE",
    "UNRECORDED",
    "Tone",
    "css",
    "slug",
    "tone",
]


@dataclass(frozen=True)
class Tone:
    """One colour in both themes, with a note on what it is for."""

    light: str
    dark: str
    usage: str = ""


# ===========================================================
# The ink ladder
# ===========================================================
CONSTRUCTION = Tone("#cdcac1", "#45474e", "Construction geometry: ring guides, the half axis")
DIMENSION = Tone("#a7a49b", "#6c6e76", "Reference marks read against the drawing: majority")
STRUCTURE = Tone("#8a8d96", "#7e818a", "The frame: the floor line under a chamber")
CONTENT = Tone("#5d606a", "#a3a5ad", "Edges of the drawn things: seat and wedge outlines")

LABEL_FAINT = Tone("#a7a49b", "#6c6e76", "A construction note: 'seats', 'majority 315'")
LABEL_PLAIN = Tone("#5d606a", "#a3a5ad", "The usual annotation: legend labels")
LABEL_STRONG = Tone("#1d1f24", "#e9e7e1", "A value read off; with LABEL_WEIGHT, the subject")

SUBJECT_FILL = Tone("#cfe2f2", "#1f3447", "The subject of a sketch as an area: a mark, a vote")
SUBJECT_LINE = Tone("#1d6fa8", "#72b2e2", "Its edge, and the subject drawn as a line or a cross")

STEP_FILL = Tone("#f6efdc", "#3a3222", "A rule of a law as an area: a step box in a protocol drawing")
STEP_LINE = Tone("#b8860b", "#e0b54a", "Its edge, and the dashed frame of a sequence or loop of steps")

SURFACE = Tone("#ffffff", "#1d1f24", "Card background, paper, a no in a chamber vote")
LINE = Tone("#dcd9d0", "#34363d", "Card border")

INKS: Mapping[str, Tone] = {
    "construction": CONSTRUCTION,
    "dimension": DIMENSION,
    "structure": STRUCTURE,
    "content": CONTENT,
    "faint": LABEL_FAINT,
    "plain": LABEL_PLAIN,
    "strong": LABEL_STRONG,
    "subject-fill": SUBJECT_FILL,
    "subject-line": SUBJECT_LINE,
    "step-fill": STEP_FILL,
    "step-line": STEP_LINE,
    "surface": SURFACE,
    "line": LINE,
}
"""Every non-party colour by its CSS name (``--ww-<name>``)."""

# ===========================================================
# Strokes and type
# ===========================================================
STROKE_MIN_PX = 0.6
"""The thinnest stroke on any plate."""

STROKE_MAX_PX = 2.0
"""The thickest stroke on any plate."""

STROKE_HAIRLINE_PX = 0.6
"""Edges of seats and wedges (content)."""

STROKE_FRAME_PX = 1.0
"""Guides, marks and the floor line (construction, dimension, structure)."""

STROKE_SUBJECT_PX = 1.4
"""The subject drawn as a line: its edge, a cross on a ballot paper. The heaviest ink."""

DASH = "2 2"
"""Dash pattern of construction geometry."""

EDGE_MIN_DIAMETER_PX = 6.0
"""Seats smaller than this get no edge: on a 2 px seat a 0.6 px edge is half the ink."""

FONT_FAMILY = '"IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace'
"""The one face of every label: the code face, as on wahlwerk-site."""

FONT_SIZE_PX = 11
"""The one size of every label, and the smallest text allowed anywhere."""

LABEL_WEIGHT = 600
"""Weight of a label that names the subject."""

CHAR_WIDTH_PX = 0.6 * FONT_SIZE_PX
"""Advance of one character of the code face, for placing text without measuring it."""


def tone(color: str | Tone) -> Tone:
    """A ``Tone`` as given, or a plain colour used in both themes."""
    return color if isinstance(color, Tone) else Tone(color, color)


def slug(label: str | None) -> str:
    """The CSS class suffix and id part of a group label (``None`` is ``unrecorded``)."""
    if label is None:
        return "unrecorded"
    text = re.sub(r"[^a-z0-9_-]+", "-", label.lower()).strip("-")
    return text or "x"


# ===========================================================
# The style block
# ===========================================================
_LABEL = f"font-family:{FONT_FAMILY};font-size:{FONT_SIZE_PX}px"

_RULES: tuple[tuple[str, str], ...] = (
    (
        ".construction",
        (
            f"fill:none;stroke:{{construction}};stroke-width:{STROKE_FRAME_PX};"
            f"stroke-dasharray:{DASH}"
        ),
    ),
    (".dimension", f"fill:none;stroke:{{dimension}};stroke-width:{STROKE_FRAME_PX}"),
    (".structure", f"fill:none;stroke:{{structure}};stroke-width:{STROKE_FRAME_PX}"),
    (".edged", f"stroke:{{content}};stroke-width:{STROKE_HAIRLINE_PX}"),
    (".subject", f"fill:{{subject-fill}};stroke:{{subject-line}};stroke-width:{STROKE_FRAME_PX}"),
    (".subject-line", f"fill:none;stroke:{{subject-line}};stroke-width:{STROKE_SUBJECT_PX}"),
    (".subject-dot", "fill:{subject-line}"),
    (".paper", f"fill:{{surface}};stroke:{{structure}};stroke-width:{STROKE_FRAME_PX}"),
    (".step", f"fill:{{step-fill}};stroke:{{step-line}};stroke-width:{STROKE_FRAME_PX}"),
    (
        ".step-frame",
        f"fill:none;stroke:{{step-line}};stroke-width:{STROKE_FRAME_PX};stroke-dasharray:{DASH}",
    ),
    (".arrow", f"fill:none;stroke:{{content}};stroke-width:{STROKE_FRAME_PX}"),
    (".arrowhead", "fill:{content}"),
    (".rule", f"fill:none;stroke:{{structure}};stroke-width:{STROKE_HAIRLINE_PX}"),
    (".hollow", f"fill:{{surface}};stroke:{{content}};stroke-width:{STROKE_HAIRLINE_PX}"),
    (".neutral", f"fill:{{faint}};stroke:{{content}};stroke-width:{STROKE_HAIRLINE_PX}"),
    (".label", _LABEL),
    (".faint", "fill:{faint};color:{faint}"),
    (".plain", "fill:{plain};color:{plain}"),
    (".strong", "fill:{strong};color:{strong}"),
    (".name", f"font-weight:{LABEL_WEIGHT}"),
    (
        "&.card",
        (
            f"display:inline-block;{_LABEL};color:{{plain}};background:{{surface}};"
            "border:1px solid {line};border-radius:6px;padding:8px 12px;line-height:1.35"
        ),
    ),
    (".card-title", "margin-bottom:6px"),
    (".card-body", "display:flex;align-items:flex-end;gap:14px"),
    (".legend", "border-collapse:collapse;font:inherit;color:inherit"),
    (".legend td", "padding:1px 8px 1px 0;vertical-align:middle"),
    (".legend td.num", "padding-right:0;text-align:right"),
    (
        ".swatch",
        (
            "display:inline-block;width:8px;height:8px;border-radius:50%;"
            f"box-sizing:border-box;border:{STROKE_HAIRLINE_PX}px solid {{content}}"
        ),
    ),
)


def _block(scope: str, values: Mapping[str, str]) -> str:
    return f"{scope}{{" + "".join(f"--ww-{k}:{v};" for k, v in values.items()) + "}"


def css(scope: str, parties: Mapping[str, Tone], *, adaptive: bool = True) -> str:
    """The one style block of a drawing or card, every selector under ``#scope``.

    A selector starting with ``&`` applies to the scope element itself (``&.card``).

    ``parties`` maps a party class suffix (:func:`slug`) to its colour. ``adaptive``
    writes CSS variables with a dark block for the theme; otherwise the light values
    are written in place, for print and for Illustrator.
    """
    root = f"#{scope}"
    tokens = {**INKS, **{f"party-{k}": v for k, v in parties.items()}}
    if adaptive:
        refs = {name: f"var(--ww-{name})" for name in tokens}
    else:
        refs = {name: t.light for name, t in tokens.items()}
    rules = [
        f"{root}{sel[1:] if sel.startswith('&') else ' ' + sel}{{{body.format(**refs)}}}"
        for sel, body in _RULES
    ]
    rules += [
        f"{root} .party-{k}{{fill:{refs[f'party-{k}']};background:{refs[f'party-{k}']}}}"
        for k in parties
    ]
    if not adaptive:
        return "".join(rules)
    light = {k: t.light for k, t in tokens.items()}
    dark = {k: t.dark for k, t in tokens.items()}
    return (
        _block(root, light)
        + "@media (prefers-color-scheme: dark){"
        + _block(f':root:not([data-theme="light"]) {root}', dark)
        + "}"
        + _block(f'[data-jp-theme-light="false"] {root}', dark)
        + _block(f'[data-theme="dark"] {root}', dark)
        + "".join(rules)
    )


# Party colours live in their own module, since that list grows with every election;
# they are re-exported here so ``style`` stays the one place to import a colour from.
from wahlwerk_ui.parties import FALLBACK_COLORS, PARTY_COLORS, UNRECORDED
