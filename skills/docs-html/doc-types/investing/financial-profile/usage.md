# financial-profile

_Authoring guidance for the `financial-profile` document type — audience, depth, and rules._

- Audience: someone who must understand a business before deciding anything
  about it. This document does NOT make a call — that is [[investment-thesis]],
  and it is normally read second.
- Filename: `<ticker>-financial-profile.html`, written by `builder.py new` when
  you pass `--slug <TICKER>`. Put it under `docs/stocks/<TICKER>/`, so that
  folder collects every report on the name.
- Depth: ask. Full means pulling the filings or a data feed; draft means
  skeleton + todos.
- Rules: **every number is dated and sourced** — a profile whose figures cannot
  be traced to a filing is an opinion. Label periods by FISCAL year and say so;
  fiscal years are not calendar years and mixing them silently misstates growth.
  The document describes; it does not recommend.

## What the skeleton composes

The document answers three questions in order, and the order is the point —
where the money comes from, where it goes, then what changed:

| section | components |
|---|---|
| Snapshot | [[security-header]] · [[lead]] |
| Where the money comes from | [[sankey]] (income statement) · [[segment-reporting]] |
| Where the money goes | [[sankey]] (cash deployment) |
| How it evolved | [[metric-trend]] ×2 · [[stacked-normalized]] · [[bridge]] |
| Reading | [[callout]] |

### Two sankeys, because "spending" means two different things

The first sankey is **accounting**: segments flow in, cost of revenue, R&D,
SG&A and tax flow out, net income is what is kept. The second is **cash**: what
management actually did with the money.

They disagree, and the gap is often the most interesting fact in the document.
Buybacks, dividends and debt repayment consume real money and appear **nowhere**
on the income statement — for a mature company they routinely dwarf capital
expenditure. A profile carrying only the first sankey quietly answers a question
the reader did not ask.

In the cash sankey, **gross up investing rather than netting it**, so capital
expenditure stays a visible node instead of vanishing inside a single "net
investing" ribbon.

### CONSERVATION — the one thing this document type can get silently wrong

**Inflows must equal outflows at every intermediate node, and nothing in the
rendering checks it.** An unbalanced sankey draws perfectly and lies. Both
diagrams need the arithmetic done by hand before publishing:

- income — segments = revenue; cost of revenue + gross profit = revenue;
  R&D + SG&A + operating income = gross profit; tax + net income = pre-tax.
- cash — total sources = total uses, with the residual carried as
  `Cash retained` rather than dropped.

[[bridge]] has the same exposure: its steps must carry the start value to the
end value. State it again here because it is the failure this document type is
most exposed to — two of its five exhibits are arithmetic the renderer trusts
the author to have got right.

### Sankey labels are canvas text, not HTML

Write `SG&A` and `Research & development` with a **raw ampersand** in sankey
node and link names. Everywhere else in a document `&amp;` is correct, but
sankey names are drawn onto a canvas by the chart engine and never pass through
an HTML parser — an entity written there renders literally, as `SG&amp;A`. The
serialiser escapes the raw `&` safely on the way out, so nothing is at risk.
Table and prose labels keep `&amp;` as usual.

### Why two trend tables

They answer different questions and neither substitutes for the other:
**revenue by segment** says where growth came from; **margins and returns** says
whether it came with operating leverage or was bought with spending. A company
can grow revenue for five years while every ratio in the second table decays.

## What it deliberately leaves out

Reach for these when the business needs them, rather than deleting them from
every draft:

| when the profile turns on… | add |
|---|---|
| geography, not product | a second [[segment-reporting]] |
| the balance sheet | [[balance-sheet]], [[debt-maturity]], [[working-capital]] |
| why returns are what they are | [[dupont]] |
| named comparables | [[peer-comparison]] |
| subscription or vintage economics | [[cohort-table]], [[unit-economics]] |
| the market's view over the same window | [[price-history]], [[drawdown-curve]] |
| accounting that needs flagging | [[footnote-disclosures]] |
| share count and buyback effect | [[roll-forward]] |

The full set is in `../../../components/domain-specific/investing/usage.md` and
`CATALOG.md`.

## The one thing to write first

The **`note` under each sankey**. The diagram shows the shape; the sentence says
what it means. Write those two sentences before filling any table — if you
cannot say what the shape of the earnings and the shape of the spending tell
you, the numbers underneath will not say it for you.
