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
| Snapshot | [[security-header]] · basis of preparation ([[facts]] in a [[callout]]) · [[lead]] |
| Where the money comes from | [[sankey]] (income statement) · [[segment-reporting]] |
| Where the money goes | [[sankey]] (cash deployment) |
| What it owns and owes | [[sankey]] (balance sheet) · [[balance-sheet]] · [[composite-score]] |
| Per share | [[roll-forward]] · [[metric-trend]] |
| How it evolved | [[metric-trend]] ×2 · [[stacked-area]] · [[stacked-normalized]] · [[bridge]] |
| How it compares | [[peer-comparison]] |
| Reading | [[callout]] |

### As-of discipline — the failure that embarrasses

Every figure in a profile is stale by construction: a filing describes a period
that has already ended. **State the report date**, and measure everything
against it. Four dates matter and are routinely collapsed into one:

| date | why it is different |
|---|---|
| report date | today — the reference for every other date |
| period end | what the numbers describe |
| filing date | when they became public; weeks after the period end |
| price date | a market price is not a filing date |

The trap is the gap between the last *audited year* and the last *reported
quarter*. A profile built on the annual report alone can be two quarters — and
a double-digit percentage — behind the business. Put trailing-twelve-month
figures in the Snapshot and say plainly which exhibits use the fiscal year and
why.

**Never mix periods inside one exhibit.** Where an annual disclosure has no
quarterly equivalent — product-line revenue is the common one — keep that
exhibit on the fiscal year and label it, rather than splicing.

### Per share is not optional

The section most profiles omit, and the one that explains shareholder returns.
A company can grow revenue slowly while growing revenue *per share* quickly by
retiring stock, and the totals never show it. Put [[roll-forward]] on the share
count next to the per-share record, and the gap between the two growth rates
is the buyback, quantified.

### Derived figures must show their working

[[composite-score]] takes the inputs, the coefficients and the contributions —
not just the result. A score whose workings are hidden is an opinion wearing a
decimal point, and a reader cannot check it against the balance sheet above.
Compute it from the figures the document already states rather than quoting a
provider's number you cannot reproduce.

### Peers are chosen, not screened

A peer list from an API is not a peer group — it will return companies that
share a keyword, not a business. Name the set, say why those names, and state
each one's fiscal year end: they rarely align, and a six-month offset means the
rows span different macro conditions.

`peer_comparison` emits the **Company** column itself. `headers` lists only the
metric columns; passing "Company" again shifts every value one column left and
leaves the last blank — a perfectly tidy wrong table.

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

### The third sankey — a stock, not a flow

The balance-sheet sankey puts assets on the left, `Total assets` in the middle
and the claims on the right, and the four roles fit it better than they fit
anything else here: a liability really is a claim that will consume value
(`cost`), and equity really is the residual left for owners (`retained`). It
answers in one look the question the table answers with arithmetic — **how much
of what it owns does the company actually own?**

**But a balance sheet is a stock.** Nothing moves along those ribbons. The roles
encode direction and there is no direction; the diagram shows composition and
claim. Say so in the `note`, because a reader who has just read two flow
sankeys above will otherwise read movement into this one.

Feed it from the same figures as the [[balance-sheet]] table. If the picture and
the table are built from separate literals they will eventually disagree, and
the one that is wrong will be whichever the reader trusts.

### Totals before shares

[[stacked-area]] then [[stacked-normalized]], in that order. The first shows the
business getting bigger and which band did it; the second shows only the mix. A
reader who sees composition shift before seeing the total move cannot tell
growth from substitution.

In a stacked area only the **bottom band and the top edge** are readable by eye
— the middle bands are not. That is why the normalised chart follows it rather
than replacing it, and it is worth saying in the `note` so nobody tries to read
a middle band off the wrong chart.

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
| a maturity wall | [[debt-maturity]] — needs a maturity schedule, which a data feed rarely carries |
| the cash conversion cycle | [[working-capital]] |
| why returns are what they are | [[dupont]] |
| subscription or vintage economics | [[cohort-table]], [[unit-economics]] |
| the market's view over the same window | [[price-history]], [[drawdown-curve]] |
| accounting that needs flagging | [[footnote-disclosures]] |
| quarterly seasonality | [[metric-trend]] on quarters rather than years |

The full set is in `../../../components/domain-specific/investing/usage.md` and
`CATALOG.md`.

## The one thing to write first

The **`note` under each sankey**. The diagram shows the shape; the sentence says
what it means. Write those two sentences before filling any table — if you
cannot say what the shape of the earnings and the shape of the spending tell
you, the numbers underneath will not say it for you.
