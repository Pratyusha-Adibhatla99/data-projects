#!/usr/bin/env python3
"""
Interactive Database Explorer & SQL Shell
1. Finds all databases in the project.
2. Can select one database.
3. Launches a SQL shell to explore it.
"""

import sqlite3
import sys
import os
from pathlib import Path

# Try to import readline for better input handling (history support)
try:
    import readline
except ImportError:
    pass  # Not available on all platforms (like basic Windows), but that's fine

# ─── CONFIGURATION ──────────────────────────────────────────────────
SEARCH_DIRS = [
    ".", 
    "database", 
    "backend/database", 
    "../database"
]

# ─── 1. FINDER LOGIC ────────────────────────────────────────────────
def find_all_databases():
    """Scans for database files recursively in common folders"""
    db_files = []
    seen_paths = set()

    for d in SEARCH_DIRS:
        path = Path(d)
        if path.exists():
            # Look for .db, .sqlite, and files with no extension named '*db*'
            patterns = ["*.db", "*.sqlite", "*db*"] 
            
            for pattern in patterns:
                for file in path.glob(pattern):
                    # Filter out directories and non-database looking files
                    if file.is_file() and not file.name.endswith('.py'):
                        full_path = str(file.resolve())
                        if full_path not in seen_paths:
                            db_files.append(file)
                            seen_paths.add(full_path)
    
    return sorted(db_files, key=lambda p: p.name)

# ─── 2. DISPLAY LOGIC ───────────────────────────────────────────────
def print_query_results(cursor):
    """Formats and prints the results of a SELECT query nicely"""
    rows = cursor.fetchall()
    
    # If no results (empty table or query)
    if not rows:
        # Check if it was an update/insert (rowcount > -1)
        if cursor.rowcount > 0:
            print(f"   ✓ Success! {cursor.rowcount} rows affected.")
        else:
            print("   (No results returned)")
        return

    # Get column headers
    col_names = [desc[0] for desc in cursor.description]
    
    # Calculate column widths for pretty printing
    widths = [len(name) for name in col_names]
    formatted_rows = []
    
    for row in rows:
        formatted_row = []
        for i, val in enumerate(row):
            val_str = str(val)
            # Truncate huge text/JSON blobs so they don't break the screen
            if len(val_str) > 60: 
                val_str = val_str[:57] + "..."
            formatted_row.append(val_str)
            widths[i] = max(widths[i], len(val_str))
        formatted_rows.append(formatted_row)

    # Print Table
    header = " | ".join(name.ljust(w) for name, w in zip(col_names, widths))
    separator = "-" * len(header)
    
    print("\n" + separator)
    print(header)
    print(separator)

    for row in formatted_rows:
        print(" | ".join(val.ljust(w) for val, w in zip(row, widths)))
    
    print(f"({len(rows)} rows)\n")

# ─── 3. INTERACTIVE SHELL ───────────────────────────────────────────
def run_sql_shell(db_path):
    """The main loop for writing queries"""
    print(f"\n" + "="*60)
    print(f"🔌 CONNECTED TO: {db_path.name}")
    print(f"📂 Path: {db_path}")
    print("="*60)
    print("Type your SQL query below.")
    print("• To see tables:  .tables")
    print("• To see schema:  .schema <table_name>")
    print("• To quit:        exit")
    print("-" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    while True:
        try:
            # Get input
            query = input("\nsql> ").strip()

            # Handle special commands
            if query.lower() in ['exit', 'quit', 'q']:
                break
            if not query:
                continue
            
            # Helper: .tables shortcut
            if query.lower() == '.tables':
                query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            
            # Helper: .schema shortcut
            if query.lower().startswith('.schema'):
                parts = query.split()
                if len(parts) > 1:
                    query = f"PRAGMA table_info({parts[1]});"
                else:
                    print("Usage: .schema <table_name>")
                    continue

            # Execute standard SQL
            try:
                cursor.execute(query)
                # If it's a SELECT (or PRAGMA), show results
                if query.lstrip().upper().startswith(("SELECT", "PRAGMA")):
                    print_query_results(cursor)
                else:
                    conn.commit()
                    print(f"   ✓ Executed. Rows affected: {cursor.rowcount}")

            except sqlite3.Error as e:
                print(f"❌ SQL Error: {e}")

        except KeyboardInterrupt:
            print("\nType 'exit' to quit")
            
    conn.close()
    print("\nDisconnected.")

# ─── MAIN EXECUTION ─────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Scan
    print("🔎 Scanning for databases...")
    databases = find_all_databases()

    if not databases:
        print("❌ No databases found! Check your 'database/' folder.")
        sys.exit(1)

    # 2. List
    print(f"\nFound {len(databases)} databases:")
    for i, db in enumerate(databases):
        print(f"   [{i+1}] {db.name}")

    # 3. Select
    selected_db = None
    if len(databases) == 1:
        print(f"\nAuto-selecting: {databases[0].name}")
        selected_db = databases[0]
    else:
        while True:
            try:
                choice = input(f"\nSelect a database (1-{len(databases)}): ")
                idx = int(choice) - 1
                if 0 <= idx < len(databases):
                    selected_db = databases[idx]
                    break
                print("Invalid number.")
            except ValueError:
                print("Please enter a number.")
    
    # 4. Launch Shell
    run_sql_shell(selected_db)