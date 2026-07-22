"""docs-html — the Python the build runs on, beside the `builder.py` entry point.

`builder.py` stays at the skill root because it is the command you type. The
modules here are what it calls:

    chartkit.py   builds the ECharts option dicts the chart components emit —
                  eleven of the twenty-one kinds are one function plus flags
    dataviz.py    verifies the chart colour tokens in js/modules/charts.js:
                  contrast, colour-blind separation, ramp monotonicity

Neither belongs under `components/`. That tree is *discovered* — the builder
rglobs it for files named `component.html.j2` — and it holds markup, not
computation. `dataviz.py` in particular has nothing to do with components at
all: it reads the JavaScript.
"""
