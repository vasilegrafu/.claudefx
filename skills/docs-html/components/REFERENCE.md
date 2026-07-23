# components/ — reference

Deep reference for the component catalog. The authoring contract lives in
`../SKILL.md`; the generated call-form list is `../CATALOG.md`; how components
are *styled* (the CSS module map, page-local CSS, rebranding) is in
`../css/REFERENCE.md`. This file is how components are *organized and called*.

## The component model

- A component is a Jinja macro in
  `components/<group>/<category>/<name>/component.html.j2`
  (macro name = folder name with `-` → `_`), exposed on the `c` namespace so
  templates call `{{ c.<name>(...) }}` (leaf) or
  `{% call c.<name>(...) %}…{% endcall %}` (container) — no imports.
- The macro file's FIRST line is `{# purpose: one line #}` — read by
  `builder.py catalog` into `CATALOG.md`.
- Every component has a `usage.md` beside it (when + how, the rules) and a live
  demo in `../showcases/components.html`.
- Each category folder has its own `usage.md`: a one-line blurb (the single
  source for `CATALOG.md` intros and the showcase bands) plus a **Use when**
  line.

**To look something up, don't open files — ask the builder.** `CATALOG.md` lists
every call form + purpose; `python builder.py show <name>` prints one
component's call form, purpose, and full `usage.md`.

### The one exception: `_`-prefixed templates

`builder.py` discovers components by rglobbing for the exact filename
`component.html.j2`, so any *other* `.j2` file in this tree is invisible to it —
no macro on `c`, no `CATALOG.md` entry, no `usage.md` expected. That is the
escape hatch for **shared template internals**, and such files are named with a
leading underscore to say so at a glance:

| file | what it holds |
|---|---|
| `charts/_render.html.j2` | the tail every chart component shares — hand the built option to the engine, then print the `chart-note` |

Use one only when several components in a category would otherwise repeat the
same markup, and keep it to **markup**. A partial that returns a value is not
possible anyway — a Jinja macro produces output, not data — so a component
that needs to compute something computes it in its own file, next to the macro
that emits it. `components/` then stays a tree the builder can walk without
special cases, and no component sends a reader to a second file to learn what
it draws.

The chart family is the worked example: every kind builds its own ECharts
option in its own template (see `charts/return-distribution/component.html.j2`),
and `_render.html.j2` shares only the markup tail.

## The five groups

Categories sit inside a group that states the component's SCOPE — the same five
groups `css/` uses, so a component and the CSS that styles it are in matching
places:

| group | categories | what it means |
|---|---|---|
| `foundational/` | `structure`, `layout`, `content`, `lists`, `callouts`, `blocks`, `front-back-matter` | any document may use it; nothing here knows a domain |
| `domain-specific/` | `business`, `investing` | one domain owns it, and its CSS classes carry that domain's name |
| `math/` | — | the formula subsystem (KaTeX) |
| `diagrams/` | — | the diagram subsystem (Mermaid) |
| `charts/` | — | the chart subsystem (Apache ECharts) |

The last three are **rendering subsystems**, and each is its own group *and* its
own category: they hold their components directly, needing no extra level. Each
pairs a CSS module with a **lazy CDN engine** in `js/modules/`, so a document
that uses none of them downloads none of them. They are separate from one
another because what gets rendered differs — a formula, a drawn relationship,
data — and each carries its own engine (see `../js/REFERENCE.md`). `diagrams`
and `charts` additionally split shared-viewport from per-engine, so a second
engine is one file.

Within `foundational`, `layout` holds the spatial primitives
(`columns`/`column`, `grid`, `card`) that arrange the others; everything else is
content. In `domain-specific`, `business` carries decision and reporting
artifacts (statements, journal entries, SWOT) and `investing` the components
that support an allocation decision — the security, the call, the thesis,
valuation, portfolio and macro. Neither borrows from the other: they used to
share `badge`, which is precisely why `badge` is now foundational.

For which CSS module styles each one, see `../css/REFERENCE.md`.

## Adding a component

Add `components/<group>/<category>/<new>/{usage.md, component.html.j2}` — pick
the group by asking who may use it, then the category within it. The builder
discovers recursively, so nothing needs registering.

The macro file's FIRST line is `{# purpose: … #}`. Style it in the matching
`css/<group>/` file (see `../css/REFERENCE.md` → "Adding a module"); if the
group is `domain-specific`, every class you add must start with the domain's
name. Add a demo to `../showcases/components.html.j2`, then run
`python builder.py catalog` and `python builder.py showcase`.
