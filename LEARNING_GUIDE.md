# Learning guide — NIKE Financial Performance Analysis

This guide explains every figure, formula and judgement in the project, so I can talk
through it rather than just show it. Open `excel/nike_financial_analysis.xlsx` alongside it.

---

## 1. Where the data comes from, and why that matters

The figures are not from a data provider or a stock website. They come from NIKE's own
10-K filings, read through the SEC's **XBRL company facts API**:

```
https://data.sec.gov/api/xbrl/companyfacts/CIK0000320187.json
```

Every US-listed company tags its financial statements in XBRL, and the SEC publishes those
tags. The endpoint is free, needs no key, and returns everything the company has ever
tagged. The only requirement is a `User-Agent` header with a contact address.

**Why it is worth using:** the numbers are exactly as filed, so they can be checked against
the PDF of the 10-K. No vendor adjustments, no "normalised" figures.

**Be able to say:** "The data is from the SEC's XBRL API, which publishes every figure a
company tags in its filings. CIK is the SEC's company identifier — NIKE's is 320187."

---

## 2. Two traps in the SEC data, and how I handled them

These are the two things most likely to be asked about, because they are where it is easy
to produce wrong numbers without noticing.

### Trap 1 — the `fy` field is the year of the *filing*, not of the figure

A 10-K reports three years of income statement. All three facts carry `fy` equal to the
filing's fiscal year. So if you build a table keyed on `fy`, FY2024 and FY2023 figures can
end up labelled 2026.

**What I do instead** (`scripts/01_extract_financials.py`):

```python
end = date.fromisoformat(row["end"])
fiscal_year = end.year          # NIKE's year ends 31 May, so the label is the end year
```

I derive the fiscal year from the fact's own `end` date. NIKE's financial year ends on
31 May, so a period ending 2026-05-31 is fiscal 2026.

I also filter on period length, to keep annual figures and drop quarters:

```python
if not 330 <= (end - date.fromisoformat(row["start"])).days <= 400:
    continue
```

### Trap 2 — the same year appears in several filings, sometimes restated

FY2024 revenue appears in the FY2024, FY2025 and FY2026 10-Ks. If a figure was restated,
the versions differ. I keep the most recently filed one:

```python
if fiscal_year not in chosen or filed > chosen[fiscal_year][1]:
    chosen[fiscal_year] = (row["val"], filed)
```

### The sign convention I got wrong first time

This is worth telling honestly, because working it out is the useful part.

The two non-operating lines are tagged `InterestIncomeExpenseNonoperatingNet` and
`OtherNonoperatingIncomeExpense`. Both have "expense" in the name, so my first version
**subtracted** them. The bridge to reported pre-tax income was then out by up to $524m, and
the error changed sign between years — which is the clue that a sign convention is wrong
rather than a figure being missing.

I tested the three possibilities against the reported pre-tax figure and found:

```
operating income + net interest income + other income = pre-tax income
```

reconciles to **exactly zero in all seven years**. So both tags are signed as income: a
positive value adds to profit, despite the tag names.

**The lesson, and the thing to say in an interview:** never assume a sign convention.
Reconcile against a figure the company reports. If the difference flips between positive
and negative across years, it is a sign problem, not a data problem.

### The four checks

`scripts/01_extract_financials.py` runs these every time and prints the result to
`outputs/extraction_log.txt`. All four come to 0.0m:

| Check | What it proves |
|---|---|
| revenue − cost of sales = reported gross profit | I picked the right revenue and COGS tags |
| demand creation + operating overhead = reported SG&A | The SG&A split is complete |
| operating income + interest + other = reported pre-tax income | My derived operating income is right, and signs are right |
| pre-tax income − tax = reported net income | The tax line is the right one |

**Be able to say:** "I don't trust an extraction until it reconciles to a figure the
company reports. Four checks, all zero."

---

## 3. Operating income — a figure NIKE does not report

NIKE's income statement is:

```
Revenue
less  Cost of sales
=     Gross profit
less  Demand creation expense       (marketing)
less  Operating overhead expense    (everything else)
=     (together: Total SG&A)
plus  Interest income (expense), net
plus  Other income (expense), net
=     Income before income taxes
```

There is no operating income line. So:

```
operating income = gross profit − SG&A
```

This is what is normally called **EBIT** for this company. The formula sits in a visible
cell in the Income statement sheet (row 11), not buried in a script.

**Be able to say:** "NIKE doesn't report operating income, so I calculated it as gross
profit less SG&A. Anyone comparing my figure with a published one should check the
definition matches — some sources include or exclude different items."

---

## 4. Every ratio, and what it actually means

All of these are formulas on the Ratios sheet, pointing at the Income statement and
Balance sheet tabs. Nothing on that sheet is typed in.

| Ratio | Formula | What it tells you |
|---|---|---|
| Gross margin | gross profit ÷ revenue | What is left after making the product. Driven by pricing, discounting, input costs and currency. |
| Operating margin | operating income ÷ revenue | Profitability after running the business, before financing and tax. |
| Net margin | net income ÷ revenue | What shareholders are left with. |
| SG&A % of revenue | SG&A ÷ revenue | How heavy the cost base is relative to sales. The key number in this project. |
| Effective tax rate | tax expense ÷ pre-tax income | The rate actually paid, not the statutory rate. |
| Current ratio | current assets ÷ current liabilities | Short-term liquidity. Above 1 means current assets cover current bills. |
| Inventory days | inventory ÷ cost of sales × 365 | How many days of sales sit in the warehouse. Rising means stock is building. |
| Receivable days | receivables ÷ revenue × 365 | How long customers take to pay. Rising ties up cash. |
| Long-term debt to equity | long-term debt ÷ equity | How much of the business is funded by borrowing. |
| Return on equity | net income ÷ **average** equity | Profit per pound of shareholder money. |
| Free cash flow | operating cash flow − capital expenditure | Cash left after keeping the business running. |

### Why return on equity uses *average* equity

Net income is earned across the whole year. Equity is a snapshot at one date. Dividing a
full-year flow by a single-day balance mismatches the two, so the standard treatment is the
average of opening and closing equity:

```excel
='Income statement'!H16/AVERAGE('Balance sheet'!G12,'Balance sheet'!H12)
```

FY2020 shows `n/a` because there is no FY2019 opening balance in my extract. Saying `n/a`
is better than quietly using the closing balance and producing a number that is not
comparable with the others.

**Be able to say:** "Average equity, because income is a flow and equity is a stock. The
first year has no opening balance, so it's n/a."

### Why inventory days uses cost of sales, not revenue

Inventory is held at cost, so the denominator should also be at cost. Using revenue would
understate the days because revenue includes the margin.

---

## 5. The margin bridge — the heart of the analysis

Saying "profit fell because sales fell" is not an analysis. The bridge quantifies it.

The question: operating income went from $6,311m in FY2024 to $3,797m in FY2026, a fall of
$2,514m. How much of that is lower sales, how much is a thinner margin, and how much did
cost savings offset?

### The arithmetic

```
revenue effect = (new revenue − old revenue) × OLD gross margin
margin effect  = NEW revenue × (new gross margin − old gross margin)
SG&A effect    = −(new SG&A − old SG&A)
```

Worked through:

| Cause | Calculation | Effect |
|---|---|---|
| Lower revenue | (46,398 − 51,362) × 44.56% | **−$2,212m** |
| Lower gross margin | 46,398 × (42.91% − 44.56%) | **−$764m** |
| Lower SG&A | −(16,114 − 16,576) | **+$462m** |
| | | **−$2,514m** |

And −2,212 − 764 + 462 = −2,514, which is exactly the reported change.

### Why the old margin and the new revenue, and not the other way round

This is the question to expect, and the answer is about avoiding double counting.

The revenue effect asks: *if the margin had stayed the same, what would the lower revenue
alone have cost?* So it uses the **old** margin.

The margin effect asks: *given the revenue we actually have, what did the thinner margin
cost?* So it uses the **new** revenue.

Taken together they cover the change exactly once. If you used the old margin *and* the old
revenue for both, the interaction between them — the bit where lower revenue and a lower
margin compound — would go missing, and the three parts would not add up. The workbook
makes the check visible in cell B12 of the Margin bridge sheet, which should always read
zero.

**You could also split it the other way** (new margin for the revenue effect, old revenue
for the margin effect) and it would also add up — the interaction term just lands in the
other bucket. Being able to say that shows you understand what the decomposition is doing
rather than having memorised a formula.

### What it tells us

88% of the profit decline is lower revenue. That reframes the problem: this is a demand
problem first, a margin problem second, and the cost savings barely moved the needle.

---

## 6. Reading the SG&A split

This is the finding I would lead with, because it is not visible in the headline numbers.

| | FY2024 | FY2026 | Change |
|---|---|---|---|
| Demand creation (marketing) | $4,285m | $4,754m | **+10.9%** |
| Operating overhead | $12,291m | $11,360m | −7.6% |
| Total SG&A | $16,576m | $16,114m | −2.8% |
| Revenue | $51,362m | $46,398m | −9.7% |

The total barely moved, but the two halves moved in opposite directions. NIKE cut back-office
cost and *increased* marketing spend while revenue was falling — marketing went from 8.3%
to 10.3% of revenue.

**How to talk about it:** this looks like a deliberate choice to spend into a downturn to
defend demand, rather than a failure to control costs. Whether it works would show up in
future revenue, which I cannot see. The honest version is to describe the choice and say
what you would look for next, not to call it right or wrong.

**The lesson:** always look inside an aggregate before concluding anything about it. "SG&A
fell 2.8%" is true and almost completely uninformative.

---

## 7. The forecast — what it is and is not

### How it works

Four assumptions per scenario, in shaded cells on the Forecast sheet:

| Assumption | Low | Base | High | FY2020–26 history |
|---|---|---|---|---|
| Revenue growth | −2% | +2% | +5% | average +4.0%, range −9.8% to +19.1% |
| Gross margin | 42.0% | 43.5% | 44.5% | average 44.0%, range 42.7% to 46.0% |
| SG&A growth | +1% | +2% | +2% | average +3.7%, range −2.9% to +13.7% |
| Tax rate | 20% | 20% | 20% | average 15.1%, FY2026 20.3% |
| Share count change | −1.0% | −1.5% | −1.5% | average −1.2% |

Each assumption sits next to what actually happened over the last seven years. That is
deliberate — it is how you tell whether an assumption is reasonable or wishful.

The mechanics, two years forward:

```
revenue       = prior year revenue × (1 + growth)
gross profit  = revenue × gross margin assumption
SG&A          = prior year SG&A × (1 + SG&A growth)
operating income = gross profit − SG&A
pre-tax       = operating income + non-operating income (held flat)
net income    = pre-tax × (1 − tax rate)
shares        = prior year shares × (1 + share count change)
EPS           = net income ÷ shares
```

Non-operating income is held flat at the FY2026 level of $103m, because it is small next to
$3.8bn of operating income and I have no basis for forecasting it. Saying that out loud is
better than hiding a guess.

### Why the tax rate is 20% and not the 15.1% average

NIKE's effective rate has risen steadily and was 20.3% in FY2026. The seven-year average is
dragged down by FY2022's 9.1%. Using the most recent rate is more defensible than an
average across very different years — but it is still a judgement, and it should be stated
as one.

### Why it is deliberately simple

There is no DCF, no cost of capital, no terminal value and no target price. Those tools
answer "what is the company worth", which is a different question and needs assumptions I
have no basis for. This forecast answers "under stated assumptions about revenue and
margin, what happens to profit" — which is the question a junior analyst in an FP&A team
actually gets asked.

### The most useful thing it shows

Even the High case — 5% growth every year *and* the gross margin back at FY2024 levels —
reaches only an 11.7% operating margin in FY2028, below FY2024's 12.3% and well short of
FY2021's 15.6%. Because SG&A keeps growing at 2% in that scenario, revenue recovery alone
cannot rebuild the old margin. That conclusion comes out of the model rather than being
asserted, which is the point of building one.

---

## 8. Why each chart exists

| Chart | Question it answers |
|---|---|
| Revenue columns with operating margin on a second axis | Did margin fall with revenue, or independently? Two axes because the units differ; the shape shows margin falling further than revenue. |
| Three margin lines (gross, operating, net) | Where in the income statement is the pressure? The gap between gross and operating margin is the cost story. |
| Stacked SG&A as % of revenue | Split into marketing and overhead — the chart that shows marketing rising while overhead fell. |
| Margin bridge columns | The three causes, sized. Three bars replace a paragraph. |
| Free cash flow vs cash returned to shareholders | Is the company paying out more than it generates? In FY2026, yes — 117% of free cash flow. |

I did not build a waterfall chart for the bridge. Excel's native waterfall needs a
different data layout, and a plain column chart of the three effects says the same thing
without extra machinery.

---

## 9. Likely interview questions

**"Walk me through what happened to NIKE."**
Revenue peaked at $51.4bn in FY2024, fell 9.7% to $46.4bn by FY2026, and FY2026 was flat —
the decline stopped but did not reverse. Profit fell much further: operating income down
39.8%, EPS down 43.2%. That gap is operating leverage.

**"Where did the profit go?"**
$2,212m from lower revenue, $764m from a 1.65 point fall in gross margin, offset by $462m
of SG&A savings. The three add to the reported $2,514m exactly.

**"What is operating leverage?"**
Fixed and semi-fixed costs do not fall when revenue does, so profit moves by more than
revenue in percentage terms. Here revenue fell 9.7% and SG&A fell only 2.8%.

**"How did you calculate operating margin?"**
Operating income ÷ revenue, where operating income is gross profit less SG&A, because NIKE
does not report an operating income line.

**"How confident are you in these numbers?"**
They are as filed, and four reconciliations against NIKE's own reported subtotals come to
zero. The analysis on top is mine, and its biggest gap is that I did not extract segment
detail, so I cannot say which region or channel drove the decline.

**"Is the stock a buy?"**
That is not what this analysis does. It has no valuation, no cost of capital and no view on
the share price. What I can say is what happened to margins and cash, and what would have
to change for profitability to recover.

**"Your forecast shows EPS recovering to $2.41 in the Base case. Why should I believe it?"**
You shouldn't believe it as a prediction. It says: *if* revenue grows 2% a year *and* the
gross margin recovers to 43.5% *and* SG&A grows 2%, then EPS is $2.41. Every one of those
is in a shaded cell next to what the last seven years actually did. The purpose is to size
the sensitivity, not to call the outcome.

**"What would you do next?"**
Pull the segment and geographic breakdowns to find where revenue fell, and look at the
inventory and receivables detail to understand the working capital movement.

**"Why did free cash flow fall further than profit?"**
Working capital. Receivables rose $1,504m despite lower revenue, taking collection from
31.5 to 46.7 days, and inventory stayed flat at about $7.5bn on lower sales. Both consume
cash that never reaches free cash flow.

---

## 10. Exercises

### Reading the data

1. Open `data/clean/nike_financials.csv` and confirm by hand that FY2026 revenue less cost
   of sales equals the reported gross profit.
2. In `outputs/extraction_log.txt`, find the four checks. Change one tag name in
   `INCOME_STATEMENT` in `scripts/01_extract_financials.py` to something wrong, re-run it,
   and watch a check fail. Change it back.
3. Look up NIKE's FY2026 10-K on [EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320187&type=10-K)
   and check three figures in the table against the filed statement.

### Excel

4. On the Forecast sheet, change the Base case revenue growth from 2% to 0%. What happens
   to FY2028 EPS, and why does operating margin fall even though the gross margin
   assumption has not changed?
5. Change the Base case gross margin to 44.56% (the FY2024 level), leaving everything else.
   How much of the gap back to FY2024's operating margin does that close? What does the
   rest tell you?
6. Add a fourth scenario of your own. You will need a new assumption column and a new
   scenario block — copy the Base block and repoint the `$C$` references to `$E$`.
7. Add a row to the Ratios sheet for gross profit per diluted share.
8. Build the margin bridge for FY2021 → FY2024 instead (the growth years). Which effect
   dominates when the business is growing?

### Analysis

9. Marketing spend rose 10.9% while revenue fell 9.7%. Write three sentences on what you
   would need to see to judge whether that was the right call.
10. Calculate NIKE's cash conversion: free cash flow ÷ net income, each year. Which years
    look unusual, and can you explain them from the balance sheet?
11. Repeat the whole analysis for a different company. Change `CIK` in
    `scripts/00_download_data.py` — Adidas is not SEC-registered, so try Lululemon
    (CIK 0001397187) or Under Armour (CIK 0001336917). Expect some tag names to differ:
    not every company uses `MarketingAndAdvertisingExpense`. Working out which tags a
    different company uses is the real exercise.

---

## 11. Things I would do differently next time

- **Reconcile before analysing.** I built the first version of the bridge on numbers whose
  signs were wrong and had to redo it. The reconciliation checks should be the first thing
  written, not the last.
- **Extract the segment data from the start.** Not having it is the main limitation of the
  project, and it was a scoping decision I should have made differently.
- **Decide what the forecast is for before building it.** My first attempt drifted towards
  a valuation model, which was not the question.
