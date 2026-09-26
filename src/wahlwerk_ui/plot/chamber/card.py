"""A small card for notebooks: a title, a chamber plot and a legend."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from typing import Literal

from wahlwerk_ui.html import Html
from wahlwerk_ui.plot.chamber.common import Group, colors_for, label_of
from wahlwerk_ui.plot.chamber.pie import half_pie_svg
from wahlwerk_ui.plot.chamber.seat import hemicycle_svg

__all__ = ["chamber_html"]


def chamber_html(
    groups: Sequence[Group],
    *,
    kind: Literal["seats", "pie"] = "seats",
    title: str = "",
    colors: Mapping[str, str] | None = None,
    width: int = 240,
) -> Html:
    """A card with ``title``, the plot and a legend of seats per group.

    ``kind`` picks the plot: ``"seats"`` draws every seat in a hemicycle, ``"pie"`` a
    half pie with one wedge per group. Returns :class:`~wahlwerk_ui.html.Html`, which
    Jupyter renders as the card.
    """
    if kind == "seats":
        svg = hemicycle_svg(groups, colors=colors, width=width)
    elif kind == "pie":
        svg = half_pie_svg(groups, colors=colors, width=width)
    else:
        raise ValueError(f"kind must be 'seats' or 'pie', got {kind!r}")
    rows = []
    for (label, count), color in zip(groups, colors_for(groups, colors)):
        rows.append(
            "<tr>"
            f'<td style="padding:1px 6px 1px 0"><span style="display:inline-block;'
            f'width:10px;height:10px;border-radius:50%;background:{color}"></span></td>'
            f'<td style="padding:1px 10px 1px 0">{escape(label_of(label))}</td>'
            f'<td style="padding:1px 0;text-align:right">{count}</td>'
            "</tr>"
        )
    header = ""
    if title:
        header = (
            f'<div style="margin-bottom:4px;font-weight:bold;color:#222">{escape(title)}</div>'
        )
    return Html(
        '<div style="display:inline-block;font-family:sans-serif;font-size:12px;'
        "color:#333;background:#fff;border:1px solid #ddd;border-radius:6px;"
        'padding:8px 12px">'
        f"{header}"
        '<div style="display:flex;align-items:flex-end;gap:14px">'
        f"<div>{svg}</div>"
        f'<table style="border-collapse:collapse">{"".join(rows)}</table>'
        "</div></div>"
    )
