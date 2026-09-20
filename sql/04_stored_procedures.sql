-- =============================================================================
-- Project 5: Procurement Analytics — ProcureEdge Supply Solutions Ltd
-- File: 04_stored_procedures.sql
-- Purpose: Business logic encapsulated as stored procedures / functions
-- =============================================================================

-- 1. fn_supplier_performance_score
CREATE OR REPLACE FUNCTION fn_supplier_performance_score(p_supplier_id CHAR(6))
RETURNS TABLE (
    supplier_name       VARCHAR,
    on_time_pct         NUMERIC,
    defect_score        NUMERIC,
    discount_score      NUMERIC,
    compliance_score    NUMERIC,
    composite_score     NUMERIC,
    performance_grade   CHAR(1)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_total_pos     INTEGER;
    v_late_pos      INTEGER;
    v_avg_defect    NUMERIC;
    v_avg_discount  NUMERIC;
    v_exceptions    INTEGER;
    v_name          VARCHAR;
BEGIN
    SELECT s.supplier_name INTO v_name
    FROM suppliers s WHERE s.supplier_id = p_supplier_id;

    SELECT COUNT(*),
           SUM(CASE WHEN (po.delivery_date - po.po_date) > 14 THEN 1 ELSE 0 END)
    INTO v_total_pos, v_late_pos
    FROM purchase_orders po
    WHERE po.supplier_id = p_supplier_id;

    SELECT ROUND(AVG(li.defect_rate_pct), 4),
           ROUND(AVG(li.discount_pct), 4)
    INTO v_avg_defect, v_avg_discount
    FROM po_line_items li
    JOIN purchase_orders po ON po.po_id = li.po_id
    WHERE po.supplier_id = p_supplier_id;

    SELECT COUNT(*) INTO v_exceptions
    FROM purchase_orders po
    WHERE po.supplier_id = p_supplier_id
      AND po.invoice_match = 'Exception';

    supplier_name    := v_name;
    on_time_pct      := ROUND(CASE WHEN v_total_pos > 0
                               THEN (v_total_pos - v_late_pos)::NUMERIC / v_total_pos * 100
                               ELSE 0 END, 2);
    defect_score     := ROUND(GREATEST(0, (10 - COALESCE(v_avg_defect,0)) / 10 * 100), 2);
    discount_score   := ROUND(LEAST(COALESCE(v_avg_discount,0) / 8 * 100, 100), 2);
    compliance_score := ROUND(GREATEST(0,
                              100 - CASE WHEN v_total_pos > 0
                                         THEN v_exceptions::NUMERIC / v_total_pos * 100
                                         ELSE 0 END), 2);
    composite_score  := ROUND(
                            on_time_pct      * 0.40 +
                            defect_score     * 0.30 +
                            discount_score   * 0.20 +
                            compliance_score * 0.10, 2);
    performance_grade := CASE
        WHEN composite_score >= 80 THEN 'A'
        WHEN composite_score >= 65 THEN 'B'
        WHEN composite_score >= 50 THEN 'C'
        ELSE 'D'
    END;
    RETURN NEXT;
END;
$$;

-- 2. sp_monthly_spend_report
CREATE OR REPLACE FUNCTION sp_monthly_spend_report(p_year INTEGER DEFAULT NULL)
RETURNS TABLE (
    spend_month     TEXT,
    total_spend     NUMERIC,
    total_savings   NUMERIC,
    po_count        BIGINT,
    avg_po_value    NUMERIC,
    mom_change_pct  NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    WITH monthly AS (
        SELECT
            TO_CHAR(po.po_date, 'YYYY-MM')   AS mth,
            SUM(li.net_total)                 AS spend,
            SUM(li.discount_amt)              AS savings,
            COUNT(DISTINCT po.po_id)          AS pos
        FROM purchase_orders po
        JOIN po_line_items li ON li.po_id = po.po_id
        WHERE (p_year IS NULL OR EXTRACT(YEAR FROM po.po_date) = p_year)
        GROUP BY TO_CHAR(po.po_date, 'YYYY-MM')
    )
    SELECT
        m.mth,
        ROUND(m.spend, 2),
        ROUND(m.savings, 2),
        m.pos,
        ROUND(m.spend / NULLIF(m.pos, 0), 2),
        ROUND((m.spend - LAG(m.spend) OVER (ORDER BY m.mth))
              / NULLIF(LAG(m.spend) OVER (ORDER BY m.mth), 0) * 100, 2)
    FROM monthly m
    ORDER BY m.mth;
END;
$$;

-- 3. fn_category_budget_status
CREATE OR REPLACE FUNCTION fn_category_budget_status(p_years INTEGER DEFAULT 2)
RETURNS TABLE (
    category_name   VARCHAR,
    budget          NUMERIC,
    actual_spend    NUMERIC,
    variance        NUMERIC,
    variance_pct    NUMERIC,
    status          TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.category_name,
        c.budget_annual * p_years                                AS budget,
        COALESCE(SUM(li.net_total), 0)                          AS actual_spend,
        COALESCE(SUM(li.net_total), 0) - c.budget_annual * p_years AS variance,
        ROUND((COALESCE(SUM(li.net_total),0) - c.budget_annual * p_years)
              / NULLIF(c.budget_annual * p_years, 0) * 100, 2)  AS variance_pct,
        CASE
            WHEN (COALESCE(SUM(li.net_total),0) - c.budget_annual * p_years)
                 / NULLIF(c.budget_annual * p_years, 0) * 100 > 5  THEN 'Over Budget'
            WHEN (COALESCE(SUM(li.net_total),0) - c.budget_annual * p_years)
                 / NULLIF(c.budget_annual * p_years, 0) * 100 < -5 THEN 'Under Budget'
            ELSE 'On Track'
        END AS status
    FROM categories c
    LEFT JOIN po_line_items   li ON li.category_id = c.category_id
    GROUP BY c.category_name, c.budget_annual
    ORDER BY variance DESC;
END;
$$;

-- 4. sp_flag_high_risk_pos
CREATE OR REPLACE FUNCTION sp_flag_high_risk_pos(
    p_min_value   NUMERIC DEFAULT 50000,
    p_risk_rating VARCHAR DEFAULT 'High'
)
RETURNS TABLE (
    po_number       VARCHAR,
    po_date         DATE,
    supplier_name   VARCHAR,
    risk_rating     VARCHAR,
    po_value        NUMERIC,
    invoice_match   VARCHAR,
    dept_name       VARCHAR,
    flag_reason     TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        po.po_number,
        po.po_date,
        s.supplier_name,
        s.risk_rating,
        ROUND(SUM(li.net_total), 2),
        po.invoice_match,
        d.dept_name,
        STRING_AGG(
            CASE
                WHEN s.risk_rating = p_risk_rating  THEN 'High-risk supplier'
                WHEN po.invoice_match = 'Exception' THEN 'Invoice exception'
                WHEN SUM(li.defect_qty) > 0         THEN 'Defects recorded'
            END,
        '; ') FILTER (WHERE
            s.risk_rating = p_risk_rating OR
            po.invoice_match = 'Exception' OR
            SUM(li.defect_qty) > 0
        ) AS flag_reason
    FROM purchase_orders po
    JOIN suppliers     s  ON s.supplier_id = po.supplier_id
    JOIN departments   d  ON d.dept_id     = po.dept_id
    JOIN po_line_items li ON li.po_id      = po.po_id
    WHERE s.risk_rating = p_risk_rating
       OR po.invoice_match = 'Exception'
    GROUP BY po.po_number, po.po_date, s.supplier_name, s.risk_rating,
             po.invoice_match, d.dept_name
    HAVING SUM(li.net_total) >= p_min_value
    ORDER BY SUM(li.net_total) DESC;
END;
$$;