"""
Pull the line items I need out of the SEC company facts file and write them as
a tidy table, one row per fiscal year.

Input : data/raw/nike_companyfacts.json
Output: data/clean/nike_financials.csv   (the reported figures, USD millions)
        data/clean/nike_ratios.csv       (margins, growth rates and ratios)
        outputs/extraction_log.txt

Two things about the SEC data that are easy to get wrong, and that I handle
explicitly below:

1.  The 'fy' field on each fact is the fiscal year of the FILING, not of the
    figure. A 10-K reports three years of income statement, so three facts can
    all carry fy=2026. I therefore work out the fiscal year from the fact's own
    'end' date instead. NIKE's financial year ends on 31 May, so a fact ending
    2026-05-31 belongs to fiscal 2026.

2.  The same fiscal year appears in several filings, sometimes with restated
    numbers. When that happens I keep the version from the most recently filed
    report, using the 'filed' date.

Usage: python scripts/01_extract_financials.py
"""

import json
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "nike_companyfacts.json"
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "outputs"

FIRST_YEAR, LAST_YEAR = 2020, 2026

# The figures I want, and the XBRL tag each one lives under.
# "duration" items cover a period (revenue, costs); "instant" items are a
# snapshot at the year end (balance sheet).
INCOME_STATEMENT = {
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "cost_of_sales": "CostOfGoodsAndServicesSold",
    "gross_profit": "GrossProfit",
    "sg_and_a": "SellingGeneralAndAdministrativeExpense",
    "demand_creation_expense": "MarketingAndAdvertisingExpense",
    "operating_overhead": "GeneralAndAdministrativeExpense",
    "net_interest_income": "InterestIncomeExpenseNonoperatingNet",
    "other_income_net": "OtherNonoperatingIncomeExpense",
    "pre_tax_income": "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    "income_tax_expense": "IncomeTaxExpenseBenefit",
    "net_income": "NetIncomeLoss",
}

CASH_FLOW = {
    "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
    "capital_expenditure": "PaymentsToAcquirePropertyPlantAndEquipment",
    "dividends_paid": "PaymentsOfDividendsCommonStock",
    "share_buybacks": "PaymentsForRepurchaseOfCommonStock",
}

BALANCE_SHEET = {
    "total_assets": "Assets",
    "current_assets": "AssetsCurrent",
    "current_liabilities": "LiabilitiesCurrent",
    "inventory": "InventoryFinishedGoodsNetOfReserves",
    "receivables": "AccountsReceivableNetCurrent",
    "cash_and_equivalents": "CashAndCashEquivalentsAtCarryingValue",
    "long_term_debt": "LongTermDebtNoncurrent",
    "shareholders_equity": "StockholdersEquity",
}

PER_SHARE = {
    "eps_diluted": ("EarningsPerShareDiluted", "USD/shares"),
    "diluted_shares": ("WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
}

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


def best_values(facts, tag, unit="USD", kind="duration"):
    """Return {fiscal_year: value} for one XBRL tag, taking the most recently
    filed version of each year."""
    if tag not in facts:
        log("  WARNING: tag not found: " + tag)
        return {}
    units = facts[tag]["units"]
    if unit not in units:
        log("  WARNING: unit {} not found for {} (has {})".format(unit, tag, list(units)))
        return {}

    chosen = {}
    for row in units[unit]:
        if row.get("form") not in ("10-K", "10-K/A"):
            continue
        end = date.fromisoformat(row["end"])
        if kind == "duration":
            if "start" not in row:
                continue
            days = (end - date.fromisoformat(row["start"])).days
            if not 330 <= days <= 400:        # keep full years, drop quarters
                continue
        else:
            if "start" in row:
                continue
        # NIKE's financial year ends on 31 May, so the fiscal year label is the
        # calendar year the period ends in.
        fiscal_year = end.year
        filed = row.get("filed", "")
        if fiscal_year not in chosen or filed > chosen[fiscal_year][1]:
            chosen[fiscal_year] = (row["val"], filed)
    return {year: value for year, (value, _) in chosen.items()}


def main():
    CLEAN.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    data = json.loads(RAW.read_text(encoding="utf-8"))
    facts = data["facts"]["us-gaap"]
    log("Company: {} (CIK {})".format(data["entityName"], data["cik"]))
    log("Fiscal years extracted: FY{} to FY{} (NIKE's year ends 31 May)".format(FIRST_YEAR, LAST_YEAR))
    log("")

    years = list(range(FIRST_YEAR, LAST_YEAR + 1))
    table = pd.DataFrame(index=years)
    table.index.name = "fiscal_year"

    log("Income statement")
    for name, tag in INCOME_STATEMENT.items():
        values = best_values(facts, tag, "USD", "duration")
        table[name] = pd.Series(values)
        log("  {:28s} {:6d} of {} years found".format(name, table[name].notna().sum(), len(years)))

    log("Cash flow")
    for name, tag in CASH_FLOW.items():
        table[name] = pd.Series(best_values(facts, tag, "USD", "duration"))
        log("  {:28s} {:6d} of {} years found".format(name, table[name].notna().sum(), len(years)))

    log("Balance sheet")
    for name, tag in BALANCE_SHEET.items():
        table[name] = pd.Series(best_values(facts, tag, "USD", "instant"))
        log("  {:28s} {:6d} of {} years found".format(name, table[name].notna().sum(), len(years)))

    log("Per share")
    for name, (tag, unit) in PER_SHARE.items():
        kind = "duration"
        table[name] = pd.Series(best_values(facts, tag, unit, kind))
        log("  {:28s} {:6d} of {} years found".format(name, table[name].notna().sum(), len(years)))

    table = table.loc[years]

    # Convert the dollar figures to millions so the tables are readable.
    # EPS stays in dollars and the share count stays in millions of shares.
    money_cols = [c for c in table.columns if c not in ("eps_diluted", "diluted_shares")]
    table[money_cols] = table[money_cols] / 1e6
    table["diluted_shares"] = table["diluted_shares"] / 1e6

    # NIKE does not report an operating income line in its income statement.
    # Its statement runs: revenue - cost of sales = gross profit, then minus
    # demand creation and operating overhead (together SG&A), then interest and
    # other income. So operating income = gross profit - SG&A, which is what
    # analysts call EBIT for this company.
    table["operating_income"] = table["gross_profit"] - table["sg_and_a"]

    log("")
    log("Checks")
    # Check 1: revenue - cost of sales should equal the reported gross profit.
    gap1 = (table["revenue"] - table["cost_of_sales"] - table["gross_profit"]).abs().max()
    log("  max difference, revenue - cost of sales vs reported gross profit: {:.1f}m".format(gap1))
    # Check 2: demand creation + operating overhead should equal reported SG&A.
    gap2 = (table["demand_creation_expense"] + table["operating_overhead"] - table["sg_and_a"]).abs().max()
    log("  max difference, demand creation + overhead vs reported SG&A:     {:.1f}m".format(gap2))
    # Check 3: operating income plus the two non-operating lines should equal
    # reported pre-tax income. Both tags are signed as income (a positive
    # value adds to profit), despite "expense" appearing in the tag names - I
    # worked that out by testing the bridge against the reported figure rather
    # than assuming.
    implied = (table["operating_income"] + table["net_interest_income"]
               + table["other_income_net"])
    gap3 = (implied - table["pre_tax_income"]).abs().max()
    log("  max difference, my operating income bridge vs reported pre-tax:  {:.1f}m".format(gap3))
    # Check 4: pre-tax income - tax should equal net income.
    gap4 = (table["pre_tax_income"] - table["income_tax_expense"] - table["net_income"]).abs().max()
    log("  max difference, pre-tax - tax vs reported net income:            {:.1f}m".format(gap4))
    log("  (anything under 1m is rounding in the filings)")

    # ---------------------------------------------------------------- ratios
    r = pd.DataFrame(index=table.index)
    r.index.name = "fiscal_year"

    r["revenue"] = table["revenue"]
    r["revenue_growth_pct"] = table["revenue"].pct_change() * 100
    r["gross_margin_pct"] = table["gross_profit"] / table["revenue"] * 100
    r["sg_and_a_pct_of_revenue"] = table["sg_and_a"] / table["revenue"] * 100
    r["demand_creation_pct_of_revenue"] = table["demand_creation_expense"] / table["revenue"] * 100
    r["overhead_pct_of_revenue"] = table["operating_overhead"] / table["revenue"] * 100
    r["operating_margin_pct"] = table["operating_income"] / table["revenue"] * 100
    r["net_margin_pct"] = table["net_income"] / table["revenue"] * 100
    r["effective_tax_rate_pct"] = table["income_tax_expense"] / table["pre_tax_income"] * 100

    r["gross_profit_growth_pct"] = table["gross_profit"].pct_change() * 100
    r["operating_income_growth_pct"] = table["operating_income"].pct_change() * 100
    r["net_income_growth_pct"] = table["net_income"].pct_change() * 100

    r["current_ratio"] = table["current_assets"] / table["current_liabilities"]
    # Inventory days: how many days of sales are sitting in the warehouse.
    r["inventory_days"] = table["inventory"] / table["cost_of_sales"] * 365
    r["receivable_days"] = table["receivables"] / table["revenue"] * 365
    # Return on equity uses AVERAGE equity, because net income is earned over
    # the year while equity is a year-end snapshot.
    avg_equity = (table["shareholders_equity"] + table["shareholders_equity"].shift(1)) / 2
    r["return_on_equity_pct"] = table["net_income"] / avg_equity * 100
    r["free_cash_flow"] = table["operating_cash_flow"] - table["capital_expenditure"]
    r["cash_returned_to_shareholders"] = table["dividends_paid"] + table["share_buybacks"]
    r["eps_diluted"] = table["eps_diluted"]

    table.round(1).to_csv(CLEAN / "nike_financials.csv")
    r.round(2).to_csv(CLEAN / "nike_ratios.csv")

    log("")
    log("Reported figures (USD millions)")
    cols = ["revenue", "cost_of_sales", "gross_profit", "demand_creation_expense",
            "operating_overhead", "sg_and_a", "operating_income",
            "net_interest_income", "other_income_net", "pre_tax_income",
            "income_tax_expense", "net_income", "eps_diluted"]
    with pd.option_context("display.width", 220, "display.max_columns", 30):
        log(table[cols].round(1).to_string())
        log("")
        log("Margins and ratios")
        log(r[["revenue_growth_pct", "gross_margin_pct", "sg_and_a_pct_of_revenue",
               "operating_margin_pct", "net_margin_pct", "effective_tax_rate_pct",
               "current_ratio", "inventory_days", "return_on_equity_pct",
               "free_cash_flow"]].round(2).to_string())

    log("")
    log("Wrote " + str(CLEAN / "nike_financials.csv"))
    log("Wrote " + str(CLEAN / "nike_ratios.csv"))
    (OUT / "extraction_log.txt").write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
