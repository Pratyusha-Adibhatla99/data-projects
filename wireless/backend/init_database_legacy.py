#!/usr/bin/env python3
"""
Initialize the wireless data database with correct schema
This creates the 'files' table that the web app expects
"""

import sqlite3
import os
from pathlib import Path

# Database will be created in the database/ folder
DB_DIR = Path("database")
DB_PATH = DB_DIR / "wireless_data_backup.db"

def init_database():
    """Initialize database with correct schema for file metadata storage"""
    
    # Create database directory if it doesn't exist
    DB_DIR.mkdir(exist_ok=True)
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the files table with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_hash TEXT UNIQUE,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            metadata TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database initialized successfully at {DB_PATH}")
    print(f"✓ Created table: files")
    print(f"\nDatabase is ready to store file metadata!")

if __name__ == "__main__":
    # Check if database already exists
    if DB_PATH.exists():
        response = input(f"⚠️  Database already exists at {DB_PATH}\nDo you want to recreate it? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted. Database not modified.")
            exit(0)
        
        # Backup existing database
        backup_path = DB_PATH.parent / f"{DB_PATH.stem}_backup.db"
        import shutil
        shutil.copy(DB_PATH, backup_path)
        print(f"✓ Backed up existing database to {backup_path}")
        
        # Remove old database
        DB_PATH.unlink()
        print(f"✓ Removed old database")
    
    init_database()