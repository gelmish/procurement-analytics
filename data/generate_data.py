"""
generate_data.py
ProcureEdge Supply Solutions Ltd — Synthetic Procurement Dataset Generator
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

SUPPLIERS = [
    {"supplier_id": f"SUP{str(i).zfill(3)}", "supplier_name": name, "country": country,
     "payment_terms": terms, "risk_rating": risk, "contract_type": ctype, "is_preferred": pref}
    for i, (name, country, terms, risk, ctype, pref) in enumerate([
        ("TechParts Global Ltd",       "United Kingdom",  "Net 30", "Low",    "Framework", True),
        ("Apex Industrial Supplies",   "Germany",         "Net 45", "Low",    "Spot",      True),
        ("NovaMed Components",         "Netherlands",     "Net 30", "Medium", "Annual",    True),
        ("SteelCore Manufacturing",    "Poland",          "Net 60", "Medium", "Framework", False),
        ("SwiftLog Packaging",         "Ireland",         "Net 30", "Low",    "Annual",    True),
        ("Horizon Electronics",        "Taiwan",          "Net 45", "High",   "Spot",      False),
        ("QualityFirst Textiles",      "India",           "Net 60", "High",   "Spot",      False),
        ("Pinnacle Chemical Co.",      "Belgium",         "Net 30", "Medium", "Annual",    True),
        ("ProBuild Materials Ltd",     "Spain",           "Net 45", "Low",    "Framework", True),
        ("FastTrack Logistics",        "France",          "Net 30", "Low",    "Annual",    True),
        ("Greenfield Agro Supplies",   "Nigeria",         "Net 30", "Medium", "Spot",      False),
        ("Pacific Rim Components",     "China",           "Net 60", "High",   "Spot",      False),
        ("EuroSeal Plastics",          "Czech Republic",  "Net 45", "Low",    "Framework", True),
        ("SkyTech Instruments",        "Sweden",          "Net 30", "Low",    "Annual",    True),
        ("Meridian Office Supplies",   "United Kingdom",  "Net 30", "Low",    "Spot",      False),
        ("BrightPath Chemicals",       "Germany",         "Net 45", "Medium", "Annual",    True),
        ("AlphaSteel Corp",            "Ukraine",         "Net 60", "High",   "Spot",      False),
        ("PrimePack Solutions",        "Portugal",        "Net 30", "Low",    "Framework", True),
        ("DeltaTech Electronics",      "South Korea",     "Net 45", "Medium", "Annual",    True),
        ("RoboComponents Inc.",        "USA",             "Net 30", "Low",    "Framework", True),
    ], start=1)
]

CATEGORIES = [
    {"category_id": f"CAT{str(i).zfill(2)}", "category_name": name, "budget_annual": budget}
    for i, (name, budget) in enumerate([
        ("Raw Materials",            5_200_000),
        ("Electronic Components",    3_800_000),
        ("Packaging & Labelling",    1_600_000),
        ("MRO & Spare Parts",        1_200_000),
        ("IT Hardware & Software",   1_000_000),
        ("Office & Facilities",        600_000),
        ("Logistics & Transport",    2_200_000),
        ("Professional Services",    1_400_000),
        ("Chemical Supplies",        1_800_000),
        ("Safety & PPE",               400_000),
    ], start=1)
]

DEPARTMENTS = [
    {"dept_id": f"DEPT{str(i).zfill(2)}", "dept_name": name, "dept_head": head, "cost_centre": cc}
    for i, (name, head, cc) in enumerate([
        ("Manufacturing",       "Chidi Okonkwo",     "CC-1001"),
        ("Supply Chain",        "Sarah Mitchell",    "CC-1002"),
        ("IT & Digital",        "Ravi Sharma",       "CC-1003"),
        ("Finance",             "Emma Balogun",      "CC-1004"),
        ("HR & Admin",          "James Whitfield",   "CC-1005"),
        ("Quality Assurance",   "Fatima Al-Hassan",  "CC-1006"),
        ("Operations",          "David Okafor",      "CC-1007"),
        ("R&D",                 "Priya Nair",        "CC-1008"),
    ], start=1)
]

CATEGORY_SUPPLIER_MAP = {
    "CAT01": ["SUP001","SUP004","SUP009","SUP011","SUP017"],
    "CAT02": ["SUP001","SUP006","SUP012","SUP019","SUP020"],
    "CAT03": ["SUP005","SUP013","SUP018"],
    "CAT04": ["SUP002","SUP009","SUP004"],
    "CAT05": ["SUP014","SUP019","SUP020","SUP006"],
    "CAT06": ["SUP015","SUP018"],
    "CAT07": ["SUP010","SUP005"],
    "CAT08": ["SUP014","SUP010","SUP020"],
    "CAT09": ["SUP008","SUP016","SUP012"],
    "CAT10": ["SUP009","SUP002","SUP015"],
}

CATEGORY_ITEMS = {
    "CAT01": ["Cold Rolled Steel Sheet","Aluminium Ingot","HDPE Granules","PVC Resin","Carbon Fibre Strip"],
    "CAT02": ["PCB Assembly","Capacitor Array","Microcontroller Unit","MOSFET Module","Sensor Array"],
    "CAT03": ["Corrugated Box 30x20","Shrink Wrap Film","Pallet Wrap Roll","Printed Label Sheet","Foam Insert Set"],
    "CAT04": ["Bearing Assembly","Hydraulic Seal Kit","Conveyor Belt Section","Lubricant 20L","Filter Element Set"],
    "CAT05": ["Laptop Dell XPS","Server Rack Unit","Network Switch 24-Port","UPS Battery","Software Licence"],
    "CAT06": ["Office Chair","A4 Paper Ream","Printer Cartridge","Cleaning Supplies Pack","Stationery Bundle"],
    "CAT07": ["Freight Forwarding Service","Last-Mile Delivery","Warehouse Storage","Cold Chain Transport","Customs Clearance"],
    "CAT08": ["Consulting Day Rate","Audit Services","Legal Advisory","Training Programme","IT Support Contract"],
    "CAT09": ["Solvent IPA 25L","Adhesive Compound","Coating Agent 10L","Cleaner Degreaser","Flux Paste"],
    "CAT10": ["Hard Hat Class E","Safety Gloves Box","Hi-Vis Vest Pack","Steel Toe Boot Pair","Eye Protection Box"],
}

records = []
po_counter = 1

for _ in range(1200):
    cat    = random.choice(CATEGORIES)
    cat_id = cat["category_id"]
    sup_id = random.choice(CATEGORY_SUPPLIER_MAP[cat_id])
    dept   = random.choice(DEPARTMENTS)
    dept_id = dept["dept_id"]

    month_weights = [6,7,8,10,9,12,8,8,9,11,11,13]
    month = random.choices(range(1,13), weights=month_weights)[0]
    day   = random.randint(1, 28)
    year  = random.choices([2023, 2024], weights=[48, 52])[0]
    order_date = datetime(year, month, day)

    sup = next(s for s in SUPPLIERS if s["supplier_id"] == sup_id)
    base_lead = {"Low": 7, "Medium": 14, "High": 25}[sup["risk_rating"]]
    lead_time = max(1, int(np.random.normal(base_lead, base_lead * 0.3)))
    delivery_date = order_date + timedelta(days=lead_time)
    if random.random() < 0.18:
        delivery_date += timedelta(days=random.randint(3, 30))

    n_lines = random.choices([1,2,3,4,5], weights=[40,30,15,10,5])[0]
    items = random.sample(CATEGORY_ITEMS[cat_id], min(n_lines, len(CATEGORY_ITEMS[cat_id])))

    for item in items:
        price_ranges = {
            "CAT01": (80, 3500), "CAT02": (15, 1200), "CAT03": (2, 120),
            "CAT04": (25, 800),  "CAT05": (200, 4500),"CAT06": (3, 250),
            "CAT07": (500, 8000),"CAT08": (800, 12000),"CAT09": (40, 600),
            "CAT10": (8, 180),
        }
        lo, hi = price_ranges[cat_id]
        unit_price   = round(random.uniform(lo, hi), 2)
        quantity     = random.randint(1, 200)
        line_total   = round(unit_price * quantity, 2)
        discount_pct = round(random.uniform(0, 8 if sup["is_preferred"] else 3), 2)
        discount_amt = round(line_total * discount_pct / 100, 2)
        net_total    = round(line_total - discount_amt, 2)

        defect_qty = 0
        if sup["risk_rating"] == "High" and random.random() < 0.22:
            defect_qty = random.randint(1, max(1, int(quantity * 0.08)))
        elif sup["risk_rating"] == "Medium" and random.random() < 0.10:
            defect_qty = random.randint(1, max(1, int(quantity * 0.04)))

        today = datetime(2025, 1, 1)
        if delivery_date < today:
            status = random.choices(
                ["Delivered","Partially Delivered","Cancelled"],
                weights=[82, 12, 6])[0]
        else:
            status = random.choices(
                ["Approved","Pending Approval","In Transit"],
                weights=[55, 25, 20])[0]

        invoice_match = "3-way" if random.random() < 0.74 else random.choice(["2-way","Exception"])

        records.append({
            "po_number": f"PO-{str(po_counter).zfill(5)}",
            "po_date": order_date.strftime("%Y-%m-%d"),
            "delivery_date": delivery_date.strftime("%Y-%m-%d"),
            "supplier_id": sup_id, "supplier_name": sup["supplier_name"],
            "supplier_country": sup["country"], "risk_rating": sup["risk_rating"],
            "is_preferred": sup["is_preferred"], "payment_terms": sup["payment_terms"],
            "contract_type": sup["contract_type"], "category_id": cat_id,
            "category_name": cat["category_name"], "dept_id": dept_id,
            "dept_name": dept["dept_name"], "cost_centre": dept["cost_centre"],
            "item_description": item, "quantity": quantity, "unit_price": unit_price,
            "line_total": line_total, "discount_pct": discount_pct,
            "discount_amt": discount_amt, "net_total": net_total,
            "lead_time_days": lead_time, "defect_qty": defect_qty,
            "defect_rate_pct": round(defect_qty / quantity * 100, 2),
            "po_status": status, "invoice_match": invoice_match,
            "year": order_date.year,
            "quarter": f"Q{(order_date.month - 1)//3 + 1}",
            "month": order_date.strftime("%Y-%m"),
        })
    po_counter += 1

df = pd.DataFrame(records)
out_raw = os.path.join(os.path.dirname(__file__), "raw", "procurement_data.csv")
df.to_csv(out_raw, index=False)
print(f"Raw dataset saved: {len(df):,} rows x {len(df.columns)} columns")
print(f"Total spend: GBP{df['net_total'].sum():,.0f}")

pd.DataFrame(SUPPLIERS).to_csv(os.path.join(os.path.dirname(__file__), "raw", "suppliers.csv"), index=False)
pd.DataFrame(CATEGORIES).to_csv(os.path.join(os.path.dirname(__file__), "raw", "categories.csv"), index=False)
pd.DataFrame(DEPARTMENTS).to_csv(os.path.join(os.path.dirname(__file__), "raw", "departments.csv"), index=False)
print("Lookup tables saved.")