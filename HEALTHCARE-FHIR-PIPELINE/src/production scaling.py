"""
===============================================================================
FILE: 07_incremental_load_architecture.py
AUTHOR: Pratyusha Adibhatla

ARCHITECTURE NOTE (BATCH VS. INCREMENTAL):
For the current scope of the project (1,774 synthetic patients, ~300,000 fact rows), 
the pipeline utilizes an idempotent Truncate-and-Load batch process. At this 
volume, a full refresh takes less than 15 minutes, making Truncate-and-Load the 
most stable and cost-effective approach.

PRODUCTION SCALING PATH:
As the population scales to 1M+ patients, full refreshes become computationally 
expensive. This script documents the architectural transition to a High-Watermark 
Incremental Pipeline. It demonstrates how to use a UTC watermark to filter new 
FHIR JSON files in Python, stage the Parquet outputs, and execute a SQL MERGE 
(Upsert) in Azure SQL.
===============================================================================
"""

import os
import datetime
import logging

# Note: In production, engine is configured via SQLAlchemy or pyodbc
# engine = create_engine('mssql+pyodbc://user:pass@server/db')

def get_utc_watermark(engine, pipeline_name):
    """
    STEP 1: GET THE WATERMARK
    Queries the Azure SQL control table to find the exact UTC timestamp 
    of the last successful pipeline run.
    """
    logging.info(f"Fetching watermark for {pipeline_name}...")
    query = f"""
        SELECT last_processed_timestamp 
        FROM etl_control_table 
        WHERE pipeline_name = '{pipeline_name}'
    """
    # watermark_utc = engine.execute(query).scalar()
    # return watermark_utc
    pass


def extract_new_fhir_data(source_directory, watermark_utc):
    """
    STEP 2: INCREMENTAL EXTRACTION
    Instead of parsing all 100,000+ patient JSONs, the script only parses 
    files that have been created or modified AFTER the UTC watermark.
    """
    new_files_to_process = []
    
    for filename in os.listdir(source_directory):
        filepath = os.path.join(source_directory, filename)
        
        # Get OS modified time and convert to UTC
        mtime = os.path.getmtime(filepath)
        file_modified_utc = datetime.datetime.utcfromtimestamp(mtime)
        
        if file_modified_utc > watermark_utc:
            new_files_to_process.append(filepath)
            
    logging.info(f"Identified {len(new_files_to_process)} new files since {watermark_utc}")
    # Process files, flatten nested JSON (schema-on-read), and save as Parquet
    return new_files_to_process


def load_to_staging_and_merge(engine, parquet_path):
    """
    STEP 3 & 4: STAGING AND SQL UPSERT
    Loads the new data into a temporary staging table, then executes a 
    SQL Stored Procedure to perform the heavy MERGE operation natively in Azure.
    """
    # Step 3: Clear staging and load new batch
    truncate_stg_sql = "TRUNCATE TABLE stg_fact_claims;"
    # ADF COPY INTO command or pandas.to_sql('stg_fact_claims', engine) executes here
    
    # Step 4: The Upsert (MERGE) Logic
    # This SQL logic updates existing financial claims or inserts brand new ones
    merge_sql = """
        MERGE fact_claims AS target
        USING stg_fact_claims AS source
        ON target.encounter_token = source.encounter_token
        
        -- If claim exists, update the financials
        WHEN MATCHED THEN 
            UPDATE SET 
                target.total_claim_cost = source.total_claim_cost,
                target.payer_coverage = source.payer_coverage,
                target.patient_out_of_pocket = source.patient_out_of_pocket

        -- If new claim, insert it
        WHEN NOT MATCHED BY TARGET THEN 
            INSERT (encounter_token, patient_key, total_claim_cost, payer_coverage, patient_out_of_pocket)
            VALUES (source.encounter_token, source.patient_key, source.total_claim_cost, source.payer_coverage, source.patient_out_of_pocket);
    """
    logging.info("Executing Azure SQL MERGE operation...")
    # engine.execute(merge_sql)


def update_watermark(engine, pipeline_name):
    """
    STEP 5: RESET WATERMARK
    Upon successful pipeline completion, updates the control table to the current 
    UTC time. Using UTC accommodates researchers in different regions and prevents 
    timezone-shift data duplication.
    """
    update_sql = f"""
        UPDATE etl_control_table
        SET last_processed_timestamp = GETUTCDATE()
        WHERE pipeline_name = '{pipeline_name}';
    """
    logging.info("Pipeline successful. Watermark updated to GETUTCDATE().")
    # engine.execute(update_sql)


if __name__ == "__main__":
    # Execution flow template
    PIPELINE = 'synthea_daily_ingestion'
    SOURCE_DIR = '/data/fhir_raw/'
    
    # watermark = get_utc_watermark(engine, PIPELINE)
    # new_files = extract_new_fhir_data(SOURCE_DIR, watermark)
    # if new_files:
    #     load_to_staging_and_merge(engine, '/data/staged_parquet/')
    #     update_watermark(engine, PIPELINE)