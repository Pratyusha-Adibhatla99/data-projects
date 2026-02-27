
--View 1: High-Cost Patients (WORKING)DROP VIEW IF EXISTS vw_high_cost_patients;
DROP VIEW IF EXISTS vw_high_cost_patients;
GO

CREATE VIEW vw_high_cost_patients AS
WITH patient_totals AS (
    SELECT 
        REPLACE(fc.patient_token, 'urn:uuid:', '') AS patient_token,
        COUNT(*) AS claim_count,
        SUM(fc.total_cost) AS total_spend,
        SUM(fc.payer_coverage) AS total_payer,
        SUM(fc.patient_out_of_pocket) AS total_oop
    FROM fact_claims fc 
    WHERE fc.total_cost IS NOT NULL 
    GROUP BY REPLACE(fc.patient_token, 'urn:uuid:', '')
),
p90 AS (
    SELECT 
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_spend) OVER () AS threshold 
    FROM patient_totals
)
SELECT 
    pt.patient_token, 
    dp.gender, 
    dp.birth_year, 
    dp.race,
    dp.zip_3digit,
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
JOIN dim_patient dp ON pt.patient_token = dp.patient_token;
GO
-- Check if dim_patient has any data
SELECT COUNT(*) FROM dim_patient;


SELECT TOP 10 * FROM vw_high_cost_patients ORDER BY total_spend DESC;




--View 2: Patient Summary (WORKING)

DROP VIEW IF EXISTS vw_patient_summary;
GO

CREATE VIEW vw_patient_summary AS
SELECT 
    dp.patient_token,
    dp.gender,
    dp.birth_year,
    dp.race,
    dp.zip_3digit,
    COUNT(DISTINCT fc.claim_token) AS total_claims,
    SUM(fc.total_cost) AS total_spend,
    SUM(fc.payer_coverage) AS total_payer,
    SUM(fc.patient_out_of_pocket) AS total_oop,
    AVG(fc.total_cost) AS avg_claim_cost,
    MIN(dd.full_date) AS first_service_date,
    MAX(dd.full_date) AS last_service_date
FROM dim_patient dp
LEFT JOIN fact_claims fc ON dp.patient_token = REPLACE(fc.patient_token, 'urn:uuid:', '')
LEFT JOIN dim_date dd ON fc.date_key = dd.date_key
GROUP BY 
    dp.patient_token,
    dp.gender,
    dp.birth_year,
    dp.race,
    dp.zip_3digit;
GO

--TEST

SELECT TOP 10 * FROM vw_patient_summary 
WHERE total_claims > 0
ORDER BY total_spend DESC;

--View 3. Readmissions 

DROP VIEW IF EXISTS vw_readmissions;
GO

CREATE VIEW vw_readmissions AS
WITH encounters AS (
    SELECT 
        fe.encounter_token,
        REPLACE(fe.patient_token, 'urn:uuid:', '') AS patient_token,
        fe.date_key,
        dd.full_date AS encounter_date,
        dd.year,
        dd.month,
        dp.gender,
        dp.zip_3digit,
        fe.encounter_type,
        fe.reason_description
    FROM fact_encounter fe 
    JOIN dim_date dd ON fe.date_key = dd.date_key 
    JOIN dim_patient dp ON REPLACE(fe.patient_token, 'urn:uuid:', '') = dp.patient_token
    WHERE dd.full_date IS NOT NULL
),
readmission_pairs AS (
    SELECT 
        a.patient_token,
        a.encounter_token AS first_encounter, 
        b.encounter_token AS readmit_encounter,
        a.encounter_date AS first_date, 
        b.encounter_date AS readmit_date,
        DATEDIFF(DAY, CAST(a.encounter_date AS DATE), CAST(b.encounter_date AS DATE)) AS days_between,
        a.year AS first_year,
        a.month AS first_month,
        a.gender,
        a.zip_3digit,
        a.reason_description AS first_reason,
        b.reason_description AS readmit_reason
    FROM encounters a 
    JOIN encounters b
        ON a.patient_token = b.patient_token 
        AND a.encounter_token <> b.encounter_token
        AND CAST(b.encounter_date AS DATE) > CAST(a.encounter_date AS DATE)
        AND DATEDIFF(DAY, CAST(a.encounter_date AS DATE), CAST(b.encounter_date AS DATE)) <= 30
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
    first_reason,
    readmit_reason,
    CASE 
        WHEN days_between <= 7 THEN '0-7 days'
        WHEN days_between <= 14 THEN '8-14 days'
        WHEN days_between <= 21 THEN '15-21 days'
        ELSE '22-30 days'
    END AS readmit_window
FROM readmission_pairs;
GO
--test
SELECT TOP 10 * FROM vw_readmissions ORDER BY days_between;



--View 4: Claims with Conditions

DROP VIEW IF EXISTS vw_claims_with_conditions;
GO

CREATE VIEW vw_claims_with_conditions AS
SELECT 
    fc.claim_token,
    REPLACE(fc.patient_token, 'urn:uuid:', '') AS patient_token,
    fc.date_key,
    dd.full_date AS service_date,
    dd.year,
    dd.month,
    fc.total_cost,
    fc.payer_coverage,
    fc.patient_out_of_pocket,
    dp.gender,
    dp.birth_year,
    dp.race,
    dp.zip_3digit,
    ROUND(fc.payer_coverage / NULLIF(fc.total_cost, 0) * 100, 1) AS coverage_pct
FROM fact_claims fc
JOIN dim_date dd ON fc.date_key = dd.date_key
JOIN dim_patient dp ON REPLACE(fc.patient_token, 'urn:uuid:', '') = dp.patient_token
WHERE fc.total_cost IS NOT NULL;
GO

SELECT TOP 10 * FROM vw_claims_with_conditions ORDER BY total_cost DESC;