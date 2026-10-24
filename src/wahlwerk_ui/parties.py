"""Party colours: the subject of every chamber plot.

Kept apart from :mod:`wahlwerk_ui.style` because this list grows with every election
the archive adds. Keys are the party ids of the wahlwerk-data registry; a party is
recorded under the name it stood under, so a renamed party is a new key. ``usage`` is
the party's name as shown in ``docs/party-colours.md``, which is generated from this
module (``python -m wahlwerk_ui.sketch.guide``).

Rules
-----
- **Data, never chrome.** A party colour encodes a party in a seat, a wedge or a
  swatch, and nothing else.
- **Both themes.** Every entry has a light and a dark value; the dark one is lighter.
- **Carbon-dark parties are a dark slate, never black**: black reads as ink.
- **The conventional colour** of the party, toned to sit beside the others; two parties
  that share a colour by convention (CDU and CDU/CSU, PDS and Die Linke) share it here.
- wahlwerk-site's ``lib/tokens.ts`` copies these values: change them here first.
"""

from __future__ import annotations

from collections.abc import Mapping

from wahlwerk_ui.style import Tone

__all__ = ["FALLBACK_COLORS", "PARTY_COLORS", "UNRECORDED"]

PARTY_COLORS: Mapping[str, Tone] = {
    "afd": Tone("#0a8fcf", "#3aa9e0", "AfD"),
    "bsw": Tone("#6d2a55", "#b0619a", "BSW"),
    "cdu": Tone("#2a2c31", "#c9c7c0", "CDU"),
    "cdu-csu": Tone("#2a2c31", "#c9c7c0", "CDU/CSU, the caucus"),
    "csu": Tone("#0080c8", "#3a9ee0", "CSU"),
    "fdp": Tone("#d9a800", "#f0c93a", "FDP"),
    "fw": Tone("#e58a00", "#f5ab40", "Freie Wähler"),
    "gruene": Tone("#3e8a25", "#62b046", "BÜNDNIS 90/DIE GRÜNEN"),
    "linke": Tone("#b3276d", "#dc5a98", "Die Linke"),
    "npd": Tone("#7a4a1f", "#b07a48", "NPD"),
    "pds": Tone("#b3276d", "#dc5a98", "PDS"),
    "spd": Tone("#d0141e", "#ec4a4f", "SPD"),
    "ssw": Tone("#003c8f", "#4f7fcf", "SSW"),
}
"""Conventional colours for party ids in the wahlwerk-data registry; never for chrome.

Carbon-dark parties are a dark slate, never black: black would read as ink.
"""

UNRECORDED = Tone("#c8c6c0", "#4f5158", "Seats whose party is not on record")

FALLBACK_COLORS: tuple[Tone, ...] = (
    Tone("#8c6d31", "#b3925a"),
    Tone("#6b6ecf", "#9a9ce6"),
    Tone("#7b4173", "#b077a8"),
    Tone("#637939", "#93a866"),
    Tone("#9c6b5e", "#c4958a"),
)
"""Cycled through, in order of appearance, for labels without a conventional colour."""
