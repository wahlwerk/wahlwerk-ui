"""Plates: a row of numbered panels, each with a title above and a caption below.

The layout of the PhD sketches (Kelvin geometry, capillarity): every panel is one idea,
drawn small; its title says what it shows, its caption names it in one line and adds at
most two lines of note under it. On a page the panels are separate SVGs that wrap at
phone width (:meth:`Plate.to_dict`); for print and documentation they are one file
(:meth:`Plate.svg`, :meth:`Plate.save`).
"""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from wahlwerk_ui.style import CHAR_WIDTH_PX, FONT_SIZE_PX, Tone
from wahlwerk_ui.svg import SVG_NS, Drawing, Svg, scope_id

__all__ = ["CAPTION_LINE_PX", "TITLE_BAND_PX", "Panel", "Plate"]

TITLE_BAND_PX = 2 * FONT_SIZE_PX
"""Height of the band above a panel's art that holds its number and title."""

CAPTION_LINE_PX = round(1.4 * FONT_SIZE_PX)
"""Line height of a caption."""

MAX_NOTE_LINES = 2
"""Lines of note a caption may have under its name; more means a second panel."""


class Panel:
    """One panel: its art (a :class:`Drawing`), a title and a caption.

    ``caption`` is the panel's name followed by at most :data:`MAX_NOTE_LINES` lines of
    note. Draw into :attr:`art` with :mod:`wahlwerk_ui.sketch.primitives`.
    """

    def __init__(
        self,
        name: str,
        title: str,
        *,
        width: float = 200,
        height: float = 140,
        caption: Sequence[str] = (),
    ) -> None:
        if len(caption) > 1 + MAX_NOTE_LINES:
            raise ValueError(
                f"panel {name!r}: a caption is a name and at most {MAX_NOTE_LINES} lines, "
                f"got {len(caption)}"
            )
        self.name = name
        self.title = title
        self.caption = tuple(caption)
        self.number = 0
        self.art = Drawing(width, height, scope=scope_id("panel", name, title), label=title)

    def svg(self) -> Svg:
        """The art alone, for a page that sets the title and caption as text."""
        return self.art.svg()

    @property
    def slot(self) -> float:
        """The width the panel takes on a plate: its art, or its widest line of text."""
        lines = [f"{self.number}  {self.title}", *self.caption]
        return max(self.art.width, *(len(line) * CHAR_WIDTH_PX + 8 for line in lines))


class Plate:
    """A row of :class:`Panel` s, numbered from 1."""

    def __init__(self, name: str, title: str = "", *, gap: float = 24) -> None:
        self.name = name
        self.title = title
        self.gap = gap
        self.panels: list[Panel] = []

    def panel(
        self,
        name: str,
        title: str,
        *,
        width: float = 200,
        height: float = 140,
        caption: Sequence[str] = (),
    ) -> Panel:
        """Add a panel and return it; it is numbered in order of adding."""
        if any(p.name == name for p in self.panels):
            raise ValueError(f"plate {self.name!r} already has a panel {name!r}")
        panel = Panel(name, title, width=width, height=height, caption=caption)
        panel.number = len(self.panels) + 1
        self.panels.append(panel)
        return panel

    def drawing(self) -> Drawing:
        """All panels side by side in one drawing, titles and captions set as text."""
        art_height = max((p.art.height for p in self.panels), default=0.0)
        lines = max((len(p.caption) for p in self.panels), default=0)
        width = sum(p.slot for p in self.panels) + self.gap * max(len(self.panels) - 1, 0)
        height = TITLE_BAND_PX + art_height + 8 + lines * CAPTION_LINE_PX
        drawing = Drawing(
            width, height, scope=scope_id("plate", self.name), label=self.title or self.name
        )
        x = 0.0
        for panel in self.panels:
            art_x = x + (panel.slot - panel.art.width) / 2
            group = ET.SubElement(
                drawing.root,
                f"{{{SVG_NS}}}g",
                {
                    "id": f"panel-{panel.name}",
                    "transform": f"translate({art_x:g} {TITLE_BAND_PX:g})",
                    "{http://www.inkscape.org/namespaces/inkscape}groupmode": "layer",
                    "{http://www.inkscape.org/namespaces/inkscape}label": panel.name,
                },
            )
            for layer in panel.art.root:
                if len(layer):
                    group.append(_prefixed(copy.deepcopy(layer), f"{panel.name}."))
            drawing.parties.update(panel.art.parties)
            middle = x + panel.slot / 2
            drawing.label(
                middle,
                FONT_SIZE_PX + 2,
                f"{panel.number}  {panel.title}",
                ink="strong",
                is_name=True,
            )
            y = TITLE_BAND_PX + art_height + 8 + FONT_SIZE_PX
            for i, line in enumerate(panel.caption):
                drawing.label(
                    middle, y + i * CAPTION_LINE_PX, line, ink="strong" if i == 0 else "faint"
                )
            x += panel.slot + self.gap
        # Titles and captions over the art, whatever order it was drawn in.
        labels = drawing.layers["labels"]
        drawing.root.remove(labels)
        drawing.root.append(labels)
        return drawing

    def svg(self) -> Svg:
        """The plate as one SVG, for documentation and print."""
        return self.drawing().svg()

    def save(self, directory: str | Path, name: str | None = None) -> Path:
        """Write the plate (printable variant) to ``<directory>/<name>.svg``."""
        return self.svg().save(directory, name or self.name)

    def parties(self) -> dict[str, Tone]:
        """Every party colour any panel uses."""
        merged: dict[str, Tone] = {}
        for panel in self.panels:
            merged.update(panel.art.parties)
        return merged

    def to_dict(self) -> dict[str, Any]:
        """The plate for a web page: one SVG per panel, titles and captions as text."""
        return {
            "name": self.name,
            "title": self.title,
            "panels": [
                {
                    "name": p.name,
                    "number": p.number,
                    "title": p.title,
                    "caption": list(p.caption),
                    "width": p.art.width,
                    "height": p.art.height,
                    "svg": str(p.svg()),
                }
                for p in self.panels
            ],
        }


def _prefixed(element: ET.Element, prefix: str) -> ET.Element:
    """Prefix every id under ``element``, so panels never share an id in one file."""
    for node in element.iter():
        if "id" in node.attrib:
            node.set("id", prefix + node.attrib["id"])
    return element
