from wahlwerk_ui.style import (
    INKS,
    PARTY_COLORS,
    STROKE_FRAME_PX,
    STROKE_HAIRLINE_PX,
    STROKE_MAX_PX,
    STROKE_MIN_PX,
    Tone,
    css,
    slug,
    tone,
)


def test_every_colour_has_both_themes():
    for t in [*INKS.values(), *PARTY_COLORS.values()]:
        assert t.light.startswith("#") and t.dark.startswith("#")


def test_strokes_stay_in_the_band():
    for width in (STROKE_FRAME_PX, STROKE_HAIRLINE_PX):
        assert STROKE_MIN_PX <= width <= STROKE_MAX_PX


def test_no_party_is_black():
    for t in PARTY_COLORS.values():
        assert t.light.lower() not in ("#000", "#000000")


def test_adaptive_css_follows_the_theme_printable_does_not():
    parties = {"spd": PARTY_COLORS["spd"]}
    adaptive = css("ww-x", parties)
    assert "prefers-color-scheme: dark" in adaptive and "var(--ww-party-spd)" in adaptive
    assert 'data-jp-theme-light="false"' in adaptive
    printable = css("ww-x", parties, adaptive=False)
    assert "var(" not in printable and "@media" not in printable
    assert PARTY_COLORS["spd"].light in printable


def test_every_selector_is_scoped():
    for rule in css("ww-x", {}, adaptive=False).split("}"):
        if rule:
            assert rule.startswith("#ww-x")


def test_slug_and_tone():
    assert slug(None) == "unrecorded"
    assert slug("cdu-csu") == "cdu-csu"
    assert slug("<B> c") == "b-c"
    assert tone("#123456") == Tone("#123456", "#123456")


def test_the_card_rule_styles_the_scope_element_itself():
    assert "#ww-x.card{" in css("ww-x", {}, adaptive=False)
