"""
02_eda.py
ProcureEdge Supply Solutions Ltd — Exploratory Data Analysis
Phase 3: Data Analysis — Step 2
"""

import pandas as pd
import numpy as np
import json, os

df = pd.read_csv("data/processed/procurement_clean.csv", parse_dates=["po_date","delivery_date"])
os.makedirs("data/processed", exist_ok=True)

results = {}

# 1. Spend by category
cat_spend = (df.groupby("category_name")
               .agg(total_spend=("net_total","sum"),
                    po_count=("po_number","nunique"),
                    avg_po_value=("net_total","mean"),
                    total_savings=("discount_amt","sum"))
               .sort_values("total_spend", ascending=False)
               .reset_index())
cat_spend["spend_pct"] = (cat_spend["total_spend"] / cat_spend["total_spend"].sum() * 100).round(2)
results["spend_by_category"] = cat_spend.to_dict(orient="records")

# 2. Spend by supplier
sup_spend = (df.groupby(["supplier_name","risk_rating","is_preferred"])
               .agg(total_spend=("net_total","sum"),
                    po_count=("po_number","nunique"),
                    avg_lead_days=("actual_lead_days","mean"),
                    late_count=("is_late","sum"),
                    defect_rate=("defect_rate_pct","mean"),
                    avg_discount=("discount_pct","mean"))
               .sort_values("total_spend", ascending=False)
               .reset_index())
sup_spend["late_pct"]  = (sup_spend["late_count"] / sup_spend["po_count"] * 100).round(2)
sup_spend["spend_pct"] = (sup_spend["total_spend"] / sup_spend["total_spend"].sum() * 100).round(2)
results["spend_by_supplier"] = sup_spend.head(15).to_dict(orient="records")

# 3. Monthly spend trend
monthly = (df.groupby("month")
             .agg(total_spend=("net_total","sum"),
                  po_count=("po_number","nunique"))
             .reset_index()
             .sort_values("month"))
results["monthly_trend"] = monthly.to_dict(orient="records")

# 4. Spend by department
dept_spend = (df.groupby("dept_name")
                .agg(total_spend=("net_total","sum"),
                     po_count=("po_number","nunique"),
                     avg_po_value=("net_total","mean"))
                .sort_values("total_spend", ascending=False)
                .reset_index())
dept_spend["spend_pct"] = (dept_spend["total_spend"] / dept_spend["total_spend"].sum() * 100).round(2)
results["spend_by_dept"] = dept_spend.to_dict(orient="records")

# 5. Risk concentration
risk = (df.groupby("risk_rating")
          .agg(total_spend=("net_total","sum"),
               supplier_count=("supplier_id","nunique"),
               po_count=("po_number","nunique"),
               avg_defect=("defect_rate_pct","mean"))
          .reset_index())
risk["spend_pct"] = (risk["total_spend"] / risk["total_spend"].sum() * 100).round(2)
results["risk_concentration"] = risk.to_dict(orient="records")

# 6. On-time delivery
otd = (df.groupby("supplier_name")
         .agg(total_pos=("po_number","count"),
              late_pos=("is_late","sum"),
              avg_days_late=("days_late","mean"),
              avg_lead=("actual_lead_days","mean"))
         .reset_index())
otd["on_time_pct"] = ((otd["total_pos"] - otd["late_pos"]) / otd["total_pos"] * 100).round(2)
otd = otd.sort_values("on_time_pct")
results["on_time_delivery"] = otd.to_dict(orient="records")

# 7. Invoice exceptions
inv = df["invoice_match"].value_counts().reset_index()
inv.columns = ["match_type","count"]
inv["pct"] = (inv["count"] / inv["count"].sum() * 100).round(2)
results["invoice_match"] = inv.to_dict(orient="records")

# 8. Pareto
sup_pareto = sup_spend[["supplier_name","total_spend"]].copy()
sup_pareto["cumulative_pct"] = (sup_pareto["total_spend"].cumsum() /
                                 sup_pareto["total_spend"].sum() * 100).round(2)
results["pareto_supplier"] = sup_pareto.to_dict(orient="records")

# 9. Quarterly spend
quarterly = (df.groupby(["year","quarter"])
               .agg(total_spend=("net_total","sum"))
               .reset_index())
results["quarterly_spend"] = quarterly.to_dict(orient="records")

# 10. KPI Summary
total_spend      = df["net_total"].sum()
total_savings    = df["discount_amt"].sum()
preferred_spend  = df[df["is_preferred"]]["net_total"].sum()
high_risk_spend  = df[df["risk_rating"] == "High"]["net_total"].sum()

results["kpi_summary"] = {
    "total_spend":            round(total_spend, 2),
    "total_savings":          round(total_savings, 2),
    "savings_rate_pct":       round(total_savings / total_spend * 100, 2),
    "total_pos":              int(df["po_number"].nunique()),
    "total_suppliers":        int(df["supplier_id"].nunique()),
    "avg_po_value":           round(df.groupby("po_number")["net_total"].sum().mean(), 2),
    "late_delivery_pct":      round(df["is_late"].mean() * 100, 2),
    "invoice_exception_pct":  round(df["is_exception"].mean() * 100, 2),
    "preferred_supplier_pct": round(preferred_spend / total_spend * 100, 2),
    "high_risk_spend_pct":    round(high_risk_spend / total_spend * 100, 2),
    "categories":             int(df["category_id"].nunique()),
    "departments":            int(df["dept_id"].nunique()),
}

with open("data/processed/eda_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

kpi = results["kpi_summary"]
print("EDA complete. Key KPIs:")
print(f"  Total Spend         : GBP{kpi['total_spend']:,.0f}")
print(f"  Total Savings       : GBP{kpi['total_savings']:,.0f}")
print(f"  Savings Rate        : {kpi['savings_rate_pct']}%")
print(f"  Late Delivery Rate  : {kpi['late_delivery_pct']}%")
print(f"  Invoice Exceptions  : {kpi['invoice_exception_pct']}%")
print(f"  Preferred Supplier %: {kpi['preferred_supplier_pct']}%")
print(f"  High-Risk Spend %   : {kpi['high_risk_spend_pct']}%")
print("\nResults saved to data/processed/eda_results.json")