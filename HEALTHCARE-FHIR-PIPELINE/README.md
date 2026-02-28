
# FHIR-Aligned Healthcare Claims Analytics Pipeline

> **Portfolio project demonstrating raw FHIR R4 parsing, deterministic UUID hashing, strict OMOP v5.4 dimensional modeling, and query optimization for executive KPI analytics.**

---

## 📖 Overview

This project engineers an end-to-end healthcare data pipeline that transforms deeply nested **FHIR R4 JSON bundles** into a highly optimized **OMOP v5.4 relational schema** hosted in **Azure SQL**.

The system is designed to solve real-world healthcare data engineering problems:

- ❌ Silent join failures from inconsistent UUID formats  
- ❌ Cartesian product explosions during multi-table joins  
- ❌ Memory timeouts in BI-facing queries  
- ❌ Slow executive dashboards due to poor semantic modeling  

By pushing heavy compute down to the SQL engine and building a pre-aggregated semantic layer, the final **Power BI executive dashboard** runs with near-zero latency while supporting financial and clinical risk analytics.


# 🏗️ Architecture

```

[ SOURCE: Raw FHIR JSON Data ]
(Synthetic patient bundles containing nested vitals, claims, encounters, and demographics)
|
|  --> Extraction Engine: Python + Pandas
|  --> Logic: Flatten nested FHIR structures into tabular formats
V
[ BRONZE: Parquet Files ]
(Flattened staging layer)

* patient_fhir.parquet
* condition_fhir.parquet
* claims_fhir.parquet
  |
  |  --> Transformation Engine: Python ETL (05_load_to_sql.py)
  |  --> Logic:
  |        • Deterministic UUID hashing
  |        • Prefix stripping ('urn:uuid:')
  |        • OMOP column alignment
  V
  [ SILVER: Azure SQL (OMOP v5.4 Base Tables) ]
  (Strict OMOP Common Data Model implementation)
* PERSON
* VISIT_OCCURRENCE
* CONDITION_OCCURRENCE
* COST
* CONCEPT
  |
  |  --> Semantic Abstraction Layer
  |  --> Heavy compute pushed down to SQL engine
  |  --> CTE-based pre-aggregation
  V
  [ GOLD: Azure SQL Views (Semantic Layer) ]
  (Pre-calculated reporting layer for BI consumption)
* vw_patient_summary
* vw_readmissions
* vw_claims_with_conditions
* vw_high_cost_patients
  |
  |  --> Visualization Engine: Power BI (Import / DirectQuery)
  |  --> DAX for dynamic thresholding & KPI calculation
  V
  [ PRESENTATION: Executive Dashboard ]

````

---

# 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Data Generation | Synthea (Synthetic Patient Data) |
| ETL Language | Python 3.11 (Pandas, deterministic hashing) |
| Bronze Storage | Parquet (fastparquet) |
| Database (Silver) | Azure SQL Database (OMOP v5.4 CDM) |
| Semantic Layer (Gold) | Azure SQL Views (CTE Pre-Aggregation) |
| Analytics | T-SQL (Window Functions, Conditional Aggregations) |
| Visualization | Power BI Desktop (DAX) |

---

# 🚀 How to Run

## 1️⃣ Clone Repository & Install Dependencies

```bash
git clone https://github.com/YOUR_USERNAME/data-projects.git
cd data-projects/HEALTHCARE-FHIR-PIPELINE
pip install -r requirements.txt
````

Or manually:

```bash
pip install pandas pyodbc fastparquet python-dotenv
```

---

## 2️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```
AZURE_SQL_SERVER="your_server.database.windows.net"
AZURE_SQL_DATABASE="your_db_name"
AZURE_SQL_USER="your_username"
AZURE_SQL_PASSWORD="your_password"
```

⚠️ Never commit your `.env` file.

---

## 3️⃣ Execute ETL Pipeline

```bash
python3 src/05_load_to_sql.py
```

This script:

* Loads Parquet staging data
* Strips `urn:uuid:` prefixes
* Applies deterministic hashing
* Aligns to OMOP v5.4 schema
* Loads data into Azure SQL

---

## 4️⃣ Deploy Semantic Views

Run:

```bash
# Execute via Azure Data Studio or sqlcmd
sql/06_semantic_views.sql
```

This creates optimized reporting views for BI consumption.

---

# ⚡ Key Engineering Decisions & Data Infrastructure Solutions

---

## 1️⃣ Deterministic UUID Hashing

### Problem

FHIR bundles contain inconsistent ID formats:

* `urn:uuid:1234-abc`
* `1234-abc`

This caused:

* Silent join failures
* Broken foreign key relationships
* Inconsistent person linking across claims and encounters

### Solution

Implemented a deterministic hashing strategy in Python:

* Strip `urn:uuid:` prefixes
* Normalize UUID strings
* Hash consistently into fixed-length integers

This guaranteed:

* Referential integrity across all OMOP tables
* Stable joins between PERSON, VISIT_OCCURRENCE, CONDITION_OCCURRENCE, and COST
* Elimination of silent join mismatches

---

## 2️⃣ Push-Down Compute & Defensive SQL (Eliminating Cartesian Explosions)

### Problem

Initial semantic views joined multiple many-to-many tables directly:

* Encounters × Conditions × Costs

This produced:

* Massive row multiplication
* Memory timeouts
* BI query latency

### Solution

Refactored architecture using:

* Common Table Expressions (CTEs)
* Pre-aggregation to `person_id` grain
* Window functions for readmission logic
* Conditional aggregation before final joins

### Result

* Query execution time reduced from timeout → under 1 second
* Stable Power BI DirectQuery performance
* Clean patient-level aggregation without duplication

---

# 📊 Executive KPIs & DAX Implementation

The Power BI dashboard sits on top of the SQL semantic layer and uses the following measures.

---

## 💰 Financial Metrics

```DAX
Total Spend = 
SUM('vw_patient_summary'[total_spend])

Total Out of Pocket = 
SUM('vw_patient_summary'[total_oop])

Patient Burden % = 
DIVIDE(
    [Total Out of Pocket], 
    [Total Spend], 
    0
)
```

---

## 📈 Cohort & Operational Metrics

```DAX
High Cost Patient Count = 
CALCULATE(
    COUNT('vw_high_cost_patients'[patient_token]),
    'vw_high_cost_patients'[cost_category] = "High Cost (Top 10%)"
)

Total Encounters = 
SUM('vw_patient_summary'[total_encounters])

30-Day Readmissions = 
COUNTROWS(
    FILTER(
        'vw_readmissions', 
        'vw_readmissions'[days_between] <= 30 &&
        'vw_readmissions'[days_between] > 0
    )
)

Readmission Rate % = 
DIVIDE(
    [30-Day Readmissions], 
    [Total Encounters], 
    0
)
```

---

# 🗂️ Repository Structure

```
HEALTHCARE-FHIR-PIPELINE/
├── src/
│   └── 05_load_to_sql.py
│        # Core ETL: Parquet → Azure SQL OMOP load & deterministic hashing
│
├── sql/
│   └── 06_semantic_views.sql
│        # Optimized CTE-based reporting views
│
├── dashboard/
│   └── healthcare_omop_dashboard.pbix
│        # Executive Power BI report
│
├── requirements.txt
├── .env.example
└── .gitignore
     # Strict exclusion of data/ and .env
```

---

# 🔐 Data Notice

All data in this project is fully synthetic and generated using **Synthea**.

* No real patient data was processed.
* No PHI or HIPAA-regulated information is stored.
* This project is strictly for educational and portfolio purposes.

---

# 🎯 What This Project Demonstrates

* Deep understanding of healthcare data standards (FHIR → OMOP)
* Deterministic ID engineering for referential integrity
* Performance optimization via SQL push-down compute
* Defensive query design to prevent row explosions
* Executive-facing KPI modeling
* End-to-end ownership: ingestion → modeling → BI

---

**Author:** Pratyusha Adibhatla
**Focus:** Healthcare Data Engineering | Clinical Risk Analytics | Cloud-Native SQL Architecture

---

```
```
