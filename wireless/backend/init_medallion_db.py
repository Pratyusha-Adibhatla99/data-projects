#!/usr/bin/env python3
"""
DAY 1: Medallion Architecture Database Schema
Creating Bronze, Silver, Gold layer tables with data lineage trackings
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path("database/wireless_data.db")

def create_medallion_schema():
    """Create complete Medallion Architecture schema"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("CREATING MEDALLION ARCHITECTURE SCHEMA")
    print("=" * 80)
    
    # ═══════════════════════════════════════════════════════════
    # USERS TABLE (for authentication)
    # ═══════════════════════════════════════════════════════════
    
    print("\n📋 Creating users table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            institution TEXT,
            research_area TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    print("   ✅ Users table created")
    
    # ═══════════════════════════════════════════════════════════
    # BRONZE LAYER - Raw Data Storage
    # ═══════════════════════════════════════════════════════════
    
    print("\n🥉 Creating BRONZE LAYER tables...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bronze_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- File information
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            file_hash TEXT UNIQUE,
            file_extension TEXT NOT NULL,
            
            -- Modality classification
            modality TEXT NOT NULL,  -- 'lidar', 'radar', 'wifi', 'channels'
            
            -- Ownership
            user_id INTEGER NOT NULL,
            dataset_name TEXT NOT NULL,
            dataset_folder TEXT NOT NULL,
            
            -- Upload tracking with timezone
            upload_time_local TIMESTAMP,
            upload_time_pst TIMESTAMP NOT NULL,
            upload_timezone TEXT,
            
            -- Status
            processing_status TEXT DEFAULT 'raw',  -- 'raw', 'processing', 'processed', 'failed'
            is_deleted BOOLEAN DEFAULT 0,
            
            -- Metadata
            metadata_json TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("   ✅ bronze_files table created")
    
    # ═══════════════════════════════════════════════════════════
    # SILVER LAYER - Cleaned & Aggregated Data
    # ═══════════════════════════════════════════════════════════
    
    print("\n🥈 Creating SILVER LAYER tables...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS silver_aggregated (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Aggregation info
            modality TEXT NOT NULL,  -- 'lidar', 'radar', 'wifi', 'channels'
            aggregation_name TEXT NOT NULL,
            
            -- Storage location
            data_path TEXT NOT NULL,  -- Path to aggregated parquet file
            metadata_path TEXT,
            lineage_path TEXT,
            
            -- Statistics
            source_file_count INTEGER,
            total_records INTEGER,
            data_size_bytes INTEGER,
            
            -- Quality metrics
            duplicate_count INTEGER DEFAULT 0,
            null_count INTEGER DEFAULT 0,
            quality_score REAL,  -- 0.0 to 1.0
            
            -- Processing info
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_duration_seconds REAL,
            
            -- Timestamp normalization
            timestamps_normalized BOOLEAN DEFAULT 0,
            timezone_standard TEXT DEFAULT 'PST',
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(modality, aggregation_name)
        )
    ''')
    print("   ✅ silver_aggregated table created")
    
    # ═══════════════════════════════════════════════════════════
    # GOLD LAYER - Analytics-Ready Metrics
    # ═══════════════════════════════════════════════════════════
    
    print("\n🥇 Creating GOLD LAYER tables...")
    
    # Daily upload metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_daily_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            date DATE NOT NULL,
            user_id INTEGER,
            modality TEXT,
            
            -- Metrics
            file_count INTEGER DEFAULT 0,
            total_size_bytes INTEGER DEFAULT 0,
            unique_datasets INTEGER DEFAULT 0,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(date, user_id, modality)
        )
    ''')
    print("   ✅ gold_daily_uploads table created")
    
    # Researcher statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_researcher_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            user_id INTEGER NOT NULL,
            
            -- Upload stats
            total_uploads INTEGER DEFAULT 0,
            total_storage_bytes INTEGER DEFAULT 0,
            total_datasets INTEGER DEFAULT 0,
            
            -- Modality breakdown
            lidar_count INTEGER DEFAULT 0,
            radar_count INTEGER DEFAULT 0,
            wifi_count INTEGER DEFAULT 0,
            channels_count INTEGER DEFAULT 0,
            
            -- Activity
            first_upload_date DATE,
            last_upload_date DATE,
            active_days INTEGER DEFAULT 0,
            
            -- Quality
            avg_quality_score REAL,
            
            last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id)
        )
    ''')
    print("   ✅ gold_researcher_stats table created")
    
    # Data quality metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gold_quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            date DATE NOT NULL,
            modality TEXT NOT NULL,
            
            -- Quality metrics
            total_files INTEGER DEFAULT 0,
            valid_files INTEGER DEFAULT 0,
            invalid_files INTEGER DEFAULT 0,
            duplicate_files INTEGER DEFAULT 0,
            
            avg_quality_score REAL,
            min_quality_score REAL,
            max_quality_score REAL,
            
            -- Issues
            null_value_count INTEGER DEFAULT 0,
            format_error_count INTEGER DEFAULT 0,
            
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(date, modality)
        )
    ''')
    print("   ✅ gold_quality_metrics table created")
    
    # ═══════════════════════════════════════════════════════════
    # DATA LINEAGE TRACKING
    # ═══════════════════════════════════════════════════════════
    
    print("\n🔗 Creating DATA LINEAGE table...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_lineage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Source (Bronze)
            bronze_file_id INTEGER,
            source_file_path TEXT NOT NULL,
            source_researcher TEXT NOT NULL,
            source_dataset TEXT NOT NULL,
            upload_time_pst TIMESTAMP NOT NULL,
            
            -- Destination (Silver)
            silver_aggregation_id INTEGER,
            destination_path TEXT,
            
            -- Transformation details
            transformation_type TEXT NOT NULL,  -- 'aggregation', 'deduplication', 'normalization'
            transformation_details TEXT,
            
            -- Processing
            processed_by TEXT,  -- 'pipeline' or user_id
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Status
            success BOOLEAN DEFAULT 1,
            error_message TEXT,
            
            FOREIGN KEY (bronze_file_id) REFERENCES bronze_files(id) ON DELETE SET NULL,
            FOREIGN KEY (silver_aggregation_id) REFERENCES silver_aggregated(id) ON DELETE SET NULL
        )
    ''')
    print("   ✅ data_lineage table created")
    
    # ═══════════════════════════════════════════════════════════
    # INDEXES for Performance
    # ═══════════════════════════════════════════════════════════
    
    print("\n📊 Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_bronze_user ON bronze_files(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_bronze_modality ON bronze_files(modality)",
        "CREATE INDEX IF NOT EXISTS idx_bronze_upload_pst ON bronze_files(upload_time_pst)",
        "CREATE INDEX IF NOT EXISTS idx_bronze_status ON bronze_files(processing_status)",
        
        "CREATE INDEX IF NOT EXISTS idx_silver_modality ON silver_aggregated(modality)",
        
        "CREATE INDEX IF NOT EXISTS idx_gold_uploads_date ON gold_daily_uploads(date)",
        "CREATE INDEX IF NOT EXISTS idx_gold_uploads_user ON gold_daily_uploads(user_id)",
        
        "CREATE INDEX IF NOT EXISTS idx_lineage_bronze ON data_lineage(bronze_file_id)",
        "CREATE INDEX IF NOT EXISTS idx_lineage_silver ON data_lineage(silver_aggregation_id)",
        "CREATE INDEX IF NOT EXISTS idx_lineage_time ON data_lineage(processed_at)",
    ]
    
    for idx in indexes:
        cursor.execute(idx)
    print(f"   ✅ {len(indexes)} indexes created")
    
    # ═══════════════════════════════════════════════════════════
    # Create default admin user
    # ═══════════════════════════════════════════════════════════
    
    print("\n👤 Creating default admin user...")
    
    import bcrypt
    
    # Hash password
    password = "admin123"  # CHANGE THIS IN PRODUCTION!
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, is_admin)
            VALUES (?, ?, ?, 1)
        ''', ('admin@wireless.lab', password_hash, 'Administrator'))
        print("   ✅ Admin user created")
        print("      Email: admin@wireless.lab")
        print("      Password: admin123")
        print("      ⚠️  CHANGE PASSWORD IN PRODUCTION!")
    except sqlite3.IntegrityError:
        print("   ℹ️  Admin user already exists")
    
    # ═══════════════════════════════════════════════════════════
    # COMMIT & VERIFY
    # ═══════════════════════════════════════════════════════════
    
    conn.commit()
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("\n" + "=" * 80)
    print("DATABASE SCHEMA CREATED SUCCESSFULLY")
    print("=" * 80)
    
    print(f"\n📊 Total tables: {len(tables)}")
    print("\nTables created:")
    for table in tables:
        if table != 'sqlite_sequence':
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table:30} ({count} rows)")
    
    print("\n" + "=" * 80)
    print("MEDALLION ARCHITECTURE LAYERS")
    print("=" * 80)
    
    print("\n🥉 BRONZE LAYER:")
    print("   • bronze_files - Raw data as uploaded by researchers")
    
    print("\n🥈 SILVER LAYER:")
    print("   • silver_aggregated - Cleaned & aggregated by modality")
    
    print("\n🥇 GOLD LAYER:")
    print("   • gold_daily_uploads - Upload metrics for dashboards")
    print("   • gold_researcher_stats - Researcher activity stats")
    print("   • gold_quality_metrics - Data quality reports")
    
    print("\n🔗 LINEAGE:")
    print("   • data_lineage - Track data from bronze → silver → gold")
    
    print("\n👤 AUTHENTICATION:")
    print("   • users - User accounts with authentication")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Verify database:")
    print("   python3 explore_database.py")
    print("\n2. Start Day 2 tomorrow:")
    print("   Implement user authentication backend")
    print("\n3. Read Day 2 instructions in:")
    print("   MEDALLION_IMPLEMENTATION_PLAN.txt")
    print("\n" + "=" * 80)
    
    conn.close()

if __name__ == "__main__":
    # Check if bcrypt is installed
    try:
        import bcrypt
    except ImportError:
        print("❌ bcrypt not installed!")
        print("\nInstall it with:")
        print("   pip install bcrypt")
        print("\nThen run this script again.")
        exit(1)
    
    create_medallion_schema()