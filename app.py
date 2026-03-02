"""
Financial Health Assessment & Valuation Tool
ACG6415: AI in Accounting — AUDIT Project
Built with Streamlit | Category 3: Analytical Tools & Visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.ratios import calculate_all_ratios, assess_health, get_cross_ratio_insights
from utils.dcf import calculate_wacc, run_dcf, sensitivity_analysis, run_scenarios, validate_assumptions
from utils.risk_models import (
    calculate_altman_z_score, calculate_beneish_m_score,
    calculate_piotroski_f_score, integrated_risk_assessment
)
from data.sample_data import SAMPLE_COMPANIES, INDUSTRY_BENCHMARKS, get_percentile

# ══════════════════════════════════════════════════════════════════════════════
# APP CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Financial Health Assessment Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; }
    .risk-critical { background-color: #fdedec; padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c; margin: 10px 0; }
    .risk-warning { background-color: #fef9e7; padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12; margin: 10px 0; }
    .risk-good { background-color: #eafaf1; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60; margin: 10px 0; }
    .insight-box { padding: 15px; border-radius: 8px; margin: 10px 0; }
    div[data-testid="stSidebar"] { background-color: #1b4f72; }
    div[data-testid="stSidebar"] .stMarkdown p { color: white; }
    div[data-testid="stSidebar"] .stMarkdown h1 { color: white; }
    div[data-testid="stSidebar"] .stMarkdown h2 { color: #d4e6f1; }
    div[data-testid="stSidebar"] .stMarkdown h3 { color: #d4e6f1; }
</style>
""", unsafe_allow_html=True)

INDUSTRIES = list(INDUSTRY_BENCHMARKS.keys())

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
if "financial_data" not in st.session_state:
    st.session_state.financial_data = None
if "prior_data" not in st.session_state:
    st.session_state.prior_data = None
if "industry" not in st.session_state:
    st.session_state.industry = INDUSTRIES[0]
if "ratios" not in st.session_state:
    st.session_state.ratios = None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📊 Financial Health Tool")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Data Input", "📈 Ratio Dashboard", "🎯 Benchmarking",
         "💰 DCF Valuation", "⚠️ Risk Assessment", "📋 Executive Report"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("### Quick Load")
    sample = st.selectbox("Load sample company:", ["— Select —"] + list(SAMPLE_COMPANIES.keys()))
    if sample != "— Select —":
        company = SAMPLE_COMPANIES[sample]
        st.session_state.financial_data = company["current"]
        st.session_state.prior_data = company["prior"]
        st.session_state.industry = company["industry"]
        st.success(f"Loaded: {sample}")

    st.markdown("---")
    st.markdown("*ACG6415 — AUDIT Project*")


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def format_number(val, is_dollar=False, is_percentage=False):
    """Format numbers for display."""
    if val is None:
        return "N/A"
    if is_dollar:
        if abs(val) >= 1_000_000_000:
            return f"${val / 1_000_000_000:,.1f}B"
        elif abs(val) >= 1_000_000:
            return f"${val / 1_000_000:,.1f}M"
        else:
            return f"${val:,.0f}"
    if is_percentage:
        return f"{val:.1%}"
    if abs(val) >= 1000:
        return f"{val:,.1f}"
    return f"{val:.2f}"


def make_gauge(value, title, min_val=0, max_val=5, thresholds=None):
    """Create a Plotly gauge chart."""
    if value is None:
        return go.Figure()
    
    if thresholds is None:
        thresholds = {"red": max_val * 0.3, "yellow": max_val * 0.6}
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        number={"font": {"size": 24}},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "bar": {"color": "#1b4f72"},
            "steps": [
                {"range": [min_val, thresholds.get("red", max_val * 0.3)], "color": "#fadbd8"},
                {"range": [thresholds.get("red", max_val * 0.3), thresholds.get("yellow", max_val * 0.6)], "color": "#fef9e7"},
                {"range": [thresholds.get("yellow", max_val * 0.6), max_val], "color": "#d5f5e3"},
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: DATA INPUT
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Data Input":
    st.title("📊 Financial Data Input")
    st.markdown("Upload financial statements or enter data manually. You can also load a sample company from the sidebar.")
    
    st.session_state.industry = st.selectbox("Select Industry for Benchmarking:", INDUSTRIES, 
                                              index=INDUSTRIES.index(st.session_state.industry))
    
    tab1, tab2 = st.tabs(["📁 Upload File", "✏️ Manual Entry"])
    
    with tab1:
        st.markdown("Upload a CSV or Excel file with financial statement data.")
        uploaded = st.file_uploader("Upload Financial Data", type=["csv", "xlsx"])
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)
                st.dataframe(df, use_container_width=True)
                st.info("Map your columns to the required fields below, or use manual entry for more control.")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with tab2:
        st.markdown("### Current Year Financial Statements")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Balance Sheet**")
            ca = st.number_input("Total Current Assets", value=0, step=1000000, key="ca")
            cl = st.number_input("Total Current Liabilities", value=0, step=1000000, key="cl")
            ta = st.number_input("Total Assets", value=0, step=1000000, key="ta")
            tl = st.number_input("Total Liabilities", value=0, step=1000000, key="tl")
            te = st.number_input("Total Equity", value=0, step=1000000, key="te")
            cash = st.number_input("Cash & Equivalents", value=0, step=1000000, key="cash")
            inv = st.number_input("Inventory", value=0, step=1000000, key="inv")
            ar = st.number_input("Accounts Receivable", value=0, step=1000000, key="ar")
            ap = st.number_input("Accounts Payable", value=0, step=1000000, key="ap")
            ltd = st.number_input("Long-Term Debt", value=0, step=1000000, key="ltd")
            re = st.number_input("Retained Earnings", value=0, step=1000000, key="re")
            mcap = st.number_input("Market Capitalization", value=0, step=1000000, key="mcap")
        
        with col2:
            st.markdown("**Income Statement**")
            rev = st.number_input("Revenue", value=0, step=1000000, key="rev")
            cogs = st.number_input("Cost of Goods Sold", value=0, step=1000000, key="cogs")
            opex = st.number_input("Operating Expenses (excl. COGS)", value=0, step=1000000, key="opex")
            ebit_val = st.number_input("EBIT / Operating Income", value=0, step=1000000, key="ebit")
            intexp = st.number_input("Interest Expense", value=0, step=1000000, key="intexp")
            taxexp = st.number_input("Tax Expense", value=0, step=1000000, key="taxexp")
            ni = st.number_input("Net Income", value=0, step=1000000, key="ni")
            dep = st.number_input("Depreciation & Amortization", value=0, step=1000000, key="dep")
        
        with col3:
            st.markdown("**Cash Flow Statement**")
            ocf = st.number_input("Operating Cash Flow", value=0, step=1000000, key="ocf")
            capex_val = st.number_input("Capital Expenditures", value=0, step=1000000, key="capex")
            
            st.markdown("**Other**")
            shares = st.number_input("Shares Outstanding", value=0, step=1000000, key="shares")
        
        if st.button("💾 Save Current Year Data", type="primary"):
            st.session_state.financial_data = {
                "total_current_assets": ca, "total_current_liabilities": cl,
                "total_assets": ta, "total_liabilities": tl, "total_equity": te,
                "cash": cash, "inventory": inv, "accounts_receivable": ar,
                "accounts_payable": ap, "long_term_debt": ltd, "retained_earnings": re,
                "market_cap": mcap, "revenue": rev, "cogs": cogs,
                "operating_expenses": opex, "operating_income": ebit_val, "ebit": ebit_val,
                "interest_expense": intexp, "tax_expense": taxexp, "net_income": ni,
                "depreciation": dep, "operating_cash_flow": ocf,
                "capital_expenditures": capex_val, "shares_outstanding": shares,
            }
            st.success("✅ Current year data saved. Navigate to the Ratio Dashboard to see results.")
    
    # Validation
    if st.session_state.financial_data:
        data = st.session_state.financial_data
        st.markdown("---")
        st.markdown("### ✅ Data Validation")
        cols = st.columns(3)
        
        with cols[0]:
            bs_check = abs((data.get("total_assets", 0) or 0) - (data.get("total_liabilities", 0) or 0) - (data.get("total_equity", 0) or 0))
            if bs_check < 1000:
                st.success("Balance sheet balances ✓")
            elif data.get("total_assets", 0) > 0:
                st.warning(f"Balance sheet imbalance: ${bs_check:,.0f}")
        
        with cols[1]:
            if (data.get("revenue", 0) or 0) > 0:
                st.success("Revenue is positive ✓")
            else:
                st.warning("Revenue is zero or negative")
        
        with cols[2]:
            if data.get("total_assets", 0) and data.get("total_assets") > 0:
                st.success("Total assets populated ✓")
            else:
                st.error("Total assets required for analysis")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: RATIO DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Ratio Dashboard":
    st.title("📈 Ratio Analysis Dashboard")
    
    if not st.session_state.financial_data:
        st.warning("⚠️ No financial data loaded. Go to Data Input to enter data or load a sample company.")
        st.stop()
    
    data = st.session_state.financial_data
    industry = st.session_state.industry
    ratios = calculate_all_ratios(data)
    st.session_state.ratios = ratios
    
    st.markdown(f"**Industry Context:** {industry}")
    
    # Group ratios by category
    categories = {}
    for key, ratio in ratios.items():
        cat = ratio.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((key, ratio))
    
    # Display each category
    for cat_name in ["Liquidity", "Profitability", "Solvency", "Efficiency", "DuPont Decomposition", "Earnings Quality"]:
        if cat_name not in categories:
            continue
        
        st.markdown(f"### {cat_name}")
        cat_ratios = categories[cat_name]
        cols = st.columns(min(len(cat_ratios), 4))
        
        for i, (key, ratio) in enumerate(cat_ratios):
            col = cols[i % len(cols)]
            val = ratio.get("value")
            health = assess_health(key, val, industry)
            
            with col:
                display_val = format_number(
                    val,
                    is_dollar=ratio.get("is_dollar", False),
                    is_percentage=ratio.get("is_percentage", False),
                )
                st.metric(
                    label=f"{health['emoji']} {ratio['name']}",
                    value=display_val,
                    help=f"{ratio['formula']}\n\n{ratio['description']}\n\nStatus: {health['commentary']}",
                )
        st.markdown("---")
    
    # DuPont Decomposition visualization
    st.markdown("### DuPont Decomposition: What Drives ROE?")
    roe_val = ratios.get("roe", {}).get("value")
    margin_val = ratios.get("dupont_margin", {}).get("value")
    turnover_val = ratios.get("dupont_turnover", {}).get("value")
    leverage_val = ratios.get("dupont_leverage", {}).get("value")
    
    if all(v is not None for v in [roe_val, margin_val, turnover_val, leverage_val]):
        fig = go.Figure(go.Bar(
            x=["Net Profit Margin", "Asset Turnover", "Equity Multiplier", "= ROE"],
            y=[margin_val, turnover_val, leverage_val, roe_val],
            marker_color=["#3498DB", "#2ECC71", "#E74C3C", "#1B4F72"],
            text=[f"{margin_val:.1%}", f"{turnover_val:.2f}x", f"{leverage_val:.2f}x", f"{roe_val:.1%}"],
            textposition="outside",
        ))
        fig.update_layout(
            title="DuPont Three-Factor Decomposition",
            yaxis_title="Value",
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpret the primary driver
        components = {"Profit Margin": abs(margin_val), "Asset Turnover": abs(turnover_val) / 3, "Leverage": abs(leverage_val) / 5}
        primary = max(components, key=components.get)
        if primary == "Leverage" and leverage_val > 2.5:
            st.warning(f"⚠️ **ROE is primarily driven by financial leverage** (equity multiplier: {leverage_val:.2f}x). "
                       "High-leverage ROE amplifies both returns and risk. A decline in earnings could quickly erode equity.")
        elif primary == "Profit Margin":
            st.success(f"✅ **ROE is driven by profitability** (net margin: {margin_val:.1%}). "
                       "This represents sustainable, high-quality returns.")
    
    # Cross-ratio insights
    insights = get_cross_ratio_insights(ratios, industry)
    if insights:
        st.markdown("### 🔍 Cross-Ratio Professional Insights")
        for insight in insights:
            css_class = {"critical": "risk-critical", "warning": "risk-warning", "positive": "risk-good"}.get(insight["type"], "insight-box")
            st.markdown(f'<div class="{css_class}"><strong>{insight["title"]}</strong><br>{insight["detail"]}</div>',
                       unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Benchmarking":
    st.title("🎯 Industry Benchmarking")
    
    if not st.session_state.financial_data:
        st.warning("⚠️ No financial data loaded. Go to Data Input first.")
        st.stop()
    
    data = st.session_state.financial_data
    industry = st.session_state.industry
    ratios = calculate_all_ratios(data)
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, {})
    
    if not benchmarks:
        st.error(f"No benchmark data available for {industry}.")
        st.stop()
    
    st.markdown(f"**Comparing against:** {industry} industry medians")
    
    # Radar Chart
    st.markdown("### Radar Chart: Company vs. Industry Median")
    radar_keys = ["current_ratio", "gross_margin", "operating_margin", "roa", "roe",
                  "debt_to_equity", "interest_coverage", "asset_turnover"]
    radar_labels = [ratios[k]["name"] for k in radar_keys if k in ratios]
    
    company_vals = []
    median_vals = []
    valid_labels = []
    for k in radar_keys:
        v = ratios.get(k, {}).get("value")
        bm = benchmarks.get(k, {}).get("median")
        if v is not None and bm is not None and bm != 0:
            # Normalize: company value as % of median
            company_vals.append(v / bm * 100)
            median_vals.append(100)
            valid_labels.append(ratios[k]["name"])
    
    if valid_labels:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=company_vals + [company_vals[0]],
            theta=valid_labels + [valid_labels[0]],
            fill="toself", name="Company",
            fillcolor="rgba(27, 79, 114, 0.2)",
            line=dict(color="#1B4F72"),
        ))
        fig.add_trace(go.Scatterpolar(
            r=median_vals + [median_vals[0]],
            theta=valid_labels + [valid_labels[0]],
            fill="toself", name="Industry Median",
            fillcolor="rgba(46, 204, 113, 0.1)",
            line=dict(color="#27AE60", dash="dash"),
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(company_vals + [150])])),
            title="Company Ratios as % of Industry Median (100% = Median)",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Percentile Rankings
    st.markdown("### Percentile Rankings")
    ranking_data = []
    for key in radar_keys + ["dso", "cash_conversion_cycle", "net_margin", "roic"]:
        val = ratios.get(key, {}).get("value")
        bm = benchmarks.get(key, {})
        if val is not None and bm:
            pctl = get_percentile(val, bm)
            is_pct = ratios.get(key, {}).get("is_percentage", False)
            ranking_data.append({
                "Ratio": ratios[key]["name"],
                "Company Value": format_number(val, is_percentage=is_pct),
                "Industry Median": format_number(bm.get("median"), is_percentage=is_pct) if bm.get("median") else "N/A",
                "Percentile": pctl,
            })
    
    if ranking_data:
        df = pd.DataFrame(ranking_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Strengths and Weaknesses
    st.markdown("### 💪 Strengths & Weaknesses vs. Peers")
    above = []
    below = []
    for key in benchmarks:
        val = ratios.get(key, {}).get("value")
        med = benchmarks[key].get("median")
        if val is not None and med is not None and med != 0:
            pct_diff = (val - med) / abs(med)
            # For ratios where lower is better (D/E, DSO, CCC), flip the sign
            if key in ["debt_to_equity", "debt_to_assets", "dso", "cash_conversion_cycle"]:
                pct_diff = -pct_diff
            if pct_diff > 0.1:
                above.append((ratios[key]["name"], pct_diff))
            elif pct_diff < -0.1:
                below.append((ratios[key]["name"], pct_diff))
    
    above.sort(key=lambda x: x[1], reverse=True)
    below.sort(key=lambda x: x[1])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🟢 Strengths (Above Median)**")
        for name, diff in above[:5]:
            st.markdown(f"- **{name}**: {diff:+.0%} vs. median")
        if not above:
            st.markdown("_No ratios significantly above industry median._")
    
    with col2:
        st.markdown("**🔴 Weaknesses (Below Median)**")
        for name, diff in below[:5]:
            st.markdown(f"- **{name}**: {diff:+.0%} vs. median")
        if not below:
            st.markdown("_No ratios significantly below industry median._")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: DCF VALUATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 DCF Valuation":
    st.title("💰 DCF Valuation Engine")
    
    if not st.session_state.financial_data:
        st.warning("⚠️ No financial data loaded. Go to Data Input first.")
        st.stop()
    
    data = st.session_state.financial_data
    
    # Load defaults from sample company if available
    defaults = {}
    for comp in SAMPLE_COMPANIES.values():
        if comp["current"] == data:
            defaults = comp.get("dcf_defaults", {})
            break
    
    base_rev = data.get("revenue", 1_000_000_000)
    
    st.markdown("### WACC Build-Up")
    wcol1, wcol2, wcol3 = st.columns(3)
    with wcol1:
        rfr = st.number_input("Risk-Free Rate (%)", value=defaults.get("risk_free_rate", 0.043) * 100, step=0.1, format="%.2f") / 100
        erp = st.number_input("Equity Risk Premium (%)", value=defaults.get("equity_risk_premium", 0.055) * 100, step=0.1, format="%.2f") / 100
        beta = st.number_input("Beta", value=defaults.get("beta", 1.0), step=0.05, format="%.2f")
    with wcol2:
        cod = st.number_input("Pre-Tax Cost of Debt (%)", value=defaults.get("cost_of_debt", 0.055) * 100, step=0.1, format="%.2f") / 100
        tax_r = st.number_input("Tax Rate (%)", value=defaults.get("tax_rate", 0.21) * 100, step=1.0, format="%.1f") / 100
    with wcol3:
        eq_w = st.number_input("Equity Weight (%)", value=defaults.get("equity_weight", 0.80) * 100, step=1.0, format="%.0f") / 100
        debt_w = 1 - eq_w
        st.metric("Debt Weight", f"{debt_w:.0%}")
    
    wacc_result = calculate_wacc(rfr, erp, beta, cod, tax_r, eq_w, debt_w)
    st.info(f"**WACC: {wacc_result['wacc']:.2%}** | Cost of Equity: {wacc_result['cost_of_equity']:.2%} | After-Tax Cost of Debt: {wacc_result['after_tax_cost_of_debt']:.2%}")
    
    st.markdown("---")
    st.markdown("### Projection Assumptions")
    
    n_years = 5
    st.markdown("**Revenue Growth Rates by Year:**")
    gcols = st.columns(n_years)
    growth_rates = []
    for i in range(n_years):
        default_gr = defaults.get("revenue_growth_rates", [0.10, 0.08, 0.06, 0.05, 0.04])
        with gcols[i]:
            gr = st.number_input(f"Yr {i+1} (%)", value=default_gr[i] * 100 if i < len(default_gr) else 5.0,
                                step=0.5, format="%.1f", key=f"gr_{i}") / 100
            growth_rates.append(gr)
    
    st.markdown("**EBITDA Margins by Year:**")
    mcols = st.columns(n_years)
    margins = []
    for i in range(n_years):
        default_m = defaults.get("ebitda_margins", [0.20, 0.21, 0.22, 0.23, 0.24])
        with mcols[i]:
            m = st.number_input(f"Yr {i+1} (%)", value=default_m[i] * 100 if i < len(default_m) else 20.0,
                               step=0.5, format="%.1f", key=f"m_{i}") / 100
            margins.append(m)
    
    acol1, acol2, acol3, acol4 = st.columns(4)
    with acol1:
        capex_pct = st.number_input("CapEx (% of Revenue)", value=defaults.get("capex_pct", 0.05) * 100, step=0.5, format="%.1f") / 100
    with acol2:
        nwc_pct = st.number_input("NWC Change (% of Rev Change)", value=defaults.get("nwc_change_pct", 0.10) * 100, step=1.0, format="%.0f") / 100
    with acol3:
        da_pct = st.number_input("D&A (% of Revenue)", value=defaults.get("da_pct", 0.05) * 100, step=0.5, format="%.1f") / 100
    with acol4:
        tgr = st.number_input("Terminal Growth Rate (%)", value=defaults.get("terminal_growth_rate", 0.025) * 100, step=0.1, format="%.2f") / 100
    
    shares_out = data.get("shares_outstanding", defaults.get("shares_outstanding", 100_000_000))
    net_debt_val = defaults.get("net_debt", (data.get("long_term_debt", 0) or 0) - (data.get("cash", 0) or 0))
    
    # Assumption validation
    assumptions = {
        "terminal_growth_rate": tgr, "risk_free_rate": rfr,
        "revenue_growth_rates": growth_rates, "ebitda_margins": margins, "wacc": wacc_result["wacc"],
    }
    warnings = validate_assumptions(assumptions)
    for w in warnings:
        if w["severity"] == "critical":
            st.error(f"⚠️ **{w['field']}:** {w['message']}")
        else:
            st.warning(f"⚡ **{w['field']}:** {w['message']}")
    
    st.markdown("---")
    
    # Run base case DCF
    dcf_result = run_dcf(base_rev, growth_rates, margins, capex_pct, nwc_pct, da_pct,
                         wacc_result["wacc"], tgr, shares_out, net_debt_val)
    
    # Key outputs
    st.markdown("### Valuation Output")
    ocol1, ocol2, ocol3, ocol4 = st.columns(4)
    ocol1.metric("Enterprise Value", format_number(dcf_result["enterprise_value"], is_dollar=True))
    ocol2.metric("Equity Value", format_number(dcf_result["equity_value"], is_dollar=True))
    ocol3.metric("Per Share Value", f"${dcf_result['per_share_value']:,.2f}" if dcf_result["per_share_value"] else "N/A")
    ocol4.metric("Terminal Value % of EV", f"{dcf_result['tv_pct_of_ev']:.0%}",
                 help="High TV% means valuation depends heavily on long-term assumptions. Above 70% warrants caution.")
    
    if dcf_result["tv_pct_of_ev"] > 0.75:
        st.warning("⚠️ Terminal value accounts for over 75% of enterprise value. "
                   "The valuation is highly sensitive to terminal growth and WACC assumptions. "
                   "Review the sensitivity analysis below carefully.")
    
    # Waterfall chart
    st.markdown("### Value Decomposition")
    decomp = dcf_result["decomposition"]
    fig = go.Figure(go.Waterfall(
        name="", orientation="v",
        measure=["relative"] * (len(decomp) - 1) + ["total"] if len(decomp) > 1 else ["total"],
        x=[d["label"] for d in decomp] + ["Enterprise Value"],
        y=[d["value"] for d in decomp] + [dcf_result["enterprise_value"]],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#27AE60"}},
        totals={"marker": {"color": "#1B4F72"}},
    ))
    # Fix: waterfall needs proper measures
    fig = go.Figure(go.Bar(
        x=[d["label"] for d in decomp],
        y=[d["value"] for d in decomp],
        marker_color=["#3498DB"] * (len(decomp) - 1) + ["#E74C3C"],
        text=[f"${d['value']/1e6:,.0f}M ({d['pct_of_ev']:.0%})" for d in decomp],
        textposition="outside",
    ))
    fig.update_layout(title="Enterprise Value Composition", yaxis_title="Present Value ($)", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Sensitivity Analysis
    st.markdown("### Sensitivity Analysis: WACC vs. Terminal Growth Rate")
    sens = sensitivity_analysis(base_rev, growth_rates, margins, capex_pct, nwc_pct, da_pct,
                                wacc_result["wacc"], tgr, shares_out, net_debt_val)
    
    # Build heatmap
    z_data = []
    for row in sens["ev_matrix"]:
        z_data.append([v / 1e6 if v else None for v in row])
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=[f"{t:.1%}" for t in sens["tgr_values"]],
        y=[f"{w:.1%}" for w in sens["wacc_values"]],
        colorscale="RdYlGn",
        text=[[f"${v:,.0f}M" if v else "N/A" for v in row] for row in z_data],
        texttemplate="%{text}",
        hovertemplate="WACC: %{y}<br>TGR: %{x}<br>EV: %{text}<extra></extra>",
    ))
    fig.update_layout(
        title="Enterprise Value Sensitivity ($M)",
        xaxis_title="Terminal Growth Rate",
        yaxis_title="WACC",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Projection table
    st.markdown("### Projection Detail")
    proj_df = pd.DataFrame(dcf_result["projections"])
    display_cols = {
        "year": "Year", "revenue": "Revenue", "revenue_growth": "Growth",
        "ebitda": "EBITDA", "ebitda_margin": "Margin",
        "fcf": "Free Cash Flow", "pv_fcf": "PV of FCF"
    }
    proj_display = proj_df[list(display_cols.keys())].rename(columns=display_cols)
    for col in ["Revenue", "EBITDA", "Free Cash Flow", "PV of FCF"]:
        proj_display[col] = proj_display[col].apply(lambda x: f"${x/1e6:,.1f}M")
    proj_display["Growth"] = proj_display["Growth"].apply(lambda x: f"{float(x.replace('$','').replace('M','')) if isinstance(x, str) else x:.1%}" if not isinstance(x, str) else x)
    proj_display["Margin"] = proj_display["Margin"].apply(lambda x: f"{float(x.replace('$','').replace('M','')) if isinstance(x, str) else x:.1%}" if not isinstance(x, str) else x)
    # Fix formatting
    proj_display2 = pd.DataFrame(dcf_result["projections"])
    st.dataframe(proj_display2[["year", "revenue", "revenue_growth", "ebitda", "ebitda_margin", "fcf", "pv_fcf"]].style.format({
        "revenue": "${:,.0f}", "revenue_growth": "{:.1%}", "ebitda": "${:,.0f}",
        "ebitda_margin": "{:.1%}", "fcf": "${:,.0f}", "pv_fcf": "${:,.0f}",
    }), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: RISK ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Risk Assessment":
    st.title("⚠️ Risk Assessment & Professional Judgment")
    
    if not st.session_state.financial_data:
        st.warning("⚠️ No financial data loaded. Go to Data Input first.")
        st.stop()
    
    data = st.session_state.financial_data
    prior = st.session_state.prior_data
    
    if not prior:
        st.warning("⚠️ Prior year data is required for M-Score and F-Score. Load a sample company to see full risk analysis.")
    
    # ── Altman Z-Score ──
    st.markdown("### 📊 Altman Z-Score — Bankruptcy Prediction")
    z_result = calculate_altman_z_score(data)
    
    if "error" not in z_result:
        zcol1, zcol2 = st.columns([1, 2])
        with zcol1:
            st.metric("Z-Score", f"{z_result['z_score']:.2f}")
            st.markdown(f"**Zone:** <span style='color:{z_result['zone_color']};font-weight:bold;'>{z_result['zone']}</span>",
                       unsafe_allow_html=True)
            st.markdown(z_result["zone_description"])
            if z_result.get("standard_reference"):
                st.info(f"📖 **Standard:** {z_result['standard_reference']}")
        
        with zcol2:
            comp_df = pd.DataFrame(z_result["components"])
            fig = go.Figure(go.Bar(
                x=[c["variable"] for c in z_result["components"]],
                y=[c["weighted"] for c in z_result["components"]],
                marker_color=["#27AE60" if c["weighted"] > 0 else "#E74C3C" for c in z_result["components"]],
                text=[f"{c['weighted']:.3f}" for c in z_result["components"]],
                textposition="outside",
            ))
            fig.update_layout(title="Z-Score Component Contributions", yaxis_title="Weighted Value", height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Component detail
        with st.expander("View Component Details"):
            for c in z_result["components"]:
                st.markdown(f"**{c['name']}**: Raw = {c['raw']:.4f} × {c['coefficient']} = {c['weighted']:.4f}")
                st.markdown(f"_{c['interpretation']}_")
                st.markdown("---")
    
    # ── Beneish M-Score ──
    if prior:
        st.markdown("---")
        st.markdown("### 🔍 Beneish M-Score — Earnings Manipulation Detection")
        m_result = calculate_beneish_m_score(data, prior)
        
        mcol1, mcol2 = st.columns([1, 2])
        with mcol1:
            st.metric("M-Score", f"{m_result['m_score']:.2f}")
            st.markdown(f"**Classification:** <span style='color:{m_result['class_color']};font-weight:bold;'>{m_result['classification']}</span>",
                       unsafe_allow_html=True)
            st.markdown(f"**Threshold:** -1.78 | **Variables Flagged:** {m_result['n_flags']}/8")
            st.markdown(m_result["class_description"])
            if m_result.get("standard_reference"):
                st.info(f"📖 **Standard:** {m_result['standard_reference']}")
        
        with mcol2:
            var_names = [v["name"].split("(")[1].rstrip(")") if "(" in v["name"] else v["name"][:10] for v in m_result["variables"]]
            var_vals = [v["value"] or 0 for v in m_result["variables"]]
            var_colors = ["#E74C3C" if v["flag"] else "#3498DB" for v in m_result["variables"]]
            
            fig = go.Figure(go.Bar(
                x=var_names, y=var_vals,
                marker_color=var_colors,
                text=[f"{v:.3f}" if v else "N/A" for v in var_vals],
                textposition="outside",
            ))
            fig.update_layout(title="M-Score Variables (Red = Flagged)", yaxis_title="Index Value", height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Flagged variable details
        if m_result["flagged_variables"]:
            st.markdown("#### 🚩 Flagged Variables — Recommended Investigation Areas")
            for v in m_result["flagged_variables"]:
                st.markdown(f'<div class="risk-critical"><strong>{v["name"]}</strong> = {v["value"]:.3f}<br>{v["interpretation"]}</div>',
                           unsafe_allow_html=True)
    
    # ── Piotroski F-Score ──
    if prior:
        st.markdown("---")
        st.markdown("### 📋 Piotroski F-Score — Financial Strength")
        f_result = calculate_piotroski_f_score(data, prior)
        
        fcol1, fcol2 = st.columns([1, 2])
        with fcol1:
            st.metric("F-Score", f"{f_result['f_score']}/9")
            st.markdown(f"**Classification:** <span style='color:{f_result['class_color']};font-weight:bold;'>{f_result['classification']}</span>",
                       unsafe_allow_html=True)
            st.markdown(f_result["class_description"])
            
            # Category breakdown
            for cat, score in f_result["category_scores"].items():
                max_s = f_result["category_max"][cat]
                st.markdown(f"**{cat}:** {score}/{max_s}")
        
        with fcol2:
            criteria_data = []
            for c in f_result["criteria"]:
                criteria_data.append({
                    "Criteria": c["id"],
                    "Name": c["name"],
                    "Result": "✅ Pass" if c["score"] == 1 else "❌ Fail",
                    "Detail": c["detail"],
                })
            st.dataframe(pd.DataFrame(criteria_data), use_container_width=True, hide_index=True)
    
    # ── Integrated Risk Assessment ──
    if prior:
        st.markdown("---")
        st.markdown("### 🎯 Integrated Risk Assessment")
        
        integrated = integrated_risk_assessment(z_result, m_result, f_result)
        
        # Overall risk level
        risk_css = {"High": "risk-critical", "Moderate": "risk-warning", "Low": "risk-good"}
        css_class = risk_css.get(integrated["risk_level"], "insight-box")
        st.markdown(f'<div class="{css_class}"><h3>Overall Risk Level: {integrated["risk_level"]}</h3>'
                   f'{integrated["overall_assessment"]}</div>', unsafe_allow_html=True)
        
        # Score summary
        scol1, scol2, scol3 = st.columns(3)
        scores = integrated["scores_summary"]
        scol1.metric("Z-Score", f"{scores['z_score']['value']:.2f}", scores['z_score']['zone'])
        scol2.metric("M-Score", f"{scores['m_score']['value']:.2f}", scores['m_score']['classification'])
        scol3.metric("F-Score", f"{scores['f_score']['value']}/9", scores['f_score']['classification'])
        
        # Cross-model insights
        if integrated["cross_insights"]:
            st.markdown("#### Cross-Model Insights")
            for insight in integrated["cross_insights"]:
                st.info(insight)
        
        # Action items
        if integrated["flags"]:
            st.markdown("#### 📋 Specific Findings & Recommended Actions")
            for flag in integrated["flags"]:
                severity_icon = "🔴" if flag["severity"] == "critical" else "🟡"
                st.markdown(f"""
                **{severity_icon} {flag['model']}**: {flag['finding']}
                
                **Standard Reference:** {flag['standard']}
                
                **Recommended Action:** {flag['action']}
                
                ---
                """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6: EXECUTIVE REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Executive Report":
    st.title("📋 Executive Summary Report")
    
    if not st.session_state.financial_data:
        st.warning("⚠️ No financial data loaded. Go to Data Input first.")
        st.stop()
    
    data = st.session_state.financial_data
    prior = st.session_state.prior_data
    industry = st.session_state.industry
    ratios = calculate_all_ratios(data)
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, {})
    
    st.markdown("---")
    st.markdown("## Financial Health Overview")
    
    # Key metrics summary
    st.markdown("### Key Metrics at a Glance")
    kcols = st.columns(5)
    key_ratios = [
        ("current_ratio", False, False),
        ("net_margin", False, True),
        ("roe", False, True),
        ("debt_to_equity", False, False),
        ("interest_coverage", False, False),
    ]
    for i, (key, is_dollar, is_pct) in enumerate(key_ratios):
        r = ratios.get(key, {})
        health = assess_health(key, r.get("value"), industry)
        kcols[i].metric(
            f"{health['emoji']} {r.get('name', key)}",
            format_number(r.get("value"), is_percentage=is_pct),
        )
    
    # Ratio health summary
    st.markdown("### Ratio Health Summary")
    health_counts = {"good": 0, "warning": 0, "critical": 0}
    for key, ratio in ratios.items():
        h = assess_health(key, ratio.get("value"), industry)
        if h["status"] in health_counts:
            health_counts[h["status"]] += 1
    
    hcols = st.columns(3)
    hcols[0].metric("🟢 Healthy", health_counts["good"])
    hcols[1].metric("🟡 Warning", health_counts["warning"])
    hcols[2].metric("🔴 Critical", health_counts["critical"])
    
    # Cross-ratio insights
    insights = get_cross_ratio_insights(ratios, industry)
    if insights:
        st.markdown("### Key Findings")
        for insight in insights:
            icon = {"critical": "🔴", "warning": "🟡", "positive": "🟢"}.get(insight["type"], "🔵")
            st.markdown(f"{icon} **{insight['title']}**: {insight['detail']}")
    
    # Risk scores
    if prior:
        st.markdown("### Risk Assessment Summary")
        z_result = calculate_altman_z_score(data)
        m_result = calculate_beneish_m_score(data, prior)
        f_result = calculate_piotroski_f_score(data, prior)
        integrated = integrated_risk_assessment(z_result, m_result, f_result)
        
        css_class = {"High": "risk-critical", "Moderate": "risk-warning", "Low": "risk-good"}.get(integrated["risk_level"])
        st.markdown(f'<div class="{css_class}"><strong>Overall Risk: {integrated["risk_level"]}</strong> — '
                   f'{integrated["overall_assessment"]}</div>', unsafe_allow_html=True)
        
        if integrated["flags"]:
            st.markdown("**Action Items:**")
            for flag in integrated["flags"]:
                st.markdown(f"- **{flag['model']}**: {flag['finding']} → _{flag['action']}_")
    
    st.markdown("---")
    st.markdown("### Export")
    st.info("📄 PDF export functionality can be added with Claude Code. This is a planned enhancement for the refinement phase.")
    
    st.markdown("---")
    st.caption("Generated by Financial Health Assessment Tool | ACG6415 AUDIT Project | "
               "This tool supports professional judgment — it does not replace it. "
               "All findings should be evaluated by qualified professionals in the context of "
               "the specific engagement and applicable professional standards.")
