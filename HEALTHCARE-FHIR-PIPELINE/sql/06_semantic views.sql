-- View 1: vw_patient_summary
ALTER VIEW dbo.vw_patient_summary AS
WITH VisitTotals AS (
    -- Pre-aggregate visits per patient
    SELECT 
        person_id, 
        COUNT(visit_occurrence_id) AS total_encounters
    FROM dbo.visit_occurrence
    GROUP BY person_id
),
CostTotals AS (
    -- Pre-aggregate costs per patient
    SELECT 
        person_id, 
        COUNT(cost_id) AS total_claims,
        CAST(SUM(ISNULL(total_charge, 0)) AS DECIMAL(18,2)) AS total_spend,
        CAST(SUM(ISNULL(total_paid, 0)) AS DECIMAL(18,2)) AS total_payer
    FROM dbo.cost
    GROUP BY person_id
)
-- Join the pre-aggregated 1-to-1 results back to the person table
SELECT 
    p.person_id AS patient_token,
    p.gender_source_value AS gender,
    p.year_of_birth AS birth_year,
    p.race_source_value AS race,
    ISNULL(v.total_encounters, 0) AS total_encounters,
    ISNULL(c.total_claims, 0) AS total_claims,
    ISNULL(c.total_spend, 0.00) AS total_spend,
    ISNULL(c.total_payer, 0.00) AS total_payer
FROM dbo.person p
LEFT JOIN VisitTotals v ON p.person_id = v.person_id
LEFT JOIN CostTotals c ON p.person_id = c.person_id;
GO
Select top 10* from [dbo].[vw_patient_summary]
-- View 2: vw_high_cost_patients
DROP VIEW IF EXISTS dbo.vw_high_cost_patients;
GO

CREATE VIEW dbo.vw_high_cost_patients AS
WITH patient_totals AS (
    SELECT 
        p.person_id,
        COUNT(DISTINCT c.cost_id) AS claim_count,
        SUM(c.total_charge) AS total_spend,
        SUM(c.total_paid) AS total_payer,
        SUM(c.paid_by_patient) AS total_oop
    FROM dbo.person p
    JOIN dbo.visit_occurrence vo ON p.person_id = vo.person_id
    JOIN dbo.cost c ON vo.visit_occurrence_id = c.cost_event_id
    WHERE c.total_charge IS NOT NULL
    GROUP BY p.person_id
),
p90 AS (
    SELECT 
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_spend) OVER () AS threshold 
    FROM patient_totals
)
SELECT 
    pt.person_id AS patient_token,
    p.gender_source_value AS gender,
    p.year_of_birth AS birth_year,
    p.race_source_value AS race,
    p.person_source_value AS zip_3digit,
    pt.claim_count,
    ROUND(pt.total_spend, 2) AS total_spend,
    ROUND(pt.total_payer, 2) AS total_payer_covered,
    ROUND(pt.total_oop, 2) AS total_out_of_pocket,
    ROUND(pt.total_oop / NULLIF(pt.total_spend, 0) * 100, 1) AS patient_burden_pct,
    CASE 
        WHEN pt.total_spend >= (SELECT TOP 1 threshold FROM p90)
        THEN 'High Cost (Top 10%)'
        ELSE 'Standard'
    END AS cost_category
FROM patient_totals pt
CROSS JOIN (SELECT TOP 1 threshold FROM p90) p9
JOIN dbo.person p ON pt.person_id = p.person_id;
GO
Select top 10* from [dbo].[vw_high_cost_patients]

-- View 3: vw_readmissions (Same as before)
DROP VIEW IF EXISTS dbo.vw_readmissions;
GO

CREATE VIEW dbo.vw_readmissions AS
WITH encounters AS (
    SELECT 
        vo.visit_occurrence_id AS first_encounter,
        vo.person_id AS patient_token,
        vo.visit_start_date AS first_date,
        vo.visit_end_date AS discharge_date,
        YEAR(vo.visit_start_date) AS first_year,
        MONTH(vo.visit_start_date) AS first_month,
        p.gender_source_value AS gender,
        p.person_source_value AS zip_3digit
    FROM dbo.visit_occurrence vo
    JOIN dbo.person p ON vo.person_id = p.person_id
    WHERE vo.visit_start_date IS NOT NULL
),
readmission_pairs AS (
    SELECT 
        a.patient_token,
        a.first_encounter,
        b.first_encounter AS readmit_encounter,
        a.first_date,
        b.first_date AS readmit_date,
        DATEDIFF(DAY, a.discharge_date, b.first_date) AS days_between,
        a.first_year,
        a.first_month,
        a.gender,
        a.zip_3digit
    FROM encounters a
    JOIN encounters b
        ON a.patient_token = b.patient_token
        AND a.first_encounter <> b.first_encounter
        AND b.first_date > a.discharge_date
        AND DATEDIFF(DAY, a.discharge_date, b.first_date) <= 30
        AND DATEDIFF(DAY, a.discharge_date, b.first_date) > 0
)
SELECT 
    patient_token,
    first_encounter,
    readmit_encounter,
    first_date,
    readmit_date,
    days_between,
    first_year,
    first_month,
    gender,
    zip_3digit,
    CASE 
        WHEN days_between <= 7 THEN '0-7 days'
        WHEN days_between <= 14 THEN '8-14 days'
        WHEN days_between <= 21 THEN '15-21 days'
        ELSE '22-30 days'
    END AS readmit_window
FROM readmission_pairs;
GO
Select top 10* from [dbo].[vw_readmissions]

-- View 4: Clinical Claims Mapping 
DROP VIEW IF EXISTS dbo.vw_claims_with_conditions;
GO

CREATE VIEW dbo.vw_claims_with_conditions AS
SELECT 
    co.condition_occurrence_id, -- Verified in your schema
    co.person_id,               -- Verified in your schema
    co.condition_start_date,    -- Verified in your schema
    c.concept_name AS condition_name,
    p.gender_source_value AS gender,
    p.year_of_birth,
    p.race_source_value AS race
FROM dbo.condition_occurrence co
JOIN dbo.person p ON co.person_id = p.person_id
JOIN dbo.concept c ON co.condition_concept_id = c.concept_id;
GO

-- Verification
SELECT TOP 10 * FROM dbo.vw_claims_with_conditions;