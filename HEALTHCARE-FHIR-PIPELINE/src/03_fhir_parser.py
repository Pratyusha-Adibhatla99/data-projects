"""
03_fhir_parser.py
-----------------
Parses Synthea FHIR R4 JSON bundles and extracts structured records for:
  - Patient resources
  - Encounter resources  
  - Condition resources

Outputs clean Parquet files (+ CSV copies) for downstream SQL loading.

FHIR R4 specs referenced:
  https://hl7.org/fhir/R4/patient.html
  https://hl7.org/fhir/R4/encounter.html
  https://hl7.org/fhir/R4/condition.html

Usage:
  python 03_fhir_parser.py
"""

import json
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
FHIR_DIR   = Path("data/raw/fhir")
OUTPUT_DIR = Path("data/processed/fhir_parsed")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def safe_get(obj, *keys, default=None):
    """Safely traverse nested dicts / lists."""
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key, default)
        elif isinstance(obj, list):
            try:
                obj = obj[int(key)]
            except (IndexError, TypeError, ValueError):
                return default
        else:
            return default
        if obj is None:
            return default
    return obj


def first_coding(coding_list, field="code", default=None):
    """Pull a field from the first entry in a FHIR coding array."""
    if not isinstance(coding_list, list) or not coding_list:
        return default
    return coding_list[0].get(field, default)


def parse_fhir_date(s):
    return str(s)[:10] if s else None


def ref_id(reference_str):
    """Strip urn:uuid: prefix from a FHIR reference."""
    if not reference_str:
        return None
    return reference_str.replace("urn:uuid:", "").replace("Patient/", "")                         .replace("Encounter/", "")


# ── Resource Parsers ───────────────────────────────────────────────────────────
def parse_patient(r: dict) -> dict:
    extensions = r.get("extension", [])
    race_ext = next((e for e in extensions if "us-core-race" in e.get("url","")), {})
    eth_ext  = next((e for e in extensions if "us-core-ethnicity" in e.get("url","")), {})

    race = (safe_get(race_ext, "extension", 0, "valueCoding", "display") or
            safe_get(race_ext, "extension", 0, "valueString"))
    ethnicity = (safe_get(eth_ext, "extension", 0, "valueCoding", "display") or
                 safe_get(eth_ext, "extension", 0, "valueString"))

    addr = r.get("address", [{}])[0]
    comm = safe_get(r, "communication", 0, "language", "coding", default=[])

    return {
        "fhir_patient_id":  r.get("id"),
        "fhir_resource":    "Patient",
        "gender":           r.get("gender"),
        "birth_year":       str(r.get("birthDate", ""))[:4] or None,
        "deceased":         int("deceasedDateTime" in r or r.get("deceasedBoolean", False)),
        "marital_status":   first_coding(safe_get(r, "maritalStatus", "coding", default=[]), "code"),
        "language":         first_coding(comm, "code"),
        "race":             race,
        "ethnicity":        ethnicity,
        "state":            addr.get("state"),
        "zip_3digit":       str(addr.get("postalCode", ""))[:3] or None,
        "data_source":      "FHIR_R4",
    }


def parse_encounter(r: dict) -> dict:
    period    = r.get("period", {})
    start_str = period.get("start")
    end_str   = period.get("end")

    duration_hrs = None
    if start_str and end_str:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            s = datetime.strptime(start_str[:19], fmt)
            e = datetime.strptime(end_str[:19],   fmt)
            duration_hrs = round((e - s).total_seconds() / 3600, 2)
        except Exception:
            pass

    reason_codings  = safe_get(r, "reasonCode", 0, "coding", default=[])
    type_codings    = safe_get(r, "type",       0, "coding", default=[])

    return {
        "fhir_encounter_id":   r.get("id"),
        "fhir_resource":       "Encounter",
        "fhir_patient_id":     ref_id(safe_get(r, "subject", "reference")),
        "status":              r.get("status"),
        "class_code":          safe_get(r, "class", "code"),
        "class_display":       safe_get(r, "class", "display"),
        "encounter_type_code": first_coding(type_codings, "code"),
        "encounter_type":      first_coding(type_codings, "display"),
        "start_date":          parse_fhir_date(start_str),
        "end_date":            parse_fhir_date(end_str),
        "duration_hrs":        duration_hrs,
        "reason_code":         first_coding(reason_codings, "code"),
        "reason_display":      first_coding(reason_codings, "display"),
        "service_provider":    ref_id(safe_get(r, "serviceProvider", "reference")),
        "data_source":         "FHIR_R4",
    }


def parse_condition(r: dict) -> dict:
    code_codings = safe_get(r, "code", "coding", default=[])
    snomed = next((c for c in code_codings if "snomed" in c.get("system","").lower()), {})
    icd    = next((c for c in code_codings if "icd"    in c.get("system","").lower()), {})

    clinical_status     = first_coding(safe_get(r, "clinicalStatus",     "coding", default=[]), "code")
    verification_status = first_coding(safe_get(r, "verificationStatus", "coding", default=[]), "code")
    category_code       = first_coding(safe_get(r, "category", 0, "coding", default=[]), "code")

    return {
        "fhir_condition_id":   r.get("id"),
        "fhir_resource":       "Condition",
        "fhir_patient_id":     ref_id(safe_get(r, "subject",  "reference")),
        "fhir_encounter_id":   ref_id(safe_get(r, "encounter", "reference")),
        "snomed_code":         snomed.get("code"),
        "snomed_display":      snomed.get("display"),
        "icd_code":            icd.get("code"),
        "icd_display":         icd.get("display"),
        "clinical_status":     clinical_status,
        "verification_status": verification_status,
        "category":            category_code,
        "onset_date":          parse_fhir_date(r.get("onsetDateTime")),
        "abatement_date":      parse_fhir_date(r.get("abatementDateTime")),
        "data_source":         "FHIR_R4",
    }


RESOURCE_PARSERS = {
    "Patient":   parse_patient,
    "Encounter": parse_encounter,
    "Condition": parse_condition,
}


# ── Bundle Processor ───────────────────────────────────────────────────────────
def process_bundle(bundle_path: Path) -> dict:
    records = {k: [] for k in RESOURCE_PARSERS}
    try:
        with open(bundle_path, encoding="utf-8") as f:
            bundle = json.load(f)
    except Exception as exc:
        log.warning(f"  Could not parse {bundle_path.name}: {exc}")
        return records

    if bundle.get("resourceType") != "Bundle":
        return records

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        rtype    = resource.get("resourceType")
        if rtype in RESOURCE_PARSERS:
            try:
                records[rtype].append(RESOURCE_PARSERS[rtype](resource))
            except Exception as exc:
                log.debug(f"  Failed {rtype} in {bundle_path.name}: {exc}")

    return records


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    log.info("=== FHIR R4 Scalable Bundle Parser ===")
    
    # 1. FORCE ABSOLUTE PATHS TO PREVENT RELATIVE PATH ERRORS
    base_path = Path.cwd()
    fhir_input = base_path / "data" / "raw" / "fhir"
    output_path = base_path / "data" / "processed" / "fhir_parsed"

    log.info(f"Looking for data in: {fhir_input}")
    
    # 2. VERIFY FOLDER EXISTS
    if not fhir_input.exists():
        log.error(f"❌ DIRECTORY NOT FOUND: {fhir_input}")
        return

    json_files = sorted(fhir_input.glob("*.json"))
    log.info(f"Found {len(json_files)} JSON files in raw folder.")

    if not json_files:
        log.warning("⚠️ No .json files found. Check your file extensions!")
        return

    json_files = sorted(Path(FHIR_DIR).glob("*.json"))
    if not json_files:
        log.error(f"No JSON files found in {FHIR_DIR}.")
        return

    log.info(f"Processing 7.7GB across {len(json_files)} bundles...")

    # Initialize storage for this batch
    batch_size = 200  # Adjust based on your RAM; 200-500 is safe for 16GB Mac
    batch_records = {k: [] for k in RESOURCE_PARSERS}
    
    total_counts = {k: 0 for k in RESOURCE_PARSERS}

    for i, path in enumerate(json_files, 1):
        # Process individual bundle
        bundle_data = process_bundle(path)
        for rtype, recs in bundle_data.items():
            batch_records[rtype].extend(recs)

        # Every 'batch_size' files, we convert to DF and handle memory
        if i % batch_size == 0 or i == len(json_files):
            log.info(f"  Memory Flush: Processing batch up to bundle {i}...")
            
            for rtype in RESOURCE_PARSERS:
                if not batch_records[rtype]:
                    continue
                
                df_batch = pd.DataFrame(batch_records[rtype])
                
                # Check for existing data to handle duplicates across batches
                parquet_path = OUTPUT_DIR / f"{rtype.lower()}_fhir.parquet"
                
                if parquet_path.exists():
                    existing_df = pd.read_parquet(parquet_path)
                    df_final = pd.concat([existing_df, df_batch]).drop_duplicates(
                        subset=[f"fhir_{rtype.lower()}_id"]
                    )
                else:
                    df_final = df_batch.drop_duplicates(subset=[f"fhir_{rtype.lower()}_id"])
                
                df_final.to_parquet(parquet_path, index=False, engine="pyarrow")
                total_counts[rtype] = len(df_final)
                
            # Clear batch from memory
            batch_records = {k: [] for k in RESOURCE_PARSERS}

    log.info("=== Final Scaled Results ===")
    for rtype, count in total_counts.items():
        log.info(f"  {rtype}: {count:,} total unique records saved to Parquet")
        # Save a small CSV sample for manual inspection (Recruiters love samples)
        sample_path = OUTPUT_DIR / f"{rtype.lower()}_sample.csv"
        pd.read_parquet(OUTPUT_DIR / f"{rtype.lower()}_fhir.parquet").head(100).to_csv(sample_path, index=False)

    log.info("Scalable FHIR parsing complete.")
if __name__ == "__main__":
    main()