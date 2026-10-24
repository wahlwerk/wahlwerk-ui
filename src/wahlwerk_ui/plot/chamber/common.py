"""What every chamber plot shares: groups, their colours and their labels.

Groups are plain ``(label, seats)`` pairs in seating order, left to right. A label of
``None`` stands for seats whose party is not on record; they are drawn in
:data:`~wahlwerk_ui.style.UNRECORDED`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from wahlwerk_ui.style import (
    FALLBACK_COLORS,
    PARTY_COLORS,
    UNRECORDED,
    Tone,
    slug,
    tone,
)

__all__ = [
    "PARTY_COLORS",
    "Group",
    "check_groups",
    "label_of",
    "majority_of",
    "party_tones",
]

Group = tuple[str | None, int]
"""A label (a party id, or ``None`` if not on record) and its number of seats."""


def check_groups(groups: Sequence[Group]) -> None:
    """Raise unless every seat count is a non-negative ``int``."""
    for label, count in groups:
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError(f"seats for {label!r} must be an int, got {count!r}")
        if count < 0:
            raise ValueError(f"seats for {label!r} is negative: {count}")


def party_tones(
    groups: Sequence[Group], colors: Mapping[str, str | Tone] | None
) -> list[tuple[str, Tone]]:
    """One ``(class suffix, colour)`` per group: given, conventional, then fallback.

    A plain colour string is used in both themes. Fallback colours go to labels without
    one in order of appearance, the same label always getting the same one.
    """
    given = {**PARTY_COLORS, **{k: tone(v) for k, v in (colors or {}).items()}}
    assigned: dict[str, Tone] = {}
    result: list[tuple[str, Tone]] = []
    for label, _ in groups:
        key = slug(label)
        if key not in assigned:
            if label is None:
                assigned[key] = UNRECORDED
            elif label in given:
                assigned[key] = given[label]
            else:
                fallbacks = sum(1 for k in assigned if k not in given and k != "unrecorded")
                assigned[key] = FALLBACK_COLORS[fallbacks % len(FALLBACK_COLORS)]
        result.append((key, assigned[key]))
    return result


def majority_of(total: int) -> int:
    """More than half of ``total`` seats: the smallest absolute majority."""
    return total // 2 + 1


def label_of(label: str | None) -> str:
    """The display label of a group."""
    return "unrecorded" if label is None else label
