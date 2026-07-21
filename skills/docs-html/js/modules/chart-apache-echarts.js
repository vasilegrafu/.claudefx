/* docs-html/chart-apache-echarts — declarative charts rendered at view time by
   Apache ECharts. ONE engine behind the shared chart frame (charts.js).

   Markup (a JSON ECharts `option` as plain text in the document — no images,
   no per-document JS):
     <pre class="chart apache-echarts">{ "xAxis": {...}, "series": [...] }</pre>

   `chart` is the marker every engine shares (charts.css styles the fallback
   box once); `apache-echarts` selects this engine.

   ECharts loads from the pinned CDN only when the document actually contains a
   chart of this kind, and renders SVG (crisp in print, one <main> column). If
   the CDN is unreachable — or the JSON is invalid — the spec stays visible as a
   readable code box; the page never breaks.

   The theme below is a TRANSLATION of the design system's dataviz tokens
   (docsHtml.chart.PALETTE / .TOKENS) into ECharts' theme shape. Change the
   colors in charts.js, never here and never per chart. */

"use strict";

(() => {
  const ECHARTS = "https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js";
  const THEME_NAME = "docs-html";

  /** Translate the shared tokens into an ECharts theme. Built lazily so the
      shared module is guaranteed to have loaded first. */
  const buildTheme = () => {
    const { ink, muted, axis, grid, surface, border, font } = docsHtml.chart.TOKENS;
    const axisCommon = {
      axisLine:  { lineStyle: { color: axis } },
      axisTick:  { show: false },
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: grid } },
    };
    return {
      color: docsHtml.chart.PALETTE,       // fixed order, never cycled
      backgroundColor: "transparent",
      textStyle: { fontFamily: font, color: ink },
      title: {
        textStyle: { color: ink, fontWeight: 700, fontSize: 15 },
        subtextStyle: { color: muted },
      },
      legend: { textStyle: { color: muted }, icon: "roundRect", itemWidth: 14, itemHeight: 8 },
      tooltip: {
        backgroundColor: surface, borderColor: border, borderWidth: 1,
        textStyle: { color: ink, fontFamily: font },
        axisPointer: { lineStyle: { color: axis }, crossStyle: { color: axis } },
      },
      grid: { containLabel: true, left: 8, right: 16, top: 44, bottom: 8 },
      categoryAxis: { ...axisCommon, splitLine: { show: false } },
      valueAxis:    { ...axisCommon, axisLine: { show: false } },
      logAxis:      { ...axisCommon, axisLine: { show: false } },
      timeAxis:     axisCommon,
      line: { lineStyle: { width: 2 }, symbol: "circle", symbolSize: 8 },
      bar:  { itemStyle: { borderRadius: [4, 4, 0, 0] }, barMaxWidth: 44 },
    };
  };

  docsHtml.register({
    name: "chart-apache-echarts",
    selector: "pre.chart.apache-echarts",

    init(nodes) {
      // Parse every spec FIRST — a bad JSON degrades to source without pulling
      // the ~900 KB engine, and an all-invalid page skips the load entirely.
      const jobs = [];
      for (const pre of nodes) {
        try {
          jobs.push({ pre, option: JSON.parse(pre.textContent), source: pre.textContent });
        } catch (e) {
          docsHtml.chart.markError(pre);   // stays visible; source is the fallback
        }
      }
      if (!jobs.length) return;

      docsHtml.util.loadScript(ECHARTS).then(() => {
        window.echarts.registerTheme(THEME_NAME, buildTheme());

        jobs.forEach(({ pre, option, source }, i) => {
          const frame = new docsHtml.chart.Frame({
            pre, index: i + 1, source,
            copyTitle: "copy ECharts spec",
          });

          // Nudge every chart toward the accessible defaults the dataviz method
          // requires, without overriding an author who set them explicitly.
          if (option.aria === undefined) option.aria = { enabled: true };
          if (option.tooltip === undefined) option.tooltip = {};
          if (option.legend === undefined && Array.isArray(option.series)
              && option.series.length > 1) option.legend = {};

          const chart = window.echarts.init(frame.canvas, THEME_NAME, { renderer: "svg" });
          chart.setOption(option);

          // Reflow on width change (responsive labels/layout, still crisp SVG).
          frame.onResize(() => chart.resize());
        });
      }).catch(() => {});   // CDN down → the JSON spec stays visible, readable
    },
  });
})();
