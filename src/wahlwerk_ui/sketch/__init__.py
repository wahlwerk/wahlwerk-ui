"""Sketches: schematic drawings built in code, as plates of numbered panels.

A sketch explains something that is not a result from data: what a vote is, how a
Stimmzettel is laid out, how a tally is shaped. It is drawn in the same style as the
plots (:mod:`wahlwerk_ui.style`) and with the same builder (:class:`~wahlwerk_ui.svg.Drawing`):
:mod:`.plate` lays panels out with a number, a title and a caption, :mod:`.primitives`
draws the pieces, :mod:`.guide` draws the style guide with them.

No drawing of a particular subject lives here: the vote sketches are drawn by
wahlwerk-site's ``sketches.py``, the way phd_ui keeps only the library.
"""

from __future__ import annotations

from wahlwerk_ui.sketch import plate, primitives

__all__ = ["plate", "primitives"]
