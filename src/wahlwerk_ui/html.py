"""An HTML string that renders itself in Jupyter."""

from __future__ import annotations

__all__ = ["Html"]


class Html(str):
    """A ``str`` of HTML that Jupyter displays rendered rather than quoted.

    Needs no IPython: Jupyter looks for ``_repr_html_`` on any object, and everywhere
    else this is an ordinary string.
    """

    def _repr_html_(self) -> str:
        return str(self)
