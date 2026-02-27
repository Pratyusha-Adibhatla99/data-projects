# FHIR-Aligned Healthcare Claims Analytics Pipeline

> **Portfolio project demonstrating FHIR R4 parsing, HIPAA Safe Harbor de-identification,
> cloud data ingestion (Azure), dimensional modeling, and KPI analytics on synthetic healthcare data.**

---

## 🏗️ Architecture

```
Synthea (750 patients)
  Raw CSV + FHIR R4 JSON
         ↓
  Azure Blob Storage          ← Cloud ingestion layer
  (raw-csv / raw-fhir)
         ↓
  Local Python ETL
  ├── PHI De-identification   ← HIPAA Safe Harbor (18 identifiers)
  └── FHIR R4 Parser          ← Patient, Encounter, Condition, Observation
         ↓
  Azure SQL Database
  └── Star Schema             ← dim_patient, dim_date, dim_condition,
                                 dim_encounter_type, fact_claims
         ↓
  SQL KPI Analysis            ← 6 analytical queries
         ↓
  Power BI Dashboard          ← 5-page recruiter-facing report
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Generation | Synthea (750 synthetic patients) |
| Cloud Storage | Azure Blob Storage (LRS, Cool tier) |
| ETL Language | Python 3.10+ |
| FHIR Processing | Custom FHIR R4 parser (Patient, Encounter, Condition, Observation) |
| De-identification | HIPAA Safe Harbor — SHA-256 tokens, date shifting, ZIP truncation |
| Database | Azure SQL Database (Basic tier, 5 DTU) |
| Data Model | Star schema (1 fact table, 4 dimension tables) |
| Analytics | T-SQL — window functions, CTEs, self-joins |
| Visualization | Power BI Desktop |
| Orchestration | Python scripts (sequential, local) |

---

## ⚡ Key Design Decisions

### 1. SHA-256 Tokenization for Patient IDs
Rather than simply dropping patient IDs (which would break all joins), patient identifiers are replaced with a deterministic SHA-256 hash using a project salt. The same patient ID always produces the same 16-character token, preserving referential integrity across all tables while making re-identification computationally infeasible. A PHI mapping table is stored locally only and is gitignored.

### 2. Per-Patient Date Shifting (not removal)
HIPAA Safe Harbor permits year-of-birth and requires removal of most date components. However, clinical usefulness requires that *relative* time relationships be preserved (e.g., "30-day readmission" is meaningless if dates are randomized independently). This pipeline applies a single consistent random offset (±365 days) per patient, maintaining temporal relationships while obscuring real dates.

### 3. Star Schema over ODS
A normalized operational data store would be more faithful to the source system, but a star schema is what analytics tools (Power BI, Tableau, SQL KPIs) work best against. Dimension tables are small and stable; the fact table is optimized for aggregation. This is the same model used in real healthcare data warehouses.

### 4. Parquet as Intermediate Format
De-identified CSVs and FHIR-parsed records are saved as Parquet before loading to SQL. Parquet is columnar, typed, and compressed — the industry standard for data lake intermediate storage. It also makes local development faster (Pandas reads Parquet 3–10x faster than CSV).

### 5. Azure Basic SQL (not Synapse)
Synapse Analytics would cost $50+/day. For a 750-patient dataset, Azure SQL Basic (5 DTU, $0.16/day) is more than sufficient and demonstrates cost-aware cloud architecture — a skill that matters in production.

---

## 🏥 HIPAA Compliance

This project applies the **HIPAA Safe Harbor** de-identification method (45 CFR §164.514(b)).

**All 18 PHI identifiers addressed:**
- ✅ Names → SHA-256 token
- ✅ Dates → Per-patient shift ±365 days
- ✅ Geographic data → ZIP truncated to 3 digits; city removed
- ✅ Age ≥ 90 → Collapsed to "90+" group
- ✅ Phone/Email → Regex redaction in free text
- ✅ SSN, MRN, License → Tokenized or removed
- ✅ All other unique identifiers → SHA-256 tokens

See [`docs/hipaa_safeharbor_checklist.md`](docs/hipaa_safeharbor_checklist.md) and [`docs/deidentification_report.md`](docs/deidentification_report.md).

---

## 📊 FHIR R4 Implementation

The pipeline parses FHIR R4 Bundle resources and extracts:

| Resource Type | Fields Extracted | FHIR URL |
|---|---|---|
| Patient | gender, birthDate (year), maritalStatus, language, race/ethnicity | [hl7.org/fhir/patient](https://www.hl7.org/fhir/patient.html) |
| Encounter | class code, period, reasonCode (SNOMED), status | [hl7.org/fhir/encounter](https://www.hl7.org/fhir/encounter.html) |
| Condition | SNOMED CT code/display, clinicalStatus, onset/abatement | [hl7.org/fhir/condition](https://www.hl7.org/fhir/condition.html) |
| Observation | LOINC code, valueQuantity, referenceRange, effectiveDateTime | [hl7.org/fhir/observation](https://www.hl7.org/fhir/observation.html) |

All records tagged with `data_source = "FHIR_R4"` for lineage tracking.

---

## 📈 KPI Analyses

| KPI | Question Answered | Technique |
|---|---|---|
| 1 | Which conditions drive highest claim costs? | GROUP BY + AVG aggregation |
| 2 | How does encounter volume trend by type? | Time-series GROUP BY |
| 3 | Who are the top-decile cost patients? | NTILE window function |
| 4 | Which conditions have the largest coverage gap? | Ratio calculation + CASE tiers |
| 5 | What is the 30-day readmission proxy rate? | LEAD() self-join pattern |
| 6 | Executive summary dashboard metrics | Multi-aggregate summary |

---

## 💰 Cloud Cost

| Resource | Usage | Cost |
|---|---|---|
| Azure Blob Storage | ~200MB CSV + 100 FHIR JSON | ~$0.10 |
| Azure SQL Basic | 4 days × $0.16/day | ~$0.64 |
| **Total** | | **~$0.74** |

---

## 🗂️ Repository Structure

```
healthcare-fhir-pipeline/
├── src/
│   ├── day1_setup_check.py        # Environment validator
│   ├── day2_blob_ingestion.py     # Azure Blob upload/download
│   ├── day3_deidentify.py         # HIPAA Safe Harbor de-identification
│   ├── day4_fhir_parser.py        # FHIR R4 JSON bundle parser
│   ├── day5_load_to_sql.py        # Star schema creation + data load
│   ├── day6_kpi_analysis.py       # KPI query runner + Excel export
│   └── day7_readme_generator.py   # Documentation generator
├── sql/
│   └── day6_kpi_queries.sql       # All 6 KPI queries (raw SQL)
├── data/
│   └── sample_output/             # 50-row samples (no PHI)
├── docs/
│   ├── deidentification_report.md
│   ├── hipaa_safeharbor_checklist.md
│   └── data_dictionary.md
├── dashboard/
│   └── healthcare_dashboard.pdf   # Power BI export
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🚀 How to Run

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/healthcare-fhir-pipeline
cd healthcare-fhir-pipeline
pip install -r requirements.txt

# 2. Configure Azure credentials
cp .env.example .env
# Edit .env with your Azure connection strings

# 3. Generate Synthea data
java -jar synthea-with-dependencies.jar -p 750 \
  --exporter.fhir.export=true \
  --exporter.csv.export=true Massachusetts
mv output/csv/* data/raw_csv/
mv output/fhir/* data/raw_fhir/

# 4. Run the pipeline (in order)
python src/day1_setup_check.py
python src/day2_blob_ingestion.py --upload --download
python src/day3_deidentify.py
python src/day4_fhir_parser.py
python src/day5_load_to_sql.py
python src/day6_kpi_analysis.py
```

---

## 📋 Sample KPI Output

### KPI 1 — Top Conditions by Average Claim Cost (sample)

| condition_name | total_claims | avg_claim_amount | avg_payer_coverage_pct |
|---|---|---|---|
| Viral sinusitis | 2,341 | $487.23 | 82.4% |
| Normal pregnancy | 1,892 | $12,847.10 | 91.2% |
| Hypertension | 3,104 | $1,203.45 | 78.6% |
| Diabetes mellitus type 2 | 1,547 | $2,891.67 | 74.3% |

---

## ⚠️ Data Notice

All data in this project is **fully synthetic**, generated by [Synthea](https://github.com/synthetichealth/synthea).
No real patient data was used. De-identification was applied as a demonstration of HIPAA practices
on synthetic data — not because the data contains real PHI.

---

*Built with Python, Azure, SQL, and Power BI | FHIR R4 | HIPAA Safe Harbor*
