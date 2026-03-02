"""
DCF Valuation Engine
Full discounted cash flow model with WACC build-up, scenario modeling,
sensitivity analysis, and assumption validation with professional judgment.
"""

import numpy as np


def validate_assumptions(assumptions: dict) -> list:
    """
    Professional judgment layer: challenge assumptions that fall outside defensible ranges.
    Returns list of warnings, similar to how a senior analyst reviews a junior's model.
    """
    warnings = []
    
    tgr = assumptions.get("terminal_growth_rate", 0)
    rfr = assumptions.get("risk_free_rate", 0)
    if tgr > rfr:
        warnings.append({
            "severity": "critical",
            "field": "Terminal Growth Rate",
            "message": f"Terminal growth rate ({tgr:.1%}) exceeds the risk-free rate ({rfr:.1%}). "
                       "This implies the company will eventually grow faster than the economy indefinitely, "
                       "which is not sustainable. Consider reducing to 2.0-2.5%.",
        })
    elif tgr > 0.03:
        warnings.append({
            "severity": "warning",
            "field": "Terminal Growth Rate",
            "message": f"Terminal growth rate ({tgr:.1%}) is above long-term GDP growth (~2.5-3.0%). "
                       "This is aggressive for perpetuity growth. Ensure this is justified by market dynamics.",
        })
    
    # Revenue growth sanity checks
    rev_growth = assumptions.get("revenue_growth_rates", [])
    if rev_growth:
        max_growth = max(rev_growth)
        if max_growth > 0.30:
            warnings.append({
                "severity": "warning",
                "field": "Revenue Growth",
                "message": f"Peak projected revenue growth ({max_growth:.0%}) is very aggressive. "
                           "Growth above 30% is difficult to sustain beyond 1-2 years. Validate with "
                           "historical trends and market size analysis.",
            })
        
        # Check if growth trend makes sense (should generally decelerate)
        if len(rev_growth) >= 3:
            if rev_growth[-1] > rev_growth[0] and rev_growth[0] > 0.10:
                warnings.append({
                    "severity": "warning",
                    "field": "Revenue Growth Trajectory",
                    "message": "Revenue growth is projected to accelerate over the forecast period. "
                              "Most companies experience growth deceleration as they scale. "
                              "Consider whether this trajectory is realistic.",
                })
    
    # EBITDA margin checks
    ebitda_margins = assumptions.get("ebitda_margins", [])
    if ebitda_margins:
        max_margin = max(ebitda_margins)
        if max_margin > 0.40:
            warnings.append({
                "severity": "warning",
                "field": "EBITDA Margin",
                "message": f"Projected EBITDA margin ({max_margin:.0%}) exceeds 40%, which is top-quartile "
                           "for most industries. Ensure margin expansion is supported by specific operational "
                           "improvements and not just optimistic assumptions.",
            })
    
    # WACC checks
    wacc = assumptions.get("wacc")
    if wacc and wacc < 0.06:
        warnings.append({
            "severity": "warning",
            "field": "WACC",
            "message": f"WACC ({wacc:.1%}) is unusually low. In most environments, a WACC below 6% "
                       "is only appropriate for the most stable, investment-grade companies. Verify inputs.",
        })
    elif wacc and wacc > 0.20:
        warnings.append({
            "severity": "warning",
            "field": "WACC",
            "message": f"WACC ({wacc:.1%}) is very high, which will heavily discount future cash flows. "
                       "Ensure the cost of equity assumptions (beta, risk premium) are appropriate.",
        })
    
    return warnings


def calculate_wacc(
    risk_free_rate: float,
    equity_risk_premium: float,
    beta: float,
    cost_of_debt: float,
    tax_rate: float,
    equity_weight: float,
    debt_weight: float,
) -> dict:
    """Calculate Weighted Average Cost of Capital with full component breakdown."""
    cost_of_equity = risk_free_rate + (beta * equity_risk_premium)
    after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
    wacc = (cost_of_equity * equity_weight) + (after_tax_cost_of_debt * debt_weight)
    
    return {
        "wacc": wacc,
        "cost_of_equity": cost_of_equity,
        "after_tax_cost_of_debt": after_tax_cost_of_debt,
        "components": {
            "risk_free_rate": risk_free_rate,
            "equity_risk_premium": equity_risk_premium,
            "beta": beta,
            "cost_of_debt": cost_of_debt,
            "tax_rate": tax_rate,
            "equity_weight": equity_weight,
            "debt_weight": debt_weight,
        }
    }


def run_dcf(
    base_revenue: float,
    revenue_growth_rates: list,
    ebitda_margins: list,
    capex_pct: float,
    nwc_change_pct: float,
    da_pct: float,
    wacc: float,
    terminal_growth_rate: float,
    shares_outstanding: float = None,
    net_debt: float = None,
) -> dict:
    """
    Run a full DCF model.
    
    Args:
        base_revenue: Current year revenue
        revenue_growth_rates: List of growth rates for each projection year
        ebitda_margins: List of EBITDA margins for each projection year
        capex_pct: Capital expenditures as % of revenue
        nwc_change_pct: Net working capital change as % of revenue change
        da_pct: Depreciation & amortization as % of revenue
        wacc: Weighted average cost of capital
        terminal_growth_rate: Perpetuity growth rate
        shares_outstanding: For per-share value calculation
        net_debt: Total debt minus cash for equity bridge
    
    Returns:
        Complete DCF output with projections, valuations, and decomposition.
    """
    n_years = len(revenue_growth_rates)
    
    # Build projections
    projections = []
    prev_revenue = base_revenue
    
    for i in range(n_years):
        revenue = prev_revenue * (1 + revenue_growth_rates[i])
        ebitda = revenue * ebitda_margins[i]
        da = revenue * da_pct
        ebit = ebitda - da
        # Assume ~25% tax rate on EBIT for FCFF
        tax_on_ebit = ebit * 0.25 if ebit > 0 else 0
        nopat = ebit - tax_on_ebit
        capex = revenue * capex_pct
        rev_change = revenue - prev_revenue
        nwc_change = rev_change * nwc_change_pct
        
        fcf = nopat + da - capex - nwc_change
        discount_factor = 1 / ((1 + wacc) ** (i + 1))
        pv_fcf = fcf * discount_factor
        
        projections.append({
            "year": i + 1,
            "revenue": revenue,
            "revenue_growth": revenue_growth_rates[i],
            "ebitda": ebitda,
            "ebitda_margin": ebitda_margins[i],
            "da": da,
            "ebit": ebit,
            "nopat": nopat,
            "capex": capex,
            "nwc_change": nwc_change,
            "fcf": fcf,
            "discount_factor": discount_factor,
            "pv_fcf": pv_fcf,
        })
        
        prev_revenue = revenue
    
    # Terminal value
    terminal_fcf = projections[-1]["fcf"] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate) if wacc > terminal_growth_rate else 0
    tv_discount_factor = 1 / ((1 + wacc) ** n_years)
    pv_terminal_value = terminal_value * tv_discount_factor
    
    # Sum PV of FCFs
    pv_fcfs = sum(p["pv_fcf"] for p in projections)
    
    # Enterprise value
    enterprise_value = pv_fcfs + pv_terminal_value
    
    # Equity value
    equity_value = enterprise_value - (net_debt or 0)
    
    # Per share
    per_share = equity_value / shares_outstanding if shares_outstanding and shares_outstanding > 0 else None
    
    # Value decomposition (for waterfall chart)
    decomposition = []
    for p in projections:
        decomposition.append({
            "label": f"Year {p['year']} FCF",
            "value": p["pv_fcf"],
            "pct_of_ev": p["pv_fcf"] / enterprise_value if enterprise_value > 0 else 0,
        })
    decomposition.append({
        "label": "Terminal Value",
        "value": pv_terminal_value,
        "pct_of_ev": pv_terminal_value / enterprise_value if enterprise_value > 0 else 0,
    })
    
    # Terminal value as % of EV (risk indicator)
    tv_pct = pv_terminal_value / enterprise_value if enterprise_value > 0 else 0
    
    return {
        "projections": projections,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "pv_fcfs": pv_fcfs,
        "enterprise_value": enterprise_value,
        "net_debt": net_debt,
        "equity_value": equity_value,
        "per_share_value": per_share,
        "tv_pct_of_ev": tv_pct,
        "decomposition": decomposition,
        "assumptions": {
            "base_revenue": base_revenue,
            "revenue_growth_rates": revenue_growth_rates,
            "ebitda_margins": ebitda_margins,
            "capex_pct": capex_pct,
            "nwc_change_pct": nwc_change_pct,
            "da_pct": da_pct,
            "wacc": wacc,
            "terminal_growth_rate": terminal_growth_rate,
        }
    }


def sensitivity_analysis(
    base_revenue: float,
    revenue_growth_rates: list,
    ebitda_margins: list,
    capex_pct: float,
    nwc_change_pct: float,
    da_pct: float,
    base_wacc: float,
    base_tgr: float,
    shares_outstanding: float = None,
    net_debt: float = None,
    wacc_range: tuple = (-0.02, 0.02, 0.005),
    tgr_range: tuple = (-0.01, 0.01, 0.005),
) -> dict:
    """
    Two-variable sensitivity analysis on WACC and terminal growth rate.
    Returns a matrix of enterprise values for each combination.
    """
    wacc_values = np.arange(
        base_wacc + wacc_range[0],
        base_wacc + wacc_range[1] + wacc_range[2],
        wacc_range[2]
    )
    tgr_values = np.arange(
        base_tgr + tgr_range[0],
        base_tgr + tgr_range[1] + tgr_range[2],
        tgr_range[2]
    )
    
    # Ensure base values are in the arrays
    wacc_values = sorted(set([round(w, 4) for w in wacc_values] + [base_wacc]))
    tgr_values = sorted(set([round(t, 4) for t in tgr_values] + [base_tgr]))
    
    matrix = []
    for w in wacc_values:
        row = []
        for t in tgr_values:
            if w <= t:
                row.append(None)  # Invalid: WACC must exceed TGR
            else:
                result = run_dcf(
                    base_revenue, revenue_growth_rates, ebitda_margins,
                    capex_pct, nwc_change_pct, da_pct, w, t,
                    shares_outstanding, net_debt
                )
                row.append(result["enterprise_value"])
        matrix.append(row)
    
    return {
        "wacc_values": wacc_values,
        "tgr_values": tgr_values,
        "ev_matrix": matrix,
        "base_wacc": base_wacc,
        "base_tgr": base_tgr,
    }


def run_scenarios(
    base_revenue: float,
    scenarios: dict,
    capex_pct: float,
    nwc_change_pct: float,
    da_pct: float,
    shares_outstanding: float = None,
    net_debt: float = None,
) -> dict:
    """
    Run DCF for multiple scenarios (Base, Bull, Bear).
    
    scenarios should be a dict like:
    {
        "Base": {"growth_rates": [...], "ebitda_margins": [...], "wacc": 0.10, "tgr": 0.025, "probability": 0.50},
        "Bull": {"growth_rates": [...], "ebitda_margins": [...], "wacc": 0.09, "tgr": 0.03, "probability": 0.25},
        "Bear": {"growth_rates": [...], "ebitda_margins": [...], "wacc": 0.12, "tgr": 0.02, "probability": 0.25},
    }
    """
    results = {}
    weighted_ev = 0
    
    for name, params in scenarios.items():
        result = run_dcf(
            base_revenue=base_revenue,
            revenue_growth_rates=params["growth_rates"],
            ebitda_margins=params["ebitda_margins"],
            capex_pct=capex_pct,
            nwc_change_pct=nwc_change_pct,
            da_pct=da_pct,
            wacc=params["wacc"],
            terminal_growth_rate=params["tgr"],
            shares_outstanding=shares_outstanding,
            net_debt=net_debt,
        )
        result["probability"] = params["probability"]
        results[name] = result
        weighted_ev += result["enterprise_value"] * params["probability"]
    
    return {
        "scenarios": results,
        "weighted_enterprise_value": weighted_ev,
        "weighted_equity_value": weighted_ev - (net_debt or 0),
        "weighted_per_share": (weighted_ev - (net_debt or 0)) / shares_outstanding if shares_outstanding else None,
    }
