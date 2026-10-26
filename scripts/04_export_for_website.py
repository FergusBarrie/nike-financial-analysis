"""
Collect the results into one JSON file for the portfolio website, and print the
headline figures used in the written findings.

Output: outputs/website_data.json

Usage: python scripts/04_export_for_website.py
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
TABLES = ROOT / "outputs" / "tables"
OUT = ROOT / "outputs" / "website_data.json"


def json_safe(obj):
    """Replace NaN/NaT with None so the output is valid JSON.

    pandas writes missing numbers as NaN, which json.dumps happily emits as the
    bare token NaN - valid Python, invalid JSON, and the website build refuses
    to parse it. Walking the payload once at the end is the reliable fix.
    """
    import math
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_safe(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if obj is pd.NaT:
        return None
    return obj


def main():
    fin = pd.read_csv(CLEAN / "nike_financials.csv", index_col="fiscal_year")
    ratios = pd.read_csv(CLEAN / "nike_ratios.csv", index_col="fiscal_year")
    bridge = pd.read_csv(TABLES / "margin_bridge.csv")
    forecast = pd.read_csv(TABLES / "forecast.csv")
    basis = pd.read_csv(TABLES / "assumption_basis.csv")

    peak_year = int(fin.revenue.idxmax())
    last_year = int(fin.index.max())
    a, b = fin.loc[peak_year], fin.loc[last_year]

    def change(col):
        return round(float(b[col] / a[col] - 1) * 100, 1)

    headline = {
        "company": "NIKE, Inc.",
        "ticker": "NKE",
        "cik": "0000320187",
        "fiscal_year_end": "31 May",
        "years_covered": "FY{} to FY{}".format(int(fin.index.min()), last_year),
        "peak_revenue_year": peak_year,
        "peak_revenue": round(float(a.revenue), 1),
        "latest_revenue": round(float(b.revenue), 1),
        "revenue_change_from_peak_pct": change("revenue"),
        "latest_revenue_growth_pct": round(float(ratios.loc[last_year, "revenue_growth_pct"]), 1),
        "operating_income_change_from_peak_pct": change("operating_income"),
        "net_income_change_from_peak_pct": change("net_income"),
        "eps_change_from_peak_pct": change("eps_diluted"),
        "gross_margin_peak_pct": round(float(ratios.loc[peak_year, "gross_margin_pct"]), 1),
        "gross_margin_latest_pct": round(float(ratios.loc[last_year, "gross_margin_pct"]), 1),
        "operating_margin_peak_pct": round(float(ratios.loc[peak_year, "operating_margin_pct"]), 1),
        "operating_margin_latest_pct": round(float(ratios.loc[last_year, "operating_margin_pct"]), 1),
        "operating_margin_best_pct": round(float(ratios.operating_margin_pct.max()), 1),
        "operating_margin_best_year": int(ratios.operating_margin_pct.idxmax()),
        "sga_pct_peak": round(float(ratios.loc[peak_year, "sg_and_a_pct_of_revenue"]), 1),
        "sga_pct_latest": round(float(ratios.loc[last_year, "sg_and_a_pct_of_revenue"]), 1),
        "sga_change_pct": change("sg_and_a"),
        "demand_creation_change_pct": change("demand_creation_expense"),
        "overhead_change_pct": change("operating_overhead"),
        "free_cash_flow_peak": round(float(ratios.loc[peak_year, "free_cash_flow"]), 1),
        "free_cash_flow_latest": round(float(ratios.loc[last_year, "free_cash_flow"]), 1),
        "roe_peak_pct": round(float(ratios.loc[peak_year, "return_on_equity_pct"]), 1),
        "roe_latest_pct": round(float(ratios.loc[last_year, "return_on_equity_pct"]), 1),
        "current_ratio_latest": round(float(ratios.loc[last_year, "current_ratio"]), 2),
        "receivable_days_peak": round(float(ratios.loc[peak_year, "receivable_days"]), 1),
        "receivable_days_latest": round(float(ratios.loc[last_year, "receivable_days"]), 1),
        "receivables_increase": round(float(b.receivables - a.receivables), 1),
        "long_term_debt_change": round(float(b.long_term_debt - a.long_term_debt), 1),
        # One percentage point of gross margin, in dollars, at current revenue.
        "one_point_of_gross_margin": round(float(b.revenue) / 100, 1),
    }

    payload = {
        "meta": {
            "project": "Financial performance analysis - NIKE, Inc.",
            "source": "NIKE 10-K filings via the SEC XBRL company facts API",
            "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320187.json",
            "filings_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320187&type=10-K",
            "currency": "USD millions, except per-share amounts",
            "note": "Figures are as reported. NIKE does not publish an operating income line, "
                    "so operating income here is gross profit less SG&A.",
        },
        "headline": headline,
        "financials": fin.reset_index().round(1).to_dict(orient="records"),
        "ratios": ratios.reset_index().where(pd.notna(ratios.reset_index()), None)
                        .round(2).to_dict(orient="records"),
        "margin_bridge": bridge.round(1).to_dict(orient="records"),
        "forecast": forecast.round(2).to_dict(orient="records"),
        "assumption_basis": basis.round(2).to_dict(orient="records"),
    }
    OUT.write_text(json.dumps(json_safe(payload), indent=2, allow_nan=False),
                   encoding="utf-8")
    print("Wrote", OUT)
    print()
    print("Headline figures for the write-up")
    print("-" * 64)
    for key, value in headline.items():
        print("{:42s} {}".format(key, value))


if __name__ == "__main__":
    main()
