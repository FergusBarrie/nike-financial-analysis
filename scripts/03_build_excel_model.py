"""
Build the Excel workbook for the NIKE financial analysis.

Output: excel/nike_financial_analysis.xlsx

The point of this workbook is that it is live. Only the figures NIKE actually
reported are typed in as numbers. Everything else - margins, growth rates,
ratios, the margin bridge and the whole forecast - is an Excel formula. The
forecast is driven by a small block of assumptions in shaded cells: change
one and every downstream figure and chart updates.

Sheets
  Dashboard         headline figures and charts
  Read me           sources, method and what to be careful about
  Income statement  FY2020-FY2026 as reported, plus common-size and growth
  Balance sheet     balance sheet and cash flow items
  Ratios            margins, liquidity, efficiency and returns
  Margin bridge     why operating income fell between FY2024 and FY2026
  Forecast          three scenarios, formula-driven from the assumptions block

Usage: python scripts/03_build_excel_model.py
"""

from pathlib import Path

import pandas as pd
import xlsxwriter

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
TABLES = ROOT / "outputs" / "tables"
OUT = ROOT / "excel" / "nike_financial_analysis.xlsx"

NAVY = "#1F3353"
STEEL = "#2E4A72"
PALE = "#8FA6C4"
CLAY = "#C2703D"
INPUT_BG = "#FFF4E0"


def col_letter(idx):
    """0 -> A, 1 -> B, ..."""
    return xlsxwriter.utility.xl_col_to_name(idx)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    fin = pd.read_csv(CLEAN / "nike_financials.csv", index_col="fiscal_year")
    bridge = pd.read_csv(TABLES / "margin_bridge.csv")
    basis = pd.read_csv(TABLES / "assumption_basis.csv")
    years = list(fin.index)
    n = len(years)

    book = xlsxwriter.Workbook(OUT)

    # ---------------------------------------------------------------- formats
    f_title = book.add_format({"bold": True, "font_size": 15, "font_color": NAVY})
    f_h2 = book.add_format({"bold": True, "font_size": 11, "font_color": NAVY, "top": 1,
                            "top_color": PALE})
    f_note = book.add_format({"font_size": 9, "italic": True, "font_color": "#7A8899",
                              "text_wrap": True, "valign": "top"})
    f_body = book.add_format({"font_size": 10, "font_color": "#3C4B5C", "text_wrap": True,
                              "valign": "top"})
    f_bodyb = book.add_format({"font_size": 10, "bold": True, "font_color": NAVY})
    f_yr = book.add_format({"bold": True, "bg_color": NAVY, "font_color": "white",
                            "align": "center", "border": 1, "border_color": NAVY})
    f_lbl = book.add_format({"font_size": 10, "indent": 1})
    f_lbl_b = book.add_format({"font_size": 10, "bold": True, "font_color": NAVY})
    f_usd = book.add_format({"num_format": "#,##0", "font_size": 10})
    f_usd_b = book.add_format({"num_format": "#,##0", "bold": True, "font_size": 10,
                               "font_color": NAVY, "top": 1, "top_color": PALE})
    f_pct = book.add_format({"num_format": "0.0%", "font_size": 10})
    f_pct_b = book.add_format({"num_format": "0.0%", "bold": True, "font_size": 10,
                               "font_color": NAVY})
    f_x = book.add_format({"num_format": "0.00", "font_size": 10})
    f_days = book.add_format({"num_format": "0", "font_size": 10})
    f_eps = book.add_format({"num_format": "$0.00", "font_size": 10})
    f_input = book.add_format({"num_format": "0.0%", "font_size": 10, "bg_color": INPUT_BG,
                               "border": 1, "border_color": CLAY, "bold": True})
    f_input_usd = book.add_format({"num_format": "#,##0", "font_size": 10, "bg_color": INPUT_BG,
                                   "border": 1, "border_color": CLAY, "bold": True})
    f_kpi_l = book.add_format({"font_size": 10, "font_color": "#5A6B80"})
    f_kpi_v = book.add_format({"font_size": 18, "bold": True, "font_color": NAVY,
                               "num_format": "$#,##0"})
    f_kpi_p = book.add_format({"font_size": 18, "bold": True, "font_color": NAVY,
                               "num_format": "0.0%"})
    f_kpi_e = book.add_format({"font_size": 18, "bold": True, "font_color": NAVY,
                               "num_format": "$0.00"})

    # =====================================================================
    # Income statement
    # =====================================================================
    ist = book.add_worksheet("Income statement")
    ist.hide_gridlines(2)
    ist.set_column(0, 0, 36)
    ist.set_column(1, n, 12)
    ist.write(0, 0, "NIKE, Inc. - income statement as reported", f_title)
    ist.write(1, 0, "USD millions, except per-share amounts. Financial year ends 31 May. "
                    "Source: NIKE 10-K filings via the SEC XBRL company facts API. Only the "
                    "reported lines are typed in; operating income, pre-tax income, net income, "
                    "the common-size block and the growth block are formulas.", f_note)
    ist.set_row(1, 30)

    HEAD = 3                                  # 0-based header row
    ist.write(HEAD, 0, "USD millions", f_yr)
    for i, y in enumerate(years):
        ist.write(HEAD, 1 + i, "FY{}".format(y), f_yr)

    # (label, source column or None for formula, format, bold)
    reported = [
        ("Revenue", "revenue", f_usd, True),
        ("Cost of sales", "cost_of_sales", f_usd, False),
        ("Gross profit", "gross_profit", f_usd, True),
        ("Demand creation expense", "demand_creation_expense", f_usd, False),
        ("Operating overhead expense", "operating_overhead", f_usd, False),
        ("Total selling and administrative expense", "sg_and_a", f_usd, True),
        ("Operating income (gross profit less SG&A)", None, f_usd, True),
        ("Interest income (expense), net", "net_interest_income", f_usd, False),
        ("Other income (expense), net", "other_income_net", f_usd, False),
        ("Income before income taxes", None, f_usd, True),
        ("Income tax expense", "income_tax_expense", f_usd, False),
        ("Net income", None, f_usd, True),
        ("Diluted earnings per share", "eps_diluted", f_eps, False),
        ("Diluted shares (millions)", "diluted_shares", f_usd, False),
    ]
    row_of = {}
    r = HEAD + 1
    for label, source, fmt, bold in reported:
        ist.write(r, 0, label, f_lbl_b if bold else f_lbl)
        row_of[label] = r + 1                 # 1-based Excel row
        r += 1

    R_REV = row_of["Revenue"]
    R_COGS = row_of["Cost of sales"]
    R_GP = row_of["Gross profit"]
    R_DC = row_of["Demand creation expense"]
    R_OH = row_of["Operating overhead expense"]
    R_SGA = row_of["Total selling and administrative expense"]
    R_OI = row_of["Operating income (gross profit less SG&A)"]
    R_INT = row_of["Interest income (expense), net"]
    R_OTH = row_of["Other income (expense), net"]
    R_PTI = row_of["Income before income taxes"]
    R_TAX = row_of["Income tax expense"]
    R_NI = row_of["Net income"]
    R_EPS = row_of["Diluted earnings per share"]
    R_SH = row_of["Diluted shares (millions)"]

    for i, y in enumerate(years):
        c = 1 + i
        L = col_letter(c)
        row = fin.loc[y]
        ist.write_number(R_REV - 1, c, float(row.revenue), f_usd)
        ist.write_number(R_COGS - 1, c, float(row.cost_of_sales), f_usd)
        ist.write_number(R_GP - 1, c, float(row.gross_profit), f_usd)
        ist.write_number(R_DC - 1, c, float(row.demand_creation_expense), f_usd)
        ist.write_number(R_OH - 1, c, float(row.operating_overhead), f_usd)
        ist.write_number(R_SGA - 1, c, float(row.sg_and_a), f_usd)
        ist.write_formula(R_OI - 1, c, "={0}{1}-{0}{2}".format(L, R_GP, R_SGA), f_usd_b)
        ist.write_number(R_INT - 1, c, float(row.net_interest_income), f_usd)
        ist.write_number(R_OTH - 1, c, float(row.other_income_net), f_usd)
        ist.write_formula(R_PTI - 1, c, "={0}{1}+{0}{2}+{0}{3}".format(L, R_OI, R_INT, R_OTH), f_usd_b)
        ist.write_number(R_TAX - 1, c, float(row.income_tax_expense), f_usd)
        ist.write_formula(R_NI - 1, c, "={0}{1}-{0}{2}".format(L, R_PTI, R_TAX), f_usd_b)
        ist.write_number(R_EPS - 1, c, float(row.eps_diluted), f_eps)
        ist.write_number(R_SH - 1, c, float(row.diluted_shares), f_usd)

    # --- common size ---
    cs_head = R_SH + 2                        # 1-based
    ist.write(cs_head - 1, 0, "As a percentage of revenue", f_h2)
    for i, y in enumerate(years):
        ist.write(cs_head - 1, 1 + i, "FY{}".format(y), f_yr)
    common = [
        ("Gross margin", R_GP, True),
        ("Demand creation expense", R_DC, False),
        ("Operating overhead expense", R_OH, False),
        ("Total SG&A", R_SGA, False),
        ("Operating margin", R_OI, True),
        ("Net margin", R_NI, True),
    ]
    cs_rows = {}
    for j, (label, src, bold) in enumerate(common):
        rr = cs_head + 1 + j
        ist.write(rr - 1, 0, label, f_lbl_b if bold else f_lbl)
        cs_rows[label] = rr
        for i in range(n):
            L = col_letter(1 + i)
            ist.write_formula(rr - 1, 1 + i, "={0}{1}/{0}${2}".format(L, src, R_REV),
                              f_pct_b if bold else f_pct)

    # --- growth ---
    g_head = cs_head + len(common) + 3
    ist.write(g_head - 1, 0, "Year-on-year growth", f_h2)
    for i, y in enumerate(years):
        ist.write(g_head - 1, 1 + i, "FY{}".format(y), f_yr)
    growth = [("Revenue", R_REV), ("Gross profit", R_GP), ("Total SG&A", R_SGA),
              ("Operating income", R_OI), ("Net income", R_NI)]
    g_rows = {}
    for j, (label, src) in enumerate(growth):
        rr = g_head + 1 + j
        ist.write(rr - 1, 0, label, f_lbl)
        g_rows[label] = rr
        ist.write(rr - 1, 1, "n/a", f_lbl)
        for i in range(1, n):
            cur, prev = col_letter(1 + i), col_letter(i)
            ist.write_formula(rr - 1, 1 + i, "={0}{2}/{1}{2}-1".format(cur, prev, src), f_pct)

    ist.write(g_head + len(growth) + 2, 0,
              "NIKE does not report an operating income line. Its income statement goes straight "
              "from gross profit to SG&A to pre-tax income, so operating income here is gross "
              "profit less SG&A - what is usually called EBIT for this company. The formula is "
              "visible in row {}.".format(R_OI), f_note)
    ist.set_row(g_head + len(growth) + 2, 44)

    # =====================================================================
    # Balance sheet and cash flow
    # =====================================================================
    bs = book.add_worksheet("Balance sheet")
    bs.hide_gridlines(2)
    bs.set_column(0, 0, 36)
    bs.set_column(1, n, 12)
    bs.write(0, 0, "NIKE, Inc. - balance sheet and cash flow items", f_title)
    bs.write(1, 0, "USD millions at 31 May of each year. Free cash flow and total cash returned "
                   "to shareholders are formulas.", f_note)
    bs.write(HEAD, 0, "USD millions", f_yr)
    for i, y in enumerate(years):
        bs.write(HEAD, 1 + i, "FY{}".format(y), f_yr)

    bs_items = [
        ("Cash and cash equivalents", "cash_and_equivalents"),
        ("Accounts receivable, net", "receivables"),
        ("Inventories", "inventory"),
        ("Total current assets", "current_assets"),
        ("Total assets", "total_assets"),
        ("Total current liabilities", "current_liabilities"),
        ("Long-term debt", "long_term_debt"),
        ("Shareholders' equity", "shareholders_equity"),
        (None, None),
        ("Cash from operating activities", "operating_cash_flow"),
        ("Capital expenditure", "capital_expenditure"),
        ("Free cash flow", None),
        ("Dividends paid", "dividends_paid"),
        ("Share buybacks", "share_buybacks"),
        ("Total returned to shareholders", None),
    ]
    bs_row = {}
    r = HEAD + 1
    for label, source in bs_items:
        if label is None:
            r += 1
            continue
        bold = label in ("Total assets", "Shareholders' equity", "Free cash flow",
                         "Total returned to shareholders")
        bs.write(r, 0, label, f_lbl_b if bold else f_lbl)
        bs_row[label] = r + 1
        r += 1

    R_OCF = bs_row["Cash from operating activities"]
    R_CAPEX = bs_row["Capital expenditure"]
    R_FCF = bs_row["Free cash flow"]
    R_DIV = bs_row["Dividends paid"]
    R_BB = bs_row["Share buybacks"]
    R_TOT = bs_row["Total returned to shareholders"]

    for i, y in enumerate(years):
        c = 1 + i
        L = col_letter(c)
        row = fin.loc[y]
        for label, source in bs_items:
            if label is None or source is None:
                continue
            bold = label in ("Total assets", "Shareholders' equity")
            bs.write_number(bs_row[label] - 1, c, float(row[source]),
                            f_usd_b if bold else f_usd)
        bs.write_formula(R_FCF - 1, c, "={0}{1}-{0}{2}".format(L, R_OCF, R_CAPEX), f_usd_b)
        bs.write_formula(R_TOT - 1, c, "={0}{1}+{0}{2}".format(L, R_DIV, R_BB), f_usd_b)

    bs.write(r + 2, 0, "Capital expenditure and the shareholder return lines are reported as "
                       "cash outflows but tagged as positive amounts, so free cash flow is "
                       "operating cash flow minus capital expenditure.", f_note)
    bs.set_row(r + 2, 30)

    # =====================================================================
    # Ratios
    # =====================================================================
    rt = book.add_worksheet("Ratios")
    rt.hide_gridlines(2)
    rt.set_column(0, 0, 36)
    rt.set_column(1, n, 12)
    rt.write(0, 0, "NIKE, Inc. - ratio analysis", f_title)
    rt.write(1, 0, "Every cell on this sheet is a formula pointing at the Income statement or "
                   "Balance sheet tab. Nothing is typed in.", f_note)
    rt.write(HEAD, 0, "", f_yr)
    for i, y in enumerate(years):
        rt.write(HEAD, 1 + i, "FY{}".format(y), f_yr)

    IS = "'Income statement'!"
    BS = "'Balance sheet'!"

    def ratio_rows(start, heading, rows):
        rt.write(start - 1, 0, heading, f_h2)
        for i, y in enumerate(years):
            rt.write(start - 1, 1 + i, "FY{}".format(y), f_yr)
        out = {}
        for j, (label, builder, fmt, first_blank) in enumerate(rows):
            rr = start + 1 + j
            rt.write(rr - 1, 0, label, f_lbl)
            out[label] = rr
            for i in range(n):
                if first_blank and i == 0:
                    rt.write(rr - 1, 1 + i, "n/a", f_lbl)
                    continue
                rt.write_formula(rr - 1, 1 + i, builder(col_letter(1 + i), col_letter(i)), fmt)
        return out, start + len(rows) + 3

    profitability = [
        ("Gross margin", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(IS, c, R_GP, R_REV), f_pct, False),
        ("Operating margin", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(IS, c, R_OI, R_REV), f_pct, False),
        ("Net margin", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(IS, c, R_NI, R_REV), f_pct, False),
        ("SG&A as % of revenue", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(IS, c, R_SGA, R_REV), f_pct, False),
        ("Effective tax rate", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(IS, c, R_TAX, R_PTI), f_pct, False),
    ]
    _, next_start = ratio_rows(HEAD + 1, "Profitability", profitability)

    liquidity = [
        ("Current ratio", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(
            BS, c, bs_row["Total current assets"], bs_row["Total current liabilities"]), f_x, False),
        ("Inventory days", lambda c, p: "={0}{1}{2}/{3}{1}{4}*365".format(
            BS, c, bs_row["Inventories"], IS, R_COGS), f_days, False),
        ("Receivable days", lambda c, p: "={0}{1}{2}/{3}{1}{4}*365".format(
            BS, c, bs_row["Accounts receivable, net"], IS, R_REV), f_days, False),
        ("Long-term debt to equity", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(
            BS, c, bs_row["Long-term debt"], bs_row["Shareholders' equity"]), f_x, False),
    ]
    _, next_start = ratio_rows(next_start, "Liquidity and working capital", liquidity)

    returns = [
        ("Return on equity (average equity)", lambda c, p: "={0}{1}{2}/AVERAGE({3}{4}{5},{3}{1}{5})".format(
            IS, c, R_NI, BS, p, bs_row["Shareholders' equity"]), f_pct, True),
        ("Return on assets (average assets)", lambda c, p: "={0}{1}{2}/AVERAGE({3}{4}{5},{3}{1}{5})".format(
            IS, c, R_NI, BS, p, bs_row["Total assets"]), f_pct, True),
        ("Free cash flow as % of revenue", lambda c, p: "={0}{1}{2}/{3}{1}{4}".format(
            BS, c, R_FCF, IS, R_REV), f_pct, False),
        ("Cash returned as % of free cash flow", lambda c, p: "={0}{1}{2}/{0}{1}{3}".format(
            BS, c, R_TOT, R_FCF), f_pct, False),
    ]
    _, next_start = ratio_rows(next_start, "Returns and cash", returns)

    rt.write(next_start - 1, 0,
             "Return on equity and return on assets use the average of the opening and closing "
             "balance, because profit is earned across the year while the balance sheet is a "
             "single-day snapshot. FY2020 has no opening balance in this dataset, so it shows n/a.",
             f_note)
    rt.set_row(next_start - 1, 44)

    # =====================================================================
    # Margin bridge
    # =====================================================================
    mb = book.add_worksheet("Margin bridge")
    mb.hide_gridlines(2)
    mb.set_column(0, 0, 34)
    mb.set_column(1, 1, 14)
    mb.set_column(2, 2, 62)
    mb.write(0, 0, "Why operating income fell $2,514m between FY2024 and FY2026", f_title)
    mb.write(1, 0, "The three effects are formulas pointing at the Income statement tab, so they "
                   "stay correct if the figures change. They add back to the actual change, which "
                   "row 12 checks.", f_note)
    mb.set_row(1, 30)

    c24 = col_letter(1 + years.index(2024))
    c26 = col_letter(1 + years.index(2026))
    mb.write(3, 0, "Item", f_yr)
    mb.write(3, 1, "USD m", f_yr)
    mb.write(3, 2, "How it is calculated", f_yr)

    rows = [
        ("FY2024 operating income", "={0}{1}{2}".format(IS, c24, R_OI),
         "as reported"),
        ("Effect of lower revenue", "=({0}{1}{3}-{0}{2}{3})*({0}{2}{4}/{0}{2}{3})".format(
            IS, c26, c24, R_REV, R_GP),
         "change in revenue x the FY2024 gross margin"),
        ("Effect of lower gross margin", "={0}{1}{3}*({0}{1}{4}/{0}{1}{3}-{0}{2}{4}/{0}{2}{3})".format(
            IS, c26, c24, R_REV, R_GP),
         "FY2026 revenue x the change in gross margin"),
        ("Effect of change in SG&A", "=-({0}{1}{3}-{0}{2}{3})".format(IS, c26, c24, R_SGA),
         "minus the change in SG&A (a fall in SG&A helps profit)"),
        ("FY2026 operating income", "={0}{1}{2}".format(IS, c26, R_OI),
         "as reported"),
    ]
    for j, (label, formula, note) in enumerate(rows):
        rr = 4 + j
        bold = j in (0, 4)
        mb.write(rr, 0, label, f_lbl_b if bold else f_lbl)
        mb.write_formula(rr, 1, formula, f_usd_b if bold else f_usd)
        mb.write(rr, 2, note, f_note)

    mb.write(10, 0, "Check: FY2024 + the three effects", f_lbl_b)
    mb.write_formula(10, 1, "=B5+B6+B7+B8", f_usd_b)
    mb.write(11, 0, "Difference from reported FY2026", f_lbl_b)
    mb.write_formula(11, 1, "=B11-B9", f_usd_b)
    mb.write(11, 2, "should be zero", f_note)

    chart_bridge = book.add_chart({"type": "column"})
    chart_bridge.add_series({
        "name": "Effect on operating income",
        "categories": ["Margin bridge", 5, 0, 7, 0],
        "values": ["Margin bridge", 5, 1, 7, 1],
        "fill": {"color": CLAY},
        "data_labels": {"value": True, "num_format": "#,##0"},
    })
    chart_bridge.set_title({"name": "Drivers of the fall in operating income, FY2024 to FY2026 ($m)"})
    chart_bridge.set_legend({"none": True})
    chart_bridge.set_size({"width": 620, "height": 300})
    mb.insert_chart(14, 0, chart_bridge)

    # =====================================================================
    # Forecast
    # =====================================================================
    fc = book.add_worksheet("Forecast")
    fc.hide_gridlines(2)
    fc.set_column(0, 0, 34)
    fc.set_column(1, 4, 13)
    fc.write(0, 0, "Simple three-scenario forecast, FY2027 and FY2028", f_title)
    fc.write(1, 0, "This is not a valuation. It answers one question: if revenue and margins "
                   "behave in a stated way, what happens to profit? Every shaded cell is an "
                   "assumption you can change - the three scenario blocks below recalculate "
                   "automatically. The last column of the 'What the last seven years did' table "
                   "is there so each assumption can be compared with history.", f_note)
    fc.set_row(1, 44)

    fc.write(3, 0, "Assumptions (change the shaded cells)", f_h2)
    fc.write(4, 0, "", f_yr)
    for j, name in enumerate(["Low", "Base", "High"]):
        fc.write(4, 1 + j, name, f_yr)

    assumption_rows = [
        ("Revenue growth per year", [-0.02, 0.02, 0.05], f_input),
        ("Gross margin", [0.420, 0.435, 0.445], f_input),
        ("SG&A growth per year", [0.01, 0.02, 0.02], f_input),
        ("Effective tax rate", [0.20, 0.20, 0.20], f_input),
        ("Diluted share count change per year", [-0.010, -0.015, -0.015], f_input),
    ]
    A_FIRST = 6                               # 1-based Excel row of the first assumption
    for j, (label, values, fmt) in enumerate(assumption_rows):
        rr = A_FIRST + j
        fc.write(rr - 1, 0, label, f_lbl)
        for k, v in enumerate(values):
            fc.write_number(rr - 1, 1 + k, v, fmt)
    A_G, A_GM, A_SGA, A_TAX, A_SH = (A_FIRST, A_FIRST + 1, A_FIRST + 2,
                                     A_FIRST + 3, A_FIRST + 4)

    R_NONOP = A_FIRST + 6
    fc.write(R_NONOP - 1, 0, "Non-operating income, held flat ($m)", f_lbl)
    fc.write_formula(R_NONOP - 1, 1,
                     "={0}{1}{2}+{0}{1}{3}".format(IS, c26, R_INT, R_OTH), f_input_usd)
    fc.write(R_NONOP - 1, 2, "interest plus other income as reported in FY2026", f_note)

    # Historical basis table
    B_HEAD = R_NONOP + 2
    fc.write(B_HEAD - 1, 0, "What the last seven years did (FY2020-FY2026)", f_h2)
    for j, h in enumerate(["Average", "Lowest", "Highest", "FY2026"]):
        fc.write(B_HEAD - 1, 1 + j, h, f_yr)
    for j, row in basis.iterrows():
        rr = B_HEAD + 1 + j
        fc.write(rr - 1, 0, row["measure"], f_lbl)
        for k, key in enumerate(["fy2020_26_average", "minimum", "maximum", "fy2026_actual"]):
            fc.write_number(rr - 1, 1 + k, float(row[key]) / 100, f_pct)

    # Scenario blocks
    block_start = B_HEAD + len(basis) + 3
    scen_cols = {"Low": "B", "Base": "C", "High": "D"}
    line_items = [
        "Revenue", "Gross profit", "Gross margin", "SG&A", "SG&A as % of revenue",
        "Operating income", "Operating margin", "Non-operating income",
        "Income before income taxes", "Income tax expense", "Net income", "Net margin",
        "Diluted shares (millions)", "Diluted EPS",
    ]
    net_income_cells = {}
    eps_cells = {}
    for scenario, acol in scen_cols.items():
        fc.write(block_start - 1, 0, "{} case - {}".format(
            scenario, SCEN_TEXT[scenario]), f_h2)
        fc.set_row(block_start - 1, 28)
        fc.write(block_start, 0, "USD millions", f_yr)
        fc.write(block_start, 1, "FY2026 actual", f_yr)
        fc.write(block_start, 2, "FY2027", f_yr)
        fc.write(block_start, 3, "FY2028", f_yr)

        rows_1b = {}
        for j, item in enumerate(line_items):
            rr = block_start + 1 + j
            bold = item in ("Revenue", "Operating income", "Net income", "Diluted EPS")
            fc.write(rr - 1, 0, item, f_lbl_b if bold else f_lbl)
            rows_1b[item] = rr

        rv, gp, gm = rows_1b["Revenue"], rows_1b["Gross profit"], rows_1b["Gross margin"]
        sg, sgp = rows_1b["SG&A"], rows_1b["SG&A as % of revenue"]
        oi, om = rows_1b["Operating income"], rows_1b["Operating margin"]
        no, pt = rows_1b["Non-operating income"], rows_1b["Income before income taxes"]
        tx, ni = rows_1b["Income tax expense"], rows_1b["Net income"]
        nm, sh = rows_1b["Net margin"], rows_1b["Diluted shares (millions)"]
        ep = rows_1b["Diluted EPS"]

        # FY2026 actual column pulls straight from the Income statement tab.
        fc.write_formula(rv - 1, 1, "={0}{1}{2}".format(IS, c26, R_REV), f_usd_b)
        fc.write_formula(gp - 1, 1, "={0}{1}{2}".format(IS, c26, R_GP), f_usd)
        fc.write_formula(gm - 1, 1, "=B{0}/B{1}".format(gp, rv), f_pct)
        fc.write_formula(sg - 1, 1, "={0}{1}{2}".format(IS, c26, R_SGA), f_usd)
        fc.write_formula(sgp - 1, 1, "=B{0}/B{1}".format(sg, rv), f_pct)
        fc.write_formula(oi - 1, 1, "=B{0}-B{1}".format(gp, sg), f_usd_b)
        fc.write_formula(om - 1, 1, "=B{0}/B{1}".format(oi, rv), f_pct_b)
        fc.write_formula(no - 1, 1, "=$B${0}".format(R_NONOP), f_usd)
        fc.write_formula(pt - 1, 1, "=B{0}+B{1}".format(oi, no), f_usd)
        fc.write_formula(tx - 1, 1, "={0}{1}{2}".format(IS, c26, R_TAX), f_usd)
        fc.write_formula(ni - 1, 1, "=B{0}-B{1}".format(pt, tx), f_usd_b)
        fc.write_formula(nm - 1, 1, "=B{0}/B{1}".format(ni, rv), f_pct)
        fc.write_formula(sh - 1, 1, "={0}{1}{2}".format(IS, c26, R_SH), f_usd)
        fc.write_formula(ep - 1, 1, "=B{0}/B{1}".format(ni, sh), f_eps)

        for c in (2, 3):                       # FY2027, FY2028
            L, P = col_letter(c), col_letter(c - 1)
            fc.write_formula(rv - 1, c, "={0}{1}*(1+${2}${3})".format(P, rv, acol, A_G), f_usd_b)
            fc.write_formula(gp - 1, c, "={0}{1}*${2}${3}".format(L, rv, acol, A_GM), f_usd)
            fc.write_formula(gm - 1, c, "={0}{1}/{0}{2}".format(L, gp, rv), f_pct)
            fc.write_formula(sg - 1, c, "={0}{1}*(1+${2}${3})".format(P, sg, acol, A_SGA), f_usd)
            fc.write_formula(sgp - 1, c, "={0}{1}/{0}{2}".format(L, sg, rv), f_pct)
            fc.write_formula(oi - 1, c, "={0}{1}-{0}{2}".format(L, gp, sg), f_usd_b)
            fc.write_formula(om - 1, c, "={0}{1}/{0}{2}".format(L, oi, rv), f_pct_b)
            fc.write_formula(no - 1, c, "=$B${0}".format(R_NONOP), f_usd)
            fc.write_formula(pt - 1, c, "={0}{1}+{0}{2}".format(L, oi, no), f_usd)
            fc.write_formula(tx - 1, c, "={0}{1}*${2}${3}".format(L, pt, acol, A_TAX), f_usd)
            fc.write_formula(ni - 1, c, "={0}{1}-{0}{2}".format(L, pt, tx), f_usd_b)
            fc.write_formula(nm - 1, c, "={0}{1}/{0}{2}".format(L, ni, rv), f_pct)
            fc.write_formula(sh - 1, c, "={0}{1}*(1+${2}${3})".format(P, sh, acol, A_SH), f_usd)
            fc.write_formula(ep - 1, c, "={0}{1}/{0}{2}".format(L, ni, sh), f_eps)

        net_income_cells[scenario] = ni
        eps_cells[scenario] = ep
        block_start += len(line_items) + 4

    # Comparison table + chart
    cmp_head = block_start
    fc.write(cmp_head - 1, 0, "Net income by scenario", f_h2)
    for j, h in enumerate(["FY2026 actual", "FY2027", "FY2028"]):
        fc.write(cmp_head - 1, 1 + j, h, f_yr)
    for j, scenario in enumerate(["Low", "Base", "High"]):
        rr = cmp_head + 1 + j
        fc.write(rr - 1, 0, scenario, f_lbl)
        for k, c in enumerate([1, 2, 3]):
            L = col_letter(c)
            fc.write_formula(rr - 1, 1 + k, "={0}{1}".format(L, net_income_cells[scenario]), f_usd)

    chart_fc = book.add_chart({"type": "column"})
    for j, scenario in enumerate(["Low", "Base", "High"]):
        chart_fc.add_series({
            "name": scenario,
            "categories": ["Forecast", cmp_head - 1, 1, cmp_head - 1, 3],
            "values": ["Forecast", cmp_head + j, 1, cmp_head + j, 3],
            "fill": {"color": [PALE, STEEL, CLAY][j]},
        })
    chart_fc.set_title({"name": "Net income by scenario ($m)"})
    chart_fc.set_legend({"position": "bottom"})
    chart_fc.set_size({"width": 620, "height": 300})
    fc.insert_chart(cmp_head + 5, 0, chart_fc)

    # =====================================================================
    # Read me
    # =====================================================================
    rm = book.add_worksheet("Read me")
    rm.hide_gridlines(2)
    rm.set_column(0, 0, 2)
    rm.set_column(1, 1, 108)
    rm.write(1, 1, "NIKE, Inc. financial performance analysis", f_title)
    readme = [
        ("h", "What this workbook is"),
        ("p", "Seven financial years of NIKE's reported results (FY2020 to FY2026), the margins and "
              "ratios derived from them, an explanation of why operating income fell between FY2024 "
              "and FY2026, and a simple three-scenario forecast of FY2027 and FY2028."),
        ("h", "Where the figures come from"),
        ("p", "NIKE's own 10-K filings, read through the SEC's XBRL company facts API "
              "(data.sec.gov). The API is free and needs no key. A Python script downloads the file "
              "and writes out the line items; nothing in this workbook is typed in by hand except "
              "the forecast assumptions."),
        ("p", "NIKE's financial year ends on 31 May, so FY2026 covers June 2025 to May 2026."),
        ("h", "Checks that were run on the extracted data"),
        ("p", "Four reconciliations, all of which come to zero: revenue less cost of sales equals "
              "reported gross profit; demand creation plus operating overhead equals reported SG&A; "
              "operating income plus interest plus other income equals reported pre-tax income; and "
              "pre-tax income less tax equals reported net income."),
        ("h", "One thing to know about operating income"),
        ("p", "NIKE does not report an operating income line. Its income statement goes from gross "
              "profit straight to SG&A and then to pre-tax income. Operating income here is gross "
              "profit less SG&A, which is what is normally called EBIT for this company. The formula "
              "is visible in the Income statement tab."),
        ("h", "What this workbook is not"),
        ("p", "It is not a valuation, a DCF or an investment recommendation. The forecast is a "
              "sensitivity exercise: it shows what happens to profit under stated assumptions about "
              "revenue growth and margins. The assumptions are mine and they are all visible in "
              "shaded cells on the Forecast tab, next to what the last seven years actually did."),
        ("h", "Sheets"),
        ("p", "Dashboard - headline figures and charts\n"
              "Income statement - as reported, plus common-size and growth blocks\n"
              "Balance sheet - balance sheet and cash flow items\n"
              "Ratios - profitability, liquidity, working capital and returns\n"
              "Margin bridge - the three causes of the fall in operating income\n"
              "Forecast - three scenarios driven by the assumptions block"),
    ]
    rr = 3
    for kind, text in readme:
        if kind == "h":
            rm.write(rr, 1, text, f_bodyb)
            rr += 1
        else:
            lines = text.count("\n") + 1
            rm.write(rr, 1, text, f_body)
            rm.set_row(rr, max(14 * lines, 14 * (len(text) // 105 + 1)))
            rr += 2

    # =====================================================================
    # Dashboard
    # =====================================================================
    db = book.add_worksheet("Dashboard")
    book.worksheets_objs.insert(0, book.worksheets_objs.pop())
    db.hide_gridlines(2)
    db.set_column(0, 0, 2)
    for c in range(1, 9):
        db.set_column(c, c, 15)
    db.write(1, 1, "NIKE, Inc. - financial performance FY2020 to FY2026", f_title)
    db.write(2, 1, "USD millions unless stated. Source: NIKE 10-K filings via the SEC XBRL API. "
                   "Financial year ends 31 May.", f_kpi_l)

    kpis = [
        ("FY2026 revenue", "='Income statement'!{}{}".format(c26, R_REV), f_kpi_v),
        ("FY2026 operating income", "='Income statement'!{}{}".format(c26, R_OI), f_kpi_v),
        ("FY2026 net income", "='Income statement'!{}{}".format(c26, R_NI), f_kpi_v),
        ("FY2026 gross margin", "=Ratios!{}{}".format(c26, HEAD + 2), f_kpi_p),
        ("FY2026 operating margin", "=Ratios!{}{}".format(c26, HEAD + 3), f_kpi_p),
        ("FY2026 diluted EPS", "='Income statement'!{}{}".format(c26, R_EPS), f_kpi_e),
    ]
    for i, (label, formula, fmt) in enumerate(kpis):
        col = 1 + (i % 3) * 2
        rr = 4 + (i // 3) * 3
        db.write(rr, col, label, f_kpi_l)
        db.write_formula(rr + 1, col, formula, fmt)

    # Revenue columns with operating margin on a second axis.
    ch1 = book.add_chart({"type": "column"})
    ch1.add_series({
        "name": "Revenue",
        "categories": ["Income statement", HEAD, 1, HEAD, n],
        "values": ["Income statement", R_REV - 1, 1, R_REV - 1, n],
        "fill": {"color": STEEL},
        "gap": 45,
    })
    ch1_line = book.add_chart({"type": "line"})
    ch1_line.add_series({
        "name": "Operating margin (right axis)",
        "categories": ["Income statement", HEAD, 1, HEAD, n],
        "values": ["Ratios", HEAD + 2, 1, HEAD + 2, n],
        "line": {"color": CLAY, "width": 2.25},
        "y2_axis": True,
    })
    ch1.combine(ch1_line)
    ch1.set_title({"name": "Revenue and operating margin"})
    ch1.set_y_axis({"num_format": "#,##0", "name": "Revenue ($m)"})
    ch1.set_y2_axis({"num_format": "0%", "name": "Operating margin"})
    ch1.set_legend({"position": "bottom"})
    ch1.set_size({"width": 760, "height": 300})
    db.insert_chart(11, 1, ch1)

    # Margin trends.
    ch2 = book.add_chart({"type": "line"})
    for j, (name, rr, colour) in enumerate([
        ("Gross margin", HEAD + 2, STEEL),
        ("Operating margin", HEAD + 3, CLAY),
        ("Net margin", HEAD + 4, PALE),
    ]):
        ch2.add_series({
            "name": name,
            "categories": ["Income statement", HEAD, 1, HEAD, n],
            "values": ["Ratios", rr - 1, 1, rr - 1, n],
            "line": {"color": colour, "width": 2.0},
        })
    ch2.set_title({"name": "Margins"})
    ch2.set_y_axis({"num_format": "0%"})
    ch2.set_legend({"position": "bottom"})
    ch2.set_size({"width": 380, "height": 300})
    db.insert_chart(28, 1, ch2)

    # SG&A split as % of revenue.
    ch3 = book.add_chart({"type": "column", "subtype": "stacked"})
    for j, (name, rr, colour) in enumerate([
        ("Demand creation", cs_rows["Demand creation expense"], CLAY),
        ("Operating overhead", cs_rows["Operating overhead expense"], STEEL),
    ]):
        ch3.add_series({
            "name": name,
            "categories": ["Income statement", HEAD, 1, HEAD, n],
            "values": ["Income statement", rr - 1, 1, rr - 1, n],
            "fill": {"color": colour},
        })
    ch3.set_title({"name": "SG&A as % of revenue"})
    ch3.set_y_axis({"num_format": "0%"})
    ch3.set_legend({"position": "bottom"})
    ch3.set_size({"width": 380, "height": 300})
    db.insert_chart(28, 5, ch3)

    # Free cash flow and shareholder returns.
    ch4 = book.add_chart({"type": "column"})
    ch4.add_series({
        "name": "Free cash flow",
        "categories": ["Income statement", HEAD, 1, HEAD, n],
        "values": ["Balance sheet", R_FCF - 1, 1, R_FCF - 1, n],
        "fill": {"color": STEEL},
    })
    ch4.add_series({
        "name": "Returned to shareholders",
        "categories": ["Income statement", HEAD, 1, HEAD, n],
        "values": ["Balance sheet", R_TOT - 1, 1, R_TOT - 1, n],
        "fill": {"color": CLAY},
    })
    ch4.set_title({"name": "Free cash flow vs cash returned to shareholders ($m)"})
    ch4.set_legend({"position": "bottom"})
    ch4.set_size({"width": 760, "height": 300})
    db.insert_chart(45, 1, ch4)

    db.write(62, 1, "Operating income is gross profit less SG&A - NIKE does not report an operating "
                    "income line. See the Read me tab.", f_note)

    book.close()
    print("Wrote", OUT)


SCEN_TEXT = {
    "Low": "revenue falls 2% a year, gross margin 42.0%, SG&A trimmed 1% a year",
    "Base": "revenue grows 2% a year, gross margin recovers to 43.5%, SG&A grows 2%",
    "High": "revenue grows 5% a year, gross margin back to 44.5%, SG&A grows 2%",
}


if __name__ == "__main__":
    main()
