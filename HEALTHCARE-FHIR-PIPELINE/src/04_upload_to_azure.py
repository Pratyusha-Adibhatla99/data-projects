"""
04_upload_to_azure.py
---------------------
Reads local Parquet files and securely uploads them to Azure Blob Storage 
using credentials from the .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load variables from .env
load_dotenv()

AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
PROCESSED_CONTAINER = os.getenv("BLOB_CONTAINER_PROCESSED")
LOCAL_PROCESSED_DIR = Path(os.getenv("LOCAL_PROCESSED_PATH"))

def main():
    print("=== Azure Blob Storage Uploader ===")
    
    # Safety check
    if not AZURE_CONN_STR or "your_connection_string_here" in AZURE_CONN_STR:
        print("❌ ERROR: Please put your real Azure Connection String in the .env file!")
        return

    # Connect to Azure
    print("Connecting to Azure...")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    
    # Check if container exists, if not, create it
    container_client = blob_service_client.get_container_client(PROCESSED_CONTAINER)
    if not container_client.exists():
        print(f"Creating container '{PROCESSED_CONTAINER}'...")
        container_client.create_container()

    # Find the Parquet files we generated earlier
    parquet_files = list(LOCAL_PROCESSED_DIR.glob("*.parquet"))
    
    if not parquet_files:
        print(f"⚠️ No Parquet files found in {LOCAL_PROCESSED_DIR}")
        return

    # Upload the files
    for file_path in parquet_files:
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"Uploading {file_path.name} ({file_size_mb:.2f} MB)...")
        
        blob_client = blob_service_client.get_blob_client(
            container=PROCESSED_CONTAINER, 
            blob=file_path.name
        )
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print(f"✅ {file_path.name} successfully uploaded!")

    print("=== All files uploaded to Azure! ===")

if __name__ == "__main__":
    main()
    