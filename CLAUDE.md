# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`wahlwerk-ui` is a sibling of the wahlwerk repositories:

```
CODE/wahlwerk_/
  wahlwerk/          the engine       Apache-2.0     (rules-as-code for electoral law)
  wahlwerk-data/     the archive      GPL-3.0; data: its source's licence   (normalised election bundles, party registries)
  wahlwerk-execute/  notebooks        GPL-3.0        (analyses and figures)
  wahlwerk-ui/       this repo        GPL-3.0
```

Its role: display and plotting for wahlwerk objects. Plots take **plain data**
(labels and seat counts), never engine objects, so this package depends on nothing,
not even the engine. The engine imports it lazily as the optional extra `wahlwerk[ui]`
for `fancy_html()` notebook display. The siblings' conventions, which apply here unless
told otherwise:

- Dependencies run one way: consumers depend on the engine (and data), never the
  reverse. Reusable modelling logic belongs in `../wahlwerk`, not here; UI or plotting
  dependencies must not leak into the engine.
- The project is built **step by step**. Do only the step asked for; do not add
  modules, features or layout ahead of it to make something look complete.
- Election data is resolved by the engine: `$WAHLWERK_DATA`, then `../wahlwerk-data`,
  then a fetched cache. Do not hard-code data paths.
- `../wahlwerk/CLAUDE.md` and `../wahlwerk/README.md` are the source of truth for what
  the engine currently provides; check them before relying on an engine API.

## Project state

| Module | Contents |
|---|---|
| `style.py` | The drawing style as data: `Tone` (light, dark, usage), the ink ladder `CONSTRUCTION`, `DIMENSION`, `STRUCTURE`, `CONTENT`, the label inks `LABEL_FAINT`/`PLAIN`/`STRONG`, `STEP_FILL`/`STEP_LINE` (protocol steps), `SURFACE`, `LINE`, `INKS`; stroke band and widths, `DASH`, `EDGE_MIN_DIAMETER_PX`; `FONT_FAMILY`, `FONT_SIZE_PX`, `LABEL_WEIGHT`; `PARTY_COLORS`, `UNRECORDED`, `FALLBACK_COLORS`; `tone`, `slug`; `css(scope, parties, adaptive=True)`, the one style block |
| `parties.py` | `PARTY_COLORS`, `UNRECORDED`, `FALLBACK_COLORS`: kept apart because the list grows with every election; re-exported by `style.py`; `docs/party-colours.md` is generated from it |
| `sketch/plate.py` | `Plate` (a row of numbered `Panel`s: title, art, caption of a name and at most two lines; `svg`, `save`, `to_dict` with one SVG per panel for the web), `Panel.slot` |
| `sketch/primitives.py` | the pieces of a sketch, each on its rung: `unit`, `axis`, `guide_circle`, `dimension`, `box`, `rule`, `link`, `arrow`, `leader`, `dot`, `crowd`, `cross`, `mark`, `text`, `table`; compositions `ballot_paper`, `chamber` (`CHOICES`: yes, no, abstain, absent) |
| `sketch/guide.py` | the style guide drawn with the library: `plates()`, `parties()`, `party_page()`, `write(dir)`; `python -m wahlwerk_ui.sketch.guide docs/style` |
| `svg.py` | `Drawing` (layers `LAYERS` at fixed z-order, `add`, `line`, `label`, `markup`, `svg`), `Svg` (a `str` with `_repr_svg_`, `printable`, `save(dir, name)`), `scope_id`, `num` |
| `html.py` | `Html`: a `str` with `_repr_html_`, so Jupyter renders it without IPython |
| `plot/chamber/common.py` | `Group`, `check_groups`, `party_tones`, `majority_of`, `label_of`; re-exports `PARTY_COLORS` |
| `plot/chamber/seat.py` | `seat_layout` (hemicycle geometry), `hemicycle_drawing`, `hemicycle_svg` (every seat drawn) |
| `plot/chamber/pie.py` | `half_pie_drawing`, `half_pie_svg` (one wedge per group; `hole` for a half ring) |
| `plot/chamber/card.py` | `chamber_html(groups, kind="seats" \| "pie", majority=False)`: title, plot and legend under one style block |
| `plot/protocol.py` | `protocol_drawing`, `protocol_svg`, `protocol_html(steps, width=640, title="")`: a protocol as a technical drawing from plain step data (the engine's `flow.protocol_data`): steps as boxes in order with their citation and settings, a sequence or loop as a dashed frame around the steps it holds, the stage in the gutter, the facts written in the margin; two styles: a step in the step colour (`STEP_FILL`/`STEP_LINE`, `.step`, a frame `.step-frame`), and inside it each core concept it computes with (`uses`: a method, a threshold) as a paper block nested like steps, with the `wahlwerk.calc` calls it makes (and the step's own `calls`) |

Plots are pure-Python SVG, kept small (default 240 px wide) for inline notebook display.
Geometry uses floats (it is drawing, not arithmetic on votes), but the seats-per-ring
split is integer largest remainder, so a layout is the same everywhere. The engine pins
two things in its own tests: a card never says "majority" unless asked (`majority` is
off by default, since which majority matters is a question of the law), and the only
`<circle>`s are seats and the only `<path>`s are pie wedges (construction lines are
`<line>`; ring guides are `<path>` in the hemicycle only).

## Drawing style: a technical drawing, not an illustration

**`STYLE.md` is the style guide, step by step, with the plates in `docs/style/`; party colours are on `docs/party-colours.md`.** Regenerate both after any change to `style.py` or `parties.py`. No sketch of a particular subject lives here: the vote sketches are drawn by wahlwerk-site's `sketches.py`.

Carried over from IR-bands (the Knowledge diagrams and the style guide's specimen plate)
and phd_ui (`sketch/`, structured SVG built in code). `style.py`'s docstring is the full
statement; the rules:

- **Everything is code.** A drawing is generated, never edited and saved back. Illustrator
  rewrites SVG on save and drops the structure; place the file in a document of your own
  and draw hand additions on a layer there.
- **Readable files.** Named layers with Inkscape layer attributes, always in the order
  `construction`, `structure`, `subject`, `dimension`, `labels`, whatever order they were
  drawn in; empty layers are left out. One group per party (`party-spd`), one id per seat
  (`seat-spd-001`). All colours in one `<style>` block generated from `style.py`, every
  selector under the drawing's id (`scope_id`, deterministic: same input, same file), so
  drawings in one notebook never restyle each other.
- **The ink ladder.** Hierarchy by ink, not weight: every stroke between 0.6 and 2 px.
  Construction (dashed ring guides, the half axis) is almost invisible; then dimension
  (the majority mark), structure (the floor), content (seat and wedge edges); the parties
  are the subject and the only saturated colour. Before adding a stroke, decide its rung.
  A lighter ink before a thinner line, never a thicker one.
- **One face, one size, four inks** for every label (`FONT_FAMILY`, the code face, at
  `FONT_SIZE_PX`): faint, plain, strong, and strong at `LABEL_WEIGHT` for the subject. A
  plot that needs a bigger label needs fewer labels. In-plot text is lowercase.
- **Both themes.** Every colour is a `Tone`. Shown in a notebook or page, a drawing follows
  `prefers-color-scheme`, JupyterLab's `data-jp-theme-light` and `data-theme`; `Svg.save`
  writes the light values in place, since Illustrator and Inkscape read no CSS variables.
- **Party colours live in `parties.py`**; wahlwerk-site's `lib/tokens.ts` copies them. Change
  them there first. A carbon-dark party is a dark slate, never black: black reads as ink.
- No em dashes in any text.

## Commands

Managed with [uv](https://docs.astral.sh/uv/), Python 3.10 (`.python-version`).

```bash
uv sync                    # create/refresh .venv
uv add <pkg>               # runtime dependency
uv add --dev <pkg>         # dev dependency
```

All must pass before anything is called done:

```bash
uv run pytest -q
uv run mypy --strict src
uv run ruff check src tests
```
