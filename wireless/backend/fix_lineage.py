import sqlite3
import os

# FIX: Go up one level (..) to find the database folder
# wireless/backend/fix_lineage.py -> wireless/database/wireless_data.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/wireless_data.db'))

if not os.path.exists(DB_PATH):
    print(f"❌ Database STILL not found at: {DB_PATH}")
    print("👉 Check if 'wireless_data.db' actually exists in the 'database' folder.")
    exit()

print(f"🔧 Connecting to database at: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Attempt to add the missing column
    print("👉 Adding 'status' column to data_lineage table...")
    cursor.execute("ALTER TABLE data_lineage ADD COLUMN status TEXT DEFAULT 'success'")
    conn.commit()
    print("✅ Success! Column 'status' added.")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("⚠️  Column 'status' already exists. No changes needed.")
    else:
        print(f"❌ Error: {e}")

conn.close()
