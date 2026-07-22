"""docs-html — chartkit: option builders for the chart component family.

Sixteen chart components would otherwise be sixteen copies of the same option
skeleton. They share it from here instead: each component macro stays a handful
of lines that names its kind and passes data through, and the parts that are
genuinely shared — axis wiring, the title/legend/grid block, stacking, the
tooltip trigger — are written once.

This lives beside `dataviz.py` rather than inside `builder.py` for the same
reason: the composer should be about composing.

Colours are never chosen here. Where a mark needs a specific tone the builder
emits a REFERENCE ("palette:1", "token:positive") which
`docsHtml.chart.resolveColors` substitutes at view time, so the design system
stays the only place a hex is written.
"""

from __future__ import annotations

# Direction tones. Only ever used where the colour encodes which WAY a number
# went — never to tell two series apart. See TOKENS in js/modules/charts.js.
UP, DOWN, NEUTRAL = "token:positive", "token:negative", "token:muted"


def _frame(option: dict, caption: str, legend_for: int,
           y_named: bool = False, x_named: bool = False) -> dict:
    """Title, legend and the grid every cartesian chart shares.

    The legend appears from two series up — identity is never colour alone —
    and the top margin only reserves room for a title when there is one.

    The left and bottom margins widen when an axis carries a NAME, because
    ECharts' `containLabel` reserves room for tick labels only: at the default
    margin a rotated axis name renders straight off the edge of the card and
    silently disappears."""
    if caption:
        option["title"] = {"text": caption}
    if legend_for > 1:
        option["legend"] = {}
    option["grid"] = {"left": 46 if y_named else 8,
                      "right": 16,
                      "top": 52 if caption else 16,
                      "bottom": 34 if x_named else 8,
                      "containLabel": True}
    return option


def _value_axis(name: str, vertical: bool = True) -> dict:
    """A value axis. The name sits MID-axis: ECharts puts it at the end by
    default, which is exactly where the title is. A vertical axis rotates its
    name to run alongside; a horizontal one must not, or it reads sideways."""
    axis: dict = {"type": "value"}
    if name:
        axis.update({"name": name, "nameLocation": "middle"})
        axis.update({"nameGap": 46, "nameRotate": 90} if vertical
                    else {"nameGap": 28})
    return axis


def cartesian(series, categories=(), caption="", y_name="", kind="line",
              smooth=False, area=False, stack=False, horizontal=False,
              normalize=False, tones=False, label=False):
    """The line/bar family: every variant is this function plus flags.

    `series` is [(name, [values])]; `categories` labels the shared axis.

    normalize -> each value becomes its share of that category's column total,
    which is the whole point of a 100% stacked chart and the one thing an author
    should never be left to do by hand.
    tones     -> colour each bar by the SIGN of its value (direction, not
    identity), for variance charts that cross zero."""
    values = [list(v) for _, v in series]
    if normalize:
        totals = [sum(abs(col[i]) for col in values) for i in range(len(categories))]
        values = [[(100 * v / totals[i] if totals[i] else 0) for i, v in enumerate(col)]
                  for col in values]

    built = []
    for (name, _), col in zip(series, values):
        s: dict = {"type": kind, "name": name}
        if kind == "line":
            if smooth:
                s["smooth"] = True
            if area:
                s["areaStyle"] = {}
            s["showSymbol"] = len(categories) <= 24
        if stack:
            s["stack"] = "total"
        if tones:
            s["data"] = [{"value": round(v, 4),
                          "itemStyle": {"color": UP if v >= 0 else DOWN}} for v in col]
        else:
            s["data"] = [round(v, 4) for v in col]
        if label or normalize:
            s["label"] = {"show": True, "position": "inside" if stack else "top"}
        built.append(s)

    cat_axis = {"type": "category", "data": list(categories)}
    val_axis = _value_axis(y_name, vertical=not horizontal)
    if normalize:
        val_axis.update({"max": 100})
    option = {
        "tooltip": {"trigger": "axis",
                    "axisPointer": {"type": "shadow" if kind == "bar" else "line"}},
        "xAxis": val_axis if horizontal else cat_axis,
        "yAxis": cat_axis if horizontal else val_axis,
        "series": built,
    }
    if horizontal:
        # A horizontal bar chart reads top-to-bottom; without this the first
        # category lands at the BOTTOM and the ranking looks inverted.
        option["yAxis"]["inverse"] = True
    return _frame(option, caption, len(built),
                  y_named=bool(y_name) and not horizontal,
                  x_named=bool(y_name) and horizontal)


def waterfall(steps, caption="", y_name=""):
    """A waterfall, which ECharts has no series type for.

    It is faked with two stacked bars: an invisible `placeholder` that lifts each
    floating bar to where it starts, and the visible delta on top. The
    placeholder heights are a running cumulative total — arithmetic the author
    would otherwise redo by hand for every chart, getting it wrong silently,
    because a waterfall with a bad placeholder still draws.

    `steps` is [(label, value, kind)] with kind start | delta | total."""
    labels, base, bars, cum = [], [], [], 0.0
    for label, value, kind in steps:
        labels.append(label)
        if kind in ("start", "total"):
            base.append(0)
            bars.append({"value": round(abs(value), 4),
                         "itemStyle": {"color": "palette:1"}})
            cum = value
        else:
            lo = min(cum, cum + value)
            base.append(round(lo, 4))
            bars.append({"value": round(abs(value), 4),
                         "itemStyle": {"color": UP if value >= 0 else DOWN}})
            cum += value

    option = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {"type": "category", "data": labels},
        "yAxis": _value_axis(y_name),
        "series": [
            {"type": "bar", "name": "placeholder", "stack": "wf",
             "itemStyle": {"color": "transparent"},
             "emphasis": {"itemStyle": {"color": "transparent"}},
             "tooltip": {"show": False}, "silent": True, "data": base},
            {"type": "bar", "name": "change", "stack": "wf",
             "label": {"show": True, "position": "top"}, "data": bars},
        ],
    }
    option = _frame(option, caption, 1, y_named=bool(y_name))
    # The placeholder is scaffolding, not a series. Name the legend explicitly
    # so the engine's "two or more series -> add a legend" default does not
    # advertise it.
    option["legend"] = {"data": ["change"], "show": False}
    return option


def pie(slices, caption="", donut=True):
    """Composition. `slices` is [(name, value)]. A donut by default — the hole
    costs nothing and stops the eye reading area as a total."""
    option = {
        "tooltip": {"trigger": "item"},
        "series": [{"type": "pie",
                    "radius": ["42%", "70%"] if donut else "68%",
                    "itemStyle": {"borderWidth": 2},
                    "data": [{"name": n, "value": v} for n, v in slices]}],
    }
    if caption:
        option["title"] = {"text": caption}
    option["legend"] = {}
    return option


def scatter(series, caption="", x_name="", y_name=""):
    """Two measures per entity. `series` is [(name, [(x, y, label)])] — the
    third element is optional and labels the point."""
    built = []
    for name, points in series:
        data = []
        for p in points:
            x, y = p[0], p[1]
            item: dict = {"value": [x, y]}
            if len(p) > 2:
                item["name"] = p[2]
                item["label"] = {"show": True, "position": "right",
                                 "formatter": "{b}", "fontSize": 10}
            data.append(item)
        built.append({"type": "scatter", "name": name, "data": data})

    option = {
        "tooltip": {"trigger": "item"},
        "xAxis": _value_axis(x_name, vertical=False) | {"scale": True},
        "yAxis": _value_axis(y_name) | {"scale": True},
        "series": built,
    }
    return _frame(option, caption, len(built),
                  y_named=bool(y_name), x_named=bool(x_name))


def radar(indicators, series, caption=""):
    """Multi-attribute comparison. `indicators` is [(name, max)] — pass max=None
    and it is derived from the data.

    The derived max is the largest observed value across every series, so all
    axes share a scale only when the data does. A radar with per-axis maxima
    chosen ad hoc draws whatever shape you like, which is why this is computed
    rather than left to the caller."""
    observed = [max((vals[i] for _, vals in series), default=0)
                for i in range(len(indicators))]
    built_ind = [{"name": name,
                  "max": mx if mx is not None else round(observed[i] * 1.15, 2)}
                 for i, (name, mx) in enumerate(indicators)]
    # The plot is pulled down and in: at full size the topmost indicator label
    # collides with the title and legend, which both sit at the top of the card.
    option = {
        "tooltip": {"trigger": "item"},
        "radar": {"indicator": built_ind, "radius": "62%",
                  "center": ["50%", "58%" if caption else "52%"]},
        "series": [{"type": "radar",
                    "data": [{"name": n, "value": v} for n, v in series]}],
    }
    if caption:
        option["title"] = {"text": caption}
    if len(series) > 1:
        option["legend"] = {}
    return option


def funnel(stages, caption=""):
    """Stage-to-stage narrowing. `stages` is [(name, value)]."""
    option = {
        "tooltip": {"trigger": "item"},
        "series": [{"type": "funnel", "left": "12%", "right": "12%",
                    "sort": "descending", "gap": 2,
                    "label": {"show": True, "position": "inside"},
                    "data": [{"name": n, "value": v} for n, v in stages]}],
    }
    if caption:
        option["title"] = {"text": caption}
    option["legend"] = {}
    return option


def gauge(value, minimum=0, maximum=100, caption="", unit=""):
    """One value against a range.

    Deliberately plain: no coloured danger bands. A gauge already spends a great
    deal of ink on one number (see this component's usage.md), and banding it
    would add a judgement the number itself does not carry."""
    option = {
        "series": [{"type": "gauge", "min": minimum, "max": maximum,
                    "progress": {"show": True, "width": 12},
                    "axisLine": {"lineStyle": {"width": 12}},
                    "axisTick": {"show": False},
                    "splitLine": {"length": 8},
                    "axisLabel": {"fontSize": 10},
                    "pointer": {"width": 4},
                    "detail": {"fontSize": 22, "offsetCenter": [0, "70%"],
                               "formatter": f"{{value}}{unit}"},
                    "data": [{"value": value}]}],
    }
    if caption:
        option["title"] = {"text": caption}
    return option


# Exposed to templates by builder.make_env.
EXPORTS = {
    "chart_cartesian": cartesian,
    "chart_waterfall": waterfall,
    "chart_pie": pie,
    "chart_scatter": scatter,
    "chart_radar": radar,
    "chart_funnel": funnel,
    "chart_gauge": gauge,
}
