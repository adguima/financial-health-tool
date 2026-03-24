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
from datetime import date
from utils.ratios import calculate_all_ratios, assess_health, get_cross_ratio_insights
from utils.dcf import calculate_wacc, run_dcf, sensitivity_analysis, run_scenarios, validate_assumptions
from utils.risk_models import (
    calculate_altman_z_score, calculate_beneish_m_score,
    calculate_piotroski_f_score, integrated_risk_assessment
)
from data.sample_data import (
    SAMPLE_COMPANIES, INDUSTRY_BENCHMARKS, get_percentile,
    COMPANY_SIZES, detect_company_size, get_size_adjusted_benchmarks,
)

# ══════════════════════════════════════════════════════════════════════════════
# APP CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Financial Health Assessment Tool",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, minimal, professional CSS — Aptos font
st.markdown("""
<style>
    html, body, [class*="css"], .stMarkdown, .stButton button,
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
    .stSelectbox, .stRadio, .stTextInput, .stNumberInput {
        font-family: 'Aptos', 'Calibri', 'Segoe UI', -apple-system, sans-serif !important;
    }

    /* Sidebar nav buttons */
    div[data-testid="stSidebar"] .stButton > button {
        width: 100%; text-align: center; padding: 10px 16px; margin: 2px 0;
        border: none !important; border-radius: 6px; background: transparent !important;
        color: #c9c9c9 !important; font-size: 0.9rem; font-weight: 500; cursor: pointer;
        font-family: 'Aptos', 'Calibri', 'Segoe UI', sans-serif !important;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background: #2a2a2a !important; color: #ffffff !important;
    }

    /* Sidebar */
    div[data-testid="stSidebar"] { background-color: #1a1a1a; }
    div[data-testid="stSidebar"] .stMarkdown p { color: #c9c9c9; font-size: 0.9rem; }
    div[data-testid="stSidebar"] .stMarkdown h1 { color: #ffffff; font-weight: 700; letter-spacing: -0.02em; }
    div[data-testid="stSidebar"] .stMarkdown h2 { color: #e0e0e0; font-weight: 600; }
    div[data-testid="stSidebar"] .stMarkdown h3 { color: #b0b0b0; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; }

    /* Metric cards */
    .stMetric {
        background-color: #fafafa;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #e8e8e8;
    }
    [data-testid="stMetricLabel"] { font-weight: 600; color: #333333; font-size: 0.85rem; }
    [data-testid="stMetricValue"] { font-weight: 700; color: #1a1a1a; }

    /* Risk / insight boxes */
    .risk-critical {
        background-color: #fff5f5;
        padding: 16px 20px;
        border-radius: 8px;
        border-left: 3px solid #e74c3c;
        margin: 12px 0;
        font-size: 0.92rem;
    }
    .risk-warning {
        background-color: #fffbf0;
        padding: 16px 20px;
        border-radius: 8px;
        border-left: 3px solid #f5a623;
        margin: 12px 0;
        font-size: 0.92rem;
    }
    .risk-good {
        background-color: #f0faf4;
        padding: 16px 20px;
        border-radius: 8px;
        border-left: 3px solid #00c805;
        margin: 12px 0;
        font-size: 0.92rem;
    }
    .insight-box {
        padding: 16px 20px;
        border-radius: 8px;
        margin: 12px 0;
        background-color: #f8f8f8;
        border: 1px solid #e8e8e8;
        font-size: 0.92rem;
    }

    /* Status indicator dots */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        vertical-align: middle;
    }
    .dot-green { background-color: #00c805; }
    .dot-yellow { background-color: #f5a623; }
    .dot-red { background-color: #e74c3c; }
    .dot-blue { background-color: #5ac8fa; }
    .dot-gray { background-color: #b0b0b0; }

    /* Section headers */
    h1 { font-weight: 700; color: #1a1a1a; letter-spacing: -0.02em; }
    h2 { font-weight: 600; color: #1a1a1a; letter-spacing: -0.01em; }
    h3 { font-weight: 600; color: #333333; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.9rem;
        padding: 10px 24px;
        font-family: 'Aptos', 'Calibri', 'Segoe UI', sans-serif !important;
    }

    /* Dividers */
    hr { border: none; border-top: 1px solid #e8e8e8; margin: 24px 0; }
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
if "company_size" not in st.session_state:
    st.session_state.company_size = COMPANY_SIZES[2]  # default Mid-Cap
if "company_name" not in st.session_state:
    st.session_state.company_name = None
if "load_source" not in st.session_state:
    st.session_state.load_source = None  # "sample" or "manual"
if "current_year_label" not in st.session_state:
    st.session_state.current_year_label = None
if "prior_year_label" not in st.session_state:
    st.session_state.prior_year_label = None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
# ── Page state ──────────────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "Executive Report"

_PAGES = ["Executive Report", "Financial Ratios", "Benchmarking",
          "DCF Valuation", "Risk Assessment", "Data Options"]

with st.sidebar:
    st.markdown("# Financial Health Tool")
    st.markdown("---")

    # ── Loaded Company ──────────────────────────────────────────────────────
    # Show loaded status above the label
    _yr_label = st.session_state.current_year_label or ""
    _yr_line = f"<br><b>Year:</b> {_yr_label}" if _yr_label else ""
    if st.session_state.company_name:
        st.markdown(f'<div style="background:#1e3a1e;color:#00c805;padding:12px 14px;border-radius:6px;'
                    f'font-size:1.25rem;margin:0 0 4px 0;font-weight:700;text-align:left;'
                    f'font-family:Aptos,Calibri,sans-serif;">'
                    f'{st.session_state.company_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#000000;font-size:1rem;margin:0 0 8px 2px;font-family:Aptos,Calibri,sans-serif;">'
                    f'<b>Industry:</b> {st.session_state.industry}<br>'
                    f'<b>Size:</b> {st.session_state.company_size}{_yr_line}</div>', unsafe_allow_html=True)
    elif st.session_state.financial_data is not None:
        st.markdown('<div style="background:#1e3a1e;color:#00c805;padding:12px 14px;border-radius:6px;'
                    'font-size:1.25rem;margin:0 0 4px 0;font-weight:700;text-align:left;'
                    'font-family:Aptos,Calibri,sans-serif;">'
                    'Manually loaded</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#000000;font-size:1rem;margin:0 0 8px 2px;font-family:Aptos,Calibri,sans-serif;">'
                    f'<b>Industry:</b> {st.session_state.industry}<br>'
                    f'<b>Size:</b> {st.session_state.company_size}{_yr_line}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Navigation buttons ──────────────────────────────────────────────────
    for p in _PAGES:
        if p == st.session_state.current_page:
            st.markdown(
                f'<div style="background:#1e3a1e;color:#00c805;padding:10px 16px;margin:0 0 14px 0;'
                f'border-radius:6px;border-left:3px solid #00c805;font-size:1rem;'
                f'text-align:center;font-weight:500;font-family:Aptos,Calibri,Segoe UI,sans-serif;">{p}</div>',
                unsafe_allow_html=True)
        else:
            if st.button(p, key=f"nav_{p}", use_container_width=True):
                st.session_state.current_page = p
                st.rerun()

    st.markdown("---")
    st.markdown("*ACG6415 — AUDIT Project*")

page = st.session_state.current_page


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
        title={"text": title, "font": {"size": 13, "family": "Aptos, Calibri, sans-serif", "color": "#333"}},
        number={"font": {"size": 22, "family": "Aptos, Calibri, sans-serif", "color": "#1a1a1a"}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": "#ccc"},
            "bar": {"color": "#1a1a1a"},
            "steps": [
                {"range": [min_val, thresholds.get("red", max_val * 0.3)], "color": "#fff5f5"},
                {"range": [thresholds.get("red", max_val * 0.3), thresholds.get("yellow", max_val * 0.6)], "color": "#fffbf0"},
                {"range": [thresholds.get("yellow", max_val * 0.6), max_val], "color": "#f0faf4"},
            ],
            "borderwidth": 0,
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10), font=dict(family="Aptos, Calibri, sans-serif"))
    return fig


def _get_industry_peers(industry, exclude_name=None):
    """Return dict of sample companies in the same industry, excluding current."""
    peers = {}
    for name, co in SAMPLE_COMPANIES.items():
        if co["industry"] == industry:
            if exclude_name and exclude_name in name:
                continue
            peers[name] = co
    return peers


def generate_pdf_report(data, prior, industry, ratios, benchmarks, company_name):
    """Generate a professional HTML report (print-to-PDF ready) and return bytes."""

    def _esc(text):
        if text is None:
            return "N/A"
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Key metrics
    key_metrics = [
        ("Current Ratio", "current_ratio", False, False),
        ("Net Margin", "net_margin", False, True),
        ("Return on Equity", "roe", False, True),
        ("Debt-to-Equity", "debt_to_equity", False, False),
        ("Interest Coverage", "interest_coverage", False, False),
    ]
    metrics_rows = ""
    for label, key, is_dollar, is_pct in key_metrics:
        r = ratios.get(key, {})
        val = r.get("value")
        val_fmt = format_number(val, is_dollar=is_dollar, is_percentage=is_pct)
        health = assess_health(key, val, industry)
        status = health.get("status", "unknown").capitalize()
        color = {"Good": "#27AE60", "Warning": "#F39C12", "Critical": "#E74C3C"}.get(status, "#666")
        metrics_rows += f'<tr><td>{_esc(label)}</td><td style="font-weight:600;">{_esc(val_fmt)}</td><td style="color:{color};font-weight:600;">{status}</td></tr>\n'

    # Health counts
    health_counts = {"good": 0, "warning": 0, "critical": 0}
    for key, ratio in ratios.items():
        h = assess_health(key, ratio.get("value"), industry)
        if h["status"] in health_counts:
            health_counts[h["status"]] += 1

    # Key findings
    insights = get_cross_ratio_insights(ratios, industry)
    findings_html = ""
    if insights:
        for insight in insights:
            badge = {"critical": "CRITICAL", "warning": "WARNING", "positive": "POSITIVE"}.get(insight["type"], "")
            badge_color = {"critical": "#E74C3C", "warning": "#F39C12", "positive": "#27AE60"}.get(insight["type"], "#666")
            findings_html += (f'<p><span style="background:{badge_color};color:#fff;padding:2px 6px;border-radius:3px;'
                              f'font-size:0.8em;font-weight:600;">{badge}</span> '
                              f'<strong>{_esc(insight["title"])}</strong>: {_esc(insight["detail"])}</p>\n')

    # Risk assessment
    risk_html = ""
    if prior:
        z_result = calculate_altman_z_score(data)
        m_result = calculate_beneish_m_score(data, prior)
        f_result = calculate_piotroski_f_score(data, prior)
        integrated = integrated_risk_assessment(z_result, m_result, f_result)
        risk_color = {"High": "#E74C3C", "Moderate": "#F39C12", "Low": "#27AE60"}.get(integrated["risk_level"], "#666")

        risk_html = f"""
        <h2>Risk Assessment</h2>
        <table>
            <tr><td>Altman Z-Score</td><td style="font-weight:600;">{z_result['z_score']:.2f}</td><td>{_esc(z_result.get('zone', 'N/A'))}</td></tr>
            <tr><td>Beneish M-Score</td><td style="font-weight:600;">{m_result['m_score']:.2f}</td><td>{_esc(m_result['classification'])}</td></tr>
            <tr><td>Piotroski F-Score</td><td style="font-weight:600;">{f_result['f_score']}/9</td><td>{_esc(f_result['classification'])}</td></tr>
        </table>
        <p style="margin-top:12px;"><strong>Overall Risk Level: </strong>
        <span style="color:{risk_color};font-weight:700;font-size:1.1em;">{_esc(integrated['risk_level'])}</span></p>
        <p>{_esc(integrated['overall_assessment'])}</p>
        """
        if integrated.get("flags"):
            risk_html += "<h3>Action Items</h3><ul>\n"
            for flag in integrated["flags"]:
                risk_html += f'<li><strong>{_esc(flag["model"])}</strong>: {_esc(flag["finding"])} &rarr; <em>{_esc(flag["action"])}</em></li>\n'
            risk_html += "</ul>\n"

    report_date = date.today().strftime("%B %d, %Y")
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Financial Health Report - {_esc(company_name)}</title>
<style>
@media print {{ @page {{ margin: 0.75in; }} body {{ font-size: 10pt; }} }}
body {{ font-family: Aptos, Calibri, Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.6; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; }}
h2 {{ color: #1a1a1a; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
h3 {{ color: #444; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }}
th {{ background: #f8f8f8; font-weight: 600; }}
.header-meta {{ color: #666; font-size: 0.95em; }}
.health-bar {{ display: flex; gap: 24px; margin: 8px 0; }}
.health-bar span {{ padding: 6px 16px; border-radius: 4px; font-weight: 600; }}
.disclaimer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #ddd; font-size: 0.8em; color: #999; font-style: italic; }}
</style></head><body>
<h1>Financial Health Assessment Report</h1>
<p class="header-meta"><strong>Company:</strong> {_esc(company_name or 'N/A')} &nbsp;|&nbsp;
<strong>Industry:</strong> {_esc(industry)} &nbsp;|&nbsp;
<strong>Date:</strong> {report_date}</p>

<h2>Key Metrics</h2>
<table><tr><th>Metric</th><th>Value</th><th>Status</th></tr>
{metrics_rows}</table>

<h2>Ratio Health Summary</h2>
<div class="health-bar">
<span style="background:#eafaf1;color:#27AE60;">Healthy: {health_counts['good']}</span>
<span style="background:#fef9e7;color:#F39C12;">Warning: {health_counts['warning']}</span>
<span style="background:#fdedec;color:#E74C3C;">Critical: {health_counts['critical']}</span>
</div>

<h2>Key Findings</h2>
{findings_html if findings_html else '<p style="color:#999;">No significant findings.</p>'}

{risk_html}

<div class="disclaimer">
This report is generated by the Financial Health Assessment Tool for educational purposes
(ACG6415 AUDIT Project). It supports professional judgment but does not replace it. All findings
should be evaluated by qualified professionals in the context of the specific engagement and
applicable professional standards.
</div>
</body></html>"""

    return html.encode("utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: DATA INPUT
# ══════════════════════════════════════════════════════════════════════════════
if page == "Data Options":
    st.title("Financial Data Input")
    st.markdown("Upload financial statements or enter data manually, or load a sample company below.")

    # ── Load Sample Company ─────────────────────────────────────────────────
    st.markdown("### Load Sample Company")

    _grouped_options = ["— Select —"]
    _seen_industries = []
    for name, comp in SAMPLE_COMPANIES.items():
        ind = comp["industry"]
        if ind not in _seen_industries:
            _seen_industries.append(ind)
    for ind in _seen_industries:
        _grouped_options.append(f"── {ind} ──")
        for name, comp in SAMPLE_COMPANIES.items():
            if comp["industry"] == ind:
                _grouped_options.append(name)

    if "prev_sample" not in st.session_state:
        st.session_state.prev_sample = "— Select —"

    sample = st.selectbox("Sample companies:", _grouped_options,
                          index=_grouped_options.index(st.session_state.prev_sample)
                          if st.session_state.prev_sample in _grouped_options else 0,
                          label_visibility="collapsed")

    if sample and not sample.startswith("—") and not sample.startswith("──"):
        if sample != st.session_state.prev_sample:
            company = SAMPLE_COMPANIES[sample]
            st.session_state.financial_data = company["current"]
            st.session_state.prior_data = company["prior"]
            st.session_state.industry = company["industry"]
            st.session_state.company_name = sample.split("(")[0].strip() if "(" in sample else sample
            st.session_state.load_source = "sample"
            st.session_state.current_year_label = company.get("current_year", "2023")
            st.session_state.prior_year_label = company.get("prior_year", "2022")
            st.session_state.prev_sample = sample
            st.rerun()
    else:
        st.session_state.prev_sample = sample

    # Show year selector if a sample company is loaded
    if st.session_state.load_source == "sample" and st.session_state.prev_sample in SAMPLE_COMPANIES:
        _loaded_co = SAMPLE_COMPANIES[st.session_state.prev_sample]
        _cy = _loaded_co.get("current_year", "2023")
        _py = _loaded_co.get("prior_year", "2022")

        # Track previous year choice to detect changes
        if "prev_year_choice" not in st.session_state:
            st.session_state.prev_year_choice = _cy

        _year_choice = st.radio("Analyze year:", [_cy, _py], horizontal=True, key="sample_year_choice")

        _year_changed = _year_choice != st.session_state.prev_year_choice
        st.session_state.prev_year_choice = _year_choice

        if _year_choice == _py:
            st.session_state.financial_data = _loaded_co["prior"]
            st.session_state.prior_data = _loaded_co["current"]
            st.session_state.current_year_label = _py
            st.session_state.prior_year_label = _cy
        else:
            st.session_state.financial_data = _loaded_co["current"]
            st.session_state.prior_data = _loaded_co["prior"]
            st.session_state.current_year_label = _cy
            st.session_state.prior_year_label = _py

        if _year_changed:
            st.rerun()

    st.markdown("---")

    # ── Manual Upload ────────────────────────────────────────────────────────
    st.markdown("### Load Manual CSV or XLSX File")

    st.session_state.industry = st.selectbox("Select Industry for Benchmarking:", INDUSTRIES,
                                              index=INDUSTRIES.index(st.session_state.industry))

    tab1, tab2 = st.tabs(["Upload File", "Manual Entry"])
    
    with tab1:
        st.markdown("Upload a CSV or Excel file. The file should have a **Field** column and one or more year columns (e.g. 2024, 2023).")
        uploaded = st.file_uploader("Upload Financial Data", type=["csv", "xlsx"])
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)

                # Detect year columns (any 4-digit header)
                year_cols = sorted(
                    [str(c) for c in df.columns if str(c).strip().isdigit() and len(str(c).strip()) == 4],
                    reverse=True,
                )

                if not year_cols or "Field" not in df.columns:
                    st.error("CSV must have a 'Field' column and at least one 4-digit year column (e.g. 2024).")
                    st.dataframe(df, use_container_width=True)
                    st.stop()

                # Year selection dropdowns — default to two most recent
                ycol1, ycol2 = st.columns(2)
                with ycol1:
                    current_year = st.selectbox("Current Year", year_cols, index=0)
                with ycol2:
                    prior_options = [y for y in year_cols if y != current_year]
                    prior_year = st.selectbox(
                        "Prior Year",
                        prior_options,
                        index=0 if prior_options else None,
                        disabled=len(prior_options) == 0,
                    ) if prior_options else None

                # Normalise Field column to lowercase/underscore keys
                df["Field"] = df["Field"].astype(str).str.strip()

                # Build a mapping from CSV field names to internal keys
                FIELD_MAP = {
                    # Accept both human-readable and snake_case forms
                    "total_current_assets": "total_current_assets",
                    "total current assets": "total_current_assets",
                    "total_current_liabilities": "total_current_liabilities",
                    "total current liabilities": "total_current_liabilities",
                    "total_assets": "total_assets",
                    "total assets": "total_assets",
                    "total_liabilities": "total_liabilities",
                    "total liabilities": "total_liabilities",
                    "total_equity": "total_equity",
                    "total equity": "total_equity",
                    "cash": "cash",
                    "cash & equivalents": "cash",
                    "cash and equivalents": "cash",
                    "inventory": "inventory",
                    "accounts_receivable": "accounts_receivable",
                    "accounts receivable": "accounts_receivable",
                    "accounts_payable": "accounts_payable",
                    "accounts payable": "accounts_payable",
                    "long_term_debt": "long_term_debt",
                    "long term debt": "long_term_debt",
                    "retained_earnings": "retained_earnings",
                    "retained earnings": "retained_earnings",
                    "market_cap": "market_cap",
                    "market capitalization": "market_cap",
                    "market cap": "market_cap",
                    "ppe_net": "ppe_net",
                    "ppe net": "ppe_net",
                    "intangibles": "intangibles",
                    "shares_outstanding": "shares_outstanding",
                    "shares outstanding": "shares_outstanding",
                    "revenue": "revenue",
                    "cogs": "cogs",
                    "cost of goods sold": "cogs",
                    "operating_expenses": "operating_expenses",
                    "operating expenses": "operating_expenses",
                    "operating_income": "operating_income",
                    "operating income": "operating_income",
                    "ebit": "ebit",
                    "interest_expense": "interest_expense",
                    "interest expense": "interest_expense",
                    "tax_expense": "tax_expense",
                    "tax expense": "tax_expense",
                    "net_income": "net_income",
                    "net income": "net_income",
                    "depreciation": "depreciation",
                    "depreciation & amortization": "depreciation",
                    "sga_expense": "sga_expense",
                    "sga expense": "sga_expense",
                    "operating_cash_flow": "operating_cash_flow",
                    "operating cash flow": "operating_cash_flow",
                    "capital_expenditures": "capital_expenditures",
                    "capital expenditures": "capital_expenditures",
                    "capex": "capital_expenditures",
                }

                def _parse_year(dataframe, year_col):
                    """Parse a single year column into a financial_data dict."""
                    result = {}
                    for _, row in dataframe.iterrows():
                        field_raw = str(row["Field"]).strip().lower()
                        key = FIELD_MAP.get(field_raw)
                        if key:
                            result[key] = pd.to_numeric(row[year_col], errors="coerce") or 0
                    # Ensure ebit mirrors operating_income if only one was provided
                    if "operating_income" in result and "ebit" not in result:
                        result["ebit"] = result["operating_income"]
                    elif "ebit" in result and "operating_income" not in result:
                        result["operating_income"] = result["ebit"]
                    return result

                # Parse current and prior year
                current_data = _parse_year(df, current_year)
                prior_data = _parse_year(df, prior_year) if prior_year else None

                # ── Industry selector ──
                # Auto-detect from CSV row if present
                csv_industry = None
                industry_row = df[df["Field"].str.strip().str.lower() == "industry"]
                if not industry_row.empty:
                    ind_value = str(industry_row.iloc[0][current_year]).strip()
                    if ind_value and ind_value.lower() != "nan" and ind_value in INDUSTRIES:
                        csv_industry = ind_value

                default_ind_idx = INDUSTRIES.index(csv_industry) if csv_industry else 0
                upload_industry = st.selectbox(
                    "Industry",
                    INDUSTRIES,
                    index=default_ind_idx,
                    key="upload_industry",
                )

                # ── Company Size selector ──
                # Auto-detect from CSV row, else from revenue
                csv_size = None
                size_row = df[df["Field"].str.strip().str.lower() == "company_size"]
                if not size_row.empty:
                    size_val = str(size_row.iloc[0][current_year]).strip()
                    if size_val and size_val.lower() != "nan" and size_val in COMPANY_SIZES:
                        csv_size = size_val

                if csv_size:
                    detected_size = csv_size
                else:
                    rev = current_data.get("revenue", 0) or 0
                    detected_size = detect_company_size(rev)

                default_size_idx = COMPANY_SIZES.index(detected_size)
                upload_size = st.selectbox(
                    "Company Size",
                    COMPANY_SIZES,
                    index=default_size_idx,
                    key="upload_size",
                )

                # Check for a company name row
                csv_company_name = None
                name_row = df[df["Field"].str.strip().str.lower().isin(["company_name", "company name", "company"])]
                if not name_row.empty:
                    name_val = str(name_row.iloc[0][current_year]).strip()
                    if name_val and name_val.lower() != "nan":
                        csv_company_name = name_val

                if st.button("Load Uploaded Data", type="primary"):
                    st.session_state.financial_data = current_data
                    st.session_state.prior_data = prior_data
                    st.session_state.industry = upload_industry
                    st.session_state.company_size = upload_size
                    # Extract company name: prefer CSV field, then filename
                    # Supports: "TICKER - Company Name.csv", "CompanyName_Ticker.csv"
                    _file_label = uploaded.name.rsplit(".", 1)[0]
                    if not csv_company_name:
                        if " - " in _file_label:
                            # "AAPL - Apple Inc" → keep as-is
                            csv_company_name = _file_label
                        elif "_" in _file_label:
                            # "AppleInc_AAPL" → "AAPL - AppleInc"
                            parts = _file_label.rsplit("_", 1)
                            csv_company_name = f"{parts[1]} - {parts[0]}" if len(parts) == 2 else _file_label
                        else:
                            csv_company_name = _file_label
                    st.session_state.company_name = csv_company_name
                    st.session_state.load_source = "manual"
                    st.session_state.current_year_label = current_year
                    st.session_state.prior_year_label = prior_year
                    st.session_state.prev_sample = "— Select —"
                    st.rerun()

                # Summary preview
                st.markdown("### Data Preview")
                preview_rows = []
                all_keys = list(dict.fromkeys(list(current_data.keys()) + (list(prior_data.keys()) if prior_data else [])))
                for k in all_keys:
                    row_data = {"Field": k, current_year: current_data.get(k, "")}
                    if prior_data:
                        row_data[prior_year] = prior_data.get(k, "")
                    preview_rows.append(row_data)
                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

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
        
        if st.button("Save Current Year Data", type="primary"):
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
            st.session_state.load_source = "manual"
            st.session_state.company_name = "Manual Entry"
            st.session_state.prev_sample = "— Select —"
            st.rerun()
    
    # ── File Format Guide ─────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("CSV / XLSX File Format Guide", expanded=False):
        st.markdown("""
Your file must contain a **Field** column and one or more **year columns** (4-digit headers like `2024`, `2023`).

**Required structure:**

| Field | 2024 | 2023 |
|---|---|---|
| Revenue | 50000000 | 45000000 |
| COGS | 30000000 | 27000000 |
| ... | ... | ... |

**Accepted field names** (case-insensitive; spaces or underscores both work):

| Category | Fields |
|---|---|
| **Balance Sheet** | Total Current Assets, Total Current Liabilities, Total Assets, Total Liabilities, Total Equity, Cash (or Cash & Equivalents), Inventory, Accounts Receivable, Accounts Payable, Long Term Debt, Retained Earnings, PPE Net, Intangibles |
| **Income Statement** | Revenue, COGS (or Cost of Goods Sold), Operating Expenses, Operating Income, EBIT, Interest Expense, Tax Expense, Net Income, Depreciation (or Depreciation & Amortization), SGA Expense |
| **Cash Flow** | Operating Cash Flow, Capital Expenditures (or Capex) |
| **Market Data** | Market Cap (or Market Capitalization), Shares Outstanding |

**Optional metadata rows** (auto-detected from the file):

| Field | Value |
|---|---|
| Industry | Technology, Healthcare, etc. |
| Company Size | Large Cap, Mid Cap, Small Cap |
| Company Name | Your Company Inc. |

**File naming conventions:**

The company name is auto-detected from the file name (unless a `Company Name` metadata row is provided). Supported formats:

| File Name | Detected Company Name |
|---|---|
| `AAPL - Apple Inc.csv` | AAPL - Apple Inc |
| `AppleInc_AAPL.xlsx` | AAPL - AppleInc |
| `MyCompany.csv` | MyCompany |

**Tips:**
- Enter values as plain numbers (no `$` signs or commas in the data cells).
- Include at least two year columns to enable trend / prior-year comparisons.
- At minimum, provide **Total Assets**, **Total Liabilities**, **Total Equity**, and **Revenue** for a meaningful analysis.
""")

    # Validation
    if st.session_state.financial_data:
        data = st.session_state.financial_data
        st.markdown("---")
        st.markdown("### Data Validation")
        cols = st.columns(3)
        
        with cols[0]:
            bs_check = abs((data.get("total_assets", 0) or 0) - (data.get("total_liabilities", 0) or 0) - (data.get("total_equity", 0) or 0))
            if bs_check < 1000:
                st.success("Balance sheet balances")
            elif data.get("total_assets", 0) > 0:
                st.warning(f"Balance sheet imbalance: ${bs_check:,.0f}")
        
        with cols[1]:
            if (data.get("revenue", 0) or 0) > 0:
                st.success("Revenue is positive")
            else:
                st.warning("Revenue is zero or negative")
        
        with cols[2]:
            if data.get("total_assets", 0) and data.get("total_assets") > 0:
                st.success("Total assets populated")
            else:
                st.error("Total assets required for analysis")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: RATIO DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Financial Ratios":
    st.title("Financial Ratio Analysis")
    if not st.session_state.financial_data:
        st.warning("No financial data loaded. Go to Data Options to enter data or load a sample company.")
        st.stop()

    data = st.session_state.financial_data
    prior = st.session_state.prior_data
    industry = st.session_state.industry
    company_size = st.session_state.company_size
    ratios = calculate_all_ratios(data)
    prior_ratios = calculate_all_ratios(prior) if prior else {}
    st.session_state.ratios = ratios
    benchmarks = get_size_adjusted_benchmarks(industry, company_size)

    # ── Compare mode selector ─────────────────────────────────────────────
    _compare_mode = st.radio("Compare against:", ["Industry Median", "Industry Peer"],
                             horizontal=True, key="ratio_compare_mode")

    peer_ratios = None
    peer_label = None
    if _compare_mode != "Industry Median":
        _peers = _get_industry_peers(industry, exclude_name=st.session_state.company_name)
        _peer_names = ["None"] + list(_peers.keys())
        _selected_peer = st.selectbox("Industry peer:", _peer_names, key="ratio_peer")
        if _selected_peer != "None" and _selected_peer in _peers:
            # Match peer's year to the year being analyzed
            _peer_co = _peers[_selected_peer]
            _analyzing_year = st.session_state.current_year_label
            _peer_cy = _peer_co.get("current_year", "2023")
            _peer_py = _peer_co.get("prior_year", "2022")
            if _analyzing_year == _peer_py:
                _peer_data = _peer_co["prior"]
            else:
                _peer_data = _peer_co["current"]
            peer_ratios = calculate_all_ratios(_peer_data)
            peer_label = _selected_peer.split("(")[0].strip()
    else:
        # Industry Mean mode: show median values as the "peer" column
        peer_ratios = {}
        for k, bm in benchmarks.items():
            med = bm.get("median")
            if med is not None:
                peer_ratios[k] = {"value": med}
        peer_label = "Industry Median"

    # ── Overall Financial Health Summary ──────────────────────────────────
    st.markdown("### Overall Financial Health Summary")

    def _generate_health_summary(ratios, industry, company_size, co_name):
        """Build a 3-4 sentence narrative summary from calculated ratios."""
        _v = lambda k: ratios.get(k, {}).get("value")
        cr = _v("current_ratio")
        npm = _v("net_margin")
        roe = _v("roe")
        dte = _v("debt_to_equity")
        ic = _v("interest_coverage")
        at = _v("asset_turnover")
        ocf_ni = _v("ocf_to_ni")
        name = co_name or "The company"

        parts = []

        # Sentence 1: Overall positioning
        if npm is not None and npm > 0.08 and cr is not None and cr > 1.2:
            parts.append(f"{name} demonstrates a solid financial position within the {industry} sector ({company_size}), "
                         f"with positive profitability (net margin: {npm:.1%}) and adequate short-term liquidity (current ratio: {cr:.2f}).")
        elif npm is not None and npm < 0:
            parts.append(f"{name} is operating at a loss within the {industry} sector ({company_size}), "
                         f"with a net margin of {npm:.1%}, raising questions about the sustainability of current operations.")
        else:
            _npm_str = f"{npm:.1%}" if npm is not None else "N/A"
            _cr_str = f"{cr:.2f}" if cr is not None else "N/A"
            parts.append(f"{name} shows a mixed financial profile within the {industry} sector ({company_size}), "
                         f"with a net margin of {_npm_str} and current ratio of {_cr_str}.")

        # Sentence 2: Capital structure & solvency
        if dte is not None and ic is not None:
            if dte > 2.0 and ic < 3.0:
                parts.append(f"The capital structure is heavily leveraged (D/E: {dte:.2f}) with limited debt service "
                             f"capacity (interest coverage: {ic:.1f}x), which may constrain financial flexibility.")
            elif dte < 1.0 and ic > 5.0:
                parts.append(f"The balance sheet is conservatively leveraged (D/E: {dte:.2f}) with strong debt service "
                             f"capacity (interest coverage: {ic:.1f}x), providing financial flexibility.")
            else:
                parts.append(f"Leverage sits at {dte:.2f}x debt-to-equity with {ic:.1f}x interest coverage, "
                             f"indicating {'manageable' if ic > 2.0 else 'tight'} debt servicing capacity.")
        elif dte is not None:
            parts.append(f"The debt-to-equity ratio of {dte:.2f} {'warrants monitoring' if dte > 1.5 else 'reflects moderate leverage'}.")

        # Sentence 3: Operational efficiency
        if roe is not None and at is not None:
            parts.append(f"Return on equity of {roe:.1%} combined with asset turnover of {at:.2f}x "
                         f"{'suggests efficient capital deployment' if roe > 0.10 and at > 0.5 else 'indicates room for operational improvement'}.")

        # Sentence 4: Earnings quality
        if ocf_ni is not None:
            if ocf_ni > 1.0:
                parts.append("Cash flow generation exceeds reported earnings, supporting earnings quality.")
            elif 0 < ocf_ni < 0.8:
                parts.append(f"Operating cash flow covers only {ocf_ni:.0%} of net income, suggesting accrual-driven "
                             "earnings that may warrant closer scrutiny.")

        return " ".join(parts) if parts else "Insufficient data to generate a financial health summary."

    _summary_text = _generate_health_summary(ratios, industry, company_size, st.session_state.company_name)

    # Determine overall health color from key ratios
    _s_npm = ratios.get("net_margin", {}).get("value")
    _s_cr = ratios.get("current_ratio", {}).get("value")
    _s_ic = ratios.get("interest_coverage", {}).get("value")
    _s_score = 0
    if _s_npm is not None:
        _s_score += (1 if _s_npm > 0.05 else -1 if _s_npm < 0 else 0)
    if _s_cr is not None:
        _s_score += (1 if _s_cr > 1.2 else -1 if _s_cr < 0.8 else 0)
    if _s_ic is not None:
        _s_score += (1 if _s_ic > 3.0 else -1 if _s_ic < 1.5 else 0)
    if _s_score >= 2:
        _sum_bg, _sum_border = "#f0faf4", "#27AE60"  # green
    elif _s_score <= -1:
        _sum_bg, _sum_border = "#fff5f5", "#E74C3C"  # red
    else:
        _sum_bg, _sum_border = "#fffbf0", "#F39C12"  # amber

    st.markdown(f'<div style="background-color:{_sum_bg};border-left:4px solid {_sum_border};padding:16px 20px;'
                f'border-radius:4px;font-size:0.95em;line-height:1.6;color:#333;">{_summary_text}</div>',
                unsafe_allow_html=True)

    # ── Helper: render a single ratio row ─────────────────────────────────
    _lower_is_better = {"debt_to_equity", "debt_to_assets", "dso", "cash_conversion_cycle",
                        "equity_multiplier", "lt_debt_ratio", "accruals_ratio"}

    def _render_ratio_row(key, ratio, ratios, prior_ratios, peer_ratios, benchmarks, industry):
        val = ratio.get("value")
        is_pct = ratio.get("is_percentage", False)
        is_dollar = ratio.get("is_dollar", False)
        display_val = format_number(val, is_dollar=is_dollar, is_percentage=is_pct)
        health = assess_health(key, val, industry)

        # Build the row using columns
        c_name, c_val, c_peer = st.columns([3, 2, 2])

        with c_name:
            _status_color = {"good": "#27AE60", "warning": "#F39C12", "critical": "#E74C3C"}.get(health["status"], "#95A5A6")
            _status_note = health.get("commentary", "")
            st.markdown(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
                        f'background:{_status_color};margin-right:6px;vertical-align:middle;"'
                        f' title="{_status_note}"></span>'
                        f'**{ratio["name"]}**'
                        f'<br><span style="font-size:0.75em;color:{_status_color};font-style:italic;">{_status_note}</span>',
                        unsafe_allow_html=True)

        with c_val:
            st.markdown(f'<span style="font-size:1.15em;font-weight:600;color:#00c805;">{display_val}</span>',
                        unsafe_allow_html=True)

        with c_peer:
            if peer_ratios and key in peer_ratios:
                _pv = peer_ratios[key].get("value")
                if _pv is not None:
                    _pfmt = format_number(_pv, is_dollar=is_dollar, is_percentage=is_pct)
                    st.markdown(f'<span style="color:#1a1a1a;font-weight:500;">{_pfmt}</span>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color:#ccc;">--</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#ccc;">--</span>', unsafe_allow_html=True)

        # Contextual interpretation line
        _interp = _build_ratio_interpretation(key, val, ratio, industry, benchmarks)
        if _interp:
            st.markdown(f'<div style="font-size:0.82em;color:#666;margin:-8px 0 6px 14px;line-height:1.4;">{_interp}</div>',
                        unsafe_allow_html=True)

    def _build_ratio_interpretation(key, val, ratio, industry, benchmarks):
        """One-sentence contextual interpretation referencing industry."""
        if val is None:
            return None
        bm = benchmarks.get(key, {})
        med = bm.get("median")
        ind_short = industry.split("/")[0].strip() if "/" in industry else industry

        _interps = {
            "current_ratio": lambda: (
                f"At {val:.2f}x, short-term coverage is {'strong' if val > 1.5 else 'adequate' if val > 1.0 else 'thin'} "
                f"relative to the {ind_short} median of {med:.2f}." if med else
                f"At {val:.2f}x, the company {'can comfortably' if val > 1.5 else 'may struggle to'} meet short-term obligations."
            ),
            "quick_ratio": lambda: (
                f"Excluding inventory, the company holds {val:.2f}x liquid assets per dollar of current liabilities"
                f"{f', versus {med:.2f} for {ind_short} peers' if med else ''}."
            ),
            "cash_ratio": lambda: (
                f"Cash alone covers {val:.0%} of current liabilities — {'a strong liquidity cushion' if val > 0.5 else 'limited immediate liquidity'}."
            ),
            "working_capital": lambda: (
                f"{'Positive' if val > 0 else 'Negative'} working capital of {format_number(val, is_dollar=True)} "
                f"{'provides a buffer' if val > 0 else 'signals reliance on short-term financing'} for operations."
            ),
            "ocf_ratio": lambda: (
                f"Operations generate {val:.2f}x current liabilities in cash flow — "
                f"{'comfortably self-funding' if val > 0.5 else 'tight cash generation from operations'}."
            ),
            "gross_margin": lambda: (
                f"Retaining {val:.1%} of revenue after direct costs "
                f"{'outpaces' if med and val > med else 'trails'} the {ind_short} median{f' of {med:.1%}' if med else ''}."
            ),
            "operating_margin": lambda: (
                f"Core operations {'generate' if val > 0 else 'consume'} {abs(val):.1%} per revenue dollar"
                f"{f', compared to {med:.1%} for {ind_short} peers' if med else ''}."
            ),
            "net_margin": lambda: (
                f"Bottom-line profitability of {val:.1%} "
                f"{'exceeds' if med and val > med else 'falls below'} the {ind_short} median{f' of {med:.1%}' if med else ''}."
            ),
            "roa": lambda: (
                f"Each dollar of assets generates {val:.1%} in net income — "
                f"{'efficient' if med and val > med else 'below-average'} asset utilization for {ind_short}."
            ),
            "roe": lambda: (
                f"Shareholders earn {val:.1%} return on equity"
                f"{f', versus {med:.1%} for {ind_short} peers' if med else ''}. "
                f"{'Review DuPont decomposition to assess quality of returns.' if abs(val) > 0.15 else ''}"
            ),
            "roic": lambda: (
                f"Return on invested capital of {val:.1%} {'exceeds' if val > 0.08 else 'is below'} "
                f"typical cost of capital, {'creating' if val > 0.08 else 'potentially destroying'} shareholder value."
            ),
            "debt_to_equity": lambda: (
                f"Total liabilities are {val:.2f}x equity — "
                f"{'conservative' if val < 1.0 else 'moderate' if val < 2.0 else 'aggressive'} leverage "
                f"for the {ind_short} sector{f' (median: {med:.2f})' if med else ''}."
            ),
            "debt_to_assets": lambda: (
                f"{'More' if val > 0.5 else 'Less'} than half of assets are debt-financed ({val:.1%})"
                f"{f', versus {med:.1%} for {ind_short} peers' if med else ''}."
            ),
            "interest_coverage": lambda: (
                f"EBIT covers interest payments {val:.1f}x — "
                f"{'comfortable' if val > 3 else 'adequate' if val > 1.5 else 'precarious; covenant risk'}"
                f" for {ind_short}."
            ),
            "equity_multiplier": lambda: (
                f"Financial leverage of {val:.2f}x amplifies both returns and risk."
            ),
            "lt_debt_ratio": lambda: (
                f"Long-term debt represents {val:.1%} of total assets."
            ),
            "asset_turnover": lambda: (
                f"Generating ${val:.2f} in revenue per dollar of assets"
                f"{f', versus ${med:.2f} for {ind_short} peers' if med else ''}."
            ),
            "inventory_turnover": lambda: (
                f"Inventory turns over {val:.1f}x annually — "
                f"{'efficient' if val > 8 else 'adequate' if val > 4 else 'slow; potential obsolescence risk'}."
            ),
            "receivables_turnover": lambda: (
                f"Receivables collected {val:.1f}x per year. "
                f"{'Efficient collection cycle.' if val > 8 else 'Monitor aging of receivables.'}"
            ),
            "dso": lambda: (
                f"Average {val:.0f} days to collect payment"
                f"{f', versus {med:.0f} days for {ind_short} peers' if med else ''}. "
                f"{'Within normal range.' if med and val <= med * 1.2 else 'Elevated; review credit policies.'}"
            ),
            "cash_conversion_cycle": lambda: (
                f"Cash cycle of {val:.0f} days from payment to collection"
                f"{f' (industry median: {med:.0f})' if med else ''}. "
                f"{'Efficient working capital management.' if val < 50 else 'Significant capital tied up in operations.'}"
            ),
            "accruals_ratio": lambda: (
                f"Accruals ratio of {val:.1%} {'is low, supporting earnings quality' if abs(val) < 0.03 else 'is elevated, suggesting earnings may not be fully cash-backed'}."
            ),
            "ocf_to_ni": lambda: (
                f"Operating cash flow is {val:.2f}x net income — "
                f"{'strong cash backing of reported earnings' if val > 1.0 else 'earnings outpace cash generation, a quality concern'}."
            ),
        }
        fn = _interps.get(key)
        if fn:
            try:
                return fn()
            except Exception:
                return None
        return None

    # ── Category insight generators ───────────────────────────────────────
    def _category_insight(cat_name, ratios, benchmarks, industry):
        """Generate a 2-3 sentence analytical finding for a ratio category."""
        _v = lambda k: ratios.get(k, {}).get("value")
        ind_short = industry.split("/")[0].strip() if "/" in industry else industry

        if cat_name == "Liquidity":
            cr, qr, cash_r, ocf_r = _v("current_ratio"), _v("quick_ratio"), _v("cash_ratio"), _v("ocf_ratio")
            ccc = _v("cash_conversion_cycle")
            parts = []
            if cr is not None and qr is not None:
                gap = cr - qr
                if gap > 0.5:
                    parts.append(f"The gap between current ratio ({cr:.2f}) and quick ratio ({qr:.2f}) indicates "
                                 f"significant inventory reliance for short-term coverage.")
                elif cr > 1.5:
                    parts.append(f"Both current ({cr:.2f}) and quick ({qr:.2f}) ratios indicate solid liquidity.")
                else:
                    parts.append(f"Current ratio of {cr:.2f} suggests {'tight' if cr < 1.0 else 'modest'} liquidity.")
            if cash_r is not None:
                if cash_r < 0.15:
                    parts.append(f"The cash ratio of {cash_r:.2f} indicates limited immediate liquidity; "
                                 "the company depends on receivable collections and/or asset conversion to meet obligations.")
                elif cash_r > 0.5:
                    parts.append(f"Cash alone covers {cash_r:.0%} of current liabilities, providing a strong liquidity buffer.")
            if ccc is not None and ccc > 60:
                parts.append(f"A cash conversion cycle of {ccc:.0f} days means significant capital is tied up between "
                             "paying suppliers and collecting from customers.")
            return " ".join(parts[:3]) if parts else None

        if cat_name == "Profitability":
            gm, om, nm, roe_v, roa_v = _v("gross_margin"), _v("operating_margin"), _v("net_margin"), _v("roe"), _v("roa")
            parts = []
            if gm is not None and om is not None:
                spread = gm - om if gm and om else None
                if spread and spread > 0.25:
                    parts.append(f"The {spread:.0%} spread between gross margin ({gm:.1%}) and operating margin ({om:.1%}) "
                                 f"suggests high operating expenses are eroding profitability.")
                elif om is not None and om > 0.15:
                    parts.append(f"Operating margin of {om:.1%} reflects strong cost control relative to revenue.")
            if nm is not None:
                if nm < 0:
                    parts.append(f"The company is unprofitable at the bottom line ({nm:.1%}), which is unsustainable long-term.")
                elif nm > 0 and roe_v is not None:
                    parts.append(f"Net margin of {nm:.1%} translates to a {roe_v:.1%} return on equity for shareholders.")
            if roa_v is not None:
                bm_roa = benchmarks.get("roa", {}).get("median")
                if bm_roa and roa_v < bm_roa * 0.6:
                    parts.append(f"ROA of {roa_v:.1%} falls well below the {ind_short} median, suggesting underutilized assets.")
            return " ".join(parts[:3]) if parts else None

        if cat_name == "Solvency":
            dte, dta, ic_v, em = _v("debt_to_equity"), _v("debt_to_assets"), _v("interest_coverage"), _v("equity_multiplier")
            parts = []
            if dte is not None and ic_v is not None:
                if dte > 2.0 and ic_v < 2.0:
                    parts.append(f"High leverage (D/E: {dte:.2f}) combined with thin interest coverage ({ic_v:.1f}x) "
                                 "creates meaningful default risk and may trigger debt covenant concerns.")
                elif dte < 1.0 and ic_v > 5.0:
                    parts.append(f"Conservative leverage (D/E: {dte:.2f}) and comfortable interest coverage ({ic_v:.1f}x) "
                                 "provide significant financial flexibility and borrowing capacity.")
                else:
                    parts.append(f"Leverage of {dte:.2f}x D/E with {ic_v:.1f}x interest coverage is "
                                 f"{'manageable' if ic_v > 2.5 else 'tight'} for {ind_short} standards.")
            if dta is not None and dta > 0.7:
                parts.append(f"With {dta:.0%} of assets debt-financed, the company has limited equity cushion "
                             "to absorb operating losses.")
            elif dta is not None and em is not None:
                parts.append(f"Debt funds {dta:.0%} of total assets (equity multiplier: {em:.2f}x).")
            return " ".join(parts[:3]) if parts else None

        if cat_name == "Efficiency":
            at_v, invt, rect, dso_v, ccc_v = _v("asset_turnover"), _v("inventory_turnover"), _v("receivables_turnover"), _v("dso"), _v("cash_conversion_cycle")
            parts = []
            if at_v is not None:
                bm_at = benchmarks.get("asset_turnover", {}).get("median")
                if bm_at and at_v < bm_at * 0.7:
                    parts.append(f"Asset turnover of {at_v:.2f}x is below {ind_short} peers, suggesting the asset base "
                                 "may be oversized relative to revenue or include underperforming assets.")
                elif at_v is not None:
                    parts.append(f"Asset turnover of {at_v:.2f}x {'compares favorably to' if bm_at and at_v >= bm_at else 'is in line with'} "
                                 f"{ind_short} peers.")
            if dso_v is not None and invt is not None:
                if dso_v > 60 and invt < 5:
                    parts.append(f"Both collection ({dso_v:.0f} days DSO) and inventory management ({invt:.1f}x turnover) "
                                 "are sluggish, tying up working capital.")
                elif dso_v < 40 and invt > 8:
                    parts.append("Efficient receivables collection and inventory management minimize working capital needs.")
            if ccc_v is not None:
                parts.append(f"The overall cash conversion cycle of {ccc_v:.0f} days "
                             f"{'is efficient' if ccc_v < 40 else 'ties up significant operating capital'}.")
            return " ".join(parts[:3]) if parts else None

        if cat_name == "Earnings Quality":
            accruals, ocf_ni = _v("accruals_ratio"), _v("ocf_to_ni")
            parts = []
            if accruals is not None and ocf_ni is not None:
                if accruals > 0.05:
                    parts.append(f"The accruals ratio of {accruals:.1%} indicates earnings significantly exceed cash generation, "
                                 "raising concerns about aggressive revenue recognition or deferred expense recognition.")
                elif ocf_ni > 1.2:
                    parts.append(f"Cash flow exceeds reported earnings by {(ocf_ni - 1):.0%} (OCF/NI: {ocf_ni:.2f}x), "
                                 "suggesting conservative accounting and high earnings quality.")
                elif ocf_ni is not None and 0 < ocf_ni < 0.8:
                    parts.append(f"Operating cash flow covers only {ocf_ni:.0%} of net income (OCF/NI: {ocf_ni:.2f}x). "
                                 "Investigate whether working capital changes or non-cash gains are inflating earnings.")
                else:
                    parts.append(f"Accruals ratio of {accruals:.1%} and OCF/NI of {ocf_ni:.2f}x suggest "
                                 "{'solid' if abs(accruals) < 0.03 and ocf_ni > 0.9 else 'acceptable'} earnings quality.")
            elif accruals is not None:
                parts.append(f"Accruals ratio of {accruals:.1%} — {'within normal range' if abs(accruals) < 0.05 else 'warrants investigation'}.")
            return " ".join(parts[:3]) if parts else None

        return None

    # ── Render ratio categories ───────────────────────────────────────────
    categories = {}
    for key, ratio in ratios.items():
        cat = ratio.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((key, ratio))

    # Column headers
    def _extract_ticker(name):
        """Extract ticker from 'ADBE - Adobe Systems' format, or return name."""
        if name and " - " in name:
            return name.split(" - ")[0].strip()
        return name or "Company"

    def _render_table_header(peer_label):
        _co_ticker = _extract_ticker(st.session_state.company_name)
        _peer_ticker = _extract_ticker(peer_label) if peer_label else "Peer"
        h_name, h_val, h_peer = st.columns([3, 2, 2])
        with h_name:
            st.markdown('<span style="font-size:0.8em;color:#999;text-transform:uppercase;letter-spacing:0.05em;">Ratio</span>', unsafe_allow_html=True)
        with h_val:
            st.markdown(f'<span style="font-size:0.8em;color:#00c805;text-transform:uppercase;letter-spacing:0.05em;">{_co_ticker}</span>', unsafe_allow_html=True)
        with h_peer:
            st.markdown(f'<span style="font-size:0.8em;color:#999;text-transform:uppercase;letter-spacing:0.05em;">{_peer_ticker}</span>', unsafe_allow_html=True)

    for cat_name in ["Liquidity", "Profitability", "Solvency", "Efficiency", "Earnings Quality"]:
        if cat_name not in categories:
            continue

        st.markdown(f"### {cat_name}")
        _render_table_header(peer_label)

        cat_ratios = categories[cat_name]
        for key, ratio in cat_ratios:
            _render_ratio_row(key, ratio, ratios, prior_ratios, peer_ratios, benchmarks, industry)

        # Category insight box
        _cat_insight = _category_insight(cat_name, ratios, benchmarks, industry)
        if _cat_insight:
            st.markdown(f'<div style="background:#f9f9f9;border-left:3px solid #5ac8fa;padding:12px 16px;'
                        f'margin:8px 0 16px;border-radius:3px;font-size:0.88em;color:#444;line-height:1.5;">'
                        f'<strong>Category Insight:</strong> {_cat_insight}</div>',
                        unsafe_allow_html=True)
        st.markdown("---")

    # ── Deep Analysis ─────────────────────────────────────────────────────
    st.markdown("## Deep Analysis")

    # DuPont Decomposition visualization
    st.markdown("### DuPont Decomposition: What Drives ROE?")
    roe_val = ratios.get("roe", {}).get("value")
    margin_val = ratios.get("dupont_margin", {}).get("value")
    turnover_val = ratios.get("dupont_turnover", {}).get("value")
    leverage_val = ratios.get("dupont_leverage", {}).get("value")

    if all(v is not None for v in [roe_val, margin_val, turnover_val, leverage_val]):
        _dp_labels = ["Net Profit Margin", "Asset Turnover", "Equity Multiplier", "= ROE"]
        _dp_vals = [margin_val, turnover_val, leverage_val, roe_val]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=st.session_state.company_name or "Company",
            x=_dp_labels,
            y=_dp_vals,
            marker_color=["#5ac8fa", "#00c805", "#e74c3c", "#1a1a1a"],
            text=[f"{margin_val:.1%}", f"{turnover_val:.2f}x", f"{leverage_val:.2f}x", f"{roe_val:.1%}"],
            textposition="outside",
            cliponaxis=False,
        ))
        if peer_ratios:
            _p_roe = peer_ratios.get("roe", {}).get("value")
            _p_margin = peer_ratios.get("dupont_margin", {}).get("value")
            _p_turn = peer_ratios.get("dupont_turnover", {}).get("value")
            _p_lev = peer_ratios.get("dupont_leverage", {}).get("value")
            if all(v is not None for v in [_p_roe, _p_margin, _p_turn, _p_lev]):
                _peer_dp = [_p_margin, _p_turn, _p_lev, _p_roe]
                fig.add_trace(go.Bar(
                    name=peer_label or "Peer",
                    x=_dp_labels,
                    y=_peer_dp,
                    marker_color="#999999",
                    text=[f"{_p_margin:.1%}", f"{_p_turn:.2f}x", f"{_p_lev:.2f}x", f"{_p_roe:.1%}"],
                    textposition="outside",
                    cliponaxis=False,
                ))
                _dp_vals = _dp_vals + _peer_dp
        _dp_max = max(abs(v) for v in _dp_vals)
        _dp_min = min(v for v in _dp_vals)
        fig.update_layout(
            title="DuPont Three-Factor Decomposition",
            yaxis_title="Value",
            height=400,
            barmode="group",
            bargap=0.3,
            margin=dict(t=50, b=40),
            yaxis=dict(range=[min(0, _dp_min * 1.3) - 0.05, _dp_max * 1.25 + 0.05]),
        )
        st.plotly_chart(fig, use_container_width=True)

        components = {"Profit Margin": abs(margin_val), "Asset Turnover": abs(turnover_val) / 3, "Leverage": abs(leverage_val) / 5}
        primary = max(components, key=components.get)
        if primary == "Leverage" and leverage_val > 2.5:
            st.warning(f"**ROE is primarily driven by financial leverage** (equity multiplier: {leverage_val:.2f}x). "
                       "High-leverage ROE amplifies both returns and risk. A decline in earnings could quickly erode equity.")
        elif primary == "Profit Margin":
            st.success(f"**ROE is driven by profitability** (net margin: {margin_val:.1%}). "
                       "This represents sustainable, high-quality returns.")

    # Cross-ratio insights
    insights = get_cross_ratio_insights(ratios, industry)
    if insights:
        st.markdown("### Cross-Ratio Professional Insights")
        for insight in insights:
            css_class = {"critical": "risk-critical", "warning": "risk-warning", "positive": "risk-good"}.get(insight["type"], "insight-box")
            st.markdown(f'<div class="{css_class}"><strong>{insight["title"]}</strong><br>{insight["detail"]}</div>',
                       unsafe_allow_html=True)

    # ── Professional Implications ─────────────────────────────────────────
    st.markdown("### Professional Implications")
    st.markdown("Audit and advisory considerations triggered by the ratio analysis:")

    _implications = []
    _v = lambda k: ratios.get(k, {}).get("value")

    # Going concern
    _cr = _v("current_ratio")
    _ic = _v("interest_coverage")
    _nm = _v("net_margin")
    _ocf = data.get("operating_cash_flow")
    if (_cr is not None and _cr < 1.0) or (_ic is not None and _ic < 1.5) or (_nm is not None and _nm < -0.10):
        _triggers = []
        if _cr is not None and _cr < 1.0:
            _triggers.append(f"current ratio below 1.0 ({_cr:.2f})")
        if _ic is not None and _ic < 1.5:
            _triggers.append(f"interest coverage below 1.5x ({_ic:.1f}x)")
        if _nm is not None and _nm < -0.10:
            _triggers.append(f"significant operating losses ({_nm:.1%})")
        _implications.append({
            "title": "Going Concern Assessment (AU-C 570)",
            "detail": f"Indicators present: {'; '.join(_triggers)}. The auditor should evaluate management's plans "
                      "for mitigating these conditions and assess the adequacy of going concern disclosures. "
                      "Consider the entity's ability to meet obligations for at least 12 months beyond the financial statement date.",
        })

    # Revenue recognition
    _dso = _v("dso")
    _accruals = _v("accruals_ratio")
    if (_dso is not None and _dso > 70) or (_accruals is not None and _accruals > 0.05):
        _detail = "Elevated "
        _parts = []
        if _dso is not None and _dso > 70:
            _parts.append(f"DSO ({_dso:.0f} days)")
        if _accruals is not None and _accruals > 0.05:
            _parts.append(f"accruals ratio ({_accruals:.1%})")
        _detail += " and ".join(_parts)
        _detail += " suggest possible aggressive revenue recognition. Evaluate compliance with ASC 606 performance obligation "
        _detail += "criteria, particularly timing of revenue recognition and the existence of side agreements or bill-and-hold arrangements."
        _implications.append({
            "title": "Revenue Recognition Risk (ASC 606)",
            "detail": _detail,
        })

    # Inventory valuation
    _invt = _v("inventory_turnover")
    _gm = _v("gross_margin")
    if _invt is not None and _invt < 4:
        _implications.append({
            "title": "Inventory Valuation (ASC 330)",
            "detail": f"Inventory turnover of {_invt:.1f}x is low, indicating slow-moving inventory. "
                      "Evaluate whether inventory is carried at the lower of cost or net realizable value (NRV) per ASC 330-10. "
                      "Request aging analysis and assess the adequacy of obsolescence reserves.",
        })

    # Debt covenants and classification
    _dte = _v("debt_to_equity")
    if (_dte is not None and _dte > 2.5) or (_ic is not None and _ic < 2.0):
        _implications.append({
            "title": "Debt Classification and Covenants (ASC 470)",
            "detail": f"{'High leverage (D/E: ' + f'{_dte:.2f})' if _dte and _dte > 2.5 else ''}"
                      f"{' and ' if _dte and _dte > 2.5 and _ic and _ic < 2.0 else ''}"
                      f"{'thin interest coverage (' + f'{_ic:.1f}x)' if _ic and _ic < 2.0 else ''} "
                      "increase the risk of covenant violations. Review debt agreements for financial covenant thresholds, "
                      "assess proper classification of debt as current vs. non-current per ASC 470-10, "
                      "and evaluate whether any subjective acceleration clauses have been triggered.",
        })

    # Impairment indicators
    _roa = _v("roa")
    _at = _v("asset_turnover")
    if (_roa is not None and _roa < 0) or (_at is not None and _at < 0.2):
        _implications.append({
            "title": "Asset Impairment Testing (ASC 350 / ASC 360)",
            "detail": "Low or negative returns on assets may indicate impairment triggers for goodwill (ASC 350) "
                      "and long-lived assets (ASC 360). Evaluate whether the carrying amount of asset groups exceeds "
                      "their fair value and whether goodwill impairment testing has been performed with reasonable assumptions.",
        })

    # Earnings quality / fraud risk
    _ocf_ni = _v("ocf_to_ni")
    if _accruals is not None and _accruals > 0.08:
        _implications.append({
            "title": "Earnings Manipulation Risk (SAS 99 / AU-C 240)",
            "detail": f"The accruals ratio of {_accruals:.1%} significantly exceeds cash generation, "
                      "which is a recognized fraud risk factor under AU-C 240. Consider expanding substantive testing "
                      "of revenue and expense cut-off, evaluating management estimates for bias, "
                      "and cross-referencing with the Beneish M-Score analysis on the Risk Assessment page.",
        })

    # Fair value measurements
    _intang = data.get("intangibles", 0) or 0
    _ta = data.get("total_assets", 1) or 1
    if _intang / _ta > 0.3:
        _implications.append({
            "title": "Fair Value Measurements (ASC 820)",
            "detail": f"Intangible assets represent {_intang / _ta:.0%} of total assets, likely requiring significant "
                      "Level 3 fair value measurements under ASC 820. Evaluate the reasonableness of valuation models, "
                      "discount rates, and growth assumptions used in measuring these assets.",
        })

    # Positive — no major concerns
    if not _implications:
        _implications.append({
            "title": "No Significant Red Flags Identified",
            "detail": "The ratio analysis does not trigger major audit risk indicators. Standard substantive procedures "
                      "and analytical review should be sufficient. Continue to evaluate industry-specific risks "
                      "and management representations as part of the overall audit strategy.",
        })

    for impl in _implications:
        st.markdown(f'<div style="background:#f9f9f9;border-left:3px solid #1a1a1a;padding:12px 16px;'
                    f'margin:8px 0;border-radius:3px;font-size:0.9em;line-height:1.5;">'
                    f'<strong>{impl["title"]}</strong><br><span style="color:#555;">{impl["detail"]}</span></div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Benchmarking":
    st.title("Benchmarking")
    if not st.session_state.financial_data:
        st.warning("No financial data loaded. Go to Data Input first.")
        st.stop()

    data = st.session_state.financial_data
    industry = st.session_state.industry
    company_size = st.session_state.company_size
    ratios = calculate_all_ratios(data)
    benchmarks = get_size_adjusted_benchmarks(industry, company_size)

    if not benchmarks:
        st.error(f"No benchmark data available for {industry}.")
        st.stop()

    # ── Peer comparison selector ──────────────────────────────────────────
    _bm_peers = _get_industry_peers(industry, exclude_name=st.session_state.company_name)
    _bm_peer_names = ["None"] + list(_bm_peers.keys())
    _bm_selected = st.selectbox("Compare with industry peer:", _bm_peer_names, key="bench_peer")
    bm_peer_ratios = None
    bm_peer_label = None
    if _bm_selected != "None" and _bm_selected in _bm_peers:
        # Match peer's year to the year being analyzed
        _bm_peer_co = _bm_peers[_bm_selected]
        _analyzing_year = st.session_state.current_year_label
        _bm_peer_cy = _bm_peer_co.get("current_year", "2023")
        _bm_peer_py = _bm_peer_co.get("prior_year", "2022")
        if _analyzing_year == _bm_peer_py:
            _bm_peer_data = _bm_peer_co["prior"]
        else:
            _bm_peer_data = _bm_peer_co["current"]
        bm_peer_ratios = calculate_all_ratios(_bm_peer_data)
        bm_peer_label = _bm_selected.split("(")[0].strip()

    # ── Radar Chart ───────────────────────────────────────────────────────
    _radar_title = "Radar Chart: Company vs. Size-Adjusted Industry Median"
    if bm_peer_label:
        _radar_title = f"Radar Chart: Company vs. {bm_peer_label} vs. Median"
    st.markdown(f"### {_radar_title}")
    radar_keys = ["current_ratio", "gross_margin", "operating_margin", "roa", "roe",
                  "debt_to_equity", "interest_coverage", "asset_turnover"]

    company_vals = []
    median_vals = []
    peer_vals = []
    valid_labels = []
    for k in radar_keys:
        v = ratios.get(k, {}).get("value")
        bm = benchmarks.get(k, {}).get("median")
        if v is not None and bm is not None and bm != 0:
            company_vals.append(v / bm * 100)
            median_vals.append(100)
            valid_labels.append(ratios[k]["name"])
            if bm_peer_ratios:
                pv = bm_peer_ratios.get(k, {}).get("value")
                peer_vals.append(pv / bm * 100 if pv is not None else 100)

    if valid_labels:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=company_vals + [company_vals[0]],
            theta=valid_labels + [valid_labels[0]],
            fill="toself", name=st.session_state.company_name or "Company",
            fillcolor="rgba(0, 200, 5, 0.15)",
            line=dict(color="#00c805"),
        ))
        if bm_peer_ratios and peer_vals:
            fig.add_trace(go.Scatterpolar(
                r=peer_vals + [peer_vals[0]],
                theta=valid_labels + [valid_labels[0]],
                fill="toself", name=bm_peer_label or "Peer",
                fillcolor="rgba(90, 200, 250, 0.10)",
                line=dict(color="#5ac8fa"),
            ))
        fig.add_trace(go.Scatterpolar(
            r=median_vals + [median_vals[0]],
            theta=valid_labels + [valid_labels[0]],
            fill="toself", name="Size-Adjusted Median",
            fillcolor="rgba(26, 26, 26, 0.05)",
            line=dict(color="#999999", dash="dash"),
        ))
        _all_radar = company_vals + peer_vals + [150]
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(_all_radar)])),
            title="Ratios as % of Size-Adjusted Median (100% = Median)",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Percentile Rankings ───────────────────────────────────────────────
    st.markdown("### Percentile Rankings")
    ranking_data = []
    for key in radar_keys + ["dso", "cash_conversion_cycle", "net_margin", "roic"]:
        val = ratios.get(key, {}).get("value")
        bm = benchmarks.get(key, {})
        if val is not None and bm:
            _raw_pctl = get_percentile(val, bm, ratio_key=key)
            pctl = _raw_pctl.split("(")[1].rstrip(")") if "(" in _raw_pctl else _raw_pctl
            is_pct = ratios.get(key, {}).get("is_percentage", False)
            row = {
                "Ratio": ratios[key]["name"],
                "Company Value": format_number(val, is_percentage=is_pct),
                "Industry Median": format_number(bm.get("median"), is_percentage=is_pct) if bm.get("median") else "N/A",
                "Percentile": pctl,
            }
            if bm_peer_ratios:
                _pv = bm_peer_ratios.get(key, {}).get("value")
                _raw_pp = get_percentile(_pv, bm, ratio_key=key) if _pv is not None else "N/A"
                _pp = _raw_pp.split("(")[1].rstrip(")") if "(" in _raw_pp else _raw_pp
                row["Peer Value"] = format_number(_pv, is_percentage=is_pct) if _pv is not None else "N/A"
                row["Peer Percentile"] = _pp
            ranking_data.append(row)

    if ranking_data:
        # Build styled HTML table
        _hdr_style = 'style="padding:10px 14px;font-size:1.05rem;font-weight:700;border-bottom:2px solid #e8e8e8;text-align:left;font-family:Aptos,Calibri,sans-serif;"'
        _co_hdr = 'style="padding:10px 14px;font-size:1.05rem;font-weight:700;border-bottom:2px solid #e8e8e8;text-align:left;color:#00c805;font-family:Aptos,Calibri,sans-serif;"'
        _co_cell = 'style="padding:8px 14px;font-size:1.05rem;border-bottom:1px solid #f0f0f0;color:#00c805;font-weight:500;font-family:Aptos,Calibri,sans-serif;"'
        _cell_style = 'style="padding:8px 14px;font-size:1.05rem;border-bottom:1px solid #f0f0f0;font-family:Aptos,Calibri,sans-serif;"'
        _peer_hdr = 'style="padding:10px 14px;font-size:1.05rem;font-weight:700;border-bottom:2px solid #e8e8e8;text-align:left;color:#5ac8fa;font-family:Aptos,Calibri,sans-serif;"'
        _peer_cell = 'style="padding:8px 14px;font-size:1.05rem;border-bottom:1px solid #f0f0f0;color:#5ac8fa;font-weight:500;font-family:Aptos,Calibri,sans-serif;"'

        _has_peer = "Peer Value" in ranking_data[0]
        _co_name = st.session_state.company_name or "Company"
        _co_ticker = _co_name.split(" - ")[0].strip() if " - " in _co_name else _co_name
        _peer_ticker = bm_peer_label.split(" - ")[0].strip() if bm_peer_label and " - " in bm_peer_label else (bm_peer_label or "Peer")
        _html = '<table style="width:100%;border-collapse:collapse;margin:8px 0;">'
        _html += f'<tr><th {_hdr_style}>Ratio</th><th {_hdr_style}>Industry Median</th><th {_co_hdr}>{_co_ticker}</th><th {_co_hdr}>Percentile</th>'
        if _has_peer:
            _html += f'<th {_peer_hdr}>{_peer_ticker}</th><th {_peer_hdr}>Percentile</th>'
        _html += '</tr>'
        for _i, r in enumerate(ranking_data):
            _row_bg = "#f8f8f8" if _i % 2 == 0 else "#ffffff"
            _html += f'<tr style="background:{_row_bg};"><td {_cell_style}>{r["Ratio"]}</td><td {_cell_style}>{r["Industry Median"]}</td><td {_co_cell}>{r["Company Value"]}</td><td {_co_cell}>{r["Percentile"]}</td>'
            if _has_peer:
                _html += f'<td {_peer_cell}>{r.get("Peer Value", "N/A")}</td><td {_peer_cell}>{r.get("Peer Percentile", "N/A")}</td>'
            _html += '</tr>'
        _html += '</table>'
        st.markdown(_html, unsafe_allow_html=True)

    # ── Strengths and Weaknesses vs. Industry ─────────────────────────────
    st.markdown("### Strengths & Weaknesses vs. Industry Median")
    above = []
    below = []
    for key in benchmarks:
        val = ratios.get(key, {}).get("value")
        med = benchmarks[key].get("median")
        if val is not None and med is not None and med != 0:
            pct_diff = (val - med) / abs(med)
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
        st.markdown("**Strengths (Above Median)**")
        for name, diff in above[:5]:
            st.markdown(f"- **{name}**: {diff:+.0%} vs. median")
        if not above:
            st.markdown("_No ratios significantly above industry median._")

    with col2:
        st.markdown("**Weaknesses (Below Median)**")
        for name, diff in below[:5]:
            st.markdown(f"- **{name}**: {diff:+.0%} vs. median")
        if not below:
            st.markdown("_No ratios significantly below industry median._")

    # ── Head-to-Head: Company vs. Peer ────────────────────────────────────
    if bm_peer_ratios and bm_peer_label:
        st.markdown(f"### Head-to-Head: {st.session_state.company_name or 'Company'} vs. {bm_peer_label}")
        _h2h_keys = ["current_ratio", "gross_margin", "operating_margin", "net_margin",
                     "roa", "roe", "debt_to_equity", "interest_coverage", "asset_turnover"]
        _h2h_labels = []
        _h2h_co = []
        _h2h_peer = []
        for k in _h2h_keys:
            cv = ratios.get(k, {}).get("value")
            pv = bm_peer_ratios.get(k, {}).get("value")
            if cv is not None and pv is not None:
                _h2h_labels.append(ratios[k]["name"])
                _h2h_co.append(cv)
                _h2h_peer.append(pv)

        if _h2h_labels:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name=st.session_state.company_name or "Company",
                y=_h2h_labels, x=_h2h_co,
                orientation="h", marker_color="#00c805",
            ))
            fig.add_trace(go.Bar(
                name=bm_peer_label,
                y=_h2h_labels, x=_h2h_peer,
                orientation="h", marker_color="#5ac8fa",
            ))
            fig.update_layout(
                barmode="group", height=max(350, len(_h2h_labels) * 45),
                margin=dict(l=20, r=20, t=40, b=30),
                xaxis_title="Value",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Summary: wins vs losses
            _co_name = st.session_state.company_name or "Company"
            _wins = 0
            _losses = 0
            _lower_better = {"debt_to_equity", "dso", "cash_conversion_cycle"}
            for k, cv, pv in zip([k for k in _h2h_keys if ratios.get(k, {}).get("value") is not None and bm_peer_ratios.get(k, {}).get("value") is not None], _h2h_co, _h2h_peer):
                if k in _lower_better:
                    if cv < pv:
                        _wins += 1
                    elif cv > pv:
                        _losses += 1
                else:
                    if cv > pv:
                        _wins += 1
                    elif cv < pv:
                        _losses += 1
            st.markdown(f"**{_co_name}** outperforms on **{_wins}** of {_wins + _losses} metrics, "
                        f"underperforms on **{_losses}**.")

    # ── Source Attribution ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.82rem;color:#888;line-height:1.6;font-family:Aptos,Calibri,sans-serif;">'
        '<b>Industry Median Sources:</b> Benchmark data derived from aggregated public filings (10-K) '
        'and industry composite statistics sourced from S&P Capital IQ, Damodaran Online '
        '(pages.stern.nyu.edu/~adamodar), and U.S. Census Bureau Annual Business Survey. '
        'Percentile bands (P25 / Median / P75) reflect trailing-twelve-month data for U.S.-listed companies '
        'within each industry classification. Size adjustments applied per revenue-tier segmentation. '
        'Data is approximate and intended for educational analysis only.</div>',
        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: DCF VALUATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "DCF Valuation":
    st.title("DCF Valuation Engine")
    if not st.session_state.financial_data:
        st.warning("No financial data loaded. Go to Data Input first.")
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
            st.error(f"**{w['field']}:** {w['message']}")
        else:
            st.warning(f"**{w['field']}:** {w['message']}")
    
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
        st.warning("Terminal value accounts for over 75% of enterprise value. "
                   "The valuation is highly sensitive to terminal growth and WACC assumptions. "
                   "Review the sensitivity analysis below carefully.")
    
    # Waterfall chart
    st.markdown("### Value Decomposition")
    decomp = dcf_result["decomposition"]
    measures = ["relative"] * len(decomp) + ["total"]
    x_labels = [d["label"] for d in decomp] + ["Enterprise Value"]
    y_values = [d["value"] for d in decomp] + [0]  # total bar auto-sums
    fig = go.Figure(go.Waterfall(
        name="", orientation="v",
        measure=measures,
        x=x_labels,
        y=y_values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#00c805"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#1a1a1a"}},
        text=[f"${d['value']/1e6:,.0f}M" for d in decomp] + [f"${dcf_result['enterprise_value']/1e6:,.0f}M"],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(
        title="Enterprise Value Composition",
        yaxis_title="Present Value ($)",
        height=400,
        margin=dict(t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sensitivity Analysis
    st.markdown("### Sensitivity Analysis: WACC vs. Terminal Growth Rate")
    sens = sensitivity_analysis(base_rev, growth_rates, margins, capex_pct, nwc_pct, da_pct,
                                wacc_result["wacc"], tgr, shares_out, net_debt_val)
    
    # Build heatmap
    z_data = []
    for row in sens["ev_matrix"]:
        z_data.append([v / 1e6 if v else None for v in row])
    
    _pastel_scale = [
        [0.0, "#f4c2c2"],   # soft rose
        [0.25, "#fce4b8"],  # soft peach
        [0.5, "#fef9e7"],   # soft cream
        [0.75, "#d5f0de"],  # soft mint
        [1.0, "#b8e6c8"],   # soft sage
    ]
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=[f"{t:.1%}" for t in sens["tgr_values"]],
        y=[f"{w:.1%}" for w in sens["wacc_values"]],
        colorscale=_pastel_scale,
        text=[[f"${v:,.0f}M" if v else "N/A" for v in row] for row in z_data],
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#333"},
        hovertemplate="WACC: %{y}<br>TGR: %{x}<br>EV: %{text}<extra></extra>",
    ))
    fig.update_layout(
        title="Enterprise Value Sensitivity ($M)",
        xaxis_title="Terminal Growth Rate",
        yaxis_title="WACC",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Scenario Analysis ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Scenario Analysis: Base / Bull / Bear")

    _base_wacc = wacc_result["wacc"]

    # Pre-populate scenario defaults
    _scenario_defaults = {
        "Base": {
            "growth_rates": list(growth_rates),
            "ebitda_margins": list(margins),
            "wacc": _base_wacc,
            "tgr": tgr,
            "probability": 0.50,
        },
        "Bull": {
            "growth_rates": [g + 0.02 for g in growth_rates],
            "ebitda_margins": [m + 0.02 for m in margins],
            "wacc": _base_wacc - 0.01,
            "tgr": tgr + 0.005,
            "probability": 0.25,
        },
        "Bear": {
            "growth_rates": [g - 0.02 for g in growth_rates],
            "ebitda_margins": [m - 0.02 for m in margins],
            "wacc": _base_wacc + 0.02,
            "tgr": tgr - 0.005,
            "probability": 0.25,
        },
    }

    scenario_tabs = st.tabs(["Base Case", "Bull Case", "Bear Case"])
    scenarios = {}
    _tab_keys = ["Base", "Bull", "Bear"]

    for idx, (tab, sname) in enumerate(zip(scenario_tabs, _tab_keys)):
        _sd = _scenario_defaults[sname]
        with tab:
            st.markdown(f"**{sname} Case Assumptions**")
            _sc_prob = st.number_input(
                f"Probability (%)", value=_sd["probability"] * 100,
                min_value=0.0, max_value=100.0, step=5.0, format="%.0f",
                key=f"sc_prob_{sname}"
            ) / 100
            _sc_gcols = st.columns(n_years)
            _sc_growth = []
            for i in range(n_years):
                with _sc_gcols[i]:
                    _gv = st.number_input(
                        f"Gr Yr{i+1} (%)", value=_sd["growth_rates"][i] * 100,
                        step=0.5, format="%.1f", key=f"sc_gr_{sname}_{i}"
                    ) / 100
                    _sc_growth.append(_gv)
            _sc_mcols = st.columns(n_years)
            _sc_margins = []
            for i in range(n_years):
                with _sc_mcols[i]:
                    _mv = st.number_input(
                        f"Mg Yr{i+1} (%)", value=_sd["ebitda_margins"][i] * 100,
                        step=0.5, format="%.1f", key=f"sc_mg_{sname}_{i}"
                    ) / 100
                    _sc_margins.append(_mv)
            _sc_wcols = st.columns(2)
            with _sc_wcols[0]:
                _sc_wacc = st.number_input(
                    "WACC (%)", value=_sd["wacc"] * 100,
                    step=0.1, format="%.2f", key=f"sc_wacc_{sname}"
                ) / 100
            with _sc_wcols[1]:
                _sc_tgr = st.number_input(
                    "TGR (%)", value=_sd["tgr"] * 100,
                    step=0.1, format="%.2f", key=f"sc_tgr_{sname}"
                ) / 100
            scenarios[sname] = {
                "growth_rates": _sc_growth,
                "ebitda_margins": _sc_margins,
                "wacc": _sc_wacc,
                "tgr": _sc_tgr,
                "probability": _sc_prob,
            }

    # Run scenarios
    scenario_result = run_scenarios(base_rev, scenarios, capex_pct, nwc_pct, da_pct, shares_out, net_debt_val)

    st.markdown("#### Scenario Results")
    _sr_cols = st.columns(3)
    for i, sname in enumerate(_tab_keys):
        _sr = scenario_result["scenarios"][sname]
        with _sr_cols[i]:
            st.markdown(f"**{sname} Case** (p={scenarios[sname]['probability']:.0%})")
            st.metric("Enterprise Value", format_number(_sr["enterprise_value"], is_dollar=True))
            st.metric("Equity Value", format_number(_sr["equity_value"], is_dollar=True))
            _ps = _sr.get("per_share_value")
            st.metric("Per Share", f"${_ps:,.2f}" if _ps else "N/A")

    st.markdown(f"**Probability-Weighted Enterprise Value:** "
                f"{format_number(scenario_result['weighted_enterprise_value'], is_dollar=True)}")

    # Bar chart comparing scenarios
    _sc_names = list(scenario_result["scenarios"].keys())
    _sc_evs = [scenario_result["scenarios"][s]["enterprise_value"] for s in _sc_names]
    fig_sc = go.Figure(go.Bar(
        x=_sc_names,
        y=_sc_evs,
        marker_color=["#5ac8fa", "#00c805", "#e74c3c"],
        text=[format_number(v, is_dollar=True) for v in _sc_evs],
        textposition="outside",
        cliponaxis=False,
    ))
    fig_sc.update_layout(
        title="Scenario Comparison: Enterprise Value",
        yaxis_title="Enterprise Value ($)",
        height=350,
        bargap=0.3,
        margin=dict(t=50, b=40),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

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
elif page == "Risk Assessment":
    st.title("Risk Assessment & Professional Judgment")
    if not st.session_state.financial_data:
        st.warning("No financial data loaded. Go to Data Input first.")
        st.stop()

    data = st.session_state.financial_data
    prior = st.session_state.prior_data

    if not prior:
        st.warning("Prior year data is required for M-Score and F-Score. Load a sample company to see full risk analysis.")

    # ── Altman Z-Score ──
    st.markdown("### Altman Z-Score — Bankruptcy Prediction")
    z_result = calculate_altman_z_score(data)
    
    if "error" not in z_result:
        zcol1, zcol2 = st.columns([1, 2])
        with zcol1:
            st.metric("Z-Score", f"{z_result['z_score']:.2f}")
            st.markdown(f"**Zone:** <span style='color:{z_result['zone_color']};font-weight:bold;'>{z_result['zone']}</span>",
                       unsafe_allow_html=True)
            st.markdown(z_result["zone_description"])
            if z_result.get("standard_reference"):
                st.info(f"**Standard:** {z_result['standard_reference']}")
        
        with zcol2:
            comp_df = pd.DataFrame(z_result["components"])
            _z_vals = [c["weighted"] for c in z_result["components"]]
            fig = go.Figure(go.Bar(
                x=[c["variable"] for c in z_result["components"]],
                y=_z_vals,
                marker_color=["#00c805" if c["weighted"] > 0 else "#e74c3c" for c in z_result["components"]],
                text=[f"{c['weighted']:.3f}" for c in z_result["components"]],
                textposition="outside",
                cliponaxis=False,
            ))
            _z_max = max(abs(v) for v in _z_vals) if _z_vals else 1
            _z_min = min(v for v in _z_vals) if _z_vals else 0
            fig.update_layout(
                title="Z-Score Component Contributions",
                yaxis_title="Weighted Value",
                height=350,
                bargap=0.3,
                margin=dict(t=50, b=40),
                yaxis=dict(range=[min(0, _z_min * 1.3) - 0.05, _z_max * 1.25 + 0.05]),
            )
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
        st.markdown("### Beneish M-Score — Earnings Manipulation Detection")
        m_result = calculate_beneish_m_score(data, prior)
        
        mcol1, mcol2 = st.columns([1, 2])
        with mcol1:
            st.metric("M-Score", f"{m_result['m_score']:.2f}")
            st.markdown(f"**Classification:** <span style='color:{m_result['class_color']};font-weight:bold;'>{m_result['classification']}</span>",
                       unsafe_allow_html=True)
            st.markdown(f"**Threshold:** -1.78 | **Variables Flagged:** {m_result['n_flags']}/8")
            st.markdown(m_result["class_description"])
            if m_result.get("standard_reference"):
                st.info(f"**Standard:** {m_result['standard_reference']}")
        
        with mcol2:
            var_names = [v["name"].split("(")[1].rstrip(")") if "(" in v["name"] else v["name"][:10] for v in m_result["variables"]]
            var_vals = [v["value"] or 0 for v in m_result["variables"]]
            var_colors = ["#e74c3c" if v["flag"] else "#5ac8fa" for v in m_result["variables"]]
            
            fig = go.Figure(go.Bar(
                x=var_names, y=var_vals,
                marker_color=var_colors,
                text=[f"{v:.3f}" if v else "N/A" for v in var_vals],
                textposition="outside",
                cliponaxis=False,
            ))
            _m_max = max(abs(v) for v in var_vals) if var_vals else 1
            _m_min = min(v for v in var_vals) if var_vals else 0
            fig.update_layout(
                title="M-Score Variables (Red = Flagged)",
                yaxis_title="Index Value",
                height=350,
                bargap=0.3,
                margin=dict(t=50, b=40),
                yaxis=dict(range=[min(0, _m_min * 1.3) - 0.05, _m_max * 1.25 + 0.05]),
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Flagged variable details
        if m_result["flagged_variables"]:
            st.markdown("#### Flagged Variables — Recommended Investigation Areas")
            for v in m_result["flagged_variables"]:
                st.markdown(f'<div class="risk-critical"><strong>{v["name"]}</strong> = {v["value"]:.3f}<br>{v["interpretation"]}</div>',
                           unsafe_allow_html=True)
    
    # ── Piotroski F-Score ──
    if prior:
        st.markdown("---")
        st.markdown("### Piotroski F-Score — Financial Strength")
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
                    "Result": "Pass" if c["score"] == 1 else "Fail",
                    "Detail": c["detail"],
                })
            st.dataframe(pd.DataFrame(criteria_data), use_container_width=True, hide_index=True)
    
    # ── Integrated Risk Assessment ──
    if prior:
        st.markdown("---")
        st.markdown("### Integrated Risk Assessment")
        
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
            st.markdown("#### Specific Findings & Recommended Actions")
            for flag in integrated["flags"]:
                severity_label = "CRITICAL" if flag["severity"] == "critical" else "WARNING"
                st.markdown(f"""
                **[{severity_label}] {flag['model']}**: {flag['finding']}
                
                **Standard Reference:** {flag['standard']}
                
                **Recommended Action:** {flag['action']}
                
                ---
                """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6: EXECUTIVE REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Executive Report":
    st.title("Executive Summary Report")
    if not st.session_state.financial_data:
        st.warning("No financial data loaded. Go to Data Input first.")
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
            f"{r.get('name', key)}",
            format_number(r.get("value"), is_percentage=is_pct),
        )
    
    # Ratio health summary
    st.markdown("### Ratio Health Summary")
    health_counts = {"good": 0, "warning": 0, "critical": 0}
    health_lists = {"good": [], "warning": [], "critical": []}
    for key, ratio in ratios.items():
        h = assess_health(key, ratio.get("value"), industry)
        if h["status"] in health_counts:
            health_counts[h["status"]] += 1
            health_lists[h["status"]].append(ratio.get("name", key))

    hcols = st.columns(3)
    hcols[0].metric("Healthy", health_counts["good"])
    hcols[1].metric("Warning", health_counts["warning"])
    hcols[2].metric("Critical", health_counts["critical"])

    # List ratios under each health category if count > 0
    if health_lists["good"]:
        st.markdown(f'<div class="risk-good"><strong>Healthy Ratios:</strong> {", ".join(health_lists["good"])}</div>',
                    unsafe_allow_html=True)
    if health_lists["warning"]:
        st.markdown(f'<div class="risk-warning"><strong>Warning Ratios:</strong> {", ".join(health_lists["warning"])}</div>',
                    unsafe_allow_html=True)
    if health_lists["critical"]:
        st.markdown(f'<div class="risk-critical"><strong>Critical Ratios:</strong> {", ".join(health_lists["critical"])}</div>',
                    unsafe_allow_html=True)

    # Cross-ratio insights — comprehensive narrative
    insights = get_cross_ratio_insights(ratios, industry)
    company_name = st.session_state.company_name or "The company"

    st.markdown("### Key Findings")

    # Build a comprehensive narrative from all available data
    narrative_parts = []

    # Opening — overall posture based on health distribution
    total_rated = health_counts["good"] + health_counts["warning"] + health_counts["critical"]
    if total_rated > 0:
        good_pct = health_counts["good"] / total_rated * 100
        if health_counts["critical"] > 0 and good_pct < 50:
            narrative_parts.append(
                f"{company_name} presents a **concerning financial profile**. Of the {total_rated} ratios evaluated, "
                f"only {health_counts['good']} fall within healthy ranges while {health_counts['critical']} are in critical territory "
                f"and {health_counts['warning']} warrant caution. This distribution suggests material areas requiring immediate attention."
            )
        elif health_counts["critical"] > 0:
            narrative_parts.append(
                f"{company_name} shows a **mixed financial profile**. While {health_counts['good']} of {total_rated} evaluated ratios "
                f"are healthy, {health_counts['critical']} critical and {health_counts['warning']} warning indicators point to specific "
                f"areas that merit closer examination."
            )
        elif health_counts["warning"] > 0:
            narrative_parts.append(
                f"{company_name} demonstrates a **generally sound financial position** with {health_counts['good']} of {total_rated} "
                f"ratios in healthy territory. However, {health_counts['warning']} ratio(s) in the warning range suggest areas "
                f"where performance could improve."
            )
        else:
            narrative_parts.append(
                f"{company_name} exhibits a **strong financial profile** across all {total_rated} evaluated ratios, with every "
                f"metric falling within healthy industry ranges."
            )

    # Liquidity narrative
    cr_val = ratios.get("current_ratio", {}).get("value")
    qr_val = ratios.get("quick_ratio", {}).get("value")
    cash_r = ratios.get("cash_ratio", {}).get("value")
    if cr_val is not None:
        if cr_val >= 1.5:
            liq_text = f"Liquidity appears adequate with a current ratio of {cr_val:.2f}"
            if qr_val is not None:
                liq_text += f" and a quick ratio of {qr_val:.2f}"
            liq_text += ", indicating the company can comfortably meet its short-term obligations."
        elif cr_val >= 1.0:
            liq_text = f"Liquidity is marginally sufficient (current ratio: {cr_val:.2f}), suggesting limited but adequate short-term coverage."
        else:
            liq_text = f"Liquidity is a concern with a current ratio of {cr_val:.2f}, indicating current liabilities exceed current assets."
        narrative_parts.append(liq_text)

    # Profitability narrative
    nm = ratios.get("net_margin", {}).get("value")
    gm = ratios.get("gross_margin", {}).get("value")
    roe_val = ratios.get("roe", {}).get("value")
    roa_val = ratios.get("roa", {}).get("value")
    prof_pieces = []
    if gm is not None:
        prof_pieces.append(f"gross margin of {gm:.1%}")
    if nm is not None:
        prof_pieces.append(f"net margin of {nm:.1%}")
    if roe_val is not None:
        prof_pieces.append(f"return on equity of {roe_val:.1%}")
    if roa_val is not None:
        prof_pieces.append(f"return on assets of {roa_val:.1%}")
    if prof_pieces:
        prof_text = f"From a profitability standpoint, the company reports a {', '.join(prof_pieces)}. "
        if nm is not None and nm < 0:
            prof_text += "The negative bottom line is a significant concern and warrants investigation into cost structure and revenue sustainability."
        elif nm is not None and nm > 0.10:
            prof_text += "These margins reflect solid earnings power and effective cost management."
        elif nm is not None:
            prof_text += "While profitable, there may be room to improve operational efficiency."
        narrative_parts.append(prof_text)

    # Solvency narrative
    dte_val = ratios.get("debt_to_equity", {}).get("value")
    ic_val = ratios.get("interest_coverage", {}).get("value")
    if dte_val is not None or ic_val is not None:
        solv_text = "Regarding solvency, "
        pieces = []
        if dte_val is not None:
            pieces.append(f"the debt-to-equity ratio stands at {dte_val:.2f}")
        if ic_val is not None:
            pieces.append(f"interest coverage is {ic_val:.2f}x")
        solv_text += " and ".join(pieces) + ". "
        if ic_val is not None and ic_val < 2.0:
            solv_text += "The thin interest coverage raises going concern considerations and suggests the company may struggle to service its debt."
        elif dte_val is not None and dte_val > 2.0:
            solv_text += "The elevated leverage warrants monitoring, particularly if earnings face downward pressure."
        else:
            solv_text += "The capital structure appears manageable relative to the company's earnings capacity."
        narrative_parts.append(solv_text)

    # Efficiency narrative
    dso_val = ratios.get("dso", {}).get("value")
    inv_turn = ratios.get("inventory_turnover", {}).get("value")
    ccc_val = ratios.get("cash_conversion_cycle", {}).get("value")
    if dso_val is not None or inv_turn is not None or ccc_val is not None:
        eff_text = "On the efficiency front, "
        pieces = []
        if dso_val is not None:
            pieces.append(f"days sales outstanding is {dso_val:.0f} days")
        if inv_turn is not None:
            pieces.append(f"inventory turns over {inv_turn:.1f}x per year")
        if ccc_val is not None:
            pieces.append(f"the cash conversion cycle spans {ccc_val:.0f} days")
        eff_text += ", ".join(pieces) + ". "
        if ccc_val is not None and ccc_val > 80:
            eff_text += "The extended cash cycle suggests the company takes a long time to convert its investments into cash, which could strain working capital."
        elif dso_val is not None and dso_val > 60:
            eff_text += "Elevated receivables collection times may signal credit risk or aggressive revenue recognition."
        else:
            eff_text += "These metrics suggest the company is managing its operating cycle effectively."
        narrative_parts.append(eff_text)

    # Integrate cross-ratio insights into the narrative
    critical_insights = [i for i in insights if i["type"] == "critical"]
    warning_insights = [i for i in insights if i["type"] == "warning"]
    positive_insights = [i for i in insights if i["type"] == "positive"]

    if critical_insights:
        narrative_parts.append(
            "**Critical findings** from cross-ratio analysis demand immediate attention: " +
            " Additionally, ".join(f"{i['title'].lower()} — {i['detail']}" for i in critical_insights)
        )
    if warning_insights:
        narrative_parts.append(
            "**Areas of caution** identified through cross-ratio analysis include: " +
            " Furthermore, ".join(f"{i['title'].lower()} — {i['detail']}" for i in warning_insights)
        )
    if positive_insights:
        narrative_parts.append(
            "**Positive indicators** from the analysis: " +
            " ".join(i['detail'] for i in positive_insights)
        )

    # Risk model integration (if prior data available)
    if prior:
        z_result = calculate_altman_z_score(data)
        m_result = calculate_beneish_m_score(data, prior)
        f_result = calculate_piotroski_f_score(data, prior)
        risk_pieces = []
        if z_result.get("score") is not None:
            risk_pieces.append(f"the Altman Z-Score of {z_result['score']:.2f} classifies the company in the {z_result.get('zone', 'N/A')} zone")
        if m_result.get("score") is not None:
            manip = "suggests possible earnings manipulation" if m_result["score"] > -1.78 else "does not indicate earnings manipulation"
            risk_pieces.append(f"the Beneish M-Score of {m_result['score']:.2f} {manip}")
        if f_result.get("score") is not None:
            strength = "strong" if f_result["score"] >= 7 else "moderate" if f_result["score"] >= 4 else "weak"
            risk_pieces.append(f"the Piotroski F-Score of {f_result['score']} signals {strength} fundamental strength")
        if risk_pieces:
            narrative_parts.append("From a risk modeling perspective, " + "; ".join(risk_pieces) + ".")

    # Closing
    if health_counts["critical"] > 0:
        narrative_parts.append(
            "**In summary**, the analysis reveals material financial risks that warrant substantive audit procedures "
            "and close professional scrutiny. The critical indicators should be prioritized in the engagement team's risk assessment."
        )
    elif health_counts["warning"] > 0:
        narrative_parts.append(
            "**In summary**, the company's financial health is broadly acceptable but not without areas of concern. "
            "The warning indicators should be factored into the risk assessment and may warrant expanded procedures in targeted areas."
        )
    else:
        narrative_parts.append(
            "**In summary**, the company presents a robust financial profile with no immediate red flags. "
            "Standard audit procedures appear appropriate, though professional skepticism should be maintained throughout the engagement."
        )

    # Render the full narrative
    st.markdown("\n\n".join(narrative_parts))
    
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
    report_bytes = generate_pdf_report(data, prior, industry, ratios, benchmarks,
                                       st.session_state.company_name)
    _report_fname = f"financial_health_report_{(st.session_state.company_name or 'company').replace(' ', '_')}.html"
    st.download_button("Download Report", data=report_bytes,
                       file_name=_report_fname,
                       mime="text/html")
    st.caption("Opens in your browser — use Print > Save as PDF for a PDF copy.")
    
    st.markdown("---")
    st.caption("Generated by Financial Health Assessment Tool | ACG6415 AUDIT Project | "
               "This tool supports professional judgment — it does not replace it. "
               "All findings should be evaluated by qualified professionals in the context of "
               "the specific engagement and applicable professional standards.")
