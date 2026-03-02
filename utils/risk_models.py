"""
Risk Assessment Models
Implements Altman Z-Score, Beneish M-Score, and Piotroski F-Score
with component-level decomposition and professional standards references.
"""


def calculate_altman_z_score(data: dict) -> dict:
    """
    Altman Z-Score: Predicts probability of bankruptcy.
    
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    
    X1 = Working Capital / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Market Value of Equity / Total Liabilities
    X5 = Sales / Total Assets
    
    Zones: > 2.99 Safe | 1.81-2.99 Grey | < 1.81 Distress
    """
    ta = data.get("total_assets", 0)
    if not ta or ta == 0:
        return {"error": "Total assets required for Z-Score calculation."}
    
    wc = (data.get("total_current_assets", 0) or 0) - (data.get("total_current_liabilities", 0) or 0)
    re = data.get("retained_earnings", 0) or 0
    ebit = data.get("ebit") or data.get("operating_income", 0) or 0
    market_cap = data.get("market_cap", 0) or 0
    tl = data.get("total_liabilities", 0) or 0
    revenue = data.get("revenue", 0) or 0
    
    x1 = wc / ta
    x2 = re / ta
    x3 = ebit / ta
    x4 = market_cap / tl if tl > 0 else 0
    x5 = revenue / ta
    
    z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
    
    # Determine zone
    if z_score > 2.99:
        zone = "Safe Zone"
        zone_color = "#27AE60"
        zone_desc = "Low probability of bankruptcy. Financial position appears stable."
    elif z_score > 1.81:
        zone = "Grey Zone"
        zone_color = "#F39C12"
        zone_desc = ("Indeterminate zone — the company shows some distress signals but is not in immediate danger. "
                     "Warrants closer monitoring and investigation of specific risk factors.")
    else:
        zone = "Distress Zone"
        zone_color = "#E74C3C"
        zone_desc = ("High probability of financial distress. Per AU-C Section 570, the auditor should evaluate "
                     "whether substantial doubt exists about the entity's ability to continue as a going concern. "
                     "Consider management's plans, available financing, and ability to restructure obligations.")
    
    # Component analysis — which factors drive the score
    components = [
        {"name": "Working Capital / Total Assets (X1)", "variable": "X1", "raw": x1, "weighted": 1.2 * x1,
         "coefficient": 1.2, "interpretation": "Liquidity position relative to size. Negative indicates current liabilities exceed current assets."},
        {"name": "Retained Earnings / Total Assets (X2)", "variable": "X2", "raw": x2, "weighted": 1.4 * x2,
         "coefficient": 1.4, "interpretation": "Cumulative profitability and age of firm. Low values indicate limited profit history or accumulated losses."},
        {"name": "EBIT / Total Assets (X3)", "variable": "X3", "raw": x3, "weighted": 3.3 * x3,
         "coefficient": 3.3, "interpretation": "Operating profitability of assets. Highest coefficient — most influential factor in the model."},
        {"name": "Market Cap / Total Liabilities (X4)", "variable": "X4", "raw": x4, "weighted": 0.6 * x4,
         "coefficient": 0.6, "interpretation": "Market's assessment of solvency. Low values suggest the market perceives high default risk."},
        {"name": "Revenue / Total Assets (X5)", "variable": "X5", "raw": x5, "weighted": 1.0 * x5,
         "coefficient": 1.0, "interpretation": "Asset efficiency. Measures how effectively the firm uses assets to generate revenue."},
    ]
    
    # Sort by contribution (absolute weighted value)
    components.sort(key=lambda c: abs(c["weighted"]), reverse=True)
    
    # Identify primary driver
    primary_driver = components[0]
    primary_drag = min(components, key=lambda c: c["weighted"])
    
    return {
        "z_score": z_score,
        "zone": zone,
        "zone_color": zone_color,
        "zone_description": zone_desc,
        "components": components,
        "primary_driver": primary_driver["name"],
        "primary_drag": primary_drag["name"],
        "standard_reference": "AU-C Section 570 — Going Concern" if z_score < 2.99 else None,
    }


def calculate_beneish_m_score(current: dict, prior: dict) -> dict:
    """
    Beneish M-Score: Detects potential earnings manipulation.
    
    Requires current and prior year financial data.
    M-Score > -1.78 indicates likely manipulation.
    
    Eight variables:
    DSRI — Days Sales in Receivables Index
    GMI  — Gross Margin Index
    AQI  — Asset Quality Index
    SGI  — Sales Growth Index
    DEPI — Depreciation Index
    SGAI — SG&A Expense Index
    LVGI — Leverage Index
    TATA — Total Accruals to Total Assets
    """
    def safe_div(a, b):
        if b is None or b == 0 or a is None:
            return None
        return a / b
    
    # Current year values
    c_rev = current.get("revenue", 0)
    c_ar = current.get("accounts_receivable", 0)
    c_cogs = current.get("cogs", 0)
    c_ta = current.get("total_assets", 0)
    c_ca = current.get("total_current_assets", 0)
    c_ppe = current.get("ppe_net", 0) or (c_ta - c_ca - current.get("intangibles", 0) if current.get("intangibles") else c_ta * 0.4)
    c_dep = current.get("depreciation", 0)
    c_sga = current.get("sga_expense", 0) or (current.get("operating_expenses", 0) - c_dep if current.get("operating_expenses") else 0)
    c_tl = current.get("total_liabilities", 0)
    c_cl = current.get("total_current_liabilities", 0)
    c_ltd = current.get("long_term_debt", 0)
    c_ni = current.get("net_income", 0)
    c_ocf = current.get("operating_cash_flow", 0)
    
    # Prior year values
    p_rev = prior.get("revenue", 0)
    p_ar = prior.get("accounts_receivable", 0)
    p_cogs = prior.get("cogs", 0)
    p_ta = prior.get("total_assets", 0)
    p_ca = prior.get("total_current_assets", 0)
    p_ppe = prior.get("ppe_net", 0) or (p_ta - p_ca - prior.get("intangibles", 0) if prior.get("intangibles") else p_ta * 0.4)
    p_dep = prior.get("depreciation", 0)
    p_sga = prior.get("sga_expense", 0) or (prior.get("operating_expenses", 0) - p_dep if prior.get("operating_expenses") else 0)
    p_tl = prior.get("total_liabilities", 0)
    p_cl = prior.get("total_current_liabilities", 0)
    p_ltd = prior.get("long_term_debt", 0)
    
    # Calculate indices
    # DSRI: Days Sales in Receivables Index
    c_dsr = safe_div(c_ar, c_rev)
    p_dsr = safe_div(p_ar, p_rev)
    dsri = safe_div(c_dsr, p_dsr) if c_dsr and p_dsr else 1.0
    
    # GMI: Gross Margin Index (> 1 means margins declining)
    c_gm = safe_div(c_rev - c_cogs, c_rev) if c_rev else 0
    p_gm = safe_div(p_rev - p_cogs, p_rev) if p_rev else 0
    gmi = safe_div(p_gm, c_gm) if p_gm and c_gm else 1.0
    
    # AQI: Asset Quality Index
    c_aq = 1 - safe_div(c_ca + c_ppe, c_ta) if c_ta else 0
    p_aq = 1 - safe_div(p_ca + p_ppe, p_ta) if p_ta else 0
    aqi = safe_div(c_aq, p_aq) if p_aq and p_aq != 0 else 1.0
    
    # SGI: Sales Growth Index
    sgi = safe_div(c_rev, p_rev) if p_rev else 1.0
    
    # DEPI: Depreciation Index (> 1 means slowing depreciation)
    c_dep_rate = safe_div(c_dep, c_dep + c_ppe) if (c_dep + c_ppe) > 0 else 0
    p_dep_rate = safe_div(p_dep, p_dep + p_ppe) if (p_dep + p_ppe) > 0 else 0
    depi = safe_div(p_dep_rate, c_dep_rate) if c_dep_rate and c_dep_rate != 0 else 1.0
    
    # SGAI: SG&A Expense Index
    c_sga_ratio = safe_div(c_sga, c_rev) if c_rev else 0
    p_sga_ratio = safe_div(p_sga, p_rev) if p_rev else 0
    sgai = safe_div(c_sga_ratio, p_sga_ratio) if p_sga_ratio and p_sga_ratio != 0 else 1.0
    
    # LVGI: Leverage Index
    c_lev = safe_div(c_tl, c_ta) if c_ta else 0
    p_lev = safe_div(p_tl, p_ta) if p_ta else 0
    lvgi = safe_div(c_lev, p_lev) if p_lev and p_lev != 0 else 1.0
    
    # TATA: Total Accruals to Total Assets
    tata = safe_div(c_ni - c_ocf, c_ta) if c_ta else 0
    
    # M-Score calculation
    m_score = (
        -4.84
        + 0.920 * (dsri or 1)
        + 0.528 * (gmi or 1)
        + 0.404 * (aqi or 1)
        + 0.892 * (sgi or 1)
        + 0.115 * (depi or 1)
        - 0.172 * (sgai or 1)
        + 4.679 * (tata or 0)
        - 0.327 * (lvgi or 1)
    )
    
    # Classification
    if m_score > -1.78:
        classification = "Likely Manipulator"
        class_color = "#E74C3C"
        class_desc = ("M-Score exceeds -1.78 threshold, indicating a high probability of earnings manipulation. "
                      "Per SAS 99 (AU-C Section 240), the auditor should consider fraud risk factors including "
                      "pressure to meet earnings targets, opportunity through weak controls, and management "
                      "rationalization. Examine the specific variables driving the score.")
    else:
        classification = "Unlikely Manipulator"
        class_color = "#27AE60"
        class_desc = "M-Score is below -1.78 threshold. No quantitative indication of earnings manipulation."
    
    variables = [
        {"name": "Days Sales in Receivables Index (DSRI)", "value": dsri, "coefficient": 0.920,
         "contribution": 0.920 * (dsri or 1),
         "flag": dsri and dsri > 1.465,
         "interpretation": "DSRI > 1.465 suggests disproportionate receivables growth vs. revenue. "
                          "May indicate inflated revenue through premature recognition (ASC 606 consideration) "
                          "or loosened credit terms to boost sales."},
        {"name": "Gross Margin Index (GMI)", "value": gmi, "coefficient": 0.528,
         "contribution": 0.528 * (gmi or 1),
         "flag": gmi and gmi > 1.193,
         "interpretation": "GMI > 1.193 means gross margins are deteriorating, which creates "
                          "pressure on management to manipulate earnings to maintain appearance of profitability."},
        {"name": "Asset Quality Index (AQI)", "value": aqi, "coefficient": 0.404,
         "contribution": 0.404 * (aqi or 1),
         "flag": aqi and aqi > 1.254,
         "interpretation": "AQI > 1.254 indicates increased capitalization of costs or growth in intangible assets. "
                          "May signal aggressive capitalization policies that defer expense recognition."},
        {"name": "Sales Growth Index (SGI)", "value": sgi, "coefficient": 0.892,
         "contribution": 0.892 * (sgi or 1),
         "flag": sgi and sgi > 1.607,
         "interpretation": "SGI > 1.607 signals rapid growth, which historically correlates with higher manipulation "
                          "risk as companies face pressure to maintain growth trajectories."},
        {"name": "Depreciation Index (DEPI)", "value": depi, "coefficient": 0.115,
         "contribution": 0.115 * (depi or 1),
         "flag": depi and depi > 1.077,
         "interpretation": "DEPI > 1.077 means the company is slowing its depreciation rate, potentially "
                          "extending useful lives to reduce expenses. Review depreciation policy changes."},
        {"name": "SG&A Expense Index (SGAI)", "value": sgai, "coefficient": -0.172,
         "contribution": -0.172 * (sgai or 1),
         "flag": sgai and sgai > 1.041,
         "interpretation": "SGAI > 1.041 indicates SG&A costs are growing faster than revenue, "
                          "suggesting declining operational efficiency."},
        {"name": "Total Accruals / Total Assets (TATA)", "value": tata, "coefficient": 4.679,
         "contribution": 4.679 * (tata or 0),
         "flag": tata and tata > 0.018,
         "interpretation": "TATA > 0.018 means earnings significantly exceed cash flows. High accruals "
                          "are a primary manipulation indicator — cash earnings divergence warrants investigation."},
        {"name": "Leverage Index (LVGI)", "value": lvgi, "coefficient": -0.327,
         "contribution": -0.327 * (lvgi or 1),
         "flag": lvgi and lvgi > 1.111,
         "interpretation": "LVGI > 1.111 indicates increasing leverage, which may create pressure "
                          "to manage earnings to comply with debt covenants."},
    ]
    
    flagged_variables = [v for v in variables if v["flag"]]
    
    return {
        "m_score": m_score,
        "classification": classification,
        "class_color": class_color,
        "class_description": class_desc,
        "variables": variables,
        "flagged_variables": flagged_variables,
        "n_flags": len(flagged_variables),
        "standard_reference": "SAS 99 / AU-C Section 240 — Consideration of Fraud" if m_score > -1.78 else None,
    }


def calculate_piotroski_f_score(current: dict, prior: dict) -> dict:
    """
    Piotroski F-Score: Nine-point financial strength assessment.
    
    Profitability (4 points):
    F1: Net Income > 0
    F2: Operating Cash Flow > 0
    F3: ROA improved (current > prior)
    F4: Cash flow > Net Income (earnings quality)
    
    Leverage & Liquidity (3 points):
    F5: Long-term debt ratio decreased
    F6: Current ratio improved
    F7: No new share issuance (shares outstanding same or decreased)
    
    Operating Efficiency (2 points):
    F8: Gross margin improved
    F9: Asset turnover improved
    
    Score: 0-3 Weak | 4-6 Moderate | 7-9 Strong
    """
    scores = []
    
    # ── Profitability ──
    c_ni = current.get("net_income", 0) or 0
    f1 = 1 if c_ni > 0 else 0
    scores.append({
        "id": "F1", "name": "Positive Net Income", "category": "Profitability",
        "score": f1, "value": c_ni,
        "detail": f"Net Income: ${c_ni:,.0f}" + (" ✓" if f1 else " — Company is unprofitable"),
    })
    
    c_ocf = current.get("operating_cash_flow", 0) or 0
    f2 = 1 if c_ocf > 0 else 0
    scores.append({
        "id": "F2", "name": "Positive Operating Cash Flow", "category": "Profitability",
        "score": f2, "value": c_ocf,
        "detail": f"Operating Cash Flow: ${c_ocf:,.0f}" + (" ✓" if f2 else " — Negative cash from operations"),
    })
    
    c_ta = current.get("total_assets", 1) or 1
    p_ta = prior.get("total_assets", 1) or 1
    c_roa = c_ni / c_ta
    p_ni = prior.get("net_income", 0) or 0
    p_roa = p_ni / p_ta
    f3 = 1 if c_roa > p_roa else 0
    scores.append({
        "id": "F3", "name": "ROA Improvement", "category": "Profitability",
        "score": f3, "value": c_roa - p_roa,
        "detail": f"ROA: {c_roa:.2%} vs prior {p_roa:.2%}" + (" ✓ Improved" if f3 else " — Declined"),
    })
    
    f4 = 1 if c_ocf > c_ni else 0
    scores.append({
        "id": "F4", "name": "Earnings Quality (OCF > NI)", "category": "Profitability",
        "score": f4, "value": c_ocf - c_ni,
        "detail": f"OCF (${c_ocf:,.0f}) {'exceeds' if f4 else 'is below'} Net Income (${c_ni:,.0f})"
                  + (" ✓ Strong earnings quality" if f4 else " — Accrual-driven earnings, quality concern"),
    })
    
    # ── Leverage & Liquidity ──
    c_ltd = current.get("long_term_debt", 0) or 0
    p_ltd = prior.get("long_term_debt", 0) or 0
    c_ltd_ratio = c_ltd / c_ta
    p_ltd_ratio = p_ltd / p_ta
    f5 = 1 if c_ltd_ratio <= p_ltd_ratio else 0
    scores.append({
        "id": "F5", "name": "Decreased Leverage", "category": "Leverage & Liquidity",
        "score": f5, "value": c_ltd_ratio - p_ltd_ratio,
        "detail": f"LT Debt/Assets: {c_ltd_ratio:.2%} vs prior {p_ltd_ratio:.2%}"
                  + (" ✓ Deleveraging" if f5 else " — Leverage increasing"),
    })
    
    c_cl = current.get("total_current_liabilities", 1) or 1
    p_cl = prior.get("total_current_liabilities", 1) or 1
    c_ca = current.get("total_current_assets", 0) or 0
    p_ca = prior.get("total_current_assets", 0) or 0
    c_cr = c_ca / c_cl
    p_cr = p_ca / p_cl
    f6 = 1 if c_cr > p_cr else 0
    scores.append({
        "id": "F6", "name": "Improved Liquidity", "category": "Leverage & Liquidity",
        "score": f6, "value": c_cr - p_cr,
        "detail": f"Current Ratio: {c_cr:.2f} vs prior {p_cr:.2f}"
                  + (" ✓ Improved" if f6 else " — Deteriorated"),
    })
    
    c_shares = current.get("shares_outstanding", 0) or 0
    p_shares = prior.get("shares_outstanding", 0) or 0
    f7 = 1 if c_shares <= p_shares else 0
    scores.append({
        "id": "F7", "name": "No Dilution", "category": "Leverage & Liquidity",
        "score": f7, "value": c_shares - p_shares,
        "detail": f"Shares: {c_shares:,.0f} vs prior {p_shares:,.0f}"
                  + (" ✓ No dilution" if f7 else " — New shares issued (dilutive)"),
    })
    
    # ── Operating Efficiency ──
    c_rev = current.get("revenue", 0) or 0
    p_rev = prior.get("revenue", 0) or 0
    c_cogs = current.get("cogs", 0) or 0
    p_cogs = prior.get("cogs", 0) or 0
    c_gm = (c_rev - c_cogs) / c_rev if c_rev else 0
    p_gm = (p_rev - p_cogs) / p_rev if p_rev else 0
    f8 = 1 if c_gm > p_gm else 0
    scores.append({
        "id": "F8", "name": "Gross Margin Improvement", "category": "Operating Efficiency",
        "score": f8, "value": c_gm - p_gm,
        "detail": f"Gross Margin: {c_gm:.2%} vs prior {p_gm:.2%}"
                  + (" ✓ Improved" if f8 else " — Declined"),
    })
    
    c_at = c_rev / c_ta if c_ta else 0
    p_at = p_rev / p_ta if p_ta else 0
    f9 = 1 if c_at > p_at else 0
    scores.append({
        "id": "F9", "name": "Asset Turnover Improvement", "category": "Operating Efficiency",
        "score": f9, "value": c_at - p_at,
        "detail": f"Asset Turnover: {c_at:.2f}x vs prior {p_at:.2f}x"
                  + (" ✓ More efficient" if f9 else " — Less efficient"),
    })
    
    total = sum(s["score"] for s in scores)
    
    if total >= 7:
        classification = "Strong"
        class_color = "#27AE60"
        class_desc = "Score of 7-9 indicates robust financial health with improving fundamentals across profitability, leverage, and efficiency."
    elif total >= 4:
        classification = "Moderate"
        class_color = "#F39C12"
        class_desc = "Score of 4-6 shows mixed signals. Some areas are improving while others are deteriorating. Examine failing criteria for specific concerns."
    else:
        classification = "Weak"
        class_color = "#E74C3C"
        class_desc = ("Score of 0-3 indicates fundamental weakness across multiple dimensions. "
                      "The company is showing deterioration in profitability, increasing leverage, or declining efficiency. "
                      "Combined with a low Altman Z-Score, this would significantly strengthen a going concern conclusion.")
    
    return {
        "f_score": total,
        "max_score": 9,
        "classification": classification,
        "class_color": class_color,
        "class_description": class_desc,
        "criteria": scores,
        "category_scores": {
            "Profitability": sum(s["score"] for s in scores if s["category"] == "Profitability"),
            "Leverage & Liquidity": sum(s["score"] for s in scores if s["category"] == "Leverage & Liquidity"),
            "Operating Efficiency": sum(s["score"] for s in scores if s["category"] == "Operating Efficiency"),
        },
        "category_max": {
            "Profitability": 4,
            "Leverage & Liquidity": 3,
            "Operating Efficiency": 2,
        }
    }


def integrated_risk_assessment(z_result: dict, m_result: dict, f_result: dict) -> dict:
    """
    Consolidate all three risk models into an integrated assessment
    with overall risk rating and specific action items.
    """
    flags = []
    risk_level = "Low"
    risk_color = "#27AE60"
    
    # Z-Score assessment
    z = z_result.get("z_score", 0)
    if z < 1.81:
        flags.append({
            "model": "Altman Z-Score",
            "severity": "critical",
            "finding": f"Z-Score of {z:.2f} places the company in the Distress Zone.",
            "standard": "AU-C Section 570 — Going Concern",
            "action": "Evaluate management's plans to address financial distress. Assess ability to "
                      "obtain financing, restructure debt, or dispose of assets. Consider the adequacy "
                      "of going concern disclosures.",
        })
        risk_level = "High"
        risk_color = "#E74C3C"
    elif z < 2.99:
        flags.append({
            "model": "Altman Z-Score",
            "severity": "warning",
            "finding": f"Z-Score of {z:.2f} places the company in the Grey Zone.",
            "standard": "AU-C Section 570 — Going Concern",
            "action": "Monitor trends in working capital, profitability, and debt service capacity. "
                      "No immediate going concern conclusion, but heightened attention is warranted.",
        })
        if risk_level != "High":
            risk_level = "Moderate"
            risk_color = "#F39C12"
    
    # M-Score assessment
    m = m_result.get("m_score", -3)
    if m > -1.78:
        n_flags = m_result.get("n_flags", 0)
        flagged = [v["name"] for v in m_result.get("flagged_variables", [])]
        flags.append({
            "model": "Beneish M-Score",
            "severity": "critical",
            "finding": f"M-Score of {m:.2f} exceeds -1.78 threshold with {n_flags} variable(s) flagged: {', '.join(flagged[:3])}.",
            "standard": "SAS 99 / AU-C Section 240 — Consideration of Fraud",
            "action": "Increase professional skepticism regarding revenue recognition and expense timing. "
                      "Consider additional substantive testing on flagged areas. "
                      "Evaluate internal controls over financial reporting.",
        })
        risk_level = "High"
        risk_color = "#E74C3C"
    
    # F-Score assessment
    f = f_result.get("f_score", 5)
    if f <= 3:
        weak_categories = [cat for cat, score in f_result.get("category_scores", {}).items()
                          if score <= f_result.get("category_max", {}).get(cat, 1) * 0.33]
        flags.append({
            "model": "Piotroski F-Score",
            "severity": "warning",
            "finding": f"F-Score of {f}/9 indicates weak and deteriorating financial health." +
                       (f" Particular weakness in: {', '.join(weak_categories)}." if weak_categories else ""),
            "standard": "Professional judgment — trend analysis",
            "action": "The declining trajectory reinforces other risk indicators. "
                      "Evaluate whether deterioration is accelerating and assess implications "
                      "for future period forecasts and going concern analysis.",
        })
        if risk_level != "High":
            risk_level = "Moderate"
            risk_color = "#F39C12"
    
    # Cross-model insights
    cross_insights = []
    if z < 2.99 and f <= 3:
        cross_insights.append(
            "Both the Z-Score (distress/grey zone) and F-Score (weak/declining) converge on financial deterioration. "
            "This dual signal significantly strengthens the case for going concern evaluation under AU-C 570."
        )
    if m > -1.78 and z < 2.99:
        cross_insights.append(
            "The combination of manipulation risk (M-Score) and financial distress (Z-Score) is particularly concerning. "
            "Companies under financial pressure face increased incentive to manipulate earnings — a key SAS 99 fraud risk factor."
        )
    if f >= 7 and z > 2.99:
        cross_insights.append(
            "Both the Z-Score (safe zone) and F-Score (strong) indicate healthy financials with positive momentum. "
            "No elevated risk signals from quantitative models."
        )
    
    # Overall assessment
    if risk_level == "Low" and not flags:
        overall = ("All three quantitative risk models indicate healthy financial standing. "
                   "No elevated risk of bankruptcy, manipulation, or fundamental deterioration detected. "
                   "Standard audit procedures are appropriate.")
    elif risk_level == "Moderate":
        overall = ("Mixed risk signals detected. While not in immediate distress, one or more models "
                   "indicate areas requiring heightened attention. Review specific flags and consider "
                   "expanding substantive testing in identified risk areas.")
    else:
        overall = ("Significant risk indicators detected across quantitative models. "
                   "Professional judgment is required to assess the cumulative impact of these findings. "
                   "Consider expanding audit scope, increasing substantive testing, and evaluating "
                   "going concern and fraud risk implications.")
    
    return {
        "risk_level": risk_level,
        "risk_color": risk_color,
        "overall_assessment": overall,
        "flags": flags,
        "cross_insights": cross_insights,
        "scores_summary": {
            "z_score": {"value": z, "zone": z_result.get("zone", "N/A")},
            "m_score": {"value": m, "classification": m_result.get("classification", "N/A")},
            "f_score": {"value": f, "classification": f_result.get("classification", "N/A")},
        }
    }
