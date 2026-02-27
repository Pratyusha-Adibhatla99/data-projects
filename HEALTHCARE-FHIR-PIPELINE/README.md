# FHIR-Aligned Healthcare Claims Analytics Pipeline

> **Portfolio project demonstrating high-volume FHIR R4 parsing, Medallion Architecture (Bronze/Silver/Gold), HIPAA Safe Harbor pseudonymization, OMOP dimensional modeling, and Executive KPI analytics on synthetic healthcare data.**

---

## 📖 Overview
This project engineers an end-to-end data pipeline to identify which clinical conditions drive the highest financial risk and 30-day hospital readmissions. It processes 15GB of deeply nested FHIR JSON data into a highly optimized Kimball Star Schema, utilizing push-down compute in Azure SQL to feed a zero-latency Power BI executive dashboard.

---

## 🏗️ Architecture

```text
[ SOURCE: 15GB Raw FHIR JSON ] 
  (1,774 synthetic patients via Synthea. Highly nested: vitals, claims, demographics)
           |
           |  --> Extraction Engine: Python Generator + Vectorized Pandas
           |  --> Logic: Schema-on-read iteratively parsing patient bundles
           V
[ BRONZE: 690MB Parquet Files ] 
  (Flattened staging layer. 113k encounters, 211k claim lines. Snappy compressed)
           |
           |  --> Pipeline Orchestration: Azure Data Factory (ADF)
           |  --> Logic: Truncate-and-Load, UTC normalization, Spend reconciliation
           V
[ SILVER: Azure SQL (OMOP Base Tables) ] 
  (Strict OMOP Common Data Model storage)
  - Tables: PERSON (w/ 3-digit zip), VISIT_OCCURRENCE, CONDITION_OCCURRENCE, COST
           |
           |  --> Semantic Abstraction: Heavy compute pushed down to SQL engine
           |  --> Logic: 30-day readmission CTEs, NULLIF defensive SQL
           V
[ GOLD: Azure SQL Views (Star Schema) ] 
  (Kimball dimensional model for BI consumption)
  - Views: vw_patient_summary, vw_readmissions, vw_claims_with_conditions
           |
           |  --> Visualization Engine: Zero-latency BI ingestion
           |  --> Logic: DAX PERCENTILE.INC for Top 10% high-cost spenders
           V
[ PRESENTATION: Power BI Executive Dashboard ] 
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| **Data Generation** | Synthea (1,774 synthetic patients, 15GB raw JSON) |
| **ETL Language** | Python 3.10+ (Pandas, vectorized operations, iterators) |
| **Bronze Storage** | Snappy-compressed Parquet files |
| **Orchestration** | Azure Data Factory (ADF) |
| **De-identification** | HIPAA Safe Harbor — SHA-256 tokens, ZIP truncation |
| **Database (Silver)** | Azure SQL Database (OMOP Common Data Model Base Tables) |
| **Semantic (Gold)** | Azure SQL Views (Kimball Star Schema) |
| **Analytics** | T-SQL — CTEs, self-joins, window functions |
| **Visualization** | Power BI Desktop (DAX logic) |

---

## 🚀 How to Run (Usage)

### 1. Clone the repository and install dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/HEALTHCARE-FHIR-PIPELINE.git
cd HEALTHCARE-FHIR-PIPELINE
pip install -r requirements.txt
```

### 2. Configure Environment Variables:

Create a `.env` file in the root directory and add your Azure SQL database connection string (ensure this file remains gitignored):

```plaintext
AZURE_SQL_CONNECTION_STRING="your_connection_string_here"
```

### 3. Execute the ETL Pipeline:

Run the Python extraction and loading scripts in sequence:

```bash
python src/03_fhir_parser.py        # Parses 15GB JSON -> 690MB Parquet
python src/04_upload_to_azure.py    # Orchestrates Blob Storage upload
python src/05_load_to_sql.py        # Loads Parquet into Azure SQL OMOP tables
python src/parse_claims.py          # Processes specific financial extraction logic
```

### 4. Deploy Semantic Views & Analyze:

Execute the SQL scripts against your Azure SQL Database to build the Gold layer and extract KPIs:

- Run `sql/06_semantic_views.sql` to generate the Star Schema.
- Run `sql/07_kpi_analysis.sql` to validate business metrics.

---

## ⚡ Key Engineering Decisions

- **Python Generator for 15GB Memory Management:** Avoided out-of-memory crashes by writing a custom Python generator to iterate through patient bundles sequentially, using a schema-on-read approach to output Snappy-compressed Parquet.
- **Two-Tier Database Architecture:** Separated core storage (OMOP v5.4 tables) from reporting layers (Kimball Star Schema SQL Views) to prevent massive query lag in Power BI.
- **Push-Down Compute & Defensive SQL:** Handled complex logic (e.g., 30-Day Readmission via self-joining CTEs and `NULLIF` for division-by-zero prevention) directly in the SQL engine to optimize performance.

---

## 📊 Executive KPIs & Business Questions

| KPI | Business Question | Technical Implementation |
|-----|-------------------|--------------------------|
| **Geographic Risk** | Which 3-digit ZIP codes have the highest readmission rate vs total cost? | SQL aggregation (GROUP BY ZIP prefix) + Scatter Plot visualization in Power BI |
| **Clinical Drivers** | Which clinical conditions drive the highest volume of 30-day readmissions? | T-SQL GROUP BY on CONDITION_OCCURRENCE + Horizontal Bar Chart |
| **Coverage Gap** | Where does insurance coverage drop off for catastrophic care cases? | DAX `PERCENTILE.INC` logic to identify Top 10% spenders + Stacked Bar visualization |
| **Readmission Proxy** | What is the true 30-day readmission rate across encounters? | T-SQL CTE using `LEAD()` window function and self-join logic for temporal encounter matching |

---

## 🗂️ Repository Structure

```plaintext
HEALTHCARE-FHIR-PIPELINE/
├── src/
│   ├── 03_fhir_parser.py                # Schema-on-read JSON generator
│   ├── 04_upload_to_azure.py            # Blob storage orchestration
│   ├── 05_load_to_sql.py                # Parquet to Azure SQL OMOP load
│   ├── 07_production_scaling.py         # ADF Incremental load config
│   └── parse_claims.py                  # Financial extraction logic
├── sql/
│   ├── 06_semantic_views.sql            # Star schema abstraction views
│   ├── 07_kpi_analysis.sql              # Core KPI queries
│   └── 08_incremental_load_architecture.sql # High-watermark MERGE logic
├── docs/
│   ├── data_dictionary.md               # Star schema definitions
│   └── hipaa_safeharbor_checklist.md    # 45 CFR §164.514(b) compliance
├── dashboard/
│   └── 08_healthcare_risk_dashboard.pbix # Power BI Executive Report
├── requirements.txt
├── .env.example
└── .gitignore                           # Strict exclusion of data/ and .env
```

---

## ⚠️ Data Notice

All data in this project is **fully synthetic**, generated by Synthea. No real patient data was processed or stored. De-identification was applied strictly as a demonstration of enterprise HIPAA compliance.
