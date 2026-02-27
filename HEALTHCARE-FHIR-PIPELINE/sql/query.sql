--1. Volume of data that is loaded 
SELECT 'dim_patient' AS Table_Name, COUNT(*) AS Total_Rows FROM dim_patient
UNION ALL
SELECT 'dim_condition', COUNT(*) FROM dim_condition
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_encounter', COUNT(*) FROM fact_encounter;
-- 2. Inspecting the Fact table to ensure keys and dates loaded cleanly
SELECT TOP 5 
    encounter_token,
    patient_token,
    date_key,
    encounter_type,
    reason_description
FROM fact_encounter
ORDER BY date_key DESC;
-- 3. Analytical query proving the Star Schema relationships work
SELECT TOP 10
    c.snomed_display AS Medical_Condition,
    COUNT(f.encounter_token) AS Total_Hospital_Visits
FROM fact_encounter f
JOIN dim_condition c 
    ON f.reason_code = c.snomed_code
WHERE c.snomed_display IS NOT NULL
GROUP BY c.snomed_display
ORDER BY Total_Hospital_Visits DESC;