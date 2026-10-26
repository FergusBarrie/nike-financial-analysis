# Financial Performance Analysis — NIKE, Inc.

Seven financial years of NIKE's reported results, analysed in Excel, with a simple
three-scenario forecast built from stated assumptions.

**Business question:** NIKE's revenue peaked in FY2024 and has fallen since. How much of
the drop in profit is explained by lower sales, and how much by margins and costs?

| | |
|---|---|
| **Tools** | Excel (formula-driven model), Python (pandas, to extract the filings) |
| **Data** | NIKE 10-K filings via the [SEC XBRL company facts API](https://data.sec.gov/api/xbrl/companyfacts/CIK0000320187.json) — free, no API key |
| **Period** | FY2020 to FY2026 (NIKE's financial year ends 31 May) |
| **Company** | NIKE, Inc. (NYSE: NKE), CIK 0000320187 |

This is not a valuation and not an investment recommendation. It is a performance analysis
and a sensitivity exercise.

---

## The income statement, as reported

USD millions. Only these figures are typed into the workbook; everything else is a formula.

| | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 |
|---|---|---|---|---|---|---|---|
| Revenue | 37,403 | 44,538 | 46,710 | 51,217 | **51,362** | 46,309 | 46,398 |
| Gross profit | 16,241 | 19,962 | 21,479 | 22,292 | 22,887 | 19,790 | 19,911 |
| Gross margin | 43.4% | 44.8% | **46.0%** | 43.5% | 44.6% | 42.7% | 42.9% |
| SG&A | 13,126 | 13,025 | 14,804 | 16,377 | 16,576 | 16,088 | 16,114 |
| SG&A % of revenue | 35.1% | **29.2%** | 31.7% | 32.0% | 32.3% | 34.7% | 34.7% |
| Operating income | 3,115 | 6,937 | 6,675 | 5,915 | 6,311 | 3,702 | 3,797 |
| Operating margin | 8.3% | **15.6%** | 14.3% | 11.6% | 12.3% | 8.0% | 8.2% |
| Net income | 2,539 | 5,727 | **6,046** | 5,070 | 5,700 | 3,219 | 3,108 |
| Diluted EPS | $1.60 | $3.56 | $3.75 | $3.23 | $3.73 | $2.16 | $2.10 |

NIKE does not publish an operating income line — its income statement runs from gross
profit straight to SG&A and then to pre-tax income. Operating income above is gross profit
less SG&A. Four reconciliation checks on the extracted data all come to exactly zero; see
`outputs/extraction_log.txt`.

## What I found

1. **Profit fell about four times as fast as revenue.** Between FY2024 and FY2026 revenue
   fell 9.7%, but operating income fell 39.8%, net income 45.5% and EPS 43.2%. This is
   operating leverage: most of NIKE's cost base does not shrink when sales do.

2. **Almost all of the profit decline is a revenue problem, not a cost problem.** Splitting
   the $2,514m fall in operating income into three parts:

   | Cause | Effect on operating income |
   |---|---|
   | Lower revenue (at the FY2024 gross margin) | **−$2,212m** |
   | Lower gross margin (44.6% → 42.9%) | **−$764m** |
   | Lower SG&A | **+$462m** |
   | **Total** | **−$2,514m** |

   Lower revenue accounts for 88% of the fall. The three effects add back to the reported
   change exactly, which the workbook checks in a visible cell.

3. **The cost base did not follow revenue down.** SG&A fell only 2.8% while revenue fell
   9.7%, so SG&A rose from 32.3% to 34.7% of revenue. Inside that total the two halves moved
   in opposite directions: marketing (which NIKE calls demand creation) rose 10.9% in cash
   terms, from 8.3% to 10.3% of revenue, while operating overhead fell 7.6%. The company
   cut back-office cost and spent more on marketing while sales were falling.

4. **Cash generation weakened more than profit.** Free cash flow fell from $6,617m in
   FY2024 to $2,184m in FY2026, a 67% drop. Receivables rose $1,504m even though revenue
   fell, taking collection from 31.5 days to 46.7 days, and inventory held flat at about
   $7.5bn on lower sales. Both tie up cash.

5. **The balance sheet absorbed it comfortably.** Long-term debt came down $1,961m, equity
   rose to $14,865m, and the current ratio is still 1.96. Return on equity nearly halved,
   from 40.1% to 22.1% — but that is a profitability story, not a solvency one.

## Forecast

A deliberately simple two-year forecast. Three scenarios, each driven by four assumptions,
all of which sit in shaded cells on the Forecast sheet next to what the last seven years
actually did.

| Scenario | Revenue growth | Gross margin | SG&A growth | FY2028 operating margin | FY2028 EPS |
|---|---|---|---|---|---|
| Low | −2% | 42.0% | +1% | 5.1% | $1.31 |
| Base | +2% | 43.5% | +2% | 8.8% | $2.41 |
| High | +5% | 44.5% | +2% | 11.7% | $3.40 |

*FY2026 actual: operating margin 8.2%, EPS $2.10.*

The useful thing this shows is how far away the old profitability is. Even the High case —
5% revenue growth every year **and** the gross margin back at its FY2024 level — produces
an 11.7% operating margin in FY2028, still below the 12.3% of FY2024 and well below the
15.6% of FY2021. Getting back there needs the cost base to come down as well, not just
sales to recover.

## What I would watch

1. **Gross margin, as closely as revenue.** At current revenue, one percentage point of
   gross margin is worth about $464m of operating profit — roughly 12% of FY2026 operating
   income. Margin is the faster lever.

2. **Whether SG&A comes down.** At 34.7% of revenue the cost base is sized for a larger
   company. If revenue stays near $46bn, holding SG&A flat is not enough to rebuild the
   margin; the Base case above assumes SG&A grows with revenue and still only reaches 8.8%.

3. **Working capital.** Receivable days rising by 15 days and inventory staying flat on
   lower sales are the two clearest signs of pressure in these statements. They explain
   much of why free cash flow fell further than profit.

## Limitations

- **I did not extract segment or geographic detail.** It exists in the filings but is
  tagged with dimensions I did not pull, so I cannot say *where* the revenue decline came
  from — which region, which brand, wholesale or direct. That is the first thing I would
  add, and it is the biggest gap in this analysis.
- **Operating income is derived, not reported.** It is gross profit less SG&A. Anyone
  comparing with a published figure should check the definition matches.
- **One-off items are not separated out.** FY2024 included $443m of restructuring charges,
  so the FY2024 starting point in the bridge is already depressed and the underlying
  decline is slightly larger than the reported one. Asset impairments in FY2025 and FY2026
  were small ($33m and $50m).
- **The forecast is a sensitivity exercise, not a prediction.** The assumptions are mine.
  There is no DCF, no cost of capital, no target price, and nothing here about whether the
  shares are cheap.
- **Annual data only, and only seven years.** No quarterly detail, no competitor
  comparison, no market share data.
- **No explanation of causes.** Financial statements show what happened. They do not say
  why demand fell, and I have not used any source other than the filings.

---

## How to reproduce this

```bash
pip install pandas xlsxwriter

python scripts/00_download_data.py        # fetch the SEC company facts JSON (~3 MB)
python scripts/01_extract_financials.py   # pull the line items, run the reconciliation checks
python scripts/02_analyse_and_forecast.py # margin bridge and three-scenario forecast
python scripts/03_build_excel_model.py    # build the Excel workbook
python scripts/04_export_for_website.py   # JSON for the portfolio site
```

Before running step 1, put your own contact address in the `USER_AGENT` line of
`scripts/00_download_data.py`. The SEC asks for it in its
[fair access policy](https://www.sec.gov/os/webmaster-faq#developers) and may block
requests without one.

## What is in this repository

```
data/raw/        nike_companyfacts.json (not committed - run 00_download_data.py)
data/clean/      nike_financials.csv (as reported) and nike_ratios.csv (derived)
scripts/         00 download, 01 extract, 02 analyse, 03 Excel, 04 website export
outputs/tables/  margin_bridge.csv, forecast.csv, assumption_basis.csv
outputs/         extraction_log.txt (including the four reconciliation checks)
excel/           nike_financial_analysis.xlsx
FINDINGS.md      the full write-up
LEARNING_GUIDE.md  how every figure and formula works, with exercises
```

## About the Excel workbook

`excel/nike_financial_analysis.xlsx` has seven sheets. The thing worth knowing is that it
is live: the only hard-coded numbers are the figures NIKE reported and the forecast
assumptions. Margins, growth rates, ratios, the margin bridge and the entire forecast are
Excel formulas, so changing an assumption updates everything downstream, charts included.

The Margin bridge sheet contains a visible check cell that should always read zero — the
three effects must add back to the reported change in operating income.

## Honest note on this project

I built this to learn how to read a set of filed accounts and turn them into an analysis.
The [learning guide](LEARNING_GUIDE.md) explains every calculation, including the sign
convention in the SEC data that I got wrong first time round and had to work out properly.
I am happy to walk through the workbook formula by formula.
