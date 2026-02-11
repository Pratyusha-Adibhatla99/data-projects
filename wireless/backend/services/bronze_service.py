import os
import sqlite3
from werkzeug.utils import secure_filename
from backend.utils.common import get_pst_time, calculate_file_hash, detect_modality

class BronzeService:
    def __init__(self, db_path, upload_root):
        self.db_path = db_path
        self.upload_root = upload_root

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def process_upload(self, file_obj, dataset_name, user_email, user_id, user_full_name):
        """
        Handles the end-to-end logic of saving a Bronze file.
        Returns: (Success: bool, Message: str)
        """
        # 1. Prepare Paths
        safe_email = user_email.replace('@', '_').replace('.', '_')
        safe_dataset = secure_filename(dataset_name)
        
        dataset_path = os.path.join(self.upload_root, safe_email, safe_dataset)
        os.makedirs(dataset_path, exist_ok=True)

        filename = secure_filename(file_obj.filename)
        filepath = os.path.join(dataset_path, filename)

        # 2. Save Physical File
        file_obj.save(filepath, buffer_size=16384)

        # 3. Calculate Metadata
        file_size = os.path.getsize(filepath)
        file_hash = calculate_file_hash(filepath)
        upload_time = get_pst_time()
        modality = detect_modality(filename)
        ext = filename.split('.')[-1].lower()

        # 4. Database Transaction
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            # Check Duplicates
            cursor.execute("SELECT id FROM bronze_files WHERE user_id=? AND file_hash=?", (user_id, file_hash))
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                return True, f"Skipped duplicate: {filename}"

            # Insert Metadata (Bronze Files)
            cursor.execute('''
                INSERT INTO bronze_files (
                    filename, file_path, file_size, file_hash, 
                    file_extension, modality, user_id, 
                    dataset_name, dataset_folder, upload_time_pst
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (filename, filepath, file_size, file_hash, ext, modality, user_id, safe_dataset, dataset_path, upload_time))
            
            # --- FIX: Insert Lineage (NOW INCLUDES source_dataset) ---
            bronze_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO data_lineage (
                    bronze_file_id, 
                    source_dataset,      
                    source_file_path, 
                    source_researcher, 
                    upload_time_pst, 
                    transformation_type, 
                    status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (bronze_id, safe_dataset, filepath, user_full_name, upload_time, 'ingestion', 'success'))

            conn.commit()
            return True, f"Uploaded {filename}"

        except Exception as e:
            conn.rollback()
            # CRITICAL: Re-raise the exception so the Controller knows it failed
            raise e
        finally:
            conn.close()
            
    def get_user_files(self, user_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT filename, file_size, file_extension, modality, upload_time_pst, dataset_name 
            FROM bronze_files 
            WHERE user_id = ? 
            ORDER BY upload_time_pst DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
