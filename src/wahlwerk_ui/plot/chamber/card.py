"""A small card for notebooks: a title, a chamber plot and a legend.

One style block serves the plot and the legend, so a legend swatch is the same colour
as its seats in both themes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from typing import Literal

from wahlwerk_ui.html import Html
from wahlwerk_ui.plot.chamber.common import Group, label_of, party_tones
from wahlwerk_ui.plot.chamber.pie import half_pie_drawing
from wahlwerk_ui.plot.chamber.seat import hemicycle_drawing
from wahlwerk_ui.style import Tone, css
from wahlwerk_ui.svg import scope_id

__all__ = ["chamber_html"]


def chamber_html(
    groups: Sequence[Group],
    *,
    kind: Literal["seats", "pie"] = "seats",
    title: str = "",
    colors: Mapping[str, str | Tone] | None = None,
    width: int = 240,
    majority: bool = False,
) -> Html:
    """A card with ``title``, the plot and a legend of seats per group.

    ``kind`` picks the plot: ``"seats"`` draws every seat in a hemicycle, ``"pie"`` a
    half pie with one wedge per group. ``majority`` marks an absolute majority on the
    plot (off by default). Returns :class:`~wahlwerk_ui.html.Html`, which Jupyter
    renders as the card.
    """
    scope = scope_id("card", tuple(groups), kind, title, colors, width, majority)
    if kind == "seats":
        drawing = hemicycle_drawing(
            groups, colors=colors, width=width, majority=majority, scope=f"{scope}-plot"
        )
    elif kind == "pie":
        drawing = half_pie_drawing(
            groups, colors=colors, width=width, majority=majority, scope=f"{scope}-plot"
        )
    else:
        raise ValueError(f"kind must be 'seats' or 'pie', got {kind!r}")
    tones = party_tones(groups, colors)
    parties = dict(tones)
    rows = [
        "<tr>"
        f'<td><span class="swatch party-{key}"></span></td>'
        f'<td class="plain">{escape(label_of(label))}</td>'
        f'<td class="num strong">{count}</td>'
        "</tr>"
        for (label, count), (key, _) in zip(groups, tones)
    ]
    header = f'<div class="card-title strong name">{escape(title)}</div>' if title else ""
    return Html(
        f'<div id="{scope}" class="ww card">'
        f"<style>{css(scope, parties)}</style>"
        f"{header}"
        '<div class="card-body">'
        f"<div>{drawing.markup(style=False)}</div>"
        f'<table class="legend">{"".join(rows)}</table>'
        "</div></div>"
    )
