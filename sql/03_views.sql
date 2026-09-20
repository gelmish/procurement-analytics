-- =============================================================================
-- Project 5: Procurement Analytics — ProcureEdge Supply Solutions Ltd
-- File: 03_views.sql
-- Purpose: Analytical views for dashboard and reporting
-- =============================================================================

-- 1. v_spend_by_category
CREATE OR REPLACE VIEW v_spend_by_category AS
SELECT
    c.category_id,
    c.category_name,
    c.budget_annual,
    c.budget_annual * 2                                   AS budget_2yr,
    COUNT(DISTINCT po.po_id)                              AS po_count,
    SUM(li.net_total)                                     AS actual_spend,
    SUM(li.discount_amt)                                  AS total_savings,
    ROUND(SUM(li.net_total) / NULLIF(SUM(SUM(li.net_total)) OVER (), 0) * 100, 2)
                                                          AS spend_pct,
    ROUND(SUM(li.net_total) - c.budget_annual * 2, 2)    AS budget_variance,
    ROUND((SUM(li.net_total) - c.budget_annual * 2)
          / NULLIF(c.budget_annual * 2, 0) * 100, 2)     AS variance_pct,
    ROUND(AVG(li.discount_pct), 2)                       AS avg_discount_pct
FROM categories c
LEFT JOIN po_line_items li ON li.category_id = c.category_id
LEFT JOIN purchase_orders po ON po.po_id = li.po_id
GROUP BY c.category_id, c.category_name, c.budget_annual;

-- 2. v_supplier_scorecard
CREATE OR REPLACE VIEW v_supplier_scorecard AS
WITH delivery AS (
    SELECT
        po.supplier_id,
        COUNT(*)                                          AS total_pos,
        AVG((po.delivery_date - po.po_date))              AS avg_lead_days
    FROM purchase_orders po
    GROUP BY po.supplier_id
),
spend AS (
    SELECT
        po.supplier_id,
        SUM(li.net_total)                                 AS total_spend,
        SUM(li.discount_amt)                              AS total_savings,
        AVG(li.discount_pct)                              AS avg_discount_pct,
        SUM(li.defect_qty)                                AS total_defects,
        AVG(li.defect_rate_pct)                           AS avg_defect_rate,
        SUM(CASE WHEN po.invoice_match = 'Exception'
                 THEN 1 ELSE 0 END)                       AS exceptions
    FROM po_line_items li
    JOIN purchase_orders po ON po.po_id = li.po_id
    GROUP BY po.supplier_id
)
SELECT
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.risk_rating,
    s.is_preferred,
    s.contract_type,
    sp.total_spend,
    sp.total_savings,
    ROUND(sp.avg_discount_pct, 2)                        AS avg_discount_pct,
    d.total_pos,
    ROUND(d.avg_lead_days, 1)                            AS avg_lead_days,
    sp.total_defects,
    ROUND(sp.avg_defect_rate, 2)                         AS avg_defect_rate,
    sp.exceptions,
    ROUND(sp.exceptions::NUMERIC / NULLIF(d.total_pos,0) * 100, 2) AS exception_rate_pct,
    ROUND(sp.total_spend / NULLIF(SUM(sp.total_spend) OVER (), 0) * 100, 2) AS spend_pct
FROM suppliers s
LEFT JOIN delivery d  ON d.supplier_id = s.supplier_id
LEFT JOIN spend    sp ON sp.supplier_id = s.supplier_id
ORDER BY sp.total_spend DESC NULLS LAST;

-- 3. v_monthly_spend_trend
CREATE OR REPLACE VIEW v_monthly_spend_trend AS
SELECT
    DATE_TRUNC('month', po.po_date)        AS spend_month,
    TO_CHAR(po.po_date, 'YYYY-MM')         AS month_label,
    EXTRACT(YEAR FROM po.po_date)::INT      AS year,
    EXTRACT(QUARTER FROM po.po_date)::INT   AS quarter,
    COUNT(DISTINCT po.po_id)                AS po_count,
    SUM(li.net_total)                       AS total_spend,
    SUM(li.discount_amt)                    AS total_savings,
    ROUND(AVG(li.discount_pct), 2)          AS avg_discount_pct
FROM purchase_orders po
JOIN po_line_items li ON li.po_id = po.po_id
GROUP BY DATE_TRUNC('month', po.po_date),
         TO_CHAR(po.po_date, 'YYYY-MM'),
         EXTRACT(YEAR FROM po.po_date),
         EXTRACT(QUARTER FROM po.po_date)
ORDER BY spend_month;

-- 4. v_po_delivery_performance
CREATE OR REPLACE VIEW v_po_delivery_performance AS
SELECT
    po.po_id,
    po.po_number,
    po.po_date,
    po.delivery_date,
    s.supplier_name,
    s.risk_rating,
    d.dept_name,
    po.po_status,
    po.invoice_match,
    (po.delivery_date - po.po_date)        AS actual_lead_days,
    SUM(li.net_total)                      AS po_value,
    SUM(li.defect_qty)                     AS total_defects,
    CASE WHEN po.delivery_date > po.po_date + INTERVAL '14 days'
         THEN TRUE ELSE FALSE END          AS is_potentially_late
FROM purchase_orders po
JOIN suppliers     s  ON s.supplier_id = po.supplier_id
JOIN departments   d  ON d.dept_id     = po.dept_id
JOIN po_line_items li ON li.po_id      = po.po_id
GROUP BY po.po_id, po.po_number, po.po_date, po.delivery_date,
         s.supplier_name, s.risk_rating, d.dept_name,
         po.po_status, po.invoice_match;

-- 5. v_department_spend
CREATE OR REPLACE VIEW v_department_spend AS
SELECT
    d.dept_id,
    d.dept_name,
    d.dept_head,
    d.cost_centre,
    COUNT(DISTINCT po.po_id)               AS po_count,
    SUM(li.net_total)                      AS total_spend,
    SUM(li.discount_amt)                   AS total_savings,
    ROUND(SUM(li.net_total) / NULLIF(SUM(SUM(li.net_total)) OVER (), 0) * 100, 2) AS spend_pct,
    ROUND(AVG(li.net_total), 2)            AS avg_line_value
FROM departments d
LEFT JOIN purchase_orders po ON po.dept_id     = d.dept_id
LEFT JOIN po_line_items   li ON li.po_id       = po.po_id
GROUP BY d.dept_id, d.dept_name, d.dept_head, d.cost_centre
ORDER BY total_spend DESC NULLS LAST;

-- 6. v_invoice_exceptions
CREATE OR REPLACE VIEW v_invoice_exceptions AS
SELECT
    po.po_number,
    po.po_date,
    s.supplier_name,
    s.risk_rating,
    po.invoice_match,
    d.dept_name,
    SUM(li.net_total) AS po_value
FROM purchase_orders po
JOIN suppliers     s  ON s.supplier_id = po.supplier_id
JOIN departments   d  ON d.dept_id     = po.dept_id
JOIN po_line_items li ON li.po_id      = po.po_id
WHERE po.invoice_match = 'Exception'
GROUP BY po.po_number, po.po_date, s.supplier_name,
         s.risk_rating, po.invoice_match, d.dept_name
ORDER BY po_value DESC;