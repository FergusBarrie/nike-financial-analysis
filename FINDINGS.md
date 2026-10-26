# Findings — NIKE, Inc. financial performance, FY2020 to FY2026

**Business question:** NIKE's revenue peaked in FY2024 and has fallen since. How much of
the drop in profit is explained by lower sales, and how much by margins and costs?

All figures are as reported in NIKE's 10-K filings, read through the SEC's XBRL company
facts API. USD millions unless stated. NIKE's financial year ends 31 May, so FY2026 covers
June 2025 to May 2026.

---

## 1. What happened to the top line

Revenue recovered strongly from the COVID year, grew for four years, peaked in FY2024 and
then fell.

| | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---|---|---|---|---|---|---|
| Revenue | 37,403 | 44,538 | 46,710 | 51,217 | **51,362** | 46,309 | 46,398 |
| Growth | — | +19.1% | +4.9% | +9.7% | +0.3% | **−9.8%** | +0.2% |

Two things are worth separating. FY2025 was the fall: −9.8%, or $5.1bn of revenue. FY2026
was flat: +0.2%. So the decline stopped, but nothing has come back. FY2026 revenue is 9.7%
below the FY2024 peak.

---

## 2. Profit fell about four times as fast as revenue

| FY2024 → FY2026 | Change |
|---|---|
| Revenue | −9.7% |
| Gross profit | −13.0% |
| **Operating income** | **−39.8%** |
| **Net income** | **−45.5%** |
| Diluted EPS | −43.2% |

This is operating leverage. Most of NIKE's cost base — stores, staff, marketing
commitments, overhead — does not shrink when sales do, so a 9.7% revenue fall becomes a
39.8% profit fall. Operating margin went from 12.3% to 8.2%, and net margin from 11.1% to
6.7%.

For context, the best year in this period was FY2021, at a 15.6% operating margin. FY2026
is roughly half that.

---

## 3. Where the $2,514m of operating profit went

This is the central piece of analysis. Splitting the fall into its three causes:

| Cause | Calculation | Effect | Share |
|---|---|---|---|
| Lower revenue | (46,398 − 51,362) × 44.56% | **−2,212** | 88% |
| Lower gross margin | 46,398 × (42.91% − 44.56%) | **−764** | 30% |
| Lower SG&A | −(16,114 − 16,576) | **+462** | −18% |
| **Total** | | **−2,514** | 100% |

The three effects add back to the reported change exactly — the workbook shows the check in
a visible cell.

**Lower revenue explains 88% of it.** This is a demand problem first and a margin problem
second. Cost savings offset less than a fifth of the damage.

The gross margin part is not trivial either: 44.56% to 42.91%, a fall of 1.65 percentage
points. At FY2026 revenue, one percentage point of gross margin is worth about **$464m** of
operating profit — about 12% of FY2026 operating income. Margin is the faster lever of the
two.

---

## 4. The cost base did not follow revenue down — and the two halves moved opposite ways

| | FY2024 | FY2026 | Change |
|---|---|---|---|
| Demand creation expense (marketing) | 4,285 | 4,754 | **+10.9%** |
| Operating overhead expense | 12,291 | 11,360 | −7.6% |
| **Total SG&A** | 16,576 | 16,114 | **−2.8%** |
| Revenue | 51,362 | 46,398 | −9.7% |

SG&A as a share of revenue rose from **32.3% to 34.7%**. Marketing rose from 8.3% to 10.3%
of revenue while overhead stayed roughly flat as a share.

So NIKE cut back-office cost and increased marketing spend into a falling top line. That
reads as a deliberate decision to defend demand rather than a failure to control costs.
Whether it worked would show up in revenue after FY2026, which this data does not cover.

"SG&A fell 2.8%" is true and tells you almost nothing. The split is the finding.

---

## 5. Cash generation weakened more than profit

| | FY2024 | FY2025 | FY2026 |
|---|---|---|---|
| Cash from operating activities | 7,429 | 3,698 | 2,868 |
| Capital expenditure | 812 | 430 | 684 |
| **Free cash flow** | **6,617** | **3,268** | **2,184** |
| Cash returned to shareholders | 6,419 | 5,285 | 2,553 |
| Returned as % of free cash flow | 97% | 162% | **117%** |

Free cash flow fell 67% between FY2024 and FY2026 — considerably more than the 45.5% fall
in net income. Working capital explains most of the gap:

| | FY2024 | FY2026 |
|---|---|---|
| Accounts receivable | 4,427 | **5,931** |
| Receivable days | 31.5 | **46.7** |
| Inventories | 7,519 | 7,501 |
| Inventory days | 96 | 103 |

Receivables rose **$1,504m** while revenue *fell*, taking collection from 31.5 days to 46.7
days. Inventory held flat in cash terms on lower sales, so inventory days rose from 96 to
103. Both tie up cash that never reaches free cash flow.

NIKE also returned more to shareholders than it generated in free cash flow in FY2025 and
FY2026, funded from the existing cash pile. Buybacks were cut sharply in FY2026 — from
$2,985m to $146m — which looks like exactly that pressure being managed.

---

## 6. The balance sheet took it comfortably

| | FY2024 | FY2026 |
|---|---|---|
| Cash and equivalents | 9,860 | 7,563 |
| Current ratio | 2.40 | 1.96 |
| Long-term debt | 7,903 | **5,942** |
| Shareholders' equity | 14,430 | 14,865 |
| Return on equity | 40.1% | **22.1%** |

Long-term debt came down $1,961m, equity rose, and the current ratio is still comfortably
above 1. Return on equity nearly halved, but that reflects lower profit on a similar equity
base — it is a profitability story, not a solvency one. Nothing in these statements
suggests financial distress.

---

## 7. Forecast — what it would take to recover

Three scenarios, two years, four assumptions each. Every assumption is visible in the
workbook next to what the last seven years actually did.

| Scenario | Revenue growth | Gross margin | SG&A growth | FY2027 EPS | FY2028 op. margin | FY2028 EPS |
|---|---|---|---|---|---|---|
| Low | −2% | 42.0% | +1% | $1.60 | 5.1% | $1.31 |
| Base | +2% | 43.5% | +2% | $2.33 | 8.8% | $2.41 |
| High | +5% | 44.5% | +2% | $2.93 | 11.7% | $3.40 |

*FY2026 actual: operating margin 8.2%, EPS $2.10.*

The useful result is the High case. Five per cent revenue growth every year **and** a gross
margin all the way back to the FY2024 level still only produces an 11.7% operating margin —
below FY2024's 12.3% and well short of FY2021's 15.6%. The reason is in the assumptions:
SG&A keeps growing at 2%. Revenue recovery on its own does not rebuild the old margin; the
cost base has to come down too.

This is a sensitivity exercise, not a prediction. There is no valuation here.

---

## What I would watch

1. **Gross margin, as closely as revenue.** One percentage point is worth about $464m of
   operating profit at current revenue — roughly 12% of FY2026 operating income. It moves
   faster than the top line.

2. **Whether SG&A comes down.** At 34.7% of revenue the cost base is sized for a larger
   company. If revenue stays near $46bn, the forecast shows that holding SG&A flat is not
   enough to rebuild margin.

3. **Receivables and inventory.** Receivable days up 15 and inventory flat on lower sales
   are the clearest signs of pressure in these statements, and they explain why free cash
   flow fell further than profit. A reversal would release cash quickly; further
   deterioration would do the opposite.

## Limitations

1. **No segment or geographic detail.** It is in the filings but tagged with dimensions I
   did not extract, so I cannot say which region, brand or channel drove the decline. This
   is the biggest gap in the analysis and the first thing I would fix.
2. **Operating income is derived,** as gross profit less SG&A, because NIKE does not report
   it. Comparisons with published figures should check the definition.
3. **One-off items are not separated.** FY2024 included $443m of restructuring charges, so
   the FY2024 base is already depressed and the underlying decline is a little larger than
   the reported one. Asset impairments in FY2025 and FY2026 were small ($33m and $50m).
4. **Nothing here explains *why* demand fell.** Financial statements record outcomes. I
   have used no source other than the filings — no management commentary, no market data,
   no competitor figures.
5. **No valuation, no view on the shares.** No DCF, no cost of capital, no target price.
6. **Annual data, seven years, one company.** No quarterly detail and no peer comparison,
   so there is no way to tell from this work how much is NIKE-specific and how much is the
   sector.
