"""
03_spend_analysis.py
ProcureEdge Supply Solutions Ltd — Spend Analysis
Phase 3: Data Analysis — Step 3
"""

import pandas as pd
import numpy as np
import json, os

df = pd.read_csv("data/processed/procurement_clean.csv", parse_dates=["po_date","delivery_date"])

results = {}

# 1. Budget vs Actual by Category
budgets = {
    "Raw Materials": 5_200_000, "Electronic Components": 3_800_000,
    "Packaging & Labelling": 1_600_000, "MRO & Spare Parts": 1_200_000,
    "IT Hardware & Software": 1_000_000, "Office & Facilities": 600_000,
    "Logistics & Transport": 2_200_000, "Professional Services": 1_400_000,
    "Chemical Supplies": 1_800_000, "Safety & PPE": 400_000,
}
cat_actual = df.groupby("category_name")["net_total"].sum().reset_index()
cat_actual.columns = ["category_name","actual_spend"]
cat_actual["budget_2yr"]   = cat_actual["category_name"].map(lambda x: budgets.get(x, 0) * 2)
cat_actual["variance"]     = cat_actual["actual_spend"] - cat_actual["budget_2yr"]
cat_actual["variance_pct"] = (cat_actual["variance"] / cat_actual["budget_2yr"] * 100).round(2)
cat_actual["status"]       = cat_actual["variance_pct"].apply(
    lambda x: "Over Budget" if x > 5 else ("Under Budget" if x < -5 else "On Track"))
results["budget_vs_actual"] = cat_actual.sort_values("variance", ascending=False).to_dict(orient="records")

# 2. Pareto
sup = df.groupby("supplier_name")["net_total"].sum().sort_values(ascending=False).reset_index()
sup["cumulative"]     = sup["net_total"].cumsum()
sup["cumulative_pct"] = sup["cumulative"] / sup["net_total"].sum() * 100
results["pareto"] = {
    "top_supplier_count": 3,
    "top_spend": round(sup.head(3)["net_total"].sum(), 2),
    "top_spend_pct": round(sup.head(3)["net_total"].sum() / sup["net_total"].sum() * 100, 2),
    "detail": sup.to_dict(orient="records")
}

# 3. Year-on-Year spend
yoy = df.groupby(["year","category_name"])["net_total"].sum().reset_index()
yoy_pivot = yoy.pivot(index="category_name", columns="year", values="net_total").fillna(0).reset_index()
if 2023 in yoy_pivot.columns and 2024 in yoy_pivot.columns:
    yoy_pivot["yoy_change"]     = yoy_pivot[2024] - yoy_pivot[2023]
    yoy_pivot["yoy_change_pct"] = ((yoy_pivot[2024] - yoy_pivot[2023]) / yoy_pivot[2023].replace(0, np.nan) * 100).round(2)
yoy_pivot.columns = [str(c) for c in yoy_pivot.columns]
results["yoy_comparison"] = yoy_pivot.to_dict(orient="records")

# 4. Savings deep-dive
savings_by_cat = (df.groupby("category_name")
                    .agg(gross_spend=("line_total","sum"),
                         net_spend=("net_total","sum"),
                         total_savings=("discount_amt","sum"),
                         avg_discount_pct=("discount_pct","mean"))
                    .reset_index())
savings_by_cat["savings_rate"] = (savings_by_cat["total_savings"] / savings_by_cat["gross_spend"] * 100).round(2)
results["savings_analysis"] = savings_by_cat.sort_values("total_savings", ascending=False).to_dict(orient="records")

# 5. Contract type spend
contract_spend = (df.groupby("contract_type")
                    .agg(total_spend=("net_total","sum"),
                         avg_discount=("discount_pct","mean"),
                         po_count=("po_number","nunique"))
                    .reset_index())
contract_spend["spend_pct"] = (contract_spend["total_spend"] / contract_spend["total_spend"].sum() * 100).round(2)
results["contract_type_spend"] = contract_spend.to_dict(orient="records")

# 6. Preferred vs non-preferred
pref = (df.groupby("is_preferred")
          .agg(total_spend=("net_total","sum"),
               avg_discount=("discount_pct","mean"),
               avg_lead=("actual_lead_days","mean"),
               late_rate=("is_late","mean"),
               defect_rate=("defect_rate_pct","mean"),
               po_count=("po_number","nunique"))
          .reset_index())
pref["label"] = pref["is_preferred"].map({True:"Preferred", False:"Non-Preferred"})
results["preferred_vs_not"] = pref.to_dict(orient="records")

with open("data/processed/spend_analysis.json","w") as f:
    json.dump(results, f, indent=2, default=str)

print("Spend analysis complete.")
print(f"  Pareto: top 3 suppliers = {results['pareto']['top_spend_pct']}% of spend")
print("\nBudget vs Actual:")
for r in results["budget_vs_actual"]:
    flag = "!!" if r["status"] == "Over Budget" else "  "
    print(f"  {flag} {r['category_name']:<30} {r['status']:<14} {r['variance_pct']:>+.1f}%")