# 🚚 Delivery Performance, Delay Risk & Logistics Efficiency Analysis
### Global Supply Chain Operations — Data Analytics & Dashboard Project

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly)](https://plotly.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikit-learn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Project Overview

Large-scale global logistics operations struggle with delivery delays that lead to SLA violations, financial penalties, and customer dissatisfaction. Despite collecting detailed order and shipping data, most logistics teams operate **reactively** — responding to delays after they occur rather than anticipating them.

This project builds a **diagnostic intelligence layer** that transforms raw shipping records into actionable answers:

- How often are deliveries on-time vs. delayed?
- Which shipping modes carry the highest delay risk?
- Which geographic markets and regions are most problematic?
- Are high-value customer segments disproportionately affected?

---

## 🏗️ Architecture

```
Raw CSV  →  data_cleaning.py  →  cleaned_data.csv
         →  feature_engineering.py  →  Delay_Gap + Delivery_Classification
         →  kpi_metrics.py  →  KPI scalars + grouped DataFrames
         →  Streamlit Dashboard  (4 interactive pages)
```

The data flow is strictly **unidirectional**. All KPI logic is defined once in `src/kpi_metrics.py` and reused identically in notebooks and the live dashboard — no divergent calculations.

---

## 📁 Folder Structure

```
supply-chain-delay-analysis/
├── data/
│   ├── raw/                          ← Place DataCoSupplyChainDataset.csv here
│   └── processed/                    ← Auto-generated: cleaned_data.csv
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda_overall_performance.ipynb
│   ├── 03_shipping_mode_analysis.ipynb
│   ├── 04_regional_market_analysis.ipynb
│   ├── 05_customer_segment_analysis.ipynb
│   └── 06_optional_ml_model.ipynb
├── src/
│   ├── __init__.py
│   ├── data_cleaning.py              ← Stage 1: load, validate, clean
│   ├── feature_engineering.py        ← Stage 2: Delay_Gap + classification
│   ├── kpi_metrics.py                ← Stage 3: all KPI functions
│   └── utils.py                      ← Shared constants and paths
├── app/
│   ├── app.py                        ← Streamlit entry point + sidebar filters
│   └── pages/
│       ├── 1_Delivery_Performance.py
│       ├── 2_Delay_Risk_Analysis.py
│       ├── 3_Shipping_Mode_Comparison.py
│       └── 4_Regional_Market_Heatmaps.py
├── reports/                          ← Research paper + executive summary
├── models/                           ← Saved ML model (optional Phase 9)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/crazycoderuser/Delivery-Performance-Delay-Risk-Logistics-Efficiency-Analysis-in-Global-Supply-Chain-Operations
cd supply-chain-delay-analysis
```

### Step 2 — Create a Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Linux / macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download the Dataset

Download **DataCoSupplyChainDataset.csv** from Kaggle:

> 🔗 [DataCo Smart Supply Chain for Big Data Analysis](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)

Place the file at:

```
data/raw/DataCoSupplyChainDataset.csv
```

> **Note:** This dataset must be loaded with `encoding='latin-1'`. The cleaning pipeline handles this automatically.

---

## 🚀 Running the Project

### Step 1 — Run the Data Cleaning Pipeline

```bash
python src/data_cleaning.py
```

**What this does:**
- Loads the raw CSV with latin-1 encoding
- Validates shipping day values (drops negative values)
- Drops rows missing critical columns
- Standardises text fields (strip + title-case)
- Parses date columns
- Removes duplicates
- Saves `data/processed/cleaned_data.csv`
- Prints a before/after row-count summary

**Expected output:**
```
=======================================================
  SUPPLY CHAIN DATA CLEANING PIPELINE
=======================================================
[INFO] Loading dataset from: data/raw/DataCoSupplyChainDataset.csv
[INFO] Raw shape: 180,519 rows × 53 columns
[CLEAN] No rows with negative shipping days found.
[CLEAN] No rows with missing critical columns.
[CLEAN] Text columns standardised (strip + title-case).
[CLEAN] Date columns parsed to datetime.
[CLEAN] No duplicate rows found.

[SUMMARY] 180,519 raw rows → 178,941 clean rows (1,578 removed, 99.1% retained)
[OUTPUT] Cleaned data saved to: data/processed/cleaned_data.csv
```

### Step 2 — Launch the Streamlit Dashboard

```bash
streamlit run app/app.py
```

Open your browser at **http://localhost:8501**

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| **🏠 Home** | Top-level KPI scorecards: On-Time Rate, Avg Delay, Late Risk Ratio, Total Orders |
| **📊 Delivery Performance** | Classification breakdown, Delay_Gap histogram, delivery status distribution, gap statistics |
| **⚠️ Delay Risk Analysis** | Risk donut chart, box plot by delivery status, high-risk region × market table, monthly trend |
| **🚢 Shipping Mode Comparison** | Late rate, SLA compliance, avg delay, and volume breakdown per shipping mode |
| **🗺️ Regional & Market Heatmaps** | Geographic scatter map, market/region bar charts, sortable regional delay table, segment impact |

### Live Sidebar Filters (apply to all pages)

| Filter | Widget | Column |
|--------|--------|--------|
| Shipping Mode | Multiselect | `Shipping Mode` |
| Market | Multiselect | `Market` |
| Customer Segment | Multiselect | `Customer Segment` |
| Date Range | Date picker | `order date (DateOrders)` |

---

## 📐 Key Metrics Explained

### Delivery Delay Gap
```
Delay_Gap = Days for shipping (real) − Days for shipment (scheduled)
```
- `> 0` → Delayed (arrived later than planned)
- `= 0` → On-time (arrived exactly as planned)
- `< 0` → Early (arrived before the planned window)

### KPIs

| KPI | Formula | Range |
|-----|---------|-------|
| On-Time Delivery Rate | `% where Delay_Gap = 0` | 0–100% |
| Average Delivery Delay | `mean(Delay_Gap)` | Any float (days) |
| Late Delivery Risk Ratio | `mean(Late_delivery_risk)` | 0–1 |
| Shipping Mode Efficiency | Grouped `late_rate` + `avg_delay` | Per mode |
| Regional Delay Index | Grouped `late_rate` + `avg_delay` | Per region/market |

---

## 🧪 Source Module Reference

### `src/data_cleaning.py`
| Function | Description |
|----------|-------------|
| `load_raw(path)` | Load CSV with latin-1 encoding; print clear error if not found |
| `validate_shipping_days(df)` | Drop rows with negative shipping day values |
| `drop_missing_critical(df)` | Drop rows missing any of the 6 critical columns |
| `standardise_text(df)` | strip() + title() on all categorical text columns |
| `parse_dates(df)` | Parse order and shipping date columns to datetime |
| `drop_duplicates(df)` | Remove exact duplicate rows |
| `clean_data(path)` | **Main pipeline** — runs all steps in sequence, saves output |

### `src/feature_engineering.py`
| Function | Description |
|----------|-------------|
| `compute_delay_gap(df)` | Adds `Delay_Gap` column |
| `classify_delivery(gap)` | Maps a gap value to Delayed/On-time/Early |
| `add_delivery_classification(df)` | Adds `Delivery_Classification` column |
| `sanity_check(df)` | Cross-tabulates derived label vs raw `Late_delivery_risk` |
| `add_delay_features(df)` | **Main entry point** — runs all three steps + sanity check |

### `src/kpi_metrics.py`
| Function | Returns | Description |
|----------|---------|-------------|
| `on_time_delivery_rate(df)` | `float` | % of On-time orders |
| `average_delay(df)` | `float` | Mean Delay_Gap |
| `late_delivery_risk_ratio(df)` | `float` | Mean of Late_delivery_risk |
| `shipping_mode_efficiency(df)` | `DataFrame` | Grouped by Shipping Mode |
| `regional_delay_index(df, group_col)` | `DataFrame` | Grouped by region/market |
| `customer_segment_impact(df)` | `DataFrame` | Grouped by Customer Segment |
| `delivery_status_breakdown(df)` | `DataFrame` | Count + % by Delivery Status |
| `delay_gap_stats(df)` | `dict` | Full descriptive stats for Delay_Gap |

---

## 🌐 Deployment (Streamlit Community Cloud)

1. Push the repository to GitHub (ensure `data/processed/cleaned_data.csv` is committed — it is under the 50 MB limit for this dataset)
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in with GitHub
3. Click **New app** → select your repo → set the main file to `app/app.py`
4. Click **Deploy**

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Data processing | Python, pandas, NumPy |
| Visualisation (EDA) | Matplotlib, Seaborn |
| Interactive charts | Plotly |
| Dashboard | Streamlit |
| Machine Learning (optional) | scikit-learn (RandomForest) |
| Explainability (optional) | SHAP (TreeExplainer) |
| Deployment | Streamlit Community Cloud |

---

## ✅ Deliverables Checklist

- [x] Cleaned dataset pipeline (`src/data_cleaning.py`)
- [x] Feature engineering module (`src/feature_engineering.py`)
- [x] Centralised KPI engine (`src/kpi_metrics.py`)
- [x] EDA notebooks (01–05, plus optional 06)
- [x] 4-page Streamlit dashboard (`app/`)
- [x] All 4 sidebar filters live on every page
- [x] Geographic heatmap (Page 4)
- [ ] Research paper → `reports/research_paper.docx`
- [ ] Executive summary → `reports/executive_summary.pdf`
- [ ] Optional ML model → `models/late_delivery_risk_model.pkl`
- [ ] Live deployed dashboard URL

---

## 🔮 Future Enhancements

- **Real-time connector**: replace static CSV with a live database or API query
- **Predictive layer**: RandomForest + SHAP explainability for pre-shipment risk scoring
- **Anomaly detection**: Isolation Forest to flag statistical outliers before they ship
- **Route optimisation**: recommend optimal shipping mode per destination based on historical delay patterns
- **Time-series forecasting**: detect seasonal delay trends and forecast future SLA risk

---

## 📄 Dataset

**DataCo Smart Supply Chain for Big Data Analysis**
- Source: [Kaggle](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
- Authors: Constante, Silva, and Pereira (2019)
- Rows: ~180,000 order-level records
- Encoding: `latin-1` (required)

---

## 👤 Author

**Utpal Chatterjee**

---

## 📃 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
