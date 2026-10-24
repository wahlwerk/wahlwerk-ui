# wahlwerk-ui

Seat charts for the [wahlwerk](../wahlwerk) engine: hemicycles and half pies as small, structured SVG, drawn in code in the style of a technical drawing (thin lines, construction geometry left visible, the parties the only saturated colour). No dependencies; light and dark themes. The rules are in [STYLE.md](STYLE.md), party colours in [docs/party-colours.md](docs/party-colours.md).

```python
from wahlwerk_ui.plot.chamber.card import chamber_html

chamber_html([("spd", 120), ("cdu-csu", 208), ("afd", 152)], title="Bundestag")  # kind="pie" for a half pie
```

From the engine: `pip install wahlwerk[ui]`, then `chamber.fancy_html()` or `chamber.fancy_html(kind="pie")`.

Save a drawing for print (light colours written in place, named layers kept):

```python
from wahlwerk_ui.plot.chamber.seat import hemicycle_svg

hemicycle_svg([("spd", 120), ("cdu-csu", 208)], majority=True).save("figures", "bundestag")
```
