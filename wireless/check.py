import sqlite3
import os

# Connect to DB
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'wireless_data.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n🔎 CHECKING DATABASE FILES...")
# Get all files
cursor.execute("SELECT id, filename, user_id, dataset_name FROM bronze_files")
files = cursor.fetchall()

if not files:
    print("❌ database 'bronze_files' table is EMPTY.")
else:
    print(f"✅ Found {len(files)} files in database.")
    for f in files:
        print(f"   - ID: {f[0]} | File: {f[1]} | User ID: {f[2]} | Dataset: {f[3]}")

# Get Users to match IDs
print("\n👤 CHECKING USERS...")
cursor.execute("SELECT id, email FROM users")
users = cursor.fetchall()
for u in users:
    print(f"   - User ID {u[0]} = {u[1]}")

conn.close()