"""What every chamber plot shares: groups, their colours and their labels.

Groups are plain ``(label, seats)`` pairs in seating order, left to right. A label of
``None`` stands for seats whose party is not on record; they are drawn grey.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

__all__ = [
    "PARTY_COLORS",
    "UNRECORDED_COLOR",
    "Group",
    "check_groups",
    "colors_for",
    "label_of",
]

Group = tuple[str | None, int]
"""A label (a party id, or ``None`` if not on record) and its number of seats."""

PARTY_COLORS: Mapping[str, str] = {
    "afd": "#009ee0",
    "bsw": "#7d254f",
    "cdu": "#151518",
    "cdu-csu": "#151518",
    "csu": "#0080c8",
    "fdp": "#ffcc00",
    "fw": "#f39200",
    "gruene": "#1aa037",
    "linke": "#be3075",
    "pds": "#be3075",
    "spd": "#e3000f",
    "ssw": "#003c8f",
}
"""Conventional colours for party ids in the wahlwerk-data registry."""

UNRECORDED_COLOR = "#c8c8c8"
"""Seats whose party is not on record."""

_FALLBACK_COLORS = ("#8c6d31", "#6b6ecf", "#9c9ede", "#e7969c", "#7b4173", "#637939")
"""Cycled through for labels without a conventional colour."""


def check_groups(groups: Sequence[Group]) -> None:
    """Raise unless every seat count is a non-negative ``int``."""
    for label, count in groups:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError(f"seats for {label!r} must be an int, got {count!r}")
        if count < 0:
            raise ValueError(f"seats for {label!r} is negative: {count}")


def colors_for(groups: Sequence[Group], colors: Mapping[str, str] | None) -> list[str]:
    """One colour per group: given, then conventional, then from the fallback cycle."""
    given = {**PARTY_COLORS, **(colors or {})}
    result: list[str] = []
    fallback = 0
    for label, _ in groups:
        if label is None:
            result.append(UNRECORDED_COLOR)
        elif label in given:
            result.append(given[label])
        else:
            result.append(_FALLBACK_COLORS[fallback % len(_FALLBACK_COLORS)])
            fallback += 1
    return result


def label_of(label: str | None) -> str:
    """The display label of a group."""
    return "unrecorded" if label is None else label
