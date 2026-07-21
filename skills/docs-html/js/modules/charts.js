/* docs-html/charts — the shared chart frame. ENGINE-AGNOSTIC.

   Every chart in the system, whatever renders it, ends up as an <svg> inside
   the same card: the validated surface, a fixed canvas height, an icon toolbar
   (download SVG · copy source), and one debounced resize dispatch for the whole
   page. This file owns all of that and knows nothing about any engine.

   An engine module (today only chart-apache-echarts.js; the pattern takes more)
   does exactly three things: parse its own spec, build a frame, and draw into
   `frame.canvas`.

       const frame = new docsHtml.chart.Frame({ pre, index, source });
       <engine>.renderInto(frame.canvas, spec);
       frame.onResize(() => <engine>.resize());

   `pre` is the source block; it is hidden once the chart renders and stays in
   the DOM as the fallback (charts.css styles it as a readable code box, so an
   unreachable CDN or an invalid spec degrades to source instead of breaking).

   It also owns the DESIGN SYSTEM's dataviz tokens as plain data — PALETTE and
   TOKENS below. They are deliberately NOT in any engine's theme format: an
   engine translates them into whatever shape it needs, so a second engine
   inherits the same validated colors rather than re-picking them. Rebrand the
   dataviz palette here, never per chart and never per engine. */

"use strict";

docsHtml.chart = (() => {
  /* The validated 8-slot categorical palette, in FIXED order (never cycled).
     Validated against the .chart-figure surface (bg-soft, #f7f9fb) — see
     css/REFERENCE.md; re-run the dataviz validator before changing either. */
  const PALETTE = ["#2a78d6", "#008300", "#e87ba4", "#eda100",
                   "#1baf7a", "#eb6834", "#4a3aa7", "#e34948"];

  /* Ink, axis and surface tokens. Literal values because engines cannot read
     CSS custom properties; kept in sync with css/modules/base.css. */
  const TOKENS = {
    ink:     "#182338",
    muted:   "#5b6b81",
    axis:    "#c3c2b7",
    grid:    "#eef1f5",
    surface: "#ffffff",
    border:  "#dde3ea",
    font:    "Inter, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  };

  const DEFAULT_HEIGHT = 340;
  const RESIZE_DEBOUNCE = 150;

  /* One debounced resize dispatch for every chart on the page, whatever engine
     drew them — not one listener per chart. */
  const resizers = [];
  let timer;
  addEventListener("resize", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      for (const fn of resizers) {
        try { fn(); } catch (e) { /* one chart failing must not stop the rest */ }
      }
    }, RESIZE_DEBOUNCE);
  });

  /** One chart's card: the surface, the canvas an engine draws into, and the
      toolbar. */
  class Frame {

    /** The toolbar, declaratively — same three entry kinds as the diagram
        Viewer's spec:
          { sep: true }                    a group separator
          { render: (f) => element }       any custom element
          { icon, title, action }          a button */
    static BUTTONS = [
      { icon: "download", title: "download as SVG", action: (f) => f.downloadSvg() },
      { icon: "copy",     title: null,              action: (f, btn) => f.copySource(btn) },
    ];

    constructor({ pre, index = 1, source = "", copyTitle = "copy chart source",
                  height, extraButtons = [] }) {
      this.pre = pre;
      this.index = index;
      this.source = source;              // live source; engines may update it
      this.copyTitle = copyTitle;
      this.extraButtons = extraButtons;

      // The generated figure is the card; the source <pre> stays in the DOM,
      // hidden, as the degradation path.
      this.figure = document.createElement("figure");
      this.figure.className = "chart-figure";
      pre.after(this.figure);
      pre.hidden = true;

      this.canvas = document.createElement("div");
      this.canvas.className = "chart-canvas";
      // Height is inline because an engine measures the container before it can
      // draw; per-document tuning is data-height on the source block.
      this.canvas.style.height =
        (height ?? docsHtml.data(pre, "height", DEFAULT_HEIGHT)) + "px";
      this.figure.appendChild(this.canvas);

      this.#buildToolbar();
    }

    /** Register a redraw callback with the shared debounced resize dispatch. */
    onResize(fn) { resizers.push(fn); }

    /* ---- export actions ---- */

    /** The <svg> is queried lazily: it does not exist until the engine has
        drawn, and an engine may replace it on redraw. */
    downloadSvg() {
      const svg = this.canvas.querySelector("svg");
      if (!svg) return;
      const clone = svg.cloneNode(true);
      clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
      const blob = new Blob([new XMLSerializer().serializeToString(clone)],
                            { type: "image/svg+xml;charset=utf-8" });
      docsHtml.util.downloadBlob(`chart-${this.index}.svg`, blob);
    }

    copySource(btn) {
      docsHtml.util.copyText(this.source || "").then(() => {
        btn.innerHTML = docsHtml.icons.check;     // brief "done" flash
        setTimeout(() => { btn.innerHTML = docsHtml.icons.copy; }, 1200);
      }).catch(() => {});
    }

    /* ---- private wiring ---- */

    /** Build the toolbar by walking the spec — generic, knows no single entry.
        It hangs off the figure, not the canvas: the canvas belongs to the
        engine, which is free to replace its contents on every redraw. */
    #buildToolbar() {
      const bar = document.createElement("div");
      bar.className = "chart-tools";

      const specs = this.extraButtons.length
        ? [...this.extraButtons, { sep: true }, ...Frame.BUTTONS]
        : [...Frame.BUTTONS];

      for (const spec of specs) {
        if (spec.sep) {
          const s = document.createElement("span");
          s.className = "sep";
          bar.appendChild(s);
        } else if (spec.render) {
          bar.appendChild(spec.render(this));
        } else {
          const b = document.createElement("button");
          b.type = "button";
          const title = spec.title || this.copyTitle;   // copy's label is per-engine
          b.title = title;
          b.setAttribute("aria-label", title);
          b.innerHTML = docsHtml.icons[spec.icon];
          b.addEventListener("click", () => spec.action(this, b));
          if (spec.wire) spec.wire(this, b);
          bar.appendChild(b);
        }
      }
      this.figure.appendChild(bar);
    }
  }

  /** Flag an unparseable spec: the source stays visible, styled as an error. */
  const markError = (pre) => pre.classList.add("chart-error");

  return { PALETTE, TOKENS, Frame, markError, DEFAULT_HEIGHT };
})();
