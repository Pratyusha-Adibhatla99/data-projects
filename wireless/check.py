import os
import pymssql
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load your credentials
load_dotenv()

print("🔍 Checking Azure for your Datasets...\n")

# --- 1. Check Azure SQL (Metadata) ---
try:
    conn = pymssql.connect(
        server=os.getenv("AZURE_SQL_SERVER"), 
        user=os.getenv("AZURE_SQL_USER"), 
        password=os.getenv("AZURE_SQL_PASSWORD"), 
        database=os.getenv("AZURE_SQL_DATABASE"),
        as_dict=True
    )
    cursor = conn.cursor()
    cursor.execute("SELECT filename, file_size, upload_time_pst FROM bronze_files")
    rows = cursor.fetchall()
    
    print("📊 --- AZURE SQL DATABASE (bronze_files table) ---")
    if not rows:
        print("   Table is empty. No files logged yet.")
    else:
        for row in rows:
            size_mb = row['file_size'] / (1024 * 1024) if row['file_size'] else 0
            print(f"   📄 {row['filename']} ({size_mb:.2f} MB) - Uploaded: {row['upload_time_pst']}")
    print("")
    conn.close()
except Exception as e:
    print(f"❌ Azure SQL Failed: {e}\n")

# --- 2. Check Azure Blob Storage (Physical Files) ---
try:
    blob_conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("BRONZE_CONTAINER_NAME")
    
    if blob_conn_str and container_name:
        blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
        container_client = blob_service_client.get_container_client(container_name)
        
        print(f"📦 --- AZURE BLOB STORAGE (Container: {container_name}) ---")
        blobs = list(container_client.list_blobs())
        
        if not blobs:
            print("   Container is empty. No physical files found.")
        else:
            for blob in blobs:
                size_mb = blob.size / (1024 * 1024)
                print(f"   💾 {blob.name} ({size_mb:.2f} MB)")
    else:
        print("❌ Storage credentials missing from .env")
except Exception as e:
    print(f"❌ Blob Storage Failed: {e}")