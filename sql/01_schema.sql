-- =============================================================================
-- Project 5: Procurement Analytics — ProcureEdge Supply Solutions Ltd
-- File: 01_schema.sql
-- Purpose: PostgreSQL normalised schema (3NF)
-- =============================================================================

DROP TABLE IF EXISTS po_line_items    CASCADE;
DROP TABLE IF EXISTS purchase_orders  CASCADE;
DROP TABLE IF EXISTS contracts        CASCADE;
DROP TABLE IF EXISTS suppliers        CASCADE;
DROP TABLE IF EXISTS categories       CASCADE;
DROP TABLE IF EXISTS departments      CASCADE;

-- 1. SUPPLIERS
CREATE TABLE suppliers (
    supplier_id      CHAR(6)      PRIMARY KEY,
    supplier_name    VARCHAR(120) NOT NULL,
    country          VARCHAR(60)  NOT NULL,
    payment_terms    VARCHAR(20)  NOT NULL DEFAULT 'Net 30',
    risk_rating      VARCHAR(10)  NOT NULL CHECK (risk_rating IN ('Low','Medium','High')),
    contract_type    VARCHAR(20)  NOT NULL CHECK (contract_type IN ('Framework','Annual','Spot')),
    is_preferred     BOOLEAN      NOT NULL DEFAULT FALSE,
    onboarded_date   DATE         NOT NULL DEFAULT CURRENT_DATE,
    active           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 2. CATEGORIES
CREATE TABLE categories (
    category_id     CHAR(5)       PRIMARY KEY,
    category_name   VARCHAR(80)   NOT NULL UNIQUE,
    budget_annual   NUMERIC(14,2) NOT NULL CHECK (budget_annual >= 0),
    active          BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- 3. DEPARTMENTS
CREATE TABLE departments (
    dept_id       CHAR(6)      PRIMARY KEY,
    dept_name     VARCHAR(60)  NOT NULL UNIQUE,
    dept_head     VARCHAR(80),
    cost_centre   VARCHAR(10)  NOT NULL UNIQUE,
    active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 4. CONTRACTS
CREATE TABLE contracts (
    contract_id     SERIAL        PRIMARY KEY,
    supplier_id     CHAR(6)       NOT NULL REFERENCES suppliers(supplier_id),
    category_id     CHAR(5)       NOT NULL REFERENCES categories(category_id),
    contract_ref    VARCHAR(30)   NOT NULL UNIQUE,
    contract_type   VARCHAR(20)   NOT NULL CHECK (contract_type IN ('Framework','Annual','Spot')),
    start_date      DATE          NOT NULL,
    end_date        DATE          NOT NULL,
    contract_value  NUMERIC(14,2),
    discount_rate   NUMERIC(5,2)  DEFAULT 0.00,
    payment_terms   VARCHAR(20)   NOT NULL DEFAULT 'Net 30',
    auto_renew      BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_contract_dates CHECK (end_date > start_date)
);

-- 5. PURCHASE_ORDERS
CREATE TABLE purchase_orders (
    po_id           SERIAL        PRIMARY KEY,
    po_number       VARCHAR(12)   NOT NULL UNIQUE,
    po_date         DATE          NOT NULL,
    delivery_date   DATE          NOT NULL,
    supplier_id     CHAR(6)       NOT NULL REFERENCES suppliers(supplier_id),
    dept_id         CHAR(6)       NOT NULL REFERENCES departments(dept_id),
    po_status       VARCHAR(25)   NOT NULL CHECK (po_status IN (
                        'Delivered','Partially Delivered','Cancelled',
                        'Approved','Pending Approval','In Transit')),
    invoice_match   VARCHAR(15)   NOT NULL CHECK (invoice_match IN ('3-Way','2-Way','Exception')),
    notes           TEXT,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_po_dates CHECK (delivery_date >= po_date)
);

-- 6. PO_LINE_ITEMS
CREATE TABLE po_line_items (
    line_id           SERIAL        PRIMARY KEY,
    po_id             INTEGER       NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    category_id       CHAR(5)       NOT NULL REFERENCES categories(category_id),
    item_description  VARCHAR(150)  NOT NULL,
    quantity          INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price        NUMERIC(12,2) NOT NULL CHECK (unit_price > 0),
    line_total        NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    discount_pct      NUMERIC(5,2)  NOT NULL DEFAULT 0.00 CHECK (discount_pct BETWEEN 0 AND 100),
    discount_amt      NUMERIC(12,2) GENERATED ALWAYS AS
                          (ROUND(quantity * unit_price * discount_pct / 100, 2)) STORED,
    net_total         NUMERIC(14,2) GENERATED ALWAYS AS
                          (ROUND(quantity * unit_price * (1 - discount_pct / 100), 2)) STORED,
    defect_qty        INTEGER       NOT NULL DEFAULT 0 CHECK (defect_qty >= 0),
    defect_rate_pct   NUMERIC(5,2)  GENERATED ALWAYS AS
                          (CASE WHEN quantity > 0
                                THEN ROUND(defect_qty::NUMERIC / quantity * 100, 2)
                                ELSE 0 END) STORED,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_defect_qty CHECK (defect_qty <= quantity)
);