-- =============================================================================
-- Project 5: Procurement Analytics — ProcureEdge Supply Solutions Ltd
-- File: 05_indexes.sql
-- Purpose: Performance indexes for analytical queries
-- =============================================================================

-- purchase_orders
CREATE INDEX IF NOT EXISTS idx_po_supplier    ON purchase_orders (supplier_id);
CREATE INDEX IF NOT EXISTS idx_po_dept        ON purchase_orders (dept_id);
CREATE INDEX IF NOT EXISTS idx_po_date        ON purchase_orders (po_date);
CREATE INDEX IF NOT EXISTS idx_po_status      ON purchase_orders (po_status);
CREATE INDEX IF NOT EXISTS idx_po_invoice     ON purchase_orders (invoice_match);
CREATE INDEX IF NOT EXISTS idx_po_date_sup    ON purchase_orders (po_date, supplier_id);

-- po_line_items
CREATE INDEX IF NOT EXISTS idx_li_po          ON po_line_items (po_id);
CREATE INDEX IF NOT EXISTS idx_li_category    ON po_line_items (category_id);
CREATE INDEX IF NOT EXISTS idx_li_net_total   ON po_line_items (net_total);

-- suppliers
CREATE INDEX IF NOT EXISTS idx_sup_risk       ON suppliers (risk_rating);
CREATE INDEX IF NOT EXISTS idx_sup_preferred  ON suppliers (is_preferred);
CREATE INDEX IF NOT EXISTS idx_sup_country    ON suppliers (country);

-- composite
CREATE INDEX IF NOT EXISTS idx_po_date_status ON purchase_orders (po_date, po_status, supplier_id);