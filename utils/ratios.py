"""
Financial Ratio Calculation Engine
Calculates 20+ ratios across 4 categories with industry-adjusted health indicators
and professional judgment interpretive commentary.
"""

import numpy as np

# ── Industry-adjusted thresholds ──────────────────────────────────────────────
# Structure: {industry: {ratio_name: (critical_low, warning_low, warning_high, critical_high)}}
# None means no upper/lower bound concern
INDUSTRY_THRESHOLDS = {
    "Technology / SaaS": {
        "current_ratio": (0.8, 1.2, 3.5, 5.0),
        "quick_ratio": (0.6, 1.0, 3.0, 4.5),
        "cash_ratio": (0.1, 0.3, 2.5, None),
        "gross_margin": (0.30, 0.50, None, None),
        "operating_margin": (-0.10, 0.05, None, None),
        "net_margin": (-0.15, 0.02, None, None),
        "roa": (-0.05, 0.03, None, None),
        "roe": (-0.10, 0.05, 0.40, 0.60),
        "roic": (-0.05, 0.05, None, None),
        "debt_to_equity": (None, None, 1.5, 2.5),
        "debt_to_assets": (None, None, 0.50, 0.70),
        "interest_coverage": (1.0, 2.5, None, None),
        "asset_turnover": (0.3, 0.5, None, None),
        "inventory_turnover": (3.0, 5.0, None, None),
        "receivables_turnover": (4.0, 6.0, None, None),
        "dso": (None, None, 75, 100),
        "cash_conversion_cycle": (None, None, 90, 120),
    },
    "Manufacturing": {
        "current_ratio": (0.8, 1.3, 3.0, 4.5),
        "quick_ratio": (0.4, 0.8, 2.0, 3.0),
        "cash_ratio": (0.05, 0.15, 1.5, None),
        "gross_margin": (0.15, 0.25, None, None),
        "operating_margin": (0.0, 0.05, None, None),
        "net_margin": (-0.05, 0.02, None, None),
        "roa": (0.0, 0.03, None, None),
        "roe": (-0.05, 0.05, 0.30, 0.50),
        "roic": (0.0, 0.04, None, None),
        "debt_to_equity": (None, None, 1.8, 3.0),
        "debt_to_assets": (None, None, 0.55, 0.75),
        "interest_coverage": (1.0, 2.0, None, None),
        "asset_turnover": (0.5, 0.8, None, None),
        "inventory_turnover": (4.0, 6.0, None, None),
        "receivables_turnover": (5.0, 8.0, None, None),
        "dso": (None, None, 60, 90),
        "cash_conversion_cycle": (None, None, 80, 110),
    },
    "Retail": {
        "current_ratio": (0.7, 1.0, 2.5, 4.0),
        "quick_ratio": (0.2, 0.5, 1.5, 2.5),
        "cash_ratio": (0.05, 0.15, 1.0, None),
        "gross_margin": (0.20, 0.30, None, None),
        "operating_margin": (0.0, 0.03, None, None),
        "net_margin": (-0.03, 0.01, None, None),
        "roa": (0.0, 0.03, None, None),
        "roe": (-0.05, 0.05, 0.30, 0.50),
        "roic": (0.0, 0.04, None, None),
        "debt_to_equity": (None, None, 2.0, 3.5),
        "debt_to_assets": (None, None, 0.60, 0.80),
        "interest_coverage": (1.0, 2.0, None, None),
        "asset_turnover": (1.0, 1.5, None, None),
        "inventory_turnover": (5.0, 8.0, None, None),
        "receivables_turnover": (10.0, 15.0, None, None),
        "dso": (None, None, 30, 50),
        "cash_conversion_cycle": (None, None, 50, 80),
    },
    "Healthcare": {
        "current_ratio": (0.8, 1.2, 3.0, 4.5),
        "quick_ratio": (0.5, 0.9, 2.5, 3.5),
        "cash_ratio": (0.1, 0.2, 2.0, None),
        "gross_margin": (0.25, 0.40, None, None),
        "operating_margin": (-0.05, 0.05, None, None),
        "net_margin": (-0.10, 0.02, None, None),
        "roa": (-0.03, 0.03, None, None),
        "roe": (-0.05, 0.05, 0.35, 0.55),
        "roic": (-0.03, 0.04, None, None),
        "debt_to_equity": (None, None, 1.5, 2.5),
        "debt_to_assets": (None, None, 0.50, 0.70),
        "interest_coverage": (1.0, 2.5, None, None),
        "asset_turnover": (0.3, 0.6, None, None),
        "inventory_turnover": (4.0, 7.0, None, None),
        "receivables_turnover": (4.0, 6.0, None, None),
        "dso": (None, None, 70, 100),
        "cash_conversion_cycle": (None, None, 80, 110),
    },
    "Financial Services": {
        "current_ratio": (0.8, 1.0, 2.0, 3.0),
        "quick_ratio": (0.5, 0.8, 1.8, 2.5),
        "cash_ratio": (0.1, 0.2, 1.5, None),
        "gross_margin": (0.30, 0.50, None, None),
        "operating_margin": (0.0, 0.10, None, None),
        "net_margin": (-0.05, 0.05, None, None),
        "roa": (0.0, 0.005, None, None),
        "roe": (-0.05, 0.06, 0.25, 0.40),
        "roic": (0.0, 0.03, None, None),
        "debt_to_equity": (None, None, 5.0, 10.0),
        "debt_to_assets": (None, None, 0.85, 0.95),
        "interest_coverage": (1.0, 1.5, None, None),
        "asset_turnover": (0.02, 0.05, None, None),
        "inventory_turnover": (None, None, None, None),
        "receivables_turnover": (2.0, 4.0, None, None),
        "dso": (None, None, 90, 120),
        "cash_conversion_cycle": (None, None, None, None),
    },
    "Energy": {
        "current_ratio": (0.7, 1.0, 2.5, 4.0),
        "quick_ratio": (0.4, 0.7, 2.0, 3.0),
        "cash_ratio": (0.05, 0.15, 1.5, None),
        "gross_margin": (0.15, 0.30, None, None),
        "operating_margin": (-0.05, 0.05, None, None),
        "net_margin": (-0.10, 0.02, None, None),
        "roa": (-0.03, 0.03, None, None),
        "roe": (-0.10, 0.05, 0.30, 0.50),
        "roic": (-0.03, 0.04, None, None),
        "debt_to_equity": (None, None, 2.0, 3.5),
        "debt_to_assets": (None, None, 0.60, 0.80),
        "interest_coverage": (1.0, 2.0, None, None),
        "asset_turnover": (0.3, 0.5, None, None),
        "inventory_turnover": (5.0, 8.0, None, None),
        "receivables_turnover": (5.0, 8.0, None, None),
        "dso": (None, None, 60, 90),
        "cash_conversion_cycle": (None, None, 70, 100),
    },
    "Real Estate": {
        "current_ratio": (0.5, 0.8, 2.0, 3.0),
        "quick_ratio": (0.3, 0.6, 1.5, 2.5),
        "cash_ratio": (0.05, 0.10, 1.0, None),
        "gross_margin": (0.25, 0.40, None, None),
        "operating_margin": (0.0, 0.10, None, None),
        "net_margin": (-0.05, 0.05, None, None),
        "roa": (0.0, 0.02, None, None),
        "roe": (-0.05, 0.04, 0.20, 0.35),
        "roic": (0.0, 0.03, None, None),
        "debt_to_equity": (None, None, 3.0, 5.0),
        "debt_to_assets": (None, None, 0.70, 0.85),
        "interest_coverage": (1.0, 1.5, None, None),
        "asset_turnover": (0.05, 0.10, None, None),
        "inventory_turnover": (None, None, None, None),
        "receivables_turnover": (3.0, 5.0, None, None),
        "dso": (None, None, 80, 110),
        "cash_conversion_cycle": (None, None, None, None),
    },
    "Consumer Goods": {
        "current_ratio": (0.8, 1.2, 3.0, 4.5),
        "quick_ratio": (0.4, 0.7, 2.0, 3.0),
        "cash_ratio": (0.05, 0.15, 1.5, None),
        "gross_margin": (0.25, 0.35, None, None),
        "operating_margin": (0.0, 0.05, None, None),
        "net_margin": (-0.03, 0.02, None, None),
        "roa": (0.0, 0.04, None, None),
        "roe": (-0.05, 0.08, 0.35, 0.55),
        "roic": (0.0, 0.05, None, None),
        "debt_to_equity": (None, None, 1.5, 2.5),
        "debt_to_assets": (None, None, 0.50, 0.70),
        "interest_coverage": (1.5, 3.0, None, None),
        "asset_turnover": (0.6, 1.0, None, None),
        "inventory_turnover": (4.0, 7.0, None, None),
        "receivables_turnover": (6.0, 10.0, None, None),
        "dso": (None, None, 50, 75),
        "cash_conversion_cycle": (None, None, 60, 90),
    },
    "Telecommunications": {
        "current_ratio": (0.6, 0.9, 2.0, 3.0),
        "quick_ratio": (0.4, 0.7, 1.8, 2.5),
        "cash_ratio": (0.05, 0.15, 1.5, None),
        "gross_margin": (0.30, 0.45, None, None),
        "operating_margin": (0.0, 0.08, None, None),
        "net_margin": (-0.05, 0.03, None, None),
        "roa": (0.0, 0.03, None, None),
        "roe": (-0.05, 0.05, 0.30, 0.50),
        "roic": (0.0, 0.04, None, None),
        "debt_to_equity": (None, None, 2.5, 4.0),
        "debt_to_assets": (None, None, 0.60, 0.80),
        "interest_coverage": (1.0, 2.0, None, None),
        "asset_turnover": (0.3, 0.5, None, None),
        "inventory_turnover": (5.0, 10.0, None, None),
        "receivables_turnover": (5.0, 8.0, None, None),
        "dso": (None, None, 55, 80),
        "cash_conversion_cycle": (None, None, 40, 70),
    },
    "Utilities": {
        "current_ratio": (0.5, 0.8, 1.8, 2.5),
        "quick_ratio": (0.3, 0.6, 1.5, 2.0),
        "cash_ratio": (0.02, 0.08, 0.8, None),
        "gross_margin": (0.20, 0.35, None, None),
        "operating_margin": (0.0, 0.10, None, None),
        "net_margin": (-0.03, 0.05, None, None),
        "roa": (0.0, 0.02, None, None),
        "roe": (-0.03, 0.04, 0.15, 0.25),
        "roic": (0.0, 0.03, None, None),
        "debt_to_equity": (None, None, 2.5, 4.0),
        "debt_to_assets": (None, None, 0.65, 0.80),
        "interest_coverage": (1.5, 2.5, None, None),
        "asset_turnover": (0.2, 0.3, None, None),
        "inventory_turnover": (5.0, 10.0, None, None),
        "receivables_turnover": (6.0, 10.0, None, None),
        "dso": (None, None, 45, 65),
        "cash_conversion_cycle": (None, None, 30, 60),
    },
}

# Fallback thresholds when industry not specified
DEFAULT_THRESHOLDS = {
    "current_ratio": (0.8, 1.2, 3.0, 5.0),
    "quick_ratio": (0.5, 0.8, 2.5, 4.0),
    "cash_ratio": (0.05, 0.2, 2.0, None),
    "gross_margin": (0.15, 0.30, None, None),
    "operating_margin": (-0.05, 0.05, None, None),
    "net_margin": (-0.10, 0.02, None, None),
    "roa": (-0.03, 0.03, None, None),
    "roe": (-0.05, 0.08, 0.35, 0.60),
    "roic": (-0.03, 0.05, None, None),
    "debt_to_equity": (None, None, 2.0, 3.0),
    "debt_to_assets": (None, None, 0.55, 0.75),
    "interest_coverage": (1.0, 2.0, None, None),
    "asset_turnover": (0.3, 0.6, None, None),
    "inventory_turnover": (3.0, 5.0, None, None),
    "receivables_turnover": (4.0, 6.0, None, None),
    "dso": (None, None, 70, 100),
    "cash_conversion_cycle": (None, None, 80, 120),
}


def safe_divide(numerator, denominator):
    """Safe division returning None if denominator is zero or inputs are None."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def calculate_all_ratios(data: dict) -> dict:
    """
    Calculate all financial ratios from input data.
    
    Expected data keys:
        Balance Sheet: total_current_assets, total_current_liabilities, total_assets,
                      total_liabilities, total_equity, cash, inventory, accounts_receivable,
                      accounts_payable, long_term_debt, retained_earnings, market_cap
        Income Statement: revenue, cogs, operating_expenses, operating_income, ebit,
                         interest_expense, tax_expense, net_income, depreciation
        Cash Flow: operating_cash_flow, capital_expenditures
    """
    ratios = {}
    
    # ── Liquidity Ratios ──
    ratios["current_ratio"] = {
        "value": safe_divide(data.get("total_current_assets"), data.get("total_current_liabilities")),
        "name": "Current Ratio",
        "category": "Liquidity",
        "formula": "Current Assets / Current Liabilities",
        "description": "Measures ability to pay short-term obligations with short-term assets.",
    }
    
    quick_assets = None
    if data.get("total_current_assets") is not None and data.get("inventory") is not None:
        quick_assets = data["total_current_assets"] - data["inventory"]
    ratios["quick_ratio"] = {
        "value": safe_divide(quick_assets, data.get("total_current_liabilities")),
        "name": "Quick Ratio",
        "category": "Liquidity",
        "formula": "(Current Assets - Inventory) / Current Liabilities",
        "description": "Measures ability to meet short-term obligations without relying on inventory sales.",
    }
    
    ratios["cash_ratio"] = {
        "value": safe_divide(data.get("cash"), data.get("total_current_liabilities")),
        "name": "Cash Ratio",
        "category": "Liquidity",
        "formula": "Cash / Current Liabilities",
        "description": "Most conservative liquidity measure — can the company pay obligations with cash alone?",
    }
    
    working_capital = None
    if data.get("total_current_assets") is not None and data.get("total_current_liabilities") is not None:
        working_capital = data["total_current_assets"] - data["total_current_liabilities"]
    ratios["working_capital"] = {
        "value": working_capital,
        "name": "Working Capital",
        "category": "Liquidity",
        "formula": "Current Assets - Current Liabilities",
        "description": "Absolute dollar amount of short-term financial cushion.",
        "is_dollar": True,
    }
    
    ratios["ocf_ratio"] = {
        "value": safe_divide(data.get("operating_cash_flow"), data.get("total_current_liabilities")),
        "name": "Operating Cash Flow Ratio",
        "category": "Liquidity",
        "formula": "Operating Cash Flow / Current Liabilities",
        "description": "Measures whether operations generate enough cash to cover short-term obligations.",
    }
    
    # ── Profitability Ratios ──
    gross_profit = None
    if data.get("revenue") is not None and data.get("cogs") is not None:
        gross_profit = data["revenue"] - data["cogs"]
    
    ratios["gross_margin"] = {
        "value": safe_divide(gross_profit, data.get("revenue")),
        "name": "Gross Margin",
        "category": "Profitability",
        "formula": "(Revenue - COGS) / Revenue",
        "description": "Percentage of revenue retained after direct costs. Reflects pricing power and cost efficiency.",
        "is_percentage": True,
    }
    
    operating_income = data.get("operating_income") or data.get("ebit")
    ratios["operating_margin"] = {
        "value": safe_divide(operating_income, data.get("revenue")),
        "name": "Operating Margin",
        "category": "Profitability",
        "formula": "Operating Income / Revenue",
        "description": "Profitability from core operations before interest and taxes.",
        "is_percentage": True,
    }
    
    ratios["net_margin"] = {
        "value": safe_divide(data.get("net_income"), data.get("revenue")),
        "name": "Net Profit Margin",
        "category": "Profitability",
        "formula": "Net Income / Revenue",
        "description": "Bottom-line profitability — what percentage of each revenue dollar becomes profit.",
        "is_percentage": True,
    }
    
    ratios["roa"] = {
        "value": safe_divide(data.get("net_income"), data.get("total_assets")),
        "name": "Return on Assets (ROA)",
        "category": "Profitability",
        "formula": "Net Income / Total Assets",
        "description": "How efficiently the company uses its total asset base to generate profits.",
        "is_percentage": True,
    }
    
    ratios["roe"] = {
        "value": safe_divide(data.get("net_income"), data.get("total_equity")),
        "name": "Return on Equity (ROE)",
        "category": "Profitability",
        "formula": "Net Income / Total Equity",
        "description": "Return generated for shareholders. High ROE from leverage carries different risk than high ROE from margins.",
        "is_percentage": True,
    }
    
    # ROIC
    invested_capital = None
    if data.get("total_equity") is not None and data.get("long_term_debt") is not None:
        invested_capital = data["total_equity"] + data["long_term_debt"]
        if data.get("cash") is not None:
            invested_capital -= data["cash"]
    nopat = None
    if operating_income is not None and data.get("tax_expense") is not None and data.get("net_income") is not None:
        # Approximate tax rate
        ebt = data["net_income"] + data["tax_expense"] if data["tax_expense"] else data["net_income"]
        tax_rate = safe_divide(data["tax_expense"], ebt) if ebt and ebt > 0 else 0.25
        if tax_rate is not None:
            nopat = operating_income * (1 - tax_rate)
    ratios["roic"] = {
        "value": safe_divide(nopat, invested_capital),
        "name": "Return on Invested Capital (ROIC)",
        "category": "Profitability",
        "formula": "NOPAT / Invested Capital",
        "description": "Measures return on all capital invested in the business, regardless of financing structure.",
        "is_percentage": True,
    }
    
    # ── DuPont Decomposition ──
    net_profit_margin = safe_divide(data.get("net_income"), data.get("revenue"))
    asset_turnover_val = safe_divide(data.get("revenue"), data.get("total_assets"))
    equity_multiplier_val = safe_divide(data.get("total_assets"), data.get("total_equity"))
    
    ratios["dupont_margin"] = {
        "value": net_profit_margin,
        "name": "DuPont: Net Profit Margin",
        "category": "DuPont Decomposition",
        "formula": "Net Income / Revenue",
        "description": "Profit margin component — how much of each dollar of revenue becomes profit.",
        "is_percentage": True,
    }
    ratios["dupont_turnover"] = {
        "value": asset_turnover_val,
        "name": "DuPont: Asset Turnover",
        "category": "DuPont Decomposition",
        "formula": "Revenue / Total Assets",
        "description": "Efficiency component — how effectively assets generate revenue.",
    }
    ratios["dupont_leverage"] = {
        "value": equity_multiplier_val,
        "name": "DuPont: Equity Multiplier",
        "category": "DuPont Decomposition",
        "formula": "Total Assets / Total Equity",
        "description": "Leverage component — higher values mean more debt financing. Amplifies both returns and risk.",
    }
    
    # ── Solvency Ratios ──
    ratios["debt_to_equity"] = {
        "value": safe_divide(data.get("total_liabilities"), data.get("total_equity")),
        "name": "Debt-to-Equity",
        "category": "Solvency",
        "formula": "Total Liabilities / Total Equity",
        "description": "How much the company relies on debt versus equity financing.",
    }
    
    ratios["debt_to_assets"] = {
        "value": safe_divide(data.get("total_liabilities"), data.get("total_assets")),
        "name": "Debt-to-Assets",
        "category": "Solvency",
        "formula": "Total Liabilities / Total Assets",
        "description": "Percentage of assets financed by debt. Above 0.50 means more debt than equity financing.",
        "is_percentage": True,
    }
    
    ratios["interest_coverage"] = {
        "value": safe_divide(operating_income or data.get("ebit"), data.get("interest_expense")),
        "name": "Interest Coverage Ratio",
        "category": "Solvency",
        "formula": "EBIT / Interest Expense",
        "description": "How many times over the company can cover its interest payments. Below 1.5 signals distress risk.",
    }
    
    ratios["equity_multiplier"] = {
        "value": equity_multiplier_val,
        "name": "Equity Multiplier",
        "category": "Solvency",
        "formula": "Total Assets / Total Equity",
        "description": "Measures financial leverage. Higher values indicate greater reliance on debt.",
    }
    
    ratios["lt_debt_ratio"] = {
        "value": safe_divide(data.get("long_term_debt"), data.get("total_assets")),
        "name": "Long-Term Debt Ratio",
        "category": "Solvency",
        "formula": "Long-Term Debt / Total Assets",
        "description": "Proportion of assets financed by long-term obligations.",
        "is_percentage": True,
    }
    
    # ── Efficiency Ratios ──
    ratios["asset_turnover"] = {
        "value": asset_turnover_val,
        "name": "Asset Turnover",
        "category": "Efficiency",
        "formula": "Revenue / Total Assets",
        "description": "How efficiently the company uses its asset base to generate revenue.",
    }
    
    ratios["inventory_turnover"] = {
        "value": safe_divide(data.get("cogs"), data.get("inventory")),
        "name": "Inventory Turnover",
        "category": "Efficiency",
        "formula": "COGS / Inventory",
        "description": "How many times inventory is sold and replaced. Low values may indicate obsolescence risk.",
    }
    
    ratios["receivables_turnover"] = {
        "value": safe_divide(data.get("revenue"), data.get("accounts_receivable")),
        "name": "Receivables Turnover",
        "category": "Efficiency",
        "formula": "Revenue / Accounts Receivable",
        "description": "How quickly the company collects from customers. Declining values may signal credit risk.",
    }
    
    dso = None
    recv_turn = safe_divide(data.get("revenue"), data.get("accounts_receivable"))
    if recv_turn and recv_turn > 0:
        dso = 365 / recv_turn
    ratios["dso"] = {
        "value": dso,
        "name": "Days Sales Outstanding",
        "category": "Efficiency",
        "formula": "365 / Receivables Turnover",
        "description": "Average days to collect payment. Rising DSO with revenue growth may signal channel stuffing.",
    }
    
    dio = None
    inv_turn = safe_divide(data.get("cogs"), data.get("inventory"))
    if inv_turn and inv_turn > 0:
        dio = 365 / inv_turn
    dpo = None
    if data.get("cogs") and data.get("accounts_payable"):
        ap_turn = data["cogs"] / data["accounts_payable"] if data["accounts_payable"] > 0 else None
        if ap_turn and ap_turn > 0:
            dpo = 365 / ap_turn
    
    ccc = None
    if dso is not None and dio is not None and dpo is not None:
        ccc = dso + dio - dpo
    ratios["cash_conversion_cycle"] = {
        "value": ccc,
        "name": "Cash Conversion Cycle",
        "category": "Efficiency",
        "formula": "DSO + DIO - DPO",
        "description": "Days between paying for inventory and collecting from customers. Lower is better.",
    }
    
    # ── Earnings Quality ──
    accruals = None
    if data.get("net_income") is not None and data.get("operating_cash_flow") is not None:
        accruals = data["net_income"] - data["operating_cash_flow"]
    ratios["accruals_ratio"] = {
        "value": safe_divide(accruals, data.get("total_assets")),
        "name": "Accruals Ratio",
        "category": "Earnings Quality",
        "formula": "(Net Income - Operating Cash Flow) / Total Assets",
        "description": "High positive accruals suggest earnings may not be backed by cash. A key earnings quality indicator.",
        "is_percentage": True,
    }
    
    ratios["ocf_to_ni"] = {
        "value": safe_divide(data.get("operating_cash_flow"), data.get("net_income")),
        "name": "OCF / Net Income",
        "category": "Earnings Quality",
        "formula": "Operating Cash Flow / Net Income",
        "description": "Healthy companies generate cash exceeding reported income. Ratio below 1.0 is a quality concern.",
    }
    
    return ratios


def assess_health(ratio_key: str, value, industry: str = None) -> dict:
    """
    Assess the health status of a ratio value given industry context.
    
    Returns dict with:
        status: 'good', 'warning', 'critical', 'neutral'
        color: hex color code
        emoji: status indicator
        commentary: interpretive text
    """
    if value is None:
        return {"status": "unavailable", "color": "#95A5A6", "emoji": "⚪", "commentary": "Insufficient data to calculate."}
    
    thresholds = INDUSTRY_THRESHOLDS.get(industry, DEFAULT_THRESHOLDS).get(ratio_key)
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS.get(ratio_key)
    if thresholds is None:
        return {"status": "neutral", "color": "#3498DB", "emoji": "🔵", "commentary": "No threshold defined for this ratio."}
    
    crit_low, warn_low, warn_high, crit_high = thresholds
    
    # Check critical low
    if crit_low is not None and value < crit_low:
        return {"status": "critical", "color": "#E74C3C", "emoji": "🔴", "commentary": f"Critically below industry threshold ({crit_low:.2f}). Immediate attention required."}
    
    # Check warning low
    if warn_low is not None and value < warn_low:
        return {"status": "warning", "color": "#F39C12", "emoji": "🟡", "commentary": f"Below healthy range for this industry (threshold: {warn_low:.2f}). Monitor closely."}
    
    # Check critical high (for ratios where too high is bad, like D/E)
    if crit_high is not None and value > crit_high:
        return {"status": "critical", "color": "#E74C3C", "emoji": "🔴", "commentary": f"Critically above industry norm ({crit_high:.2f}). May indicate excessive risk."}
    
    # Check warning high
    if warn_high is not None and value > warn_high:
        return {"status": "warning", "color": "#F39C12", "emoji": "🟡", "commentary": f"Above typical range for this industry (threshold: {warn_high:.2f}). Warrants investigation."}
    
    return {"status": "good", "color": "#27AE60", "emoji": "🟢", "commentary": "Within healthy range for this industry."}


def get_cross_ratio_insights(ratios: dict, industry: str = None) -> list:
    """
    Generate professional judgment insights by analyzing relationships between ratios.
    This is the sophistication layer — connecting ratios to tell a story.
    """
    insights = []
    
    # Helper to safely get ratio values
    def val(key):
        r = ratios.get(key, {})
        return r.get("value") if isinstance(r, dict) else None
    
    # 1. Liquidity masking operational issues
    cr = val("current_ratio")
    ccc = val("cash_conversion_cycle")
    if cr and ccc and cr > 1.5 and ccc and ccc > 80:
        insights.append({
            "type": "warning",
            "title": "Liquidity May Mask Operational Inefficiency",
            "detail": f"Current ratio ({cr:.2f}) appears healthy, but the cash conversion cycle ({ccc:.0f} days) is elevated. "
                      "The company may be tying up capital in receivables or inventory despite appearing liquid. "
                      "Investigate whether receivables are aging or inventory is becoming obsolete.",
            "related_ratios": ["current_ratio", "cash_conversion_cycle", "dso", "inventory_turnover"],
        })
    
    # 2. Revenue quality concern — DSO rising
    dso = val("dso")
    if dso and dso > 60:
        insights.append({
            "type": "warning",
            "title": "Receivables Collection Risk",
            "detail": f"Days Sales Outstanding ({dso:.0f} days) is elevated. If DSO is increasing while revenue grows, "
                      "this may indicate loosened credit terms, channel stuffing, or potential revenue recognition "
                      "issues under ASC 606. Examine customer concentration and aging schedules.",
            "related_ratios": ["dso", "receivables_turnover", "accruals_ratio"],
        })
    
    # 3. DuPont decomposition insight — ROE driven by leverage
    roe = val("roe")
    em = val("dupont_leverage")
    npm = val("dupont_margin")
    if roe and em and npm:
        if roe > 0.15 and em > 2.5:
            insights.append({
                "type": "warning",
                "title": "ROE Driven by Leverage, Not Profitability",
                "detail": f"ROE ({roe:.1%}) appears strong, but the equity multiplier ({em:.2f}x) indicates heavy "
                          f"leverage is the primary driver rather than profit margins ({npm:.1%}). "
                          "High-leverage ROE is inherently riskier — if earnings decline, the equity cushion is thin. "
                          "Cross-reference with the Altman Z-Score solvency components.",
                "related_ratios": ["roe", "dupont_leverage", "dupont_margin", "debt_to_equity"],
            })
        elif roe > 0.15 and npm and npm > 0.10 and em < 2.0:
            insights.append({
                "type": "positive",
                "title": "High-Quality ROE Driven by Margins",
                "detail": f"ROE ({roe:.1%}) is strong and driven primarily by profit margins ({npm:.1%}) "
                          f"rather than leverage (equity multiplier: {em:.2f}x). This represents sustainable, "
                          "high-quality earnings generation.",
                "related_ratios": ["roe", "dupont_margin", "dupont_turnover", "dupont_leverage"],
            })
    
    # 4. Earnings quality concern
    accruals = val("accruals_ratio")
    ocf_ni = val("ocf_to_ni")
    if accruals is not None and accruals > 0.05:
        insights.append({
            "type": "critical",
            "title": "Earnings Quality Concern — High Accruals",
            "detail": f"Accruals ratio ({accruals:.1%}) is significantly positive, meaning reported earnings "
                      "substantially exceed cash generated. This divergence can indicate aggressive accounting "
                      "policies, premature revenue recognition, or deferred expense recognition. "
                      "Compare with the Beneish M-Score for additional manipulation indicators.",
            "related_ratios": ["accruals_ratio", "ocf_to_ni"],
        })
    elif ocf_ni is not None and ocf_ni < 0.8 and ocf_ni > 0:
        insights.append({
            "type": "warning",
            "title": "Operating Cash Flow Lags Net Income",
            "detail": f"OCF-to-Net Income ratio ({ocf_ni:.2f}x) is below 1.0, suggesting earnings are not fully "
                      "supported by cash generation. Investigate working capital changes and non-cash items.",
            "related_ratios": ["ocf_to_ni", "accruals_ratio"],
        })
    
    # 5. Solvency stress
    ic = val("interest_coverage")
    dte = val("debt_to_equity")
    if ic is not None and ic < 2.0:
        detail = f"Interest coverage ({ic:.2f}x) is thin — the company barely earns enough to cover debt service. "
        if dte and dte > 2.0:
            detail += f"Combined with a debt-to-equity ratio of {dte:.2f}, this signals potential covenant violation risk. "
        detail += "Review debt maturity schedule and assess going concern implications per AU-C Section 570."
        insights.append({
            "type": "critical",
            "title": "Debt Service Strain — Going Concern Indicator",
            "detail": detail,
            "related_ratios": ["interest_coverage", "debt_to_equity", "debt_to_assets"],
        })
    
    # 6. Inventory concern
    inv_turn = val("inventory_turnover")
    gm = val("gross_margin")
    if inv_turn and gm and inv_turn < 4 and gm and gm > 0.25:
        insights.append({
            "type": "warning",
            "title": "Potential Inventory Obsolescence",
            "detail": f"Inventory turnover ({inv_turn:.1f}x) is low while gross margins ({gm:.1%}) remain stable. "
                      "This pattern can indicate inventory that is aging and may require write-downs "
                      "that have not yet been recognized. Investigate inventory aging and NRV assessments.",
            "related_ratios": ["inventory_turnover", "gross_margin"],
        })
    
    # 7. Positive overall health
    if cr and cr > 1.5 and ic and ic > 3.0 and npm and npm > 0.05:
        if not any(i["type"] == "critical" for i in insights):
            insights.append({
                "type": "positive",
                "title": "Solid Overall Financial Position",
                "detail": f"The company shows healthy liquidity (current ratio: {cr:.2f}), comfortable debt service "
                          f"(interest coverage: {ic:.1f}x), and positive profitability (net margin: {npm:.1%}). "
                          "No immediate red flags detected in the ratio analysis.",
                "related_ratios": ["current_ratio", "interest_coverage", "net_margin"],
            })
    
    return insights
