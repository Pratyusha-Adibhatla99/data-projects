#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from mat_processor import WirelessDataProcessor

def process_directory():
    data_dir = 'channels_release'
    mat_files = list(Path(data_dir).glob('*.mat'))
    
    print(f"\n{'='*70}")
    print(f"🔄 Processing {len(mat_files)} files from {data_dir}/")
    print(f"{'='*70}\n")
    
    channels = [f for f in mat_files if 'channels' in f.name]
    timestamps = [f for f in mat_files if 'timestamps' in f.name]
    
    print(f"📊 Channels files: {len(channels)}")
    print(f"📊 Timestamps files: {len(timestamps)}\n")
    
    for i, filepath in enumerate(mat_files, 1):
        print(f"\n[{i}/{len(mat_files)}] {filepath.name}")
        try:
            processor = WirelessDataProcessor(str(filepath))
            data = processor.read_file()
            print(f"   ✅ Processed ({len(data)} variables)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print("✅ Done!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    process_directory()
