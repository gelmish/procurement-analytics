"""
04_supplier_performance.py
ProcureEdge Supply Solutions Ltd — Supplier Performance Analysis
Phase 3: Data Analysis — Step 4
"""

import pandas as pd
import numpy as np
import json

df = pd.read_csv("data/processed/procurement_clean.csv", parse_dates=["po_date","delivery_date"])

results = {}

# 1. Full Supplier Scorecard
scorecard = (df.groupby(["supplier_id","supplier_name","risk_rating","is_preferred","contract_type","supplier_country"])
               .agg(
                   total_spend     =("net_total","sum"),
                   po_count        =("po_number","nunique"),
                   avg_po_value    =("net_total","mean"),
                   avg_lead_days   =("actual_lead_days","mean"),
                   on_time_count   =("is_late", lambda x: (~x).sum()),
                   late_count      =("is_late","sum"),
                   avg_days_late   =("days_late","mean"),
                   avg_defect_rate =("defect_rate_pct","mean"),
                   total_defect_qty=("defect_qty","sum"),
                   avg_discount_pct=("discount_pct","mean"),
                   total_savings   =("discount_amt","sum"),
                   exception_count =("is_exception","sum"),
               )
               .reset_index())

scorecard["on_time_pct"]    = (scorecard["on_time_count"] / scorecard["po_count"] * 100).round(2)
scorecard["late_rate_pct"]  = (scorecard["late_count"] / scorecard["po_count"] * 100).round(2)
scorecard["exception_rate"] = (scorecard["exception_count"] / scorecard["po_count"] * 100).round(2)
scorecard["spend_pct"]      = (scorecard["total_spend"] / scorecard["total_spend"].sum() * 100).round(2)

def score_supplier(row):
    otd_score      = row["on_time_pct"] * 0.40
    defect_score   = max(0, (10 - row["avg_defect_rate"]) / 10 * 100) * 0.30
    discount_score = min(row["avg_discount_pct"] / 8 * 100, 100) * 0.20
    exc_score      = max(0, (100 - row["exception_rate"])) * 0.10
    return round(otd_score + defect_score + discount_score + exc_score, 2)

scorecard["performance_score"] = scorecard.apply(score_supplier, axis=1)
scorecard["performance_grade"] = scorecard["performance_score"].apply(
    lambda s: "A" if s >= 80 else ("B" if s >= 65 else ("C" if s >= 50 else "D")))

results["supplier_scorecard"] = scorecard.sort_values("total_spend", ascending=False).to_dict(orient="records")

# 2. Risk matrix
risk_matrix = scorecard[["supplier_name","total_spend","performance_score","risk_rating","spend_pct"]].copy()
risk_matrix["quadrant"] = risk_matrix.apply(lambda r:
    "Strategic"   if r["performance_score"] >= 65 and r["spend_pct"] >= 5 else
    "Leverage"    if r["performance_score"] >= 65 and r["spend_pct"] <  5 else
    "Bottleneck"  if r["performance_score"] <  65 and r["spend_pct"] >= 5 else
    "Non-Critical", axis=1)
results["risk_matrix"] = risk_matrix.to_dict(orient="records")

# 3. Lead time by category
lead_by_cat = (df.groupby("category_name")
                 .agg(avg_lead=("actual_lead_days","mean"),
                      max_lead=("actual_lead_days","max"),
                      min_lead=("actual_lead_days","min"),
                      late_rate=("is_late","mean"))
                 .reset_index())
lead_by_cat["late_rate_pct"] = (lead_by_cat["late_rate"] * 100).round(2)
results["lead_time_by_category"] = lead_by_cat.to_dict(orient="records")

# 4. Defect analysis
defect_sup = (df[df["defect_qty"] > 0]
               .groupby(["supplier_name","risk_rating"])
               .agg(total_defects=("defect_qty","sum"),
                    avg_defect_rate=("defect_rate_pct","mean"),
                    affected_pos=("po_number","nunique"))
               .reset_index()
               .sort_values("total_defects", ascending=False))
results["defect_analysis"] = defect_sup.to_dict(orient="records")

# 5. Country risk exposure
country_risk = (df.groupby(["supplier_country","risk_rating"])
                  .agg(total_spend=("net_total","sum"),
                       supplier_count=("supplier_id","nunique"))
                  .reset_index()
                  .sort_values("total_spend", ascending=False))
results["country_risk"] = country_risk.to_dict(orient="records")

with open("data/processed/supplier_performance.json","w") as f:
    json.dump(results, f, indent=2, default=str)

print("Supplier Performance Analysis complete.")
print("\nSupplier Scorecard (top 10 by spend):")
for r in results["supplier_scorecard"][:10]:
    print(f"  {r['supplier_name']:<35} Score: {r['performance_score']:>5.1f} "
          f"({r['performance_grade']})  OTD: {r['on_time_pct']:>5.1f}%  Risk: {r['risk_rating']}")