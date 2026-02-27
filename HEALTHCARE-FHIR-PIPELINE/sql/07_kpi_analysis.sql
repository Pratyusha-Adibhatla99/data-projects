-- 06_kpi_analysis.sql - Healthcare KPI Queries
-- Run against de-identified Azure SQL star schema

-- KPI 1: Claim Cost by Condition Category
SELECT
    dc.condition_category,
    COUNT(*)                                AS claim_count,
    ROUND(AVG(fc.total_claim_cost), 2)      AS avg_total_claim,
    ROUND(AVG(fc.payer_coverage), 2)        AS avg_payer_coverage,
    ROUND(AVG(fc.patient_out_of_pocket), 2) AS avg_patient_oop,
    ROUND(AVG(CAST(fc.payer_coverage AS FLOAT)) / NULLIF(AVG(CAST(fc.total_claim_cost AS FLOAT)), 0) * 100, 1) AS payer_coverage_pct,
    ROUND(SUM(fc.total_claim_cost), 2)      AS total_cost_all
FROM fact_claims fc
JOIN dim_condition dc ON fc.condition_key = dc.condition_key
WHERE fc.total_claim_cost IS NOT NULL
GROUP BY dc.condition_category
ORDER BY avg_total_claim DESC;

-- KPI 2: Monthly Encounter Volume by Type
SELECT
    dd.year, dd.month, dd.month_name,
    CAST(dd.year AS VARCHAR) + '-' + RIGHT('0' + CAST(dd.month AS VARCHAR), 2) AS year_month,
    CASE WHEN det.is_emergency=1 THEN 'Emergency' WHEN det.is_inpatient=1 THEN 'Inpatient' ELSE 'Outpatient' END AS encounter_category,
    COUNT(*) AS encounter_count,
    ROUND(AVG(fc.total_claim_cost), 2) AS avg_claim_cost
FROM fact_claims fc
JOIN dim_date dd ON fc.date_key = dd.date_key
JOIN dim_encounter_type det ON fc.encounter_type_key = det.encounter_type_key
WHERE dd.year BETWEEN 2015 AND 2025
GROUP BY dd.year, dd.month, dd.month_name, det.class_display, det.is_emergency, det.is_inpatient
ORDER BY dd.year, dd.month;


-- KPI 4: Payer Coverage Gap by Condition
SELECT
    dc.condition_category, dc.snomed_display,
    COUNT(*) AS encounter_count,
    ROUND(SUM(fc.total_claim_cost), 2) AS total_cost,
    ROUND(SUM(fc.payer_coverage), 2) AS total_payer,
    ROUND(SUM(fc.patient_out_of_pocket), 2) AS total_patient_oop,
    ROUND(SUM(CAST(fc.payer_coverage AS FLOAT)) / NULLIF(SUM(CAST(fc.total_claim_cost AS FLOAT)),0)*100, 1) AS payer_coverage_pct,
    ROUND(SUM(CAST(fc.patient_out_of_pocket AS FLOAT)) / NULLIF(SUM(CAST(fc.total_claim_cost AS FLOAT)),0)*100, 1) AS patient_burden_pct
FROM fact_claims fc JOIN dim_condition dc ON fc.condition_key = dc.condition_key
WHERE fc.total_claim_cost > 0 AND fc.payer_coverage IS NOT NULL AND fc.patient_out_of_pocket IS NOT NULL
GROUP BY dc.condition_category, dc.snomed_display
HAVING COUNT(*) >= 10
ORDER BY patient_burden_pct DESC;

-- KPI 5: 30-Day Readmission Proxy
WITH enc AS (
    SELECT fc.patient_key, fc.encounter_token, dd.full_date AS service_date, fc.total_claim_cost
    FROM fact_claims fc JOIN dim_date dd ON fc.date_key = dd.date_key WHERE fc.service_start IS NOT NULL
),
pairs AS (
    SELECT a.patient_key, a.encounter_token AS first_enc, b.encounter_token AS readmit_enc,
           a.service_date AS first_date, b.service_date AS readmit_date,
           DATEDIFF(DAY, a.service_date, b.service_date) AS days_between, b.total_claim_cost AS readmit_cost
    FROM enc a JOIN enc b
        ON a.patient_key = b.patient_key AND a.encounter_token <> b.encounter_token
        AND b.service_date > a.service_date AND DATEDIFF(DAY, a.service_date, b.service_date) <= 30
)
SELECT p.patient_key, dp.patient_token, dp.gender, dp.state_abbr,
       COUNT(DISTINCT p.first_enc) AS readmission_events,
       MIN(p.days_between) AS min_days_to_readmit,
       ROUND(AVG(CAST(p.days_between AS FLOAT)),1) AS avg_days_to_readmit,
       ROUND(SUM(p.readmit_cost),2) AS total_readmit_cost
FROM pairs p JOIN dim_patient dp ON p.patient_key = dp.patient_key
GROUP BY p.patient_key, dp.patient_token, dp.gender, dp.state_abbr
ORDER BY readmission_events DESC, total_readmit_cost DESC;

-- BONUS: Summary KPI Card
SELECT
    COUNT(DISTINCT fc.patient_key) AS total_patients,
    COUNT(*) AS total_claims,
    ROUND(AVG(fc.total_claim_cost), 2) AS avg_claim_cost,
    ROUND(SUM(fc.total_claim_cost), 2) AS total_cost_all,
    ROUND(SUM(fc.payer_coverage), 2) AS total_payer_covered,
    ROUND(SUM(fc.patient_out_of_pocket), 2) AS total_patient_oop,
    ROUND(AVG(CAST(fc.payer_coverage AS FLOAT))/NULLIF(AVG(CAST(fc.total_claim_cost AS FLOAT)),0)*100,1) AS overall_payer_coverage_pct
FROM fact_claims fc WHERE fc.total_claim_cost IS NOT NULL;
