-- =============================================================================
-- Project 5: Procurement Analytics — ProcureEdge Supply Solutions Ltd
-- File: 02_seed_data.sql
-- Purpose: Reference data inserts (suppliers, categories, departments)
-- =============================================================================

-- Suppliers
INSERT INTO suppliers (supplier_id, supplier_name, country, payment_terms, risk_rating, contract_type, is_preferred, onboarded_date) VALUES
('SUP001','TechParts Global Ltd',       'United Kingdom', 'Net 30', 'Low',    'Framework', TRUE,  '2020-03-01'),
('SUP002','Apex Industrial Supplies',   'Germany',        'Net 45', 'Low',    'Spot',      TRUE,  '2019-07-15'),
('SUP003','NovaMed Components',         'Netherlands',    'Net 30', 'Medium', 'Annual',    TRUE,  '2021-01-10'),
('SUP004','SteelCore Manufacturing',    'Poland',         'Net 60', 'Medium', 'Framework', FALSE, '2018-11-20'),
('SUP005','SwiftLog Packaging',         'Ireland',        'Net 30', 'Low',    'Annual',    TRUE,  '2020-06-01'),
('SUP006','Horizon Electronics',        'Taiwan',         'Net 45', 'High',   'Spot',      FALSE, '2022-02-28'),
('SUP007','QualityFirst Textiles',      'India',          'Net 60', 'High',   'Spot',      FALSE, '2021-09-14'),
('SUP008','Pinnacle Chemical Co.',      'Belgium',        'Net 30', 'Medium', 'Annual',    TRUE,  '2019-04-05'),
('SUP009','ProBuild Materials Ltd',     'Spain',          'Net 45', 'Low',    'Framework', TRUE,  '2020-08-22'),
('SUP010','FastTrack Logistics',        'France',         'Net 30', 'Low',    'Annual',    TRUE,  '2018-03-01'),
('SUP011','Greenfield Agro Supplies',   'Nigeria',        'Net 30', 'Medium', 'Spot',      FALSE, '2023-01-15'),
('SUP012','Pacific Rim Components',     'China',          'Net 60', 'High',   'Spot',      FALSE, '2022-05-10'),
('SUP013','EuroSeal Plastics',          'Czech Republic', 'Net 45', 'Low',    'Framework', TRUE,  '2021-03-18'),
('SUP014','SkyTech Instruments',        'Sweden',         'Net 30', 'Low',    'Annual',    TRUE,  '2019-11-01'),
('SUP015','Meridian Office Supplies',   'United Kingdom', 'Net 30', 'Low',    'Spot',      FALSE, '2020-01-07'),
('SUP016','BrightPath Chemicals',       'Germany',        'Net 45', 'Medium', 'Annual',    TRUE,  '2020-09-30'),
('SUP017','AlphaSteel Corp',            'Ukraine',        'Net 60', 'High',   'Spot',      FALSE, '2021-06-12'),
('SUP018','PrimePack Solutions',        'Portugal',       'Net 30', 'Low',    'Framework', TRUE,  '2022-01-20'),
('SUP019','DeltaTech Electronics',      'South Korea',    'Net 45', 'Medium', 'Annual',    TRUE,  '2020-10-08'),
('SUP020','RoboComponents Inc.',        'USA',            'Net 30', 'Low',    'Framework', TRUE,  '2019-05-15')
ON CONFLICT (supplier_id) DO NOTHING;

-- Categories
INSERT INTO categories (category_id, category_name, budget_annual) VALUES
('CAT01','Raw Materials',            5200000.00),
('CAT02','Electronic Components',    3800000.00),
('CAT03','Packaging & Labelling',    1600000.00),
('CAT04','MRO & Spare Parts',        1200000.00),
('CAT05','IT Hardware & Software',   1000000.00),
('CAT06','Office & Facilities',       600000.00),
('CAT07','Logistics & Transport',    2200000.00),
('CAT08','Professional Services',    1400000.00),
('CAT09','Chemical Supplies',        1800000.00),
('CAT10','Safety & PPE',              400000.00)
ON CONFLICT (category_id) DO NOTHING;

-- Departments
INSERT INTO departments (dept_id, dept_name, dept_head, cost_centre) VALUES
('DEPT01','Manufacturing',      'Chidi Okonkwo',     'CC-1001'),
('DEPT02','Supply Chain',       'Sarah Mitchell',    'CC-1002'),
('DEPT03','IT & Digital',       'Ravi Sharma',       'CC-1003'),
('DEPT04','Finance',            'Emma Balogun',      'CC-1004'),
('DEPT05','HR & Admin',         'James Whitfield',   'CC-1005'),
('DEPT06','Quality Assurance',  'Fatima Al-Hassan',  'CC-1006'),
('DEPT07','Operations',         'David Okafor',      'CC-1007'),
('DEPT08','R&D',                'Priya Nair',        'CC-1008')
ON CONFLICT (dept_id) DO NOTHING;