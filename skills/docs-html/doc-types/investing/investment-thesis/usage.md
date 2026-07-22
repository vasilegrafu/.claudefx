# investment-thesis

_Authoring guidance for the `investment-thesis` document type — audience, depth, and rules._

- Audience: yourself in six months, or an investment partner — someone who
  must judge the bet without you in the room.
- Filename: `docs/investment-thesis-<asset>.html`
- Depth: ask. Full means reading filings/data; draft means skeleton + todos.
- Rules: the thesis states the VARIANT view (why the market is wrong), never
  a description of the company; scenarios carry explicit price/return
  outcomes; the invalidation criteria are falsifiable — a thesis without an
  exit condition is a hope, not a thesis. Update via `modify` with a
  change-history row on every material development.

## What the skeleton composes

The skeleton instantiates the components a thesis is **dishonest without** —
the call, the claims, the price, the odds, the risks:

| section | components |
|---|---|
| Summary | [[security-header]] · [[recommendation]] |
| Thesis | [[thesis-pillars]] — claim, evidence, **falsifier** |
| Valuation | [[valuation-multiples]] · [[valuation-range]] |
| Scenarios | [[scenarios]] · [[expected-value]] |
| Catalysts | [[catalyst-timeline]] |
| Risks | [[risk-metrics]] |

Two of these carry arithmetic the document must not get wrong:
**[[expected-value]] probabilities sum to 100%**, and **[[valuation-range]]
bars share one `scale_min`/`scale_max`** — a football field whose methods are
drawn on different scales compares nothing. Nothing in the rendering checks
either.

## What it deliberately leaves out

Reach for these when the argument needs them, rather than deleting them from
every draft:

| when the thesis turns on… | add |
|---|---|
| competitive position | [[five-forces]], [[quadrant-map]] |
| a cash-flow build | [[dcf-summary]] |
| named comparables | [[peer-comparison]] |
| a scored framework | [[scorecard]], [[composite-score]] |
| decomposing a move | [[bridge]], or the [[waterfall]] chart |
| accounting that needs flagging | [[footnote-disclosures]], [[income-statement]] |
| a price history | [[price-history]], [[drawdown-curve]] |
| segment detail | [[segment-reporting]] |

The full set is in `../../../components/investing/usage.md` and `CATALOG.md`.

## The one thing to write first

`thesis_pillars` — because the falsifier column is the part that makes the rest
of the document worth writing. If you cannot state what observation would break
a claim, that claim is not doing any work, and no amount of valuation detail
underneath it will help.
