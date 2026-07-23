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

## Where the unit goes — the shape decides

A unit belongs wherever the reader's eye lands on the number, and that is a
property of the chart's **shape**, not its name. So the rule is not "always
state a unit" — it is *state it where there is nowhere else to read it*.

| family | kinds | where the unit lives |
|---|---|---|
| `required` | sankey, pie, funnel, gauge, price-history, distribution | the **subtext**. There is nowhere else — a ribbon, a slice, a stage is a bare number with no axis beside it. |
| `axis` | bar, line, area, their stacked forms, waterfall | the **axis name** (`y_name`), which sits right next to the numbers. `unit` still allowed when it genuinely helps. |
| `multi` | scatter | **per axis** (`x_name` *and* `y_name`). Two measures, two units — one subtext for both would be a lie. |
| `none` | correlation matrix, 100% stacked, drawdown, radar | **nothing.** The scale is fixed by construction — a coefficient is −1…1, a mix column is always 100% — and demanding a unit here only teaches authors to write something meaningless. |

```jinja
{{ c.sankey(caption="Apple FY2025 — revenue to net income", unit="$ millions", …) }}
{{ c.bar(caption="Revenue by quarter", y_name="$M", …) }}
{{ c.scatter(caption="Risk against return", x_name="volatility %", y_name="return %", …) }}
```

Every kind accepts `unit` regardless of family — the API stays uniform, and the
family governs what is *required*, not what is *allowed*.

### Each chart declares its own family

The family is a `{# unit: … #}` header in the component, beside `purpose` and
`sample`:

```jinja
{# purpose: flow decomposition — how a total splits, merges or converts #}
{# unit: required — a ribbon is a bare number with no axis to label #}
```

`builder.py check` reads that declaration and enforces the matching rule —
including, for a `required` kind, that **the showcase demo states a unit**,
because the showcase is the reference example and a demo that omits one teaches
every copy to omit it. A missing or unknown header is itself a failure, so a new
chart cannot skip the decision by saying nothing.

### The title area has one owner

`_render.html.j2` sets the title, positions the legend clear of it, and
reserves the top margin — for every kind, from one rule. Do not set `title` in
a chart component and do not hand-tune a `top`: pass `caption` and `unit` to
`r.out(option, height, note, caption, unit)` and let it place them. When each
component did this for itself the copies drifted, and the sankey ended up
drawing its caption straight through the ribbons.

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

Each kind carries a `{# sample: … #}` header — a real call with real arguments.
Nothing runs it, so treat it as the worked example to copy from, and check a new
kind by composing a document with it and opening that in a browser.

## Colour is not yours to choose

Every kind takes its colours from the design system — the categorical palette
for series identity, the sequential ramp for ordered quantities, and the
semantic tones **only for direction** (a waterfall's rise and fall, a signed
bar's sign, a candlestick's up and down). All three live in
`js/modules/charts.js`.

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
