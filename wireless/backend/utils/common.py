import pytz
import hashlib
from datetime import datetime

def get_pst_time():
    """Returns current time in US/Pacific timezone"""
    pst_tz = pytz.timezone('US/Pacific')
    return datetime.now(pst_tz)

def calculate_file_hash(filepath):
    """Generates SHA256 hash for file integrity"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def detect_modality(filename):
    """Classifies file type based on extension/name"""
    ext = filename.lower().split('.')[-1]
    name = filename.lower()
    if ext in ['pcd', 'las', 'laz']: return 'lidar'
    if ext in ['bin']: return 'radar'
    if 'channel' in name or 'csi' in name: return 'wifi'
    if ext == 'csv': return 'tabular'
    if ext == 'mat': return 'matlab'
    return 'unknown'