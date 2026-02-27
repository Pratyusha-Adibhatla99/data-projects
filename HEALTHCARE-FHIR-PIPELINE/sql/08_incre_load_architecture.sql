-- /* =========================================================================================
--    FILE: 08_incremental_load_architecture.sql
--    AUTHOR: Pratyusha Adibhatla
   
--    ARCHITECTURE NOTE (MVP vs. PRODUCTION ELT): 
--    For the current scope of ~1,774 synthetic patients and ~300,000 fact rows, the pipeline 
--    utilizes an idempotent Truncate-and-Load batch process. At this volume, a full 
--    refresh takes mere minutes, making it the most stable and cost-effective approach.

--    PRODUCTION SCALING PATH (INCREMENTAL LOAD):
--    As the dataset scales to 1M+ patients, full refreshes become computationally expensive. 
--    This script documents the database-side ELT architecture for a High-Watermark 
--    Incremental Load. It defines the Control Table, the Staging Layer, and the Master 
--    Stored Procedure required to execute a secure Upsert (MERGE) operation natively 
--    within Azure SQL.
--    ========================================================================================= */

-- /* -----------------------------------------------------------------------------------------
--    STEP 1: METADATA CONTROL TABLE (THE WATERMARK)
--    Instead of dropping and reloading everything, we track exactly when the pipeline 
--    last ran. Azure Data Factory (ADF) queries this table before extracting new data.
--    ----------------------------------------------------------------------------------------- */
 CREATE TABLE etl_control_table (
    pipeline_name VARCHAR(100) PRIMARY KEY,
    target_table VARCHAR(100),
    last_processed_timestamp DATETIME
);

-- Seed the initial baseline watermark
INSERT INTO etl_control_table (pipeline_name, target_table, last_processed_timestamp) 
VALUES ('synthea_claims_ingestion', 'fact_claims', '2010-01-01 00:00:00');


-- /* -----------------------------------------------------------------------------------------
--    STEP 2: STAGING TABLE (THE LANDING ZONE)
--    A temporary table that perfectly mirrors the target Fact table. 
--    Python flattens the NEW daily JSON files into Parquet, and ADF runs a COPY INTO 
--    command to dump those records here. This table is TRUNCATED before every run.
--    ----------------------------------------------------------------------------------------- */
CREATE TABLE stg_fact_claims (
    encounter_token VARCHAR(100),
    patient_key INT,
    total_claim_cost DECIMAL(18,2),
    payer_coverage DECIMAL(18,2),
    patient_out_of_pocket DECIMAL(18,2)
);


-- /* -----------------------------------------------------------------------------------------
--    STEP 3: MASTER MERGE STORED PROCEDURE (THE UPSERT)
--    This procedure is triggered by ADF after the staging table is populated.
--    It securely merges the delta records into production and updates the watermark.
--    ----------------------------------------------------------------------------------------- */
CREATE PROCEDURE sp_incremental_load_fact_claims
AS
BEGIN
    SET NOCOUNT ON;
   -- Use TRY...CATCH to ensure the pipeline fails gracefully if an error occurs
    BEGIN TRY
        -- Wrap the MERGE and the Watermark update in a single transaction.
        -- If one fails, the entire block rolls back to prevent data corruption.
        BEGIN TRANSACTION;
      -- 3A. EXECUTE THE MERGE (UPSERT)
        MERGE fact_claims AS target
        USING stg_fact_claims AS source
        ON target.encounter_token = source.encounter_token -- Primary Key Match

        -- WHEN MATCHED: The claim already exists. Update the financial metrics 
        -- in case of insurance adjustments or late-arriving modifications.
        WHEN MATCHED THEN 
            UPDATE SET 
                target.total_claim_cost = source.total_claim_cost,
                target.payer_coverage = source.payer_coverage,
                target.patient_out_of_pocket = source.patient_out_of_pocket

        -- WHEN NOT MATCHED: It is a brand new encounter. Insert the full row.
        WHEN NOT MATCHED BY TARGET THEN 
            INSERT (encounter_token, patient_key, total_claim_cost, payer_coverage, patient_out_of_pocket)
            VALUES (source.encounter_token, source.patient_key, source.total_claim_cost, source.payer_coverage, source.patient_out_of_pocket);

        -- 3B. UPDATE THE WATERMARK
        -- CRITICAL LOGIC: Timestamps are explicitly recorded in UTC (not PST) 
        -- to better accommodate researchers pulling data from different regions, 
        -- preventing timezone-shift data duplication.
        UPDATE etl_control_table
        SET last_processed_timestamp = GETUTCDATE()
        WHERE pipeline_name = 'synthea_claims_ingestion';
-- --
-- --         -- If both steps succeed, commit the changes to the database
        COMMIT TRANSACTION;
        PRINT 'Incremental load and UTC watermark update completed successfully.';
        
    END TRY
    BEGIN CATCH
        -- Rollback all changes if any part of the transaction fails
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
-- --             
-- --         -- Raise the specific SQL error back to Azure Data Factory for pipeline alerting
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@ErrorMessage, 16, 1);
    END CATCH
END;