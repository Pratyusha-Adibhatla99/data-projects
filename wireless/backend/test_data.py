from dotenv import load_dotenv
load_dotenv()
import os, pymssql
from azure.storage.blob import BlobServiceClient

CONTAINER = os.getenv('BRONZE_CONTAINER_NAME', 'bronze-layer')

def get_db():
    return pymssql.connect(
        server   = os.getenv("AZURE_SQL_SERVER"),
        user     = os.getenv("AZURE_SQL_USER"),
        password = os.getenv("AZURE_SQL_PASSWORD"),
        database = os.getenv("AZURE_SQL_DATABASE"),
        as_dict  = True
    )

def step1_add_missing_columns():
    """Add researcher_name, researcher_email, is_deleted if they don't exist"""
    print("\n[STEP 1] Adding missing columns to bronze_files...")
    conn   = get_db()
    cursor = conn.cursor()

    # Add columns one by one (SQL Server ignores IF NOT EXISTS so we catch errors)
    alterations = [
        "ALTER TABLE bronze_files ADD researcher_name  NVARCHAR(200) NULL",
        "ALTER TABLE bronze_files ADD researcher_email NVARCHAR(200) NULL",
        "ALTER TABLE bronze_files ADD is_deleted       BIT DEFAULT 0",
    ]

    for sql in alterations:
        try:
            cursor.execute(sql)
            conn.commit()
            col = sql.split("ADD")[1].strip().split()[0]
            print(f"  ✅ Added column: {col}")
        except Exception as e:
            if "Column names in each table must be unique" in str(e) or \
               "already an object named" in str(e) or \
               "Duplicate column" in str(e):
                col = sql.split("ADD")[1].strip().split()[0]
                print(f"  ℹ️  Column already exists: {col}")
            else:
                print(f"  ⚠️  {e}")

    # Also add to data_lineage if needed
    lineage_cols = [
        "ALTER TABLE data_lineage ADD source_researcher_email NVARCHAR(200) NULL",
    ]
    for sql in lineage_cols:
        try:
            cursor.execute(sql)
            conn.commit()
            print(f"  ✅ Added lineage column")
        except:
            print(f"  ℹ️  Lineage column already exists")

    conn.close()
    print("  ✅ Schema update complete")


def step2_show_bad_blobs():
    """List existing blobs with bad paths (using user_id instead of name)"""
    print("\n[STEP 2] Scanning blob storage for bad paths...")
    bsc = BlobServiceClient.from_connection_string(
        os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    )
    container_client = bsc.get_container_client(CONTAINER)

    bad_blobs  = []
    good_blobs = []

    for blob in container_client.list_blobs():
        name = blob.name
        # Bad pattern: starts with a number (user_id) instead of a name
        first_part = name.split('/')[0]
        if first_part.isdigit():
            bad_blobs.append(name)
        else:
            good_blobs.append(name)

    print(f"\n  ❌ BAD blobs (using user_id, need to delete): {len(bad_blobs)}")
    for b in bad_blobs:
        print(f"     {b}")

    print(f"\n  ✅ GOOD blobs (correct format): {len(good_blobs)}")
    for b in good_blobs:
        print(f"     {b}")

    return bad_blobs


def step3_delete_bad_blobs(bad_blobs):
    """Delete blobs with bad paths"""
    if not bad_blobs:
        print("\n[STEP 3] No bad blobs to delete ✅")
        return

    print(f"\n[STEP 3] Deleting {len(bad_blobs)} bad blobs...")
    bsc = BlobServiceClient.from_connection_string(
        os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    )
    container_client = bsc.get_container_client(CONTAINER)

    for blob_name in bad_blobs:
        try:
            container_client.delete_blob(blob_name)
            print(f"  🗑️  Deleted: {blob_name}")
        except Exception as e:
            print(f"  ⚠️  Could not delete {blob_name}: {e}")

    print("  ✅ Cleanup complete")


def step4_clear_sql_records():
    """Clear bad SQL records so user can re-upload fresh"""
    print("\n[STEP 4] Clearing bad SQL records...")
    conn   = get_db()
    cursor = conn.cursor()

    # Show what we're clearing
    cursor.execute("SELECT COUNT(*) AS cnt FROM bronze_files")
    count = cursor.fetchone()['cnt']
    print(f"  Found {count} existing records")

    if count > 0:
        # Delete lineage first (foreign key)
        cursor.execute("DELETE FROM data_lineage")
        cursor.execute("DELETE FROM bronze_files")
        conn.commit()
        print(f"  🗑️  Cleared {count} records from bronze_files")
        print(f"  🗑️  Cleared all lineage records")

    conn.close()
    print("  ✅ SQL cleared - ready for fresh uploads")


def step5_verify():
    """Verify everything is clean"""
    print("\n[STEP 5] Verifying clean state...")

    # Check SQL
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM bronze_files")
    sql_count = cursor.fetchone()['cnt']
    conn.close()
    print(f"  SQL bronze_files: {sql_count} rows (should be 0)")

    # Check Blob
    bsc = BlobServiceClient.from_connection_string(
        os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    )
    container_client = bsc.get_container_client(CONTAINER)
    blobs = list(container_client.list_blobs())
    print(f"  Blob storage: {len(blobs)} blobs (should be 0)")

    if sql_count == 0 and len(blobs) == 0:
        print("\n  ✅ CLEAN STATE CONFIRMED")
        print("  → You can now re-upload your files")
        print("  → Files will be saved as: pratyusha/radar0/0001.csv")
    else:
        print("\n  ⚠️  Some data remains - check manually")


if __name__ == "__main__":
    print("=" * 60)
    print("BRONZE LAYER MIGRATION & CLEANUP")
    print("=" * 60)
    print("\nThis will:")
    print("  1. Add missing columns to SQL tables")
    print("  2. Delete bad blobs (1/Default_Dataset/...)")
    print("  3. Clear SQL records")
    print("  4. Leave you with a clean state to re-upload")

    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        exit()

    step1_add_missing_columns()
    bad_blobs = step2_show_bad_blobs()
    step3_delete_bad_blobs(bad_blobs)
    step4_clear_sql_records()
    step5_verify()

    print("\n" + "=" * 60)
    print("DONE - Re-upload your files now")
    print("They will be saved as: pratyusha/foldername/filename.csv")
    print("=" * 60)












