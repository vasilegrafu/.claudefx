# Charts — charts

Declarative data charts — a spec in the document, rendered to SVG at view time, never a screenshot.

**Use when** the shape of the numbers carries the argument.

---

## The chart kinds

This is the list. A chart in a docs-html document is one of these forms, and
picking the form is the first decision — before the data, before the colours.
Anything not here is either a [[mermaid]] diagram (a relationship, not a
measurement) or not a chart at all (see *When it is not a chart* below).

Every kind is a macro: you pass data, it writes the spec. None of them takes
colours — those come from the design system.

### Over time

| kind | call | what it is for |
|---|---|---|
| line | `{{ c.line(...) }}` | a measure over time — the honest default |
| smoothed line | `{{ c.smoothed_line(...) }}` | the trend, when the wiggles are noise |
| area | `{{ c.area(...) }}` | as line, where the quantity beneath is real |
| stacked line | `{{ c.stacked_line(...) }}` | additive parts and their total |
| stacked area | `{{ c.stacked_area(...) }}` | composition and total over time |
| price action | `{{ c.price_history(...) }}` | candlestick with volume, one shared axis |
| drawdown | `{{ c.drawdown_curve(...) }}` | peak-to-trough decline, derived for you |

### Across categories

| kind | call | what it is for |
|---|---|---|
| bar | `{{ c.bar(...) }}` | the workhorse comparison |
| stacked column | `{{ c.stacked_column(...) }}` | parts of a whole per category |
| stacked horizontal bar | `{{ c.stacked_horizontal_bar(...) }}` | the same, for long category names |
| 100% stacked | `{{ c.stacked_normalized(...) }}` | mix, when totals differ wildly |
| signed bar | `{{ c.bar_negative(...) }}` | a measure that crosses zero |
| waterfall | `{{ c.waterfall(...) }}` | how one total became another |
| pie | `{{ c.pie(...) }}` | three or four parts of one whole |
| funnel | `{{ c.funnel_chart(...) }}` | stage-to-stage narrowing |

### Relationships and shape

| kind | call | what it is for |
|---|---|---|
| flow | `{{ c.sankey(...) }}` | how a total splits and converts across stages |
| scatter | `{{ c.scatter(...) }}` | two measures per entity |
| correlation | `{{ c.correlation_matrix(...) }}` | pairwise relationships, on the sequential ramp |
| distribution | `{{ c.return_distribution(...) }}` | spread rather than average, outliers drawn |
| radar | `{{ c.radar(...) }}` | profile shape across attributes |
| gauge | `{{ c.gauge(...) }}` | one value against a real range — read its usage.md first |

Anything the catalogue does not cover, write directly as an ECharts `option`
through [[apache-echarts]]. The macros are a shortcut to the common forms, not a
fence around the engine.

## Where the maths happens

Four kinds compute something at compose time, so the rendered spec carries the
derived numbers and a reader can check them:

- **waterfall** — the running cumulative total behind each floating bar.
  ECharts has no waterfall series; it is a transparent placeholder stack, and
  getting the placeholder wrong still draws a chart.
- **100% stacked** — each value as a share of its column total. Pass raw
  amounts.
- **drawdown** — the running peak, from a level series.
- **distribution** — quartiles and Tukey fences, outliers separated rather than
  absorbed into a whisker.

`python builder.py charts` renders every one of them from its `{# sample: … #}`
header and fails if the spec is malformed or breaks the relief rule.

## Colour is not yours to choose

Every kind takes its colours from the design system — the categorical palette
for series identity, the sequential ramp for ordered quantities, and the
semantic tones **only for direction** (a waterfall's rise and fall, a signed
bar's sign, a candlestick's up and down). All three live in
`js/modules/charts.js` and are checked by `python builder.py dataviz`.

A spec that genuinely needs to name one references it rather than writing a hex:
`"palette:3"`, `"token:positive"`, `"ramp:2"`. Colouring by ROLE rather than by
item is why a fifteen-node sankey never runs out of colours.

## When it is NOT a chart

Several of these have a CSS twin in `investing` that needs no engine, prints
cleanly, and keeps its numbers as selectable text. Prefer the twin when the
figures are meant to be read rather than compared by eye:

| chart | CSS twin |
|---|---|
| [[waterfall]] | [[bridge]] |
| [[funnel-chart]] | [[funnel]] |
| [[gauge]] | [[meter]], or a [[kpi-tiles]] tile |
| [[radar]] | [[scorecard]] |
| [[pie]] / [[stacked-normalized]] | [[exposure-bars]] |

And some things are not charts at all: a single headline number is a
[[kpi-tiles]] tile, a 2×2 positioning grid is [[risk-matrix]] or
[[quadrant-map]], a schedule of amounts by year is [[debt-maturity]]. Reach for
a chart when the *shape* of the data is the argument; reach for an investing
component when the numbers are.
