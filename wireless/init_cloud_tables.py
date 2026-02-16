from backend.app import app
from backend.models.db import db
from sqlalchemy import text

def init_medallion_tables():
    with app.app_context():
        print("🚀 Connecting to Azure SQL to initialize tables...")
        
        # 1. Create BRONZE_FILES Table
        # Matches the columns in your bronze_service.py
        create_bronze = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='bronze_files' AND xtype='U')
        CREATE TABLE bronze_files (
            id INT IDENTITY(1,1) PRIMARY KEY,
            filename NVARCHAR(255) NOT NULL,
            file_path NVARCHAR(MAX) NOT NULL,
            file_size BIGINT,
            file_hash NVARCHAR(64),
            file_extension NVARCHAR(20),
            modality NVARCHAR(50),
            user_id INT,
            dataset_name NVARCHAR(255),
            dataset_folder NVARCHAR(255),
            upload_time_pst DATETIME
        );
        """
        
        # 2. Create DATA_LINEAGE Table
        # Required for your "Source Researcher" tracking
        create_lineage = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='data_lineage' AND xtype='U')
        CREATE TABLE data_lineage (
            id INT IDENTITY(1,1) PRIMARY KEY,
            bronze_file_id INT,
            source_dataset NVARCHAR(255),
            source_file_path NVARCHAR(MAX),
            source_researcher NVARCHAR(100),
            upload_time_pst DATETIME,
            transformation_type NVARCHAR(50),
            status NVARCHAR(20),
            FOREIGN KEY (bronze_file_id) REFERENCES bronze_files(id)
        );
        """

        try:
            print("⏳ Creating 'bronze_files' table...", end=" ")
            db.session.execute(text(create_bronze))
            print("✅ Done.")

            print("⏳ Creating 'data_lineage' table...", end=" ")
            db.session.execute(text(create_lineage))
            print("✅ Done.")

            db.session.commit()
            print("\n🎉 ALL CLOUD TABLES CREATED SUCCESSFULLY!")
            
        except Exception as e:
            print(f"\n❌ Error creating tables: {e}")
            db.session.rollback()

if __name__ == "__main__":
    init_medallion_tables()