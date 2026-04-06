import os
import pymssql
import hashlib
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
from datetime import datetime
import tzlocal  # <-- New import for dynamic timezone detection
from dotenv import load_dotenv

load_dotenv()

class BronzeService:

    def __init__(self, db_source, upload_root):
        self.upload_root        = upload_root
        self.connection_string  = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name     = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')

    def get_db_connection(self):
        return pymssql.connect(
            server   = os.getenv("AZURE_SQL_SERVER"),
            user     = os.getenv("AZURE_SQL_USER"),
            password = os.getenv("AZURE_SQL_PASSWORD"),
            database = os.getenv("AZURE_SQL_DATABASE"),
            as_dict  = True
        )

    def _get_researcher_name(self, user_email, user_full_name):
        """
        Get clean first name from full name for folder naming.
        'Pratyusha Adibhatla' → 'pratyusha'
        Fallback to email prefix if no full name.
        """
        if user_full_name and user_full_name.strip():
            first_name = user_full_name.strip().split()[0].lower()
            return ''.join(c for c in first_name if c.isalnum())
        return user_email.split('@')[0].lower().replace('.', '_')

    def process_upload(self, file_obj, dataset_name, user_email,
                       user_id, user_full_name):
        """
        Process a single file upload.
        """
        filename      = secure_filename(file_obj.filename)
        
        # ── Capture the RAW local time and timezone ──
        raw_local_time = datetime.now()
        try:
            local_tz_string = str(tzlocal.get_localzone())
        except:
            local_tz_string = 'America/New_York'  # Safe fallback 
            
        ext           = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'unknown'
        researcher    = self._get_researcher_name(user_email, user_full_name)

        if dataset_name in ('Default_Dataset', '', None):
            blob_path    = f"{researcher}/{filename}"
            display_folder = None
        else:
            safe_folder  = secure_filename(dataset_name)
            blob_path    = f"{researcher}/{safe_folder}/{filename}"
            display_folder = safe_folder

        # ── 1. Stream to Azure Blob 
        sha256_hash = hashlib.sha256()
        file_size   = 0

        try:
            bsc         = BlobServiceClient.from_connection_string(self.connection_string)
            blob_client = bsc.get_blob_client(
                container = self.container_name,
                blob      = blob_path
            )

            print(f"🚀 Uploading → {blob_path}")
            file_obj.seek(0)

            def stream_generator():
                nonlocal file_size
                while True:
                    chunk = file_obj.read(4 * 1024 * 1024)  # 4MB chunks
                    if not chunk:
                        break
                    file_size += len(chunk)
                    sha256_hash.update(chunk)
                    yield chunk

            blob_client.upload_blob(stream_generator(), overwrite=True)
            final_hash = sha256_hash.hexdigest()

            print(f"✅ Blob saved: {blob_path} ({file_size/(1024**2):.2f} MB)")

        except Exception as e:
            print(f"❌ Blob upload failed: {e}")
            raise

        # ── 2. Record in Azure SQL 
        conn   = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, filename FROM bronze_files WHERE file_hash = %s",
                (final_hash,)
            )
            existing = cursor.fetchone()
            if existing:
                print(f"⚠️  Duplicate: {filename} matches {existing['filename']}")
                return True, f"Skipped duplicate: {filename}"

            # ── Insert using the RAW time and dynamic timezone ──
            cursor.execute("""
                INSERT INTO bronze_files (
                    filename,
                    file_path,
                    file_size,
                    file_hash,
                    file_extension,
                    modality,
                    user_id,
                    dataset_name,
                    dataset_folder,
                    raw_upload_time,      
                    upload_timezone,
                    processing_status,
                    researcher_name,
                    researcher_email
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, 'raw', %s, %s
                )
            """, (
                filename,
                blob_path,
                file_size,
                final_hash,
                ext,
                ext,             
                user_id,
                display_folder or 'root',
                blob_path,
                raw_local_time,   # Updated variable
                local_tz_string,  # Updated variable
                user_full_name,  
                user_email       
            ))

            cursor.execute("SELECT SCOPE_IDENTITY() AS id")
            bronze_id = cursor.fetchone()['id']

            # Note: Assuming you kept the column name 'upload_time_utc' in your data_lineage table, 
            # we are still passing the raw time into it here.
            cursor.execute("""
                INSERT INTO data_lineage (
                    bronze_file_id,
                    source_dataset,
                    source_file_path,
                    source_researcher,
                    source_researcher_email,
                    upload_time_utc,     
                    transformation_type,
                    status
                ) VALUES (%s, %s, %s, %s, %s, %s, 'ingestion', 'success')
            """, (
                bronze_id,
                display_folder or 'root',
                blob_path,
                user_full_name,
                user_email,
                raw_local_time   # Passed raw time to lineage table
            ))

            conn.commit()
            print(f"✅ SQL recorded: id={bronze_id}, researcher={user_full_name}")
            return True, f"Uploaded {filename} ({file_size/(1024**2):.2f} MB)"

        except Exception as e:
            conn.rollback()
            print(f"❌ SQL insert failed: {e}")
            raise
        finally:
            conn.close()

    def get_user_files(self, user_id):
        conn   = self.get_db_connection()
        cursor = conn.cursor()
        
        # Print to terminal so we can see who we are asking for!
        print(f"🔍 Searching Azure for files belonging to User ID: {user_id}")
        
        cursor.execute("""
            SELECT
                filename,
                file_size,
                file_extension,
                file_path,
                dataset_name,
                upload_time_utc,
                upload_timezone,
                researcher_name,
                researcher_email
            FROM bronze_files
            WHERE user_id = %s
              AND is_deleted = 0
            ORDER BY upload_time_utc DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        
        # Grab the column names (e.g., 'filename', 'file_size')
        dict_results = []
        for row in results:
            dict_results.append(dict(row))
            
        print(f"📦 Successfully parsed {len(dict_results)} files!")
        
        conn.close()
        return dict_results

    def get_all_files_for_admin(self):
        conn   = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                b.filename,
                b.file_size,
                b.file_path,
                b.file_extension,
                b.dataset_name,
                b.raw_upload_time,
                b.upload_timezone,
                b.researcher_name,
                b.researcher_email,
                l.transformation_type,
                l.status
            FROM bronze_files b
            LEFT JOIN data_lineage l ON b.id = l.bronze_file_id
            WHERE b.is_deleted = 0
            ORDER BY b.raw_upload_time DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return results