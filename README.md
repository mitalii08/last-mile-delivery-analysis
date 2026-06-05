# last-mile-delivery-analysis
SQL + Python + Tableau analysis of 100K+ orders identifying SLA breach patterns and $369K cost reduction opportunity

# Last-Mile Delivery Failure Analysis & Cost Reduction

## Project Overview
End-to-end SQL + Python + Tableau analysis of 110,189 orders across 425 carriers 
identifying SLA breach patterns and routing inefficiencies in last-mile delivery.
Built for Amazon Logistics / Walmart Transport use case using the Olist Brazilian 
E-Commerce dataset.

## Tools Used
- PostgreSQL — data pipeline and SLA breach detection
- Python (pandas, numpy) — root-cause segmentation and DRSI scoring
- Tableau Public — executive dashboard with 4 drill-down views
- Excel — business-ready savings model for stakeholders

## Key Findings
- Overall SLA breach rate: 7.91% across 110,189 delivered orders
- Top 4 corridors (18% of states) drive 92.98% of all SLA breaches
- Multi-SKU orders carry 1.9x higher late-delivery rate (15.74% vs 8.29%)
- 425 carriers scored using DRSI — top 107 flagged as high risk
- Projected savings of $369,798 by routing high-risk corridors to top-quartile carriers

---

## Methodology

### 1. SQL Pipeline (PostgreSQL)
- Loaded 5 Olist tables (110K+ orders, 3K sellers, 1M geolocation records)
- Built SLA breach view comparing actual vs estimated delivery dates
- Identified corridor concentration: top 4 states = 92.98% of all breaches
- SP state alone accounts for 76.85% of total breaches
- MA state has highest breach rate at 24.42% — 1 in 4 orders late

### 2. Python Analysis (pandas)
- Multi-SKU segmentation: orders with 2+ items are 1.9x more likely to be late
- Single-SKU late rate: 8.29% vs Multi-SKU late rate: 15.74%
- Savings model: $369,798 projected by moving high-risk corridors to top-quartile carriers
- Top-quartile benchmark breach rate: 2.77%

### 3. Delivery Risk Scoring Index (DRSI) — Original Framework

Most delivery analyses rank routes by raw failure count — this penalizes 
high-volume corridors unfairly and misses low-volume routes with catastrophic 
revenue exposure.

DRSI reranks routes by **business impact**, not failure count, using a 
composite 0-100 score across 4 weighted dimensions:

| Dimension | Weight | Rationale |
|---|---|---|
| Delay Frequency | 35% | Core SLA breach signal |
| Post-Delay Review Drop | 25% | Customer retention impact |
| Revenue at Risk | 25% | Financial exposure per route |
| Carrier Variance | 15% | Consistency vs peers in same state |

**Result:** Routes ranked by DRSI told a completely different story than 
raw breach counts — surfacing high-value low-volume corridors that would 
have been ignored in a standard analysis.

A **Tableau What-If Simulator** was built on top of DRSI allowing executives 
to model carrier swap ROI by adjusting two parameters: % of high-risk carriers 
swapped and % breach rate reduction expected.

### 4. Tableau Dashboard
4 interactive views replacing 4 manual weekly reports:
- **Carrier Breach Rate** — ranked bar chart with top-quartile benchmark line at 2.77%
- **DRSI Risk Matrix** — scatter plot of risk score vs revenue at risk, bubble sized by order volume
- **State Breach Map** — geographic view of Brazil breach concentration
- **What-If Simulator** — parameter sliders to model carrier swap ROI in real time

**Live Dashboard:** [View on Tableau Public](https://public.tableau.com/app/profile/mitali.nivangune/viz/Last-MileDeliveryFailureAnalysis/Dashboard1?publish=yes)

---

## Repository Structure
├── delivery_analysis.py       # Python analysis and DRSI scoring
├── queries/
│   ├── create_tables.sql      # Table creation scripts
│   ├── sla_breach_view.sql    # Core SLA breach view
│   └── corridor_analysis.sql  # Corridor concentration queries
├── data/
│   ├── breach_master.csv
│   ├── carrier_summary.csv
│   └── drsi_scored_routes.csv
└── delivery_analysis.xlsx     # Excel savings model


## Dataset
Olist Brazilian E-Commerce Dataset  
Source: kaggle.com/datasets/olistbr/brazilian-ecommerce  
100K+ orders across 73 carriers, 27 Brazilian states, 2016-2018

---
