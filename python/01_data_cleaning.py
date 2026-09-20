"""
01_data_cleaning.py
ProcureEdge Supply Solutions Ltd — Data Cleaning & Validation
Phase 3: Data Analysis — Step 1
"""

import pandas as pd
import numpy as np
import os

RAW_PATH    = "data/raw/procurement_data.csv"
CLEAN_PATH  = "data/processed/procurement_clean.csv"
REPORT_PATH = "data/processed/cleaning_report.txt"

os.makedirs("data/processed", exist_ok=True)

df = pd.read_csv(RAW_PATH)
original_shape = df.shape
report_lines = [
    "=" * 60,
    "DATA CLEANING REPORT — ProcureEdge Supply Solutions Ltd",
    "=" * 60,
    f"Source file : {RAW_PATH}",
    f"Loaded      : {original_shape[0]:,} rows x {original_shape[1]} columns", ""
]

# 1. Type conversions
df["po_date"]       = pd.to_datetime(df["po_date"])
df["delivery_date"] = pd.to_datetime(df["delivery_date"])
df["is_preferred"]  = df["is_preferred"].astype(bool)
report_lines.append("[1] Date columns cast to datetime. is_preferred cast to bool.")

# 2. Null check
null_counts = df.isnull().sum()
null_report = null_counts[null_counts > 0]
if null_report.empty:
    report_lines.append("[2] No null values found in any column.")
else:
    report_lines.append(f"[2] Nulls detected:\n{null_report.to_string()}")
    df.dropna(subset=["po_number","supplier_id","category_id","net_total"], inplace=True)

# 3. Duplicates
dupes = df.duplicated().sum()
report_lines.append(f"[3] Duplicate rows found: {dupes}")
if dupes > 0:
    df.drop_duplicates(inplace=True)

# 4. Negative/zero values
bad_price = (df["unit_price"] <= 0).sum()
bad_qty   = (df["quantity"]   <= 0).sum()
bad_total = (df["net_total"]  <  0).sum()
report_lines.append(f"[4] Negative/zero unit_price: {bad_price} | quantity: {bad_qty} | net_total: {bad_total}")
df = df[(df["unit_price"] > 0) & (df["quantity"] > 0) & (df["net_total"] >= 0)]

# 5. Derived date fields
df["actual_lead_days"] = (df["delivery_date"] - df["po_date"]).dt.days
df["is_late"]          = df["actual_lead_days"] > df["lead_time_days"]
df["days_late"]        = (df["actual_lead_days"] - df["lead_time_days"]).clip(lower=0)
df["year"]             = df["po_date"].dt.year
df["quarter"]          = "Q" + df["po_date"].dt.quarter.astype(str)
df["month"]            = df["po_date"].dt.to_period("M").astype(str)
df["week"]             = df["po_date"].dt.isocalendar().week.astype(int)
report_lines.append("[5] Derived: actual_lead_days, is_late, days_late, week.")

# 6. Standardise text
for col in ["po_status","invoice_match","risk_rating","contract_type","payment_terms"]:
    df[col] = df[col].str.strip().str.title()
report_lines.append("[6] Text fields stripped and title-cased.")

# 7. Outlier flagging
Q1, Q3 = df["net_total"].quantile(0.25), df["net_total"].quantile(0.75)
IQR = Q3 - Q1
df["is_high_value"] = df["net_total"] > (Q3 + 3 * IQR)
report_lines.append(f"[7] High-value outliers flagged: {df['is_high_value'].sum()} rows")

# 8. Invoice exception flag
df["is_exception"] = df["invoice_match"] == "Exception"
report_lines.append(f"[8] Invoice exceptions flagged: {df['is_exception'].sum()}")

# 9. Discount validation
df["savings_validated"] = (df["discount_pct"] * df["line_total"] / 100).round(2)
mismatch = (abs(df["savings_validated"] - df["discount_amt"]) > 0.05).sum()
report_lines.append(f"[9] Discount validation mismatches (>5p): {mismatch}")

# Final summary
report_lines += [
    "", "FINAL DATASET SUMMARY", "-" * 40,
    f"Rows         : {len(df):,}",
    f"Columns      : {len(df.columns)}",
    f"POs          : {df['po_number'].nunique():,}",
    f"Suppliers    : {df['supplier_id'].nunique()}",
    f"Date range   : {df['po_date'].min().date()} to {df['po_date'].max().date()}",
    f"Total spend  : GBP{df['net_total'].sum():,.2f}",
    f"Total savings: GBP{df['discount_amt'].sum():,.2f}",
    f"Late POs     : {df['is_late'].sum():,} ({df['is_late'].mean()*100:.1f}%)",
    f"Exceptions   : {df['is_exception'].sum():,} ({df['is_exception'].mean()*100:.1f}%)",
]

df.to_csv(CLEAN_PATH, index=False)
report_text = "\n".join(report_lines)
with open(REPORT_PATH, "w") as f:
    f.write(report_text)
print(report_text)
print(f"\nClean file saved: {CLEAN_PATH}")