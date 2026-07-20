/* docs-html/drawio — freeform diagrams from draw.io / diagrams.net mxGraph XML,
   rendered at view time by the pinned diagrams.net viewer.

   Markup (the mxGraph XML as plain text in the document — the editable source):
     <pre class="drawio"><mxGraphModel>…</mxGraphModel></pre>

   The viewer (a single ~3.6 MB script) loads from the pinned CDN only when the
   document actually contains a .drawio element, and renders SVG (crisp in print,
   its own zoom/lightbox toolbar). If the CDN is unreachable, the mxGraph XML
   stays visible as a code box (diagrams.css) — verbose, but the page survives.

   Unlike Mermaid, draw.io XML is machine geometry, not hand-written prose: it is
   authored/edited as XML (positions + styles are explicit), never auto-laid-out. */

"use strict";

(() => {
  const VIEWER = "https://cdn.jsdelivr.net/gh/jgraph/drawio@24.7.17/src/main/webapp/js/viewer-static.min.js";

  docsHtml.register({
    name: "drawio",
    selector: "pre.drawio",

    init(nodes) {
      const pres = [...nodes].filter((p) => p.textContent.trim());
      if (!pres.length) return;

      // For each source, add a .mxgraph host carrying the XML; hide the source.
      const hosts = [];
      for (const pre of pres) {
        const host = document.createElement("div");
        host.className = "mxgraph drawio-figure";
        host.setAttribute("data-mxgraph", JSON.stringify({
          xml: pre.textContent.trim(),
          resize: true,           // fit the reading column
          nav: true,              // hover navigation
          toolbar: "zoom layers", // in-place zoom; lightbox on click by default
        }));
        pre.after(host);
        pre.hidden = true;
        hosts.push(host);
      }

      const revert = () => {          // viewer unavailable → show the XML source
        for (const h of hosts) h.remove();
        for (const p of pres) p.hidden = false;
      };

      docsHtml.util.loadScript(VIEWER).then(() => {
        try {
          window.GraphViewer.processElements();   // renders every .mxgraph host to SVG
        } catch (e) {
          revert();
        }
      }).catch(revert);              // CDN down → the mxGraph XML stays readable
    },
  });
})();
