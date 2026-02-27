
HEALTHCARE FINANCIAL & CLINICAL RISK ENGINE: DATA FLOW ARCHITECTURE


[ SOURCE: 15GB Raw FHIR JSON ] 
  (1,774 synthetic patients via Synthea. Highly nested: vitals, claims, demographics)
           |
           |  --> Extraction Engine: Python Generator + Vectorized Pandas
           |  --> Logic: Schema-on-read, iteratively parsing patient bundles to avoid memory crash
           V
[ BRONZE: 690MB Parquet Files ] 
  (Flattened staging files. 113k encounters, 211k claim lines. Compressed with Snappy save them as compressed Parquet files)
           |
           |  --> Pipeline Orchestration: Truncate-and-Load batch process
           |  --> Logic: UTC normalization, $144M spend reconciliation
           V
[ SILVER: Azure SQL (OMOP Base Tables) ] 
  (Strict OMOP Common Data Model storage)
  - Tables: PERSON (w/ 3-digit zip), VISIT_OCCURRENCE, CONDITION_OCCURRENCE, COST
           |
           |  --> Semantic Abstraction: Heavy compute pushed down to SQL engine
           |  --> Logic: 30-day readmission CTEs (excluding Day 0 transfers), NULLIF defensive SQL
           V
[ GOLD: Azure SQL Views (Star Schema) ] 
  (Kimball dimensional model for BI consumption)
  - Views: dim_patient, dim_condition, dim_date, fact_claims
           |
           |  --> Visualization Engine: Zero-latency ingestion of pre-calculated views
           |  --> Logic: DAX PERCENTILE.INC for Top 10% high-cost spenders
           V
[ PRESENTATION: Power BI Executive Dashboard ] 
  (Business Impact: Geographic risk by zip code, Clinical drivers, Insurance vs. Out-of-pocket gap)

=======================================================================================