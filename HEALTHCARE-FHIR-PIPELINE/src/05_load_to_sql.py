import os
import urllib.parse
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from sqlalchemy import create_engine
from dotenv import load_dotenv
import time

def get_engine():
    """Uses the official Microsoft ODBC driver and scrubs .env variables"""
    load_dotenv()
    
    # .strip().strip('"').strip("'") removes ALL hidden spaces and quote marks!
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

def load_dim_date(engine):
    print("── Building dim_date ──")
    start, end = date(2010, 1, 1), date(2035, 12, 31)
    dates, cur = [], start
    while cur <= end:
        dates.append({
            "date_key": int(cur.strftime("%Y%m%d")),
            "full_date": cur.isoformat(),
            "year": cur.year,
            "month": cur.month,
            "day_of_week": cur.isoweekday(),
            "is_weekend": int(cur.isoweekday() >= 6),
        })
        cur += timedelta(days=1)
    df = pd.DataFrame(dates)
    df.to_sql("dim_date", con=engine, if_exists="replace", index=False)
    print(f"  ✓ dim_date: {len(df):,} rows loaded")

def load_dim_patient(engine, local_dir):
    print("── Building dim_patient ──")
    df = pd.read_parquet(local_dir / "patient_fhir.parquet")
    
    # Grab the exact columns that exist in your Parquet file
    dim_df = df[['fhir_patient_id', 'gender', 'birth_year', 'race', 'zip_3digit']].copy()
    
    # Rename fhir_patient_id to patient_token to match your Star Schema design
    dim_df.rename(columns={'fhir_patient_id': 'patient_token'}, inplace=True)
    
    dim_df.to_sql("dim_patient", con=engine, if_exists="replace", index=False)
    print(f"  ✓ dim_patient: {len(dim_df):,} rows loaded")
    
def load_dim_condition(engine, local_dir):
    print("── Building dim_condition ──")
    df = pd.read_parquet(local_dir / "condition_fhir.parquet")
    
    # Your parser already named these perfectly!
    dim_df = df[['snomed_code', 'snomed_display']].drop_duplicates().dropna()
    
    dim_df.to_sql("dim_condition", con=engine, if_exists="replace", index=False)
    print(f"  ✓ dim_condition: {len(dim_df):,} rows loaded")

def load_fact_encounter(engine, local_dir):
    print("── Building fact_encounter ──")
    df = pd.read_parquet(local_dir / "encounter_fhir.parquet")
    
    # Create the date_key using your 'start_date' column
    df['date_key'] = pd.to_datetime(df['start_date']).dt.strftime('%Y%m%d').astype(int)
    
    # Select the columns based on your exact Parquet output
    fact_df = df[['fhir_encounter_id', 'fhir_patient_id', 'date_key', 'class_display', 'reason_code', 'reason_display']].copy()
    
    # Rename them to fit the Star Schema design
    fact_df.rename(columns={
        'fhir_encounter_id': 'encounter_token', 
        'fhir_patient_id': 'patient_token', 
        'class_display': 'encounter_type',
        'reason_display': 'reason_description'
    }, inplace=True)
    
    fact_df.to_sql("fact_encounter", con=engine, if_exists="replace", index=False)
    print(f"  ✓ fact_encounter: {len(fact_df):,} rows loaded")

def load_fact_claims(engine, local_dir):
    print("── Building fact_claims ──")
    df = pd.read_parquet(local_dir / "claims_fhir.parquet")
    
    # THE FIX: Add utc=True to handle messy healthcare timezones
    df['date_key'] = pd.to_datetime(df['created'], utc=True).dt.strftime('%Y%m%d').astype(int)
    
    # Map FHIR fields to your SQL Star Schema
    fact_df = df[['claim_id', 'patient_id', 'date_key', 'total_cost', 'payment_amount']].copy()
    fact_df.rename(columns={
        'claim_id': 'claim_token',
        'patient_id': 'patient_token',
        'payment_amount': 'payer_coverage'
    }, inplace=True)
    
    # Add a calculated column for out-of-pocket cost
    fact_df['patient_out_of_pocket'] = fact_df['total_cost'] - fact_df['payer_coverage']

    fact_df.to_sql("fact_claims", con=engine, if_exists="replace", index=False)
    print(f"  ✓ fact_claims: {len(fact_df):,} rows loaded")

    
    
def main():
    print("=== Azure SQL Star Schema Builder ===")
    load_dotenv()
    local_dir = Path(os.getenv("LOCAL_PROCESSED_PATH", "data/processed/fhir_parsed"))
    
    if not local_dir.exists():
        print(f"❌ Could not find the folder: {local_dir}")
        return

    print("Connecting to Azure SQL...")
    engine = get_engine()
    
    # Try to wake up the database before loading
    for attempt in range(3):
        try:
            with engine.connect() as conn:
                pass
            print("✅ Database is online and connected!")
            break
        except Exception as e:
            print(f"😴 Database waking up... (Attempt {attempt+1}/3)")
            time.sleep(15)
    
    load_dim_date(engine)
    load_dim_patient(engine, local_dir)
    load_dim_condition(engine, local_dir)
    load_fact_encounter(engine, local_dir)
    load_fact_claims(engine, local_dir)
    print("=== Star Schema Successfully Deployed to Azure! ===")

if __name__ == "__main__":
    main()