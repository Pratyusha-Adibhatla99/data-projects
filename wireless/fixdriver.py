import os
import shutil

# 1. Define where the driver lives on M1/M2 Macs
driver_path = "/opt/homebrew/lib/libmsodbcsql.17.dylib"
if not os.path.exists(driver_path):
    # Fallback for Intel Macs
    driver_path = "/usr/local/lib/libmsodbcsql.17.dylib"

# 2. Define the config content
config_content = f"""[ODBC Driver 17 for SQL Server]
Description = Microsoft ODBC Driver 17 for SQL Server
Driver      = {driver_path}
UsageCount  = 1
"""

# 3. Find where unixODBC expects the config file
# We check the environment or default to Homebrew's location
target_file = "/opt/homebrew/etc/odbcinst.ini"
if not os.path.exists(os.path.dirname(target_file)):
    target_file = "/usr/local/etc/odbcinst.ini"

print(f"🔧 Fixing ODBC Driver...")
print(f"   Driver Path: {driver_path}")
print(f"   Target Config: {target_file}")

try:
    # Write the file (requires sudo if permission denied, but try direct first)
    with open("temp_odbc.ini", "w") as f:
        f.write(config_content)
    
    # Use shell move to handle permissions if needed
    os.system(f"sudo mv temp_odbc.ini {target_file}")
    print("✅ Driver Registered Successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")