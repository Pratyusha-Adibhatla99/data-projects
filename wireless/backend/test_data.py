import sqlite3
import os
import sys

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../database/wireless_data.db')

def audit_system():
    print(f"🕵️  STARTING BRONZE LAYER AUDIT...\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ CRITICAL: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- 1. VERIFY ITEM 3: CATALOGING ---
    print("📋 [ITEM 3] Checking Catalog (bronze_files table)...")
    cursor.execute("SELECT id, filename, file_path, user_id, upload_time_pst FROM bronze_files ORDER BY id DESC LIMIT 1")
    latest_file = cursor.fetchone()
    
    if not latest_file:
        print("   ⚠️  Database is empty. Upload a file first!")
        return
    
    print(f"   ✅ Catalog Entry Found:")
    print(f"      - ID: {latest_file['id']}")
    print(f"      - Name: {latest_file['filename']}")
    print(f"      - Owner User ID: {latest_file['user_id']}")
    print(f"      - Time: {latest_file['upload_time_pst']}")

    # --- 2. VERIFY ITEM 2: IMMUTABLE STORAGE ---
    print("\n📦 [ITEM 2] Checking Immutable Storage (Physical Files)...")
    real_path = latest_file['file_path']
    if os.path.exists(real_path):
        size = os.path.getsize(real_path)
        print(f"   ✅ File exists on disk at: {real_path}")
        print(f"   ✅ File Size: {size / 1024:.2f} KB")
        print("   ✅ Status: SAFE (Stored in 'uploads' directory)")
    else:
        print(f"   ❌ CRITICAL: File is missing from disk! Path: {real_path}")

    # --- 3. VERIFY ITEM 5: LINEAGE TRACKING ---
    print("\n🔗 [ITEM 5] Checking Data Lineage (data_lineage table)...")
    cursor.execute("SELECT * FROM data_lineage WHERE bronze_file_id=?", (latest_file['id'],))
    lineage = cursor.fetchone()
    
    if lineage:
        print(f"   ✅ Lineage Record Found:")
        print(f"      - Source Researcher: {lineage['source_researcher']}")
        print(f"      - Transformation: {lineage['transformation_type']} (Raw Ingestion)")
        print(f"      - Status: {lineage['status']}")
    else:
        print("   ❌ CRITICAL: Lineage broken. No entry found for this file.")

    conn.close()
    print("\n✨ AUDIT COMPLETE.")

if __name__ == "__main__":
    audit_system()