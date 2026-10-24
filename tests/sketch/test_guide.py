from wahlwerk_ui.parties import PARTY_COLORS
from wahlwerk_ui.sketch import guide


def test_every_plate_draws_and_saves(tmp_path):
    paths = guide.write(tmp_path / "style")
    assert [p.name for p in paths] == [
        "1-anatomy.svg",
        "2-inks.svg",
        "3-strokes.svg",
        "4-circles.svg",
        "5-labels.svg",
        "6-furniture.svg",
        "parties.svg",
        "party-colours.md",
    ]
    for path in paths[:-1]:
        assert path.read_text("utf-8").startswith("<?xml")


def test_the_party_page_lists_every_party():
    page = guide.party_page()
    for key, tone in PARTY_COLORS.items():
        assert f"| `{key}` | {tone.usage} | `{tone.light}` | `{tone.dark}` |" in page
