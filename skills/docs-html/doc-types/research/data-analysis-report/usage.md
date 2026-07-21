# data-analysis-report

_Authoring guidance for the `data-analysis-report` document type — audience, depth, and rules._

- Audience: someone who will act on the numbers — or rerun them.
- Filename: `docs/data-analysis-report-<topic>.html`.
- Depth: ask.
- Rules: the Data section makes the dataset reconstructible (source, period,
  cleaning); code snippets carry the method when prose would blur it
  (`data-lang` coloring applies); charts are `chart_apache_echarts` — the data stays
  in the document as an editable JSON option, never an image; a result without
  its caveat is a half-result.
