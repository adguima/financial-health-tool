# Financial Health Assessment & Valuation Tool

**ACG6415: AI in Accounting — AUDIT Project**  
**Platform:** Coding Agent (Claude Code) | **Category:** Analytical Tools & Visualization  
**Framework:** Python + Streamlit

---

## Quick Start

### 1. Install Python
Download Python 3.10+ from [python.org](https://www.python.org/downloads/).  
During installation, **check "Add Python to PATH"**.

### 2. Install Dependencies
Open your terminal/command prompt, navigate to this project folder, and run:

```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`.

---

## Project Structure

```
financial-health-tool/
├── app.py                  # Main Streamlit application (all 6 modules)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── utils/
│   ├── __init__.py
│   ├── ratios.py           # Ratio calculation engine with industry thresholds
│   ├── dcf.py              # DCF valuation with scenarios & sensitivity
│   └── risk_models.py      # Z-Score, M-Score, F-Score implementations
└── data/
    ├── __init__.py
    └── sample_data.py      # Sample companies & industry benchmarks
```

## Modules

| Module | Description |
|--------|-------------|
| 1. Data Input | Upload CSV/Excel or manual entry with validation |
| 2. Ratio Dashboard | 20+ ratios with industry-adjusted health indicators & DuPont decomposition |
| 3. Benchmarking | Radar charts, percentile rankings, strengths/weaknesses vs. peers |
| 4. DCF Valuation | WACC build-up, 5-year projection, sensitivity heatmap, assumption validation |
| 5. Risk Assessment | Altman Z-Score, Beneish M-Score, Piotroski F-Score with integrated analysis |
| 6. Executive Report | Consolidated findings with health summary and action items |

## Sample Companies

Two pre-loaded companies are available for demonstration:
- **TechGrowth Inc.** — Healthy SaaS company with strong margins and growth
- **RetailStruggle Corp.** — Distressed retailer with declining revenue and negative cash flow

Load either from the sidebar dropdown to see the full analysis.

## Planned Enhancements (Claude Code Refinement Phase)

- [ ] PDF report export
- [ ] Multi-period trend analysis (3-5 years)
- [ ] Scenario comparison tab in DCF (Base/Bull/Bear side-by-side)
- [ ] CSV file column auto-mapping
- [ ] Additional industry benchmarks
- [ ] Tooltips and educational overlays for each ratio
- [ ] Visual polish and consistent color theme
