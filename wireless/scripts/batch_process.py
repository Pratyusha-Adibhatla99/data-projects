import os
import sys

# Ensure Python can find your 'backend' folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.silver_service import SilverService

def run_cloud_batch_conversion():
    print(f"\n{'='*70}")
    print("🚀 Starting Medallion Pipeline: Bronze -> Silver")
    print(f"{'='*70}\n")
    
    silver_service = SilverService()
    conn = silver_service.get_db_connection()
    cursor = conn.cursor()

    try:
        # Query the ledger for ANY raw files (CSV or MAT)
        cursor.execute("""
            SELECT id, filename, file_path, file_extension 
            FROM bronze_files 
            WHERE file_extension IN ('csv', 'mat', 'pcd') 
              AND processing_status = 'raw' 
              AND is_deleted = 0
        """)
        unprocessed_files = cursor.fetchall()

        if not unprocessed_files:
            print("✨ No new files to process. The Silver Layer is up to date!")
            return

        total_files = len(unprocessed_files)
        print(f"📦 Found {total_files} file(s) pending Silver transformation.\n")

        success_count = 0
        
        for i, file in enumerate(unprocessed_files, 1):
            file_id = file['id']
            filename = file['filename']
            ext = file['file_extension']
            
            print(f"⏳ [{i}/{total_files}] Processing {ext.upper()}: {filename}...")
            
            # Route to the correct processor based on the file extension
            if ext == 'csv':
                success = silver_service.process_csv_to_parquet(file_id)
            elif ext == 'mat':
                success = silver_service.process_mat_to_silver(file_id)
            elif ext == 'pcd':
                success = silver_service.process_pcd_to_silver(file_id)
            else:
                success = False
            
            if success:
                success_count += 1

        print(f"\n{'='*70}")
        print(f"🎉 Pipeline Complete! Successfully converted {success_count}/{total_files} files.")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"❌ Pipeline encountered a critical error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_cloud_batch_conversion()