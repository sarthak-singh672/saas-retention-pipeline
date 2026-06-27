# B2B SaaS Customer Retention Analytics Pipeline

An end-to-end data analytics pipeline that tracks customer lifecycle, churn behaviour, monthly recurring revenue, and customer lifetime value across a B2B SaaS business — from raw data ingestion through to executive dashboards and AI-generated retention recommendations.

---

## Overview

This project simulates the data infrastructure a Customer Success or Revenue Operations team would build at a SaaS company. Starting from raw CRM and event data, the pipeline cleans, transforms, and loads data into PostgreSQL, runs advanced SQL analysis, models financial scenarios in Excel, and surfaces business intelligence through a Tableau dashboard.

The analysis covers 500 accounts across five industries — Cybersecurity, DevTools, EdTech, FinTech, and HealthTech — operating across the US, UK, India, France, Canada, and Australia.

---

## Key Findings

| Metric | Value |
|---|---|
| Total accounts | 500 |
| Overall churn rate | 22.0% |
| Total MRR | $11,338,747 |
| MRR at risk | $2,500,892 |
| Avg MRR per account | $22,677 |
| SLA breach rate | 16.8% (337 of 1,500 HIGH-priority tickets) |
| Avg customer satisfaction | 3.99 / 5.0 |

A 20% reduction in churn through targeted retention programmes would recover $498,904 in monthly recurring revenue, generating $17.9M in additional ARR over three years.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data cleaning and ETL | Python, Pandas, SQLAlchemy |
| Database | PostgreSQL |
| SQL analysis | CTEs, window functions, cohort analysis |
| AI recommendations | Google Gemini API |
| Financial modelling | Excel, openpyxl |
| Visualisation | Tableau |

---

## Project Structure

```
saas_retention_pipeline/
├── raw/                        # Original Kaggle CSV files — never modified
├── processed/                  # Cleaned and transformed CSV outputs
├── etl/
│   ├── clean_and_transform.py  # Data cleaning and feature engineering
│   ├── load_to_postgres.py     # PostgreSQL ingestion
│   ├── gemini_retention_engine.py  # AI recommendation generation
│   └── build_excel_model.py   # Excel model automation
├── sql/                        # Cohort, MRR, LTV and churn SQL queries
├── excel/
│   └── saas_retention_model.xlsx  # SLA model, scenario grid, churn summary
├── docs/
└── README.md
```

---

## Pipeline Architecture

```
Raw CSV (Kaggle)
       |
       v
Python ETL (clean_and_transform.py)
       |
       v
PostgreSQL (saas_retention_db)
       |
       v
SQL Analysis (cohort retention, MRR, LTV, churn rate)
       |
       +-----------+
       |           |
       v           v
Excel Model    Gemini AI
(SLA, scenarios) (per-account recommendations)
       |
       v
Tableau Dashboard
```

---

## Analysis Breakdown

### Churn analysis

Overall churn sits at 22% across all three plan tiers, with Enterprise MRR at risk totalling $1,872,581 — the highest exposure despite similar churn rates across tiers. This indicates Enterprise accounts carry disproportionate revenue risk.

| Plan | Accounts | Churned | Churn Rate | MRR at Risk |
|---|---|---|---|---|
| Basic | 168 | 37 | 22.0% | $167,296 |
| Pro | 178 | 39 | 21.9% | $461,014 |
| Enterprise | 154 | 34 | 22.1% | $1,872,581 |

### Cohort retention analysis

Month-over-month retention tracked by signup cohort using SQL window functions, identifying which cohorts showed accelerated drop-off and at what time post-acquisition.

### MRR trends

MRR tracked from 2023 to 2025, showing exponential growth in the final quarters. Revenue scenario modelling quantifies the impact of churn reduction at five levels — Pessimistic through Aggressive — with ROI projections exceeding 9,600% even under the most conservative scenario.

### SLA performance

HIGH-priority tickets have an average response time of 91.4 minutes against a 15-minute target, generating 337 SLA breaches and triggering credit liability. MEDIUM, LOW and URGENT tickets all operate within target response windows.

### AI-powered retention recommendations

The Gemini API generates per-account retention actions based on churn probability, plan tier, support history, and industry. Outputs include a recommended primary action, a tailored offer, the key risk signal, and a measurable success metric.

---

## Revenue Scenario Modelling

| Scenario | Churn Reduction | Accounts Saved | MRR Recovered | 3-Year Revenue Gain |
|---|---|---|---|---|
| Pessimistic | 5% | 6 | $136,065 | $4,898,338 |
| Conservative | 10% | 11 | $249,452 | $8,980,286 |
| Moderate | 15% | 16 | $362,840 | $13,062,234 |
| Optimistic | 20% | 22 | $498,905 | $17,960,572 |
| Aggressive | 30% | 33 | $748,357 | $26,940,858 |

---

## Dashboard

The Tableau dashboard covers six views: churn by plan tier, MRR trends over time, churn reasons by category, satisfaction by support priority, churn by industry, and a combined retention intelligence summary.

[![Screenshot 2026-06-27 at 7.27.06 PM.png](..%2F..%2FDesktop%2FScreenshot%202026-06-27%20at%207.27.06%E2%80%AFPM.png)
]

---

## How to Run

**Prerequisites:** Python 3.11, PostgreSQL, a Google Gemini API key.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/saas-retention-pipeline.git
cd saas-retention-pipeline

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your PostgreSQL credentials and Gemini API key to .env

# Run the pipeline
python etl/clean_and_transform.py
python etl/load_to_postgres.py
python etl/gemini_retention_engine.py
python etl/build_excel_model.py
```

Then open the Tableau workbook from the `excel/` directory.

---

## Dataset

Source data generated to represent a realistic B2B SaaS customer base: 500 accounts, subscription records, churn events, feature usage logs, and support ticket history across five industries and six countries.

---

## Author

[Sarthak Singh]  
[www.linkedin.com/in/sarthak-singh-015064271 ]  
[sarthak97180@gmail.com]

