"""Drawings written as structured SVG.

A drawing is meant to be read, reused and regenerated, by a person and by an AI, so the
file is kept readable: every layer is a named group with Inkscape layer attributes, at
a fixed z-order (:data:`LAYERS`) whatever order it was drawn in; every party is a named
group (``party-spd``) and every seat has an id (``seat-spd-001``); all colours sit in one
style block at the top, generated from :mod:`wahlwerk_ui.style`.

User units are pixels at final size. Pure standard library.

**A generated SVG is regenerated, never edited and saved back.** Illustrator rewrites
SVG on save and drops the group structure. Place the file in a document of your own and
put hand additions on a layer there.
"""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from pathlib import Path

from wahlwerk_ui.style import Tone, css

__all__ = ["LAYERS", "Drawing", "Svg", "scope_id"]

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)

LAYERS: tuple[str, ...] = ("construction", "structure", "subject", "dimension", "labels")
"""The layers of every drawing, bottom to top: the rungs of the ink ladder."""


def _tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def num(value: float) -> str:
    """A coordinate with two decimals and no trailing zeros."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def scope_id(*parts: object) -> str:
    """A deterministic id for a drawing, from what it shows.

    The style block is scoped under it, so two drawings in one notebook never restyle
    each other, and the same input always gives the same file.
    """
    digest = hashlib.sha1(repr(parts).encode("utf-8")).hexdigest()[:8]
    return f"ww-{digest}"


class Svg(str):
    """A ``str`` of SVG that Jupyter displays rendered, and that can be saved.

    The string follows the reader's theme. :meth:`save` writes :attr:`printable`, the
    same drawing with the light colours written in place.
    """

    printable: str = ""

    @classmethod
    def with_printable(cls, text: str, printable: str) -> Svg:
        """The SVG ``text``, carrying ``printable`` for :meth:`save`."""
        svg = cls(text)
        svg.printable = printable
        return svg

    def _repr_svg_(self) -> str:
        return str(self)

    def save(self, directory: str | Path, name: str) -> Path:
        """Write ``<directory>/<name>.svg`` (the printable variant); return its path."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{name}.svg"
        text = self.printable or str(self)
        path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + text, "utf-8")
        return path


class Drawing:
    """An SVG drawing with the layers of :data:`LAYERS`, built in code."""

    def __init__(self, width: float, height: float, *, scope: str, label: str) -> None:
        self.scope = scope
        self.width = width
        self.height = height
        self.parties: dict[str, Tone] = {}
        self.root = ET.Element(
            _tag("svg"),
            {
                "id": scope,
                "class": "ww",
                "width": num(width),
                "height": num(height),
                "viewBox": f"0 0 {num(width)} {num(height)}",
                "role": "img",
                "aria-label": label,
            },
        )
        self.layers = {
            name: ET.SubElement(
                self.root,
                _tag("g"),
                {
                    "id": f"layer-{name}",
                    f"{{{INKSCAPE_NS}}}groupmode": "layer",
                    f"{{{INKSCAPE_NS}}}label": name,
                },
            )
            for name in LAYERS
        }

    def add(
        self,
        parent: str | ET.Element,
        tag: str,
        attrs: Mapping[str, str] | None = None,
        text: str | None = None,
    ) -> ET.Element:
        """Append ``<tag>`` to a layer (by name) or to an element; return it."""
        if isinstance(parent, str):
            if parent not in self.layers:
                raise KeyError(f"no layer {parent!r}; layers are {', '.join(LAYERS)}")
            parent = self.layers[parent]
        element = ET.SubElement(parent, _tag(tag), dict(attrs or {}))
        if text is not None:
            element.text = text
        return element

    def line(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> ET.Element:
        """A straight line in a layer, styled by the layer's rung."""
        return self.add(
            layer,
            "line",
            {"class": layer, "x1": num(x1), "y1": num(y1), "x2": num(x2), "y2": num(y2)},
        )

    def label(
        self,
        x: float,
        y: float,
        text: str,
        *,
        ink: str = "plain",
        is_name: bool = False,
        anchor: str = "middle",
    ) -> ET.Element:
        """A label: one face, one size, ink ``faint``, ``plain`` or ``strong``; or
        ``selected``, a setting's value in a protocol drawing, the one thing a
        counterfactual changes."""
        if ink not in ("faint", "plain", "strong", "selected"):
            raise ValueError(f"ink must be 'faint', 'plain', 'strong' or 'selected', got {ink!r}")
        classes = f"label {ink}" + (" name" if is_name else "")
        return self.add(
            "labels",
            "text",
            {"class": classes, "x": num(x), "y": num(y), "text-anchor": anchor},
            text,
        )

    def markup(self, *, style: bool = True, adaptive: bool = True) -> str:
        """The SVG as a string; ``style=False`` leaves out the style block."""
        root = ET.fromstring(ET.tostring(self.root))  # a copy, so the drawing stays reusable
        for layer in list(root):
            if len(layer) == 0:
                root.remove(layer)
        if style:
            element = ET.Element(_tag("style"))
            element.text = css(self.scope, self.parties, adaptive=adaptive)
            root.insert(0, element)
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode")

    def svg(self) -> Svg:
        """The drawing for display, carrying its printable variant."""
        return Svg.with_printable(self.markup(), self.markup(adaptive=False))
