"""wahlwerk-ui -- display and plotting for wahlwerk.

Plots take plain data (labels and seat counts), never engine objects, so this package
does not depend on the engine; the engine imports it lazily for its notebook display.
"""

from __future__ import annotations

__version__ = "0.1.0"
