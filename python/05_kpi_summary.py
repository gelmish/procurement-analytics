"""
05_kpi_summary.py
ProcureEdge Supply Solutions Ltd — Final KPI Summary for Dashboard
Combines all analysis outputs into a single dashboard data file.
"""

import pandas as pd
import numpy as np
import json, os

df = pd.read_csv("data/processed/procurement_clean.csv", parse_dates=["po_date","delivery_date"])

with open("data/processed/eda_results.json") as f:
    eda = json.load(f)
with open("data/processed/spend_analysis.json") as f:
    spend = json.load(f)
with open("data/processed/supplier_performance.json") as f:
    perf = json.load(f)

dashboard = {}

# KPI Cards
kpi = eda["kpi_summary"]
dashboard["kpis"] = [
    {"label":"Total Spend",         "value":f"£{kpi['total_spend']/1e6:.1f}M",    "trend":"+8.3% YoY",       "status":"neutral"},
    {"label":"Total Savings",       "value":f"£{kpi['total_savings']/1e6:.2f}M",   "trend":"3.87% rate",      "status":"good"},
    {"label":"Total POs",           "value":f"{kpi['total_pos']:,}",                "trend":"2,457 line items","status":"neutral"},
    {"label":"Active Suppliers",    "value":str(kpi["total_suppliers"]),             "trend":"10 categories",   "status":"neutral"},
    {"label":"Late Delivery Rate",  "value":f"{kpi['late_delivery_pct']}%",          "trend":"Target: <10%",    "status":"bad"},
    {"label":"Invoice Exceptions",  "value":f"{kpi['invoice_exception_pct']}%",      "trend":"Target: <5%",     "status":"bad"},
    {"label":"Preferred Spend",     "value":f"{kpi['preferred_supplier_pct']}%",     "trend":"of total spend",  "status":"good"},
    {"label":"High-Risk Spend",     "value":f"{kpi['high_risk_spend_pct']}%",        "trend":"Target: <10%",    "status":"warn"},
]

# Spend by category
cat_data = sorted(eda["spend_by_category"], key=lambda x: x["total_spend"], reverse=True)
dashboard["category_spend"] = {
    "labels": [r["category_name"] for r in cat_data],
    "values": [round(r["total_spend"]/1000, 0) for r in cat_data],
    "pcts":   [r["spend_pct"] for r in cat_data],
}

# Monthly trend
monthly = sorted(eda["monthly_trend"], key=lambda x: x["month"])
dashboard["monthly_trend"] = {
    "labels": [r["month"] for r in monthly],
    "values": [round(r["total_spend"]/1000, 0) for r in monthly],
}

# Supplier spend top 10
sup_data = sorted(eda["spend_by_supplier"], key=lambda x: x["total_spend"], reverse=True)[:10]
dashboard["supplier_spend"] = {
    "labels": [r["supplier_name"] for r in sup_data],
    "values": [round(r["total_spend"]/1000, 0) for r in sup_data],
    "risk":   [r["risk_rating"] for r in sup_data],
}

# Supplier scorecard
dashboard["supplier_scorecard"] = perf["supplier_scorecard"]

# Risk donut
risk_data = eda["risk_concentration"]
dashboard["risk_donut"] = {
    "labels": [r["risk_rating"] for r in risk_data],
    "values": [round(r["spend_pct"], 2) for r in risk_data],
    "colors": {"High":"#ef4444","Medium":"#f59e0b","Low":"#22c55e"},
}

# Invoice match
inv_data = eda["invoice_match"]
dashboard["invoice_match"] = {
    "labels": [r["match_type"] for r in inv_data],
    "values": [r["count"] for r in inv_data],
}

# Quarterly
dashboard["quarterly"] = eda["quarterly_spend"]

# Dept spend
dept_data = sorted(eda["spend_by_dept"], key=lambda x: x["total_spend"], reverse=True)
dashboard["dept_spend"] = {
    "labels": [r["dept_name"] for r in dept_data],
    "values": [round(r["total_spend"]/1000, 0) for r in dept_data],
}

# Savings
sav = sorted(spend["savings_analysis"], key=lambda x: x["total_savings"], reverse=True)
dashboard["savings"] = {
    "labels":       [r["category_name"] for r in sav],
    "gross_spend":  [round(r["gross_spend"]/1000, 0) for r in sav],
    "net_spend":    [round(r["net_spend"]/1000, 0) for r in sav],
    "savings":      [round(r["total_savings"]/1000, 0) for r in sav],
    "savings_rate": [r["savings_rate"] for r in sav],
}

# Recommendations
dashboard["recommendations"] = [
    {
        "priority":"HIGH", "area":"Supplier Concentration Risk",
        "finding":"Top 3 suppliers account for 61.2% of total spend (£252.5M). FastTrack Logistics alone = 26.6%.",
        "action":"Dual-source FastTrack Logistics within 6 months. Identify 2 qualified alternates for Logistics & Transport.",
        "owner":"Head of Supply Chain", "saving":"Estimated 4-6% cost reduction through competitive tension.",
        "timeline":"Q2 2025"
    },
    {
        "priority":"HIGH", "area":"Late Delivery Rate",
        "finding":"17.7% of purchase orders delivered late. High-risk suppliers average 25+ day lead times vs 7 days for Low-risk.",
        "action":"Implement SLA penalties for suppliers with >10% late rate. Move 3 high-risk suppliers to watch list.",
        "owner":"Procurement Manager", "saving":"Every 1% reduction saves approx. £180K in expediting costs.",
        "timeline":"Q1 2025"
    },
    {
        "priority":"HIGH", "area":"Invoice Exception Rate",
        "finding":"12.7% of invoices flagged as exceptions vs 5% industry benchmark.",
        "action":"Mandate e-invoicing for all Framework and Annual contract suppliers. Target 3-way match >90%.",
        "owner":"Finance Controller", "saving":"Reducing exceptions to 5% saves approx. £145K annually.",
        "timeline":"Q2 2025"
    },
    {
        "priority":"MEDIUM", "area":"Savings Rate",
        "finding":"Current savings rate of 3.87%. Preferred supplier discounts average 4.8% vs 1.2% for non-preferred.",
        "action":"Consolidate spend to preferred suppliers. Renegotiate Framework agreements to target 6%+ discount.",
        "owner":"CPO", "saving":"Closing gap from 3.87% to 5.5% saves approximately £6.8M annually.",
        "timeline":"Q3 2025"
    },
    {
        "priority":"MEDIUM", "area":"Professional Services Overspend",
        "finding":"Professional Services spend is 5,525% over the modelled 2-year budget allocation.",
        "action":"Establish a formal SoW approval process. Require CFO sign-off for engagements >£50K.",
        "owner":"CFO / Category Manager", "saving":"Estimated 15-20% reduction in unplanned consulting spend.",
        "timeline":"Q1 2025"
    },
    {
        "priority":"LOW", "area":"High-Risk Supplier Defects",
        "finding":"High-risk suppliers account for 6.79% of spend but generate 68% of defect incidents.",
        "action":"Introduce incoming quality inspection for all High-risk suppliers. Define defect KPI threshold of <2%.",
        "owner":"Quality Assurance Manager", "saving":"Reduces rework, scrap and customer complaint costs.",
        "timeline":"Q2 2025"
    },
]

with open("data/processed/dashboard_data.json","w") as f:
    json.dump(dashboard, f, indent=2, default=str)

print("Dashboard data compiled successfully.")
print(f"  KPI cards       : {len(dashboard['kpis'])}")
print(f"  Recommendations : {len(dashboard['recommendations'])}")
print(f"  Monthly points  : {len(dashboard['monthly_trend']['labels'])}")