import os
import urllib.parse
import pandas as pd
import hashlib
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import time

def get_engine():
    """Uses the official Microsoft ODBC driver and scrubs .env variables"""
    load_dotenv()
    SERVER = os.getenv("AZURE_SQL_SERVER").strip().strip('"').strip("'")
    DATABASE = os.getenv("AZURE_SQL_DATABASE").strip().strip('"').strip("'")
    USERNAME = os.getenv("AZURE_SQL_USERNAME").strip().strip('"').strip("'")
    PASSWORD = os.getenv("AZURE_SQL_PASSWORD").strip().strip('"').strip("'")
    
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{SERVER},1433;"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=60;"
    )
    params = urllib.parse.quote_plus(conn_str)
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

def uuid_to_int(uuid_str):
    """Deterministically converts a string UUID into a 32-bit OMOP Integer ID"""
    return int(hashlib.sha256(str(uuid_str).encode('utf-8')).hexdigest(), 16) % (10**9)

def load_person(engine, local_dir):
    print("── Building true OMOP PERSON table ──")
    df = pd.read_parquet(local_dir / "patient_fhir.parquet")
    
    def map_gender(g):
        g = str(g).lower()
        return 8507 if 'male' in g else 8532 if 'female' in g else 0
        
    def map_race(r):
        r = str(r).lower()
        if 'white' in r: return 8527
        if 'black' in r: return 8516
        if 'asian' in r: return 8515
        return 0

    person_df = pd.DataFrame()
    
    person_df['person_id'] = df['fhir_patient_id'].apply(lambda x: uuid_to_int(str(x).replace('urn:uuid:', '')))
    
    person_df['gender_concept_id'] = df['gender'].apply(map_gender)
    person_df['year_of_birth'] = df['birth_year'].astype(int)
    person_df['race_concept_id'] = df['race'].apply(map_race)
    person_df['ethnicity_concept_id'] = 0
    person_df['person_source_value'] = df['fhir_patient_id']
    person_df['gender_source_value'] = df['gender']
    person_df['race_source_value'] = df['race']
    
    person_df.to_sql("person", con=engine, if_exists="replace", index=False)
    print(f"  ✓ person: {len(person_df):,} rows loaded")

def load_visit_occurrence(engine, local_dir):
    print("── Building true OMOP VISIT_OCCURRENCE table ──")
    df = pd.read_parquet(local_dir / "encounter_fhir.parquet")
    
    visit_df = pd.DataFrame()
    visit_df['visit_occurrence_id'] = df['fhir_encounter_id'].apply(uuid_to_int)
    visit_df['person_id'] = df['fhir_patient_id'].apply(uuid_to_int)
    visit_df['visit_concept_id'] = 9202 # Standard OMOP Outpatient code
    visit_df['visit_start_date'] = pd.to_datetime(df['start_date']).dt.date
    visit_df['visit_end_date'] = visit_df['visit_start_date']
    visit_df['visit_type_concept_id'] = 32035 # Standard OMOP EHR generation code
    visit_df['visit_source_value'] = df['fhir_encounter_id']
    
    visit_df.to_sql("visit_occurrence", con=engine, if_exists="replace", index=False)
    print(f"  ✓ visit_occurrence: {len(visit_df):,} rows loaded")

def load_cost(engine, local_dir):
    print("── Building true OMOP COST table ──")
    df = pd.read_parquet(local_dir / "claims_fhir.parquet")
    
    cost_df = pd.DataFrame()
    # Clean the claim ID
    cost_df['cost_id'] = df['claim_id'].apply(lambda x: uuid_to_int(str(x).replace('urn:uuid:', '')))
    
    # ✅ FIX 1: Strip prefixes so the patient hash perfectly matches the person table
    cost_df['person_id'] = df['patient_id'].apply(lambda x: uuid_to_int(str(x).replace('urn:uuid:', '')))
    
    # ✅ FIX 2: Map to encounter_id (not claim_id) so it can join to visit_occurrence
    cost_df['cost_event_id'] = df['encounter_id'].apply(lambda x: uuid_to_int(str(x).replace('urn:uuid:', ''))) 
    
    cost_df['cost_domain_id'] = 'Visit'
    cost_df['cost_type_concept_id'] = 32814  
    cost_df['total_charge'] = df['total_cost']
    cost_df['total_paid'] = df['payment_amount']
    cost_df['paid_by_patient'] = df['total_cost'] - df['payment_amount']
    
    cost_df.to_sql("cost", con=engine, if_exists="replace", index=False)
    print(f"  ✓ cost: {len(cost_df):,} rows loaded")
    
    
def load_concept(engine, local_dir):
    print("── Building true OMOP CONCEPT table ──")
    df = pd.read_parquet(local_dir / "condition_fhir.parquet")
    
    # FIX: Only drop rows if the actual code or display name is missing
    df = df.dropna(subset=['snomed_code', 'snomed_display']).drop_duplicates(subset=['snomed_code'])
    
    concept_df = pd.DataFrame()
    concept_df['concept_id'] = df['snomed_code'].apply(lambda x: uuid_to_int(str(x)))
    concept_df['concept_name'] = df['snomed_display'].str[:255]
    concept_df['domain_id'] = 'Condition'
    concept_df['vocabulary_id'] = 'SNOMED'
    concept_df['concept_class_id'] = 'Clinical Finding'
    concept_df['standard_concept'] = 'S'
    concept_df['concept_code'] = df['snomed_code']
    
    concept_df.to_sql("concept", con=engine, if_exists="replace", index=False)
    print(f"  ✓ concept: {len(concept_df):,} rows loaded")

def load_condition_occurrence(engine, local_dir):
    print("── Building true OMOP CONDITION_OCCURRENCE table ──")
    df = pd.read_parquet(local_dir / "condition_fhir.parquet")
    
    # We must map your parquet columns (fhir_condition_id, fhir_patient_id, snomed_code)
    # to the OMOP standard names (condition_occurrence_id, person_id, condition_concept_id)
    cond_occ = pd.DataFrame()
    cond_occ['condition_occurrence_id'] = df['fhir_condition_id'].apply(uuid_to_int)
    cond_occ['person_id'] = df['fhir_patient_id'].apply(uuid_to_int)
    cond_occ['condition_concept_id'] = df['snomed_code'].apply(lambda x: uuid_to_int(str(x)))
    cond_occ['condition_start_date'] = pd.to_datetime(df['onset_date']).dt.date
    cond_occ['condition_type_concept_id'] = 32020 
    cond_occ['condition_source_value'] = df['snomed_code']
    
    cond_occ.to_sql("condition_occurrence", con=engine, if_exists="replace", index=False)
    print(f"  ✓ condition_occurrence: {len(cond_occ):,} rows loaded")
def main():
    print("=== Azure SQL OMOP Database Builder ===")
    load_dotenv()
    local_dir = Path(os.getenv("LOCAL_PROCESSED_PATH", "data/processed/fhir_parsed"))
    
    if not local_dir.exists():
        print(f"❌ Could not find the folder: {local_dir}")
        return

    print("Connecting to Azure SQL...")
    engine = get_engine()
    
    for attempt in range(3):
        try:
            with engine.connect() as conn:
                pass
            print("✅ Database is online and connected!")
            break
        except Exception as e:
            print(f"😴 Database waking up... (Attempt {attempt+1}/3)")
            time.sleep(15)
    
    load_person(engine, local_dir)
    load_visit_occurrence(engine, local_dir)
    load_cost(engine, local_dir)
    load_concept(engine, local_dir)
    load_condition_occurrence(engine, local_dir)
    print("=== OMOP Tables Successfully Deployed to Azure! ===")

if __name__ == "__main__":
    main()