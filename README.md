\# Project 5 — Procurement Analytics

\## ProcureEdge Supply Solutions Ltd



!\[Dashboard](docs/dashboard\_preview.png)



\---



\## Table of Contents

1\. \[Business Problem](#1-business-problem)

2\. \[Business Objectives](#2-business-objectives)

3\. \[Stakeholders](#3-stakeholders)

4\. \[Requirements](#4-requirements)

5\. \[Dataset](#5-dataset)

6\. \[Data Dictionary](#6-data-dictionary)

7\. \[Data Cleaning](#7-data-cleaning)

8\. \[SQL Analysis](#8-sql-analysis)

9\. \[Python Analysis](#9-python-analysis)

10\. \[Data Model](#10-data-model)

11\. \[Dashboard](#11-dashboard)

12\. \[Key Findings](#12-key-findings)

13\. \[Business Recommendations](#13-business-recommendations)

14\. \[System Requirements](#14-system-requirements)

15\. \[Future Improvements](#15-future-improvements)

16\. \[Technologies Used](#16-technologies-used)



\---



\## 1. Business Problem



ProcureEdge Supply Solutions Ltd is a mid-to-large manufacturing and distribution business spending over £412M annually across 18 suppliers in 10 procurement categories. The CFO and Head of Supply Chain have no centralised view of where spend is going, which suppliers are underperforming, or where the company is carrying unacceptable procurement risk.



The core questions driving this project:



\- \*\*Where is the money going?\*\* Which categories and suppliers account for the majority of spend, and is that spend within budget?

\- \*\*Are we getting value?\*\* What is the effective savings rate, and are preferred suppliers delivering better terms?

\- \*\*Are we exposed?\*\* How concentrated is spend in high-risk or single suppliers? What is the on-time delivery failure rate?

\- \*\*What needs to change?\*\* Which actions — ranked by impact — should the CPO take to reduce cost, risk, and operational disruption?



\---



\## 2. Business Objectives



| # | Objective | Success Metric |

|---|-----------|---------------|

| 1 | Achieve full visibility of £412M spend by category, supplier and department | 100% of PO data in a single dashboard |

| 2 | Identify savings gap vs. benchmark (target: 5.5% savings rate) | Current rate 3.87% — gap of 1.63pp |

| 3 | Reduce late delivery rate from 17.7% to below 10% | On-time delivery KPI tracked weekly |

| 4 | Reduce invoice exception rate from 12.7% to below 5% | 3-way match rate KPI tracked monthly |

| 5 | Mitigate supplier concentration risk | No single supplier >20% of total spend |



\---



\## 3. Stakeholders



| Role | Interest | Data Need |

|------|----------|-----------|

| CFO / Finance Director | Cost control, budget variance, savings | Category spend vs. budget, savings rate |

| Chief Procurement Officer (CPO) | Supplier strategy, risk, savings pipeline | Supplier scorecard, concentration, Pareto |

| Head of Supply Chain | Delivery performance, disruption risk | OTD rates, lead times, risk rating |

| Finance Controller | Invoice accuracy, cash flow timing | Invoice match exceptions, payment terms |

| Category Managers | Category-level performance | Per-category spend, savings, supplier mix |

| Quality Assurance Manager | Defect rates, supplier quality | Defect qty, defect rate by supplier |



\---



\## 4. Requirements



\### Functional Requirements

\- Spend dashboard filterable by category, supplier, department, and time period

\- Supplier scorecard with composite performance score (OTD + quality + price + compliance)

\- Budget vs. actual comparison by category with variance flagging

\- Pareto analysis identifying spend concentration

\- Invoice exception report for Finance team

\- Automated risk flag for high-risk POs above threshold value



\### Non-Functional Requirements

\- Dashboard renders in any modern browser with no internet dependency

\- All data stored in normalised PostgreSQL schema (3NF)

\- Analysis reproducible end-to-end from raw CSV via Python scripts

\- Stored procedures encapsulate all business logic



\### Acceptance Criteria

\- All 10 categories represented with budget and actual spend

\- Supplier scorecard covers all 18 suppliers with performance grades

\- Dashboard loads in <3 seconds on a standard laptop

\- All 6 recommendations are quantified with owner and timeline



\---



\## 5. Dataset



\*\*Source:\*\* Synthetic dataset generated for ProcureEdge Supply Solutions Ltd.  

\*\*Generation script:\*\* `data/generate\_data.py`



| File | Rows | Description |

|------|------|-------------|

| `procurement\_data.csv` | 2,457 | Main purchase order line items |

| `suppliers.csv` | 20 | Supplier master data |

| `categories.csv` | 10 | Category master with annual budgets |

| `departments.csv` | 8 | Internal cost centres |



\*\*Scope:\*\* 1,200 purchase orders across FY2023–2024 (January 2023 – December 2024).  

\*\*Total spend:\*\* £412,896,800



\---



\## 6. Data Dictionary



\### procurement\_data.csv (key fields)



| Column | Type | Description |

|--------|------|-------------|

| `po\_number` | string | Purchase order reference (PO-00001 format) |

| `po\_date` | date | Date PO was raised |

| `delivery\_date` | date | Actual or scheduled delivery date |

| `supplier\_id` | string | FK to suppliers master (SUP001 format) |

| `category\_id` | string | FK to categories master (CAT01 format) |

| `dept\_id` | string | FK to departments master (DEPT01 format) |

| `item\_description` | string | Free-text description of goods/services |

| `quantity` | integer | Units ordered |

| `unit\_price` | float | Price per unit (£) |

| `line\_total` | float | quantity × unit\_price (£) |

| `discount\_pct` | float | Discount negotiated (%) |

| `discount\_amt` | float | Discount value (£) |

| `net\_total` | float | line\_total − discount\_amt (£) |

| `defect\_qty` | integer | Units with quality defects on receipt |

| `defect\_rate\_pct` | float | defect\_qty / quantity × 100 |

| `po\_status` | string | Delivered / Partially Delivered / Cancelled / Approved / etc. |

| `invoice\_match` | string | 3-Way / 2-Way / Exception |

| `risk\_rating` | string | Supplier risk: Low / Medium / High |

| `is\_preferred` | boolean | Supplier on preferred vendor list |



\---



\## 7. Data Cleaning



Script: `python/01\_data\_cleaning.py`



| Step | Action | Result |

|------|--------|--------|

| Type casting | Dates → datetime, is\_preferred → bool | Zero type errors |

| Null check | All 30 columns checked | No nulls found |

| Duplicate rows | Full row deduplication | 0 duplicates removed |

| Negative values | unit\_price, quantity, net\_total validated | All valid |

| Derived fields | actual\_lead\_days, is\_late, days\_late, week | Added 7 new columns |

| Text standardisation | Status, invoice\_match, risk fields title-cased | Consistent categories |

| Outlier flagging | IQR method (Q3 + 3×IQR) | 176 high-value POs flagged |

| Invoice exception flag | is\_exception boolean | 312 exceptions identified |

| Discount validation | Recalculated from raw fields | 0 mismatches > 5p |



\*\*Final clean dataset:\*\* 2,457 rows × 37 columns



\---



\## 8. SQL Analysis



Schema: `sql/01\_schema.sql`  

Views: `sql/03\_views.sql`  

Stored Procedures: `sql/04\_stored\_procedures.sql`  

Key Queries: `sql/06\_analysis\_queries.sql`



\### Key queries answered:



```sql

\-- Q1. Spend summary — £412.9M, 3.87% savings rate

SELECT COUNT(DISTINCT po.po\_id) AS total\_pos,

&#x20;      ROUND(SUM(li.net\_total), 2) AS total\_spend,

&#x20;      ROUND(SUM(li.discount\_amt)/SUM(li.line\_total)\*100, 2) AS savings\_rate\_pct

FROM purchase\_orders po JOIN po\_line\_items li ON li.po\_id = po.po\_id;



\-- Q2. Pareto — top 3 suppliers = 61.2% of spend

SELECT s.supplier\_name,

&#x20;      ROUND(SUM(li.net\_total)/SUM(SUM(li.net\_total)) OVER () \* 100, 2) AS spend\_pct,

&#x20;      ROUND(SUM(SUM(li.net\_total)) OVER (ORDER BY SUM(li.net\_total) DESC)

&#x20;            / SUM(SUM(li.net\_total)) OVER () \* 100, 2) AS cumulative\_pct

FROM po\_line\_items li

JOIN purchase\_orders po ON po.po\_id = li.po\_id

JOIN suppliers s ON s.supplier\_id = po.supplier\_id

GROUP BY s.supplier\_name ORDER BY spend\_pct DESC;

```



\*\*Stored procedures:\*\*

\- `fn\_supplier\_performance\_score(supplier\_id)` — Returns weighted composite score (0–100) and grade A–D

\- `sp\_monthly\_spend\_report(year)` — Month-by-month spend with MoM % change

\- `fn\_category\_budget\_status(years)` — Budget vs actual with over/under flag

\- `sp\_flag\_high\_risk\_pos(min\_value, risk\_rating)` — Escalation queue for CPO review



\---



\## 9. Python Analysis



| Script | Purpose | Key Output |

|--------|---------|-----------|

| `01\_data\_cleaning.py` | Type casting, validation, derived fields | `procurement\_clean.csv` |

| `02\_eda.py` | Exploratory analysis across all dimensions | `eda\_results.json` |

| `03\_spend\_analysis.py` | Budget vs actual, Pareto, YoY, savings | `spend\_analysis.json` |

| `04\_supplier\_performance.py` | Scorecard, risk matrix, OTD, defects | `supplier\_performance.json` |

| `05\_kpi\_summary.py` | Dashboard data compiler (all JSONs → one) | `dashboard\_data.json` |



\*\*Key findings from Python analysis:\*\*

\- 83.4% of spend sits with Low-risk suppliers — positive headline

\- Top 3 suppliers (FastTrack, RoboComponents, SwiftLog) account for 61.2% of spend

\- Preferred suppliers deliver average 4.8% discount vs. 1.2% for non-preferred

\- High-risk supplier defect rate averages 3.4% vs. <0.1% for Low-risk



\---



\## 10. Data Model



\### ERD (PostgreSQL — 3NF)



```

┌──────────────┐        ┌──────────────────┐        ┌───────────────┐

│  suppliers   │        │  purchase\_orders  │        │  departments  │

│──────────────│        │──────────────────│        │───────────────│

│ supplier\_id PK│◄──────│ supplier\_id FK   │───────►│ dept\_id PK    │

│ supplier\_name│        │ po\_id PK         │        │ dept\_name     │

│ country      │        │ po\_number        │        │ dept\_head     │

│ risk\_rating  │        │ po\_date          │        │ cost\_centre   │

│ is\_preferred │        │ delivery\_date    │        └───────────────┘

│ payment\_terms│        │ dept\_id FK       │

│ contract\_type│        │ po\_status        │

└──────────────┘        │ invoice\_match    │

&#x20;                       └────────┬─────────┘

&#x20;                                │ 1:N

&#x20;                       ┌────────▼─────────┐        ┌───────────────┐

&#x20;                       │  po\_line\_items   │        │  categories   │

&#x20;                       │──────────────────│        │───────────────│

&#x20;                       │ line\_id PK       │───────►│ category\_id PK│

&#x20;                       │ po\_id FK         │        │ category\_name │

&#x20;                       │ category\_id FK   │        │ budget\_annual │

&#x20;                       │ item\_description │        └───────────────┘

&#x20;                       │ quantity         │

&#x20;                       │ unit\_price       │        ┌───────────────┐

&#x20;                       │ line\_total\*      │        │  contracts    │

&#x20;                       │ discount\_pct     │        │───────────────│

&#x20;                       │ discount\_amt\*    │        │ contract\_id PK│

&#x20;                       │ net\_total\*       │        │ supplier\_id FK│

&#x20;                       │ defect\_qty       │        │ category\_id FK│

&#x20;                       │ defect\_rate\_pct\* │        │ contract\_ref  │

&#x20;                       └──────────────────┘        │ start\_date    │

&#x20;                                                    │ end\_date      │

&#x20;                       \* GENERATED ALWAYS columns   └───────────────┘

```



\*\*Normalisation notes:\*\*

\- \*\*1NF:\*\* All columns are atomic, no repeating groups

\- \*\*2NF:\*\* No partial dependencies — all non-key attributes depend on the full PK

\- \*\*3NF:\*\* No transitive dependencies — supplier attributes live in `suppliers`, not on every line item



\---



\## 11. Dashboard



\*\*File:\*\* `dashboard/index.html`  

\*\*Launch:\*\* `python run\_dashboard.py`



Five tabs covering the full analyst chain:



| Tab | Purpose | Charts / Tables |

|-----|---------|----------------|

| \*\*Executive Summary\*\* | CFO-level overview | 8 KPI cards, category bar, monthly trend, risk donut, invoice match |

| \*\*Spend Analysis\*\* | Category and supplier deep-dive | Supplier bar, dept bar, quarterly comparison, budget vs actual table |

| \*\*Supplier Performance\*\* | Scorecard and OTD analysis | OTD bar, discount bar, full 18-supplier scorecard table |

| \*\*Risk \& Compliance\*\* | Risk concentration and exceptions | Risk spend bar, Pareto chart, exception table |

| \*\*Recommendations\*\* | Phase 6 — Management actions | 6 prioritised recommendations with owners and savings estimates |



\---



\## 12. Key Findings



\### Spend Concentration

\- \*\*61.2% of total spend sits with just 3 suppliers.\*\* FastTrack Logistics alone accounts for £110M (26.6%). A single disruption event at this supplier would halt operations across multiple departments.

\- Professional Services and Logistics together consume 68% of total spend — both categories are significantly over any modelled budget benchmark.



\### Delivery Performance

\- \*\*17.7% of purchase orders were delivered late.\*\* High-risk suppliers (High rating) average 25+ day lead times; Low-risk suppliers average 7 days. The late delivery rate directly correlates with supplier risk rating.

\- AlphaSteel Corp (Ukraine, High risk) shows the worst on-time delivery at 60.7% and the highest defect rate at 4.1%.



\### Financial Leakage

\- \*\*The savings rate of 3.87% lags the 5.5% peer benchmark\*\* by 1.63 percentage points — equivalent to £6.8M left on the table annually.

\- Preferred suppliers deliver 4.8% average discount; non-preferred suppliers deliver 1.2%. The case for consolidating to the approved vendor list is financially clear.



\### Invoice Compliance

\- \*\*12.7% of invoices resulted in exceptions\*\* (312 POs), against an industry best practice of <5%. At £180 average processing cost per exception, the admin burden exceeds £56K. Exceptions are disproportionately concentrated in non-preferred, high-risk suppliers.



\---



\## 13. Business Recommendations



| Priority | Area | Action | Owner | Timeline | Est. Saving |

|----------|------|--------|-------|----------|-------------|

| 🔴 HIGH | Supplier Concentration | Dual-source FastTrack Logistics; cap any single supplier at 20% of category | Head of Supply Chain | Q2 2025 | £8–12M |

| 🔴 HIGH | Late Delivery Rate | SLA penalties in contracts; 3 suppliers on improvement plans | Procurement Manager | Q1 2025 | £180K per 1pp improvement |

| 🔴 HIGH | Invoice Exceptions | Mandate e-invoicing; target 3-way match >90% | Finance Controller | Q2 2025 | £131K/yr |

| 🟡 MEDIUM | Savings Rate | Consolidate to preferred suppliers; renegotiate Framework agreements for 6%+ | CPO | Q3 2025 | £6.8M/yr |

| 🟡 MEDIUM | Professional Services Overrun | SoW approval process; CFO sign-off >£50K; preferred consulting panel | CFO | Q1 2025 | 15–20% reduction |

| 🟢 LOW | High-Risk Defects | Incoming quality inspection; <2% defect KPI in contracts | QA Manager | Q2 2025 | £400–600K/yr |



\---



\## 14. System Requirements



| Component | Requirement |

|-----------|-------------|

| Python | 3.10+ |

| Libraries | pandas, numpy, matplotlib, seaborn, jupyter |

| Database | PostgreSQL 14+ (SQLite 3.35+ for local dev) |

| Dashboard | Any modern browser (Chrome, Edge, Firefox) |

| Storage | 50MB minimum for data and outputs |

| RAM | 2GB+ for Python analysis scripts |



\---



\## 15. Future Improvements



1\. \*\*Live data integration\*\* — Connect to ERP (SAP/Oracle) via API to replace synthetic data with live PO feeds

2\. \*\*Price benchmarking module\*\* — Compare unit prices against market indices to identify price creep by item

3\. \*\*Contract expiry alerts\*\* — Flag contracts expiring within 90 days for proactive renewal

4\. \*\*Spend forecasting\*\* — ARIMA/Prophet time series model to forecast Q1 2025 spend by category

5\. \*\*Supplier diversity tracking\*\* — Add spend with SMEs, minority-owned businesses for ESG reporting

6\. \*\*Power BI version\*\* — Migrate dashboard to Power BI Service for enterprise sharing and scheduled refresh



\---



\## 16. Technologies Used



| Technology | Purpose |

|------------|---------|

| \*\*Python 3.11\*\* | Data generation, cleaning, EDA, analysis |

| \*\*pandas / numpy\*\* | Data manipulation and numerical analysis |

| \*\*PostgreSQL 14\*\* | Normalised production database |

| \*\*SQL\*\* | Views, stored procedures, analytical queries |

| \*\*Chart.js 4.4\*\* | Interactive dashboard charts |

| \*\*HTML / CSS / JavaScript\*\* | Dashboard front end |

| \*\*Jupyter Notebook\*\* | Exploratory analysis and documentation |

| \*\*Git / GitHub\*\* | Version control and portfolio hosting |



\---



\*\*Portfolio:\*\* \[github.com/gelmish](https://github.com/gelmish)  

\*\*Project:\*\* Project 5 of 10 — Procurement Analytics  

\*\*Author:\*\* George Jerry Eze | Gelmish Technology Ltd  

\*\*Standards:\*\* 6-Phase Methodology | PostgreSQL | 16-Section README | Deployable Dashboard | Full Analyst Chain



