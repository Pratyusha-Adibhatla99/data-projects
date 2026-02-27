# HIPAA Safe Harbor De-Identification Checklist
**Standard:** 45 CFR §164.514(b)  
**Dataset:** Synthea Synthetic Patient Data 

## The 18 Safe Harbor Identifiers

| # | Identifier | Action | Implementation |
|---|---|---|---|
| 1 | Names | Removed | First, last, prefix, suffix, maiden columns dropped. |
| 2 | Geographic (smaller than state) | Transformed | ZIP → 3-digit prefix. (Note: Prefixes with population < 20,000 mapped to '000' per Safe Harbor rules). City, address, lat/lon removed. |
| 3 | Dates & Ages (except year) | Transformed | Extracted Year only. All dates (admission, discharge, birth) stripped of month/day. Ages > 89 aggregated into a single '90+' category. |
| 4 | Phone numbers | Removed | Regex → `[PHONE REMOVED]` |
| 5 | Fax numbers | Removed | Included in phone regex |
| 6 | Email addresses | Removed | Regex → `[EMAIL REMOVED]` |
| 7 | Social security numbers | Tokenized | SHA-256 → `patient_token` |
| 8 | Medical record numbers | Tokenized | UUID token |
| 9 | Health plan numbers | Removed | Payer ID column dropped |
| 10 | Account numbers | Tokenized | UUID token |
| 11 | Certificate/license numbers | Removed | DRIVERS, PASSPORT columns dropped |
| 12 | Vehicle identifiers | N/A | Not present in Synthea source |
| 13 | Device identifiers | N/A | Not present in Synthea source |
| 14 | URLs | Removed | Regex → `https://www.merriam-webster.com/dictionary/removed` |
| 15 | IP addresses | Removed | Regex → `[IP REMOVED]` |
| 16 | Biometric identifiers | N/A | Not present in Synthea source |
| 17 | Full-face photographs | N/A | No images in dataset |
| 18 | Other unique identifying numbers | Removed | Provider, org, appointment IDs dropped |

## Referential Integrity & Pseudonymization
To maintain relational integrity for analytics without exposing PHI, unique identifiers were hashed (SHA-256 of original patient UUID) to create a consistent `patient_token` across all tables. 
* **Security Control:** The `phi_mapping.csv` file acting as the re-identification key is strictly excluded from version control via `.gitignore`.

## Disclaimer
This project utilizes Synthea synthetic data. No real Protected Health Information (PHI) was created, processed, or stored at any point during this pipeline execution.