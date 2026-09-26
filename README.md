# wahlwerk-ui

Display and plotting for [wahlwerk](../wahlwerk): hemicycle seat charts and half pies as small inline SVG for notebooks.

```python
from wahlwerk_ui.plot.chamber.card import chamber_html

chamber_html([("spd", 120), ("cdu-csu", 208), ("afd", 152)], title="Bundestag")  # kind="pie" for a half pie
```

From the engine: `pip install wahlwerk[ui]`, then `chamber.fancy_html()` or `chamber.fancy_html(kind="pie")`.
