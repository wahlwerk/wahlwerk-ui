"""The style guide, drawn with the library it documents.

Every plate here is a :class:`~wahlwerk_ui.sketch.plate.Plate` built from
:mod:`~wahlwerk_ui.sketch.primitives`, so the guide cannot show a rule the code does
not follow. ``STYLE.md`` at the repository root walks through the plates step by step;
regenerate them after any change to :mod:`wahlwerk_ui.style`::

    uv run python -m wahlwerk_ui.sketch.guide docs/style
"""

from __future__ import annotations

import sys
from pathlib import Path

from wahlwerk_ui.sketch import primitives as sk
from wahlwerk_ui.sketch.plate import Plate
from wahlwerk_ui.style import (
    CONTENT,
    EDGE_MIN_DIAMETER_PX,
    FALLBACK_COLORS,
    FONT_SIZE_PX,
    PARTY_COLORS,
    STROKE_FRAME_PX,
    STROKE_HAIRLINE_PX,
    STROKE_SUBJECT_PX,
    SURFACE,
    UNRECORDED,
)
from wahlwerk_ui.svg import num

__all__ = [
    "anatomy",
    "circles",
    "furniture",
    "inks",
    "labels",
    "parties",
    "party_page",
    "plates",
    "strokes",
    "write",
]

W, H = 150, 100
"""Size of a guide panel's art."""


def anatomy() -> Plate:
    """Step 1: a plate is a row of panels; a panel is a title, its art and a caption."""
    plate = Plate("anatomy", "a plate")
    p = plate.panel(
        "panel",
        "title",
        width=220,
        height=120,
        caption=("name", "first line of note", "second line, no more"),
    )
    a = p.art
    sk.unit(a, 1, 1, 218, 118, "art")
    sk.dimension(a, 1, 104, 219, 104, "width")
    sk.dimension(a, 150, 6, 150, 96, "height")
    sk.dot(a, 80, 56, 26, cls="subject")
    sk.text(a, 80, 60, "subject", ink="strong", is_name=True)
    return plate


def inks() -> Plate:
    """Step 2: the ink ladder, one rung per panel, faintest first."""
    plate = Plate("inks", "the ink ladder")
    cx, cy = W / 2, H / 2

    p = plate.panel(
        "construction",
        "construction",
        width=W,
        height=H,
        caption=("construction", "dashed, almost invisible", "guides, units, axes"),
    )
    sk.guide_circle(p.art, cx, cy, 30)
    sk.axis(p.art, cx - 45, cy, cx + 45, cy)

    p = plate.panel(
        "dimension",
        "dimension",
        width=W,
        height=H,
        caption=("dimension", "a mark read against", "the drawing: a width, a majority"),
    )
    sk.dimension(p.art, 25, cy + 10, W - 25, cy + 10, "100 px")

    p = plate.panel(
        "structure",
        "structure",
        width=W,
        height=H,
        caption=("structure", "the frame: a floor,", "paper, a table rule"),
    )
    sk.box(p.art, 30, 25, W - 60, 40)
    sk.rule(p.art, 20, W - 20, 80)

    p = plate.panel(
        "content",
        "content",
        width=W,
        height=H,
        caption=("content", "edges and arrows", "of the drawn things"),
    )
    sk.arrow(p.art, 25, cy, W - 50, cy)
    sk.dot(p.art, W - 35, cy, 9, cls="hollow")

    p = plate.panel(
        "subject",
        "subject",
        width=W,
        height=H,
        caption=("subject", "what the panel is about:", "the only saturated ink"),
    )
    sk.dot(p.art, cx - 22, cy, 14, cls="subject")
    sk.cross(p.art, cx + 22, cy, 14)
    return plate


def strokes() -> Plate:
    """Step 3: every stroke in one band; a lighter ink before a thinner line."""
    plate = Plate("strokes", "strokes")
    p = plate.panel(
        "band",
        "one band",
        width=300,
        height=110,
        caption=("0.6 to 2 px", "rank by ink, then by weight", "never a thicker line"),
    )
    rows = (
        (STROKE_HAIRLINE_PX, "rule", "hairline: edges, rules"),
        (STROKE_FRAME_PX, "structure", "frame: guides, marks, floor"),
        (STROKE_SUBJECT_PX, "subject-line", "subject: a cross, an edge"),
    )
    for i, (width, cls, note) in enumerate(rows):
        y = 22 + i * 30
        p.art.add(
            "structure" if cls != "subject-line" else "subject",
            "line",
            {"class": cls, "x1": "10", "y1": num(y), "x2": "90", "y2": num(y)},
        )
        sk.text(p.art, 100, y + 4, f"{width:g} px", ink="strong", anchor="start")
        sk.text(p.art, 100, y + 4 + FONT_SIZE_PX + 2, note, ink="faint", anchor="start")
    return plate


def circles() -> Plate:
    """Step 4: how a circle is drawn, from construction to a choice."""
    plate = Plate("circles", "circles")
    cx, cy = W / 2, H / 2 - 4

    p = plate.panel(
        "construct",
        "construct",
        width=W,
        height=H,
        caption=("centre and radius", "dashed circle, dot,", "radius as a dimension"),
    )
    sk.guide_circle(p.art, cx, cy, 28)
    sk.dot(p.art, cx, cy, 1.6, cls="arrowhead")
    sk.dimension(p.art, cx, cy, cx + 28, cy, "r")

    p = plate.panel(
        "small",
        "small",
        width=W,
        height=H,
        caption=(
            "fill only",
            f"below {EDGE_MIN_DIAMETER_PX:g} px across",
            "an edge would be half the ink",
        ),
    )
    for i in range(7):
        sk.dot(p.art, cx - 30 + i * 10, cy, 2.4)

    p = plate.panel(
        "edged",
        "edged",
        width=W,
        height=H,
        caption=(
            "fill and edge",
            f"from {EDGE_MIN_DIAMETER_PX:g} px across",
            f"edge {STROKE_HAIRLINE_PX:g} px, content ink",
        ),
    )
    p.art.parties["spd"] = PARTY_COLORS["spd"]
    for i, x in enumerate((cx - 28, cx, cx + 28)):
        p.art.add(
            "subject",
            "circle",
            {"class": "party-spd edged", "cx": num(x), "cy": num(cy), "r": num(6 + 2 * i)},
        )

    p = plate.panel(
        "subject",
        "subject",
        width=W,
        height=H,
        caption=("a sketch's subject", "light fill, line edge", "one voter, one vote"),
    )
    sk.dot(p.art, cx, cy, 22, cls="subject")
    sk.dot(p.art, cx, cy, 3)

    p = plate.panel(
        "choices",
        "choices",
        width=230,
        height=H,
        caption=("a mandate's choice", "yes filled, no hollow,", "abstain grey, absent dashed"),
    )
    for i, choice in enumerate(sk.CHOICES):
        x = 30 + i * 56
        sk.dot(p.art, x, cy, 9, cls=sk.CHOICES[choice])
        sk.text(p.art, x, cy + 26, choice, ink="faint")
    return plate


def labels() -> Plate:
    """Step 5: one face, one size, four inks."""
    plate = Plate("labels", "labels")
    p = plate.panel(
        "inks",
        "four inks",
        width=240,
        height=110,
        caption=("one face, one size", "a bigger label means", "fewer labels"),
    )
    for i, (ink, is_name, word, note) in enumerate(
        (
            ("faint", False, "faint", "a construction note"),
            ("plain", False, "plain", "the usual annotation"),
            ("strong", False, "strong", "a value read off: 433"),
            ("strong", True, "name", "names the subject"),
        )
    ):
        y = 20 + i * 24
        sk.text(p.art, 10, y, word, ink=ink, is_name=is_name, anchor="start")
        sk.text(p.art, 70, y, note, ink=ink, is_name=is_name, anchor="start")
    return plate


def furniture() -> Plate:
    """Step 6: the furniture every sketch shares."""
    plate = Plate("furniture", "furniture")
    cx, cy = W / 2, H / 2

    p = plate.panel(
        "unit",
        "unit",
        width=W,
        height=H,
        caption=("a unit", "dashed outline,", "its name faint inside"),
    )
    sk.unit(p.art, 20, 15, W - 40, H - 30, "wahlbezirk")
    sk.crowd(p.art, 30, 35, W - 60, H - 55, 18)

    p = plate.panel(
        "arrow",
        "arrow",
        width=W,
        height=H,
        caption=("an arrow", "a step of a process,", "head filled, on the point"),
    )
    sk.arrow(p.art, 25, cy, W - 25, cy)

    p = plate.panel(
        "leader",
        "leader",
        width=W,
        height=H,
        caption=("a leader", "from a label", "to what it names"),
    )
    sk.dot(p.art, cx + 25, cy + 15, 10, cls="subject")
    sk.leader(p.art, 40, 30, cx + 18, cy + 9)
    sk.text(p.art, 38, 26, "this", anchor="end")

    p = plate.panel(
        "table",
        "table",
        width=W,
        height=H,
        caption=("a table", "faint header, hairline,", "numbers strong, right"),
    )
    sk.table(
        p.art,
        15,
        12,
        ("party", "count"),
        (("afd", "209"), ("cdu", "61"), ("spd", "37")),
        numeric=(False, True),
    )

    p = plate.panel(
        "tree",
        "tree",
        width=W,
        height=H,
        caption=("a tree", "parent above,", "edges down and across"),
    )
    sk.text(p.art, cx, 22, "land", ink="strong")
    for x in (cx - 40, cx + 40):
        sk.link(p.art, cx, 27, x, 52)
        sk.text(p.art, x, 64, "wahlkreis", ink="plain")
    return plate


def parties() -> Plate:
    """Party colours in both themes, drawn with their literal values."""
    plate = Plate("parties", "party colours")
    keys = [k for k in PARTY_COLORS if k not in ("cdu-csu", "pds")]
    step = 48
    width = 40 + step * (len(keys) + 1)
    p = plate.panel(
        "parties",
        "parties, light and dark",
        width=width,
        height=104,
        caption=(
            "party colours",
            "data, never chrome; dark slate,",
            "never black, for carbon-dark parties",
        ),
    )
    p.art.add(
        "structure",
        "rect",
        {"x": "0", "y": "52", "width": num(width), "height": "52", "style": f"fill:{SURFACE.dark}"},
    )
    for i, key in enumerate(keys):
        x = 28 + i * step
        tone = PARTY_COLORS[key]
        for y, value, edge in ((26, tone.light, CONTENT.light), (78, tone.dark, CONTENT.dark)):
            p.art.add(
                "subject",
                "circle",
                {
                    "cx": num(x),
                    "cy": num(y),
                    "r": "8",
                    "style": f"fill:{value};stroke:{edge};stroke-width:{STROKE_HAIRLINE_PX}",
                },
            )
        sk.text(p.art, x, 47, key, ink="faint")
    x = 28 + len(keys) * step
    for y, value in ((26, UNRECORDED.light), (78, UNRECORDED.dark)):
        p.art.add(
            "subject", "circle", {"cx": num(x), "cy": num(y), "r": "8", "style": f"fill:{value}"}
        )
    sk.text(p.art, x, 47, "unrec.", ink="faint")
    return plate


def plates() -> list[Plate]:
    """Every plate of the guide, in the order STYLE.md walks through them."""
    return [anatomy(), inks(), strokes(), circles(), labels(), furniture()]


def party_page() -> str:
    """``docs/party-colours.md``: every party colour, generated from :mod:`wahlwerk_ui.parties`."""
    lines = [
        "# Party colours",
        "",
        "Generated from [`src/wahlwerk_ui/parties.py`](../src/wahlwerk_ui/parties.py) by",
        "`uv run python -m wahlwerk_ui.sketch.guide docs/style`; edit the module, not this page.",
        "The rules are in the module's docstring and in [STYLE.md](../STYLE.md#party-colours).",
        "",
        "![party colours](style/parties.svg)",
        "",
        "| id | party | light | dark |",
        "| --- | --- | --- | --- |",
    ]
    for key, tone in sorted(PARTY_COLORS.items()):
        lines.append(f"| `{key}` | {tone.usage} | `{tone.light}` | `{tone.dark}` |")
    lines += [
        "",
        f"Seats whose party is not on record: `{UNRECORDED.light}` / `{UNRECORDED.dark}`.",
        "A label without a colour here takes the next fallback, in order of appearance: "
        + ", ".join(f"`{t.light}`" for t in FALLBACK_COLORS)
        + ".",
        "",
    ]
    return "\n".join(lines)


def write(directory: str | Path) -> list[Path]:
    """Save every plate as ``<directory>/<n>-<name>.svg``, the party plate as
    ``<directory>/parties.svg`` and the party page beside the directory as
    ``party-colours.md``; return the paths."""
    directory = Path(directory)
    paths = [
        plate.save(directory, f"{i}-{plate.name}") for i, plate in enumerate(plates(), start=1)
    ]
    paths.append(parties().save(directory, "parties"))
    page = directory.parent / "party-colours.md"
    page.write_text(party_page(), encoding="utf-8")
    paths.append(page)
    return paths


if __name__ == "__main__":  # pragma: no cover
    for path in write(sys.argv[1] if len(sys.argv) > 1 else "docs/style"):
        print(path)
