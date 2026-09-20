# Phase 2 — System Analysis
## ProcureEdge Supply Solutions Ltd — Procurement Analytics

---

## 1. As-Is System Overview

ProcureEdge Supply Solutions Ltd currently manages its procurement operations through a fragmented combination of spreadsheets, email workflows, and disconnected ERP modules. There is no single source of truth for spend data, supplier performance, or contract compliance.

### Current Process — Purchase to Pay

1. **Requisition** — Department head raises a purchase requisition via email or a shared spreadsheet. No formal workflow or approval routing exists.
2. **Supplier selection** — Category managers select suppliers based on personal knowledge or historical emails. No centralised preferred vendor list is enforced at the point of ordering.
3. **Purchase order creation** — POs are raised manually in the ERP system (SAP B1) by procurement administrators. Data entry is error-prone and inconsistent across departments.
4. **Approval** — POs above £5,000 require CFO approval via email. There is no automated escalation, audit trail, or SLA on approval turnaround.
5. **Goods receipt** — Warehouse staff record deliveries in a separate Excel log. This log is not linked to the ERP, so delivery performance data is never consolidated.
6. **Invoice processing** — Accounts payable manually matches invoices to POs using email trails. Invoice exceptions are resolved by phone or email with suppliers — no exception workflow exists.
7. **Reporting** — Monthly procurement reports are built manually in Excel by the Finance team. This takes 3-5 days at month-end and is often out of date by the time it reaches the CFO.

### Pain Points Identified

| # | Pain Point | Business Impact |
|---|-----------|----------------|
| 1 | No consolidated spend visibility | CFO cannot see total spend by category, supplier, or department in real time |
| 2 | No preferred vendor enforcement | Buyers use non-approved suppliers, losing negotiated discounts and creating risk |
| 3 | Manual delivery tracking | Late deliveries are not systematically identified or escalated |
| 4 | Invoice matching done manually | 12.7% exception rate; each exception costs £180 in admin time |
| 5 | No supplier performance scoring | No objective basis for supplier reviews, renewals, or de-listings |
| 6 | Month-end reporting takes 3-5 days | Decisions are made on stale data |
| 7 | Contract expiry not tracked | Contracts lapse without renegotiation; spot buying at premium rates follows |
| 8 | No risk visibility | High-risk suppliers identified only after incidents occur |

---

## 2. To-Be System Overview

The To-Be system introduces a centralised PostgreSQL procurement database fed by the ERP, with a Python analytics pipeline and a live dashboard accessible to all stakeholders. All manual reporting is eliminated.

### Target Architecture

```
ERP (SAP B1)
    |
    v
ETL Pipeline (Python)
    |
    v
PostgreSQL Database
(suppliers, categories, departments,
 contracts, purchase_orders, po_line_items)
    |
    |-- Analytical Views (6)
    |-- Stored Procedures (4)
    |-- Performance Indexes (13)
         |
         v
   Dashboard (Chart.js)
   5 tabs: Executive | Spend | Supplier | Risk | Recommendations
         |
         |-- CFO / Finance Director
         |-- Chief Procurement Officer
         |-- Head of Supply Chain
         |-- Category Managers
         |-- Quality Assurance Manager
```

### To-Be Process — Purchase to Pay

1. **Requisition** — Department head raises requisition in the ERP. The system validates against the preferred vendor list and flags non-approved suppliers automatically.
2. **Supplier selection** — System surfaces preferred suppliers for the relevant category with current pricing and performance scores.
3. **Purchase order creation** — PO is created in ERP with mandatory fields validated. Data flows automatically to the procurement database via nightly ETL.
4. **Approval** — Automated approval routing based on value thresholds. POs above £50,000 route to CFO with a 24-hour SLA. Audit trail is permanent.
5. **Goods receipt** — Warehouse records delivery in ERP. System automatically calculates actual lead time and flags late deliveries against contracted SLA.
6. **Invoice processing** — Suppliers submit invoices via e-invoicing portal. 3-way matching runs automatically. Exceptions route to a structured workflow with resolution SLAs.
7. **Reporting** — Dashboard refreshes nightly. CFO has live spend visibility at 8am every morning. Monthly reports generate automatically in under 5 minutes.

---

## 3. Gap Analysis

| Capability | As-Is | To-Be | Gap |
|-----------|-------|-------|-----|
| Spend visibility | Monthly Excel, 3-5 day lag | Daily dashboard, nightly refresh | Automate ETL from ERP |
| Supplier performance | No scoring | Composite score (OTD + quality + price + compliance) | Build scorecard in Python and SQL |
| Preferred vendor enforcement | Not enforced | System-enforced at PO creation | ERP configuration change |
| Invoice matching | Manual, email-based | Automated 3-way match via e-invoicing | Mandate e-invoicing portal |
| Late delivery tracking | Not tracked | Automatic SLA breach alerts | Link goods receipt to PO in ERP |
| Contract management | Manual spreadsheet | Contract table with expiry alerts | Populate contracts table |
| Risk visibility | None | Risk rating per supplier, spend exposure | Supplier risk data in master table |
| Reporting speed | 3-5 days | Same day | Python pipeline and dashboard |

---

## 4. Functional Requirements

| ID | Requirement | Priority |
|----|------------|---------|
| FR01 | System shall display total spend by category, supplier, and department | Must Have |
| FR02 | System shall calculate and display supplier performance score (0-100) | Must Have |
| FR03 | System shall flag POs with late delivery against contracted lead times | Must Have |
| FR04 | System shall identify invoice exceptions and route to resolution workflow | Must Have |
| FR05 | System shall display budget vs actual variance by category | Must Have |
| FR06 | System shall support Pareto analysis of supplier spend concentration | Should Have |
| FR07 | System shall track contract expiry dates and send alerts at 90 days | Should Have |
| FR08 | System shall support year-on-year spend comparison by category | Should Have |
| FR09 | System shall produce monthly procurement report automatically | Could Have |
| FR10 | System shall support drill-down from category to individual PO level | Could Have |

---

## 5. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR01 | Dashboard load time | Under 3 seconds on standard laptop |
| NFR02 | Data freshness | Nightly ETL by 06:00 each day |
| NFR03 | Data accuracy | Zero tolerance for calculation errors in spend and savings figures |
| NFR04 | Availability | Dashboard available 99.5% of business hours |
| NFR05 | Audit trail | All PO changes logged with timestamp and user ID |
| NFR06 | Scalability | Database to support 10,000+ POs without performance degradation |
| NFR07 | Browser compatibility | Chrome, Edge, Firefox — no plugin or install required |
| NFR08 | Data security | Role-based access: executives see all; category managers see own category |

---

## 6. System Design Decisions

### Why PostgreSQL
- Generated columns (line_total, discount_amt, net_total, defect_rate_pct) eliminate calculation errors at source
- Window functions support Pareto and YoY comparisons without application-layer complexity
- Foreign key constraints enforce referential integrity — no orphaned line items
- Stored procedures encapsulate business logic so the rules cannot drift between reports

### Why Python pipeline (not Excel)
- Reproducible from raw CSV in one command
- Cleaning, EDA, spend analysis, supplier scoring, and dashboard data compilation are all documented and version-controlled
- Output is a single dashboard_data.json — the dashboard reads one file, not a chain of linked Excel workbooks

### Why Chart.js dashboard (not Power BI)
- Zero licensing cost, zero infrastructure dependency
- Runs locally from a single HTML file via run_dashboard.py
- Can be published to any static host without a Power BI Premium licence
- Full source control — the dashboard is code, not a binary file

---

*Phase 2 complete. See Phase 3 (Data Analysis) for the Python pipeline and Phase 4 (Database) for the full PostgreSQL schema.*
