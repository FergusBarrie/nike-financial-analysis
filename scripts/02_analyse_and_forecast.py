"""
Two pieces of analysis on top of the extracted figures:

1.  A bridge that splits the fall in operating income between FY2024 and
    FY2026 into three causes: lower revenue, a lower gross margin, and the
    change in SG&A.

2.  A simple three-scenario forecast of FY2027 and FY2028, driven entirely by
    stated assumptions. This is not a valuation and not a DCF - it answers one
    question: if revenue and margins behave in a particular way, what happens
    to profit?

Input : data/clean/nike_financials.csv
Output: outputs/tables/margin_bridge.csv
        outputs/tables/forecast.csv
        outputs/tables/assumption_basis.csv

Usage: python scripts/02_analyse_and_forecast.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
TABLES = ROOT / "outputs" / "tables"

# ----------------------------------------------------------------- scenarios
#
# Every number in this block is an assumption, not a result. The basis for
# each one is printed by the script and recorded in assumption_basis.csv so it
# can be challenged. Non-operating income is held flat at the FY2026 level
# because it is small (about $103m against $3.8bn of operating income) and I
# have no basis for forecasting it.
#
SCENARIOS = {
    "Low": {
        "revenue_growth": -0.02,
        "gross_margin": 0.420,
        "sg_and_a_growth": 0.01,
        "tax_rate": 0.20,
        "share_count_change": -0.010,
        "description": "Revenue falls a further 2% a year and the gross margin slips to 42.0%. "
                       "SG&A is only trimmed by 1% a year.",
    },
    "Base": {
        "revenue_growth": 0.02,
        "gross_margin": 0.435,
        "sg_and_a_growth": 0.02,
        "tax_rate": 0.20,
        "share_count_change": -0.015,
        "description": "Revenue grows 2% a year, the gross margin recovers part of the way back to "
                       "43.5%, and SG&A grows in line with revenue.",
    },
    "High": {
        "revenue_growth": 0.05,
        "gross_margin": 0.445,
        "sg_and_a_growth": 0.02,
        "tax_rate": 0.20,
        "share_count_change": -0.015,
        "description": "Revenue grows 5% a year and the gross margin returns to the FY2024 level of "
                       "44.5%, while SG&A grows only 2%.",
    },
}

FORECAST_YEARS = [2027, 2028]


def margin_bridge(fin, start_year, end_year):
    """Split the change in operating income into revenue, margin and SG&A effects.

    The arithmetic is the standard three-part split:
      revenue effect = change in revenue x the OLD gross margin
      margin effect  = the NEW revenue x change in gross margin
      SG&A effect    = minus the change in SG&A
    The three add back to the actual change, which the script checks.
    """
    a, b = fin.loc[start_year], fin.loc[end_year]
    gm_a = a.gross_profit / a.revenue
    gm_b = b.gross_profit / b.revenue

    revenue_effect = (b.revenue - a.revenue) * gm_a
    margin_effect = b.revenue * (gm_b - gm_a)
    sga_effect = -(b.sg_and_a - a.sg_and_a)
    actual = b.operating_income - a.operating_income

    rows = [
        ("FY{} operating income".format(start_year), a.operating_income, ""),
        ("Lower revenue", revenue_effect,
         "revenue fell ${:,.0f}m, at the FY{} gross margin of {:.1%}".format(
             a.revenue - b.revenue, start_year, gm_a)),
        ("Lower gross margin", margin_effect,
         "gross margin went from {:.1%} to {:.1%} on FY{} revenue".format(gm_a, gm_b, end_year)),
        ("Change in SG&A", sga_effect,
         "SG&A went from ${:,.0f}m to ${:,.0f}m".format(a.sg_and_a, b.sg_and_a)),
        ("FY{} operating income".format(end_year), b.operating_income, ""),
    ]
    bridge = pd.DataFrame(rows, columns=["item", "usd_millions", "note"])
    check = revenue_effect + margin_effect + sga_effect - actual
    return bridge, actual, check


def build_forecast(fin):
    last = fin.index.max()
    base = fin.loc[last]
    non_operating = base.net_interest_income + base.other_income_net

    rows = []
    for name, a in SCENARIOS.items():
        revenue = base.revenue
        sga = base.sg_and_a
        shares = base.diluted_shares
        for year in FORECAST_YEARS:
            revenue = revenue * (1 + a["revenue_growth"])
            sga = sga * (1 + a["sg_and_a_growth"])
            shares = shares * (1 + a["share_count_change"])
            gross_profit = revenue * a["gross_margin"]
            operating_income = gross_profit - sga
            pre_tax = operating_income + non_operating
            net_income = pre_tax * (1 - a["tax_rate"])
            rows.append({
                "scenario": name,
                "fiscal_year": year,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "gross_margin_pct": a["gross_margin"] * 100,
                "sg_and_a": sga,
                "sg_and_a_pct_of_revenue": sga / revenue * 100,
                "operating_income": operating_income,
                "operating_margin_pct": operating_income / revenue * 100,
                "pre_tax_income": pre_tax,
                "net_income": net_income,
                "net_margin_pct": net_income / revenue * 100,
                "diluted_shares": shares,
                "eps_diluted": net_income / shares,
            })
    return pd.DataFrame(rows), non_operating


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    fin = pd.read_csv(CLEAN / "nike_financials.csv", index_col="fiscal_year")

    # ------------------------------------------------------------- bridge
    bridge, actual, check = margin_bridge(fin, 2024, 2026)
    bridge.round(1).to_csv(TABLES / "margin_bridge.csv", index=False)
    print("Operating income bridge, FY2024 to FY2026 (USD millions)")
    print("-" * 78)
    print(bridge.round(0).to_string(index=False))
    print()
    print("Actual change: {:,.0f}m. The three effects add to within {:,.1f}m of that.".format(
        actual, abs(check)))
    print()

    # ---------------------------------------------- basis for the assumptions
    growth = fin.revenue.pct_change().dropna() * 100
    gm = (fin.gross_profit / fin.revenue * 100)
    sga_growth = fin.sg_and_a.pct_change().dropna() * 100
    tax = (fin.income_tax_expense / fin.pre_tax_income * 100)
    share_change = fin.diluted_shares.pct_change().dropna() * 100

    basis = pd.DataFrame([
        ["Revenue growth %", growth.mean(), growth.min(), growth.max(), growth.iloc[-1]],
        ["Gross margin %", gm.mean(), gm.min(), gm.max(), gm.iloc[-1]],
        ["SG&A growth %", sga_growth.mean(), sga_growth.min(), sga_growth.max(), sga_growth.iloc[-1]],
        ["Effective tax rate %", tax.mean(), tax.min(), tax.max(), tax.iloc[-1]],
        ["Diluted share count change %", share_change.mean(), share_change.min(),
         share_change.max(), share_change.iloc[-1]],
    ], columns=["measure", "fy2020_26_average", "minimum", "maximum", "fy2026_actual"])
    basis.round(2).to_csv(TABLES / "assumption_basis.csv", index=False)
    print("What the last seven years actually did - the basis for my assumptions")
    print("-" * 78)
    print(basis.round(1).to_string(index=False))
    print()

    # ----------------------------------------------------------- forecast
    forecast, non_operating = build_forecast(fin)
    forecast.round(2).to_csv(TABLES / "forecast.csv", index=False)
    print("Forecast (USD millions except EPS). Non-operating income held flat at ${:,.0f}m.".format(
        non_operating))
    print("-" * 78)
    show = ["scenario", "fiscal_year", "revenue", "gross_margin_pct", "operating_income",
            "operating_margin_pct", "net_income", "net_margin_pct", "eps_diluted"]
    print(forecast[show].round(2).to_string(index=False))
    print()
    print("For reference, FY2026 actual: revenue ${:,.0f}m, operating income ${:,.0f}m "
          "({:.1f}% margin), net income ${:,.0f}m, EPS ${:.2f}".format(
              fin.loc[2026].revenue, fin.loc[2026].operating_income,
              fin.loc[2026].operating_income / fin.loc[2026].revenue * 100,
              fin.loc[2026].net_income, fin.loc[2026].eps_diluted))
    print()
    print("Wrote", TABLES / "margin_bridge.csv")
    print("Wrote", TABLES / "assumption_basis.csv")
    print("Wrote", TABLES / "forecast.csv")


if __name__ == "__main__":
    main()
