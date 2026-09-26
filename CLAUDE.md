# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`wahlwerk-ui` is a sibling of the wahlwerk repositories:

```
CODE/wahlwerk_/
  wahlwerk/          the engine       Apache-2.0     (rules-as-code for electoral law)
  wahlwerk-data/     the archive      dl-de/by-2-0   (normalised election bundles, party registries)
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
| `html.py` | `Html`: a `str` with `_repr_html_`, so Jupyter renders it without IPython |
| `plot/chamber/common.py` | `Group`, `PARTY_COLORS`, `UNRECORDED_COLOR`, `check_groups`, `colors_for`, `label_of` |
| `plot/chamber/seat.py` | `seat_layout` (hemicycle geometry), `hemicycle_svg` (every seat drawn) |
| `plot/chamber/pie.py` | `half_pie_svg` (one wedge per group; `hole` for a half ring) |
| `plot/chamber/card.py` | `chamber_html(groups, kind="seats" \| "pie")`: title, plot and legend |

Plots are pure-Python SVG strings, kept small (default 240 px wide) for inline notebook
display. Geometry uses floats (it is drawing, not arithmetic on votes), but the
seats-per-ring split is integer largest remainder, so a layout is the same everywhere.

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
